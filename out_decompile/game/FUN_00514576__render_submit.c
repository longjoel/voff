/* FUN_00514576 at VA 00514576 — render bridge (replaced with DDraw Blt)
 *
 * This is the central rendering dispatch. Instead of building D3D
 * execute buffer commands, we forward directly to d3d_submit which
 * draws colored rectangles from the current transform matrix.
 */
#include "../voff_bridge.h"
#include "game.h"

void FUN_00514576__render_submit(uint param_1, uint param_2, uint param_3, int param_4)
{
  /* Forward to d3d_submit — the sprite position is already in the
   * transform matrix (set up by FUN_0040ef60 / FUN_00514639 etc).
   * The data pointers param_1-3 describe what to draw, which we
   * ignore for now (just drawing colored rects at matrix position). */
  FUN_005cc4c6__d3d_submit(param_1, param_2, param_3, param_4);
}
