#!/bin/bash
# run_von_qemu.sh — Launch Virtual On via QEMU + QEMU-native Win98 image
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VM_DISK="$SCRIPT_DIR/isos/win98.qcow2"
VM_CD="$SCRIPT_DIR/von.img"

[ ! -f "$VM_DISK" ] && { echo "Need Win98 image at: $VM_DISK"; exit 1; }
[ ! -f "$VM_CD" ] && { echo "Need von.img at: $VM_CD"; exit 1; }

echo "=== Virtual On — QEMU + Win98 (softgpu) ==="
echo "   Disk: $(basename "$VM_DISK")"
echo "   CD:   von.img"
echo ""

exec qemu-system-i386 \
    -name "Virtual On — Windows 98" \
    -M pc,accel=kvm \
    -cpu pentium \
    -m 256 \
    -drive file="$VM_DISK",format=qcow2,if=ide \
    -drive file="$VM_CD",format=raw,if=ide,media=cdrom \
    -boot c \
    -vga cirrus \
    -device sb16 \
    -net none \
    -usb \
    -device usb-tablet \
    "$@"

[ ! -f "$VM_DISK" ] && { echo "Need Win98 image at: $VM_DISK"; exit 1; }
[ ! -f "$VM_CD" ] && { echo "Need von.img at: $SCRIPT_DIR"; exit 1; }

echo "=== Virtual On — QEMU + Win98 (pre-built) ==="
echo ""

exec qemu-system-i386 \
    -name "Virtual On — Windows 98" \
    -M pc,accel=kvm \
    -cpu pentium \
    -m 256 \
    -drive file="$VM_DISK",format=qcow2,if=none,id=hd \
    -device piix4-ide,id=ide \
    -device ide-hd,drive=hd,bus=ide.0 \
    -drive file="$VM_CD",format=raw,if=none,id=cd,media=cdrom \
    -device ide-cd,drive=cd,bus=ide.1 \
    -boot c \
    -vga cirrus \
    -device sb16 \
    -net none \
    -usb \
    -device usb-tablet \
    "$@"

# For IFSMGR.VXD or other boot errors:
#   Press F8 when "Starting Windows 98" appears
#   Select "Safe Mode" or "Step-by-step confirmation"
#   If Safe Mode works, the issue is a driver conflict
