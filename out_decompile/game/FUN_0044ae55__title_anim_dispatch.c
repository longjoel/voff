/* FUN_0044ae55 at VA 0044ae55 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_0044ae55__title_anim_dispatch(int param_1)

{
  static int _cc = 0; _cc++;
  DAT_0345bd28 = 10;  /* force set */
  if (_cc <= 2) LOG("anim_dispatch: p1=%d call=%d data=%p DAT_0345bd28=%d", param_1, _cc, (void*)__data_start, (int)*(int*)(&DAT_0345bd28));
  int iVar1;
  int local_10;
  int local_c;
  
  local_c = *(int *)(&DAT_0345bd38 + param_1 * 0x54);
  iVar1 = *(int *)(&DAT_0345bd28 + param_1 * 0x54);
    if (_cc <= 2) LOG("  iVar1=%d local_c=%d", iVar1, local_c);
  for (local_10 = 0; local_10 < iVar1; local_10 = local_10 + 1) {
    if (*(int *)(&DAT_0345b290 + local_c * 0x54) < *(int *)(&DAT_0345b298 + local_c * 0x54)) {
      /* Dispatch via PTR_FUN_005fb228 jump table — call compiled handlers */
      int handler_idx = *(int *)(&DAT_0345b294 + local_c * 0x54);
      switch (handler_idx) {
      case 0: FUN_0044a670__sprite_render_slot(param_1, local_c); break;
      case 1: FUN_0044ac4a__sprite_render_slot2(param_1, local_c); break;
      default: break;
      }
      *(int *)(&DAT_0345b290 + local_c * 0x54) = *(int *)(&DAT_0345b290 + local_c * 0x54) + 1;
    }
    else {
      FUN_004a6f70(param_1,local_c);
    }
    local_c = *(int *)(&DAT_0345b2a8 + local_c * 0x54);
  }
  return;
}

