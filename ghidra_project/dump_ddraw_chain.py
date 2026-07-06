# Ghidra Python script -- decompile DDraw chain functions
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from java.io import FileWriter
import os

OUT = "/var/home/longjoel/Projects/voff/out_decompile"

DDRAW_CHAIN = {
    0x001147e8: "ddraw_create",
    0x00114726: "ddraw_surface_setup",
    0x0011484d: "ddraw_unk1",
    0x001148d0: "ddraw_unk2",
    0x00114950: "ddraw_unk3",
}

program = getCurrentProgram()
decompiler = DecompInterface()
decompiler.openProgram(program)
fm = program.getFunctionManager()
space = program.getAddressFactory().getDefaultAddressSpace()
outpath = os.path.join(OUT, "ddraw_chain.c")

lines = ["/* DDraw chain functions */\n\n"]
for rva, name in sorted(DDRAW_CHAIN.items()):
    va = 0x00400000 + rva
    func = fm.getFunctionAt(space.getAddress(va))
    if func is None:
        lines.append("/* {} - NOT FOUND */\n\n".format(name))
        print("  {:08x} {}: NOT FOUND".format(va, name))
        continue
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
        lines.append("/* ===== {} (VA {:08x}) ===== */\n".format(name, va))
        lines.append(c)
        lines.append("\n\n")
        print("  {:08x} {}: {} lines".format(va, name, c.count("\n")))
    else:
        lines.append("/* {} - DECOMPILE FAILED */\n\n".format(name))
        print("  {:08x} {}: DECOMPILE FAILED".format(va, name))

with open(outpath, "w") as f:
    f.write("".join(lines))
print("Done: {} ({} bytes)".format(outpath, len("".join(lines))))
