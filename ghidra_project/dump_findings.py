# Ghidra Python script -- dump SDE-related functions and data
# @category Analysis

from ghidra.program.model.symbol import RefType, SymbolType
from ghidra.program.model.listing import CodeUnit


def find_sde_table(program):
    listing = program.getListing()
    addr_factory = program.getAddressFactory()
    
    sde_table_addr = addr_factory.getDefaultAddressSpace().getAddress(0x69BA10)
    
    try:
        ptr = program.getMemory().getInt(sde_table_addr)
        if ptr:
            str_addr = addr_factory.getDefaultAddressSpace().getAddress(ptr)
            data = listing.getDataAt(str_addr)
            if data and data.hasStringValue():
                print("SDE table found at {}".format(sde_table_addr))
                print("  First entry: points to \"{}\"".format(data.getValue()))
                return sde_table_addr
    except:
        pass
    
    return sde_table_addr


def getReferencesTo(addr):
    program = getCurrentProgram()
    return program.getReferenceManager().getReferencesTo(addr)


def getFunctionContaining(addr):
    program = getCurrentProgram()
    return program.getFunctionManager().getFunctionContaining(addr)


def dump_sde_entries(program, table_addr):
    listing = program.getListing()
    addr_factory = program.getAddressFactory()
    mem = program.getMemory()
    
    entries = []
    for i in range(176):
        addr = table_addr.add(i * 4)
        ptr = mem.getInt(addr)
        if ptr == 0 or ptr == 0x63F030:
            continue
        
        str_addr = addr_factory.getDefaultAddressSpace().getAddress(ptr)
        data = listing.getDataAt(str_addr)
        if data and data.hasStringValue():
            s = str(data.getValue())
            if s.startswith("SDE_"):
                entries.append((i, ptr, s, str_addr))
    
    print("\n=== SDE ENTRIES ({} active) ===".format(len(entries)))
    
    for i, ptr, name, str_addr in entries[:20]:
        refs_iter = getReferencesTo(str_addr)
        refs_list = []
        funcs = set()
        try:
            for r in refs_iter:
                refs_list.append(r)
                func = getFunctionContaining(r.getFromAddress())
                if func:
                    funcs.add(func.getName())
        except:
            pass
        ref_locs = [str(r.getFromAddress()) for r in refs_list]
        print("  [{:3d}] \"{}\" -> refs={} funcs={}".format(
            i, name, len(refs_list), list(funcs)[:3]))
    
    return entries


def dump_float_regions(program):
    """Find float-heavy regions in .rdata"""
    rdata_block = None
    for block in program.getMemory().getBlocks():
        if block.getName() == ".rdata":
            rdata_block = block
            break
    
    if rdata_block is None:
        print("\nERROR: .rdata section not found")
        return
    
    start = rdata_block.getStart()
    end = rdata_block.getEnd()
    
    print("\n=== FLOAT REGIONS IN .rdata ===")
    
    current = start
    regions = []
    in_float_region = False
    region_start = None
    float_count = 0
    
    while current < end:
        try:
            # Read 4 bytes as float
            raw = [getByte(current.add(i)) & 0xFF for i in range(4)]
            f = getFloat(current)
            
            # Check if value looks like a reasonable float (not NaN/inf, not extreme)
            is_reasonable = (abs(f) < 10000.0 and f == f and abs(f) >= 0.001)
            
            if is_reasonable:
                if not in_float_region:
                    region_start = current
                    float_count = 0
                    in_float_region = True
                float_count += 1
            else:
                if in_float_region and float_count >= 8:
                    regions.append((region_start, float_count, region_start.getOffset()))
                    if len(regions) <= 40:
                        # Print the first few values
                        vals = []
                        rptr = region_start
                        for j in range(min(float_count, 15)):
                            vals.append("{:.2f}".format(getFloat(rptr)))
                            rptr = rptr.add(4)
                        print("  RVA 0x{:08x}: {} floats: [{}...]".format(
                            region_start.getOffset(), float_count, ", ".join(vals)))
                
                in_float_region = False
                float_count = 0
            
            current = current.add(4)
        except:
            current = current.add(4)
    
    print("\n  Total float regions found: {}".format(len(regions)))
    return regions


def dump_function_disasm(program):
    """Decompile the SDE table indexing function"""
    addr_factory = program.getAddressFactory()
    listing = program.getListing()
    
    func_addr = addr_factory.getDefaultAddressSpace().getAddress(0x4F2559)
    func = getFunctionContaining(func_addr)
    
    if func:
        print("\n=== FUNCTION using SDE table ===")
        print("  Name: {}".format(func.getName()))
        print("  Entry: {}".format(func.getEntryPoint()))
        print("  Body: {}".format(func.getBody()))
        
        # Show disassembly (first 30 instructions)
        print("\n  Disassembly (first 30 instructions):")
        instr = listing.getInstructionAt(func.getEntryPoint())
        count = 0
        while instr is not None and count < 30 and func.getBody().contains(instr.getAddress()):
            print("    {}  {}".format(instr.getAddress(), instr))
            instr = instr.getNext()
            count += 1
        
        # Try to decompile
        try:
            from ghidra.app.decompiler import DecompInterface
            decomp = DecompInterface()
            decomp.openProgram(program)
            result = decomp.decompileFunction(func, 30, None)
            if result and result.decompileCompleted():
                c_code = result.getDecompiledFunction().getC()
                print("\n  Decompiled:\n{}".format(c_code))
            else:
                print("\n  Decompile failed or incomplete")
        except Exception as e:
            print("\n  Decompile error: {}".format(e))
    else:
        print("Function not found at 0x4F2559, searching for SDE table usage...")
        
        # Fallback: search for instructions that reference the SDE table
        ref_mgr = program.getReferenceManager()
        sde_table_addr = addr_factory.getDefaultAddressSpace().getAddress(0x69BA10)
        refs = ref_mgr.getReferencesTo(sde_table_addr)
        
        if refs:
            refs_list = list(refs)
            print("  Found {} references to SDE table at 0x69BA10:".format(len(refs_list)))
            for ref in refs_list:
                from_addr = ref.getFromAddress()
                func = getFunctionContaining(from_addr)
                if func:
                    print("    {} -> {} (function: {})".format(from_addr, ref.getReferenceType(), func.getName()))
                    print("      Entry: {}, Body: {}".format(func.getEntryPoint(), func.getBody()))
        else:
            print("  No direct references to SDE table found. Searching for address pattern...")
            # Search in .text for mov instructions with the table offset
            text_block = None
            for block in program.getMemory().getBlocks():
                if block.getName() == ".text":
                    text_block = block
                    break
            if text_block:
                print("  Scanning .text for 0x69BA10 references...")
                cur = text_block.getStart()
                end = text_block.getEnd()
                found = 0
                while cur < end and found < 10:
                    try:
                        instr = listing.getInstructionAt(cur)
                        if instr:
                            # Check if instruction references our table
                            op_refs = instr.getOperandReferences(0)
                            for op_ref in op_refs:
                                if op_ref.getToAddress().getOffset() == 0x69BA10:
                                    f = getFunctionContaining(instr.getAddress())
                                    fname = f.getName() if f else "(no function)"
                                    print("    {} {} -> in function: {}".format(
                                        instr.getAddress(), instr, fname))
                                    found += 1
                            cur = instr.getAddress().add(instr.getLength())
                        else:
                            cur = cur.add(1)
                    except:
                        cur = cur.add(1)
                        continue


def main():
    program = getCurrentProgram()
    print("Program: {}".format(program.getName()))
    print("Image base: {}".format(program.getImageBase()))
    
    funcs = list(program.getFunctionManager().getFunctions(True))
    print("Functions: {}".format(len(funcs)))
    
    table_addr = find_sde_table(program)
    if table_addr:
        entries = dump_sde_entries(program, table_addr)
        dump_function_disasm(program)
        dump_float_regions(program)

if __name__ == "__main__":
    main()
