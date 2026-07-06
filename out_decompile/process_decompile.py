#!/usr/bin/env python3
"""Process Ghidra decompiled C output to make it compilable with winegcc."""

import re
import sys
import os
from collections import defaultdict

OUT_DIR = os.path.dirname(os.path.abspath(__file__)) or "."


def main():
    with open(os.path.join(OUT_DIR, "voff.c")) as f:
        c_code = f.read()

    # Find all global variable references
    globals_found = set()
    funcs_found = set()

    for match in re.finditer(r'\b(DAT_[0-9a-fA-F]{8})\b', c_code):
        globals_found.add(match.group(1))
    for match in re.finditer(r'\b(PTR_[a-zA-Z_][a-zA-Z0-9_]{1,30})\b', c_code):
        globals_found.add(match.group(1))
    for match in re.finditer(r'\b(PTR_s_[0-9a-fA-F]{8})\b', c_code):
        globals_found.add(match.group(1))

    # Find all called functions
    for match in re.finditer(r'\b(FUN_[0-9a-fA-F]{8})\b', c_code):
        funcs_found.add(match.group(1))

    # Count max args for each function from callsites
    func_args = {}
    for f_name in funcs_found:
        max_args = 0
        pattern = re.escape(f_name) + r'\s*\(([^)]*)\)'
        for m in re.finditer(pattern, c_code):
            args = m.group(1).strip()
            if args and args != 'void':
                num = args.count(',') + 1
                if num > max_args:
                    max_args = num
        func_args[f_name] = max_args

    # Check which functions are defined (not just called)
    defined_funcs = set()
    for match in re.finditer(r'(?:void|int|uint|bool|ATOM|LRESULT|HANDLE|short|byte|uint\d+_t)\s+(FUN_[0-9a-fA-F]{8})\s*\(', c_code):
        defined_funcs.add(match.group(1))
    # Also check for entry/other known functions
    if 'void entry(void)' in c_code:
        defined_funcs.add('entry')

    # Only generate stubs for functions NOT defined in the C file
    stub_funcs = funcs_found - defined_funcs

    print(f"Found {len(globals_found)} global variable references")
    print(f"Found {len(funcs_found)} function calls, {len(defined_funcs)} defined, {len(stub_funcs)} need stubs")

    # ============ Generate stubs header ============
    h_lines = []
    h_lines.append("/* Auto-generated stubs */\n")
    h_lines.append("#ifndef VOFF_DECOMPILED_H\n")
    h_lines.append("#define VOFF_DECOMPILED_H\n\n")
    h_lines.append("#define WIN32_LEAN_AND_MEAN\n")
    h_lines.append("#include \"voff_types.h\"\n")
    h_lines.append("#include <windows.h>\n")
    h_lines.append("#include <mmsystem.h>\n")
    h_lines.append("#include <commctrl.h>\n")
    h_lines.append("#include <ddraw.h>\n")
    h_lines.append("#include <dsound.h>\n")
    h_lines.append("#include <dinput.h>\n")
    h_lines.append("#include <stdio.h>\n")
    h_lines.append("#include <stdlib.h>\n")
    h_lines.append("#include <string.h>\n")
    h_lines.append("#include <math.h>\n\n")

    h_lines.append("/* === Global data (will be resolved at link time from .data section) === */\n")
    for g in sorted(globals_found):
        h_lines.append(f"extern uint8_t {g}[65536];\n")

    h_lines.append("\n/* === Function stubs for unresolved callees === */\n")
    for f_name in sorted(stub_funcs):
        n = func_args.get(f_name, 0)
        if n == 0:
            h_lines.append(f"extern void {f_name}(void);\n")
        else:
            args = ", ".join(f"int a{i}" for i in range(n))
            h_lines.append(f"extern int {f_name}({args});\n")

    h_lines.append("\n#endif /* VOFF_DECOMPILED_H */\n")

    with open(os.path.join(OUT_DIR, "voff_stubs.h"), "w") as f:
        f.write("".join(h_lines))

    # ============ Generate processed C file ============
    lines = []

    # Include
    lines.append('#include "voff_stubs.h"\n\n')

    # Stub implementation section
    lines.append("/* === Stub implementations === */\n")
    for f_name in sorted(stub_funcs):
        n = func_args.get(f_name, 0)
        if n == 0:
            lines.append(f"void {f_name}(void) {{ }}\n")
        else:
            args = ", ".join(f"int a{i}" for i in range(n))
            lines.append(f"int {f_name}({args}) {{ return 0; }}\n")
    lines.append("\n")

    lines.append("/* ===== Actual decompiled code ===== */\n\n")

    # Process the C code
    c_code = re.sub(r'/\* WARNING:.*?\*/', '', c_code)
    c_code = c_code.replace("void __local_unwind2(int param_1,int param_2)",
                             "static void __local_unwind2(int param_1, int param_2)")
    c_code = c_code.replace("void entry(void)",
                             "int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR cmd, int show)")
    c_code = re.sub(r'CONCAT\d+\s*\(([^)]+)\)', r'(\1)', c_code)
    c_code = re.sub(r'\bCONCAT\d+\b', '', c_code)
    c_code = c_code.replace("(code *)", "(void *)")
    # Replace undefined types - do undefined1 first since it's substring of undefined8/etc
    c_code = c_code.replace(" undefined1 ", " uint8_t ")
    c_code = c_code.replace("*(undefined1 *)", "*(uint8_t *)")
    c_code = c_code.replace(" undefined8 ", " uint64_t ")
    c_code = c_code.replace(" undefined4 ", " uint32_t ")
    c_code = c_code.replace(" undefined2 ", " uint16_t ")
    c_code = c_code.replace(" undefined ", " uint8_t ")
    c_code = c_code.replace("&stack0x", "0x")
    c_code = re.sub(r'\bCONCAT\d+\b', '', c_code)

    # Fix void-pointer function calls and array member access
    # Pattern 1: (*(void *)(&PTR_FOO)[idx])(args) -> ((int(*)(int,...))PTR_FOO)(args)
    def fix_funcptr(m):
        ptr_name = m.group(1)  # e.g., &PTR_FUN_00604bb8
        idx = m.group(2)       # e.g., idx
        args = m.group(3)      # e.g., param_1
        return f"((int(*)(int))({ptr_name}))({args})"

    c_code = re.sub(
        r'\(\*\(void \*\)\((&[A-Z_][A-Z0-9_]*)\)\[([^\]]+)\]\)\(([^)]*)\)',
        fix_funcptr,
        c_code
    )

    # Pattern 2: (void *)(&PTR_FOO)[idx] != NULL comparison
    c_code = re.sub(
        r'\(\(void \*\)\(&([A-Z_][A-Z0-9_]*)\)\[([^\]]+)\]\) != \(void \*\)0x0\)',
        r'(((int(*)())(&(\1))) != NULL)',
        c_code
    )

    # Pattern 3: *(undefined2 *)(&DAT_xxx + offset) -> array access
    c_code = re.sub(
        r'\*\(([^)]*\*)\s*\)\(&([A-Z_][A-Z0-9_]+)\s*\+(.+?)\)',
        r'*((\1 )(&(\2)[0] + (\3)))',
        c_code
    )
    c_code = c_code.replace("][0] +", "] +")

    # Pattern 4: &PTR_FOO cast to something
    # Leave as-is for now, the arrays are large enough

    lines.append(c_code)

    with open(os.path.join(OUT_DIR, "voff_processed.c"), "w") as f:
        f.write("".join(lines))

    print("Generated voff_processed.c")


if __name__ == "__main__":
    main()
