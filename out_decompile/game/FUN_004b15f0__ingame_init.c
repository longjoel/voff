/* FUN_004b15f0 at VA 004b15f0 */
#include "../voff_bridge.h"
#include "game.h"


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004b15f0__ingame_init(void)

{
  if (DAT_00bf6f50 == 0) {
    FUN_00597433(1);
    FUN_0056240a();
    _DAT_01ae2e24 = 0;
    DAT_01ae1ffc = DAT_01ae1ffc + 1;
  }
  if (DAT_006bc94c == 0) {
    if ((((((DAT_01ae2014 == 0x10) || (DAT_01ae2014 == 0x13)) || (DAT_01ae2014 == 0x14)) ||
         ((DAT_01ae2014 == 0x62 || (DAT_01ae2014 == 99)))) ||
        (((DAT_01ae2014 == 0x70 || ((DAT_01ae2014 == 0x71 || (DAT_01ae2014 == 0x90)))) ||
         (DAT_01ae2014 == 0x91)))) ||
       ((((DAT_01ae2014 == 0xa0 || (DAT_01ae2014 == 0xa1)) || (DAT_01ae2014 == 0x50)) ||
        (((DAT_01ae2014 == 0x51 || (DAT_01ae2014 == 0x52)) ||
         ((DAT_01ae2014 == 0xff || (DAT_01ae2014 == 0xfe)))))))) {
      if ((DAT_01ae2014 == 0xff) || ((DAT_01ae353c != 0 && (DAT_00bf6f50 < 5)))) {
        DAT_00bf6f50 = DAT_00bf6f50 + 1;
      }
      else {
        _DAT_01ae2e24 = 0x23;
        DAT_01ae3690 = 3;
        DAT_01ae2e1c = 0;
      }
    }
    else {
      _DAT_01ae2e24 = 0;
      DAT_00bf6f1c = 0;
      DAT_01ae2004 = 0x293;
      FUN_004cd542();
      FUN_004cd8c3(0x1c,0x1d);
      FUN_004d020a(DAT_01ae2004 / 0x3c);
      FUN_004d026a();
      DAT_01ae2e1c = 1;
      FUN_004d0275(1,0);
      DAT_01ae3690 = DAT_01ae3690 + 1;
      FUN_00483200();
    }
  }
  else {
    _DAT_01ae2e24 = 0x21;
    DAT_01ae2e28 = 0xffff;
    DAT_01ae3690 = 2;
    DAT_01ae2e1c = 1;
    FUN_004cd542();
  }
  DAT_01ae3598 = 0;
  return;
}

