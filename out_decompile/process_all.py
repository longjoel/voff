#!/usr/bin/env python3
"""Post-process Ghidra-decompiled C to make it compilable with logging."""

import os, re, glob, sys

BASE = os.path.dirname(os.path.abspath(__file__)) or "."
SRC_DIR = os.path.join(BASE, "src")
OUT_DIR = os.path.join(BASE, "build")

LOG_FUNCTIONS = {
    # Key functions to inject entry/exit logging into
    "FUN_005c5c7a": True,   # main_game_loop
    "FUN_005c563c": True,   # ddraw_init
    "FUN_005c5909": True,   # register_window_class
    "FUN_005c59a9": True,   # create_window
    "FUN_004f17ca": True,   # sde_dispatcher (was 0x0F2559)
    "FUN_005083ef": True,   # cpuid_check
    "FUN_005c6311": True,   # mmx_cpu_check wrapper
    "FUN_005146c6": True,   # DDraw init
    "FUN_001e7930": False,  # would be WinMain but let's skip
}

def process_file(fpath):
    with open(fpath) as f:
        content = f.read()

    # Extract function name from first line comment
    name_match = re.search(r'FUN_[0-9a-fA-F]{8}', content)
    func_name = name_match.group(0) if name_match else None

    # === Fixups ===

    # 1. Replace Ghidra calling conventions
    content = content.replace("__cdecl(", "(")
    content = content.replace("__thiscall ", " ")
    content = content.replace("__stdcall ", " ")
    content = content.replace("__fastcall ", " ")

    # 2. CONCAT removal
    content = re.sub(r'CONCAT\d+\s*\(', '(', content)
    content = re.sub(r'\bCONCAT\d+\b', '', content)

    # 3. (code *) -> (void *)
    content = content.replace("(code *)", "(void *)")
    content = content.replace("(code  *)", "(void *)")

    # 4. Ghidra undefined types -> standard types
    # Do longest first to avoid substring issues
    content = content.replace(" undefined8 ", " uint64_t ")
    content = content.replace(" undefined4 ", " uint32_t ")
    content = content.replace(" undefined2 ", " uint16_t ")
    content = content.replace(" undefined1 ", " uint8_t ")
    content = content.replace(" undefined ", " uint8_t ")
    content = re.sub(r'\bundefined8\b', 'uint64_t', content)
    content = re.sub(r'\bundefined4\b', 'uint32_t', content)
    content = re.sub(r'\bundefined2\b', 'uint16_t', content)
    content = re.sub(r'\bundefined1\b', 'uint8_t', content)
    content = re.sub(r'\bundefined\b', 'uint8_t', content)
    content = re.sub(r'undefined\d*\s*\*', 'uint8_t *', content)

    # Replace whole-word type uses at function signatures
    content = re.sub(r'^undefined4 ', 'uint32_t ', content, flags=re.MULTILINE)
    content = re.sub(r'^undefined8 ', 'uint64_t ', content, flags=re.MULTILINE)
    content = re.sub(r'^undefined2 ', 'uint16_t ', content, flags=re.MULTILINE)
    content = re.sub(r'^undefined ', 'uint8_t ', content, flags=re.MULTILINE)

    # 5. &stack0x -> 0x (stack offset references)
    content = content.replace("&stack0x", "0x")

    # 6. Fix DAT_/PTR_ member access: *DAT_xxx -> DAT_xxx[0]
    content = re.sub(r'\*((?:DAT_|PTR_)[A-Za-z0-9_]+)\b', r'\1[0]', content)

    # 7. Fix ADDR casts
    content = re.sub(
        r'\(\*\(void \*\)\(&([A-Z_][A-Z0-9_]*)\)\[([^\]]+)\]\)\(([^)]*)\)',
        r'((void(*)(int))(\1[0]))(\3)',
        content
    )
    # Simpler case: (*(void *)(&PTR_FOO)[idx])(args)
    content = re.sub(
        r'\(\*\(void \*\)\(&([A-Z_][A-Z0-9_]*)\)\[([^\]]*)\]\)\(([^)]*)\)',
        r'((void(*)(int))(\1[0]))(\3)',
        content
    )

    # 8. Inject logging for key functions
    if func_name and LOG_FUNCTIONS.get(func_name):
        content = inject_logging(content, func_name)

    # Ensure include is present
    if '#include' not in content.split('\n')[1]:
        content = content.replace(
            '/* {} at VA'.format(func_name or ''),
            '/* {} at VA'.format(func_name or '') + ' */\n#include "../voff_all.h"\n/*',
            1
        )

    return content


def inject_logging(content, func_name):
    """Add LOG_ENTER/LOG_EXIT to function body"""
    # Find function body opening brace
    # Pattern: the first { after the function declaration
    lines = content.split('\n')
    result = []
    in_body = False
    depth = 0

    for i, line in enumerate(lines):
        result.append(line)

        if not in_body and '{' in line:
            in_body = True
            brace_line = i
            # Find indentation
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            # Insert LOG_ENTER right after the opening brace
            result.append('{}LOG_ENTER("called");'.format(indent + '  '))
            continue

    # Find the last closing brace and add LOG_EXIT before it
    # For simplicity, find return statements and add LOG_EXIT before them
    final_lines = []
    for line in result:
        # Add LOG_EXIT before each return statement inside the function
        if in_body and re.match(r'^(\s+)return\b', line):
            indent = line[:len(line) - len(line.lstrip())]
            final_lines.append('{}LOG_EXIT("returning");'.format(indent))
        final_lines.append(line)

    return '\n'.join(final_lines)


def process_all():
    os.makedirs(OUT_DIR, exist_ok=True)

    files = sorted(glob.glob(os.path.join(SRC_DIR, "f_*.c")))
    total = len(files)
    print("Processing {} files...".format(total))

    processed = 0
    for fpath in files:
        try:
            new_content = process_file(fpath)
            outname = os.path.basename(fpath)
            outpath = os.path.join(OUT_DIR, outname)
            with open(outpath, "w") as f:
                f.write(new_content)
            processed += 1
        except Exception as e:
            print("  ERROR processing {}: {}".format(os.path.basename(fpath), e))

        if processed % 500 == 0:
            print("  {}/{}...".format(processed, total))

    print("Done: {} processed to {}".format(processed, OUT_DIR))

    # Generate Makefile
    generate_makefile(files, total)


def generate_makefile(files, total):
    """Generate a Makefile that compiles all processed .c files"""
    make_lines = []
    make_lines.append("# Auto-generated Makefile - {} source files\n".format(total))
    make_lines.append("WINE = winegcc\n")
    make_lines.append("CFLAGS = -Wall -Wno-implicit-function-declaration -Wno-unused-variable -I..\n")
    make_lines.append("LDFLAGS = -lgdi32 -lcomctl32 -lwinmm -lddraw -ldsound -ldinput\n")
    make_lines.append("\n")
    make_lines.append("OBJS = \\\n")

    obj_files = []
    for f in files:
        obj = os.path.basename(f).replace('.c', '.o')
        obj_files.append(obj)
    # Write 5 per line
    for i in range(0, len(obj_files), 5):
        batch = obj_files[i:i+5]
        make_lines.append("    " + " ".join(batch))
        if i + 5 < len(obj_files):
            make_lines.append(" \\")
        make_lines.append("\n")

    make_lines.append("\n")
    make_lines.append("TARGET = voff_full.exe\n")
    make_lines.append("\n")
    make_lines.append("all: $(TARGET)\n")
    make_lines.append("\n")
    make_lines.append("$(TARGET): $(OBJS) ../voff_data.o\n")
    make_lines.append("\t$(WINE) $(CFLAGS) -o $@ $^ $(LDFLAGS)\n")
    make_lines.append("\n")
    make_lines.append("%.o: %.c\n")
    make_lines.append("\t$(WINE) $(CFLAGS) -c -o $@ $<\n")
    make_lines.append("\n")
    make_lines.append("clean:\n")
    make_lines.append("\trm -f $(TARGET) $(TARGET).so *.o\n")
    make_lines.append("\n")
    make_lines.append(".PHONY: all clean\n")

    with open(os.path.join(OUT_DIR, "Makefile"), "w") as f:
        f.write("".join(make_lines))
    print("Makefile written to {}".format(os.path.join(OUT_DIR, "Makefile")))


if __name__ == "__main__":
    process_all()
