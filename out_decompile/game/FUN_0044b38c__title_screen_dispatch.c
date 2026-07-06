/* FUN_0044b38c at VA 0044b38c — title screen sub-state dispatcher */
#include "../voff_bridge.h"
#include "game.h"

void FUN_0044b38c__title_screen_dispatch(void)
{
  int iVar1;
  void *pcVar2;
  uint32_t local_c;

  if (DAT_01ae353c != 2) {
    if (DAT_01caf4d4 == 0) {
      /* DAT_01ed5e1e._2_2_ means bits 16-31 of the uint32_t */
      uint16_t subfield = (uint16_t)(DAT_01ed5e1e >> 16);
      if ((subfield == 0) || (DAT_01ae3690 == 0x1e)) {
        if ((4 < (int)DAT_01ae3690) && (((int)DAT_01ae3690 < 0x1d && (DAT_01caf4d8 != 0)))) {
          DAT_01ae3690 = 0x1d;
        }
      }
      else {
        DAT_01ae3690 = 0x1d;
      }
    }
    _DAT_01ae2e24 = 0x10;
  }

  /* PTR_FUN_005fb238 is a 32-entry function pointer table in .rdata */
  pcVar2 = (void *)(uintptr_t)*(uint32_t*)(__rdata_start + (0x005FB238 - 0x005F5000)
                                            + (DAT_01ae3690 & 0x1f) * 4);
  if ((pcVar2 == NULL) || ((DAT_01ae353c == 2 && (pcVar2 == (void*)(uintptr_t)0x004D53FF)))) {
    DAT_01ae3690 = 1;
  }
  else {
    /* Call the sub-state handler. In the real game this calls through a
     * function pointer. We can't call the original address, so we skip it. */
    /* (*pcVar2)(); */
  }

  if (DAT_01ae353c == 2) {
    local_c = (uint32_t)DAT_03415608;
    do {
      iVar1 = (int)local_c - 1;
      if ((int)local_c < 1) {
        return;
      }
      {
        uint8_t slot = *(uint8_t*)(__data_start + (0x01AE2014 - 0x0063F000) + iVar1 * 0x380);
        if (slot != 0x20 && slot != 0x23 && slot != 0x22) {
          local_c = (uint32_t)iVar1;
        } else {
          break;
        }
      }
    } while (1);
    /* local_c._0_1_ = lo byte of local_c */
    local_c = (local_c & 0xFFFFFF00) | ((uint8_t)iVar1);
    DAT_01caf4a2 = (uint32_t)(uint8_t)local_c;
    DAT_034155e4 = (uint32_t)0xffffffff;
    DAT_01ae3594 = DAT_01ae3594 + 1;
    DAT_01ae3690 = 0;
  }
  else if ((((DAT_01ed5ec4 >> 4 & 1) != 0) && (DAT_006bc94c == 0)) &&
          ((DAT_01ae3690 == 0 || (4 < (int)DAT_01ae3690)))) {
    FUN_00597365(0x1d);
    DAT_01ae3690 = 0x10;
    FUN_004cda9f(0);
  }
  return;
}
