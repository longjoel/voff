# Ghidra Python script -- trace window/DirectDraw initialization
# @category Analysis

from ghidra.program.model.symbol import RefType, SourceType

def find_import(program, dll_name, func_name):
    """Find an imported function by DLL and name using external manager."""
    ext_mgr = program.getExternalManager()
    ext_locs = ext_mgr.getExternalLocations(func_name)
    for loc in ext_locs:
        lib_name = loc.getLibraryName()
        if lib_name and lib_name.lower().startswith(dll_name.lower()):
            return loc.getExternalSpaceAddress()
    return None

def get_calling_functions(program, import_addr):
    """Find all functions that call this import."""
    ref_mgr = program.getReferenceManager()
    func_mgr = program.getFunctionManager()
    refs = ref_mgr.getReferencesTo(import_addr)
    callers = {}
    for ref in refs:
        from_addr = ref.getFromAddress()
        func = func_mgr.getFunctionContaining(from_addr)
        if func:
            name = func.getName()
            if name not in callers:
                callers[name] = []
            callers[name].append(from_addr)
    return callers

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

def dump_function_disasm(program, func, max_instr=50):
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

def find_string_refs(program, search_str):
    """Find data that references a given string."""
    ref_mgr = program.getReferenceManager()
    
    results = []
    for block in program.getMemory().getBlocks():
        if not block.isInitialized():
            continue
        start = block.getStart()
        end = block.getEnd()
        current = start
        while current < end:
            try:
                # Read a chunk and check first char
                b = getByte(current)
                if 32 <= b < 127:
                    # Read string until null
                    s = ""
                    p = current
                    for _ in range(128):
                        cb = getByte(p)
                        if cb == 0:
                            break
                        if 32 <= cb < 127:
                            s += chr(cb)
                        else:
                            break
                        p = p.add(1)
                    if search_str in s and len(s) >= len(search_str):
                        refs = ref_mgr.getReferencesTo(current)
                        ref_list = []
                        for r in refs:
                            ref_list.append(r.getFromAddress())
                        if ref_list:
                            results.append((current, s, ref_list))
                current = current.add(1)
            except:
                current = current.add(1)
                continue
    return results


def main():
    program = getCurrentProgram()
    listing = program.getListing()
    func_mgr = program.getFunctionManager()
    
    # Find window-related strings first
    print("=== WINDOW CLASS / TITLE STRINGS ===")
    window_strings = find_string_refs(program, "Virtual")
    for addr, s, refs in window_strings:
        print("  \"{}\" at {}".format(s[:40], addr))
        for r in refs[:5]:
            func = func_mgr.getFunctionContaining(r)
            fname = func.getName() if func else "(unknown)"
            print("    Referenced from: {} ({}())".format(r, fname))
    
    print()
    
    # Key imports
    interesting = [
        ("USER32.dll", "CreateWindowExA"),
        ("USER32.dll", "RegisterClassA"),
        ("USER32.dll", "ShowWindow"),
        ("USER32.dll", "UpdateWindow"),
        ("USER32.dll", "GetMessageA"),
        ("USER32.dll", "PeekMessageA"),
        ("USER32.dll", "DispatchMessageA"),
        ("USER32.dll", "DefWindowProcA"),
        ("USER32.dll", "GetDC"),
        ("USER32.dll", "GetClientRect"),
        ("USER32.dll", "SetCursor"),
        ("USER32.dll", "ShowCursor"),
        ("USER32.dll", "LoadCursorA"),
        ("USER32.dll", "LoadIconA"),
        ("USER32.dll", "SetWindowPos"),
        ("USER32.dll", "MessageBoxA"),
        ("KERNEL32.dll", "GetModuleHandleA"),
        ("DDRAW.dll", "DirectDrawCreate"),
    ]
    
    print("=== WINDOW / DIRECTDRAW IMPORTS ===\n")
    
    for dll, func_name in interesting:
        addr = find_import(program, dll, func_name)
        if addr:
            callers = get_calling_functions(program, addr)
            if callers:
                print("--- {}!{} ---".format(dll, func_name))
                print("  Called from {} functions:".format(len(callers)))
                for fname, sites in callers.items():
                    print("    {}() called from: {}".format(fname, [str(s) for s in sites[:5]]))
                print()
            else:
                print("--- {}!{} ---  (no callers)".format(dll, func_name))
        else:
            # Try ordinal search
            print("--- {}!{} ---  NOT FOUND via external name".format(dll, func_name))
    
    # Look at entry point function and its call chain
    print("\n=== ENTRY POINT ANALYSIS ===")
    entry = program.getImageBase().add(0x1E7930)
    entry_func = func_mgr.getFunctionContaining(entry)
    
    if entry_func:
        print("Entry: {}()".format(entry_func.getName()))
        c = decompile_function(program, entry_func)
        if c:
            c_short = c[:3000]
            print("\n  Decompiled:\n{}".format(c_short))
        
        # Show what functions it calls (first 40 instructions)
        print("\n  First 40 instructions:")
        print(dump_function_disasm(program, entry_func, 40))
    
    # Find functions called from entry that look like init functions
    print("\n=== CALL CHAIN FROM ENTRY ===")
    if entry_func:
        entry_body = entry_func.getBody()
        instr = listing.getInstructionAt(entry_func.getEntryPoint())
        called_funcs = set()
        count = 0
        while instr is not None and count < 100 and entry_body.contains(instr.getAddress()):
            if instr.getFlowType().isCall():
                for op_idx in range(instr.getNumOperands()):
                    op_refs = instr.getOperandReferences(op_idx)
                    for ref in op_refs:
                        target = ref.getToAddress()
                        func = func_mgr.getFunctionContaining(target)
                        if func:
                            called_funcs.add((str(instr.getAddress()), func.getName(), func.getEntryPoint()))
            instr = instr.getNext()
            count += 1
        
        print("Functions called from entry:")
        for call_addr, fname, fentry in sorted(called_funcs):
            print("  at {} -> {}() at {}".format(call_addr, fname, fentry))

if __name__ == "__main__":
    main()
