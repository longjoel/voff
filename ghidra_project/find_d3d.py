# Ghidra script — find D3D initialization code
# Look for: QueryInterface on IDirectDraw to get IDirect3D
# IDirectDraw vtable offset 0x00 = QueryInterface
# IDirect3D vtable offsets for CreateDevice, EnumDevices, etc.

import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

program = getCurrentProgram()
fm = program.getFunctionManager()
ref_mgr = program.getReferenceManager()
listing = program.getListing()
sym_table = program.getSymbolTable()
addr_space = program.getAddressFactory().getDefaultAddressSpace()

OUT = "/var/home/longjoel/Projects/voff/out_decompile"

decompiler = DecompInterface()
decompiler.openProgram(program)

# Strategy: Find functions that call through the IDirectDraw vtable
# Pattern: (**(code **)(*lpDD + OFFSET))(args)  
# Common D3D offsets on IDirectDraw:
#   0x00 = QueryInterface (to get IDirect3D)
#   0x18 = Initialize (DEPRECATED in D3D, use QueryInterface)

# Also search for GUID references: 
# IID_IDirect3D = {0x3BBA0080, 0x2421, 0x11CF, {0xA3,0x1A,0x00,0xAA,0x00,0xB9,0x33,0x56}}
# IID_IDirect3DDevice = ...
# IID_IDirect3DExecuteBuffer = ...

# Search in .rdata for these GUID bytes
# Actually, let's find functions that reference the execute buffer creation
# Look for "Execute" in symbol names and strings

print("=== Searching for D3D-related code ===")

# METHOD 1: Look for vtable calls at specific offsets
# Scan .text for instructions that read lpDD->lpVtbl and call a method
d3d_caller_funcs = set()

# Look for functions containing *(lpDD + 0) pattern (vtable dereference)
# and subsequent call through offset patterns like + 0x18, + 0x1C, etc.
for func in fm.getFunctions(True):
    name = func.getName()
    if not name.startswith("FUN_"):
        continue
    
    body = func.getBody()
    if body is None or body.getNumAddresses() > 10000:  # Skip huge functions
        continue
    
    # Check if function contains calls through vtable pointers
    instr = listing.getInstructionAt(func.getEntryPoint())
    has_vtable_call = False
    while instr and body.contains(instr.getAddress()):
        mnem = str(instr.getMnemonicString())
        # Look for indirect call patterns
        if mnem in ("CALL", "CALLF") and "=>" in str(instr):
            has_vtable_call = True
            break
        instr = instr.getNext()
    
    if has_vtable_call:
        d3d_caller_funcs.add(func.getEntryPoint().getOffset())

print("Found {} functions with indirect calls".format(len(d3d_caller_funcs)))

# METHOD 2: Search for the specific D3D GUID patterns in .rdata
rdata_block = program.getMemory().getBlock(".rdata")
if rdata_block:
    start = rdata_block.getStart()
    end = rdata_block.getEnd()
    addr = start
    found_guids = []
    while addr < end:
        try:
            b0 = program.getMemory().getByte(addr)
            # IID_IDirect3D starts with 0x3BBA0080
            if b0 == 0x3B:
                b1 = program.getMemory().getByte(addr.add(1))
                if b1 == 0xBA:
                    # Check what references this address
                    refs = list(ref_mgr.getReferencesTo(addr))
                    if refs:
                        found_guids.append((addr, len(refs)))
        except:
            pass
        addr = addr.add(1)
    
    print("Found {} GUID-like references in .rdata".format(len(found_guids)))
    for addr, nrefs in found_guids[:10]:
        print("  {} has {} references".format(addr, nrefs))

# METHOD 3: Look for strings "Direct3D" or "D3D" in data sections
for block in program.getMemory().getBlocks():
    if ".rdata" in block.getName() or ".data" in block.getName():
        addr = block.getStart()
        end = block.getEnd()
        try:
            data = program.getListing().getDataAt(addr)
            while addr < end:
                data = program.getListing().getDataAt(addr)
                if data and data.hasStringValue():
                    s = str(data.getValue())
                    if "Direct3D" in s or "D3D" in s:
                        refs = list(ref_mgr.getReferencesTo(addr))
                        if refs:
                            print("  String '{}' at {}: {} refs".format(s, addr, len(refs)))
                            for ref in refs[:3]:
                                caller = fm.getFunctionContaining(ref.getFromAddress())
                                if caller:
                                    print("    -> {} in {}".format(ref.getFromAddress(), caller.getName()))
                addr = addr.add(1)
        except:
            pass

print("\n=== Key D3D init function candidates ===")
# Decompile the most promising ones
key_funcs = sorted(d3d_caller_funcs)
key_funcs = key_funcs[:20]  # limit for speed

results = []
for va in key_funcs[:10]:
    func = fm.getFunctionAt(addr_space.getAddress(va))
    if func is None:
        continue
    name = func.getName()
    c = None
    try:
        result = decompiler.decompileFunction(func, 30, ConsoleTaskMonitor())
        if result and result.decompileCompleted():
            c = result.getDecompiledFunction().getC()
    except:
        pass
    
    if c:
        c = c.replace("__cdecl(", "(")
        c = c.replace("__thiscall ", "")
        c = c.replace("__stdcall ", "")
        results.append((va, name, c))
        print("  {:08x} {}: {} lines".format(va, name, c.count("\n")))

# Write results
with open(os.path.join(OUT, "d3d_findings.txt"), "w") as f:
    f.write("=== D3D callers ===\n")
    for va, name, c in results:
        f.write("\n/* {:08x} {} */\n".format(va, name))
        f.write(c)
        f.write("\n")

print("\nWrote findings to d3d_findings.txt")
