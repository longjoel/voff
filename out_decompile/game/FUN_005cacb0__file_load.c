/* FUN_005cacb0 at VA 005cacb0 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_005cacb0__file_load(CHAR *param_1,uint32_t param_2,uint32_t param_3,uint32_t param_4)

{
  int iVar1;
  CHAR local_114 [260];
  CHAR *local_10;
  undefined *local_c;
  int local_8;
  
  local_c = &DAT_02b05d50;
  local_8 = FUN_005e6230(&DAT_02b05d50);
  if (0 < local_8) {
    iVar1 = FUN_005e6230(param_1);
    if ((local_8 + iVar1) - 1U < 0x104) {
      if (local_c[local_8 + -1] == '\\') {
        wsprintfA(local_114,&DAT_006c88c8,local_c,param_1);
      }
      else {
        wsprintfA(local_114,s__s__s_00651b34,local_c,param_1);
      }
      local_10 = local_114;
      goto LAB_005cad61;
    }
  }
  local_10 = param_1;
LAB_005cad61:
  FUN_00566e47();
  if (DAT_006c88c4 != 0) {
    iVar1 = FUN_0040d872();
    if (iVar1 == 0) {
      FUN_0040dcc7();
      DAT_0063f43c = 1;
    }
  }
  FUN_005cadb1(local_10,param_2,param_3,param_4);
  return;
}

