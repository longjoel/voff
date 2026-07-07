/* FUN_0044ac4a at VA 0044ac4a */
#include "../voff_bridge.h"
#include "game.h"


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0044ac4a__sprite_render_slot2(uint32_t param_1,int param_2)

{
  uint local_8;
  
  if (*(int *)(&DAT_0345b290 + param_2 * 0x54) < 0x10) {
    *(float *)(&DAT_0345b2d4 + param_2 * 0x54) =
         (float)*(int *)(&DAT_0345b290 + param_2 * 0x54) * (float)_DAT_005fb2e8;
  }
  else if (*(int *)(&DAT_0345b290 + param_2 * 0x54) < 0x20) {
    if (DAT_006c84d0 == 2) {
      local_8 = *(uint *)(&DAT_0345b290 + param_2 * 0x54) >> 1;
    }
    else {
      local_8 = *(uint *)(&DAT_0345b290 + param_2 * 0x54);
    }
    local_8 = local_8 & 1;
    if (local_8 == 0) {
      *(float *)(&DAT_0345b2d4 + param_2 * 0x54) =
           (float)_DAT_005fb2f8 -
           (float)(0x20 - *(int *)(&DAT_0345b290 + param_2 * 0x54)) * (float)_DAT_005fb2f0;
    }
    else {
      *(float *)(&DAT_0345b2d4 + param_2 * 0x54) =
           (float)(0x20 - *(int *)(&DAT_0345b290 + param_2 * 0x54)) * (float)_DAT_005fb2f0 +
           (float)_DAT_005fb2f8;
    }
  }
  else {
    *(uint32_t *)(&DAT_0345b2d4 + param_2 * 0x54) = 0x41000000;
  }
  FUN_004a70c6(0);
  FUN_00408630();
  FUN_00408720(((float)(&DAT_0345b2c0)[param_2 * 0x15] + *(float *)(&DAT_0345b2d4 + param_2 * 0x54))
               - (float)_DAT_005fb310,(float)(&DAT_0345b2c4)[param_2 * 0x15] + (float)_DAT_005fb308,
               (&DAT_0345b2c8)[param_2 * 0x15]);
  FUN_00408790(0x3fca3d71,0x3fca3d71,0x3fca3d71);
  FUN_00514430();
  FUN_00514576(&DAT_009ebd14,&DAT_009ebd44,&DAT_00913a90,0);
  FUN_004086b0();
  return;
}

