/* FUN_0044a670 at VA 0044a670 */
#include "../voff_bridge.h"
#include "game.h"


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0044a670__sprite_render_slot(int param_1,int param_2)

{
  static int entry_count = 0;
  entry_count++;
  if (entry_count <= 3) {
    LOG("sprite_render_slot: p1=%d p2=%d (call #%d)", param_1, param_2, entry_count);
  }
  short sVar1;
  int iVar2;
  uint uVar3;
  float fVar4;
  float fVar5;
  uint local_28;
  uint32_t local_20;
  float local_1c;
  
  if (*(int *)(&DAT_0345b290 + param_2 * 0x54) == 0) {
    FUN_004d04f8(1);
    DAT_034155d0 = 0x8000;
  }
  if (*(int *)(&DAT_0345b290 + param_2 * 0x54) < 0x20) {
    (&DAT_0345b2c4)[param_2 * 0x15] = 0;
    (&DAT_0345b2c8)[param_2 * 0x15] = (float)*(int *)(&DAT_0345b290 + param_2 * 0x54);
  }
  else {
    (&DAT_0345b2c4)[param_2 * 0x15] = 0;
    (&DAT_0345b2c8)[param_2 * 0x15] = 0x42000000;
  }
  if (*(int *)(&DAT_0345b290 + param_2 * 0x54) == 0x20) {
    FUN_005973a0(0x1f);
  }
  if (*(int *)(&DAT_0345b290 + param_2 * 0x54) == 0x30) {
    FUN_005973a0(0x87);
  }
  else if (*(int *)(&DAT_0345b290 + param_2 * 0x54) == 0x8f) {
    FUN_005973a0(0x86);
  }
  (&DAT_0345b2c0)[param_2 * 0x15] = 0;
  FUN_004a70c6(0);
  iVar2 = *(int *)(&DAT_0345bd24 + param_1 * 0x54) + -0x40;
  if (iVar2 < 0) {
    fVar4 = (float)FUN_004089e0(0xc000);
    fVar5 = (float)FUN_00408a00(0xc000);
    FUN_00514639((float)-fVar4,0,(float)fVar5);
  }
  else if (iVar2 < 0x10) {
    sVar1 = (short)iVar2 * 0x400 + -0x4000;
    fVar4 = (float)FUN_004089e0(sVar1);
    fVar5 = (float)FUN_00408a00(sVar1);
    FUN_00514639((float)-fVar4,0,(float)fVar5);
  }
  else {
    fVar4 = (float)FUN_004089e0(0);
    fVar5 = (float)FUN_00408a00(0);
    FUN_00514639((float)-fVar4,0,(float)fVar5);
  }
  iVar2 = *(int *)(&DAT_0345bd24 + param_1 * 0x54) + -0x30;
  if ((0xf < iVar2) && (iVar2 < 0x90)) {
    uVar3 = *(int *)(&DAT_0345bd24 + param_1 * 0x54) + -0x40 >> 2;
    FUN_004cda9f((uVar3 & 0xffff) << 5 | (uVar3 & 0xffff) << 10 | uVar3 & 0xffff);
  }
  FUN_00408630();
  FUN_00408720((&DAT_0345b2c0)[param_2 * 0x15],(&DAT_0345b2c4)[param_2 * 0x15],
               (&DAT_0345b2c8)[param_2 * 0x15]);
  FUN_00408720(0x3fa3d70a,0x402147ae,0);
  FUN_00408790(0x3fca3d71,0x3fca3d71,0x3fca3d71);
  FUN_00514430();
  FUN_00514576(&DAT_009e6b34,&DAT_009ebccc,&DAT_009055b4,0);
  FUN_004086b0();
  if (*(int *)(&DAT_0345b290 + param_2 * 0x54) < 0x40) {
    if (DAT_006c84d0 == 2) {
      local_28 = *(uint *)(&DAT_0345b290 + param_2 * 0x54) >> 1;
    }
    else {
      local_28 = *(uint *)(&DAT_0345b290 + param_2 * 0x54);
    }
    local_28 = local_28 & 1;
    if (local_28 != 0) {
      if (*(int *)(&DAT_0345b290 + param_2 * 0x54) < 0x20) {
        local_1c = 4.0;
      }
      else {
        if (DAT_00a00a1c == 0) {
          fVar4 = ((float)(0x40 - *(int *)(&DAT_0345b290 + param_2 * 0x54)) *
                  (float)_DAT_005fb2d0) / (float)/* CONCAT44 DAT_005fb2dc,DAT_005fb2d8 */ (double)DAT_005fb2d8;
        }
        else {
          fVar4 = (float)1.0f /* __adj_fdiv_m64 stub */;
        }
        local_1c = (float)fVar4;
      }
      FUN_00408630();
      FUN_00408720((&DAT_0345b2c0)[param_2 * 0x15],(&DAT_0345b2c4)[param_2 * 0x15],
                   (&DAT_0345b2c8)[param_2 * 0x15]);
      FUN_00408720(0x3fa3d70a,0x402147ae,-local_1c);
      FUN_00408790(0x3fca3d71,0x3fca3d71,0x3fca3d71);
      FUN_00514430();
      FUN_00514576(&DAT_009e6b34,&DAT_009ebccc,&DAT_009055b4,0);
      FUN_004086b0();
      FUN_00408630();
      FUN_00408720((&DAT_0345b2c0)[param_2 * 0x15],(&DAT_0345b2c4)[param_2 * 0x15],
                   (&DAT_0345b2c8)[param_2 * 0x15]);
      FUN_00408720(0x3fa3d70a,0x402147ae,-local_1c * (float)_DAT_005fb2e0);
      FUN_00408790(0x3fca3d71,0x3fca3d71,0x3fca3d71);
      FUN_00514430();
      FUN_00514576(&DAT_009e6b34,&DAT_009ebccc,&DAT_009055b4,0);
      FUN_004086b0();
    }
  }
  if (0x3f < *(int *)(&DAT_0345b290 + param_2 * 0x54)) {
    local_20 = 0x39;
    if ((((uint8_t)DAT_006bf598 & 1) == 0) || (DAT_006bc948 != 0)) {
      FUN_004cd8c3(0x39,0x17);
      FUN_004cf4cc(4,2);
      local_20 = 0x3f;
    }
    else {
      FUN_004cd8c3(0x3f,0x17);
      FUN_004cf4cc(4,2);
    }
    FUN_004d13dc(local_20,0x17);
  }
  return;
}

