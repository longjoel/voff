#!/bin/bash
# run_von.sh — Launch Virtual On under Wine (Flatpak)
# Usage: ./run_von.sh [--setup] [--debug] [--no-patch]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GAME_DIR="$SCRIPT_DIR/out_stage2/data"
PATCHEXE="$GAME_DIR/V_ON/V_ON.EXE"

# --------------------------------------------------
# Prerequisites
# --------------------------------------------------
if ! flatpak list 2>/dev/null | grep -q org.winehq.Wine; then
    echo "Wine not installed."
    echo "  Run: flatpak install flathub org.winehq.Wine"
    exit 1
fi

if [ ! -f "$PATCHEXE" ]; then
    echo "Game not extracted."
    echo "  Run: python3 extract_von_img.py von.img --output out_stage2 --no-audio"
    exit 1
fi

# --------------------------------------------------
# Argument parsing
# --------------------------------------------------
SETUP=false
DEBUG=false
PATCH_SKIP=false
for arg in "$@"; do
    case "$arg" in
        --setup)   SETUP=true ;;
        --debug)   DEBUG=true ;;
        --no-patch) PATCH_SKIP=true ;;
    esac
done

# --------------------------------------------------
# Binary patches (idempotent, apply on each launch)
# --------------------------------------------------
if [ "$PATCH_SKIP" = false ]; then
    if [ ! -f "$PATCHEXE.bak" ]; then
        cp "$PATCHEXE" "$PATCHEXE.bak"
    fi

    python3 -c "
import sys
exe = '$PATCHEXE'
bak = exe + '.bak'

# Restore clean backup if file differs (previously patched or corrupted)
with open(exe, 'rb') as f1, open(bak, 'rb') as f2:
    if f1.read() != f2.read():
        import shutil
        shutil.copy2(bak, exe)

# Apply patches
patches = [
    (0x1CA1B1, b'\xb8\x01\x00\x00\x00\xc3\x90\x90', 'CD check #1 (CD audio init)'),
    (0x1C76BA, b'\xb8\x01\x00\x00\x00\xc3',           'CD check #2 (CD drive detect)'),
    (0x1C50B6, b'\xe9\x26\x00\x00\x00\x90',           'MMX CPU check'),
]

with open(exe, 'r+b') as f:
    for offset, patch, desc in patches:
        f.seek(offset)
        f.write(patch)
        print('  {}'.format(desc))
" || { echo "  ERROR: patch failed"; exit 1; }

    echo ""
fi

# --------------------------------------------------
# Wine helpers
# --------------------------------------------------
WINE="flatpak run --filesystem=$SCRIPT_DIR --command=/app/bin/wine org.winehq.Wine"
WINEBOOT="flatpak run --filesystem=$SCRIPT_DIR --command=/app/bin/wineboot org.winehq.Wine"

# --------------------------------------------------
# Wine prefix
# --------------------------------------------------
echo "=== Initializing Wine ==="

# First Wine invocation inside flatpak is slow (sandbox setup + prefix creation).
# Run in background with a message so the user knows something is happening.
(
    $WINEBOOT -u 2>/dev/null || true
) &
BOOT_PID=$!

# Show dots while waiting (max ~20s)
for i in $(seq 1 20); do
    if ! kill -0 $BOOT_PID 2>/dev/null; then
        break
    fi
    printf "."
    sleep 1
done
wait $BOOT_PID 2>/dev/null || true
echo ""

# Registry: Direct3D/DirectDraw OpenGL backend
USER_REG="$HOME/.var/app/org.winehq.Wine/data/wine/user.reg"
ensure_key() {
    if [ -f "$USER_REG" ] && ! grep -q "\"${2}\"" "$USER_REG" 2>/dev/null; then
        sed -i '/^$/d' "$USER_REG"
        printf '\n[%s] %s\n"%s"="%s"\n' "$1" "$(date +%s)" "$2" "$3" >> "$USER_REG"
    fi
}
ensure_key 'Software\\Wine\\Direct3D'  "renderer" "gl"
ensure_key 'Software\\Wine\\DirectDraw' "renderer" "opengl"

# --------------------------------------------------
# Environment
# --------------------------------------------------
export WINEDLLOVERRIDES="dpctrl=b${WINEDLLOVERRIDES:+;$WINEDLLOVERRIDES}"
export WINEDEBUG="${WINEDEBUG:-warn+heap}"

# --------------------------------------------------
# Debug
# --------------------------------------------------
if [ "$DEBUG" = true ]; then
    echo "=== Debug ==="
    $WINE --version 2>/dev/null || true
    echo "PATCHEXE=$PATCHEXE"
    echo "WINEDEBUG=$WINEDEBUG"
    echo "WINEDLLOVERRIDES=$WINEDLLOVERRIDES"
    echo ""
fi

# --------------------------------------------------
# Launch
# --------------------------------------------------
echo "=== Virtual On ==="
echo "Controls (likely): Arrow keys = move, Z/X/C = actions, Esc = quit"
echo ""

exec $WINE "$PATCHEXE"
