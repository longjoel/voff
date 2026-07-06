/* FUN_004cd542 at VA 004cd542 */
#include "../voff_bridge.h"
#include "game.h"


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004cd542__anim_schedule(void)

{
  uint local_c;
  uint32_t *local_8;
  
  DAT_034155c4 = 0;
  DAT_034155c6 = 0;
  DAT_034155c8 = 0;
  _DAT_034155ca = 0;
  DAT_034155cc = 0;
  DAT_034155ce = 0;
  DAT_034155d0 = 0;
  DAT_034155d2 = 0;
  DAT_034155d4 = 0;
  _DAT_034155d8 = 0;
  local_8 = &DAT_01cc1500;
  for (local_c = 0; local_c < 0x3260; local_c = local_c + 1) {
    *local_8 = 0;
    local_8 = local_8 + 1;
  }
  FUN_00480f10();
  return;
}

