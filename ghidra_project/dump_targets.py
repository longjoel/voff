# Ghidra Python script -- decompile specific functions by address
# @category Analysis

import os, re
from java.io import FileWriter
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUTPUT_DIR = None

# Key functions from the game loop, by RVA (VA - 0x00400000)
# Ghidra names them FUN_00XXXXXX where 0x00XXXXXX is the VA
# RVA = VA - 0x00400000
TARGETS = {
    # Init sequence
    0x001146c6: "ddraw_init",           # FUN_005146c6 - takes hWnd
    0x0007e600: "unk_47e600",           # thunk called before window
    # Window message handling
    0x000f2559: "sde_dispatcher",        # FUN_004f2559 - SDE event dispatcher
    # Main init functions  
    0x001c97e2: "unk_5c97e2",
    0x001895a0: "unk_5895a0",
    0x00111434: "unk_511434",
    0x0009f7fe: "unk_49f7fe",
    0x001c5ac3: "unk_5c5ac3",
    0x001ce180: "unk_5ce180",
    0x001c5b31: "unk_5c5b31",
    0x00044388: "unk_444388",
    0x0000f43e: "unk_40f43e",
    0x001cc616: "unk_5cc616",
    0x000b5fcf: "unk_4b5fcf",
    0x00101097: "unk_501097",
    0x001898e6: "unk_5898e6",
    0x00095a40: "unk_495a40",
    # Frame functions
    0x000442ce1: "unk_442ce1",
    0x000b560f: "unk_4b560f",
    0x001bcbd2: "unk_5bcbd2",
    0x001006df: "unk_5006df",
    0x00166dce: "unk_566dce",
    0x000b5c2b: "unk_4b5c2b",
    0x0009fbc0: "unk_49fbc0",
    0x000086e0: "unk_4086e0",
    0x0009f8e8: "unk_49f8e8",
    0x00166c01: "unk_566c01",
    0x00100d2b: "unk_500d2b",
    0x0000f7b0: "unk_40f7b0",
    0x0001d770: "unk_41d770",
    0x0000f528: "unk_40f528",
    0x001c9f70: "unk_5c9f70",
}

def setup():
    global OUTPUT_DIR
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out_decompile")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def wf(path, content):
    fw = FileWriter(path)
    fw.write(content)
    fw.close()

def main():
    program = getCurrentProgram()
    setup()
    decompiler = DecompInterface()
    decompiler.openProgram(program)
    fm = program.getFunctionManager()
    listing = program.getListing()

    addr_space = program.getAddressFactory().getDefaultAddressSpace()

    all_code = []
    print("Decompiling {} target functions...".format(len(TARGETS)))

    for rva, name in sorted(TARGETS.items()):
        # VA = base + RVA. The Ghidra offset format: VA = 0x00400000 + RVA
        # But getOffset() on functions returns VA, and getFunctionAt takes VA
        va = 0x00400000 + rva
        func = fm.getFunctionAt(addr_space.getAddress(va))
        if func is None:
            print("  {:08x} ({}) - NOT FOUND as function, trying containing...".format(va, name))
            func = fm.getFunctionContaining(addr_space.getAddress(va))

        if func:
            c = None
            try:
                result = decompiler.decompileFunction(func, 60, ConsoleTaskMonitor())
                if result and result.decompileCompleted():
                    c = result.getDecompiledFunction().getC()
            except:
                pass

            if c:
                c = c.replace("__cdecl(", "(")
                c = c.replace("__thiscall ", "")
                c = c.replace("__stdcall ", "")
                c = c.replace("__fastcall ", "")
                all_code.append((va, name, c))
                lines = c.count("\n")
                print("  {:08x} {}: {} lines".format(va, name, lines))
            else:
                all_code.append((va, name, "/* decompile failed */"))
                print("  {:08x} {}: DECOMPILE FAILED".format(va, name))
                # Show first few instructions
                instr = listing.getInstructionAt(func.getEntryPoint())
                for i in range(5):
                    if instr and func.getBody().contains(instr.getAddress()):
                        print("    asm: {} {}".format(instr.getAddress(), instr))
                        instr = instr.getNext()
        else:
            print("  {:08x} {}: NOT FOUND".format(va, name))

    # Write output
    lines = []
    lines.append("/* Target functions decompiled from V_ON.EXE */\n")
    lines.append("/* {} function(s) */\n\n".format(len([x for x in all_code if "decompile failed" not in x[2]])))

    for va, name, c in all_code:
        lines.append("/* ============================================================ */\n")
        lines.append("/* {} at VA {:08x} */\n".format(name, va))
        lines.append("/* ============================================================ */\n\n")
        lines.append(c)
        lines.append("\n\n")

    outpath = os.path.join(OUTPUT_DIR, "target_functions.c")
    wf(outpath, "".join(lines))
    print("\nWritten {} function(s) to {}".format(len(all_code), outpath))

if __name__ == "__main__":
    main()
