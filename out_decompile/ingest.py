#!/usr/bin/env python3
"""ingest.py — copy a decompiled source file into game/, apply fixups.

Usage:
  ./ingest.py src/f_XXXXXXXX__FUN_XXXXXXXX.c "descriptive_name" game/

Does:
  1. Copies source file to game/FUN_XXXXXXXX__descriptive_name.c
  2. Replaces #include "../voff_all.h" with #include "../voff_bridge.h"
  3. Renames function: FUN_XXXXXXXX -> FUN_XXXXXXXX__descriptive_name
  4. Cleans up calling conventions, CONCAT, code*, &stack0x
  5. Leaves DAT_/PTR_ references untouched
  6. Prints added stub declarations for any called FUN_ functions
"""

import re
import sys
import os

if len(sys.argv) < 3:
    print("Usage: ingest.py <src_file> <descriptive_name> [dest_dir]")
    print("  src_file: path to decompiled .c file in src/")
    print("  descriptive_name: snake_case name like 'matrix_translate'")
    print("  dest_dir: output dir (default: game/)")
    sys.exit(1)

src_path = sys.argv[1]
desc_name = sys.argv[2]
dest_dir = sys.argv[3] if len(sys.argv) > 3 else "game"

if not os.path.exists(src_path):
    print(f"ERROR: source file not found: {src_path}")
    sys.exit(1)

basename = os.path.basename(src_path)
# Extract FUN_XXXXXXXX from filename: f_XXXXXXXX__FUN_XXXXXXXX.c
m = re.match(r'f_([0-9a-fA-F]{8})__FUN_([0-9a-fA-F]{8})\.c', basename)
if not m:
    print(f"ERROR: cannot parse filename: {basename}")
    sys.exit(1)

va_str = m.group(1)
func_name = "FUN_" + m.group(2)
new_func_name = func_name + "__" + desc_name
out_name = func_name + "__" + desc_name + ".c"
out_path = os.path.join(dest_dir, out_name)

with open(src_path) as f:
    content = f.read()

# 1. Fix includes
content = content.replace('#include "../voff_all.h"', '#include "../voff_bridge.h"\n#include "game.h"')

# 2. Rename the function definition
# Look for: <ret> FUN_XXXXXXXX(params)
# Replace only the function definition, not calls to other FUN_ functions
content = re.sub(
    r'\b' + re.escape(func_name) + r'\b(\s*\()',
    new_func_name + r'\1',
    content
)

# 3. Clean up calling conventions
content = content.replace('__cdecl(', '(')
content = content.replace('__thiscall ', ' ')
content = content.replace('__stdcall ', ' ')
content = content.replace('__fastcall ', ' ')

# 4. CONCAT removal
content = re.sub(r'CONCAT\d+\s*\(', '(', content)
content = re.sub(r'\bCONCAT\d+\b', '', content)

# 5. (code *) -> (void *)
content = content.replace('(code *)', '(void *)')
content = content.replace('(code  *)', '(void *)')

# 6. &stack0x -> 0x
content = content.replace('&stack0x', '0x')

# 7. Fix: TYPE * cast syntax where TYPE has space before *
# e.g. "undefined4 *" -> "uint32_t *"
# Type replacements (longest first to avoid substring issues)
type_map = [
    ('undefined8', 'uint64_t'),
    ('undefined4', 'uint32_t'),
    ('undefined2', 'uint16_t'),
    ('undefined1', 'uint8_t'),
    ('byte', 'uint8_t'),
    ('word', 'uint16_t'),
    ('dword', 'uint32_t'),
]
for old, new in type_map:
    # Replace whole-word occurrences
    content = re.sub(r'\b' + old + r'\b', new, content)

os.makedirs(dest_dir, exist_ok=True)
with open(out_path, 'w') as f:
    f.write(content)

print(f"OK  {out_name}")

# Find all FUN_ calls in this function that aren't the renamed one
called_funcs = set()
for m in re.finditer(r'\b(FUN_[0-9a-fA-F]{8})\b', content):
    fname = m.group(1)
    if fname != func_name and fname != new_func_name:
        called_funcs.add(fname)

if called_funcs:
    print(f"    calls {len(called_funcs)} other FUN_ functions:")
    for f in sorted(called_funcs):
        print(f"      {f}")
    print(f"    After ingestion, run 'make gen' to create stubs.")
