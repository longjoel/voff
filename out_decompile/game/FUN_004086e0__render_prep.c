/* FUN_004086e0 at VA 004086e0 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_004086e0__render_prep(void)

{
  uint32_t uVar1;
  uint32_t uVar2;
  uint32_t *puVar3;
  
  puVar3 = DAT_01ae61e0;
  uVar2 = DAT_006bf448;
  uVar1 = DAT_006bf444;
  *DAT_01ae61e0 = DAT_006bf444;
  puVar3[1] = uVar2;
  puVar3[2] = uVar2;
  puVar3[3] = uVar2;
  puVar3[4] = uVar1;
  puVar3[5] = uVar2;
  puVar3[6] = uVar2;
  puVar3[7] = uVar2;
  puVar3[8] = uVar1;
  puVar3[9] = uVar2;
  puVar3[10] = uVar2;
  puVar3[0xb] = uVar2;
  return;
}

