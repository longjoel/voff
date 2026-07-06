# VOFF Build Pipeline
#
# Stages:
#   1. von.img -> out_stage2/          (ISO extraction)
#   2. V_ON.EXE -> ghidra_project/     (Ghidra binary analysis)
#   3. Ghidra DB -> out_decompile/src/ (decompile all functions)
#   4. Source + data -> voff_sdl       (SDL2 native Linux binary)
#   5. Source + data -> voff.exe       (Winelib binary via Wine)

.PHONY: all sdl winelib stage1 stage2 stage3 clean-all help

# ============================================================
# Default: build the SDL2 native binary
# ============================================================
all: sdl

sdl: stage1 stage3
	$(MAKE) -C out_decompile sdl

winelib: stage1 stage3
	$(MAKE) -C out_decompile all

# ============================================================
# Stage 1: Extract von.img -> out_stage2/
# ============================================================
stage1: out_stage2/data/V_ON/V_ON.EXE

out_stage2/data/V_ON/V_ON.EXE: von.img extract_von_img.py
	@echo "=== Stage 1: Extracting ISO ==="
	python3 extract_von_img.py von.img --output out_stage2 --no-audio
	@echo "=== Stage 1: Complete ==="

# ============================================================
# Stage 2: Ghidra analysis — V_ON.EXE -> ghidra_project/
# Requires: Ghidra 11.3.1 installed at ghidra/ghidra_11.3.1_PUBLIC/
# This imports the binary and runs auto-analysis (~3 minutes)
# ============================================================
stage2: ghidra_project/VirtualOn.rep/

ghidra_project/VirtualOn.rep/: out_stage2/data/V_ON/V_ON.EXE
	@echo "=== Stage 2: Ghidra analysis ==="
	@echo "Requires Ghidra 11.3.1 at ghidra/ghidra_11.3.1_PUBLIC/"
	@echo "Download: https://github.com/NationalSecurityAgency/ghidra/releases"
	ghidra/ghidra_11.3.1_PUBLIC/support/analyzeHeadless \
		ghidra_project VirtualOn \
		-import out_stage2/data/V_ON/V_ON.EXE \
		-overwrite
	@echo "=== Stage 2: Complete ==="

# ============================================================
# Stage 3: Decompile all functions + dump data sections
# Requires: Stage 2 (Ghidra DB) must exist
# ============================================================
stage3: out_decompile/src/

out_decompile/src/: ghidra_project/VirtualOn.rep/
	@echo "=== Stage 3: Decompiling all functions ==="
	mkdir -p out_decompile
	ghidra/ghidra_11.3.1_PUBLIC/support/analyzeHeadless \
		ghidra_project VirtualOn \
		-process V_ON.EXE \
		-scriptPath ghidra_project \
		-postScript dump_all.py \
		-noanalysis
	@echo "=== Stage 3: Dumping data sections ==="
	ghidra/ghidra_11.3.1_PUBLIC/support/analyzeHeadless \
		ghidra_project VirtualOn \
		-process V_ON.EXE \
		-scriptPath ghidra_project \
		-postScript dump_decompile.py \
		-noanalysis
	@echo "=== Stage 3: Complete ==="

# ============================================================
# Convenience targets
# ============================================================
run-sdl: sdl
	./out_decompile/voff_sdl

run-winelib: winelib
	./run_voff.sh

clean-all:
	$(MAKE) -C out_decompile clean
	rm -rf out_decompile/src/ out_decompile/build/
	rm -f out_decompile/voff_all.h out_decompile/voff_stubs.h
	rm -f out_decompile/*.c out_decompile/*.h
	rm -f out_decompile/function_index.txt out_decompile/call_graph.txt
	rm -f out_decompile/.data.bin out_decompile/.rdata.bin out_decompile/.rsrc.bin

help:
	@echo "VOFF Build Pipeline"
	@echo "==================="
	@echo ""
	@echo "Prerequisites:"
	@echo "  1. Place von.img in this directory"
	@echo "  2. Install Ghidra 11.3.1 at ghidra/ghidra_11.3.1_PUBLIC/"
	@echo "  3. For SDL2 build: dnf install SDL2-devel mesa-libGL-devel"
	@echo "  4. For Winelib build: set up distrobox container (see README)"
	@echo ""
	@echo "Targets:"
	@echo "  make sdl        Build native SDL2 binary (no Wine)"
	@echo "  make winelib    Build Winelib binary (needs distrobox)"
	@echo "  make stage1     Extract ISO image only"
	@echo "  make stage2     Run Ghidra analysis on V_ON.EXE"
	@echo "  make stage3     Decompile all functions + dump data"
	@echo "  make run-sdl    Build and run SDL2 binary"
	@echo "  make clean-all  Remove all generated files"
	@echo ""
	@echo "Pipeline: von.img -> stage1 -> stage2 -> stage3 -> sdl/winelib"
