#!/usr/bin/env python3
"""
voff_viewer.py — 3D model viewer for Virtual On models.

Supports OBJ files (from voff_mt_tool.py) and direct MT_*.BIN files.
Uses pyglet 2.x for OpenGL windowing.

Controls:
    Left drag    — orbit around model
    Middle drag  — pan
    Scroll       — zoom
    W            — wireframe toggle
    L            — lighting toggle
    F            — fit view to model
    Escape       — quit

Usage:
    python3 voff_viewer.py model.obj
    python3 voff_viewer.py MT_ZIG.BIN
    python3 voff_viewer.py model1.obj model2.obj  # load multiple models
"""

import math
import struct
import sys
from pathlib import Path
import ctypes

import numpy as np
import pyglet
from pyglet.gl import gl

# ====================================================================
# Shaders (embedded, no external files needed)
# ====================================================================

VERTEX_SHADER = b"""
#version 130
uniform mat4 u_modelview;
uniform mat4 u_projection;
uniform mat3 u_normalmat;
in vec3 a_position;
in vec3 a_normal;
out vec3 v_normal;
out vec3 v_pos;
void main() {
    vec4 world_pos = u_modelview * vec4(a_position, 1.0);
    gl_Position = u_projection * world_pos;
    v_normal = u_normalmat * a_normal;
    v_pos = world_pos.xyz;
}
"""

FRAGMENT_SHADER = b"""
#version 130
uniform vec3 u_color;
uniform vec3 u_light_dir;
uniform float u_ambient;
uniform int u_lighting;
in vec3 v_normal;
in vec3 v_pos;
out vec4 frag_color;
void main() {
    if (u_lighting == 0) {
        frag_color = vec4(u_color, 1.0);
        return;
    }
    vec3 n = normalize(v_normal);
    float diff = max(dot(n, u_light_dir), 0.0);
    float light = u_ambient + (1.0 - u_ambient) * diff;
    frag_color = vec4(u_color * light, 1.0);
}
"""


def compile_shader(source, shader_type):
    """Compile a GLSL shader, return handle."""
    handle = gl.glCreateShader(shader_type)
    gl.glShaderSource(handle, 1, ctypes.cast(
        ctypes.pointer(ctypes.c_char_p(source)),
        ctypes.POINTER(ctypes.POINTER(ctypes.c_char))
    ), None)
    gl.glCompileShader(handle)
    result = (gl.GLint * 1)()
    gl.glGetShaderiv(handle, gl.GL_COMPILE_STATUS, result)
    if result[0] != gl.GL_TRUE:
        log_len = (gl.GLint * 1)()
        gl.glGetShaderiv(handle, gl.GL_INFO_LOG_LENGTH, log_len)
        log_buf = ctypes.create_string_buffer(log_len[0])
        gl.glGetShaderInfoLog(handle, log_len[0], None, log_buf)
        raise RuntimeError(f"Shader compile error: {log_buf.value.decode()}")
    return handle


def link_program(vs, fs):
    """Link vertex + fragment shaders into a program."""
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, vs)
    gl.glAttachShader(prog, fs)
    gl.glLinkProgram(prog)
    result = (gl.GLint * 1)()
    gl.glGetProgramiv(prog, gl.GL_LINK_STATUS, result)
    if result[0] != gl.GL_TRUE:
        log_len = (gl.GLint * 1)()
        gl.glGetProgramiv(prog, gl.GL_INFO_LOG_LENGTH, log_len)
        log_buf = ctypes.create_string_buffer(log_len[0])
        gl.glGetProgramInfoLog(prog, log_len[0], None, log_buf)
        raise RuntimeError(f"Program link error: {log_buf.value.decode()}")
    return prog


# ====================================================================
# OBJ Parser
# ====================================================================

def parse_obj(path):
    """Parse a Wavefront OBJ file. Returns list of strips, each a list of (x,y,z).

    Handles 'o' (object) and 'g' (group) lines as strip boundaries.
    """
    vertices = []
    groups = []       # list of (name, face_index_lists)
    current_faces = []

    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("v "):
                parts = line.split()
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("f "):
                parts = line.split()
                indices = [int(p.split("/")[0]) - 1 for p in parts[1:]]
                current_faces.append(indices)
            elif line.startswith("o ") or line.startswith("g "):
                if current_faces:
                    groups.append((line[2:].strip(), current_faces))
                    current_faces = []

    if current_faces:
        groups.append(("unnamed", current_faces))

    # If no groups, all faces are one group
    if not groups:
        return [vertices] if not current_faces else [[vertices[i] for i in current_faces[0]]]

    # Each group is a strip — convert faces to vertex positions
    strips = []
    for name, faces in groups:
        if not faces:
            continue
        # Faces should already be in triangle strip order from our exporter.
        # First triangle gives 3 verts, each subsequent triangle adds 1 vert.
        strip = [vertices[i] for i in faces[0]]
        for fi in range(1, len(faces)):
            # Find the vertex not in the previous triangle
            prev = set(faces[fi - 1])
            curr = set(faces[fi])
            new_vert = list(curr - prev)
            if new_vert:
                strip.append(vertices[new_vert[0]])
            elif len(curr) == 3:
                # Degenerate / restart: add all 3 as new vertices
                strip.extend(vertices[i] for i in faces[fi])
        strips.append(strip)

    return strips


# ====================================================================
# MT File Parser
# ====================================================================

def _is_ok_position(v):
    return not math.isnan(v) and not math.isinf(v) and abs(v) < 5000


def parse_mt(path):
    """Parse an MT_*.BIN file directly. Returns list of strips."""
    with open(path, "rb") as f:
        data = f.read()

    strips = []
    current = None
    stride = 20

    for vi in range(len(data) // stride):
        pos = 8 + vi * stride
        if pos + stride > len(data):
            break

        word0 = struct.unpack_from("<I", data, pos)[0]
        exponent = (word0 >> 23) & 0xFF
        mantissa = word0 & 0x007FFFFF
        is_nan = exponent == 0xFF and mantissa != 0

        if is_nan:
            if current:
                strips.append(current)
            x = struct.unpack_from("<f", data, pos + 8)[0]
            y = struct.unpack_from("<f", data, pos + 12)[0]
            z = struct.unpack_from("<f", data, pos + 16)[0]
            current = [(x, y, z)]
        else:
            x1, y1, z1 = struct.unpack_from("<fff", data, pos)
            z3 = struct.unpack_from("<f", data, pos + 16)[0]
            x2, y2, z2 = struct.unpack_from("<fff", data, pos + 8)

            if all(_is_ok_position(c) for c in (x1, y1, z1)):
                p = (x1, y1, z1)
            elif all(_is_ok_position(c) for c in (x1, y1, z3)):
                p = (x1, y1, z3)
            elif all(_is_ok_position(c) for c in (x2, y2, z2)):
                p = (x2, y2, z2)
            else:
                continue

            if current is None:
                current = [p]
            else:
                current.append(p)

    if current:
        strips.append(current)

    return strips


# ====================================================================
# Model Builder
# ====================================================================

class Model:
    """A loaded model with GPU buffers (created lazily on first draw)."""

    def __init__(self, strips, name="", color=(1.0, 0.6, 0.2), offset=(0, 0, 0)):
        self.name = name
        self.color = color
        self.offset = offset
        self.strips = strips
        self._gpu_ready = False
        self._build_cpu_data()

    def _build_cpu_data(self):
        """Compute vertex arrays and strip ranges on CPU (no GL needed)."""
        all_verts = []
        all_norms = []

        for strip in self.strips:
            for i in range(len(strip)):
                all_verts.extend(strip[i])
                if i < len(strip) - 2:
                    a, b, c = strip[i], strip[i + 1], strip[i + 2]
                    ux = b[0] - a[0]; uy = b[1] - a[1]; uz = b[2] - a[2]
                    vx = c[0] - a[0]; vy = c[1] - a[1]; vz = c[2] - a[2]
                    nx = uy * vz - uz * vy
                    ny = uz * vx - ux * vz
                    nz = ux * vy - uy * vx
                    ln = math.sqrt(nx * nx + ny * ny + nz * nz)
                    if ln > 0.0001:
                        nx, ny, nz = nx / ln, ny / ln, nz / ln
                    all_norms.extend((nx, ny, nz))
                elif i > 0:
                    all_norms.extend(all_norms[-3:])
                else:
                    all_norms.extend((0.0, 1.0, 0.0))

        self.vertex_data = np.array(all_verts, dtype=np.float32)
        self.normal_data = np.array(all_norms, dtype=np.float32)
        self.vertex_count = len(all_verts) // 3

        self.strip_ranges = []
        offset = 0
        for s in self.strips:
            self.strip_ranges.append((offset, len(s)))
            offset += len(s)

    def _init_gl(self):
        """Create GPU buffers (call when GL context is active)."""
        if self._gpu_ready:
            return

        self.vbo_verts = gl.GLuint()
        gl.glGenBuffers(1, self.vbo_verts)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_verts)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            self.vertex_data.nbytes,
            self.vertex_data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            gl.GL_STATIC_DRAW,
        )

        self.vbo_norms = gl.GLuint()
        gl.glGenBuffers(1, self.vbo_norms)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_norms)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            self.normal_data.nbytes,
            self.normal_data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            gl.GL_STATIC_DRAW,
        )

        self.vao = gl.GLuint()
        gl.glGenVertexArrays(1, self.vao)
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_verts)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_norms)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(1)
        gl.glBindVertexArray(0)

        self._gpu_ready = True

    @property
    def total_vertices(self):
        return sum(len(s) for s in self.strips)

    @property
    def total_triangles(self):
        return sum(max(0, len(s) - 2) for s in self.strips)

    @property
    def bounds(self):
        """Return [min_x, max_x, min_y, max_y, min_z, max_z]."""
        all_v = [v for s in self.strips for v in s]
        if not all_v:
            return [0, 0, 0, 0, 0, 0]
        xs = [v[0] for v in all_v]
        ys = [v[1] for v in all_v]
        zs = [v[2] for v in all_v]
        return [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]


# ====================================================================
# Camera
# ====================================================================

class Camera:
    """Orbit camera."""

    def __init__(self):
        self.radius = 200.0
        self.theta = 0.5
        self.phi = 0.4
        self.target = [0.0, 0.0, 0.0]
        self.rotate_speed = 0.005
        self.zoom_speed = 1.05
        self.pan_speed = 1.0

    def orbit(self, dx, dy):
        self.theta -= dx * self.rotate_speed
        self.phi += dy * self.rotate_speed
        self.phi = max(-math.pi / 2 + 0.05, min(math.pi / 2 - 0.05, self.phi))

    def pan(self, dx, dy):
        right = (-math.sin(self.theta), 0.0, math.cos(self.theta))
        up = (
            math.sin(self.phi) * math.cos(self.theta),
            -math.cos(self.phi),
            math.sin(self.phi) * math.sin(self.theta),
        )
        scale = self.radius / 200.0 * self.pan_speed
        self.target[0] += (right[0] * dx + up[0] * dy) * scale
        self.target[1] += (right[1] * dx + up[1] * dy) * scale
        self.target[2] += (right[2] * dx + up[2] * dy) * scale

    def zoom(self, amount):
        self.radius *= self.zoom_speed ** amount
        self.radius = max(1.0, min(2000.0, self.radius))

    def fit(self, bounds):
        cx = (bounds[0] + bounds[1]) / 2
        cy = (bounds[2] + bounds[3]) / 2
        cz = (bounds[4] + bounds[5]) / 2
        dx = bounds[1] - bounds[0]
        dy = bounds[3] - bounds[2]
        dz = bounds[5] - bounds[4]
        self.target = [cx, cy, cz]
        self.radius = max(dx, dy, dz) * 1.5
        self.theta = 0.5
        self.phi = 0.4

    def view_matrix(self):
        """Return 4x4 view matrix as list-of-floats (column-major for OpenGL)."""
        eye_x = self.target[0] + self.radius * math.cos(self.phi) * math.cos(self.theta)
        eye_y = self.target[1] + self.radius * math.sin(self.phi)
        eye_z = self.target[2] + self.radius * math.cos(self.phi) * math.sin(self.theta)

        fwd = (
            self.target[0] - eye_x,
            self.target[1] - eye_y,
            self.target[2] - eye_z,
        )
        fl = math.sqrt(fwd[0] ** 2 + fwd[1] ** 2 + fwd[2] ** 2)
        if fl > 0:
            fwd = (fwd[0] / fl, fwd[1] / fl, fwd[2] / fl)

        up = (0.0, 1.0, 0.0)
        right = (
            up[1] * fwd[2] - up[2] * fwd[1],
            up[2] * fwd[0] - up[0] * fwd[2],
            up[0] * fwd[1] - up[1] * fwd[0],
        )
        rl = math.sqrt(right[0] ** 2 + right[1] ** 2 + right[2] ** 2)
        if rl > 0:
            right = (right[0] / rl, right[1] / rl, right[2] / rl)

        new_up = (
            fwd[1] * right[2] - fwd[2] * right[1],
            fwd[2] * right[0] - fwd[0] * right[2],
            fwd[0] * right[1] - fwd[1] * right[0],
        )

        # LookAt matrix (column-major)
        return [
            right[0], new_up[0], -fwd[0], 0.0,
            right[1], new_up[1], -fwd[1], 0.0,
            right[2], new_up[2], -fwd[2], 0.0,
            -(right[0] * eye_x + right[1] * eye_y + right[2] * eye_z),
            -(new_up[0] * eye_x + new_up[1] * eye_y + new_up[2] * eye_z),
            (fwd[0] * eye_x + fwd[1] * eye_y + fwd[2] * eye_z),
            1.0,
        ]

    @staticmethod
    def perspective(fov_y, aspect, near, far):
        """Return 4x4 perspective matrix (column-major)."""
        f = 1.0 / math.tan(fov_y / 2.0)
        return [
            f / aspect, 0.0, 0.0, 0.0,
            0.0, f, 0.0, 0.0,
            0.0, 0.0, (far + near) / (near - far), -1.0,
            0.0, 0.0, (2.0 * far * near) / (near - far), 0.0,
        ]


# ====================================================================
# Grid
# ====================================================================

class Grid:
    """Reference grid on the XZ plane (GPU buffers created lazily)."""

    def __init__(self, size=300, step=10):
        verts = []
        for i in range(-size, size + 1, step):
            verts.extend((float(i), 0.0, float(-size)))
            verts.extend((float(i), 0.0, float(size)))
            verts.extend((float(-size), 0.0, float(i)))
            verts.extend((float(size), 0.0, float(i)))

        self.vertex_data = np.array(verts, dtype=np.float32)
        self.vertex_count = len(verts) // 3
        self._gpu_ready = False

    def _init_gl(self):
        if self._gpu_ready:
            return

        self.vbo = gl.GLuint()
        gl.glGenBuffers(1, self.vbo)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            self.vertex_data.nbytes,
            self.vertex_data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            gl.GL_STATIC_DRAW,
        )

        self.vao = gl.GLuint()
        gl.glGenVertexArrays(1, self.vao)
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, 0)
        gl.glEnableVertexAttribArray(0)
        gl.glBindVertexArray(0)

        self._gpu_ready = True


# ====================================================================
# Renderer
# ====================================================================

class Renderer:
    """Manages shader programs and drawing."""

    def __init__(self):
        vs = compile_shader(VERTEX_SHADER, gl.GL_VERTEX_SHADER)
        fs = compile_shader(FRAGMENT_SHADER, gl.GL_FRAGMENT_SHADER)
        self.program = link_program(vs, fs)
        gl.glDeleteShader(vs)
        gl.glDeleteShader(fs)

        self.u_modelview = gl.glGetUniformLocation(self.program, b"u_modelview")
        self.u_projection = gl.glGetUniformLocation(self.program, b"u_projection")
        self.u_normalmat = gl.glGetUniformLocation(self.program, b"u_normalmat")
        self.u_color = gl.glGetUniformLocation(self.program, b"u_color")
        self.u_light_dir = gl.glGetUniformLocation(self.program, b"u_light_dir")
        self.u_ambient = gl.glGetUniformLocation(self.program, b"u_ambient")
        self.u_lighting = gl.glGetUniformLocation(self.program, b"u_lighting")

    def draw_grid(self, grid, projection, view):
        grid._init_gl()
        gl.glUseProgram(self.program)

        model = [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ]
        mv = self._multiply(view, model)

        normal_mat = [
            mv[0], mv[1], mv[2],
            mv[4], mv[5], mv[6],
            mv[8], mv[9], mv[10],
        ]

        gl.glUniformMatrix4fv(self.u_modelview, 1, gl.GL_TRUE, (gl.GLfloat * 16)(*mv))
        gl.glUniformMatrix4fv(self.u_projection, 1, gl.GL_TRUE, (gl.GLfloat * 16)(*projection))
        gl.glUniformMatrix3fv(self.u_normalmat, 1, gl.GL_FALSE, (gl.GLfloat * 9)(*normal_mat))
        gl.glUniform3f(self.u_color, 0.25, 0.25, 0.28)
        gl.glUniform3f(self.u_light_dir, 0.0, 0.0, 0.0)
        gl.glUniform1f(self.u_ambient, 1.0)
        gl.glUniform1i(self.u_lighting, 0)

        gl.glBindVertexArray(grid.vao)
        gl.glDrawArrays(gl.GL_LINES, 0, grid.vertex_count)
        gl.glBindVertexArray(0)

    def draw_model(self, model, projection, view, wireframe=False, lighting=True):
        model._init_gl()

        gl.glUseProgram(self.program)

        ox, oy, oz = model.offset
        r, g, b = model.color

        model_mat = [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            ox, oy, oz, 1.0,
        ]
        mv = self._multiply(view, model_mat)

        normal_mat = [
            mv[0], mv[1], mv[2],
            mv[4], mv[5], mv[6],
            mv[8], mv[9], mv[10],
        ]

        gl.glUniformMatrix4fv(self.u_modelview, 1, gl.GL_TRUE, (gl.GLfloat * 16)(*mv))
        gl.glUniformMatrix4fv(self.u_projection, 1, gl.GL_TRUE, (gl.GLfloat * 16)(*projection))
        gl.glUniformMatrix3fv(self.u_normalmat, 1, gl.GL_FALSE, (gl.GLfloat * 9)(*normal_mat))
        gl.glUniform3f(self.u_color, r, g, b)
        gl.glUniform3f(self.u_light_dir, 0.5, 0.8, 1.0)
        gl.glUniform1f(self.u_ambient, 0.2)
        gl.glUniform1i(self.u_lighting, 1 if lighting else 0)

        if wireframe:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

        gl.glBindVertexArray(model.vao)

        for start, count in model.strip_ranges:
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, start, count)

        gl.glBindVertexArray(0)

        if wireframe:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    def _multiply(self, a, b):
        """Column-major 4x4 matrix multiply."""
        result = [0.0] * 16
        for col in range(4):
            for row in range(4):
                s = 0.0
                for k in range(4):
                    s += a[k * 4 + row] * b[col * 4 + k]
                result[col * 4 + row] = s
        return result


# ====================================================================
# Main Window
# ====================================================================

class ViewerWindow(pyglet.window.Window):
    def __init__(self, models, width=1280, height=800):
        config = pyglet.gl.Config(
            double_buffer=True,
            depth_size=24,
            sample_buffers=1,
            samples=4,
        )
        try:
            super().__init__(
                width=width,
                height=height,
                caption="Virtual On Model Viewer",
                resizable=True,
                config=config,
            )
        except Exception:
            super().__init__(
                width=width,
                height=height,
                caption="Virtual On Model Viewer",
                resizable=True,
            )

        self.models = models
        self.camera = Camera()
        self.wireframe = False
        self.lighting = True
        self.renderer = None
        self.grid = None

        # Compute global bounds
        all_bounds = [m.bounds for m in models]
        if all_bounds:
            gx_min = min(b[0] for b in all_bounds)
            gx_max = max(b[1] for b in all_bounds)
            gy_min = min(b[2] for b in all_bounds)
            gy_max = max(b[3] for b in all_bounds)
            gz_min = min(b[4] for b in all_bounds)
            gz_max = max(b[5] for b in all_bounds)
            self.camera.fit([gx_min, gx_max, gy_min, gy_max, gz_min, gz_max])

        self._drag_button = None
        self._last_x = 0
        self._last_y = 0
        self._fps_display = pyglet.window.FPSDisplay(window=self)

        pyglet.clock.schedule_interval(self._update, 1 / 60.0)

    def _init_gl(self):
        if self.renderer is not None:
            return
        self.renderer = Renderer()
        self.grid = Grid()
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClearColor(0.15, 0.15, 0.18, 1.0)

    def _update(self, dt):
        pass

    def on_draw(self):
        self._init_gl()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        projection = Camera.perspective(
            45.0 * math.pi / 180.0,
            self.width / max(self.height, 1),
            1.0,
            5000.0,
        )
        view = self.camera.view_matrix()

        self.renderer.draw_grid(self.grid, projection, view)

        for model in self.models:
            self.renderer.draw_model(
                model, projection, view,
                wireframe=self.wireframe,
                lighting=self.lighting,
            )

        self._draw_hud()

    def _draw_hud(self):
        y = self.height - 20
        for i, model in enumerate(self.models):
            label = pyglet.text.Label(
                f"[{i}] {model.name} — {model.total_vertices:,} verts, "
                f"{len(model.strips)} strips, {model.total_triangles:,} tris",
                font_name="monospace",
                font_size=12,
                x=10,
                y=y,
                color=(220, 220, 220, 255),
            )
            label.draw()
            y -= 18

        mode_label = pyglet.text.Label(
            f"Mode: {'WIREFRAME' if self.wireframe else 'SOLID'} | "
            f"Lighting: {'ON' if self.lighting else 'OFF'} | "
            f"W=toggle wireframe  L=toggle lights  F=fit view",
            font_name="monospace",
            font_size=11,
            x=10,
            y=20,
            color=(150, 150, 160, 255),
        )
        mode_label.draw()

        self._fps_display.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        gl.glViewport(0, 0, width, height)

    def on_mouse_press(self, x, y, button, modifiers):
        self._drag_button = button
        self._last_x = x
        self._last_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        self._drag_button = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self._drag_button == pyglet.window.mouse.LEFT:
            self.camera.orbit(dx, dy)
        elif self._drag_button == pyglet.window.mouse.MIDDLE:
            self.camera.pan(dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.camera.zoom(scroll_y)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.W:
            self.wireframe = not self.wireframe
        elif symbol == pyglet.window.key.L:
            self.lighting = not self.lighting
        elif symbol == pyglet.window.key.F:
            all_bounds = [m.bounds for m in self.models]
            gx_min = min(b[0] for b in all_bounds)
            gx_max = max(b[1] for b in all_bounds)
            gy_min = min(b[2] for b in all_bounds)
            gy_max = max(b[3] for b in all_bounds)
            gz_min = min(b[4] for b in all_bounds)
            gz_max = max(b[5] for b in all_bounds)
            self.camera.fit([gx_min, gx_max, gy_min, gy_max, gz_min, gz_max])
        elif symbol == pyglet.window.key.ESCAPE:
            self.close()


# ====================================================================
# Entry Point
# ====================================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    models = []
    colors = [
        (1.0, 0.6, 0.2),
        (0.3, 0.7, 1.0),
        (0.4, 1.0, 0.5),
        (1.0, 0.4, 0.7),
        (0.9, 0.9, 0.3),
    ]

    for i, path in enumerate(sys.argv[1:]):
        p = Path(path)
        if not p.exists():
            print(f"Skipping: {path} (not found)")
            continue

        if p.suffix.lower() in (".obj",):
            strips = parse_obj(path)
        elif p.suffix.lower() in (".bin",):
            strips = parse_mt(path)
        else:
            print(f"Unknown format: {p.suffix}")
            continue

        if not strips:
            print(f"No geometry found in: {path}")
            continue

        ox = (i % 3) * 150 - 150
        oz = (i // 3) * 150

        model = Model(
            strips=strips,
            name=p.stem,
            color=colors[i % len(colors)],
            offset=(ox, 0, oz),
        )
        models.append(model)
        print(f"Loaded: {p.name} — {model.total_vertices:,} verts, "
              f"{len(strips)} strips, {model.total_triangles:,} tris")

    if not models:
        print("No models loaded.")
        sys.exit(1)

    ViewerWindow(models)
    pyglet.app.run()


if __name__ == "__main__":
    main()
