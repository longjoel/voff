#!/usr/bin/env python3
"""
voff_mt_tool.py — Extract and compile Virtual On MT_*.BIN 3D model files.

MT is the main robot/model format used by the 1997 PC game
"Cyber Troopers Virtual On."

FILE FORMAT
===========
Header:  8 bytes = 4 x uint16 (meaning TBD — varies per file)
Body:    20-byte vertex stride, stored as triangle strips in draw order.

There are two vertex layouts within the same file:

Type A (first strip / main body mesh):
    bytes 0-11:  Position (float32 x, y, z)
    bytes 12-15: Attribute (2 x uint16) — normals or UVs (unknown encoding)
    bytes 16-17: Group index (uint16) — bone/material
    bytes 18-19: Padding (uint16, always 0)

Type B (all subsequent strips):
    bytes 0-3:   Metadata word 0
                 NaN (0xFFxxxxxx) marks a STRIP BOUNDARY
                 Non-NaN = per-vertex data
    bytes 4-7:   Metadata word 1 (uint32)
    bytes 8-19:  Position (float32 x, y, z)

Strip boundaries are marked by NaN float values in bytes 0-3.
Within a strip, vertices form a triangle strip (every 3 consecutive
vertices form a triangle).

Usage:
    python3 voff_mt_tool.py extract MT_APH.BIN -o aphrodite
    python3 voff_mt_tool.py compile aphrodite.obj -o MT_APH_NEW.BIN
"""

import struct
import math
import os
import sys
import json
import argparse
from pathlib import Path


# ====================================================================
# Constants
# ====================================================================

VERTEX_STRIDE = 20
HEADER_SIZE = 8


def _is_ok_position(v):
    """Check if a float value looks like a valid 3D position coordinate."""
    return not math.isnan(v) and not math.isinf(v) and abs(v) < 5000


# ====================================================================
# MT -> OBJ + sidecar
# ====================================================================

def mt_extract(input_path, output_path):
    """Extract an MT binary file to OBJ + JSON sidecar with strip metadata."""

    with open(input_path, "rb") as f:
        data = f.read()

    header = list(struct.unpack_from("<HHHH", data, 0))
    strips = []
    current = None

    for vi in range(len(data) // VERTEX_STRIDE):
        pos = HEADER_SIZE + vi * VERTEX_STRIDE
        if pos + VERTEX_STRIDE > len(data):
            break

        word0 = struct.unpack_from("<I", data, pos)[0]
        word1 = struct.unpack_from("<I", data, pos + 4)[0]
        exponent = (word0 >> 23) & 0xFF
        mantissa = word0 & 0x007FFFFF
        is_nan = exponent == 0xFF and mantissa != 0

        if is_nan:
            if current and current["verts"]:
                strips.append(current)
            x = struct.unpack_from("<f", data, pos + 8)[0]
            y = struct.unpack_from("<f", data, pos + 12)[0]
            z = struct.unpack_from("<f", data, pos + 16)[0]
            current = {
                "type": "B",
                "header_w0": word0,
                "header_w1": word1,
                "verts": [(x, y, z)],
                "meta": [],   # no meta for strip header vertex
            }
        else:
            # Try the three vertex layouts in priority order:
            #
            # Type A: position at bytes 0-11, attrs at 12-19
            # Type C: x at 0-3, y at 4-7, meta at 8-15, z at 16-19
            # Type B: meta at 0-7, position at 8-19
            x1 = struct.unpack_from("<f", data, pos)[0]
            y1 = struct.unpack_from("<f", data, pos + 4)[0]
            z1 = struct.unpack_from("<f", data, pos + 8)[0]
            z3 = struct.unpack_from("<f", data, pos + 16)[0]
            x2 = struct.unpack_from("<f", data, pos + 8)[0]
            y2 = struct.unpack_from("<f", data, pos + 12)[0]
            z2 = struct.unpack_from("<f", data, pos + 16)[0]

            if all(_is_ok_position(c) for c in (x1, y1, z1)):
                # Type A: pos 0-11, attrs 12-19
                meta_bytes = data[pos + 12 : pos + 20]
                vert_type = "A"
                pos_tuple = (x1, y1, z1)
            elif all(_is_ok_position(c) for c in (x1, y1, z3)):
                # Type C: x at 0-3, y at 4-7, meta at 8-15, z at 16-19
                meta_bytes = data[pos + 8 : pos + 16]
                vert_type = "C"
                pos_tuple = (x1, y1, z3)
            elif all(_is_ok_position(c) for c in (x2, y2, z2)):
                # Type B: meta 0-7, pos 8-19
                meta_bytes = data[pos : pos + 8]
                vert_type = "B"
                pos_tuple = (x2, y2, z2)
            else:
                continue

            if current is None:
                current = {
                    "type": vert_type,
                    "header_w0": 0,
                    "header_w1": 0,
                    "verts": [pos_tuple],
                    "meta": [meta_bytes],
                }
            else:
                current["verts"].append(pos_tuple)
                current["type"] = vert_type
                current["meta"].append(meta_bytes)

    if current and current["verts"]:
        strips.append(current)

    # Write OBJ
    obj_path = output_path.with_suffix(".obj")
    with open(obj_path, "w") as f:
        f.write(f"# {os.path.basename(input_path)} — {len(strips)} strips\n")
        f.write(f"mtllib {output_path.stem}.mtl\n")
        vert_base = 1
        for si, s in enumerate(strips):
            nv = len(s["verts"])
            # OBJ group: each strip gets its own named object for Blender
            vert_type = s.get("type", "A")
            f.write(f"\no strip_{si:03d}_t{vert_type}_{nv}v\n")
            for v in s["verts"]:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for tri in range(nv - 2):
                a = vert_base + tri
                b = vert_base + tri + 1
                c = vert_base + tri + 2
                if a != b and b != c and a != c:
                    f.write(f"f {a} {b} {c}\n")
            vert_base += nv

    # Write JSON sidecar
    sidecar_path = output_path.with_suffix(".json")
    sidecar = {
        "source": os.path.basename(input_path),
        "format": "MT (Virtual On 3D Model)",
        "vertex_stride": VERTEX_STRIDE,
        "header": header,
        "num_strips": len(strips),
        "strips": [],
    }
    for s in strips:
        sidecar["strips"].append(
            {
                "type": s["type"],
                "header_w0": s["header_w0"],
                "header_w1": s["header_w1"],
                "num_vertices": len(s["verts"]),
                "meta_hex": [bytes(m).hex() for m in s["meta"]],
            }
        )

    with open(sidecar_path, "w") as f:
        json.dump(sidecar, f, indent=2)

    total_verts = sum(len(s["verts"]) for s in strips)
    total_tris = sum(max(0, len(s["verts"]) - 2) for s in strips)

    return {
        "strips": len(strips),
        "vertices": total_verts,
        "triangles": total_tris,
        "obj": str(obj_path),
        "sidecar": str(sidecar_path),
    }


# ====================================================================
# OBJ + sidecar -> MT
# ====================================================================

def mt_compile(obj_path, output_path, sidecar_path=None, original_path=None):
    """Compile an OBJ (+ optional sidecar) back to MT binary format."""

    # Determine sidecar path
    if sidecar_path is None:
        sidecar_path = Path(obj_path).with_suffix(".json")
    if not os.path.exists(sidecar_path):
        if original_path:
            sidecar_path = Path(original_path).with_suffix(".json")
        else:
            raise FileNotFoundError(
                f"Sidecar not found: {sidecar_path}. "
                "Provide --sidecar or --original to locate it."
            )

    with open(sidecar_path) as f:
        sidecar = json.load(f)

    with open(obj_path) as f:
        obj_lines = f.readlines()

    # Parse OBJ vertices
    obj_verts = []
    for line in obj_lines:
        if line.startswith("v "):
            parts = line.split()
            obj_verts.append((float(parts[1]), float(parts[2]), float(parts[3])))

    # Parse OBJ faces to group vertices into strips
    obj_faces = []
    for line in obj_lines:
        if line.startswith("f "):
            parts = line.split()
            indices = [int(p.split("/")[0]) - 1 for p in parts[1:]]
            obj_faces.append(indices)

    # Reconstruct strip vertex lists using sidecar metadata
    header = sidecar.get("header", [0, 0, 0, 0])
    strip_count = sidecar["num_strips"]
    strip_meta = sidecar["strips"]

    # Map vertices from OBJ back to strips using sidecar vertex counts.
    # The OBJ stores all vertices in order: strip 0 vertex 0..N0-1,
    # strip 1 vertex 0..N1-1, etc.
    vert_offset = 0
    reconstructed_strips = []
    for i, smeta in enumerate(strip_meta):
        nv = smeta["num_vertices"]
        if vert_offset + nv > len(obj_verts):
            nv = max(0, len(obj_verts) - vert_offset)

        strip_verts = obj_verts[vert_offset : vert_offset + nv]
        vert_offset += nv

        reconstructed_strips.append(
            {
                "orig_type": smeta["type"],
                "header_w0": smeta["header_w0"],
                "header_w1": smeta["header_w1"],
                "verts": strip_verts,
                "meta_hex": smeta.get("meta_hex", []),
            }
        )

    # Build binary
    buf = bytearray()
    buf.extend(struct.pack("<HHHH", *header))

    for si, s in enumerate(reconstructed_strips):
        verts = s["verts"]
        meta_hex = s.get("meta_hex", [])
        orig_type = s.get("orig_type", "A")
        is_header_strip = orig_type == "B" or orig_type == "C"

        for i, (x, y, z) in enumerate(verts):
            if si == 0:
                # First strip — always Type A layout
                buf.extend(struct.pack("<fff", x, y, z))
                if i < len(meta_hex):
                    buf.extend(bytes.fromhex(meta_hex[i]))
                else:
                    buf.extend(b"\x00" * 8)
            elif is_header_strip and i == 0:
                # Header vertex of Type B/C strip — NaN + metadata + position
                buf.extend(struct.pack("<II", s["header_w0"], s["header_w1"]))
                buf.extend(struct.pack("<fff", x, y, z))
            elif orig_type == "B":
                # Type B body vertex — meta at 0-7, position at 8-19
                if i - 1 < len(meta_hex):
                    buf.extend(bytes.fromhex(meta_hex[i - 1]))
                else:
                    buf.extend(b"\x00" * 8)
                buf.extend(struct.pack("<fff", x, y, z))
            elif orig_type == "C":
                # Type C: x at 0-3, y at 4-7, meta at 8-15, z at 16-19
                buf.extend(struct.pack("<ff", x, y))
                if i - 1 < len(meta_hex):
                    buf.extend(bytes.fromhex(meta_hex[i - 1]))
                else:
                    buf.extend(b"\x00" * 8)
                buf.extend(struct.pack("<f", z))
            elif orig_type == "A":
                buf.extend(struct.pack("<fff", x, y, z))
                if i < len(meta_hex):
                    buf.extend(bytes.fromhex(meta_hex[i]))
                else:
                    buf.extend(b"\x00" * 8)

    with open(output_path, "wb") as f:
        f.write(buf)

    return len(buf)


# ====================================================================
# CLI
# ====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Extract and compile Virtual On MT_*.BIN 3D model files."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Extract
    extr = sub.add_parser("extract", help="Extract MT binary to OBJ + JSON sidecar")
    extr.add_argument("input", help="Input .BIN file")
    extr.add_argument("-o", "--output", help="Output base name (default: <input>)")

    # Compile
    comp = sub.add_parser("compile", help="Compile OBJ back to MT binary (needs sidecar)")
    comp.add_argument("input", help="Input .obj file")
    comp.add_argument("-o", "--output", help="Output .BIN file")
    comp.add_argument(
        "--sidecar",
        help="Path to JSON sidecar (default: <input>.json)",
    )
    comp.add_argument(
        "--original",
        help="Path to original .BIN (to find .json sidecar)",
    )

    args = parser.parse_args()

    if args.command == "extract":
        out = args.output or os.path.splitext(args.input)[0]
        result = mt_extract(args.input, Path(out))
        print(f"Extracted: {result['strips']} strips, "
              f"{result['vertices']} vertices, {result['triangles']} triangles")
        print(f"  OBJ:     {result['obj']}")
        print(f"  Sidecar: {result['sidecar']}")

    elif args.command == "compile":
        out = args.output or Path(args.input).with_suffix(".bin")
        original = args.original
        sidecar = args.sidecar
        size = mt_compile(args.input, out, sidecar_path=sidecar, original_path=original)
        print(f"Compiled: {size} bytes -> {out}")


if __name__ == "__main__":
    main()
