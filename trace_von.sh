#!/bin/bash
# trace_von.sh — Run Virtual On with DDraw/D3D debug tracing
# Output goes to von_trace.log (filtered) and von_trace_full.log (everything)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GAME_DIR="$SCRIPT_DIR/out_stage2/data"

WINE="flatpak run --filesystem=$SCRIPT_DIR --command=/app/bin/wine org.winehq.Wine"

# Focused trace channels for graphics debugging:
#   +ddraw     — DirectDraw surface create/flip/blit
#   +d3d       — Direct3D execute buffers, draw calls
#   +d3d_shader — shader compilation (if using GLSL backend)
#   -heap      — suppress the heap spam we already fixed
export WINEDEBUG="+ddraw,+d3d,+d3d_shader,warn-heap"

echo "=== Tracing Virtual On graphics ==="
echo "Output: von_trace_full.log (all channels)"
echo "        von_trace.log      (surface/flip/draw only)"
echo ""

# Run and capture everything, then filter interesting lines
$WINE "$GAME_DIR/V_ON/V_ON.EXE" > von_trace_full.log 2>&1

echo ""
echo "=== Trace captured ==="
echo "Key events (surface create, flip, draw):"
grep -iE 'surface.*create|flip|blit|draw.*prim|execute.*buffer|set.*render.*state|clear' von_trace_full.log > von_trace.log 2>/dev/null
echo "  $(wc -l < von_trace.log) relevant events in von_trace.log"
echo ""
echo "First 20 surface/flip events:"
head -20 von_trace.log
