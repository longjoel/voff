/* FUN_00483200 at VA 00483200 */
#include "../voff_bridge.h"
#include "game.h"


uint32_t FUN_00483200__arena_setup(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  if (DAT_0066c1ac != 7) {
    FUN_005cafc0(DAT_0066c1a0);
    FUN_005cafc0(DAT_0066c1a8);
    iVar3 = DAT_005fdad0;
    iVar2 = DAT_005fda50;
    iVar1 = DAT_005fda40;
    DAT_0066c1a0 = &DAT_0353e420;
    iVar5 = DAT_005fda80 + DAT_005fda40 + DAT_005fda50 + DAT_005fd6d4 + DAT_005fdad0 + DAT_005fda88;
    FUN_005cacb0("scradd0.bin",&DAT_0353e420,DAT_005fdad0,DAT_005fdad4);
    FUN_005cacb0("escrgame.bin",DAT_0066c1a0 + iVar3,DAT_005fd6d4,DAT_005fd6d0);
    iVar6 = iVar3 + DAT_005fd6d4 + iVar1;
    FUN_005cacb0("escrgame.bin",DAT_0066c1a0 + iVar3 + DAT_005fd6d4,iVar1,DAT_005fda44);
    iVar7 = iVar6 + iVar2;
    FUN_005cacb0("escrgame.bin",DAT_0066c1a0 + iVar6,iVar2,DAT_005fda54);
    FUN_005cacb0("escrgame.bin",DAT_0066c1a0 + iVar7,DAT_005fda80,DAT_005fda84);
    FUN_005cacb0("escrgame.bin",DAT_0066c1a0 + iVar7 + DAT_005fda80,DAT_005fda88,DAT_005fda8c);
    FUN_00480f30(DAT_0066c1a0,iVar5);
    FUN_0047f0c0(DAT_0066c1a0 + iVar3,DAT_005fd6d4 + iVar1);
    uVar4 = DAT_0066c178;
    DAT_0066c178 = DAT_0066c178 | 4;
    FUN_0047f0c0(DAT_0066c1a0 + iVar3 + DAT_005fd6d4 + iVar1,iVar2);
    DAT_0066c178 = uVar4;
    FUN_0047f0c0(DAT_0066c1a0 + iVar3 + DAT_005fd6d4 + iVar2 + iVar1,
                 (((iVar5 - iVar2) - DAT_005fd6d4) - iVar3) - iVar1);
    DAT_00bf5f7c = (int)(iVar5 + (iVar5 >> 0x1f & 0x7fU)) >> 7;
    DAT_0066c1a8 = &DAT_0345d420;
    FUN_005cacb0("scradd1.bin",&DAT_0345d420,iVar3,DAT_005fdad4);
    FUN_005cacb0("escrgame.bin",DAT_0066c1a8 + iVar3,DAT_005fd6d4,DAT_005fd6d0 + DAT_005fda1c);
    iVar6 = iVar3 + DAT_005fd6d4 + iVar1;
    FUN_005cacb0("escrgame.bin",DAT_0066c1a8 + iVar3 + DAT_005fd6d4,iVar1,
                 DAT_005fda44 + DAT_005fda1c);
    FUN_005cacb0("escrgame.bin",DAT_0066c1a8 + iVar6,iVar2,DAT_005fda54 + DAT_005fda1c);
    FUN_005cacb0("escrgame.bin",DAT_0066c1a8 + iVar6 + iVar2,DAT_005fda80,
                 DAT_005fda84 + DAT_005fda1c);
    FUN_00480f30(DAT_0066c1a8,iVar5);
    iVar6 = DAT_005fd6d4 + iVar1;
    FUN_0047f0c0(DAT_0066c1a8 + iVar3,iVar6);
    uVar4 = DAT_0066c178;
    DAT_0066c178 = DAT_0066c178 | 4;
    FUN_0047f0c0(DAT_0066c1a8 + iVar3 + iVar6,iVar2);
    DAT_0066c178 = uVar4;
    FUN_0047f0c0(DAT_0066c1a8 + iVar3 + iVar2 + iVar1 + DAT_005fd6d4,
                 (((iVar5 - iVar2) - DAT_005fd6d4) - iVar3) - iVar1);
    DAT_00bf5f78 = (int)(iVar5 + (iVar5 >> 0x1f & 0x7fU)) >> 7;
    DAT_0066c1ac = 7;
    return 0;
  }
  return 0;
}

