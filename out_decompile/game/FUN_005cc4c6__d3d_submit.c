/* FUN_005cc4c6 at VA 005cc4c6 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_005cc4c6__d3d_submit(uint param_1,uint param_2,uint param_3,int param_4)

{
  if ((param_1 & 0xf0000000) != 0) {
    param_1 = *(int *)(&DAT_006a067c + (param_1 >> 0x1c) * 4) + (param_1 & 0xfffffff);
  }
  if ((param_2 & 0xf0000000) != 0) {
    param_2 = *(int *)(&DAT_006a067c + (param_2 >> 0x1c) * 4) + (param_2 & 0xfffffff);
  }
  if ((param_3 & 0xf0000000) != 0) {
    param_3 = *(int *)(&DAT_006a067c + (param_3 >> 0x1c) * 4) + (param_3 & 0xfffffff);
  }
  if (((param_2 & 0xfff00000) != 0) && ((param_3 & 0xfff00000) != 0)) {
    FUN_005e03a0(param_1,param_2,param_3);
  }
  return;
}

