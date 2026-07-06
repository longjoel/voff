/* FUN_004a6ab0 at VA 004a6ab0 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_004a6ab0__slot_setup(void)

{
  int local_8;
  
  for (local_8 = 0; local_8 < 0x40; local_8 = local_8 + 1) {
    *(uint32_t *)(&DAT_0345bd20 + local_8 * 0x54) = 0;
    *(int *)(&DAT_0345b180 + local_8 * 4) = local_8;
  }
  DAT_0345b284 = 0;
  return;
}

