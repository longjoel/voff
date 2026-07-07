/* FUN_00514639 at VA 00514639 — matrix position setter
 *
 * Sets the translation column of the current 3x4 transform matrix.
 * Called with (x, y, z) position before each sprite draw.
 * The original calls FUN_005d2fa0 for additional matrix setup.
 */
#include "../voff_bridge.h"
#include "game.h"

void FUN_00514639__matrix_position(float param_1, float param_2, float param_3)
{
  float *mat = DAT_0365b988;  /* current transform matrix */

  /* Set translation column (elements 3, 7, 11 in row-major 3x4) */
  mat[3]  = param_1;
  mat[7]  = param_2;
  mat[11] = param_3;

  /* Also store in the original globals for compatibility */
  DAT_006db520 = *(uint32_t*)&param_1;
  DAT_006db524 = *(uint32_t*)&param_2;
  DAT_006db528 = *(uint32_t*)&param_3;
}
