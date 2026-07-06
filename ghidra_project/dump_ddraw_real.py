# Decompile FUN_005c563c (calls DirectDrawCreate)
import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

program = getCurrentProgram()
fm = program.getFunctionManager()
space = program.getAddressFactory().getDefaultAddressSpace()

func = fm.getFunctionAt(space.getAddress(0x005c563c))
if func is None:
    print("Function not found at 0x005c563c")
    exit(1)

decomp = DecompInterface()
decomp.openProgram(program)
result = decomp.decompileFunction(func, 60, ConsoleTaskMonitor())

if result and result.decompileCompleted():
    c = result.getDecompiledFunction().getC()
    c = c.replace("__cdecl(", "(")
    c = c.replace("__thiscall ", "")
    c = c.replace("__stdcall ", "")
    c = c.replace("__fastcall ", "")
    out = "/var/home/longjoel/Projects/voff/out_decompile/ddraw_real_init.c"
    with open(out, "w") as f:
        f.write("/* FUN_005c563c - the actual DDraw init */\n\n")
        f.write(c)
    print("Written {} lines to {}".format(c.count("\n") + 1, out))
else:
    print("Decompile failed")
    # Show first few instructions
    listing = program.getListing()
    instr = listing.getInstructionAt(func.getEntryPoint())
    for i in range(20):
        if instr and func.getBody().contains(instr.getAddress()):
            print("  {} {}".format(instr.getAddress(), instr))
            instr = instr.getNext()
