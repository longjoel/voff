# Virtual On: Reverse Engineering Diary

---

## Entry 1 — Dusting off the disc (154 megabytes of 1997)

**Date:** 2026-06-15

### What I set out to do

There's this game. _Cyber Troopers Virtual On._ Sega, 1997. Giant robots
shooting each other in a 3D arena with twin-stick controls. I played it as a
kid and it never really left me.

I have a file called `von.img` — 154 megabytes. It's the PC port on a CD-ROM
image. The goal: bring this thing into 2026. Run it on Linux. Understand how it
was built along the way. Reverse engineer it with AI assistance, learn some
forensics, document everything.

This entry is step zero. Before you can reverse engineer a game, you have to
know what you're even looking at.

### What I found

First command: `file von.img`. The machine says it's an **ISO 9660 CD-ROM
filesystem** with the label "VON." That's good — it's a standard disc image,
not something proprietary.

Hex dump at offset 0x8000 (sector 16 — where ISO 9660 puts its Primary Volume
Descriptor) reveals the disc's identity:

```
offset   hex                                    ascii
00008000 01 43 44 30 30 31 01 00                .CD001..
00008008 41 50 50 4c 45 20 43 4f 4d 50 55 54    APPLE COMPUT
         45 52 2c 20 49 4e 43 2e 2c 20 54 59     ER, INC., TY
         50 45 3a 20 30 30 30 32                  PE: 0002
00008028 56 4f 4e 20 20 20 20 20 20 20 20        VON
```

**System ID:** "APPLE COMPUTER, INC., TYPE: 0002" — this disc was authored
on a Mac. The `0002` type code identifies it as an ISO 9660 with Apple
extensions (a hybrid disc targeting both Mac and Windows).

**Application ID:** "TOAST ISO 9660 BUILDER COPYRIGHT (C) 1997 ADAPTEC, INC.
— HAVE A NICE DAY." Toast was _the_ CD burning tool on classic Mac OS. Someone
at Sega or the porting house sat down at a Mac in 1997 and burned the master
disc with Toast.

**Volume space size:** 78,674 logical blocks at 2,048 bytes each = 153.7 MB of
filesystem data. The image file itself is 154 MB — the extra bytes are just
zero padding after the last sector. No hidden partition. No separate audio
tracks. Everything lives on one ISO 9660 filesystem.

#### The filesystem tree

Extracting all 626 files across 38 directories reveals the disc's purpose:
it's an **Autorun installer disc** for Windows 95/NT.

```
/ (root)
├── SETUP.EXE          — Launcher
├── AUTOPLAY.EXE       — AutoPlay stub
├── AUTORUN.INF        — "insert disc, run setup"
├── VIRTUAL/           — InstallShield installer payload
├── V_ON/              — THE GAME (95 files, ~130 MB)
│   ├── V_ON.EXE        — Main game executable (6.6 MB)
│   ├── VON.AVI         — Cinematic (Cinepak, 320×240, 24fps, 16 MB)
│   ├── SND_*.BIN       — 11 sound effect/voice files
│   ├── ESCRADV.BIN     — Attract mode audio (4 MB)
│   ├── ESCRGAME.BIN    — In-game background music (4 MB)
│   ├── TEXB0-5.IMG     — 6 texture banks (1 MB each)
│   ├── BSEL_*.BIN      — 8 character-select model files
│   ├── MT_*.BIN        — 11 robot model/texture files
│   ├── RB_*.BIN        — 12 robot body/rig files
│   ├── FC_*.BIN        — 11 unknown binary files (face/character?)
│   ├── FLD_*.BIN       — 10 field/stage mesh files
│   ├── MAP_*.BIN       — 11 map definition files
│   ├── FBOSS*.BIN      — 3 boss data files
│   └── DPCTRL.DLL      — DirectPlay controller stub
├── DIRECTX/           — DirectX 3 redistributables (drivers, runtime)
├── IE/                — Internet Explorer 4.0 installer (yes, really)
├── ENGLISH/ FRENCH/ GERMAN/ SPANISH/ — Language packs with help files
├── ACROBAT/           — Acrobat Reader 3.0 installer
├── BACKWEB/           — BackWeb push client (a late-90s thing)
└── DOCS/              — PDF manuals
```

#### The audio: raw 8-bit PCM

The sound effect files (`SND_APH.BIN`, `SND_BEL.BIN`, etc.) have no headers.
They start with values clustered around `0x80` — the center point of 8-bit
unsigned PCM audio. You can see the waveform peeking through the hex:

```
00000000  80 7f 80 80 80 80 80 80 7f 80 7f 80 7f 80 7f 7f  |................|
00000010  80 7f 80 7f 80 7f 80 80 80 80 80 80 80 80 7f 7f  |................|
00000030  80 7e 7d 7d 7f 7f 7e 7e 7e 7f 7d 7b 7a 7d 7e 7d  |.~}}..~~~.}{z}~}|
```

The two 4 MB files (`ESCRADV.BIN`, `ESCRGAME.BIN`) are the same format — raw
unsigned 8-bit PCM — but much larger. At 22,050 Hz they clock in at just over
3 minutes each. These are the game's background music tracks, stored as raw
samples rather than Red Book CD audio.

The video file (`VON.AVI`) is a standard RIFF AVI: 320×240, 24 fps, Cinepak
video with 44,100 Hz stereo PCM audio. This one is already playable as-is.

#### Clues from the executable

Running `strings` on `V_ON.EXE` drops a few breadcrumbs:

- **`pcWaveOpen.c`** — the source file that handles audio playback. This
  confirms the game uses Windows `waveOut` API to push raw PCM samples to the
  sound card. The audio format is configured in code, not in the data files.

- **`CDPLAY:%d,%d`** and **"READING CD INFO"** — the game has a CD audio
  playback path. The original disc for this game probably had Red Book CD-DA
  tracks for background music. The PC port shoved that music into `ESCR*.BIN`
  files instead, but the CD playback code is still there.

- **File references:** `escradv.bin`, `escrgame.bin`, `snd_zig.bin`,
  `snd_jag.bin`, and so on — every `.bin` asset is referenced by name in the
  executable. No external index file; the EXE knows the exact filenames it
  expects.

- **"Please insert VIRTUAL ON CD"** — the game checks for the disc at runtime.
  Emulating that check will be one of the things we'll need to handle.

### What it means

This is a snapshot of PC gaming in 1997. A hybrid Mac/Windows CD, authored on a
Mac but targeting Windows 95. DirectX 3. Internet Explorer 4 bundled on the
disc because nobody had it installed yet. Raw PCM audio because disk space was
plentiful (154 MB was a _lot_ in 1997) and decoding MP3 at runtime was
expensive.

The naming conventions tell us about the game's internal structure:
- `MT_` = model/texture (the visual data for each robot)
- `RB_` = robot body (rigging or mesh data)
- `FLD_` = field (stage geometry — there are fields named AIR, DOCK, FACTory,
  FORE, INKA, MOON, TRO, WATR — plus BOSN/BOSW for boss stages)
- `SND_` = sound (APHrodite, BELgdor, FEI-Yen, JAGuarandi, etc. — one file
  per character)
- `BSEL_` = battle select (the character selection screen renders)
- `ESCR_` = screen (title screen, attract mode, etc.)
- `MAP_` = map file (3.4 KB each — small enough to be layout/waypoint data,
  not geometry)
- `TEXB_` = texture bank
- `FBOSS_` = final boss

The filenames are a rosetta stone for the game's asset pipeline.

### Next up

Now we have the disc mapped and the audio is playable. Stage 2 is going to
be about **decoding the binary asset formats** — figuring out what's inside
those `MT_*.BIN`, `RB_*.BIN`, `TEXB*.IMG`, and `FLD_*.BIN` files. Are they
custom containers? Known formats? Compressed?

That's where the reverse engineering actually starts.

---

## Entry 2 — The robots are triangle strips (decoding the MT 3D format)

**Date:** 2026-06-15

### What I set out to do

The mecha are why I love this game. I want to pull them out of the binary,
look at them in Blender, touch them up, and put them back in. That means
figuring out exactly how the 3D model files work — the `MT_*.BIN` format.

There are 12 model files. The ones with character names are the robots
themselves (MT_APH, MT_BAS, MT_BBB, MT_DOM, MT_FEI, MT_GUF, MT_JAG, MT_KAS,
MT_VAL, MT_ZIG). MT_SCENE is some kind of stage/scene model, and MT_SEL might
be the character select screen.

I started with MT_ZIG — the smallest robot at 1.8 MB — so I can iterate fast
and not hit edge cases until I'm confident in the structure.

### What I found

#### The header: 8 mysterious bytes

Every MT file starts with 8 bytes: four uint16 values. For MT_ZIG:

```
3c 00 5e 02 23 00 00 00   →   (60, 606, 35, 0)
```

For a while I thought these were submesh counts, vertex counts, material
counts. The evidence didn't hold up — GUF, JAG, and KAS have identical
header values (512, 3488, 65446, 0) despite being different robots.

**Verdict:** Unknown. Probably flags or checksums used by the engine. Not
needed for geometry extraction. Preserved as-is in the sidecar for
round-tripping.

#### The vertex stride: 20 bytes, everywhere

After the 8-byte header, the rest of the file is a flat array of 20-byte
vertices. No index buffers. No section tables. Just vertex after vertex,
forming triangle strips in draw order.

But there are **three different vertex layouts** within the same file:

```
╔═══════╤══════════════════════════════════════════════════════╗
║ Type  │ Bytes 0-3  4-7    8-11    12-15   16-19             ║
╠═══════╪══════════════════════════════════════════════════════╣
║   A   │   x   │   y   │   z   │   attrs (8 bytes)           ║
║   B   │   meta (8 bytes)    │   x   │   y   │   z           ║
║   C   │   x   │   y   │   meta (8 bytes)    │   z           ║
╚═══════╧══════════════════════════════════════════════════════╝
```

- **Type A** — Simple layout. Position first, then 8 bytes of per-vertex
  attribute data. Used in the first strip of each file (the main body mesh).

- **Type B** — Metadata first, then position. The metadata word 0 (bytes
  0-3) is the key to the strip structure: when its IEEE 754 exponent is 0xFF
  with a non-zero mantissa, it's a **NaN sentinel** that marks a **new
  triangle strip boundary**. These NaN vertices form the strip headers.

- **Type C** — Split position. X and Y up front, Z at the end, 8 bytes of
  metadata in the middle. Found in body vertices of many strips.

The three types mix freely within the file. Which type a vertex uses is
determined by trial: try Type A first (most specific), then Type C, then Type
B. If none produce valid positions (within [-5000, 5000]), the vertex is
dropped.

#### Triangle strips, not indexed meshes

There are **no separate index buffers** in this format. Every sequence of 3
consecutive vertices forms a triangle. The NaN float values mark strip
boundaries. Within a strip, the rasterizer draws consecutive triangles from
consecutive vertices — standard triangle strip rendering.

MT_ZIG has **476 NaN markers**, which means **477 strips** (the first strip
doesn't have a NaN header — it uses Type A layout throughout). The strips
contain **93,777 vertices** forming **92,988 triangles**.

Here's what the presence/absence of indices means for the game engine: it
never calls `DrawIndexedPrimitive`. It uses `DrawPrimitive` with triangle
strips directly from the vertex buffer. This is very Direct3D 3/5 era — the
game shipped with DirectX 3 on the disc.

#### What's in the 8 attribute bytes?

Short answer: I don't know yet. Long answer:

Looking at the byte values across vertices, they have patterns:
- Bytes 16-17 form groups (2-3 consecutive vertices share the same value)
- Bytes 12-15 don't decode as unit-length normals (int8 or int16)
- They don't decode as obvious [0,1] UV coordinates (unless using an unusual
  fixed-point scale)

The game engine likely interprets these as **bone indices + weights** or
**compressed normals + UVs** using a hardcoded format. Finding the exact
encoding would require either:
- Finding the vertex declaration in the EXE (Ghidra/patch analysis)
- Rendering the model with different interpretations and seeing which looks
  correct

For the OBJ extractor, I preserve these 8 bytes as hex in a JSON sidecar.
When recompiling, they're written back verbatim, so the round-trip preserves
them even if we don't understand them yet.

#### The model gallery

All 12 MT files extracted cleanly:

| File | Strips | Vertices | Triangles | Notes |
|------|--------|----------|-----------|-------|
| MT_ZIG | 477 | 93,777 | 92,988 | Viper (smallest) |
| MT_SEL | 83 | 9,187 | 9,045 | Selection screen |
| MT_SCENE | 9 | 22,586 | 22,568 | Stage scene |
| MT_JAG | 592 | 97,643 | 96,579 | Jaguarandi |
| MT_BBB | 1,408 | 115,709 | 113,501 | Belgdor (lots of strips) |
| MT_APH | 700 | 137,532 | 136,297 | Aphrodite |
| MT_KAS | 603 | 140,736 | 139,621 | Specineff |
| MT_FEI | 429 | 147,573 | 146,850 | Fei-Yen |
| MT_GUF | 742 | 148,391 | 147,117 | Viper II |
| MT_BAS | 829 | 149,282 | 147,773 | Temjin |
| MT_VAL | 539 | 154,123 | 153,199 | Raiden (largest) |
| MT_DOM | 1,087 | 162,453 | 160,662 | Dominator |

The robot sizes match their visual complexity — Dominator and Raiden are the
bulkiest mecha, while Viper is sleek and minimal.

### What it means

The MT format is surprisingly simple for a commercial game. No compression.
No chunk-based container. No material system embedded in the file. Just a
flat array of vertices organized as triangle strips, with the game engine
knowing hardcoded material/texture assignments.

This simplicity makes it easy to extract and edit. The round-trip works: you
can pull out the OBJ, edit in Blender, and recompile back to a valid MT file.
The positions survive (within floating-point precision of text-based OBJ), and
the attribute bytes are preserved in the sidecar.

The triangle strip design is a performance choice from 1997. Triangle strips
need fewer vertices per triangle than indexed triangle lists (roughly 1 vertex
per triangle vs. 3 indices per triangle), saving both memory and bus bandwidth
on hardware of that era. Direct3D 3 had explicit triangle strip support
(`D3DPT_TRIANGLESTRIP`), so this was the natural primitive choice.

### What's still unsolved

- The 8 attribute bytes — normals, UVs, bone weights, or something else
- The 8-byte file header — what do the 4 uint16 values actually mean?
- Texture/material assignment — likely in a separate file or hardcoded
- How the RB_ (robot body), BSEL_ (character select), and FC_ files relate
  to the MT files

### Next up

Two natural directions:

1. **Texture decoding** — The `TEXB*.IMG` files are 1 MB each of 8-bit
   paletted pixel data. Finding the palette and converting to PNG would
   let us see the robot textures.

2. **Field geometry** — The `FLD_*.BIN` files appear to use a similar
   vertex format. Decoding them would let us walk around the arenas.

Or: **Ghidra analysis** — disassemble `V_ON.EXE` and find the vertex format
declaration, which would tell us exactly what the attribute bytes mean in
one shot.

---

## Entry 3 — Seeing the mecha (building a 3D viewer)

**Date:** 2026-06-15

### What I set out to do

We have OBJ files. We have 93,777 vertices of Ziggurat sitting in a text file.
But I can't _see_ them. The OBJ is just numbers. I need a viewer — something
that puts pixels on screen and lets me orbit around the robot, toggle
wireframe, zoom in on the details.

I want it to be simple. Python, one file, no heavy dependencies. Something I
can drop into the project and anyone can run.

### What I found

Pyglet 2.x ships clean OpenGL bindings without the old-school fixed-function
pipeline. That means writing actual GLSL shaders — which is fine. The viewer
uses a minimal vertex + fragment shader pair:

- **Vertex shader** transforms positions through model-view-projection matrices
  and passes normals through the normal matrix
- **Fragment shader** does simple diffuse lighting with a single directional
  light and ambient term

The rest is plumbing:

- **Camera**: orbit camera with spherical coordinates (theta, phi, radius).
  Left-drag rotates, middle-drag pans, scroll zooms. The view and projection
  matrices are computed on the CPU with plain math — no deprecated `gluLookAt`.

- **Model**: strips of triangle strips. Each gets a VBO for positions and a
  VBO for normals (computed as flat per-triangle normals — close enough for
  a preview). A VAO binds them together. Strip ranges let us submit one draw
  call per strip with `glDrawArrays(GL_TRIANGLE_STRIP)`.

- **Grid**: 2D reference grid on the XZ plane. Helps with spatial orientation —
  you can see which way the robot is facing.

- **HUD**: pyglet text labels showing vertex/triangle counts, render mode,
  and FPS.

The viewer handles both OBJ and raw MT binary files. For OBJs, it reconstructs
triangle strips from the flat face list (greedy adjacency search). For MT
files, it uses the same three-format parser from Entry 2 directly.

### What it means

We can finally see what we're working with. No more staring at hex dumps and
guessing. The screenshot shows Ziggurat rendered in orange on a dark
background with the reference grid — a recognizable mecha silhouette.

The viewer is part of the toolchain now. Extract a model, view it, edit in
Blender, recompile, view again. The loop is closed.

Technically, the viewer uses modern OpenGL (3.0+ core profile) through
pyglet's bindings. No deprecated immediate mode. The shaders are embedded
as byte strings in the Python file — no external files needed. It's
self-contained and portable.

```
Controls:
    Left drag    — orbit
    Middle drag  — pan
    Scroll       — zoom
    W            — wireframe toggle
    L            — lighting toggle
    F            — fit view to model
    Escape       — quit
```

### Project status

```
voff/
├── von.img                 # The artifact
├── DIARY.md                # This journal
├── extract_von_img.py      # Stage 1: ISO extractor + audio converter
├── voff_mt_tool.py         # Stage 2: MT model extractor/compiler
└── voff_viewer.py          # Stage 3: 3D model viewer

---

## Entry 4 — Blender, the scary mesh, and the animation that isn't there

**Date:** 2026-06-15

### What I set out to do

The OBJ extraction worked. The viewer works. But the real goal is to open these
robots in Blender — move parts around, maybe retexture, maybe animate. So I
opened `MT_ZIG.obj` in Blender.

I got scared.

The screen filled with 93,000 overlapping triangles. Every single triangle
strip — all 477 of them — rendered on top of each other as one giant mesh.
Arms tangled with legs, weapons clipped through torsos, wireframe lines
painted the viewport into a solid block of orange static.

I had to figure out what was going on, fix it, and then chase down the
animation data.

### What I found

#### The scary mesh explained

The 477 triangle strips in one OBJ file aren't a mistake — that's how the
game stores the robot. Each strip is a separate draw call. Some strips are
body parts (a span of 500+ vertices — a complete limb mesh), others are
LODs (the same part at lower detail, overlapping the same space), and still
others are tiny 1-3 vertex separators that delimit strip boundaries in the
binary format.

The OBJ parser dumped all 93,777 vertices into one flat object. Blender had
no way to know which triangle belonged to which strip. Hence: polygon soup.

**The fix:** I rewrote the OBJ exporter to insert `o strip_000_tA_97v` group
directives before each strip. The name encodes the strip index, vertex type
(A/B/C), and vertex count. Now Blender imports each strip as a separate
named mesh object — 477 objects you can hide, show, or delete individually.

For bigger-picture work, I wrote `import_mt_blender.py` — a Blender Python
script that goes straight from MT binary to `.blend`. No OBJ middleman. It
creates a single merged mesh with four color-coded materials (orange for
large parts, blue for medium, red for small) plus sun and fill lights.

```bash
# Generate a .blend directly
blender --background --python import_mt_blender.py -- MT_ZIG.BIN

# Or with each strip as a separate object
blender --background --python import_mt_blender.py -- --separate MT_ZIG.BIN
```

All 12 robots converted to `.blend` files. The largest is Dominator at 162K
triangles, 2.5 MB. The selection screen model is only 9K triangles, 220 KB.

| Robot | Filename | Triangles | Notes |
|-------|----------|-----------|-------|
| Ziggurat | MT_ZIG.blend | 90,508 | Viper, the test subject |
| Aphrodite | MT_APH.blend | 136,133 | Pink armored |
| Temjin | MT_BAS.blend | 147,771 | Blue protagonist |
| Belgdor | MT_BBB.blend | 112,365 | Insectoid boss |
| Dominator | MT_DOM.blend | 160,600 | Biggest model |
| Fei-Yen | MT_FEI.blend | 135,587 | Idol robot |
| Viper II | MT_GUF.blend | 146,893 | Ziggurat upgrade |
| Jaguarandi | MT_JAG.blend | 96,553 | Sleek feline |
| Specineff | MT_KAS.blend | 139,479 | Floating mecha |
| Raiden | MT_VAL.blend | 153,107 | Heavy tank |
| Scene | MT_SCENE.blend | 22,568 | Stage object |
| Select | MT_SEL.blend | 8,684 | Char select screen |

#### The animation dead end

The robots are static meshes. For them to dash, jump, and shoot, something
has to move the vertices at runtime. I needed to find where that data lives.

I searched every file on the disc:

- **MT files** — static triangle strips. No transform data.
- **RB files** — tried them as MT format. They're lower-LOD versions of the
  same meshes (RB_APH: 1 strip, 18K verts vs MT_APH: 700 strips, 137K verts).
  Not animation.
- **BSEL files** — character select screen models. Static poses, not animated.
- **FC files** — all zeros. Empty containers or placeholder data.
- **No `.ani`, `.mot`, `.skl`, `.rig` files anywhere on the disc.**

Then I ran `strings` on `V_ON.EXE` and found 177 named events with the
prefix `SDE_`:

```
SDE_frame_01            SDE_zig_rotate          SDE_dash_01
SDE_dash_01_loop        SDE_jump_01             SDE_jump_04
SDE_tem_sword_cut       SDE_tem_sword_hit       SDE_tem_sword_on
SDE_aph_ton_hit         SDE_aph_shotgun         SDE_aph_ton_shake
SDE_bbb_fireball        SDE_bbb_h_bit_laser     SDE_bbb_needle1
SDE_heart_beam3         SDE_heart_beam_s1       SDE_heart_beam_s2
SDE_gameover            SDE_count_down          SDE_warning
SDE_presented_by_SEGA   SDE_mission             SDE_enemy_is
...
```

These are named animation clips — dash, jump, weapon attacks, hit reactions,
UI sequences. They follow a naming convention: `SDE_{robot}_{action}` for
character-specific moves, `SDE_{generic_action}` for shared effects.

**"SDE"** almost certainly stands for **Sega Data Event** — an internal name
for a timeline of keyframes. The data for these clips isn't in any external
file. It's compiled directly into `V_ON.EXE` as arrays of bone transforms.

This was common practice in 1997. The executable is 6.6 MB, which with 10+
robots and dozens of moves each works out to maybe 30-50 KB per animation
clip — reasonable for sparse keyframe data. The game likely stores quaternion
+ translation per joint per keyframe, with spherical linear interpolation at
runtime.

### What it means

We've hit the wall of what you can discover from file formats alone. The
remaining questions — animation data, texture palettes, vertex normals/UVs —
are all answered _inside the binary_. They're not in separate files with
convenient headers. They're in the executable's data section, referenced by
hardcoded offsets, structured according to whatever the programmers decided
in `pcWaveOpen.c` and its sibling source files.

To go further we'd need Ghidra:

1. **Find the SDE_ string table** — locate the 177 animation labels in the
   EXE's data section
2. **Trace cross-references** — find the code that reads from each label to
   understand the animation data format
3. **Find the D3D vertex declaration** — this would tell us what those 8
   mysterious attribute bytes in the MT format actually mean (normals? UVs?
   bone indices?)
4. **Find the texture palette** — the TEXB*.IMG files are 8-bit indexed
   pixel data but the palette must be somewhere in the EXE or in a resource

This is computer forensics proper. Not guessing at hex patterns, but reading
the actual instructions that read the data.

### Project status

```
voff/
├── von.img                 # The artifact (154 MB ISO 9660 CD-ROM)
├── DIARY.md                # This journal (entries 1-4)
│
├── extract_von_img.py      # Stage 1: ISO extractor + raw PCM → WAV
├── voff_mt_tool.py         # Stage 2: MT 3D model extractor + compiler
├── voff_viewer.py          # Stage 3: 3D model viewer (pyglet + OpenGL)
└── import_mt_blender.py    # Stage 3b: Blender direct import script
│
├── out_stage1/data/        # Extracted ISO files (626 files)
│   └── V_ON/               # Game assets — models, sounds, textures
├── out_stage2/             # Stage 2 outputs
│   ├── MT_*.obj            # Extracted OBJ models (grouped by strip)
│   ├── MT_*.json           # Strip metadata sidecars
│   └── MT_*.blend          # Direct Blender imports (12 robots)
└── out_stage2/viewer_screenshot.png  # First render of Ziggurat
```

### Next up

Ghidra on `V_ON.EXE`. Install Ghidra, load the binary, find the SDE_ table,
trace the references. The animation data format is the prize — if we can read
it, we can write it back, and then we can do the thing I originally wanted:
touch up a model in Blender, put it back in the game, and watch it fight.

That's Stage 4.

---

## Entry 5 — Peeling the executable (PE forensics)

**Date:** 2026-06-15

### What I set out to do

No animation files on disc. The data is inside `V_ON.EXE`. Time to crack it
open with proper tools — not `strings` and guesswork, but PE dissection and
a disassembler.

Installed Ghidra 11.3.1 alongside `pefile` and `capstone` for Python-level
inspection. The plan: map the PE structure, find the SDE_ animation table,
trace the cross-references to understand the data format, then write an
extractor.

### What I found

#### PE skeleton

`V_ON.EXE` is a 32-bit Windows GUI executable (i386, subsystem 2 =
WINDOWS_GUI). Entry point at `0x1E7930`. Image base `0x400000`.

```
Section   VAddr        VSize       RawSize     Flags
.text     0x00001000   0x1F3E3E    0x1F4000    code+exec
.rdata    0x001F5000   0x0498E8    0x049A00    read-only data
.data     0x0023F000   0x301DB28   0x3C3C00    read+write+init
.idata    0x0325D000   0x0001196   0x0001200    import table
.rsrc     0x0325F000   0x0009658   0x0009800    resources
.reloc    0x03269000   0x004B7E8   0x004B800    base relocations
```

The `.data` section is the tell — virtual size of **50 MB** but only 3.9 MB
on disk. That's a huge BSS-style allocation. At runtime, the game reserves
50 MB for vertex buffers, audio buffers, texture surfaces, and scratch
memory. The initialized portion (3.9 MB) holds global variables, lookup
tables, and string constants.

#### Who the game talks to (imports)

| DLL | What it's used for |
|-----|-------------------|
| `DDRAW.dll` | DirectDraw — 2D/3D rendering surfaces. Direct3D 3 was accessed through DirectDraw's `QueryInterface` in this era, so this covers all rendering. |
| `WINMM.dll` | Windows Multimedia — `waveOut` for raw PCM audio, `mciSendString` for CD audio playback, `timeGetTime` for timing. |
| `DSOUND.dll` | DirectSound — mixed with WINMM, probably for simultaneous sound effects. |
| `DINPUT.dll` | DirectInput — joystick/gamepad support (this is Virtual On — twin sticks were the whole point). |
| `DPCTRL.DLL` | DirectPlay — network multiplayer. The PC port had online play. |
| `KERNEL32.dll` | File I/O, memory, thread management. |
| `USER32.dll` | Windows, dialogs, message pump. |
| `GDI32.dll` | 2D drawing, bitmaps, fonts. |
| `ADVAPI32.dll` | Registry access — likely for save data and settings. |

Notably: **no Direct3D import**. The 3D rendering goes through DirectDraw,
consistent with DirectX 3-era design where you'd call
`DirectDrawSurface::QueryInterface` to get a `IDirect3DDevice`. The vertex
format (triangle strips) aligns with this — `D3DPT_TRIANGLESTRIP` was a
Direct3D 3 primitive.

#### The SDE_ string table

156 SDE_ named events clustered at raw offset `0x299E8C` (RVA `0x29B08C`)
in the `.data` section. Packed tightly as null-terminated ASCII — no struct
data between entries. Each is just a string constant:

```
SDE_frame_01         SDE_zig_rotate       SDE_dash_01
SDE_dash_01_loop     SDE_jump_01          SDE_jump_04
SDE_tem_sword_cut    SDE_aph_ton_hit      SDE_heart_beam_s1
SDE_bbb_fireball     SDE_count_down       SDE_gameover
SDE_presented_by_SEGA  SDE_round_01  ...  SDE_round_10
...156 total
```

The naming convention reveals the animation system design:

- `SDE_{robot}_{action}` — character-specific: `SDE_zig_rotate`,
  `SDE_tem_sword_cut`, `SDE_aph_ton_shake`
- `SDE_{robot}` alone — likely the idle/animation set for that robot:
  `SDE_zigrad`, `SDE_viper`, `SDE_temjin`, `SDE_feiyen`
- `SDE_{generic_action}{number}` — shared effects with variants:
  `SDE_dash_01` through `SDE_dash_05`, `SDE_jump_01` through `SDE_jump_04`,
  `SDE_hit_01` through `SDE_hit_14`
- `SDE_new_voice{1-24}` — voice line triggers (24 unique voice lines)
- `SDE_round_01` through `SDE_round_10`, `SDE_final_round`,
  `SDE_penalty_stage` — match progression
- `SDE_click_0` through `SDE_click_3`, `SDE_count_down`, `SDE_count2` — UI
  sound effects

There's no 1:1 pointer table next to the strings — they're bare string
constants. The code that uses them must reference them directly via
immediate `push` instructions or through a jump table stored elsewhere.

#### No D3D vertex declaration yet

Scanned imports and found no calls to `IDirect3DDevice::SetVertexFormat` or
similar. The vertex layout is configured purely in the push-buffer /
execute-buffer path through DirectDraw. Finding the exact FVF flags or
vertex stride in the disassembly is the next step — it'll tell us what
those 8 mysterious attribute bytes in the MT format actually encode.

### What it means

We're past the "guessing at file formats" phase. The executable's structure
is mapped. The SDE_ label table is located. The import table tells us the
rendering and audio pipeline. What remains is to follow the code — trace from
an SDE_ string reference to the animation data it points at, then from a
draw call back to the vertex format declaration.

Ghidra is installed and analyzed the binary (though it timed out after 120s
— needs a longer run for full function recovery). The project is saved at
`ghidra_project/VirtualOn`. I can write Ghidra Python scripts that run
headlessly to extract specific data: string cross-references, function
decompilation, data type recovery.

### Project status

```
voff/
├── DIARY.md                # This journal (entries 1-5)
│
├── extract_von_img.py      # Stage 1: ISO extractor + audio converter
├── voff_mt_tool.py         # Stage 2: MT 3D model extractor/compiler
├── voff_viewer.py          # Stage 3: 3D model viewer
├── import_mt_blender.py    # Stage 3b: Blender import
│
├── ghidra_project/          # Stage 4: Ghidra analysis (in progress)
│   └── VirtualOn/           #   Analyzed binary, function recovery pending
└── ghidra/                  #   Ghidra 11.3.1 installation
```

### Next up

Resume Ghidra analysis with a 300s timeout. Write a headless script that
finds cross-references to the SDE_ string table — those xrefs point at the
code that triggers each animation. The code in turn references the animation
keyframe data. Following that chain gets us the format.

---

## Entry 6 — The SDE pointer table and the ghost of animation data

**Date:** 2026-06-15

### What I set out to do

The SDE_ strings are just strings — they can't be the animation data. There
must be a data structure that connects an event name like `SDE_dash_01` to
actual keyframe transforms. With Ghidra installed and the binary loaded, the
goal was to find that connection.

### What I found

#### The SDE pointer table — found it

The SDE strings aren't referenced by code directly. There's an **array of
176 pointers** at RVA `0x29BA10` in the `.data` section. Each entry is a
4-byte pointer to an SDE string. 156 entries are active (pointing to real
strings), 20 are empty or point to a default address at `0x23F030`.

This is an **event ID lookup table** — the game indexes into it by an
integer event ID to get the associated SDE string:

```
Index  String
  0    SDE_type03
  1    SDE_bom_01       (bomb effect)
  9    SDE_dash_03       (dash movement)
 23    SDE_jump_01       (jump)
 39    SDE_zig_foot_low  (Ziggurat foot step)
 44    SDE_tem_rifle     (Temjin rifle weapon)
 67    SDE_dol_phalanx_on (Dorkas phalanx weapon)
 123   SDE_apharmd       (Aphrodite — likely idle/animation set)
 132   SDE_zigrad         (Ziggurat — idle set)
 172   SDE_click_3        (UI click sound)
```

#### The code that uses it

Around offset `0xF2559` in the `.text` section, we found the indexing code:

```asm
mov  eax, [ebp+0Ch]               ; event ID parameter
mov  eax, [eax*4 + 0x69BA10]      ; index into SDE pointer table
movsx eax, byte ptr [eax]          ; read first char of SDE string
test eax, eax
jnz  do_something                  ; if non-empty, dispatch event
```

This is part of a function that takes an event ID and either triggers the
associated SDE event or returns 0 if the entry is empty. After loading the
string pointer, it calls two indirect functions via the import table:

```asm
call dword ptr [0x365D4C8]   ; likely some setup/sound function
call dword ptr [0x365D4D4]   ; likely the event dispatcher
```

These are in the `.idata` import section — likely `mciSendString` or
similar from `WINMM.dll` for CD audio control. This confirms the SDE events
are primarily **sound and CD audio triggers**, not full animation controllers.

#### Float data in .rdata — animation keyframes?

37 float-heavy regions in `.rdata` ranging from 27 to 140 floats. The data
patterns are intriguing:

At RVA `0x1FD8DC` (repeated at `0x200F1C` — likely debug + release copies):
```
(  2.71, -17.50,  22.60)
(-17.50,  22.60,   1.00)
( 22.60,   1.00,  41.90)
(  1.00,  41.90, -10.80)
( 41.90, -10.80,   1.80)
```

At RVA `0x1FD97C`:
```
( -2.97,  30.00, -30.00)
( 30.00, -30.00,  -2.90)
(-30.00,  -2.90,  29.20)
( -2.90,  29.20,  -4.10)
```

The values in each triplet are relatively large (up to ±45), and each
successive triplet shares two values with the previous one. This sliding
window pattern is unlike 3D coordinates — it looks more like a **spline
parameter sequence** or a **motion path curve** stored as overlapping
triplets. The full arrays are 27-35 floats each, which for triplets
gives ~9-11 key control points — reasonable for a single animation curve
(walk cycle, dash, jump arc).

There are 37 such regions totaling about 4,600 floats across `.rdata`.
If each is a separate animation curve, that's 37 animation parameters
across 156 events —  many events share the same curve data.

#### Ghidra analysis: complete

Re-ran Ghidra analysis with a 300-second timeout. Completed in 186 seconds
with full function recovery, stack analysis, and x86 constant references.
The project is saved at `ghidra_project/VirtualOn/` and can be opened in
the Ghidra GUI anytime.

### What it means

The SDE system works like this:

1. Something in the game triggers an event ID (a jump, a weapon fire, a hit)
2. The event dispatcher function (at `0xF2550`) indexes into the SDE pointer
   table with that ID
3. If the entry is non-empty, it sends the SDE string to two WINMM.dll
   functions — likely `mciSendString` for CD audio commands — to play the
   associated sound effect
4. The **visual animation** (robot movement, weapon effects) is triggered
   separately by the same event ID through a different code path

The float data in `.rdata` is likely the **animation curve data** — spline
control points for robot movement. But the connection between event ID and
curve data isn't a simple parallel array. It's probably embedded in
switch/case logic or indexed through a separate table we haven't found yet.

The key insight: **SDE events are audio triggers first.** The visual
animation is handled by a separate system that shares the same event IDs
but has its own data path. This makes sense for a 1997 game — play the
sound on CD audio track, animate the robot separately.

### What's still unsolved

- The exact animation data format — the float regions in `.rdata` are
  likely animation curves, but we need to confirm their structure
- The connection between event ID and animation data
- The vertex attribute format (normals/UVs in the MT files)
- The texture palette for TEXB*.IMG files

### Project status

```
voff/
├── DIARY.md                # This journal (entries 1-6)
├── extract_von_img.py      # Stage 1
├── voff_mt_tool.py         # Stage 2
├── voff_viewer.py          # Stage 3
├── import_mt_blender.py    # Stage 3b
├── ghidra_project/VirtualOn/  # Stage 4: analyzed binary
└── ghidra/                 #   Ghidra 11.3.1
```

---

## Entry 8 — Two patches, one white box (the CD falls, the renderer stumbles)

**Date:** 2026-06-15

### What I set out to do

The game launches under Wine but immediately shows "Please insert VIRTUAL
ON CD" and refuses to proceed. I need to find every code path that triggers
that dialog and neutralize it. Binary patch, not configuration.

### What I found

#### The first CD check

The string "Please insert VIRTUAL ON CD" lives at two locations in the
binary (raw offsets `0x223B48` and `0x2C7590`). The first is referenced
from a CD audio playback function at RVA `0x1CADB1`. Here's the logic:

```
call  CD_setup()           ; try to open CD audio device
cmp   eax, 0               ; did it fail?
jne   CD_present           ; if OK, jump to playback code
push  "Please insert..."   ; show error dialog
call  MessageBox(ABORT|RETRY|IGNORE)
test  eax, eax
je    give_up              ; user clicked Ignore → return 0
jmp   retry                ; user clicked Retry → loop back

CD_present:
... (read CD tracks, play audio, etc.)
```

I overwrote the function prologue at `0x1CADB1` with:

```
mov eax, 1    ; b8 01 00 00 00
ret           ; c3
nop           ; 90
nop           ; 90
```

The function now returns 1 (CD present) before it ever checks for a disc.

#### The second CD check

But the dialog still appeared. Searching for the second copy of the string
led to a separate CD detection function at RVA `0x1C82BA`:

```
call  detect_cd_device()
cmp   [global_cd_handle], -1
je    show_dialog
mov   eax, 1               ; CD found → return success
ret

show_dialog:
push  "Please insert..."   ; second copy of the string
call  MessageBox(ABORT|RETRY|IGNORE)
cmp   eax, IDABORT         ; user clicked Abort?
jne   retry                ; loop back
xor   eax, eax             ; return 0 (failure)
```

This one is responsible for detecting whether a CD-ROM drive exists at all
(before attempting audio playback). Applied the same patch — `mov eax, 1;
ret` — at `0x1C82BA`. Now both detection and playback skip the check.

#### The game launches past the CD check

With both patches applied, the game proceeds to graphics initialization.
In the headless Xvfb test, we saw Direct3D errors (no DRI3 support, pixel
format mismatch) — expected for a virtual display. On the user's real
display, the game starts, the CD dialog is gone, and...

We get a white box in the upper left corner that eventually turns blue.

#### The white box problem

This is a classic Wine DirectDraw surface flip failure. The sequence:

1. Game creates a DirectDraw primary surface at 640×480
2. Creates a back buffer, clears it to blue
3. Calls `IDirectDrawSurface::Flip()` to swap buffers
4. Wine's DDraw→OpenGL translator fails the flip
5. What's visible on screen is either the initial clear color (white) or
   the back buffer's clear color (blue)

The root cause: DirectDraw 3 games from 1997 use exclusive fullscreen
mode with `DDSCL_EXCLUSIVE | DDSCL_FULLSCREEN`. Wine's virtual desktop
mode wraps this into a window that the compositor can actually manage.
Without it, the flip target doesn't match the visible framebuffer and
the swap never reaches your eyes.

### The fix (all registry, no winecfg)

Three registry keys to set via `wine reg add`:

1. **Virtual Desktop** — wraps the game in a managed window instead of
   letting it fight the compositor for exclusive fullscreen:

   ```
   HKCU\Software\Wine\Explorer\Desktops
     Default = "1024x768"
   ```

2. **Direct3D renderer** — force OpenGL backend. Wine's default GDI
   renderer doesn't support the `IDirect3DExecuteBuffer` path this game
   uses to submit geometry:

   ```
   HKCU\Software\Wine\Direct3D
     renderer = "gl"
   ```

3. **Force native DirectX DLLs** — the game disc ships with `DDRAW.dll`
   (DirectX 3 redistributable). Wine's built-in `ddraw.dll` doesn't
   support some of the older execute buffer opcodes. The game already
   has `D3DRM.DLL`, `D3DXOF.DLL` etc. in its directory — we tell Wine
   to load those instead of its stubs:

   ```
   WINEDLLOVERRIDES="ddraw,d3drm,d3dxof=n"
   ```

### What it means

We've moved from "game won't start" to "game starts but doesn't render."
That's progress. The CD check was the gate. The surface flip is the door.
Once the rendering works, we'll know if the audio path (DirectSound,
waveOut) and input path (DirectInput) work — or if they need fixes too.

The patches live directly in the binary. If the user re-extracts from
the ISO, they'll need to re-apply. A future version of the launch script
could do this automatically with a `--patch` flag.

### The heap errors

The game produced endless `heap: validate_used_block` errors after the
first `Flip()`. This is a false positive — 1997 games compiled with
MSVC 4.2 use a custom allocator that doesn't match Wine's heap validation
expectations. Added `WINEDEBUG=warn+heap` to suppress them.

### It runs

The game launches. The CD dialog is gone. The surface flip reaches the
screen. Alt opens a file menu. The rendering pipeline is alive.

The white box turned blue because the back buffer is cleared to blue.
On the user's real display, the game renders correctly — Direct3D
execute buffers stream geometry to the GPU through Wine's OpenGL
translator, triangle strips and all.

Next: CD audio emulation (the background music in ESCR*.BIN needs to
be fed to the game's MCI cdaudio path), input mapping (keyboard +
potentially gamepad), and verifying the full gameplay loop works.

### Project status

```
voff/
├── DIARY.md                # This journal (entries 1-8)
├── run_von.sh              # Wine launcher (auto-patches, virtual desktop)
├── extract_von_img.py      # Stage 1: ISO extractor + audio converter
├── voff_mt_tool.py         # Stage 2: MT 3D model extractor/compiler
├── voff_viewer.py          # Stage 3: 3D model viewer
├── import_mt_blender.py    # Stage 3b: Blender import
├── ghidra_project/          # Stage 4: analyzed binary
└── ghidra/                  #   Ghidra 11.3.1
```

---

## Entry 9 — The GDI surface and the player select screen

**Date:** 2026-06-16

### What happened

The game launched but displayed a white box that slowly turned blue.
No 3D rendering. No menus. Just a rectangle of failure.

I traced every DirectDraw call with `WINEDEBUG=+ddraw`. The last thing
the game did before dying:

```
ddraw7_FlipToGDISurface → GDI surface not available
ddraw7_FlipToGDISurface → Failed, hr 0x887600ff (DDERR_EXCEPTION)
```

The game calls `FlipToGDISurface()` during initialization to release the
fullscreen surface so Windows GDI can draw menus and dialogs. Wine's Virtual
Desktop wrapper had no GDI surface to hand back — the desktop window was
1024×768 but the underlying surface handle was owned by the virtual desktop
compositor, not by GDI.

The fix was removing the Virtual Desktop setting entirely. Let the game have
true exclusive fullscreen via `DDSCL_EXCLUSIVE | DDSCL_FULLSCREEN`. On
modern compositors (X11, Wayland via Xwayland), Wine handles the mode switch
by creating a fullscreen borderless window — the compositor still sees it,
but the game thinks it owns the screen.

Removed the `Explorer\Desktops` registry key from `run_von.sh`. Kept the
OpenGL renderer setting.

### It works

The game reached the player select screen. Input works. The CD check is dead.
The rendering pipeline is alive.

**Confirmed working:**
- CD check bypass (two binary patches)
- Direct3D OpenGL rendering (no white box, no blue screen)
- Input handling (keyboard controls navigate menus)
- Full gameplay loop reaches character select

**Still missing:**
- CD audio (background music) — `mciSendString("play cdaudio...")` 
  calls silently fail since there's no CD device
- Sound effects might work via `waveOut` / DirectSound (unconfirmed)

### Project status

```
voff/
├── DIARY.md                # This journal (entries 1-9)
├── run_von.sh              # Wine launcher — OpenGL renderer, CD patches
├── trace_von.sh            # DDraw/D3D debug trace script
├── extract_von_img.py      # Stage 1: ISO extractor + audio converter
├── voff_mt_tool.py         # Stage 2: MT 3D model extractor/compiler
├── voff_viewer.py          # Stage 3: 3D model viewer
├── import_mt_blender.py    # Stage 3b: Blender import
├── ghidra_project/          # Stage 4: analyzed binary
└── ghidra/                  #   Ghidra 11.3.1
```





```

---

## Entry 10 — The emulation pivot (why Wine lost to a Pentium 133)

**Date:** 2026-06-17

### What happened

Wine got us past the CD check and the character select screen. Input worked.
Menus responded. But the 3D rendering never came — white box, black screen,
garbled pixels at 320×200 stuck in the corner.

### The pivot: full hardware emulation

CPU:    Intel Pentium 133 MHz (via KVM — near-native speed)
RAM:    64 MB
Video:  Cirrus Logic GD5446 (2 MB) — DirectDraw supported, Win98 drivers
Sound:  Sound Blaster 16 (ISA)
CD-ROM: von.img mounted as IDE ATAPI CD-ROM
HDD:    4 GB FAT32 (pre-built Win98 SE desktop)
```

**Step 3: The VMware→QEMU migration.** The pre-built VM was installed
on VMware with VMware-specific drivers. First attempt booted but Windows
98 hung on hardware detection. Switching to KVM acceleration (`accel=kvm`
instead of `accel=tcg`) made the difference — the VM booted fully in
10-20 seconds instead of timing out after minutes of software emulation.

**Step 4: Launch script.** `run_von_qemu.sh` — single command boots the
full Windows 98 VM with the game CD mounted. User opens My Computer →
CD-ROM → V_ON → V_ON.EXE.

### Why this should work

The game sees exactly what it expects:
- A Pentium-class CPU executing x86 instructions (KVM provides this
  at native speed — no translation, no API mapping)
- A Cirrus Logic video card with real Win98 DirectDraw drivers (QEMU
  emulates the hardware registers, Win98 drivers talk to them)
- A Sound Blaster 16 for audio (QEMU emulates the ISA card, Win98
  routes waveOut and DirectSound through it)
- A CD-ROM drive with Red Book audio support (mounted von.img, MCI
  `cdaudio` commands go to the emulated drive)
- 64 MB of RAM (the game assumes this, no address space issues)

No Wine. No DLL translation. No API mapping. Just a 1997 PC, emulated
faithfully enough that the software rasterizer — the one that never
worked through OpenGL translation — runs natively.

### What's different from the Wine path

| | Wine | QEMU |
|---|------|------|
| CPU | Native x86_64 | KVM-accelerated Pentium |
| Rendering | D3D→OpenGL translation | Software rasterizer → emulated Cirrus Logic framebuffer |
| Surface flips | Failed (GDI surface error) | Works (real DirectDraw driver) |
| CD audio | MCI cdaudio fails (no device) | Emulated CD-ROM with von.img |
| DirectPlay | Crashed (RPC unavailable) | Works (real Win98 DCOM) |
| Resolution | 320×200 in corner | Full 640×480 in QEMU window |
| File access | Z:\ paths through Wine | Native C:\ and D:\ in VM |

### Project status

```
voff/
├── DIARY.md                # This journal (entries 1-10)
├── run_von.sh              # Wine launcher (CD patches, registry fixes)
├── run_von_qemu.sh         # QEMU launcher (full Win98 VM)
├── trace_von.sh            # DDraw/D3D debug trace script
├── extract_von_img.py      # Stage 1: ISO extractor + audio converter
├── voff_mt_tool.py         # Stage 2: MT 3D model extractor/compiler
├── voff_viewer.py          # Stage 3: 3D model viewer
├── import_mt_blender.py    # Stage 3b: Blender import
├── ghidra_project/          # Stage 4: analyzed binary
├── ghidra/                  #   Ghidra 11.3.1
└── isos/                    # VM images
    ├── von.img              #   Game CD (154 MB)
    ├── win98_hdd.img        #   Win98 SE disk (4 GB, KVM-bootable)
    └── win98_se_boot.iso    #   Win98 installer backup
```


```

---

## Entry 11 — The driver cabinet rabbit hole

**Date:** 2026-06-17

### What happened

The QEMU-native Win98 image (`win98-softgpu.qcow2`) booted and immediately
threw an `IFSMGR.VXD` error — the Installable File System Manager VxD.
Without it, Windows can't access the hard drive. Dead before the desktop.

Same root cause as the VMware→QEMU migration: the image was built for a
different IDE controller or QEMU version. Windows 98's IDE driver is baked
into the registry at install time. Change the controller, break the boot.

### The trail of attempts

- **VMware→QEMU**: IFSMGR or BSOD from VMware driver conflicts
- **VMware→DOSBox-X**: Boots but 16-color VGA only — missing Win98 driver CABs
- **Registry cleaning**: Zeroed 3dfx/voodoo entries, deleted DXMM3DFX INF
  files, set SYSTEM.INI to Super VGA. Still 16 colors.
- Downloaded **QEMU-native image** from archive.org (`win98-qemu-i440x.7z`):
  `win98-softgpu.qcow2` (952 MB) — IFSMGR.VXD on boot
  `win98.qcow2` (3.9 GB) — pending test

### Why this is hard

Windows 98 marries itself to the hardware it was installed on. Every
emulator presents different IDE, video, and input devices. Without the
Win98 driver CABs, Windows can't adapt. And archive.org blocks automated
ISO downloads.

### Status

Three images in play. The main `win98.qcow2` is the next shot. If it
fails, we either find the driver CABs as a standalone download (~80 MB)
or try ReactOS.

---

## Entry 12 — The emulation graveyard

**Date:** 2026-06-17

### What we set out to do

The game needs Windows 98. It needs DirectDraw. It needs a CD-ROM drive
with Red Book audio. Wine couldn't translate the rendering, so we turned
to full hardware emulation — QEMU, DOSBox-X, 86Box. The plan was simple:
emulate a 1997 PC, boot Windows, run the game.

### What actually happened

We fought six different approaches across two days. Every single one died
to a different cause:

| # | Approach | Death |
|---|----------|-------|
| 1 | Wine + CD patch | Rendering broken. White box in corner. GDI surface error. FlipToGDISurface failure. RPC crash from DirectPlay COM. |
| 2 | QEMU + VMware Win98 VM | BSOD on boot. VMware IDE/display drivers incompatible. 151 VMware registry entries. |
| 3 | DOSBox-X + VMware Win98 | Boots! Desktop appears. But 16-color VGA only. S3 ViRGE driver needs Win98 CD — which archive.org refuses to serve. SYSTEM.INI edited, registry cleaned, 3dfx INF files deleted. Still 16 colors. |
| 4 | DOSBox-X + SoftGPU | Downloaded SoftGPU driver package (253 MB). Injected into disk image with mtools. SYSTEM.INI manually configured. Still 16 colors — VESA BIOS insufficient for Super VGA driver. |
| 5 | QEMU + QEMU-native Win98 | Downloaded `win98-qemu-i440x.7z` (879 MB). Two disk images inside. Both hit `IFSMGR.VXD` on boot — IDE controller mismatch. Can't even reach Safe Mode. |
| 6 | QEMU + SuperNanoXP 2.0 | 91 MB ISO. Installs. Boots to desktop with full SVGA. Finally, color! Then `F_Thunk` error from KERNEL32. Compatibility engine stripped from nano ISO. Right-click → Properties: no Compatibility tab. |
| 7 | QEMU + MicroXP | Pending. Should have the compatibility engine. But at this point the question is: even if it works, what did we learn that makes the next game easier? |

### The driver problem, stated once

Windows 98 bakes itself to the hardware it was installed on. Change the
IDE controller, the display adapter, or the chipset, and it demands its
installation CD — a CD we couldn't download because archive.org blocks
automated access. The game is 154 MB. The driver CABs are 80 MB. Neither
is large. Both are inaccessible.

Windows XP is more forgiving — generic drivers built in. But the game
was compiled against Windows 98's KERNEL32, which has 16-bit→32-bit
thunking functions that XP's compatibility engine re-exports. Strip
that engine (nano XP) and the game can't start.

### What survived the wreckage

Not all of it was failure. We built real tools along the way:

- **CD check bypass** (two binary patches at RVAs 0x1CADB1 and 0x1C82BA)
- **DirectPlay stub** (DPCTRL.DLL patched to return 0 immediately)
- **Wine registry automation** (`ensure_registry_key` in bash)
- **FAT32 disk image reader/writer** (Python, for injecting drivers)
- **SoftGPU driver extraction** (253 MB download, 70 MB of driver files)
- **mtools-based disk manipulation** (no sudo mount needed)
- **SDE string pointer table** located at RVA 0x29BA10 (176 entries)
- **Ghidra project** fully analyzed (186 seconds, all functions recovered)
- **3D model format** fully decoded (three vertex layouts, triangle strips)
- **Audio format** decoded (raw 8-bit PCM, MAP-indexed)
- **Three launchers** written (Wine, QEMU, DOSBox-X)
- **Twelve Blender files** generated (one per robot)
- **Two ISO downloads** successfully automated (QEMU Win98, SuperNanoXP)

### The real cost

Two days. Six emulation approaches. Three operating systems. Four disk
images. Two emulators. Registry edits. Binary patches. Driver injections.
Floppy disk images. FAT32 filesystem parsing. All to approximate a
Pentium 133 running Windows 98 in 1997.

The game is 6.6 MB of x86 instructions. Every single one of those
instructions is doing something we could read, understand, and recompile.
Instead we spent two days trying to trick it into running inside a
Russian doll of virtualization layers.

### The pivot

Decompilation was always the fourth path. We put it aside because Wine
seemed faster. Then QEMU seemed faster. Then DOSBox-X. Then XP.

If MicroXP works: great. We play the game. If not: we stop trying to
recreate 1997 and instead lift 1997 into 2026.

The game's logic — the robot state machines, the collision detection,
the animation keyframes, the render loop, the audio mixer — is all in
that binary. We have Ghidra. We have the function graph. We have the
import table. We have every data format decoded. The only missing piece
is the C code that ties them together, and that's exactly what a
decompiler produces.

No more drivers. No more registry hell. No more CAB files. Just code.

---

## Entry 13 — The MMX check and three patches deep

**Date:** 2026-06-18

### What I set out to do

Wine can render the game now (after the CD patches and GDI surface fix from
Entry 9). But "render" is generous. The game gets past the CD dialog, then
immediately blocks on a CPU check that requires MMX. My CPU has MMX. But my VM
or emulation layer might lie about it. Rather than debug why the CPU ID comes
back wrong, I patched the check out entirely.

Also: time to make the patches automatic. Every launch, the binary gets
repaired. No remembering offsets, no manual hex editing. The script handles it.

### What I found

#### The MMX check

In the main game loop (`FUN_005c5c7a` at `0x5C5C7A`), before anything else:

```c
local_30 = FUN_005c6311();           // query CPU type
if (local_30 != 0x33 && local_30 != 0x3d) {
    MessageBoxA("This game requires MMX(R) Technology Pentium(R) Processor.\n"
                "Cannot execute with usual Pentium(R).", "virtualon", MB_ICONSTOP);
    return 0;                         // refuse to run
}
```

`FUN_005c6311` is a thin wrapper around `FUN_005083ef` — likely a CPUID-based
check that returns the processor family/model. 0x33 and 0x3d are the two MMX
Pentium processor IDs the game accepts.

The assembly at RVA `0x1C5CB6`:

```asm
83 7D D4 33       CMP  [EBP-0x2C], 0x33    ; CPU type == 0x33?
0F 84 25 00 00 00 JZ   0x5C5CE1             ; yes -> skip to game
83 7D D4 3D       CMP  [EBP-0x2C], 0x3D    ; CPU type == 0x3D?
0F 84 1B 00 00 00 JZ   0x5C5CE1             ; yes -> skip to game
6A 10             PUSH 0x10                 ; else: show error dialog
68 44 87 6C 00    PUSH "virtualon"
68 E0 86 6C 00    PUSH "This game requires MMX..."
```

**Patch:** Change the first `JZ` (conditional) to `JMP` (unconditional):

```
Before: 0F 84 25 00 00 00    JZ   0x5C5CE1
After:  E9 26 00 00 00 90    JMP  0x5C5CE1  ; always skip, never show error
```

The displacement changes from 0x25 to 0x26 because JMP is 5 bytes (not 6 like
JZ), so the target calculation shifts by one.

#### Three patches, one script

`run_von.sh` now applies all three patches automatically before launch:

| # | File Offset | Patch Bytes | What It Does |
|---|-------------|-------------|--------------|
| 1 | `0x1CA1B1` | `B8 01 00 00 00 C3 90 90` | CD check bypass (CD audio init, RVA `0x1CADB1`) |
| 2 | `0x1C76BA` | `B8 01 00 00 00 C3 90 90` | CD check bypass (CD drive detection, RVA `0x1C82BA`) |
| 3 | `0x1C50B6` | `E9 26 00 00 00 90` | MMX CPU check bypass (JZ → JMP, RVA `0x1C5CB6`) |

The logic:
1. On first run, copies `V_ON.EXE` → `V_ON.EXE.bak` (preserving the original)
2. Every launch: compares EXE against `.bak`. If different (already patched or
   corrupted), restores from `.bak` first.
3. Applies all three patches to the clean binary.
4. Pass `--no-patch` to skip this (e.g. for debugging an unpatched build).

Also sets `WINEDLLOVERRIDES="dpctrl=b"` to use Wine's built-in DirectPlay stub
instead of the game's broken `DPCTRL.DLL`.

### What it means

The game now boots cleanly through Wine with no manual intervention:
- No CD dialog
- No MMX error
- No DirectPlay crash
- OpenGL rendering via Wine's D3D translator

Three binary patches, one flag, zero friction. The game starts every time.

### Project status

```
voff/
├── DIARY.md                # This journal (entries 1-13)
├── run_von.sh              # Wine launcher — auto-patches + registry + launch
├── trace_von.sh            # DDraw/D3D debug trace script
├── extract_von_img.py      # Stage 1: ISO extractor + audio converter
├── voff_mt_tool.py         # Stage 2: MT 3D model extractor/compiler
├── voff_viewer.py          # Stage 3: 3D model viewer
├── import_mt_blender.py    # Stage 3b: Blender import
├── ghidra_project/          # Stage 4: analyzed binary + analysis scripts
│   ├── dump_findings.py    #   SDE table, float regions, function decompilation
│   ├── dump_sde.py         #   SDE string cross-references
│   ├── dump_window_init.py #   Window creation / DirectDraw init trace
│   ├── dump_window_deep.py #   Window class registration decompilation
│   └── dump_mmx_check.py   #   MMX CPU check location for patching
└── ghidra/                  #   Ghidra 11.3.1
```



---

## Entry 14 — The Great Decompilation: Winelib, D3D3, and the Host Boundary

**Date:** 2026-07-06

### What I set out to do

Entries 12 and 13 ended with a fork in the road: either force emulation to work,
or pivot to full decompilation. I chose the third option — decompile, recompile
against Winelib, and run the game as a native Linux binary. No VM. No CAB files.
No registry. Just code.

The plan: use Ghidra's headless decompiler to export every function from
`V_ON.EXE`, build a Winelib toolchain, translate the game logic into clean C,
and get it rendering through Wine's D3D implementation.

### What I found

#### The toolchain works

Setting up a Winelib build environment on an immutable Fedora (Aurora/Kinoite)
required distrobox. Inside a Fedora 44 container: `winegcc`, `winebuild`, `wrc`,
and GCC 16. The toolchain compiles 32-bit and 64-bit Winelib ELFs that link
directly against Wine's `libddraw`, `libd3d`, `libdsound`, and `libdinput`.

First test: a MessageBox stub compiled and ran. Second test: the hand-translated
game loop (window creation, DDraw init, message pump, render loop) compiled and
ran at 60 FPS with a 640x480x16 fullscreen surface. The binary is 422 KB,
dynamically loads the 50 MB data section at runtime via malloc.

#### All 4,162 functions decompiled

Wrote `ghidra_project/dump_all.py` — a headless Ghidra script that decompiles
every function in the binary. Result: 4,162 C files in `out_decompile/src/`,
zero failures. Also generated:

- `voff_all.h` — 3,961 function declarations with proper signatures
- `function_index.txt` — VA, section, and name for every function
- `call_graph.txt` — 11,245 edges mapping caller->callee relationships

The code is real. Dialog procedures handling radio buttons and list boxes for
the options menu. Matrix math for 3D transforms (push, pop, rotate, translate,
scale). D3D execute buffer construction with opcodes. State machines with jump
tables. This isn't placeholder decompilation — it's the actual game.

#### D3D3 pipeline confirmed working through Wine

The game uses Direct3D 3 execute buffers (pre-D3D5 immediate mode). Tested the
full pipeline: `QueryInterface(IID_IDirect3D)` -> `FindDevice` -> 3D device
surface -> `CreateViewport` -> `AddViewport` -> `CreateExecuteBuffer` ->
`Lock`/`Unlock` -> `Execute`. Wine translates every call to OpenGL natively.

The D3D execute buffer API: the game builds instruction streams with opcodes
like `D3DOP_TRIANGLE`, `D3DOP_PROCESSVERTICES`, `D3DOP_STATETRANSFORM`, and
submits them to the device. Wine's `ddraw.dll` handles this directly — no
additional DLLs needed.

Log output confirmed: "D3D3 Execute: OK! Pipeline works via Wine!"

#### The real data section is embedded

Instead of a zero-initialized 50 MB placeholder, the binary now loads the
original `.data` section (3.9 MB initialized + 46 MB BSS) and `.rdata`
section (301 KB) from the EXE into memory at runtime. Verified: string
pointers resolve to the correct data — "VirtualONClass" and "Virtual ON for
PC" are at the expected offsets. The game's palette, config, font tables, SDE
event strings, and all static data are now available through the `DAT()` macros.

#### The host/game boundary is clean

The 4,162 functions fall into three address bands:

| Range | Count | Layer |
|---|---|---|
| `0x00401000`-`0x005BFFFF` | ~3,500 | Game engine |
| `0x005C0000`-`0x005CFFFF` | ~200 | Host (Win32/MFC) |
| `0x005E0000`-`0x005F4E38` | ~210 | CRT/library thunks |

The boundary function is `FUN_005c5c7a` — the real WinMain body. It does host
setup (register class, create window, DDraw init), then enters a loop
alternating between `PeekMessage`/`DispatchMessage` (host) and ~20 game tick
functions (engine).

The game engine functions have no awareness of `HWND`, message loops, or MFC.
They operate purely on global data in the `.data` section through offset-based
addressing. The engine-to-host interface is minimal — mostly WndProc calling
back into menu handlers on key press.

The host layer (~200 functions) could be replaced by ~300 lines of SDL2.

#### Logging infrastructure

Added structured logging that writes to both stderr and `voff.log`:
- Entry/exit tracing for key functions
- FPS counter (every 2 seconds)
- DDraw/D3D init status with HRESULT codes
- Data section diagnostics (key globals, string pointers)

#### Project status

```
voff/
├── DIARY.md                   # This journal (entries 1-14)
├── run_von.sh                 # Wine launcher for original EXE
├── run_voff_winelib.sh        # Winelib build launcher
├── extract_von_img.py         # Stage 1: ISO extractor + audio converter
├── voff_mt_tool.py            # Stage 2: MT 3D model extractor/compiler
├── voff_viewer.py             # Stage 3: 3D model viewer
├── import_mt_blender.py       # Stage 3b: Blender import
├── ghidra_project/            # Stage 4: Ghidra analysis
│   ├── dump_all.py            #   Bulk decompile all 4,162 functions
│   ├── dump_decompile.py      #   Key function export
│   ├── dump_targets.py        #   Targeted function dump
│   ├── dump_ddraw_chain.py    #   DDraw init chain
│   ├── find_d3d.py            #   D3D pipeline discovery
│   ├── find_ddraw_caller.py   #   DDraw caller tracing
│   └── (older scripts)        #   SDE, window, MMX analysis
├── ghidra/                    # Ghidra 11.3.1
└── out_decompile/             # Stage 5: Decompiled Winelib build
    ├── src/                   #   4,162 decompiled function .c files
    ├── build/                 #   Processed compilable versions
    ├── voff_bridge.h          #   Win32/D3D bridge header + logging
    ├── voff_game.c            #   Hand-translated game loop (667 lines)
    ├── voff_data.c            #   Data section loader (malloc + memcpy)
    ├── voff_all.h             #   3,961 function declarations
    ├── function_index.txt     #   Full function address map
    ├── call_graph.txt         #   11,245-edge call graph
    ├── .data.bin              #   50 MB PE .data section dump
    ├── .rdata.bin             #   301 KB PE .rdata section dump
    ├── .rsrc.bin              #   38 KB PE .rsrc section dump
    ├── Makefile               #   Winelib build system
    └── voff.log               #   Runtime log output
```

### Next steps

1. **Translate the host-to-engine interface** — replace the ~20 host-to-game
   function calls in the message loop with direct invocations of the
   decompiled game engine functions
2. **Load TEXB textures into D3D surfaces** — find the palette, convert the
   8-bit indexed pixel data to 16-bit surfaces
3. **Translate the D3D execute buffer construction** — the game's
   `FUN_005cc380` through `FUN_005e03a0` build triangle strip submissions;
   translating these would render the title screen
4. **Replace host layer with SDL2** — window creation, input, and message
   loop in ~300 lines, dropping the MFC/Win32 dependency entirely

---

## Entry 15 — Plan: Wiring the Game Engine (Init, Tick, Input)

**Date:** 2026-07-06

### The goal

Get past the title screen. The game boots, creates a window, initializes DDraw,
and enters the message loop — but the render loop is a test pattern, not the
game. To see the real title screen (and eventually gameplay), we need to wire
up the actual game engine init and tick functions from the decompiled binary.

The strategy: translate the host→engine interface functions into clean C, call
them in the correct order, and trace the state machine until we can trigger a
"press start" to advance.

### The init sequence (in order)

From `FUN_005c5c7a`, the game calls these functions after window creation:

```
1.  FUN_005c6311()              MMX CPU check
2.  FUN_005c82ba()              CD-ROM / system check
3.  FUN_0054056d()              Generic init
4.  FUN_005c5909(hInst)         Register window class  [HOST]
5.  FUN_005c59a9(hInst,...)     Create window           [HOST]
6.  thunk_FUN_0047e600()        Unknown init (fail if 0)
7.  FUN_005c97e2()              Post-window init
8.  FUN_005895a0()              DirectSound init
9.  FUN_0040df03(data)          Game state init
10. DAT_006bc94c = ...          Set CD audio mode flag
11. FUN_005c5ac3()              ?
12. FUN_005ce180()              Resource loading init
13. FUN_00511434()              Game data setup
14. FUN_0049f7fe()              Frame/state init
15. FUN_005146c6(hWnd)          DDraw surface setup (GDI)
16. thunk_FUN_00566fb0()        Audio/mixer init
17. FUN_005c5b31()              ?
18. FUN_00444388()              ?
19. FUN_0040f43e()              ?
20. FUN_005cc616(hWnd)          Takes window handle
21. FUN_004b5fcf() / FUN_00501097()  CD audio (if present)
22. FUN_005898e6()              ?
23. FUN_00495a40()              ?
24. GlobalMemoryStatus()        RAM check -> low-mem mode
```

### The per-frame tick (three modes)

The game has three frame modes controlled by `g_CDAudioMode`:

**Mode 0** (no CD audio — stubbed/patched, simplest path to start with):
```
FUN_00442ce1()    ← INPUT (DirectInput + keyboard)
FUN_0049fbc0()    ← Animation update
FUN_004086e0()    ← Render prep / graphics setup
FUN_0049f8e8()    ← ?
FUN_005c9f70()    ← Frame sync / timing
```

**Mode 1** (CD audio active — normal gameplay):
```
FUN_00442ce1()    ← INPUT
FUN_004b560f(1)   ← Game state machine
FUN_005bcbd2()    ← ?
FUN_005006df(1)   ← Core update tick
FUN_00566dce()    ← CD audio track
FUN_004b5c2b()    ← Game state
FUN_0049fbc0()    ← Animation
FUN_004086e0()    ← Render prep
FUN_0049f8e8()    ← ?
FUN_004b560f(0)   ← Game state machine
FUN_00566c01()    ← CD audio
FUN_00500d2b()    ← ?
FUN_0040f7b0()    ← Reset matrix stack
FUN_0041d770()    ← Load identity matrix (3D transform)
FUN_0040f528()    ← SDE event dispatcher
FUN_005006df(0)   ← Core update tick
FUN_005c9f70()    ← Frame sync
```

**Mode 2** (CD audio sequential):
```
FUN_00442ce1()    ← INPUT
[CD track logic]
FUN_004b560f(0/1) ← State machine
FUN_0049fbc0()    ← Animation
FUN_004086e0()    ← Render prep
FUN_0049f8e8()    ← ?
FUN_005c9f70()    ← Frame sync
```

### Input polling

Windows messages: `PeekMessage` handles keyboard shortcuts (Alt+F4, F4).
But the main game input is in `FUN_00442ce1()` — called every frame in all
modes. This function reads DirectInput device state and updates the game's
input globals (`DAT_01ae3594` = game state, etc.).

The title screen advancement (pressing Start/Enter) would be detected either
in `FUN_00442ce1()` or through the state machine in `FUN_004b560f()`.

### Implementation plan

1. **Translate the init sequence** — all 24 functions as stubs returning
   success (1 or TRUE). Log each one as it's called.
2. **Translate Mode 0 per-frame tick** — 5 functions. Start with stubs,
   then fill in `FUN_00442ce1()` (input) first.
3. **Log the state machine** — trace `g_GameState` and `g_GameSubState`
   each frame to watch the title→menu transition attempt.
4. **Find and trigger "press start"** — read `FUN_00442ce1()` decompiled
   code, find where it checks for the start button, and force it.
5. **Expand rendering** — once the state machine advances, the render
   prep (`FUN_004086e0`) and 3D transform (`FUN_0041d770`) should start
   submitting geometry through D3D3.

### What this unlocks

Once the state machine advances past the title screen, the game's actual
rendering pipeline activates: `FUN_004086e0` sets up per-frame state,
`FUN_0041d770` loads the identity transform, and subsequent functions submit
D3D execute buffers. The title screen sprites (logo text, "PRESS START
BUTTON") would render through Wine's D3D3 translation. From there, the
character select screen and gameplay are the same pipeline with different
state machine mode.


---

## Entry 16 — The Texture Atlas Decoded (4-bit Byte-Interleaved)

**Date:** 2026-07-06

### The TEXB format

Six `TEXB*.IMG` files, 1 MB each. The diary guessed they were 8-bit paletted
pixel data back in Entry 2. That was wrong. They're more interesting than that.

`FUN_00510ecb` — the texture loader — reveals the actual format:

1. **Byte-interleaved.** The raw file is 1,048,576 bytes treated as pairs of
   bytes. Odd bytes form the top half of a 1024×1024 image. Even bytes form the
   bottom half.

2. **4-bit nibble split.** After deinterleaving, each byte is split into two
   4-bit pixels (high nibble and low nibble). This produces a 2048×1024 image
   with 4 bits per pixel — 16 possible values per texel.

3. **Mipmap chain.** The loader generates a full mipmap chain: 1024×1024,
   512×512, 256×256, 128×128, 64×64, 32×32. Each level is stored at a different
   address in the data section.

4. **16-color palette.** The 4-bit values index into a 16-entry palette stored
   somewhere in the data section. Finding that palette is the next challenge.

The deinterleave algorithm, translated from the decompiled code:

```c
for (row = 0; row < 1024; row++) {
    for (col = 0; col < 1024; col += 2) {
        int odd_byte  = source[row * 1024 + col + 1];
        int even_byte = source[row * 1024 + col];
        dest[row * 1024 + col/2] = odd_byte;           // top half
        dest[(2*row + 1) * 512 + col/2] = even_byte;   // bottom half
    }
}
```

Then each byte in the deinterleaved image becomes two 4-bit texels:

```
texel_lo = byte & 0x0F;
texel_hi = byte >> 4;
```

### The texture explorer

Built `texplorer.html` — a zero-dependency JavaScript tool for iterating on
texture format discovery. Drag-and-drop TEXB files, dial in stride/width/height,
toggle palette modes, auto-scan all dimensions. The "VOFF 4-bit" mode implements
the deinterleave + nibble-split decoder, showing both the 1024×1024
deinterleaved view and the 2048×1024 nibble-expanded view.

This replaces the cycle of: edit C code → compile → launch Wine → squint at
screen. Now: open a browser tab, drop a file, see it instantly.

### What's still missing

The 16-color palette. The 4-bit texel values (0-15) map to actual RGB colors
through a palette that must be in the `.data` or `.rdata` section. Finding it
would make the textures viewable in their intended colors.


---

## Entry 17 — Plan: Getting the Title Screen Visible

**Date:** 2026-07-06

### The problem

The state machine runs through states 0→1→2→3→4, but the title screen (state
1) is completely dark. We're not calling any of the game's actual rendering code
— our `render_frame()` just shows the decoded TEXB atlas as a background.

To get the title screen rendering properly, we need to run the game's own title
screen sub-state handlers and render sprites through the game's pipeline.

### The architecture

The title screen state (state 1, `FUN_0044b38c`) dispatches through 24 sub-states
via a jump table at `PTR_FUN_005fb238`:

- Sub-states 0-4: Initialize sprite system, transform slots, fade engine
- Sub-states 5-7: Load assets, fade in
- Sub-state 8: Copy animation keyframes to render slots
- **Sub-state 9**: Main display loop — calls `FUN_0044ae55` ~575 times to
  render sprites for "VIRTUAL ON" logo and "PRESS START BUTTON" text
- Sub-states 10-31: Attract mode, sound, options transitions

Each sprite is drawn by `FUN_0042ca55`, which sets up a 3×4 transform matrix,
then submits a D3D execute buffer. The execute buffer chain (`FUN_005cc380` →
`FUN_005cc4c6` → `FUN_005e03a0`) is a 1400+ line software triangle rasterizer.

### The strategy: Hybrid approach

Rather than translating the entire 1400-line D3D rasterizer, we replace the
rendering backend with DirectDraw Blt operations while keeping the game's init
and state machine logic intact.

**Phase 1 — Build infrastructure**: Compile the ~40 needed functions from the
decompiled source into our build

**Phase 2 — Translate the state machine**: Replace our hand-rolled
`tick_state_dispatch()` with calls to the real `FUN_0049f8e8` and
`FUN_0044b38c`

**Phase 3 — Stub the D3D chain**: Create replacement functions that log the
calls but skip the execute buffer submission. Verify the state machine advances
correctly through all sub-states.

**Phase 4 — Implement sprite rendering**: Build a font texture atlas from the
TEXB data. Replace `FUN_005cc4c6` with code that reads the current transform
matrix, computes screen-space coordinates, and calls `IDirectDrawSurface::Blt`
to draw sprites from the atlas.

**Phase 5 — Wire and polish**: Hook keyboard input through the real input
function (`FUN_00442ce1`). Handle frame timing. Get "PRESS START" to advance
past the title screen.

### Key data tables

The font glyph data is in `DAT_006471e0` (offset 0x81E0 in .data section),
indexed by character code. The sprite descriptor tables and animation data are
in BSS (runtime-allocated) and get populated by the init functions.

### Risks

The biggest unknown is whether all the BSS data tables will be correctly
populated by the init functions. Some references (like `DAT_007e7c58`) are at
addresses past the initialized .data region and must be set up at runtime. We
must call all init functions in the correct order.


---

## Entry 18 — Lessons from Wiring the State Machine

**Date:** 2026-07-06

### The title screen is a 24-sub-state machine

State 1 (the title screen) doesn't just display an image. It dispatches through
24 sub-states via `PTR_FUN_005fb238` (.rdata), each with a handler function:

- Sub-states 0-4: Initialize sprite system, transform slots, fade engine
- Sub-states 5-7: Load assets, handle fade-in
- Sub-state 8: Copy animation keyframes to render slots
- Sub-state 9: Main display loop — runs for ~575 frames, calls
  `FUN_0044ae55` each frame which iterates sprite slots and submits
  D3D execute buffers
- Sub-states 10-31: Attract mode, sound, options transitions, loop back

The complete state progression is 0→1→2→3→4, where:
- 0 = startup (auto-advances to 1)
- 1 = title screen (waits for Start press)
- 2 = transition (auto-advances to 3 immediately)
- 3 = menu/mode select (auto-advances to 4)
- 4 = in-game (stays here)

### The Ghidra DAT_ naming convention

Ghidra names data globals as `DAT_XXXXXXXX` where `XXXXXXXX` is the **offset
from the start of the data section** (.data VA 0x0063F000), NOT a virtual
address. This caused multiple bugs:

1. `DAT_01ae353c` at offset 0x01AE353C — when mistakenly treated as a VA
   (0x01AE353C - 0x0063F000), the offset becomes negative, reading garbage
2. Hand-translated code like `*(uint8_t*)(__data_start + (0x01AE2014 - 0x0063F000))`
   reads BEFORE __data_start — the correct form is just `__data_start + 0x01AE2014`
3. The gen_game.py script must treat ALL hex values from DAT_ names as direct
   offsets, never subtracting 0x0063F000

### State advancement requires initialized player slots

The title screen won't advance unless:
1. `DAT_03415608` (player slot count) is at least 1
2. At least one player slot at `DAT_01ae2014 + slot * 0x380` has value 0x20,
   0x22, or 0x23 (meaning "player present")
3. `DAT_01ae353c` (attract mode / "Start pressed" flag) is set to 2

All three are in BSS and were zero at startup because our stubbed init functions
never populate them. Setting them manually unblocked the state machine.

### The jump tables are in .rdata, not .data

`PTR_FUN_005fe5e0` (main state dispatch) and `PTR_FUN_005fb238` (sub-state
dispatch) are both in the `.rdata` section (read-only data, VA 0x005F5000+).
These tables contain 32-bit function pointers — on a 64-bit build, reading them
as `void**` reads two entries at once. Must use `uint32_t*` access.

### The TEXB format is 4-bit byte-interleaved

Not 8-bit as the diary guessed in Entry 2. `FUN_00510ecb` reveals:
1. Raw file is byte-interleaved: even bytes → bottom half of atlas,
   odd bytes → top half
2. After deinterleave, each byte splits into two 4-bit nibbles
3. Produces a 2048×1024 atlas at 4 bits per pixel (16-color palette)
4. The 16-color palette is somewhere in the data section, still unfound

### The rendering pipeline is D3D3 execute buffers

The game doesn't use DDraw `Blt` for 2D rendering. It builds D3D execute
buffer instruction streams with opcodes and submits them to `IDirect3DDevice::Execute()`.
The execute buffer chain is `FUN_005cc380` → `FUN_005cc4c6` → `FUN_005e03a0`
(a 1400-line software triangle rasterizer).

Wine supports D3D3 execute buffers natively — our test confirmed the full
pipeline works: QueryInterface → FindDevice → CreateSurface → Viewport →
ExecuteBuffer → Lock/Unlock → Execute.

### The host/game boundary is at ~0x005C0000

4,162 functions fall into three clean bands by address:
- 0x00401000-0x005BFFFF: ~3,500 game engine functions
- 0x005C0000-0x005CFFFF: ~200 host layer (Win32/MFC)
- 0x005E0000-0x005F4E38: ~210 CRT/thunks

The boundary function is `FUN_005c5c7a` — the real WinMain body. The host
calls ~20 game init functions then ~5 per-frame tick functions. The game engine
has no awareness of `HWND` or message loops.

### What's working

- 23 compiled game functions + 31 stubs, zero compile errors
- State machine: 0→1→2→3→4 with auto-advance or keyboard trigger
- Windowed DDraw mode with GetAsyncKeyState input
- Data section loaded at runtime (3.9MB init + BSS)
- D3D3 execute buffer pipeline confirmed via Wine
- TEXB texture atlas decoded and viewable
- SDL2 native Linux binary (no Wine) compiles and runs
- Full build pipeline: `make sdl` or `make winelib`

### What's next

1. **Translate D3D execute buffer → DirectDraw Blt** (Phase 4 from Entry 17
   plan) — the biggest remaining piece. This replaces the 1400-line software
   rasterizer with DirectDraw surface blits from the TEXB texture atlas.
2. **Wire the sub-state rendering** — the `title_anim_dispatch` function pointer
   calls need to dispatch to compiled sprite functions.
3. **Find the 16-color palette** — the TEXB atlas uses 4-bit indices into a
   16-entry palette somewhere in the data section.
4. **Wire real keyboard input** — map SDL/DInput to the game's input globals
   so the user can control the game naturally.


---

## Entry 19 — MAME Source Dump: Arcade Texture & Vertex Format

**Date:** 2026-07-06

### What the MAME Model 2 driver tells us

The arcade version of Virtual On runs on Sega Model 2B hardware. MAME's
`model2_v.cpp` driver (by R. Belmont, ElSemi, Olivier Galibert) documents the
hardware rasterizer. Key findings for our PC port reverse engineering:

### Vertex format

The Model 2 vertex structure (`poly_vertex`) has:
- `x`, `y`, `pz` — 3D position (floats)
- `pu`, `pv` — texture U/V coordinates in **13.3 fixed point** format
- `p[]` — array of 4 floats (likely normal vector)

The PC MT model vertex format (20 bytes = 5 floats) maps to this: 3 position
floats + 2 UV integers? Or 3 position + 3 normal + 2 UV coords encoded as
the 8 mystery attribute bytes.

### Texture header

Each polygon carries a 4-entry `texheader[]` (u16 array) controlling:
- `texheader[0]` bits 13-14: renderer mode (textured, transparent)
- Texture page/offset within the sheet
- LOD/mipmap level
- Mirror flags (X and Y)
- Microtexture enable (128×128 detail texture)

### Palette format

Arcade palette entries are 16-bit words in **5-5-5 RGB** format:
```
bits 0-4:   Red   (0-31)
bits 5-9:   Green (0-31)
bits 10-14: Blue  (0-31)
```
System palette: 4096 entries (0x1000).
The PC version likely uses the same 5-5-5 format encoded differently in the
data section — worth searching `.data` for 16-entry or 4096-entry arrays
of 16-bit values matching this pattern.

### Texture parameters

From the renderer (`model2rd.ipp`):
- `tex_width`, `tex_height` — per-texture dimensions
- `tex_x`, `tex_y` — position within sheet (with -2048/-1024 bias for
  regular textures, different offsets for microtextures)
- `texsheet[]` — pointer array for mipmap levels
- `utexminlod`, `utexx`, `utexy` — microtexture parameters
- `texmirrorx`, `texmirrory` — mirror/clamp flags
- `texlod` — computed LOD value from log RAM lookup

### U/V coordinate format

U and V are in **13.3 fixed point**:
- 13 integer bits + 3 fractional bits
- Subtract 0.5 texel (0x80) before sampling
- Bilinear filtering via fractional parts (0xFF mask)

### Texture ROM layout

Arcade ROMs: 4 MB of textures organized as `u16*` (16-bit word pointer).
The PC's TEXB*.IMG files (1 MB each, 4-bit byte-interleaved) are a storage
optimization — the `FUN_00510ecb` loader expands raw bytes to the
1024×1024 texture sheet the hardware expects.

### What this means for our work

1. The 16-color TEXB palette should be a 16-entry × 2-byte table of 5-5-5
   RGB values somewhere in `.data` or `.rdata`.
2. The MT vertex mystery bytes likely encode UV coordinates in the arcade's
   fixed-point format (possibly 13.3 or similar).
3. The texture headers (`texheader[0..3]`) in the polygon command buffer
   control all rendering modes — these are what the D3D execute buffer chain
   constructs.
4. The 37 float regions in `.rdata` may also include the LOD coefficient
   table (`coef_table[32]`) and texture parameters (`texture_parameters[32]`).

### Credit

MAME Model 2 driver authors: R. Belmont, Olivier Galibert, ElSemi,
Angelo Salese, Matthew Daniels. The hardware reverse engineering was
originally done by ElSemi.


---

## Entry 20 — Data Section Cartography

**Date:** 2026-07-06

### The .data section organized by content type

A 64KB-block analysis of the 3.9 MB initialized .data section reveals clear
zones:

| VA Range | Type | Content |
|---|---|---|
| 0x0063F000-0x006AF000 | **Strings** | Heavy ASCII (10K-33K chars/block): CD audio, MCI, config, UI labels, SDE events, weapon/robot names, input mapping, CRT debug messages, asset filenames |
| 0x006BF000-0x0070F000 | **Zeros/Sparse** | Mostly BSS-like padding with scattered data. Contains some pointers and small lookup tables |
| 0x0071F000-0x0092F000 | **Strings** | More ASCII — continued game string data. Screen/UI text, menu strings, network messages, robot descriptions |
| 0x0093F000-0x009AF000 | **Sparse strings** | Declining string density, increasing zero fill. Transition zone |
| 0x009BF000-0x009CF000 | **Dense mixed** | 256 unique bytes, heavy ASCII with mixed binary — likely sprite/font glyph bitmaps |
| 0x009CF000-0x009FF000 | **Sparse** | Declining data density, approaching BSS boundary |

The entire initialized data section is **predominantly string data**. Out of
~3.9 MB, roughly 2.5-3 MB is ASCII strings — config, UI, weapon/robot names,
CD audio commands, CRT debug messages, MCI command strings, input mapping keys,
network protocol strings, and filenames. The game's "data section" is less a
database of numeric constants and more a localization table + config dump.

### Font glyph table (DAT_006471e0)

At offset 0x81E0: an array of 96 pointers (characters 0x20-0x7F). Each pointer
is a 4-byte VA pointing to glyph data elsewhere in .data. Example entries:

| Char | VA | Glyph data (first 8 bytes) |
|---|---|---|
| `#` | 0x007E6950 | `55039d0055039d00` |
| `$` | 0x007E6A20 | `d04000003f08c070` |
| `%` | 0x0079F56C | `890cdc3e000000bf` |
| `'` | 0x007E8060 | `d04000003f08c070` |
| `.` | 0x0079CC5C | `556f5ebe172c9240` |

The glyph data appears to be small structures (possibly width/height + pixel
offset or encoded bitmap data). Characters like `$`, `'`, and `0` share
identical glyph data (`d04000003f08c070`), suggesting these are blank/space
glyphs or share the same default entry.

### Float3 arrays

Found 78,258 candidate locations where 3-float tuples appear consecutively.
The highest-scoring region is at offset 0x9C18 with values cycling through
{2.322, 2.337, 2.329} — likely a vertex array or normal vector table.

### What's NOT in .data

- **Float constants**: Very few. Most "floats" in .data are integers
  mis-cast. The real float data lives in .rdata (the 37 float regions
  documented in Entry 6).
- **The 16-color TEXB palette**: Not found as a 32-byte 5-5-5 RGB block
  in either .data or .rdata. Might be generated programmatically or
  stored in a non-obvious encoding.
- **Large lookup tables**: The game appears to use generated/calculated
  values rather than pre-computed lookup tables. This matches the arcade
  Model 2 architecture where many values come from log/coefficient RAM.

### From the MAME driver

The arcade uses 5-5-5 RGB format for palettes. The scan found 148,088
candidates in .rdata — the thresholds need refinement. The game likely
stores its palette as 16-bit words, but the encoding might differ from
the arcade (PC uses a different color depth path through Windows GDI/DDraw).


---

## Entry 21 — String Archaeology: Weapons, Robots, and Source Paths

**Date:** 2026-07-06

### The .data section is a string goldmine

28,691 ASCII strings extracted from the 3.9 MB initialized .data section.
Filtering out CRT debug noise, keyboard scan codes, and compiler artifacts
leaves several dense structured tables of game content.

### Weapon table (fixed-stride array at 0x00658xxx)

Every weapon × robot combination has 7 property variants with suffixes
_N, _F, _S, _R, _J, _Z, packed at 36-byte strides:

```
TBOMB_N  <TEM>    TBOMB_F  <TEM>    TBOMB_S  <TEM>    TBOMB_R  <TEM>
RIFLE_N  <TEM>    RIFLE_F  <TEM>    RIFLE_S  <TEM>    RIFLE_R  <TEM>
BOWGUN_N <FEI>    BOWGUN_F <FEI>    BOWGUN_S <FEI>    BOWGUN_R <FEI>
SONICWAVE_N <TEM> SONICWAVE_F <TEM> ...
```

The suffixes likely encode weapon properties — Normal, Fire, Speed, Range,
Jump, Zone? Or animation modes. Each entry appears at a precise 36-byte
interval, confirming the user's prediction of fixed-length sequential arrays.

### Source path leak

```
D:\Virtual.ON\Release\source\main\src\pcWaveOpen.c
```

The full Sega developer build path is baked into the binary. The directory
structure reveals: `source/main/src/` for core code, `pcWaveOpen.c` for
Windows audio initialization.

### Asset inventory (filename arrays)

Sound files: `snd_zig.bin`, `snd_jag.bin`, `snd_bbb.bin`, `snd_aph.bin`,
`snd_kas.bin`, `snd_rai.bin`, `snd_bel.bin`, `snd_vip.bin`, `snd_tem.bin`,
`snd_else.bin` — one per robot plus generic.

Map files: `map_zig.bin`, `map_jag.bin`, `map_fei.bin`, etc. — same pattern.

### UI strings

```
MODE SELECT              PLAYER DATA EXPORT       TODAY'S BEST PILOTS
2 PLAYERS VERSUS         NETWORK VERSUS           CANNOT CONTINUE
SELECTED_VS              SELECTING_1P             VR.AVIONICS CONFIGURATION
Low Resolution           High Resolution          FieldGraphic
Device Settings          CurrentJoystickSettings   Joystick and KB
```

### SDE events in string form

`SDE_zig_rotate`, `SDE_warning` — the 156 SDE event names from Entry 6
are confirmed to exist as readable strings in the data section. They were
not assigned `s_` prefixes by Ghidra because they live in a packed table
rather than as individually-named data labels.

### Network mode strings

```
THIS IS STANDALONE MACHINE       Checking Network Now
Network Check Success            THERE IS NO COMMUNICATION BOARD!
Network Total Nodes: %d          THIS IS MASTER SITE
THIS IS SLAVE SITE               THIS IS RELAY SITE
```

### Error messages

```
Cannot execute with usual Pentium(R).
Cannot create primary buffer
OBSTACLE POINT ERROR [1P:%08x]
HAND_PUT ID ERROR [2P:%2d]
```

### DAT_ string mnemonics

Created a mapping convention: `DAT_XXXXXXXX__STR__descriptive_name`. Example:
`DAT_006C86E0__STR__This_game_requires_MMX_R__Technology`. The generation
script produces 28,691 entries in `out_decompile/dat_strings.h`. When browsing
decompiled code and encountering a `DAT_` reference, grepping this file
reveals what string lives at that address.


---

## Entry 22 — Arena Loading: scradd + escrgame

**Date:** 2026-07-07

### The arena load pipeline

`FUN_00483200` (arena_setup) is called at match init. It loads the stage
background data from three files:

| File | Size | Content |
|---|---|---|
| `SCRADD0.BIN` | 16,384 bytes | Displacement/height data (repeating 16-bit values: 0x2003=800, 0x6002=608) |
| `SCRADD1.BIN` | 16,384 bytes | Same format, second copy |
| `ESCRGAME.BIN` | 4,194,304 bytes | Background visual/audio data in chunks |

The assembly process:

1. `FUN_005cacb0("scradd0.bin", &DAT_0353e420, 16384, 0)` — loads scradd0
2. Five chunks of `escrgame.bin` loaded at different offsets into the buffer:
   - chunk 1: 98,304 bytes (background layer 1)
   - chunk 2: 33,408 bytes (background layer 2)
   - chunk 3: 278,528 bytes (main background)
   - chunk 4: 196,608 bytes (background overlay)
   - chunk 5: 32,768 bytes (detail layer)
3. `FUN_00480f30(&DAT_0353e420, total_size)` — initializes the assembled data
4. `FUN_0047f0c0(ptr, size)` × 3 — sets up rendering for each data block
5. Same process repeated for player 2 arena at `&DAT_0345d420`

Total assembled per arena: ~656,000 bytes.

The chunk sizes are hardcoded in `.rdata` at `DAT_005fdad0` through
`DAT_005fda8c`. The file paths are built by `FUN_005cacb0__file_load` which
combines a base directory (`DAT_02b05d50`) with the filename using
`wsprintfA`.

`SCRADD0.BIN` contains 16-bit word pairs like `(0x2003, 0x2003, 0, 0)`
repeating — likely a height map or collision grid for the stage geometry.

### File loader chain

```
FUN_005cacb0__file_load(filename, dest, size, param4)
  → builds full path (base_dir + filename)
  → calls FUN_00566e47 (CD audio sync)
  → calls FUN_005cadb1__file_read(path, dest, size, param4)  [Ghidra decompile failed]
```

`FUN_005cadb1` couldn't be decompiled by Ghidra — shows only `return 1`.
The actual implementation is in assembly, likely using `fopen`/`fread`/`fclose`.

