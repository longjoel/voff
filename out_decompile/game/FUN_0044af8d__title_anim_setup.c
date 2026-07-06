/* FUN_0044af8d at VA 0044af8d */
#include "../voff_bridge.h"
#include "game.h"


void FUN_0044af8d__title_anim_setup(void)

{
  int iVar1;
  uint32_t *puVar2;
  uint32_t *puVar3;
  
  FUN_004a38a0(0);
  FUN_004cd542();
  FUN_004cda9f(0x8000);
  FUN_004a6b68();
  puVar2 = &DAT_005fb140;
  puVar3 = (uint32_t *)(&DAT_0345bd20 + DAT_0345b280 * 0x54);
  for (iVar1 = 0x15; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  DAT_0345b288 = &DAT_005fb198;
  DAT_0345bd10 = -DAT_005fb198;
  DAT_01ae3690 = DAT_01ae3690 + 1;
  FUN_004d04f8(1);
  FUN_00597311(0x208);
  FUN_00597311(0xfdf8);
  FUN_00597311(0x208);
  FUN_00597311(0xfdf8);
  FUN_005973a0(0x101a);
  return;
}

