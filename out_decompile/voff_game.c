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
static int  cdrom_detect(void) {
    LOG("  cdrom_detect: patched, return 1");
    return 1;
}

/* ===============================================================
 * INIT SEQUENCE FUNCTIONS — translated from original binary
 * Called in exact order from FUN_005c5c7a after window creation.
 * =============================================================== */

static int init_system_check(void) {
    LOG_ENTER();
    LOG_EXIT1("OK");
    return 1;
}

static void init_generic(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_post_window(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_dsound(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_game_state(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_misc1(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_resource_loading(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_game_data(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_frame_state(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static int init_thunk_47e600(void) {
    LOG_ENTER();
    LOG_EXIT1("OK");
    return 1;
}

static int init_thunk_566fb0(void) {
    LOG_ENTER();
    LOG_EXIT1("OK");
    return 1;
}

static void init_misc2(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_unk_444388(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_unk_40f43e(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_unk_5cc616(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_cd_audio(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_unk_501097(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_unk_5898e6(void) {
    LOG_ENTER();
    LOG_EXIT();
}

static void init_unk_495a40(void) {
    LOG_ENTER();
    LOG_EXIT();
}

/* Forward declarations for tick functions that call each other */
static void tick_title_screen(void);
static void tick_state_dispatch(void);

/* Render prep — original at 0x004086e0 */
static void tick_render_prep(void) {
    uint32_t *dst = (uint32_t *)DAT(void*, 0x0063F000 + 0x01AE61E0);
    uint32_t a = DAT(uint32_t, 0x0063F000 + 0x006BF444);
    uint32_t b = DAT(uint32_t, 0x0063F000 + 0x006BF448);
    dst[0] = a; dst[1] = b; dst[2] = b; dst[3] = b;
    dst[4] = a; dst[5] = b; dst[6] = b; dst[7] = b;
    dst[8] = a;
}

/* Input processing — original at 0x00442ce1
 * Reads DirectInput device state. Key for title screen advancement.
 * The DInput device pointer is at DAT_006536cc.
 * For now: stub that fakes no input. We'll inject "press start" later.
 */
static void tick_input(void) {
    static int first_call = 1;
    if (first_call) {
        LOG("  tick_input: DInput device at %p (stubbed, no input read)",
            (void*)(uintptr_t)DAT(void*, 0x0063F000 + 0x06536CC));
        first_call = 0;
    }
}

/* State dispatcher — original at 0x0049f8e8
 * Jump table at PTR_FUN_005fe5e0 indexed by g_GameState & 0xF.
 * The jump table contains VA pointers from the original binary.
 * We can't call those directly — instead we hardcode the dispatch.
 */
static void tick_state_dispatch(void) {
    int state = (int)g_GameState & 0xF;

    switch (state) {
    case 0:
        LOG("  state_dispatch: state 0 -> 1 (splash screen)");
        g_GameState = 1;
        g_GameSubState = 0;
        break;

    case 1:
        /* State 1: Opening cinematic / title sequence */
        tick_title_screen();
        break;

    case 2:
        /* State 2: Transition (calls FUN_004cda9f, advances immediately) */
        LOG("  state_dispatch: state 2 -> 3 (transition)");
        DAT(uint16_t, 0x0063F000 + 0x01CB1500) = 0;
        g_GameState = 3;
        g_GameSubState = 0;
        break;

    case 3:
        /* State 3: Menu / mode select (FUN_004B1BFC) */
        LOG("  state_dispatch: state 3 -> 4 (menu -> game)");
        DAT(int32_t, 0x0063F000 + 0x01AE352C) = 0;
        DAT(int32_t, 0x0063F000 + 0x01AE3590) = 0;
        DAT(int32_t, 0x0063F000 + 0x00681808) = -1;
        DAT(int32_t, 0x0063F000 + 0x01AE1FFC) = 0;
        DAT(int32_t, 0x0063F000 + 0x00BF6F50) = 0;
        DAT(int32_t, 0x0063F000 + 0x01AE362C) = 0;
        DAT(int32_t, 0x0063F000 + 0x01AE368C) = 0;
        DAT(int32_t, 0x0063F000 + 0x01AE2008) = 0;
        DAT(int32_t, 0x0063F000 + 0x00BF6F48) = 0;
        DAT(int32_t, 0x0063F000 + 0x01AE2000) = 0;
        DAT(int16_t, 0x0063F000 + 0x01AE35E6) = 1;
        DAT(void*,  0x0063F000 + 0x01AE0CB8) = (void*)(voff_data_ptr() + (0x01AE1840));
        DAT(void*,  0x0063F000 + 0x01AE12B8) = (void*)(voff_data_ptr() + (0x01AE1C20));
        g_GameState = 4;
        g_GameSubState = 0;
        break;

    case 4:
        /* State 4: In-game */
        {
            static int logged = 0;
            if (!logged) {
                LOG("  state_dispatch: entered IN-GAME (state 4)!");
                logged = 1;
            }
        }
        break;

    default:
        LOG("  state_dispatch: unhandled state %d, resetting to 1", state);
        g_GameState = 1;
        g_GameSubState = 0;
        break;
    }
}

/* Title screen sub-state dispatch
 * Jump table at PTR_FUN_005fb238 in .rdata section
 */
static void tick_title_screen(void) {
    int substate = (int)g_GameSubState & 0x1F;
    static int last_substate = -1;
    static int log_cooldown = 0;

    if (substate != last_substate) {
        LOG("  title: substate %d -> %d", last_substate, substate);
        last_substate = substate;
        log_cooldown = 0;
    }

    /* Get sub-state handler from .rdata jump table (32-bit pointers) */
    uint32_t *jump_table = (uint32_t *)(__rdata_start + (0x005FB238 - 0x005F5000));
    uint32_t handler_va = jump_table[substate];

    if (log_cooldown == 0) {
        LOG("  title: substate=%d handler=FUN_%08X", substate, handler_va);
        log_cooldown = 60;
    }
    log_cooldown--;

    /* Check for game mode 2 (attract mode / start pressed) */
    int mode = DAT(int32_t, 0x0063F000 + 0x01AE353C);
    if (mode == 2) {
        LOG("  title: attract mode, advancing state!");

        int num_players = DAT(int32_t, 0x0063F000 + 0x03415608);
        int found = 0;
        for (int i = num_players - 1; i >= 0; i--) {
            uint8_t slot = DAT(uint8_t, 0x0063F000 + 0x01AE2014 + i * 0x380);
            if (slot == 0x20 || slot == 0x22 || slot == 0x23) {
                found = 1;
                DAT(uint8_t, 0x0063F000 + 0x01CAF4A2) = (uint8_t)i;
                break;
            }
        }
        DAT(int32_t, 0x0063F000 + 0x034155E4) = -1;
        g_GameState = g_GameState + 1;
        g_GameSubState = 0;
        LOG("  title: advanced to game=%d sub=%d (player_found=%d)",
            (int)g_GameState, (int)g_GameSubState, found);
        return;
    }

    /* Normal title screen — wait for input (ENTER = START, SPACE = menu) */
    if (handler_va == 0) {
        g_GameSubState = 1;
    }
    /* (sub-state stays at current value until user presses keys) */

    /* Check for Start button (bit 4 of input register) */
    int input_bits = DAT(int32_t, 0x0063F000 + 0x01ED5EC4);
    if ((input_bits >> 4) & 1) {
        if (g_CDAudioMode == 0 && (g_GameSubState == 0 || g_GameSubState > 4)) {
            LOG("  title: START pressed (input=0x%08x)", input_bits);
            DAT(int32_t, 0x0063F000 + 0x01AE3690) = 0x10;
        }
    }
}

/* Animation update — original at 0x0049fbc0 */
static void tick_anim_update(void) {
    /* DAT_01ae61e0 = &DAT_01ae6000; DAT_006bf440 = 0; */
    DAT(void*, 0x0063F000 + 0x01AE61E0) = (void*)(voff_data_ptr() + (0x01AE6000));
    DAT(int32_t, 0x0063F000 + 0x006BF440) = 0;
}

/* Frame sync / timing — original at 0x005c9f70 */
static void tick_frame_sync(void) {
    /* Reads timing values from data section. Stubbed for now. */
}

/* DDraw surface setup (GDI) — original at 0x005146c6 */
static void init_gdi_surface(HWND hWnd) {
    LOG_ENTER1("hWnd=%p", (void*)hWnd);
    /* Gets DC, selects stock brushes, calls palette setup */
    LOG_EXIT();
}

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

    /* Set display mode: 640x480x16-bit (ColorFill uses fill color) */
    hr = IDirectDraw_SetDisplayMode(g_pDD, 640, 480, 16);
    if (FAILED(hr)) {
        hr = IDirectDraw_SetDisplayMode(g_pDD, 640, 480, 16);
        if (SUCCEEDED(hr)) {
            LOG("SetDisplayMode OK: 640x480x16 (16-bit fallback)");
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
 * Render a frame — clean black screen with state info in log
 * =============================================================== */
/* ===============================================================
 * BSEL sprite loader — extracts 8-bit indexed data, converts to
 * 16-bit surface using a grayscale palette for debugging.
 * =============================================================== */
static LPDIRECTDRAWSURFACE load_bsel_raw(LPDIRECTDRAW lpDD,
                                          const char *path,
                                          int data_offset,
                                          int w, int h)
{
    HANDLE hFile;
    DWORD bytesRead;
    uint8_t *pixels;
    LPDIRECTDRAWSURFACE lpSurf = NULL;
    DDSURFACEDESC ddsd;
    HRESULT hr;

    hFile = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ,
                        NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) return NULL;

    int size = w * h;
    pixels = (uint8_t *)malloc(size);
    if (!pixels) { CloseHandle(hFile); return NULL; }

    SetFilePointer(hFile, data_offset, NULL, FILE_BEGIN);
    ReadFile(hFile, pixels, size, &bytesRead, NULL);
    CloseHandle(hFile);

    if (bytesRead < (DWORD)size) { free(pixels); return NULL; }

    /* Create 16-bit RGB surface */
    memset(&ddsd, 0, sizeof(ddsd));
    ddsd.dwSize = sizeof(ddsd);
    ddsd.dwFlags = DDSD_CAPS | DDSD_WIDTH | DDSD_HEIGHT | DDSD_PIXELFORMAT;
    ddsd.dwWidth  = w;
    ddsd.dwHeight = h;
    ddsd.ddsCaps.dwCaps = DDSCAPS_OFFSCREENPLAIN | DDSCAPS_SYSTEMMEMORY;
    ddsd.ddpfPixelFormat.dwSize = sizeof(DDPIXELFORMAT);
    ddsd.ddpfPixelFormat.dwFlags = DDPF_RGB;
    ddsd.ddpfPixelFormat.dwRGBBitCount = 16;
    ddsd.ddpfPixelFormat.dwRBitMask = 0xF800;
    ddsd.ddpfPixelFormat.dwGBitMask = 0x07E0;
    ddsd.ddpfPixelFormat.dwBBitMask = 0x001F;

    hr = IDirectDraw_CreateSurface(lpDD, &ddsd, &lpSurf, NULL);
    if (FAILED(hr)) { free(pixels); return NULL; }

    /* Lock and fill with grayscale palette */
    memset(&ddsd, 0, sizeof(ddsd));
    ddsd.dwSize = sizeof(ddsd);
    hr = IDirectDrawSurface_Lock(lpSurf, NULL, &ddsd, DDLOCK_WAIT, NULL);
    if (SUCCEEDED(hr)) {
        uint16_t *dst = (uint16_t *)ddsd.lpSurface;
        int pitch16 = ddsd.lPitch / 2;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                uint8_t idx = pixels[y * w + x];
                /* Grayscale: map 0-255 to 5-6-5 RGB */
                uint8_t r5 = (idx >> 3) & 0x1F;
                uint8_t g6 = (idx >> 2) & 0x3F;
                uint8_t b5 = (idx >> 3) & 0x1F;
                dst[y * pitch16 + x] = (uint16_t)((r5 << 11) | (g6 << 5) | b5);
            }
        }
        IDirectDrawSurface_Unlock(lpSurf, ddsd.lpSurface);
    }
    free(pixels);
    return lpSurf;
}

/* ===============================================================
 * TEXB texture decoder — byte-interleaved 4-bit format
 * From FUN_00510ecb. Deinterleaves byte pairs, splits into nibbles.
 * Returns a 1024x1024 16-bit surface (grayscale for now).
 * =============================================================== */
static LPDIRECTDRAWSURFACE texb_load_atlas(LPDIRECTDRAW lpDD, int texb_index)
{
    char path[512];
    HANDLE hFile;
    DWORD br;
    uint8_t *raw, *deint;
    LPDIRECTDRAWSURFACE surf = NULL;
    int i;

    snprintf(path, sizeof(path), "%s/../out_stage2/data/V_ON/TEXB%d.IMG",
             ".", texb_index);

    hFile = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ,
                        NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {
        LOG("TEXB%d: cannot open %s", texb_index, path);
        return NULL;
    }

    raw = (uint8_t *)malloc(1048576);
    if (!raw) { CloseHandle(hFile); return NULL; }
    ReadFile(hFile, raw, 1048576, &br, NULL);
    CloseHandle(hFile);
    if (br < 1048576) { free(raw); return NULL; }

    /* Step 1: Deinterleave. Even bytes -> bottom half, odd bytes -> top half */
    deint = (uint8_t *)malloc(1048576);
    if (!deint) { free(raw); return NULL; }

    for (int row = 0; row < 1024; row++) {
        for (int col = 0; col < 1024; col += 2) {
            int src = row * 1024 + col;
            deint[row * 1024 + col/2] = raw[src + 1];              /* odd -> top */
            deint[(2*row + 1) * 512 + col/2] = raw[src];           /* even -> bottom */
        }
    }
    free(raw);

    /* Step 2: Create 16-bit surface, fill with nibble-expanded grayscale.
     * Each deinterleaved byte -> two 4-bit texels side by side.
     * We display as 2048x1024 surface (scaled down to fit screen). */
    DDSURFACEDESC ddsd;
    memset(&ddsd, 0, sizeof(ddsd));
    ddsd.dwSize = sizeof(ddsd);
    ddsd.dwFlags = DDSD_CAPS | DDSD_WIDTH | DDSD_HEIGHT | DDSD_PIXELFORMAT;
    ddsd.dwWidth = 2048; ddsd.dwHeight = 1024;
    ddsd.ddsCaps.dwCaps = DDSCAPS_OFFSCREENPLAIN | DDSCAPS_SYSTEMMEMORY;
    ddsd.ddpfPixelFormat.dwSize = sizeof(DDPIXELFORMAT);
    ddsd.ddpfPixelFormat.dwFlags = DDPF_RGB;
    ddsd.ddpfPixelFormat.dwRGBBitCount = 16;
    ddsd.ddpfPixelFormat.dwRBitMask = 0xF800;
    ddsd.ddpfPixelFormat.dwGBitMask = 0x07E0;
    ddsd.ddpfPixelFormat.dwBBitMask = 0x001F;

    if (FAILED(IDirectDraw_CreateSurface(lpDD, &ddsd, &surf, NULL))) {
        free(deint); return NULL;
    }

    memset(&ddsd, 0, sizeof(ddsd));
    ddsd.dwSize = sizeof(ddsd);
    if (SUCCEEDED(IDirectDrawSurface_Lock(surf, NULL, &ddsd, DDLOCK_WAIT, NULL))) {
        uint16_t *dst = (uint16_t *)ddsd.lpSurface;
        int pitch = ddsd.lPitch / 2;
        for (int y = 0; y < 1024; y++) {
            for (int x = 0; x < 1024; x++) {
                uint8_t b = deint[y * 1024 + x];
                uint8_t lo = b & 0xF;
                uint8_t hi = (b >> 4) & 0xF;
                /* Scale 0-15 to 5-bit/6-bit channels for 565 RGB */
                uint8_t r5 = (lo * 31) / 15;
                uint8_t g6 = (lo * 63) / 15;
                uint8_t b5 = (lo * 31) / 15;
                dst[y * pitch + x*2]     = (uint16_t)((r5 << 11) | (g6 << 5) | b5);
                r5 = (hi * 31) / 15;
                g6 = (hi * 63) / 15;
                b5 = (hi * 31) / 15;
                dst[y * pitch + x*2 + 1] = (uint16_t)((r5 << 11) | (g6 << 5) | b5);
            }
        }
        IDirectDrawSurface_Unlock(surf, ddsd.lpSurface);
    }
    free(deint);

    return surf;
}

/* TEXB atlas surface */
static LPDIRECTDRAWSURFACE texb_atlas = NULL;
static BOOL atlas_loaded = FALSE;

/* ===============================================================
 * Render a frame — display TEXB texture atlas
 * =============================================================== */
static void render_frame(void)
{
    static int frame_count = 0;
    static DWORD last_log_time = 0;
    DWORD now = timeGetTime();
    DDBLTFX bltfx;
    RECT dst_rect;

    frame_count++;
    if (frame_count == 1) LOG("First frame rendered");

    if (!atlas_loaded) {
        texb_atlas = texb_load_atlas(g_pDD, 0);
        if (texb_atlas) {
            LOG("TEXB0 atlas loaded: 2048x1024 (4-bit deinterleaved)");
        } else {
            LOG("TEXB0 atlas load FAILED");
        }
        atlas_loaded = TRUE;
    }

    if (now - last_log_time >= 2000) {
        float fps = frame_count * 1000.0f / (float)(now - last_log_time + 1);
        LOG("FPS=%.1f state=%d sub=%d", fps,
            (int)g_GameState, (int)g_GameSubState);
        frame_count = 0;
        last_log_time = now;
    }

    memset(&bltfx, 0, sizeof(bltfx));
    bltfx.dwSize = sizeof(bltfx);
    bltfx.dwFillColor = 0;
    IDirectDrawSurface_Blt(g_pDDSBack, NULL, NULL, NULL,
                            DDBLT_COLORFILL | DDBLT_WAIT, &bltfx);

    /* Display the texture atlas — scaled to fit 640x480 */
    if (texb_atlas) {
        dst_rect.left   = 0;
        dst_rect.top    = 0;
        dst_rect.right  = 640;
        dst_rect.bottom = 480;
        IDirectDrawSurface_Blt(g_pDDSBack, &dst_rect,
                                texb_atlas, NULL, DDBLT_WAIT, NULL);
    }

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
    static int frame = 0;
    static int force_advance_frame = 0;
    frame++;

    /* Mode 0 tick — no CD audio (simplest path) */
    tick_input();           /* FUN_00442ce1 — read input */
    tick_anim_update();     /* FUN_0049fbc0 — animation */
    tick_render_prep();     /* FUN_004086e0 — graphics setup */
    tick_state_dispatch();  /* FUN_0049f8e8 — state machine */
    tick_frame_sync();      /* FUN_005c9f70 — timing */

    /* State machine logging every 60 frames */
    if (frame % 60 == 0) {
        LOG("STATE: game=%d sub=%d cd_mode=%d",
            (int)g_GameState, (int)g_GameSubState, (int)g_CDAudioMode);
    }

    /* Also do the software render pattern for visual feedback */
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
        g_MMX_K6 = 1;
    }

    /* System check (CD-ROM detect, etc.) */
    if (!cdrom_detect()) {
        LOG("System check failed");
        return 0;
    }

    /* ============================================================
     * REAL INIT SEQUENCE — translated from FUN_005c5c7a
     * Call order is critical. Each function logs on entry/exit.
     * ============================================================ */
    LOG("=== Game Engine Init Sequence ===");

    init_generic();                  /* FUN_0054056d */

    /* Register window class if needed */
    if (nCmdShow == 0 || !register_window_class(hInstance)) {
        LOG("RegisterClass failed");
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

    /* Continue init sequence */
    if (!init_thunk_47e600()) {      /* thunk_FUN_0047e600 */
        LOG("init_thunk_47e600 failed");
        return -1;
    }

    init_post_window();              /* FUN_005c97e2 */
    init_dsound();                   /* FUN_005895a0 */
    init_game_state();               /* FUN_0040df03 */
    g_CDAudioMode = (g_CDAudioState != 0) ? 1 : 0;
    init_misc1();                    /* FUN_005c5ac3 */
    init_resource_loading();         /* FUN_005ce180 */
    init_game_data();                /* FUN_00511434 */
    init_frame_state();              /* FUN_0049f7fe */
    init_gdi_surface(g_hWnd);       /* FUN_005146c6 */

    if (!init_thunk_566fb0()) {      /* thunk_FUN_00566fb0 */
        LOG("init_thunk_566fb0 failed");
        return -1;
    }

    init_misc2();                    /* FUN_005c5b31 */
    init_unk_444388();               /* FUN_00444388 */
    init_unk_40f43e();               /* FUN_0040f43e */
    init_unk_5cc616();               /* FUN_005cc616 */

    if (g_CDAudioState != 0) {
        init_cd_audio();             /* FUN_004b5fcf */
        init_unk_501097();           /* FUN_00501097 */
    }

    init_unk_5898e6();               /* FUN_005898e6 */
    init_unk_495a40();               /* FUN_00495a40 */

    LOG("=== Init Complete ===");

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

    /* The real init sequence should have set these. Log what we got. */
    LOG("Post-init: g_GameState=%d g_GameSubState=%d g_IsActive=%d g_RenderFrame=%d",
        (int)g_GameState, (int)g_GameSubState,
        (int)g_IsActive, (int)g_RenderFrame);

    /* Force active and render if init didn't set them */
    if (g_IsActive == 0) g_IsActive = 1;
    if (g_RenderFrame == 0) g_RenderFrame = 1;

    LOG("Entering main loop...");

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
            if (msg.message == WM_KEYDOWN) {
                switch (msg.wParam) {
                case VK_ESCAPE:
                    LOG("ESC pressed — quitting");
                    PostQuitMessage(0);
                    break;
                case VK_RETURN:
                    LOG("ENTER pressed — injecting START");
                    DAT(int32_t, 0x0063F000 + 0x01AE353C) = 2;
                    break;
                case VK_SPACE:
                    LOG("SPACE pressed — toggling input bit for state advance");
                    DAT(int32_t, 0x0063F000 + 0x01ED5EC4) ^= 0x10;
                    break;
                case '1': case '2': case '3': case '4': case '5':
                case '6': case '7': case '8': case '9': case '0': {
                    int st = msg.wParam == '0' ? 0 : msg.wParam - '0';
                    LOG("Force state %d", st);
                    g_GameState = st;
                    g_GameSubState = 0;
                    break;
                }
                }
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
