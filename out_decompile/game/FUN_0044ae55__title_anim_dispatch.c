/* FUN_0044ae55 at VA 0044ae55 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_0044ae55__title_anim_dispatch(int param_1)

{
  int iVar1;
  int local_10;
  int local_c;
  
  local_c = *(int *)(&DAT_0345bd38 + param_1 * 0x54);
  iVar1 = *(int *)(&DAT_0345bd28 + param_1 * 0x54);
  for (local_10 = 0; local_10 < iVar1; local_10 = local_10 + 1) {
    if (*(int *)(&DAT_0345b290 + local_c * 0x54) < *(int *)(&DAT_0345b298 + local_c * 0x54)) {
      /* Call through PTR_FUN_005fb228 jump table — stubbed */
      /* (*(void *)(&PTR_FUN_005fb228)[*(int *)(&DAT_0345b294 + local_c * 0x54)])(param_1,local_c); */
      *(int *)(&DAT_0345b290 + local_c * 0x54) = *(int *)(&DAT_0345b290 + local_c * 0x54) + 1;
    }
    else {
      FUN_004a6f70(param_1,local_c);
    }
    local_c = *(int *)(&DAT_0345b2a8 + local_c * 0x54);
  }
  return;
}

