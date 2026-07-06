# Ghidra Python script -- find MMX CPU check for patching
# @category Analysis

def decompile_function(program, func):
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

def main():
    program = getCurrentProgram()
    listing = program.getListing()
    func_mgr = program.getFunctionManager()
    
    # FUN_005c6311 is the CPU check function
    # The MMX check is in FUN_005c5c7a after calling FUN_005c6311
    # local_30 = FUN_005c6311();
    # if ((local_30 == 0x33) || (local_30 == 0x3d)) { ... }
    
    space = program.getAddressFactory().getDefaultAddressSpace()
    
    # First, decompile the CPU check function itself
    cpu_check_addr = space.getAddress(0x5c6311)
    cpu_check_func = func_mgr.getFunctionContaining(cpu_check_addr)
    if cpu_check_func:
        print("=== CPU CHECK FUNCTION: {}() ===".format(cpu_check_func.getName()))
        print("  Entry: {}".format(cpu_check_func.getEntryPoint()))
        print("  Body: {}".format(cpu_check_func.getBody()))
        c = decompile_function(program, cpu_check_func)
        if c:
            print("  Decompiled:\n{}".format(c))
        print()
    
    # Now find the exact comparison in FUN_005c5c7a
    main_loop_addr = space.getAddress(0x5c5c7a)
    main_loop_func = func_mgr.getFunctionContaining(main_loop_addr)
    
    if main_loop_func:
        print("=== MMX CHECK IN MAIN LOOP: {}() ===".format(main_loop_func.getName()))
        
        # Find the call to FUN_005c6311 and subsequent comparison
        body = main_loop_func.getBody()
        instr = listing.getInstructionAt(main_loop_func.getEntryPoint())
        
        while instr is not None and body.contains(instr.getAddress()):
            # Look for CALL to FUN_005c6311
            if instr.getFlowType().isCall():
                for op_idx in range(instr.getNumOperands()):
                    op_refs = instr.getOperandReferences(op_idx)
                    for ref in op_refs:
                        target = ref.getToAddress()
                        if target.getOffset() == 0x5c6311:
                            call_addr = instr.getAddress()
                            print("  Found call to CPU check at: {}".format(call_addr))
                            
                            # Show surrounding instructions (context)
                            ctx_instr = instr
                            # Walk backward to find function call context
                            prev_instrs = []
                            p = listing.getInstructionBefore(call_addr)
                            for _ in range(5):
                                if p:
                                    prev_instrs.append(p)
                                    p = listing.getInstructionBefore(p.getAddress())
                            
                            print("  Before:")
                            for i in reversed(prev_instrs):
                                print("    {}  {}".format(i.getAddress(), i))
                            
                            print("    {}  {}  <-- CALL CPU CHECK".format(call_addr, instr))
                            
                            # Walk forward to find comparison and branch
                            next_instr = listing.getInstructionAfter(instr.getAddress())
                            count = 0
                            while next_instr and count < 15:
                                mnemonic = str(next_instr.getMnemonicString()).upper()
                                # Look for CMP or conditional jumps
                                if mnemonic in ["CMP", "TEST", "JE", "JNE", "JZ", "JNZ", "JA", "JB", "JG", "JL", "JMP"]:
                                    mark = ""
                                    if mnemonic in ["CMP", "TEST"]:
                                        # Check operands for 0x33 or 0x3d
                                        ops = str(next_instr)
                                        if "33" in ops or "3d" in ops or "0x33" in ops or "3D" in ops.upper() or "0x3d" in ops:
                                            mark = "  <-- COMPARING AGAINST 0x33/0x3d"
                                    if mnemonic.startswith("J"):
                                        mark = "  <-- CONDITIONAL BRANCH"
                                    print("    {}  {}{}".format(next_instr.getAddress(), next_instr, mark))
                                elif mnemonic in ["CALL", "RET", "MOV"]:
                                    # Might be relevant
                                    ops = str(next_instr)
                                    if "33" in ops or "3d" in ops or "0x33" in ops or "0x3D" in ops:
                                        print("    {}  {}  <-- VALUE 0x33/0x3d".format(next_instr.getAddress(), next_instr))
                                
                                next_instr = listing.getInstructionAfter(next_instr.getAddress())
                                count += 1
                            
                            print()
                            break
                if target.getOffset() == 0x5c6311:
                    break
            instr = instr.getNext()
        
        # Also show raw hex bytes around the call site for patching
        print("\n=== PATCH SUGGESTIONS ===")
        print("The check is: call FUN_005c6311; cmp eax, 0x33; je ok; cmp eax, 0x3d; je ok; (else show error)")
        print("Patch: change the first conditional jump to unconditional, or force cmp to always match.")
        print("Simplest: NOP the call + move al,0x33 (so the check always passes)")
        print()
        print("Analyze the exact bytes at the call site to craft the patch.")
        print("Call to FUN_005c6311 is at some address; replace it with:")
        print("  mov eax, 0x33    (b8 33 00 00 00)")
        print("  nop               (90) for remaining call bytes")

if __name__ == "__main__":
    main()
