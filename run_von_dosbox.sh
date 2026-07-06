#!/bin/bash
# run_von_dosbox.sh — Launch Virtual On via DOSBox-X + Win98 VM
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOSBOX_CONF="$SCRIPT_DIR/dosbox_win98.conf"

cat > "$DOSBOX_CONF" << CONFEOF
[sdl]
output = opengl
windowresolution = 1024x768

[dosbox]
machine = svga_et4000
memsize = 255

[cpu]
core = dynamic
cputype = pentium_mmx
cycles = 120000

[video]
vmemsize = 4
vesa modelist = 1024x768 640x480 800x600
vesa old vbe = true
vesa write modes = linear

[sblaster]
sbtype = sb16
sbbase = 220
irq = 7
dma = 1
hdma = 5

[ide, primary]
enable = true

[ide, secondary]
enable = true

[autoexec]
imgmount c "$SCRIPT_DIR/isos/win98_hdd.img" -size 512,63,64,1024
imgmount d "$SCRIPT_DIR/von.img" -t iso
imgmount a "$SCRIPT_DIR/isos/softgpu_drivers.img" -t floppy
boot -l c
CONFEOF

echo "=== Virtual On — DOSBox-X + SoftGPU ==="
echo ""
echo "After Windows boots:"
echo "  Right-click desktop → Properties → Settings → Advanced → Adapter → Change"
echo "  Select 'Have Disk' → Browse to A:\\"
echo "  Pick vmdisp9x.inf → Install 'VM Display Adapter'"
echo "  Reboot → full color SVGA + DirectDraw + Direct3D"
echo ""

exec flatpak run \
  --filesystem="$SCRIPT_DIR" \
  com.dosbox_x.DOSBox-X \
  -conf "$DOSBOX_CONF" \
  "$@"
