/* FUN_004a6b09 at VA 004a6b09 */
#include "../voff_bridge.h"
#include "game.h"


uint32_t FUN_004a6b09__slot_alloc(void)

{
  uint32_t uVar1;
  
  if (DAT_0345b284 < 0x40) {
    DAT_0345b284 = DAT_0345b284 + 1;
    uVar1 = *(uint32_t *)(&DAT_0345b17c + DAT_0345b284 * 4);
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

