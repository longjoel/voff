/* FUN_005cc4c6 at VA 005cc4c6 — D3D submit (replaced with DirectDraw Blt)
 *
 * Instead of submitting a D3D execute buffer, reads the current
 * transform matrix and draws a colored rectangle at the sprite position.
 */
#include "../voff_bridge.h"
#include "game.h"

void FUN_005cc4c6__d3d_submit(uint param_1, uint param_2, uint param_3, int param_4)
{
  static int call_count = 0;
  call_count++;
  if (call_count == 1 || call_count % 100 == 0) {
    LOG("d3d_submit call #%d: p1=0x%x p2=0x%x p3=0x%x p4=%d",
        call_count, param_1, param_2, param_3, param_4);
  }
  float *mat = DAT_0365b988;
  float tx = mat[3];
  float ty = mat[7];
  float sx = mat[0];
  float sy = mat[5];
  if (sx < 0) sx = -sx;
  if (sy < 0) sy = -sy;

  int x = (int)tx;
  int y = (int)ty;
  int w = (int)(sx * 16.0f);
  int h = (int)(sy * 16.0f);
  if (w < 2) w = 2;
  if (w > 200) w = 200;
  if (h < 2) h = 2;
  if (h > 200) h = 200;
  if (x < 0) x = 0;
  if (y < 0) y = 0;
  if (x + w > 639) w = 639 - x;
  if (y + h > 479) h = 479 - y;

  if (!g_pDDSBack || w <= 0 || h <= 0) return;

  DDSURFACEDESC ddsd;
  memset(&ddsd, 0, sizeof(ddsd));
  ddsd.dwSize = sizeof(ddsd);
  if (FAILED(IDirectDrawSurface_Lock(g_pDDSBack, NULL, &ddsd,
                                      DDLOCK_WAIT, NULL)))
    return;

  uint16_t *dst = (uint16_t *)ddsd.lpSurface;
  int pitch = ddsd.lPitch / 2;
  /* Color cycles through hues based on param_1 (sprite type) */
  uint16_t color = (uint16_t)(
    ((((param_1 * 37) & 0x1F)) << 11) |
    ((((param_1 * 71) & 0x3F)) << 5)  |
    (((param_1 * 13) & 0x1F)));

  for (int dy = 0; dy < h; dy++)
    for (int dx = 0; dx < w; dx++)
      dst[(y + dy) * pitch + (x + dx)] = color;

  IDirectDrawSurface_Unlock(g_pDDSBack, ddsd.lpSurface);
}
