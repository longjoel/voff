/* FUN_004b1841 at VA 004b1841 */
#include "../voff_bridge.h"
#include "game.h"


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004b1841__ingame_setup1(void)

{
  FUN_004cd8c3(0x1c,0x1d);
  FUN_004d020a(DAT_01ae2004 / 0x3c);
  if (DAT_00bf6f1c == 0) {
    if (DAT_01ae2004 != 0) {
      DAT_01ae2004 = DAT_01ae2004 - 1;
    }
    if ((((DAT_01ae2014 == 0x10) || (DAT_01ae2014 == 0x13)) || (DAT_01ae2014 == 0x14)) ||
       ((((DAT_01ae2014 == 0x62 || (DAT_01ae2014 == 99)) ||
         ((DAT_01ae2014 == 0x70 || ((DAT_01ae2014 == 0x71 || (DAT_01ae2014 == 0x90)))))) ||
        ((DAT_01ae2014 == 0x91 ||
         (((((DAT_01ae2014 == 0xa0 || (DAT_01ae2014 == 0xa1)) || (DAT_01ae2014 == 0x50)) ||
           ((DAT_01ae2014 == 0x51 || (DAT_01ae2014 == 0x52)))) ||
          ((DAT_01ae2014 == 0xff || (DAT_01ae2014 == 0xfe)))))))))) {
      DAT_01ae2e1c = 0;
      _DAT_01ae2e24 = 0x23;
      DAT_00bf6f1c = 1;
    }
    else if ((DAT_01ae2004 == 0) ||
            (((((DAT_01ed5ec4 >> 8 & 1) != 0 || ((DAT_01ed5ec4 >> 0x10 & 1) != 0)) ||
              ((DAT_01ed5ec4 >> 4 & 1) != 0)) && (DAT_01ae2004 < 0x280)))) {
      FUN_00597311(0x12);
      if (DAT_01ae2e1c == 0) {
        _DAT_01ae2e24 = 0x23;
      }
      else {
        _DAT_01ae2e24 = 0x21;
        DAT_01ae2e28 = 0xffff;
      }
      DAT_00bf6f1c = DAT_00bf6f1c + 1;
    }
    else if ((((DAT_01ed5ec4 >> 0xe & 1) == 0) && ((DAT_01ed5ec4 >> 0x16 & 1) == 0)) ||
            (DAT_01ae2e1c == 0)) {
      if ((((DAT_01ed5ec4 >> 0xf & 1) != 0) || ((DAT_01ed5ec4 >> 0x17 & 1) != 0)) &&
         (DAT_01ae2e1c == 0)) {
        DAT_01ae2e1c = 1;
        FUN_00597311(1);
      }
    }
    else {
      DAT_01ae2e1c = 0;
      FUN_00597311(1);
    }
    FUN_004d0275(DAT_01ae2e1c,0);
  }
  else {
    DAT_00bf6f1c = DAT_00bf6f1c + 1;
    FUN_004d0275(DAT_01ae2e1c,DAT_00bf6f1c);
    if (0x3c < DAT_00bf6f1c) {
      if (DAT_01ae2e1c == 0) {
        _DAT_01ae2e24 = 0x23;
        DAT_01ae3690 = 3;
      }
      else {
        _DAT_01ae2e24 = 0x21;
        DAT_01ae2e28 = 0xffff;
        DAT_01ae2004 = 0;
        DAT_01ae3690 = DAT_01ae3690 + 1;
      }
    }
  }
  return;
}

