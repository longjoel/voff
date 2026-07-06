"""
import_mt_blender.py — Import Virtual On MT_*.BIN models directly into Blender.

Run from Blender's Scripting workspace (Alt+P) or via command line:

    blender --python import_mt_blender.py -- /path/to/MT_ZIG.BIN

Each triangle strip becomes a separate mesh object, named by strip index
and vertex count. The main body mesh (strip 0) is selected on import.
"""

import struct
import math
import os
import sys
from pathlib import Path

import bpy
import bmesh


# ====================================================================
# MT File Parser (same logic as voff_mt_tool.py)
# ====================================================================

def _is_ok_position(v):
    return not math.isnan(v) and not math.isinf(v) and abs(v) < 5000


def parse_mt_strips(filepath):
    """Parse an MT binary file. Returns list of strips, each a dict with
    type, verts (list of (x,y,z)), header_w0, header_w1."""
    with open(filepath, "rb") as f:
        data = f.read()

    strips = []
    current = None

    for vi in range(len(data) // 20):
        pos = 8 + vi * 20
        if pos + 20 > len(data):
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
            }
        else:
            x1 = struct.unpack_from("<f", data, pos)[0]
            y1 = struct.unpack_from("<f", data, pos + 4)[0]
            z1 = struct.unpack_from("<f", data, pos + 8)[0]
            z3 = struct.unpack_from("<f", data, pos + 16)[0]
            x2 = struct.unpack_from("<f", data, pos + 8)[0]
            y2 = struct.unpack_from("<f", data, pos + 12)[0]
            z2 = struct.unpack_from("<f", data, pos + 16)[0]

            if all(_is_ok_position(c) for c in (x1, y1, z1)):
                vt = "A"
                p = (x1, y1, z1)
            elif all(_is_ok_position(c) for c in (x1, y1, z3)):
                vt = "C"
                p = (x1, y1, z3)
            elif all(_is_ok_position(c) for c in (x2, y2, z2)):
                vt = "B"
                p = (x2, y2, z2)
            else:
                continue

            if current is None:
                current = {"type": vt, "header_w0": 0, "header_w1": 0, "verts": [p]}
            else:
                current["verts"].append(p)
                current["type"] = vt

    if current and current["verts"]:
        strips.append(current)

    return strips


# ====================================================================
# Blender Mesh Builder
# ====================================================================

def _clean_scene():
    """Remove default cube and other startup objects."""
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def _create_material(name, color):
    """Create a simple diffuse material."""
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = (*color, 1.0)
    return mat


COLLECTION_COLORS = [
    (1.0, 0.5, 0.1),     # orange — large strips (main body)
    (1.0, 0.7, 0.3),     # light orange — medium strips (parts)
    (0.3, 0.6, 0.9),     # blue — small strips
    (0.7, 0.2, 0.2),     # red — tiny strips (separators)
]


def import_mt(filepath, merge_strips=True, skip_single_verts=True):
    """Import an MT file into the current Blender scene.

    Args:
        filepath: Path to .BIN file
        merge_strips: If True, merge all strips into one mesh object.
                      If False, each strip is a separate object.
        skip_single_verts: If True, skip 1-vertex strips (separator markers).
    """
    strips = parse_mt_strips(filepath)
    name = Path(filepath).stem

    if merge_strips:
        return _import_merged(strips, name, skip_single_verts)
    else:
        return _import_separate(strips, name, skip_single_verts)


def _import_merged(strips, name, skip_single_verts):
    """Import all strips as a single mesh with separate materials per strip
    size category."""
    bm = bmesh.new()
    materials = {}
    for idx, color in enumerate(COLLECTION_COLORS):
        materials[idx] = _create_material(f"{name}_mat_{idx}", color)

    vert_index = 0
    for si, s in enumerate(strips):
        nv = len(s["verts"])
        if skip_single_verts and nv < 2:
            continue
        if nv < 3:
            continue  # need at least 3 verts for a triangle

        # Determine material by strip size
        if nv > 500:
            mat_idx = 0
        elif nv > 100:
            mat_idx = 1
        elif nv > 10:
            mat_idx = 2
        else:
            mat_idx = 3

        # Add vertices
        first_v = len(bm.verts)
        for x, y, z in s["verts"]:
            bm.verts.new((x, y, z))
        bm.verts.ensure_lookup_table()

        # Add faces as triangle strip
        for i in range(nv - 2):
            a = bm.verts[first_v + i]
            b = bm.verts[first_v + i + 1]
            c = bm.verts[first_v + i + 2]
            # Skip degenerate triangles (duplicate vertices)
            ca, cb, cc = a.co, b.co, c.co
            if (ca == cb) or (cb == cc) or (ca == cc):
                continue
            try:
                face = bm.faces.new((a, b, c))
                face.material_index = mat_idx
                face.smooth = False
            except ValueError:
                pass  # duplicate face

    bm.faces.ensure_lookup_table()

    # Create mesh object
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)

    # Assign materials
    for mat in materials.values():
        obj.data.materials.append(mat)

    # Put in a collection named after the file
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    coll.objects.link(obj)

    # Set origin to geometry center
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    return obj


def _import_separate(strips, name, skip_single_verts):
    """Import each strip as a separate mesh object."""
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)

    objs = []
    for si, s in enumerate(strips):
        nv = len(s["verts"])
        if skip_single_verts and nv < 2:
            continue
        if nv < 3:
            continue  # no triangles

        mesh = bpy.data.meshes.new(f"{name}_{si:03d}")
        obj = bpy.data.objects.new(f"{name}_{si:03d}", mesh)
        coll.objects.link(obj)

        # Build mesh
        verts = s["verts"]
        edges = []
        faces = []
        for i in range(nv - 2):
            faces.append((i, i + 1, i + 2))

        mesh.from_pydata(verts, edges, faces)
        mesh.update()

        # Color by size
        if nv > 500:
            color = COLLECTION_COLORS[0]
        elif nv > 100:
            color = COLLECTION_COLORS[1]
        elif nv > 10:
            color = COLLECTION_COLORS[2]
        else:
            color = COLLECTION_COLORS[3]

        mat = _create_material(f"{name}_mat_{si}", color)
        obj.data.materials.append(mat)

        objs.append(obj)

    # Select the largest object
    if objs:
        largest = max(objs, key=lambda o: len(o.data.vertices))
        bpy.context.view_layer.objects.active = largest
        largest.select_set(True)
        # Zoom to it
        bpy.ops.object.select_all(action="DESELECT")
        largest.select_set(True)
        bpy.ops.view3d.view_selected()


# ====================================================================
# Additional setup
# ====================================================================

def setup_scene():
    """Configure render, lighting, and viewport."""
    # Viewport shading
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "SOLID"
                    space.shading.color_type = "MATERIAL"
                    space.shading.show_backface_culling = True

    # World background
    world = bpy.data.worlds.new("VON_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.08, 0.08, 0.11, 1.0)

    # Add sun light
    light_data = bpy.data.lights.new("VON_Sun", "SUN")
    light_data.energy = 3.0
    light_data.angle = 0.1
    light_obj = bpy.data.objects.new("VON_Sun", light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.rotation_euler = (0.8, 0.2, 0.6)

    # Add fill light
    fill_data = bpy.data.lights.new("VON_Fill", "SUN")
    fill_data.energy = 0.8
    fill_obj = bpy.data.objects.new("VON_Fill", fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (-0.3, -1.2, -0.5)


# ====================================================================
# Entry Point
# ====================================================================

def main():
    # Parse args after '--' separator
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        # Running from Blender's text editor: look for MT files in cwd
        argv = [str(p) for p in Path(".").glob("MT_*.BIN")]

    if not argv:
        print("Usage: blender --python import_mt_blender.py -- model.bin")
        print("   or: run from Blender text editor with MT_*.BIN in current dir")
        return

    filepath = argv[0]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    merge = "--separate" not in sys.argv

    print(f"Importing: {filepath}")
    print(f"  Mode: {'merged' if merge else 'separate objects'}")

    _clean_scene()
    setup_scene()

    obj = import_mt(filepath, merge_strips=merge)

    if obj:
        print(f"  Done: {len(obj.data.vertices):,} vertices, "
              f"{len(obj.data.polygons):,} triangles")
    else:
        print("  No geometry imported.")
        return

    # Save .blend if requested
    blend_path = filepath.rsplit(".", 1)[0] + ".blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  Saved: {blend_path}")

    # Frame the view (only works in GUI mode)
    try:
        bpy.ops.view3d.view_selected()
    except RuntimeError:
        pass  # background mode, no viewport


if __name__ == "__main__":
    main()
