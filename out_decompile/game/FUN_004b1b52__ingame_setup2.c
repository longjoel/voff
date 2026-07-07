/* FUN_004b1b52 at VA 004b1b52 */
#include "../voff_bridge.h"
#include "game.h"


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004b1b52__ingame_setup2(void)

{
  int iVar1;
  
  iVar1 = DAT_01ae2004;
  DAT_01ae2004 = DAT_01ae2004 + 1;
  if (iVar1 == 0) {
    FUN_004cd542();
    FUN_00597311(0x100b);
    FUN_004d1328(1);
    FUN_00483200();
  }
  FUN_004d11cd(DAT_01ae35a0 & 8);
  _DAT_01ae2e24 = 0x21;
  DAT_01ae2e28 = 0xffff;
  if ((DAT_01ae2014 == 0x20) ||
     (((DAT_01ae353c == 0 && (DAT_01ae2014 == 0x21)) || (DAT_006bc94c != 0)))) {
    DAT_01ae3690 = DAT_01ae3690 + 1;
  }
  return;
}

