/* FUN_0049f8e8 at VA 0049f8e8 */
#include "../voff_bridge.h"
#include "game.h"


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0049f8e8__state_dispatcher(void)

{
  bool bVar1;
  
  bVar1 = true;
  FUN_00589923();
  _DAT_006a0568 = _DAT_006a0568 + 0x2711;
  FUN_0049fb9b();
  FUN_0046270d();
  DAT_01ed5ea0 = DAT_01ed5ea0 & 0xfffb;
  FUN_005c017d();
  if ((*(uint32_t*)(__rdata_start + (0x005FE5E0 - 0x005F5000)
       + (DAT_01ae3594 & 0xf) * 4)) == 0) {
    DAT_01ae3594 = 1;
    DAT_01ae3690 = 0;
  }
  else {
    /* Dispatch to compiled handler functions */
    int st = (int)DAT_01ae3594 & 0xf;
    switch (st) {
    case 0: FUN_00476620__state0_handler(); break;
    case 1: FUN_0044b38c__title_screen_dispatch(); break;
    case 2: /* transition — auto-advance */
            DAT_01ae3594 = 3; DAT_01ae3690 = 0; break;
    default:
            DAT_01ae3594 = 1; DAT_01ae3690 = 0; break;
    }
    /* (*(void *)(&PTR_FUN_005fe5e0)[DAT_01ae3594 & 0xf])(); */
    if ((int)DAT_01ae3594 < 0) {
      FUN_0049fb9b();
      FUN_0049f82c();
      return;
    }
  }
  if ((DAT_01ae3528 == 0) && (((DAT_01ed5e22 >> 2 & 1) != 0 || ((DAT_01ed5ed4 & 1) != 0)))) {
    _DAT_01ae35d8 = DAT_01ae3594;
    _DAT_01ae3634 = DAT_01ae3690;
    DAT_01ae3594 = 5;
    DAT_01ae3690 = 0;
  }
  FUN_0051456b();
  if ((DAT_01ae3528 == 0) && (DAT_01ae2014 == 0x50)) {
    DAT_03415611 = 0;
  }
  else {
    bVar1 = false;
  }
  if (bVar1) {
    FUN_0049fa26();
  }
  return;
}

