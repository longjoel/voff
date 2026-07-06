#!/bin/bash
# run_von_xp.sh — Launch Virtual On via QEMU + Windows XP
# MicroXP v0.82 — minimal XP, keeps the Win9x compatibility engine
# First boot: installs XP from ISO. After install, run again to play.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
XP_DISK="$SCRIPT_DIR/isos/xp_hdd.qcow2"
XP_ISO="$SCRIPT_DIR/isos/microxp.iso"
VM_CD="$SCRIPT_DIR/von.img"

[ ! -f "$XP_ISO" ] && { echo "Need XP ISO at: $XP_ISO"; exit 1; }
[ ! -f "$VM_CD" ] && { echo "Need von.img at: $VM_CD"; exit 1; }

# First run: boot from CD to install XP
# After install: change '-boot d' to '-boot c' below

if [ "${1:-}" = "--install" ] || [ ! -s "$XP_DISK" ] || [ "$(stat -c%s "$XP_DISK")" -lt 100000000 ]; then
    BOOT="-boot d"
    echo "=== Installing Windows XP ==="
    echo "Boot from CD, follow setup. After install, run:"
    echo "  ./run_von_xp.sh"
else
    BOOT="-boot c"
    echo "=== Virtual On — Windows XP ==="
    echo ""
    echo "After desktop: run D:\\V_ON\\V_ON.EXE"
    echo "Or install first: D:\\SETUP.EXE"
    echo ""
fi

exec qemu-system-i386 \
    -name "Virtual On — Windows XP" \
    -M pc,accel=kvm \
    -cpu pentium \
    -m 512 \
    -drive file="$XP_DISK",format=qcow2,if=ide \
    -drive file="$XP_ISO",format=raw,if=ide,media=cdrom \
    -drive file="$VM_CD",format=raw,if=ide,media=cdrom \
    -drive file="$SCRIPT_DIR/isos/fix_floppy.img",format=raw,if=floppy \
    $BOOT \
    -vga cirrus \
    -device sb16 \
    -net none \
    -usb \
    -device usb-tablet \
    "$@"
