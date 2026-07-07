/* FUN_004b1ca7 at VA 004b1ca7 */
#include "../voff_bridge.h"
#include "game.h"


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004b1ca7__ingame(void)

{
  DAT_006bf5a0 = 0xffffffff;
  FUN_005c0226();
  FUN_0049fbc0();
  FUN_004086e0();
  if (((DAT_01ae2e1c == 0) && (DAT_01ae2014 == 0x21)) &&
     (((7 < (int)DAT_01ae3690 && ((int)DAT_01ae3690 < 0xd)) || (DAT_01ae3690 == 0x1b)))) {
    DAT_01cb14a0 = DAT_01cb14a0 & 0xfffe;
    FUN_00597433(1);
    _DAT_01ae2e24 = 0x20;
    FUN_00597311(0x4004);
    FUN_00597311(0x1c);
    DAT_01ae3690 = 5;
    DAT_01ae2e1c = 1;
  }
  /* DAT_01ed5e1e._2_2_ — access high 16 bits of uint32 */
  if (((uint16_t)(DAT_01ed5e1e >> 16) != 0) &&
     (((4 < (int)DAT_01ae3690 && ((int)DAT_01ae3690 < 7)) ||
      ((0xc < (int)DAT_01ae3690 && ((int)DAT_01ae3690 < 0x13)))))) {
    FUN_004cf5c9();
  }
  memcpy(&DAT_01ae3362, (void*)(__data_start + (0x01CAF4B6 - 0x0063F000)), 0x14);
  if ((6 < (int)DAT_01ae3690) && ((int)DAT_01ae3690 < 0xb)) {
    if ((DAT_01ae2e1c == 0) || (DAT_01ae353c == 0)) {
      DAT_01ae2e10 = (uint)DAT_01caf4c0;
      DAT_01ae354c = (uint)DAT_01caf4c5;
      DAT_01ae3554 = (uint)DAT_01caf4c4;
    }
    else {
      DAT_01caf4ba = DAT_01ae2556;
      DAT_01caf4bf = DAT_01ae255b;
      DAT_01ae2e10 = (uint)DAT_01ae255c;
      DAT_01ae354c = (uint)DAT_01ae2561;
      DAT_01ae3554 = (uint)DAT_01ae2560;
    }
  }
  if (DAT_01ae3690 != 0) {
    DAT_00bf6f50 = 0;
  }
  /* PTR_FUN_005ff1c0 — 64-entry in-game sub-state jump table in .rdata */
  {
    int sub = (int)DAT_01ae3690 & 0x3f;
    uint32_t handler = *(uint32_t*)(__rdata_start + (0x005FF1C0 - 0x005F5000) + sub * 4);
    static int logged = 0;
    if (!logged) {
      LOG("ingame: sub=%d handler=0x%08X", sub, handler);
      logged = 1;
    }
    if (handler == 0) {
      DAT_01ae3594 = DAT_01ae3594 + 1;
      DAT_01ae3690 = 0;
      LOG("ingame: NULL handler at sub=%d, advancing state", sub);
    } else {
      /* Dispatch to compiled sub-state handlers */
      switch (sub) {
      case 0: FUN_004b15f0__ingame_init(); break;
      case 1: FUN_004b1841__ingame_setup1(); break;
      case 2: FUN_004b1b52__ingame_setup2(); break;
      default:
        /* Auto-advance untranslated sub-states every 60 frames */
        { static int frame = 0; frame++;
          if (frame >= 60) { frame = 0;
            DAT_01ae3690 = (DAT_01ae3690 + 1) & 0x3f;
            LOG("ingame: auto sub %d -> %d", sub, (int)DAT_01ae3690); }
        }
        break;
      }
    }
  }
  DAT_006bf5a0 = 0xffffffff;
  return;
}

