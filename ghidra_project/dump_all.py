# Ghidra Python script -- decompile ALL functions to organized C files
# @category Analysis

import os, sys, time
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

BASE = "/var/home/longjoel/Projects/voff/out_decompile"
SRC_DIR   = os.path.join(BASE, "src")
HEADER_H  = os.path.join(BASE, "voff_all.h")
STUBS_C   = os.path.join(BASE, "voff_stubs.c")
INDEX_TXT = os.path.join(BASE, "function_index.txt")
CALLGRAPH  = os.path.join(BASE, "call_graph.txt")

BATCH_SIZE = 200
DECOMPILE_TIMEOUT = 15  # seconds per function

def ensure_dirs():
    for d in [SRC_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def sanitize(name):
    out = []
    for c in name:
        if c.isalnum() or c == '_':
            out.append(c)
        else:
            out.append('_')
    return ''.join(out)

def func_filename(func):
    addr = func.getEntryPoint().getOffset()
    name = sanitize(func.getName())
    return "f_{:08x}__{}.c".format(addr, name)

def func_section(func):
    """Determine which section a function belongs to"""
    addr = func.getEntryPoint().getOffset()
    if addr < 0x005F5000: return ".text"
    if addr < 0x0063F000: return ".rdata"
    return ".data"

def main():
    program = getCurrentProgram()
    listing = program.getListing()
    fm = program.getFunctionManager()
    ref_mgr = program.getReferenceManager()
    sym_table = program.getSymbolTable()

    ensure_dirs()

    decompiler = DecompInterface()
    decompiler.openProgram(program)

    all_funcs = sorted(list(fm.getFunctions(True)),
                       key=lambda f: f.getEntryPoint().getOffset())
    total = len(all_funcs)
    print("Total functions: {}".format(total))

    # ================================================================
    # PHASE 1: Collect all function signatures and global data refs
    # ================================================================
    print("\n[Phase 1] Collecting signatures and references...")

    all_decls = []       # (func_name, return_type, params, rva_str)
    all_globals = set()  # DAT_xxx, PTR_xxx, s_xxx
    all_imports = set()  # import function names
    call_graph = {}      # caller -> set(callee names)

    for i, func in enumerate(all_funcs):
        if (i % 500) == 0:
            print("  Collecting {}/{}...".format(i + 1, total))

        name = func.getName()
        entry_va = func.getEntryPoint().getOffset()
        rva_str = "{:08x}".format(entry_va)

        # Signature
        sig = func.getSignature()
        ret = "void"
        params_str = "void"
        try:
            ret_type = sig.getReturnType()
            if ret_type:
                ret = str(ret_type).replace("undefined", "uint8_t").strip()
            args = sig.getArguments()
            if args and len(args) > 0:
                plist = []
                for j, arg in enumerate(args):
                    dt = str(arg.getDataType()).replace("undefined", "uint8_t")
                    plist.append("{} p{}".format(dt, j))
                params_str = ", ".join(plist)
        except:
            pass

        decl = "{} {}({})".format(ret, name, params_str)
        all_decls.append((name, ret, params_str, rva_str))

        # Collect globals referenced in this function
        try:
            body = func.getBody()
            if body:
                instr = listing.getInstructionAt(func.getEntryPoint())
                count = 0
                while instr and body.contains(instr.getAddress()) and count < 500:
                    for ref in ref_mgr.getReferencesFrom(instr.getAddress()):
                        to_addr = ref.getToAddress()
                        to_sym = sym_table.getPrimarySymbol(to_addr)
                        if to_sym:
                            sname = to_sym.getName()
                            if sname.startswith(("DAT_", "PTR_", "s_", "FUN_")):
                                if sname.startswith("FUN_"):
                                    if sname != name:
                                        call_graph.setdefault(name, set()).add(sname)
                                else:
                                    all_globals.add(sname)
                    count += 1
                    instr = instr.getNext()
        except:
            pass

    print("  {} function declarations".format(len(all_decls)))
    print("  {} unique global references".format(len(all_globals)))
    print("  {} edges in call graph".format(sum(len(v) for v in call_graph.values())))

    # ================================================================
    # PHASE 2: Decompile all functions, write to files
    # ================================================================
    print("\n[Phase 2] Decompiling {} functions...".format(total))

    successes = 0
    failures = 0

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        print("  Batch {}-{} / {}...".format(batch_start + 1, batch_end, total))

        for i in range(batch_start, batch_end):
            func = all_funcs[i]
            name = func.getName()
            entry_va = func.getEntryPoint().getOffset()

            c_code = None
            try:
                result = decompiler.decompileFunction(func, DECOMPILE_TIMEOUT,
                                                      ConsoleTaskMonitor())
                if result and result.decompileCompleted():
                    c_code = result.getDecompiledFunction().getC()
            except:
                pass

            fname = func_filename(func)
            fpath = os.path.join(SRC_DIR, fname)

            with open(fpath, "w") as f:
                f.write("/* {} at VA {:08x} */\n".format(name, entry_va))
                f.write('#include "../voff_all.h"\n\n')

                if c_code:
                    # Clean up calling conventions
                    c_code = c_code.replace("__cdecl(", "(")
                    c_code = c_code.replace("__thiscall ", "")
                    c_code = c_code.replace("__stdcall ", "")
                    c_code = c_code.replace("__fastcall ", "")
                    f.write(c_code)
                    successes += 1
                else:
                    f.write("/* DECOMPILE FAILED - stub */\n")
                    sig = func.getSignature()
                    proto = sig.getPrototypeString() if sig else "void {}()".format(name)
                    f.write("{} {{ /* failed */ }}\n".format(proto))
                    failures += 1

        if (batch_start % 1000) == 0 and batch_start > 0:
            print("    Progress: {} done, {} ok, {} failed".format(
                batch_start, successes, failures))

    print("  Done: {} decompiled OK, {} failed".format(successes, failures))

    # ================================================================
    # PHASE 3: Generate header
    # ================================================================
    print("\n[Phase 3] Generating header...")

    h_lines = []
    h_lines.append("/* AUTO-GENERATED VOFF decompiled header */\n")
    h_lines.append("/* {} functions, {} globals */\n".format(total, len(all_globals)))
    h_lines.append("#ifndef VOFF_ALL_H\n")
    h_lines.append("#define VOFF_ALL_H\n\n")

    h_lines.append("#define WIN32_LEAN_AND_MEAN\n")
    h_lines.append("#include <windows.h>\n")
    h_lines.append("#include <mmsystem.h>\n")
    h_lines.append("#include <commctrl.h>\n")
    h_lines.append("#include <ddraw.h>\n")
    h_lines.append("#include <dsound.h>\n")
    h_lines.append("#include <dinput.h>\n")
    h_lines.append("#include <dplay.h>\n")
    h_lines.append("#include <stdio.h>\n")
    h_lines.append("#include <stdlib.h>\n")
    h_lines.append("#include <string.h>\n")
    h_lines.append("#include <math.h>\n")
    h_lines.append("#include <stdint.h>\n")
    h_lines.append("#include <stdbool.h>\n\n")

    h_lines.append("/* === Ghidra type aliases === */\n")
    h_lines.append("typedef uint8_t  undefined;\n")
    h_lines.append("typedef uint16_t undefined2;\n")
    h_lines.append("typedef uint32_t undefined4;\n")
    h_lines.append("typedef uint64_t undefined8;\n")
    h_lines.append("typedef uint8_t  byte;\n")
    h_lines.append("typedef uint16_t word;\n")
    h_lines.append("typedef uint32_t dword;\n")
    h_lines.append("typedef void *   code;\n\n")

    h_lines.append("/* === LOGGING === */\n")
    h_lines.append("#define VOFF_LOG 1\n")
    h_lines.append("#if VOFF_LOG\n")
    h_lines.append("  #define LOG_ENTER(fmt, ...) \\\n")
    h_lines.append("    fprintf(stderr, \"[VOFF] ENTER %s: \" fmt \"\\n\", __func__, ##__VA_ARGS__)\n")
    h_lines.append("  #define LOG_EXIT(fmt, ...) \\\n")
    h_lines.append("    fprintf(stderr, \"[VOFF] EXIT  %s: \" fmt \"\\n\", __func__, ##__VA_ARGS__)\n")
    h_lines.append("  #define LOG_INFO(fmt, ...) \\\n")
    h_lines.append("    fprintf(stderr, \"[VOFF] INFO  %s: \" fmt \"\\n\", __func__, ##__VA_ARGS__)\n")
    h_lines.append("  #define LOG_WARN(fmt, ...) \\\n")
    h_lines.append("    fprintf(stderr, \"[VOFF] WARN  %s: \" fmt \"\\n\", __func__, ##__VA_ARGS__)\n")
    h_lines.append("#else\n")
    h_lines.append("  #define LOG_ENTER(...) ((void)0)\n")
    h_lines.append("  #define LOG_EXIT(...)  ((void)0)\n")
    h_lines.append("  #define LOG_INFO(...)  ((void)0)\n")
    h_lines.append("  #define LOG_WARN(...)  ((void)0)\n")
    h_lines.append("#endif\n\n")

    h_lines.append("/* === Data section (50MB) === */\n")
    h_lines.append("extern uint8_t __data_start[0x301DB28];\n")
    h_lines.append("extern const uint8_t __rdata_start[0x049A00];\n")
    h_lines.append("#define DAT8(rva)  (*(uint8_t*)((uint8_t*)__data_start + ((rva) - 0x0063F000)))\n")
    h_lines.append("#define DAT16(rva) (*(uint16_t*)((uint8_t*)__data_start + ((rva) - 0x0063F000)))\n")
    h_lines.append("#define DAT32(rva) (*(uint32_t*)((uint8_t*)__data_start + ((rva) - 0x0063F000)))\n")
    h_lines.append("#define DATPTR(rva) (*(void**)((uint8_t*)__data_start + ((rva) - 0x0063F000)))\n\n")

    h_lines.append("/* === Global data declarations === */\n")
    for g in sorted(all_globals):
        h_lines.append("extern uint8_t {}[256];\n".format(sanitize(g)))

    h_lines.append("\n/* === Function declarations === */\n")
    for name, ret, params, rva_str in all_decls:
        h_lines.append("/* {:08x} */ {} {}({});\n".format(
            int(rva_str, 16), ret, name, params))

    h_lines.append("\n#endif /* VOFF_ALL_H */\n")

    with open(HEADER_H, "w") as f:
        f.write("".join(h_lines))
    print("  Written {} ({:,} bytes)".format(HEADER_H, len("".join(h_lines))))

    # ================================================================
    # PHASE 4: Generate stubs for unresolved functions
    # ================================================================
    print("\n[Phase 4] Generating stubs...")

    s_lines = []
    s_lines.append("/* Stubs for unresolved external/DLL functions */\n")
    s_lines.append('#include "voff_all.h"\n\n')

    for name, ret, params_str, rva_str in all_decls:
        # Generate stubs only for functions NOT found in the source files
        # (we don't know which are imports vs local functions yet)
        pass  # Stubs are generated by the post-processor

    with open(STUBS_C, "w") as f:
        f.write("".join(s_lines))

    # ================================================================
    # PHASE 5: Call graph
    # ================================================================
    print("\n[Phase 5] Writing call graph...")
    cg_lines = []
    cg_lines.append("# Call graph: {} functions, {} edges\n".format(total,
        sum(len(v) for v in call_graph.values())))
    cg_lines.append("# Format: caller -> [callee1, callee2, ...]\n\n")
    for caller, callees in sorted(call_graph.items()):
        cg_lines.append("{} -> {}\n".format(caller, ", ".join(sorted(callees))))

    with open(CALLGRAPH, "w") as f:
        f.write("".join(cg_lines))

    # ================================================================
    # PHASE 6: Function index
    # ================================================================
    print("\n[Phase 6] Writing function index...")
    idx = []
    idx.append("# Function index: {} functions\n".format(total))
    idx.append("# VA       | Section | Name\n")
    for func in all_funcs:
        va = func.getEntryPoint().getOffset()
        sec = func_section(func)
        idx.append("{:08x} | {:6s} | {}\n".format(va, sec, func.getName()))

    with open(INDEX_TXT, "w") as f:
        f.write("".join(idx))

    print("\nDone! Output in {}".format(BASE))
    print("  {} source files in {}".
          format(len([f for f in os.listdir(SRC_DIR) if f.endswith('.c')]), SRC_DIR))
    print("  Header: {}".format(HEADER_H))
    print("  Index:  {}".format(INDEX_TXT))
    print("  Call graph: {}".format(CALLGRAPH))

if __name__ == "__main__":
    main()
