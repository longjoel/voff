/* VOFF SDL2 Host — native Linux binary, no Wine, no Win32, no MFC
 *
 * Replaces the ~200-function host layer (0x005C0000-0x005CFFFF) and the
 * Win32 CRT layer (0x005E0000-0x005F4E38) with ~300 lines of SDL2 + OpenGL.
 *
 * The game engine (~3,500 functions at 0x00401000-0x005BFFFF) operates
 * on the original .data section, which is loaded at runtime.
 *
 * Build: gcc -o voff_sdl voff_sdl.c data_init.o rdata_init.o \
 *             -lSDL2 -lGL -lm
 */

#include <SDL2/SDL.h>
#include <GL/gl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* ================================================================
 * Logging
 * ================================================================ */
static FILE *log_fp = NULL;

#define LOG(fmt, ...) do { \
    fprintf(stderr, "[VOFF] " fmt "\n", ##__VA_ARGS__); \
    if (log_fp) { fprintf(log_fp, "[VOFF] " fmt "\n", ##__VA_ARGS__); fflush(log_fp); } \
} while(0)

/* ================================================================
 * Data section — loaded from original PE's .data and .rdata
 * ================================================================ */

/* Embedded binary blobs (generated via objcopy from .data.bin, .rdata.bin) */
extern const char _binary_data_init_bin_start[];
extern const char _binary_data_init_bin_end[];
extern const char _binary__rdata_bin_start[];
extern const char _binary__rdata_bin_end[];

/* Virtual address space matching the original PE layout */
static uint8_t *voff_data = NULL;       /* 50 MB .data section */
static uint8_t *voff_rdata = NULL;      /* 301 KB .rdata section */

/* DAT macro: access a global variable at its original VA in the data section.
 * VA = 0x00400000 (image base) + RVA
 * Offset into voff_data = VA - 0x0063F000 (.data section base)
 */
#define DAT(type, va) (*(type *)(voff_data + ((va) - 0x0063F000)))
#define RDAT(type, va) (*(type *)(voff_rdata + ((va) - 0x005F5000)))

/* Key game state globals (offsets from original binary) */
#define g_GameState      DAT(int32_t, 0x0063F000 + 0x01AE3594)
#define g_IsActive       DAT(int32_t, 0x0063F000 + 0x006BF56C)
#define g_RenderFrame    DAT(int32_t, 0x0063F000 + 0x006C84D0)
#define g_ScreenWidth    DAT(int32_t, 0x0063F000 + 0x006BF5B8)
#define g_ScreenHeight   DAT(int32_t, 0x0063F000 + 0x006BF5BC)

/* ================================================================
 * CPU detection (MMX check — original at 0x001083EF)
 * ================================================================ */
static uint32_t cpuid_check(void)
{
    int cpu_info[4];
    uint32_t family, model;

    __asm__ __volatile__(
        "cpuid"
        : "=a"(cpu_info[0]), "=b"(cpu_info[1]),
          "=c"(cpu_info[2]), "=d"(cpu_info[3])
        : "a"(1)
    );

    family = (cpu_info[0] >> 8) & 0xF;
    model  = (cpu_info[0] >> 4) & 0xF;

    if (family == 6) {
        if (model == 3)  return 0x33;
        if (model >= 5)  return 0x33;
    }
    if (family == 5) {
        if (model == 4 || model == 3) return 0x33;
        if (model >= 8)               return 0x3D;
    }
    return 0;
}

/* ================================================================
 * OpenGL renderer — simple test scene (replace with game D3D calls)
 * ================================================================ */
static void render_frame(SDL_Window *window)
{
    static int frame = 0;
    static Uint32 last_fps = 0;
    static int fps_count = 0;
    Uint32 now = SDL_GetTicks();

    frame++;
    fps_count++;

    if (now - last_fps >= 2000) {
        float fps = fps_count * 1000.0f / (float)(now - last_fps);
        LOG("FPS=%.1f (frame %d)", fps, frame);
        fps_count = 0;
        last_fps = now;
    }

    /* Clear to the game's title screen color: white */
    glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    /* Draw a test triangle */
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, 640, 480, 0, -1, 1);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    glBegin(GL_TRIANGLES);
    glColor3f(0.0f, 0.0f, 1.0f);
    glVertex2f(320, 140);
    glColor3f(0.0f, 1.0f, 0.0f);
    glVertex2f(220, 340);
    glColor3f(1.0f, 0.0f, 0.0f);
    glVertex2f(420, 340);
    glEnd();

    /* Draw the game title text (placeholder for sprite rendering) */
    /* In the real game, this would be a D3D execute buffer submission
     * rendered through the game's sprite/text engine at FUN_0042ca55 */

    SDL_GL_SwapWindow(window);
}

/* ================================================================
 * Game state machine (placeholder — will call real game engine)
 * ================================================================ */
static void game_tick(void)
{
    /* In the real game, this calls:
     *   FUN_00442ce1()  — process input
     *   FUN_004b560f()  — game state machine
     *   FUN_0049fbc0()  — animation update
     *   FUN_004086e0()  — render prep
     *   FUN_0041d770()  — 3D transform / submit
     *   FUN_005c9f70()  — frame sync
     *
     * For now: just render the placeholder scene.
     */
}

/* ================================================================
 * Keyboard input (replaces DirectInput + WndProc keyboard handling)
 * ================================================================ */
static int handle_keydown(SDL_Keysym key)
{
    switch (key.sym) {
    case SDLK_ESCAPE:
        return 1;  /* quit */
    case SDLK_RETURN:
        if (key.mod & KMOD_ALT) {
            /* Alt+Enter — toggle fullscreen (original game behavior) */
            LOG("Alt+Enter: fullscreen toggle (not yet implemented)");
        }
        break;
    case SDLK_F4:
        if (key.mod & KMOD_ALT) {
            return 1;  /* Alt+F4 — quit (original game behavior) */
        }
        break;
    case SDLK_f:
        LOG("FPS counter requested");
        break;
    default:
        break;
    }
    return 0;
}

/* ================================================================
 * Data section initialization
 * ================================================================ */
static int init_data_section(void)
{
    size_t sz;

    voff_data = (uint8_t *)calloc(1, 0x301DB28);  /* 50 MB */
    if (!voff_data) {
        fprintf(stderr, "FATAL: cannot allocate 50 MB data section\n");
        return -1;
    }

    voff_rdata = (uint8_t *)calloc(1, 0x049A00);   /* 301 KB */
    if (!voff_rdata) {
        fprintf(stderr, "FATAL: cannot allocate rdata section\n");
        free(voff_data);
        return -1;
    }

    /* Copy initialized data from embedded binaries */
    sz = _binary_data_init_bin_end - _binary_data_init_bin_start;
    memcpy(voff_data, _binary_data_init_bin_start, sz);
    LOG("Loaded %zu bytes of .data section", sz);

    sz = _binary__rdata_bin_end - _binary__rdata_bin_start;
    memcpy(voff_rdata, _binary__rdata_bin_start, sz);
    LOG("Loaded %zu bytes of .rdata section", sz);

    return 0;
}

/* ================================================================
 * Main — SDL2 host replacing WinMain + all MFC/Win32 code
 * ================================================================ */
int main(int argc, char *argv[])
{
    SDL_Window *window = NULL;
    SDL_GLContext glctx = NULL;
    uint32_t cpu_type;
    int running = 1;
    (void)argc;
    (void)argv;

    /* ---- Init ---- */
    log_fp = fopen("voff_sdl.log", "w");
    LOG("VOFF SDL2 host starting");

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) < 0) {
        LOG("SDL_Init failed: %s", SDL_GetError());
        return 1;
    }
    LOG("SDL2 initialized");

    /* CPU check (original game refuses to run without MMX) */
    cpu_type = cpuid_check();
    LOG("CPU check: type=0x%02x (%s)",
        cpu_type, cpu_type == 0x33 ? "Pentium MMX" :
                   cpu_type == 0x3D ? "K6" : "unknown");

    /* Load original data section */
    if (init_data_section() < 0) {
        SDL_Quit();
        return 1;
    }

    /* Create window (replaces RegisterClassA + CreateWindowExA) */
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 16);

    window = SDL_CreateWindow(
        "Cyber Troopers Virtual On",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        640, 480,
        SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE
    );
    if (!window) {
        LOG("SDL_CreateWindow failed: %s", SDL_GetError());
        free(voff_data);
        free(voff_rdata);
        SDL_Quit();
        return 1;
    }
    LOG("Window created: 640x480");

    glctx = SDL_GL_CreateContext(window);
    if (!glctx) {
        LOG("SDL_GL_CreateContext failed: %s", SDL_GetError());
        SDL_DestroyWindow(window);
        free(voff_data);
        free(voff_rdata);
        SDL_Quit();
        return 1;
    }
    LOG("OpenGL context created");

    /* Set up OpenGL state */
    glViewport(0, 0, 640, 480);
    glEnable(GL_DEPTH_TEST);
    LOG("OpenGL initialized");

    /* ---- Main loop (replaces PeekMessage/DispatchMessage) ---- */
    LOG("Entering main loop...");

    while (running) {
        SDL_Event ev;

        /* Process all pending events */
        while (SDL_PollEvent(&ev)) {
            switch (ev.type) {
            case SDL_QUIT:
                running = 0;
                break;
            case SDL_KEYDOWN:
                if (handle_keydown(ev.key.keysym))
                    running = 0;
                break;
            case SDL_WINDOWEVENT:
                if (ev.window.event == SDL_WINDOWEVENT_RESIZED) {
                    int w = ev.window.data1;
                    int h = ev.window.data2;
                    glViewport(0, 0, w, h);
                    LOG("Resized to %dx%d", w, h);
                }
                break;
            default:
                break;
            }
        }

        /* Game tick — call the engine */
        game_tick();

        /* Render frame */
        render_frame(window);
    }

    /* ---- Cleanup ---- */
    LOG("Shutting down...");
    SDL_GL_DeleteContext(glctx);
    SDL_DestroyWindow(window);
    SDL_Quit();
    free(voff_data);
    free(voff_rdata);
    if (log_fp) {
        fprintf(log_fp, "=== VOFF SDL2 Log End ===\n");
        fclose(log_fp);
    }
    LOG("Done.");
    return 0;
}
