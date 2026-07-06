# Ghidra Python script -- find and decompile all DDraw-related functions
# @category Analysis

import os
import re
from java.io import FileWriter
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUTPUT_DIR = None

DDRAW_CALLS = [
    "DirectDrawCreate",
    "DirectDrawCreateClipper",
    "IDirectDraw",
    "IDirectDrawSurface",
    "IDirectDrawPalette",
    "IDirectDrawClipper",
]

DDRAW_METHODS = [
    "SetCooperativeLevel", "SetDisplayMode",
    "CreateSurface", "CreatePrimarySurface",
    "Blt", "BltFast", "Flip", "Lock", "Unlock",
    "GetAttachedSurface", "GetDisplayMode",
    "SetPalette", "CreatePalette",
    "SetClipper", "SetColorKey", "GetCaps",
    "RestoreDisplayMode", "WaitForVerticalBlank",
    "GetScanLine", "GetAvailableVidMem",
    "EnumDisplayModes", "Compact", "RestoreAllSurfaces",
    "GetPixelFormat", "SetEntries", "GetEntries",
]

DDRAW_STRS = [
    "DDSURFACEDESC", "DDPIXELFORMAT", "DDSCAPS",
    "DDBLT", "DDCOLORKEY", "DDPALETTE",
    "surface_desc", "pixel_format",
]

def setup():
    global OUTPUT_DIR
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out_decompile")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def wf(path, content):
    fw = FileWriter(path)
    fw.write(content)
    fw.close()

def decompile_func(program, decomp, func, timeout=60):
    try:
        result = decomp.decompileFunction(func, timeout, ConsoleTaskMonitor())
        if result and result.decompileCompleted():
            return result.getDecompiledFunction().getC()
    except:
        pass
    return None

def main():
    program = getCurrentProgram()
    setup()
    fm = program.getFunctionManager()
    sym_table = program.getSymbolTable()
    ref_mgr = program.getReferenceManager()
    listing = program.getListing()

    print("=" * 60)
    print("Finding DDraw-related functions...")
    print("=" * 60)

    decompiler = DecompInterface()
    decompiler.openProgram(program)

    # Step 1: Find all functions that call DDraw imports
    ddraw_funcs = set()
    import_addrs = {}

    for sym in sym_table.getExternalSymbols():
        name = sym.getName()
        matched = False
        for pattern in DDRAW_CALLS:
            if name == pattern:
                matched = True
                break
        if matched:
            addr = sym.getAddress()
            refs = list(ref_mgr.getReferencesTo(addr))
            if refs:
                print("  Import {} referenced {} times".format(name, len(refs)))
                for ref in refs:
                    caller = fm.getFunctionContaining(ref.getFromAddress())
                    if caller:
                        ddraw_funcs.add(caller.getEntryPoint().getOffset())
                import_addrs[name] = (addr, len(refs))

    # Also search for calls to COM interface methods (indirect calls)
    # by searching for the method name strings
    for sym in sym_table.getAllSymbols(True):
        name = sym.getName()
        # Look for string references to "IDirectDraw" pattern
        if "IDirectDraw" in name and not name.startswith("_"):
            addr = sym.getAddress()
            refs = list(ref_mgr.getReferencesTo(addr))
            if refs:
                for ref in refs:
                    caller = fm.getFunctionContaining(ref.getFromAddress())
                    if caller:
                        ddraw_funcs.add(caller.getEntryPoint().getOffset())

    print("\nFound {} DDraw-related functions".format(len(ddraw_funcs)))

    # Step 2: Also find functions called by these DDraw functions (1 level deep)
    expanded = set(ddraw_funcs)
    # Walk instructions within each function to find callees
    for rva in list(ddraw_funcs):
        func = fm.getFunctionAt(addr_space.getAddress(rva))
        if func and func.getBody():
            instr = listing.getInstructionAt(func.getEntryPoint())
            while instr is not None and func.getBody().contains(instr.getAddress()):
                refs = ref_mgr.getReferencesFrom(instr.getAddress())
                for ref in refs:
                    target = fm.getFunctionContaining(ref.getToAddress())
                    if target:
                        expanded.add(target.getEntryPoint().getOffset())
                instr = instr.getNext()

    # Step 3: Also look for functions that reference key data structures
    # Find functions using the primary surface pointer or back buffer
    # (We'll search for the known window handle store address)

    # Step 4: Decompile all found functions
    print("\nDecompiling {} DDraw-related functions (including callees)...".format(len(expanded)))
    print("  RVAs: {}".format([hex(x) for x in sorted(expanded)]))

    all_code = []
    addr_space = program.getAddressFactory().getDefaultAddressSpace()
    for rva in sorted(expanded):
        addr = addr_space.getAddress(rva)
        func = fm.getFunctionAt(addr)
        print("  Looking up func at {}: func={}".format(addr, func))
        if func is None:
            # Try getFunctionContaining as well
            func = fm.getFunctionContaining(addr)
            print("    getFunctionContaining: func={}".format(func))
        if func is None:
            all_code.append((rva, "unknown_{:08x}".format(rva), "/* function not found at this address */"))
            continue
        name = func.getName()

        c = decompile_func(program, decompiler, func)
        if c:
            c = c.replace("__cdecl(", "(")
            c = c.replace("__thiscall ", "")
            c = c.replace("__stdcall ", "")
            c = c.replace("__fastcall ", "")
            all_code.append((rva, name, c))
            print("  {:08x} {} ({} chars)".format(rva, name, len(c)))
        else:
            all_code.append((rva, name, "/* decompile failed */"))

    # Step 5: Write output
    lines = []
    lines.append("/* DDraw-related decompiled functions from V_ON.EXE */\n")
    lines.append("/* {} functions */\n\n".format(len(all_code)))
    lines.append("/* Import references:\n")
    for name, (addr, count) in sorted(import_addrs.items()):
        lines.append("   {}: {} calls\n".format(name, count))
    lines.append("*/\n\n")

    for rva, name, c in all_code:
        lines.append("/* ============================================================ */\n")
        lines.append("/* {} at 0x{:08x} */\n".format(name, rva))
        lines.append("/* ============================================================ */\n\n")
        lines.append(c)
        lines.append("\n\n")

    outpath = os.path.join(OUTPUT_DIR, "ddraw_functions.c")
    wf(outpath, "".join(lines))
    print("\nWritten {} functions to {}".format(len(all_code), outpath))

    # Step 6: Write a function list
    maplines = []
    for rva, name, c in all_code:
        maplines.append("0x{:08x}: {}\n".format(rva, name))
    wf(os.path.join(OUTPUT_DIR, "ddraw_function_map.txt"), "".join(maplines))


if __name__ == "__main__":
    main()
