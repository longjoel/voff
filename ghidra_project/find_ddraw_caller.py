# Ghidra script -- find callers of DirectDrawCreate and decompile them
import os

program = getCurrentProgram()
fm = program.getFunctionManager()
sym_table = program.getSymbolTable()
ref_mgr = program.getReferenceManager()
listing = program.getListing()

# Find DirectDrawCreate import
ddc_sym = None
for sym in sym_table.getExternalSymbols():
    if sym.getName() == "DirectDrawCreate":
        ddc_sym = sym
        break

if ddc_sym is None:
    print("DirectDrawCreate not found in imports!")
    exit(1)

print("DirectDrawCreate at: {}".format(ddc_sym.getAddress()))

# Get references
refs = list(ref_mgr.getReferencesTo(ddc_sym.getAddress()))
print("References: {}".format(len(refs)))

# Find calling functions
callers = set()
for ref in refs:
    from_addr = ref.getFromAddress()
    func = fm.getFunctionContaining(from_addr)
    if func:
        callers.add(func)
        print("  Called from {} at {} (function: {} entry {})".format(
            ref.getFromAddress(), ref.getReferenceType(),
            func.getName(), func.getEntryPoint()))

# Also look for thunks
for func in list(callers):
    # Check if any other functions reference this function
    for ref2 in ref_mgr.getReferencesTo(func.getEntryPoint()):
        caller2 = fm.getFunctionContaining(ref2.getFromAddress())
        if caller2 and caller2 != func:
            print("  -> Also called from {}".format(caller2.getName()))

# Now search more broadly: find functions that contain "IDirectDraw" references
print("\nSearching for IDirectDraw interface references...")
for sym in sym_table.getAllSymbols(True):
    name = sym.getName()
    if "DirectDraw" in name and "IDirectDraw" not in name:
        continue
    if "IDirectDraw" in name or "DirectDrawSurface" in name or "DirectDrawPalette" in name:
        addr = sym.getAddress()
        refs = list(ref_mgr.getReferencesTo(addr))
        if refs:
            print("  Symbol '{}' at {} has {} refs".format(name, addr, len(refs)))
            for ref in refs[:5]:
                caller = fm.getFunctionContaining(ref.getFromAddress())
                if caller:
                    print("    -> {} in {}".format(ref.getFromAddress(), caller.getName()))
