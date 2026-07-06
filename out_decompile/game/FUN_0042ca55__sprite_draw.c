/* FUN_0042ca55 at VA 0042ca55 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_0042ca55__sprite_draw(char param_1,uint32_t param_2,float param_3,uint32_t param_4,
                 uint32_t param_5,float param_6,int param_7,int param_8)

{
  float fVar1;
  int iVar2;
  float fVar3;

  if (DAT_00a00a1c == 0) {
    /* Original: CONCAT44(DAT_005f8894, DAT_005f8890) as a double divisor.
     * DAT_005f8890 and DAT_005f8894 are 32-bit values forming a 64-bit double.
     * Stubbed: use param_6 directly as scale factor. */
    fVar3 = param_6;
  }
  else {
    /* __adj_fdiv_m64 is an MSVC intrinsic — stubbed */
    fVar3 = param_6;
  }
  fVar1 = (float)fVar3;
  iVar2 = FUN_005e6230(DAT_03656878);
  if (*(char *)(iVar2 + -3 + DAT_03656878) == param_1) {
    if (param_8 == 0) {
      FUN_0042c999(param_3 + fVar1,param_4,param_5);
    }
    else {
      FUN_0040ef60(param_3 + fVar1,param_4,param_5);
    }
    if (param_7 == 0) {
      FUN_004224d0(0x3f800000,0x3f800000,0x41200000);
    }
    FUN_005cc380();
    if (param_7 == 0) {
      FUN_005cc4c6(&DAT_007e7c58,&DAT_007e7cb8,&DAT_007a24b8,0);
    }
    else {
      FUN_005cc4c6(&DAT_00791a58,param_2,&DAT_007b5278,0);
    }
  }
  else {
    iVar2 = FUN_005e6230(DAT_03656878);
    if ((*(char *)(iVar2 + -2 + DAT_03656878) == param_1) || (param_1 == '<')) {
      FUN_0040ef60(param_3 + fVar1,param_4,param_5);
      if (param_7 == 0) {
        FUN_004224d0(0x3f800000,0x3f800000,0x41200000);
      }
      FUN_005cc380();
      if (param_7 == 0) {
        FUN_005cc4c6(&DAT_007e82c0,&DAT_007e83c8,&DAT_007a347c,0);
      }
      else {
        FUN_005cc4c6(&DAT_00791a58,param_2,&DAT_007b56d4,0);
      }
    }
    else {
      iVar2 = FUN_005e6230(DAT_03656878);
      if ((*(char *)(iVar2 + -1 + DAT_03656878) == param_1) || (param_1 == '>')) {
        FUN_0040ef60(param_3 + fVar1,param_4,param_5);
        if (param_7 == 0) {
          FUN_004224d0(0x3f800000,0x3f800000,0x41200000);
        }
        FUN_005cc380();
        if (param_7 == 0) {
          FUN_005cc4c6(&DAT_007e83d8,&DAT_007e87e8,&DAT_007a3740,0);
        }
        else {
          FUN_005cc4c6(&DAT_00791a58,param_2,&DAT_007b5790,0);
        }
      }
      else {
        if (param_8 == 0) {
          FUN_0042c999(param_3 + fVar1,param_4,param_5);
        }
        else {
          FUN_0040ef60(param_3 + fVar1,param_4,param_5);
        }
        if (param_7 == 0) {
          FUN_004224d0(0x3f800000,0x3f800000,0x41200000);
        }
        FUN_005cc380();
        if (param_7 == 0) {
          FUN_005cc4c6(*(uint32_t *)(&DAT_006471e0 + (param_1 * 3 + -0x60) * 4),
                       *(uint32_t *)(&DAT_006471e4 + (param_1 * 3 + -0x60) * 4),
                       *(uint32_t *)(&DAT_006471e8 + (param_1 * 3 + -0x60) * 4),0);
        }
        else {
          FUN_005cc4c6(&DAT_00791a58,param_2,(&PTR_DAT_00646ff0)[param_1],0);
        }
      }
    }
  }
  return;
}

