/* VOFF game logic -- hand-translated from Ghidra decompilation
 *
 * Key game functions reconstructed as clean C from the original binary.
 * Uses the bridge header for data access and type definitions.
 */

#include "voff_bridge.h"

/* ===============================================================
 * .data section: global variables used by game logic
 *
 * These are at specific RVAs in the original binary. We reference
 * them via the DAT/RVA macros from voff_bridge.h.
 * =============================================================== */

/* Global data section declarations */
/* =============================================================== */

/* --- Window handles --- */
#define g_hInstance      DAT(HINSTANCE,   0x0063F000 + 0x01AE5F3C)
#define g_hWnd           DAT(HWND,       0x0063F000 + 0x01AE5F58)
#define g_hAccel         DAT(HACCEL,     0x0063F000 + 0x01ADD12C)
#define g_hDC            DAT(HDC,         0x0063F000 + 0x01AC9F64)

/* --- DirectDraw objects --- */
#define g_lpDD           DAT(LPDIRECTDRAW,       0x0063F000 + 0x01AE5F64)
#define g_lpDDSFront     DAT(LPDIRECTDRAWSURFACE,0x0063F000 + 0x01AE5F68)
#define g_lpDDSBack      DAT(LPDIRECTDRAWSURFACE,0x0063F000 + 0x01AE5F6E)
#define g_lpDDPal        DAT(LPDIRECTDRAWPALETTE, 0x0063F000 + 0x01AE5F72)

/* --- Display mode --- */
#define g_ScreenWidth    DAT(int32_t,    0x0063F000 + 0x006BF5B8)
#define g_ScreenHeight   DAT(int32_t,    0x0063F000 + 0x006BF5BC)
#define g_HalfWidth      DAT(int32_t,    0x0063F000 + 0x006DB530)
#define g_HalfHeight     DAT(int32_t,    0x0063F000 + 0x006DB534)

/* --- Timing --- */
#define g_TimeStart      DAT(uint32_t,   0x0063F000 + 0x01AE5F6C)
#define g_TimeEnd        DAT(uint32_t,   0x0063F000 + 0x01AE5F70)
#define g_TimeTick       DAT(uint32_t,   0x0063F000 + 0x01AE5F84)

/* --- Game state globals --- */
#define g_GameState      DAT(int32_t,    0x0063F000 + 0x01AE3594)
#define g_GameSubState   DAT(int32_t,    0x0063F000 + 0x01AE3690)
#define g_IsPaused       DAT(int32_t,    0x0063F000 + 0x01ADD128)
#define g_IsActive       DAT(int32_t,    0x0063F000 + 0x006BF56C)
#define g_CDAudioMode    DAT(int32_t,    0x0063F000 + 0x006BC94C)
#define g_CDAudioState   DAT(int32_t,    0x0063F000 + 0x006BC948)
#define g_LowMemory      DAT(int32_t,    0x0063F000 + 0x006C84DC)
#define g_MMX_K6         DAT(int32_t,    0x0063F000 + 0x006C84E0)
#define g_RenderQuality  DAT(int32_t,    0x0063F000 + 0x006C84D8)
#define g_RenderFrame    DAT(int32_t,    0x0063F000 + 0x006C84D0)
#define g_RenderSkip     DAT(int32_t,    0x0063F000 + 0x006C84CC)
#define g_RenderSkip2    DAT(int32_t,    0x0063F000 + 0x006C84C8)
#define g_Resolution     DAT(int32_t,    0x0063F000 + 0x006BF598)
#define g_LastRes        DAT(int32_t,    0x0063F000 + 0x006C84E4)
#define g_VRAMPresent    DAT(int32_t,    0x0063F000 + 0x0063F43C)
#define g_PalMode        DAT(int32_t,    0x0063F000 + 0x006BF5A0)
#define g_PalTicks       DAT(int32_t,    0x0063F000 + 0x006BF5A4)
#define g_DrawState      DAT(uint8_t,    0x0063F000 + 0x006BC598)
#define g_CDTrackNumber  DAT(int32_t,    0x0063F000 + 0x006BC958)
#define g_CDMaxTracks    DAT(int32_t,    0x0063F000 + 0x006BC550)
#define g_CDPrevTrack    DAT(int32_t,    0x0063F000 + 0x006BC554)
#define g_FrameLimit     DAT(int32_t,    0x0063F000 + 0x006BF568)
#define g_FrameLimitRes  DAT(int32_t,    0x0063F000 + 0x006C84E8)

#define g_MMXErrorTitle  DAT(const char *, 0x006C86E0)
#define g_MMXErrorBody   DAT(const char *, 0x006C8744)

/* --- CD audio detection --- */
/* Mem threshold for low-memory mode: 0x02DC6C00 = 48MB */
#define MEMORY_THRESHOLD 0x02DC6C00

/* ===============================================================
 * Forward declarations of functions we haven't reimplemented yet
 * =============================================================== */

/* === STUB FORWARD DECLARATIONS === */
static int  stub_cdrom_detect(void) { return 1; }
static void stub_game_init(void) { }
static void stub_input_update(void) { }

/* ===============================================================
 * DirectDraw initialization
 * Original at 0x001C563C
 *
 * Creates DDraw object, sets cooperative level,
 * sets display mode, creates primary surface with backbuffer.
 * =============================================================== */
static LPDIRECTDRAW         g_pDD = NULL;
static LPDIRECTDRAWSURFACE  g_pDDSFront = NULL;
static LPDIRECTDRAWSURFACE  g_pDDSBack = NULL;
static LPDIRECTDRAWPALETTE  g_pDDPal = NULL;

static BOOL ddraw_init(void)
{
    HRESULT hr;
    DDSURFACEDESC ddsd;

    LOG_ENTER();

    /* Create DirectDraw object */
    hr = DirectDrawCreate(NULL, &g_pDD, NULL);
    if (FAILED(hr)) {
        LOG("DirectDrawCreate FAILED: hr=0x%08lx", (unsigned long)hr);
        return FALSE;
    }
    LOG("DirectDrawCreate OK: g_pDD=%p", (void*)g_pDD);

    /* Set cooperative level */
    hr = IDirectDraw_SetCooperativeLevel(g_pDD, g_hWnd,
                                          DDSCL_FULLSCREEN | DDSCL_EXCLUSIVE);
    if (FAILED(hr)) {
        LOG("SetCooperativeLevel FAILED: hr=0x%08lx", (unsigned long)hr);
        return FALSE;
    }
    LOG("SetCooperativeLevel OK: fullscreen+exclusive");

    /* Set display mode: 640x480x16-bit */
    hr = IDirectDraw_SetDisplayMode(g_pDD, 640, 480, 16);
    if (FAILED(hr)) {
        hr = IDirectDraw_SetDisplayMode(g_pDD, 640, 480, 8);
        if (SUCCEEDED(hr)) {
            LOG("SetDisplayMode OK: 640x480x8 (8-bit fallback)");
        } else {
            LOG("SetDisplayMode FAILED: 16-bit and 8-bit both failed");
            return FALSE;
        }
    } else {
        LOG("SetDisplayMode OK: 640x480x16");
    }

    /* Create primary surface */
    memset(&ddsd, 0, sizeof(ddsd));
    ddsd.dwSize = sizeof(ddsd);
    ddsd.dwFlags = DDSD_CAPS | DDSD_BACKBUFFERCOUNT;
    ddsd.dwBackBufferCount = 1;
    ddsd.ddsCaps.dwCaps = DDSCAPS_PRIMARYSURFACE | DDSCAPS_FLIP | DDSCAPS_COMPLEX;

    hr = IDirectDraw_CreateSurface(g_pDD, &ddsd, &g_pDDSFront, NULL);
    if (FAILED(hr)) {
        LOG("CreateSurface FAILED: hr=0x%08lx", (unsigned long)hr);
        return FALSE;
    }

    /* Get the backbuffer */
    {
        DDSCAPS caps;
        memset(&caps, 0, sizeof(caps));
        caps.dwCaps = DDSCAPS_BACKBUFFER;
        hr = IDirectDrawSurface_GetAttachedSurface(g_pDDSFront, &caps, &g_pDDSBack);
        if (FAILED(hr)) {
            LOG("GetAttachedSurface FAILED: hr=0x%08lx", (unsigned long)hr);
            return FALSE;
        }
    }
    LOG("Primary+backbuffer surfaces created: front=%p back=%p", (void*)g_pDDSFront, (void*)g_pDDSBack);

    /* ============================================================
     * D3D3 test: create device, execute buffer, submit test op
     * ============================================================ */
    {
        LPDIRECT3D lpD3D = NULL;
        LPDIRECT3DDEVICE lpD3DDev = NULL;
        LPDIRECTDRAWSURFACE lpD3DSurf = NULL;
        LPDIRECT3DEXECUTEBUFFER lpExecBuf = NULL;
        HRESULT d3dhr;

        d3dhr = IDirectDraw_QueryInterface(g_pDD, &IID_IDirect3D, (void**)&lpD3D);
        if (FAILED(d3dhr)) {
            LOG("IDirect3D QueryInterface FAILED: hr=0x%08lx", (unsigned long)d3dhr);
        } else {
            LOG("IDirect3D obtained: %p", (void*)lpD3D);

            D3DFINDDEVICESEARCH search = {0};
            D3DFINDDEVICERESULT result = {0};
            search.dwSize = sizeof(search);
            search.dwFlags = D3DFDS_COLORMODEL;
            search.dcmColorModel = D3DCOLOR_RGB;
            result.dwSize = sizeof(result);

            d3dhr = IDirect3D_FindDevice(lpD3D, &search, &result);
            if (FAILED(d3dhr)) {
                LOG("FindDevice FAILED: hr=0x%08lx", (unsigned long)d3dhr);
            } else {
                LOG("FindDevice OK: guid=%08x-%04x-%04x",
                    (unsigned)result.guid.Data1,
                    (unsigned)result.guid.Data2,
                    (unsigned)result.guid.Data3);

                DDSURFACEDESC d3dsd = {0};
                d3dsd.dwSize = sizeof(d3dsd);
                d3dsd.dwFlags = DDSD_CAPS | DDSD_WIDTH | DDSD_HEIGHT;
                d3dsd.dwWidth  = 640;
                d3dsd.dwHeight = 480;
                d3dsd.ddsCaps.dwCaps = DDSCAPS_3DDEVICE | DDSCAPS_OFFSCREENPLAIN;

                d3dhr = IDirectDraw_CreateSurface(g_pDD, &d3dsd, &lpD3DSurf, NULL);
                if (FAILED(d3dhr)) {
                    LOG("3D device surface FAILED: hr=0x%08lx", (unsigned long)d3dhr);
                } else {
                    LOG("3D device surface: %p", (void*)lpD3DSurf);

                    d3dhr = IDirectDrawSurface_QueryInterface(lpD3DSurf,
                                &IID_IDirect3DRGBDevice, (void**)&lpD3DDev);
                    if (FAILED(d3dhr)) {
                        LOG("D3DDevice QI FAILED: hr=0x%08lx", (unsigned long)d3dhr);
                    } else {
                        LOG("D3D Device: %p", (void*)lpD3DDev);

                        /* Create a viewport (required for Execute) */
                        LPDIRECT3DVIEWPORT lpViewport = NULL;
                        d3dhr = IDirect3D_CreateViewport(lpD3D, &lpViewport, NULL);
                        if (FAILED(d3dhr)) {
                            LOG("CreateViewport FAILED: hr=0x%08lx", (unsigned long)d3dhr);
                        } else {
                            LOG("Viewport: %p", (void*)lpViewport);

                            d3dhr = IDirect3DDevice_AddViewport(lpD3DDev, lpViewport);
                            if (FAILED(d3dhr)) {
                                LOG("AddViewport FAILED: hr=0x%08lx", (unsigned long)d3dhr);
                            } else {
                                LOG("Viewport added to device");

                                /* Set viewport data */
                                D3DVIEWPORT vpData = {0};
                                vpData.dwSize = sizeof(vpData);
                                vpData.dwX = 0;
                                vpData.dwY = 0;
                                vpData.dwWidth  = 640;
                                vpData.dwHeight = 480;
                                vpData.dvScaleX = 320.0f;
                                vpData.dvScaleY = 240.0f;
                                vpData.dvMaxX   = 1.0f;
                                vpData.dvMaxY   = 1.0f;
                                vpData.dvMinZ   = 0.0f;
                                vpData.dvMaxZ   = 1.0f;
                                IDirect3DViewport_SetViewport(lpViewport, &vpData);

                                /* Now create and execute the buffer */
                                D3DEXECUTEBUFFERDESC ebdesc = {0};
                        ebdesc.dwSize = sizeof(ebdesc);
                        ebdesc.dwFlags = D3DDEB_BUFSIZE | D3DDEB_CAPS;
                        ebdesc.dwBufferSize = 1024;
                        ebdesc.dwCaps = D3DDEBCAPS_SYSTEMMEMORY;

                        d3dhr = IDirect3DDevice_CreateExecuteBuffer(lpD3DDev, &ebdesc,
                                                                     &lpExecBuf, NULL);
                        if (FAILED(d3dhr)) {
                            LOG("CreateExecuteBuffer FAILED: hr=0x%08lx", (unsigned long)d3dhr);
                        } else {
                            LOG("Execute buffer: %p", (void*)lpExecBuf);

                            memset(&ebdesc, 0, sizeof(ebdesc));
                            ebdesc.dwSize = sizeof(ebdesc);
                            d3dhr = IDirect3DExecuteBuffer_Lock(lpExecBuf, &ebdesc);
                            if (SUCCEEDED(d3dhr)) {
                                DWORD *cmd = (DWORD*)ebdesc.lpData;
                                *cmd++ = D3DOP_EXIT;
                                *cmd++ = 0;
                                *cmd++ = 0;
                                *cmd++ = 0;
                                IDirect3DExecuteBuffer_Unlock(lpExecBuf);

                                D3DEXECUTEDATA execData = {0};
                                execData.dwSize = sizeof(execData);
                                execData.dwInstructionLength = 
                                    (DWORD)((char*)cmd - (char*)ebdesc.lpData);

                                d3dhr = IDirect3DDevice_Execute(lpD3DDev, lpExecBuf,
                                                                  lpViewport, 0);
                                if (FAILED(d3dhr)) {
                                    LOG("Execute FAILED: hr=0x%08lx", (unsigned long)d3dhr);
                                } else {
                                    LOG("D3D3 Execute: OK! Pipeline works via Wine!");
                                }
                            }
                        }
                        if (lpViewport) { IDirect3DViewport_Release(lpViewport); }
                    }
                }
            }
        }
        }
        }
        /* Release D3D resources (keep DDraw for software render) */
        if (lpExecBuf) IDirect3DExecuteBuffer_Release(lpExecBuf);
        if (lpD3DDev)  IDirect3DDevice_Release(lpD3DDev);
        if (lpD3DSurf) IDirectDrawSurface_Release(lpD3DSurf);
        if (lpD3D)     IDirect3D_Release(lpD3D);
    }

    /* Create palette (256 entries) */
    {
        PALETTEENTRY pe[256];
        int i;
        for (i = 0; i < 256; i++) {
            pe[i].peRed   = (i & 0xE0);
            pe[i].peGreen = (i & 0x1C) << 3;
            pe[i].peBlue  = (i & 0x03) << 6;
            pe[i].peFlags = 0;
        }
        hr = IDirectDraw_CreatePalette(g_pDD, DDPCAPS_8BIT, pe, &g_pDDPal, NULL);
        if (SUCCEEDED(hr)) {
            IDirectDrawSurface_SetPalette(g_pDDSFront, g_pDDPal);
        }
    }

    g_ScreenWidth  = 640;
    g_ScreenHeight = 480;
    g_HalfWidth    = 320;
    g_HalfHeight   = 240;

    LOG_EXIT1("OK");
    return TRUE;
}

/* ===============================================================
 * Render a frame — clear to a solid color, draw test pattern
 * =============================================================== */
static void render_frame(void)
{
    DDSURFACEDESC ddsd;
    HRESULT hr;
    int x, y, bpp;
    static int frame_count = 0;
    static DWORD last_log_time = 0;
    static int first_frame = 1;
    DWORD now = timeGetTime();

    frame_count++;

    if (first_frame) {
        LOG("First frame rendered");
        first_frame = 0;
        last_log_time = now;
        frame_count = 0;
    }

    /* Log FPS every 2 seconds */
    if (now - last_log_time >= 2000) {
        float fps = frame_count * 1000.0f / (float)(now - last_log_time + 1);
        LOG("FPS=%.1f (frame %d, %dx%d)", fps, frame_count, 640, 480);
        frame_count = 0;
        last_log_time = now;
    }

    memset(&ddsd, 0, sizeof(ddsd));
    ddsd.dwSize = sizeof(ddsd);

    hr = IDirectDrawSurface_Lock(g_pDDSBack, NULL, &ddsd,
                                  DDLOCK_WAIT | DDLOCK_WRITEONLY, NULL);
    if (FAILED(hr))
        return;

    /* Detect pixel format from the surface */
    bpp = ddsd.ddpfPixelFormat.dwRGBBitCount / 8;
    if (bpp < 1) bpp = 1;

    if (bpp == 2) {
        /* 16-bit mode: 5-6-5 RGB */
        uint16_t *buf16 = (uint16_t *)ddsd.lpSurface;
        int pitch16 = ddsd.lPitch / 2;

        for (y = 0; y < 480; y++) {
            uint16_t *row = &buf16[y * pitch16];
            uint16_t color = (y < 240)
                ? (uint16_t)(((y * 31 / 240) << 11) | 0x001F)   /* blue gradient top */
                : (uint16_t)(0x7E0 | ((479 - y) * 31 / 240));     /* green gradient bottom */
            for (x = 0; x < 640; x++) {
                row[x] = color;
            }
        }

        /* White rectangle in center */
        for (y = 200; y < 280; y++) {
            uint16_t *row = &buf16[y * pitch16];
            for (x = 100; x < 540; x++) {
                if (x < 120 || x > 520 || y < 210 || y > 270)
                    row[x] = 0xFFFF;
            }
        }
    } else {
        /* 8-bit palettized mode */
        uint8_t *buf8 = (uint8_t *)ddsd.lpSurface;

        for (y = 0; y < 480; y++) {
            int color = (y * 256) / 480;
            for (x = 0; x < 640; x++) {
                buf8[y * ddsd.lPitch + x] = (uint8_t)((color + x / 10) & 0xFF);
            }
        }

        for (y = 200; y < 280; y++) {
            for (x = 100; x < 540; x++) {
                if (x < 120 || x > 520 || y < 210 || y > 270)
                    buf8[y * ddsd.lPitch + x] = 255;
            }
        }
    }

    IDirectDrawSurface_Unlock(g_pDDSBack, ddsd.lpSurface);
    IDirectDrawSurface_Flip(g_pDDSFront, NULL, DDFLIP_WAIT);
}

/* ===============================================================
 * Cleanup DDraw resources
 * =============================================================== */
static void ddraw_cleanup(void)
{
    if (g_pDDPal)     { IDirectDrawPalette_Release(g_pDDPal); g_pDDPal = NULL; }
    if (g_pDDSBack)   { /* released with front */ g_pDDSBack = NULL; }
    if (g_pDDSFront)  { IDirectDrawSurface_Release(g_pDDSFront); g_pDDSFront = NULL; }
    if (g_pDD)        { IDirectDraw_Release(g_pDD); g_pDD = NULL; }
}

/* ===============================================================
 * MMX CPU detection
 * Original at 0x001083EF
 * Returns 0x33 (Pentium MMX), 0x3D (K6), or 0
 * =============================================================== */
uint32_t cpuid_check(void)
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

/* ===============================================================
 * Window class registration
 * Original at 0x001C5909
 *
 * Registers "VirtualONClass" window class
 * =============================================================== */
ATOM register_window_class(HINSTANCE hInstance)
{
    WNDCLASSA wc;

    memset(&wc, 0, sizeof(wc));
    wc.style         = CS_HREDRAW | CS_VREDRAW | CS_DBLCLKS;
    wc.lpfnWndProc   = DefWindowProcA;  /* Overridden later */
    wc.hInstance     = hInstance;
    wc.hIcon         = LoadIconA(hInstance, MAKEINTRESOURCEA(101));
    wc.hCursor       = LoadCursorA(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH);
    wc.lpszClassName = "VirtualONClass";

    return RegisterClassA(&wc);
}

/* ===============================================================
 * Window creation
 * Original at 0x001C59A9
 *
 * Creates the main game window
 * =============================================================== */
BOOL create_window(HINSTANCE hInstance, int nCmdShow)
{
    g_hInstance = hInstance;
    g_hAccel = LoadAcceleratorsA(hInstance, MAKEINTRESOURCEA(101));

    g_hWnd = CreateWindowExA(
        WS_EX_APPWINDOW,
        "VirtualONClass",
        "Virtual ON for PC",
        WS_POPUP,
        0, 0,
        640, 480,
        NULL, NULL,
        hInstance, NULL
    );

    if (!g_hWnd)
        return FALSE;

    ShowWindow(g_hWnd, nCmdShow);
    UpdateWindow(g_hWnd);

    return TRUE;
}

/* ===============================================================
 * Game frame: the main render/logic loop iteration
 * Original at 0x001C5C7A inner loop (~line 756)
 *
 * This is called once per frame from the message loop.
 * Handles CD audio, input, game state machine, rendering.
 * =============================================================== */
static void game_frame(void)
{
    render_frame();
}

/* ===============================================================
 * Main game loop
 * Original at 0x001C5C7A
 *
 * Initializes game subsystems, enters message loop
 * =============================================================== */
int main_game_loop(HINSTANCE hInstance, int nCmdShow)
{
    MSG msg;
    uint32_t cpu_type;
    int result;
    HWND existing_wnd;

    /* MMX CPU check */
    cpu_type = cpuid_check();
    LOG("CPU check: type=0x%02x (%s)", cpu_type,
        cpu_type == 0x33 ? "Pentium MMX" : cpu_type == 0x3D ? "K6" : "UNSUPPORTED");
    if (cpu_type != 0x33 && cpu_type != 0x3D) {
        LOG("MMX check FAILED - showing error dialog");
        MessageBoxA(NULL,
            "This game requires MMX(R) Technology.\n",
            "Virtual ON",
            MB_OK | MB_ICONERROR);
        return 0;
    }

    if (cpu_type == 0x3D) {
        g_MMX_K6 = 1;  /* K6 has different MMX implementation */
    }

    /* Detect CD-ROM (patched to always succeed) */
    if (!stub_cdrom_detect()) {
        return 0;
    }

    /* Init game subsystems */
    stub_game_init();

    /* Register window class if needed */
    if (nCmdShow == 0 || !register_window_class(hInstance)) {
        return 0;
    }

    /* Check for existing instance */
    existing_wnd = FindWindowA("VirtualONClass", NULL);
    if (existing_wnd) {
        BringWindowToTop(existing_wnd);
        return 0;
    }

    /* Create game window */
    LOG("Creating game window...");
    if (!create_window(hInstance, nCmdShow)) {
        LOG("WINDOW CREATION FAILED");
        return 0;
    }
    LOG("Window created: hWnd=%p", (void*)g_hWnd);

    /* Init DirectDraw */
    LOG("Initializing DirectDraw...");
    if (!ddraw_init()) {
        LOG("DDRAW INIT FAILED");
        ddraw_cleanup();
        return -1;
    }
    LOG("DDraw initialized successfully");

    /* Dump key globals from the real data section */
    LOG("--- Data Section Diagnostics ---");
    LOG("g_GameState   = %d (was 0 with zeroed data)", (int)g_GameState);
    LOG("g_GameSubState= %d", (int)g_GameSubState);
    LOG("g_IsActive   = %d", (int)g_IsActive);
    LOG("g_RenderFrame= %d", (int)g_RenderFrame);
    LOG("g_RenderQuality=%d", (int)g_RenderQuality);
    LOG("g_FrameLimit  = %d", (int)g_FrameLimit);
    LOG("g_DrawState   = 0x%02x", (int)g_DrawState);
    LOG("g_Resolution  = %d", (int)g_Resolution);
    LOG("g_ScreenWidth = %d", (int)g_ScreenWidth);
    LOG("g_ScreenHeight= %d", (int)g_ScreenHeight);
    LOG("g_CDAudioMode = %d", (int)g_CDAudioMode);
    LOG("g_CDAudioState= %d", (int)g_CDAudioState);
    LOG("g_PalMode     = 0x%08x", (int)g_PalMode);
    /* Check string data */
    LOG("WindowClass ptr = %p", (void*)(uintptr_t)DAT(uint32_t, 0x006BF544));
    LOG("WindowTitle ptr = %p", (void*)(uintptr_t)DAT(uint32_t, 0x006BF548));
    LOG("--- End Diagnostics ---");

    /* Force game active state (in real game, set by init code) */
    g_IsActive = 1;
    g_RenderFrame = 1;
    g_RenderQuality = 1;  /* Don't check fps limiter */

    LOG("Entering main loop...");

    /* CD audio detection */
    g_CDAudioState = 0;

    /* Additional init */
    stub_input_update();

    /* Main message loop */
    for (;;) {
        g_PalMode   = -1;
        g_PalTicks  = 9999;

        /* Check for quit flag */
        if (g_DrawState & 1)
            break;

        /* Peek message */
        if (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) {
            /* Check for quit keys */
            if (msg.message == 0x104) {
                /* F4 or other interrupt - check */
            }
            if (msg.message == WM_QUIT) {
                LOG("WM_QUIT received, exiting");
                break;
            }

            TranslateAcceleratorA(g_hWnd, g_hAccel, &msg);
            TranslateMessage(&msg);
            DispatchMessageA(&msg);
        } else {
            /* No messages: game frame */
            static int render_check = 0;
            if (render_check == 0) {
                LOG("Entered render path (g_IsActive=%d)", (int)g_IsActive);
                render_check = 1;
            }
            if (g_IsActive == 0) {
                if (IsIconic(g_hWnd)) {
                    ShowWindow(g_hWnd, SW_SHOW);
                }
            } else {
                /* Resolution change detection */
                if (g_VRAMPresent) {
                    if (g_Resolution != g_LastRes) {
                        g_LastRes = g_Resolution;
                        /* Reinit video mode */
                    }
                }

                /* Frame limiting — just render every frame for now */
                {
                    g_TimeStart = timeGetTime();
                    game_frame();
                    g_TimeEnd   = timeGetTime();
                    g_TimeTick  = g_TimeEnd;
                }
            }
        }
    }

    /* Cleanup */
    ddraw_cleanup();
    return msg.wParam;
}

/* ===============================================================
 * WinMain entry point
 * Original at 0x001E7930
 * =============================================================== */
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
                   LPSTR lpCmdLine, int nCmdShow)
{
    (void)hPrevInstance;
    (void)lpCmdLine;

    voff_log_init("voff.log");
    LOG("VOFF Winelib starting");
    LOG("hInstance=%p nCmdShow=%d", (void*)hInstance, nCmdShow);

    return main_game_loop(hInstance, nCmdShow);
}
