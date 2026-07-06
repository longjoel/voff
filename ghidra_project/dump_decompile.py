# Ghidra Python script -- fast decompile: dump data as raw bytes, decompile key funcs
# @category Analysis

import os
import re
import sys
from java.io import FileWriter, FileOutputStream
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUTPUT_DIR = None

KEY_FUNC_RVAS = {
    # RVAs (with image base 0x00400000, VA = RVA + 0x00400000)
    # Entry point
    0x1E7930: "WinMain",
    # CD / startup
    0x1C74F0: "startup_init",
    0x1C7DA0: "cdrom_detect",
    0x1CA910: "cd_audio_init",
    # DirectDraw
    0x1E6D60: "ddraw_init",
    # Window
    0x1C5909: "register_window_class",
    0x1C59A9: "create_window",
    0x1C5A45: "window_init_helper",
    # Game loop / MMX
    0x1C5C7A: "main_game_loop",
    0x1C6311: "mmx_cpu_check",
    0x1083EF: "cpuid_check",
    # SDE dispatcher
    0x0F2559: "sde_dispatcher",
    # Misc
    0x166EA9: "virtual_on_string",
}

SECTION_DUMP = [".data", ".rdata", ".rsrc"]


def setup():
    global OUTPUT_DIR
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out_decompile")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def wf(path, content):
    fw = FileWriter(path)
    fw.write(content)
    fw.close()


def get_func_at(program, rva):
    addr = program.getImageBase().add(rva)
    return program.getFunctionManager().getFunctionContaining(addr)


def decompile(decompiler, func, timeout=60):
    try:
        result = decompiler.decompileFunction(func, timeout, ConsoleTaskMonitor())
        if result and result.decompileCompleted():
            return result.getDecompiledFunction().getC()
    except:
        pass
    return None


def extract_sig(name, c_code):
    """Extract function signature from C code"""
    brace = c_code.find("{")
    if brace >= 0:
        sig = c_code[:brace].strip().rstrip()
        # Keep just the function signature line
        lines = sig.split("\n")
        sig = " ".join(line.strip() for line in lines).strip()
        # Remove extra whitespace
        sig = re.sub(r'\s+', ' ', sig)
        return sig
    return "void {}()".format(name)


def sanitize(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


def main():
    program = getCurrentProgram()
    setup()
    print("=" * 60)
    print("VOFF Fast Decompile Export")
    print("Program: {} at base {}".format(program.getName(), program.getImageBase()))

    #
    # STEP 1: Dump binary sections as raw .bin files
    #
    print("\n[1/3] Dumping binary sections...")
    for sec_name in SECTION_DUMP:
        block = program.getMemory().getBlock(sec_name)
        if block is None:
            print("  {}: NOT FOUND".format(sec_name))
            continue
        start = block.getStart()
        end = block.getEnd()
        size = end.subtract(start) + 1
        if size > 50 * 1024 * 1024:  # Skip huge uninit BSS
            print("  {}: SKIPPED ({} MB, probably BSS)".format(sec_name, size / 1024 / 1024))
            continue

        outpath = os.path.join(OUTPUT_DIR, sec_name + ".bin")
        fos = FileOutputStream(outpath)
        addr = start
        count = 0
        while addr <= end:
            try:
                b = program.getMemory().getByte(addr)
                fos.write(b)
            except:
                fos.write(0)
            addr = addr.add(1)
            count += 1
            if count % 0x100000 == 0:
                print("    {}: {:x} / {:x} ...".format(sec_name, count, size))
        fos.close()
        print("  {}: {:,} bytes dumped to {}".format(sec_name, size, os.path.basename(outpath)))

    #
    # STEP 2: Decompile key functions
    #
    print("\n[2/3] Decompiling key functions...")
    decomp = DecompInterface()
    decomp.openProgram(program)

    all_code = []
    all_sigs = []

    for rva, nice_name in sorted(KEY_FUNC_RVAS.items()):
        func = get_func_at(program, rva)
        if func is None:
            print("  0x{:08x} ({}) - NOT FOUND".format(rva, nice_name))
            continue

        c_code = decompile(decomp, func)
        if c_code:
            # Post-process
            c_code = c_code.replace("__cdecl(", "(")
            c_code = c_code.replace("__cdecl ", "")
            c_code = c_code.replace("__thiscall ", "")
            c_code = c_code.replace("__stdcall ", "")
            c_code = c_code.replace("_cdecl ", "")
            sig = extract_sig(nice_name, c_code)
            all_code.append((rva, nice_name, c_code))
            all_sigs.append((rva, nice_name, sig))
            print("  0x{:08x} ({}) - OK ({} chars)".format(rva, nice_name, len(c_code)))
        else:
            print("  0x{:08x} ({}) - DECOMPILE FAILED")

    #
    # STEP 3: Generate header and combined C file
    #
    print("\n[3/3] Generating C files...")

    # Header
    h_lines = []
    h_lines.append("/* VOFF decompiled - header */\n")
    h_lines.append("#ifndef VOFF_DECOMPILED_H\n")
    h_lines.append("#define VOFF_DECOMPILED_H\n\n")
    h_lines.append("#define WIN32_LEAN_AND_MEAN\n")
    h_lines.append("#include <windows.h>\n")
    h_lines.append("#include <mmsystem.h>\n")
    h_lines.append("#include <commctrl.h>\n")
    h_lines.append("#include <ddraw.h>\n")
    h_lines.append("#include <dsound.h>\n")
    h_lines.append("#include <dinput.h>\n")
    h_lines.append("#include <dplay.h>\n")
    h_lines.append("#include <stdio.h>\n")
    h_lines.append("#include <stdlib.h>\n")
    h_lines.append("#include <string.h>\n")
    h_lines.append("#include <math.h>\n\n")

    h_lines.append("/* Function declarations */\n")
    for rva, name, sig in all_sigs:
        h_lines.append("/* 0x{:08x} */ {};\n".format(rva, sig))

    h_lines.append("\n#endif\n")
    wf(os.path.join(OUTPUT_DIR, "voff.h"), "".join(h_lines))
    print("  voff.h written ({:,} bytes)".format(len("".join(h_lines))))

    # Main C file
    c_lines = []
    c_lines.append("/* VOFF decompiled code */\n")
    c_lines.append("#include \"voff.h\"\n\n")
    c_lines.append("/* Embedded binary sections */\n")
    c_lines.append("/* See .bin files in this directory */\n\n")

    for rva, name, c_code in all_code:
        c_lines.append("/* === {} (0x{:08x}) === */\n".format(name, rva))
        c_lines.append(c_code)
        c_lines.append("\n\n")

    # WinMain entry
    c_lines.append("/* Entry point wrapper */\n")
    c_lines.append("int WINAPI WinMain(HINSTANCE hi, HINSTANCE hp, LPSTR cmd, int show)\n")
    c_lines.append("{\n")
    c_lines.append("    WinMain();  /* actual entry */\n")
    c_lines.append("    return 0;\n")
    c_lines.append("}\n")

    wf(os.path.join(OUTPUT_DIR, "voff.c"), "".join(c_lines))
    print("  voff.c written ({:,} bytes)".format(len("".join(c_lines))))

    # Summary
    print("\nDone. {} functions exported to {}".format(len(all_code), OUTPUT_DIR))


if __name__ == "__main__":
    main()
