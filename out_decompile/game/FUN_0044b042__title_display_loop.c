/* FUN_0044b042 at VA 0044b042 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_0044b042__title_display_loop(void)

{
  int iVar1;
  
  iVar1 = DAT_0345b280;
  while (DAT_0345bd10 == 0) {
    FUN_004a6c0a(iVar1);  /* stubbed — would load asset data */
    break;  /* prevent infinite loop since FUN_004a6c0a is stubbed */
  }
  if (DAT_0345bd10 < 1) {
    DAT_0345bd10 = DAT_0345bd10 + 1;
  }
  FUN_004086e0();
  FUN_0044ae55(iVar1);
  *(int *)(&DAT_0345bd24 + iVar1 * 0x54) = *(int *)(&DAT_0345bd24 + iVar1 * 0x54) + 1;
  if (0x23f < *(int *)(&DAT_0345bd24 + iVar1 * 0x54)) {
    FUN_004cda9f(0);
    DAT_01ae3690 = DAT_01ae3690 + 1;
  }
  return;
}

