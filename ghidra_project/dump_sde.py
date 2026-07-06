# Ghidra Python script: dump SDE string references and surrounding data
# @category Analysis
# Run via: analyzeHeadless ... -postScript dump_sde.py

from ghidra.program.model.symbol import RefType
from ghidra.program.model.listing import CodeUnit

def main():
    program = getCurrentProgram()
    listing = program.getListing()
    addressFactory = program.getAddressFactory()
    
    data_section = None
    for block in program.getMemory().getBlocks():
        if block.getName() == ".data":
            data_section = block
            break
    
    if data_section is None:
        print("ERROR: .data section not found")
        return
    
    start = data_section.getStart()
    end = data_section.getEnd()
    current = start
    
    sde_count = 0
    sde_entries = []
    
    print("Scanning .data for SDE_ strings...")
    while current < end:
        try:
            b = getByte(current)
            if b == 83:
                bs = [getByte(current.add(i)) for i in range(4)]
                if bs == [83, 68, 69, 95]:
                    sde_start = current
                    s = ""
                    p = current
                    while True:
                        b = getByte(p)
                        if b == 0:
                            break
                        if 32 <= b < 127:
                            s += chr(b)
                        else:
                            s += "."
                        p = p.add(1)
                    
                    sde_entries.append((sde_start, s))
                    sde_count += 1
                    current = p.add(1)
                    continue
        except:
            pass
        current = current.add(1)
    
    print("Found {} SDE_ entries".format(sde_count))
    
    print("\n=== SDE STRING CROSS-REFERENCES ===")
    for addr, name in sde_entries:
        refs = getReferencesTo(addr)
        if refs:
            for ref in refs:
                ref_addr = ref.getFromAddress()
                ref_type = ref.getReferenceType()
                print("  {:<40s} @ {}  <-  {} ({})".format(name, addr, ref_addr, ref_type))
    
    print("\n=== RAW DATA AROUND FIRST 5 SDE ENTRIES ===")
    for i, (addr, name) in enumerate(sde_entries[:5]):
        print("\n  {} @ {}:".format(name, addr))
        for offset in range(-32, 64, 4):
            try:
                val = getInt(addr.add(offset))
                fval = getFloat(addr.add(offset))
                marker = " <-- SDE" if offset == 0 else ""
                print("    [{:+4d}] 0x{:08x} (int={}, float={:.4f}){}".format(
                    offset, val & 0xFFFFFFFF, val, fval, marker))
            except:
                pass

if __name__ == "__main__":
    main()
