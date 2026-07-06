# Ghidra Python script -- deep dive on window init functions
# @category Analysis

from ghidra.program.model.symbol import RefType, SourceType


def decompile_function(program, func):
    """Decompile a function."""
    try:
        from ghidra.app.decompiler import DecompInterface
        decomp = DecompInterface()
        decomp.openProgram(program)
        result = decomp.decompileFunction(func, 60, None)
        if result and result.decompileCompleted():
            return result.getDecompiledFunction().getC()
    except:
        pass
    return None


def dump_function_disasm(program, func, max_instr=80):
    """Show disassembly for a function."""
    listing = program.getListing()
    lines = []
    instr = listing.getInstructionAt(func.getEntryPoint())
    count = 0
    while instr is not None and count < max_instr and func.getBody().contains(instr.getAddress()):
        lines.append("    {}  {}".format(instr.getAddress(), instr))
        instr = instr.getNext()
        count += 1
    return "\n".join(lines)


def get_calls_from(program, func):
    """Get all function calls made by a function."""
    listing = program.getListing()
    func_mgr = program.getFunctionManager()
    body = func.getBody()
    instr = listing.getInstructionAt(func.getEntryPoint())
    calls = []
    while instr is not None and body.contains(instr.getAddress()):
        if instr.getFlowType().isCall():
            for op_idx in range(instr.getNumOperands()):
                op_refs = instr.getOperandReferences(op_idx)
                for ref in op_refs:
                    target = ref.getToAddress()
                    called = func_mgr.getFunctionContaining(target)
                    if called:
                        calls.append((instr.getAddress(), called))
                        break
        instr = instr.getNext()
    return calls


def dump_all_strings_in_func(program, func):
    """Find all string references within a function body."""
    listing = program.getListing()
    ref_mgr = program.getReferenceManager()
    body = func.getBody()
    strings = []
    
    instr = listing.getInstructionAt(func.getEntryPoint())
    while instr is not None and body.contains(instr.getAddress()):
        for op_idx in range(instr.getNumOperands()):
            op_refs = instr.getOperandReferences(op_idx)
            for ref in op_refs:
                target = ref.getToAddress()
                data = listing.getDataAt(target)
                if data and data.hasStringValue():
                    strings.append((instr.getAddress(), str(data.getValue())))
        instr = instr.getNext()
    return strings


def main():
    program = getCurrentProgram()
    func_mgr = program.getFunctionManager()
    sym_table = program.getSymbolTable()
    listing = program.getListing()
    
    # From our string search, the key window init function is FUN_005c5909
    # "VirtualONClass" is referenced from 0x5c5960 (FUN_005c5909)
    # "Virtual ON for PC" is referenced from 0x5c59ea (FUN_005c59a9)
    
    # Find these functions
    addr_factory = program.getAddressFactory()
    space = addr_factory.getDefaultAddressSpace()
    
    # FUN_005c5909 - RegisterClass caller
    func_addr = space.getAddress(0x5c5909)
    wnd_class_func = func_mgr.getFunctionContaining(func_addr)
    
    if wnd_class_func:
        print("=== WINDOW CLASS REGISTRATION: {}() ===".format(wnd_class_func.getName()))
        print("  Entry: {}".format(wnd_class_func.getEntryPoint()))
        print("  Body: {}".format(wnd_class_func.getBody()))
        
        strings = dump_all_strings_in_func(program, wnd_class_func)
        if strings:
            print("  Strings referenced:")
            for addr, s in strings[:15]:
                print("    {}: \"{}\"".format(addr, s))
        
        c = decompile_function(program, wnd_class_func)
        if c:
            print("\n  Decompiled:\n{}".format(c))
        print()
    
    # FUN_005c59a9 - CreateWindowEx caller
    func_addr2 = space.getAddress(0x5c59a9)
    create_wnd_func = func_mgr.getFunctionContaining(func_addr2)
    
    if create_wnd_func != wnd_class_func:
        if create_wnd_func:
            print("=== WINDOW CREATION: {}() ===".format(create_wnd_func.getName()))
            print("  Entry: {}".format(create_wnd_func.getEntryPoint()))
            print("  Body: {}".format(create_wnd_func.getBody()))
            
            strings = dump_all_strings_in_func(program, create_wnd_func)
            if strings:
                print("  Strings referenced:")
                for addr, s in strings[:15]:
                    print("    {}: \"{}\"".format(addr, s))
            
            c = decompile_function(program, create_wnd_func)
            if c:
                print("\n  Decompiled:\n{}".format(c))
            print()
    
    # FUN_005c5a45 - another function referencing window title
    func_addr3 = space.getAddress(0x5c5a45)
    wnd_func3 = func_mgr.getFunctionContaining(func_addr3)
    
    if wnd_func3 and wnd_func3 != wnd_class_func and wnd_func3 != create_wnd_func:
        print("=== FUN_005c5a45: {}() ===".format(wnd_func3.getName()))
        strings = dump_all_strings_in_func(program, wnd_func3)
        if strings:
            print("  Strings referenced:")
            for addr, s in strings[:15]:
                print("    {}: \"{}\"".format(addr, s))
        c = decompile_function(program, wnd_func3)
        if c:
            print("\n  Decompiled:\n{}".format(c))
        print()
    
    # FUN_005c5c7a - another
    func_addr4 = space.getAddress(0x5c5c7a)
    wnd_func4 = func_mgr.getFunctionContaining(func_addr4)
    
    if wnd_func4 and wnd_func4 != wnd_class_func and wnd_func4 != create_wnd_func and wnd_func4 != wnd_func3:
        print("=== FUN_005c5c7a: {}() ===".format(wnd_func4.getName()))
        strings = dump_all_strings_in_func(program, wnd_func4)
        if strings:
            print("  Strings referenced:")
            for addr, s in strings[:15]:
                print("    {}: \"{}\"".format(addr, s))
        c = decompile_function(program, wnd_func4)
        if c:
            print("\n  Decompiled:\n{}".format(c))
        print()
    
    # Also: FUN_00566ea9 references "Virtual ON" 
    func_addr5 = space.getAddress(0x566ea9)
    von_func = func_mgr.getFunctionContaining(func_addr5)
    if von_func:
        print("=== VIRTUAL ON STRING USER: {}() ===".format(von_func.getName()))
        strings = dump_all_strings_in_func(program, von_func)
        if strings:
            print("  Strings referenced:")
            for addr, s in strings[:10]:
                print("    {}: \"{}\"".format(addr, s))
        
        # Show calls from this function
        calls = get_calls_from(program, von_func)
        if calls:
            print("  Functions called:")
            for call_addr, called in calls[:20]:
                print("    {} -> {}()".format(call_addr, called.getName()))
        
        c = decompile_function(program, von_func)
        if c:
            print("\n  Decompiled:\n{}".format(c[:2000]))
        print()
    
    # Entry point also calls FUN_00566ea9 
    print("\n=== ENTRY POINT FLOW ===")
    entry = space.getAddress(0x1E7930)
    entry_func = func_mgr.getFunctionContaining(entry)
    if entry_func:
        calls = get_calls_from(program, entry_func)
        print("Entry {}() calls:".format(entry_func.getName()))
        for call_addr, called in calls:
            if called:
                print("  at {} -> {}()".format(call_addr, called.getName()))


if __name__ == "__main__":
    main()
