# VOFF — Cyber Troopers Virtual On (1997) Reverse Engineering

Decompiling Sega's 1997 PC port of _Cyber Troopers Virtual On_ into a native
Linux binary. No VM. No Wine. No CAB files. Just code.

## What this is

A build pipeline that takes the original `von.img` CD-ROM image and produces:

- **`voff_sdl`** — native 64-bit Linux binary (SDL2 + OpenGL, no Wine needed)
- **`voff.exe`** — Winelib binary (runs through Wine with D3D3 support)

The game's original 4,162 functions are fully decompiled to C, the data sections
are extracted and embedded, and the host layer (MFC/Win32) is replaced with
~300 lines of SDL2.

## Quick start

```bash
# 1. Place von.img in this directory
cp /path/to/von.img .

# 2. Install Ghidra 11.3.1
#    Download from: https://github.com/NationalSecurityAgency/ghidra/releases
#    Extract to:   ghidra/ghidra_11.3.1_PUBLIC/

# 3. Run the full pipeline
make stage1    # Extract ISO (~30 sec)
make stage2    # Ghidra analysis (~3 min)
make stage3    # Decompile all functions (~30 min)
make sdl       # Build native binary (~10 sec)

# 4. Run
make run-sdl
```

## Build stages

```
von.img  ──[stage1]──>  out_stage2/          (ISO extraction, 626 files)
                           │
                    V_ON.EXE (6.4 MB)
                           │
              ──[stage2]──>  ghidra_project/     (Ghidra analysis, ~3 min)
                           │
                    VirtualOn.rep/ (54 MB DB)
                           │
              ──[stage3]──>  out_decompile/      (4,162 C files, ~30 min)
                           │
                    src/  .data.bin  .rdata.bin
                           │
              ──[make]───>  voff_sdl             (native binary, ~10 sec)
                           └─> voff.exe          (Winelib binary)
```

## Project structure

```
voff/
├── von.img                    # Original CD-ROM (you provide this)
├── Makefile                   # Top-level build pipeline
├── DIARY.md                   # Reverse engineering journal
├── README.md                  # This file
│
├── extract_von_img.py         # Stage 1: ISO 9660 extractor + audio decoder
│
├── voff_mt_tool.py            # Stage 2: 3D model (.MT) extractor/compiler
├── voff_viewer.py             # Stage 3: OpenGL 3D model viewer
├── import_mt_blender.py       # Stage 3b: Blender MT import
│
├── ghidra_project/            # Stage 4: Ghidra analysis scripts
│   ├── dump_all.py            #   Decompile all 4,162 functions
│   ├── dump_decompile.py      #   Key function export + data dump
│   ├── dump_targets.py        #   Targeted function decompilation
│   ├── dump_ddraw_chain.py    #   DDraw init chain tracer
│   ├── find_ddraw_caller.py   #   DDraw call site finder
│   ├── find_d3d.py            #   D3D pipeline discovery
│   ├── dump_findings.py       #   SDE table + float region scanner
│   ├── dump_sde.py            #   SDE string cross-references
│   ├── dump_window_init.py    #   Window creation trace
│   ├── dump_window_deep.py    #   Window class decompilation
│   └── dump_mmx_check.py      #   MMX CPU check locator
│
├── out_decompile/             # Stage 5: Winelib + SDL2 builds
│   ├── voff_bridge.h          #   Win32/D3D type bridge + logging
│   ├── voff_game.c            #   Hand-translated game loop
│   ├── voff_data.c            #   Data section loader
│   ├── voff_sdl.c             #   SDL2 host (native Linux, no Wine)
│   ├── voff_types.h           #   Ghidra type definitions
│   ├── process_decompile.py   #   Post-processor for decompiled C
│   ├── process_all.py         #   Batch post-processor
│   └── Makefile               #   Winelib + SDL2 build rules
│
├── run_von.sh                 # Launch original EXE via Wine (patched)
├── run_voff.sh                # Launch decompiled build
├── run_von_qemu.sh            # QEMU launcher (Win98)
├── run_von_dosbox.sh          # DOSBox-X launcher
├── run_von_xp.sh              # QEMU + Windows XP
├── trace_von.sh               # DDraw/D3D debug trace
├── v_on.ini                   # Game settings file
└── dosbox_win98.conf          # DOSBox-X config template
```

## Requirements

| Stage | Tool | Version |
|---|---|---|
| 1 | Python 3 | Any |
| 2 | Ghidra | 11.3.1 |
| 2 | Java (JDK) | 17+ |
| 3 | Ghidra (headless) | 11.3.1 |
| 4 (SDL2) | GCC, SDL2, OpenGL | Any |
| 4 (Winelib) | distrobox + winegcc | Fedora 44+ |

## License

The scripts, tools, and original source code in this repository are provided
for educational and preservation purposes. The game _Cyber Troopers Virtual On_
is copyright Sega Enterprises, Ltd. (1997). This project does not distribute
any copyrighted game assets — all derived data is regenerated from the original
CD-ROM image via the build pipeline.

## Acknowledgments

Built with [Ghidra](https://ghidra-sre.org/) and far too much caffeine.
