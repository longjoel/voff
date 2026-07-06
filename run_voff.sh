#!/bin/bash
# run_voff.sh — Build and launch VOFF (Winelib or SDL2 native)
# Usage: ./run_voff.sh [--build] [--sdl]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/out_decompile"

MODE="winelib"
AUTO_BUILD=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --build) AUTO_BUILD=true; shift ;;
        --sdl)   MODE="sdl"; shift ;;
        -h|--help)
            echo "Usage: $0 [--build] [--sdl]"
            echo "  --build   Rebuild before running"
            echo "  --sdl     Use SDL2 native build (no Wine)"
            echo "  (default) Winelib build via distrobox"
            exit 0 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

if [ "$MODE" = "sdl" ]; then
    # Native SDL2 build — runs directly on Linux
    if [ "$AUTO_BUILD" = true ] || [ ! -f "$BUILD_DIR/voff_sdl" ]; then
        echo "=== Building VOFF SDL2 native... ==="
        distrobox enter voff-builder -- make -C "$BUILD_DIR" sdl
        echo
    fi
    if [ ! -f "$BUILD_DIR/voff_sdl" ]; then
        echo "ERROR: voff_sdl not found. Run with --build."
        exit 1
    fi
    echo "=== Launching VOFF SDL2 native ==="
    exec "$BUILD_DIR/voff_sdl"
else
    # Winelib build — runs inside distrobox
    if [ "$AUTO_BUILD" = true ] || [ ! -f "$BUILD_DIR/voff.exe.so" ]; then
        echo "=== Building VOFF Winelib... ==="
        distrobox enter voff-builder -- make -C "$BUILD_DIR" clean all
        echo
    fi
    if [ ! -f "$BUILD_DIR/voff.exe.so" ]; then
        echo "ERROR: voff.exe.so not found. Run with --build."
        exit 1
    fi
    echo "=== Launching VOFF Winelib ==="
    exec distrobox enter voff-builder -- \
        bash -c "cd '$BUILD_DIR' && WINEDEBUG=-all wine voff.exe.so"
fi
