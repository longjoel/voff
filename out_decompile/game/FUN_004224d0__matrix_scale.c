/* FUN_004224d0 at VA 004224d0 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_004224d0__matrix_scale(float param_1,float param_2,float param_3)

{
  float *pfVar1;
  float fVar2;
  float *pfVar3;
  
  pfVar3 = DAT_0365b988;
  pfVar1 = DAT_0365b988 + 1;
  fVar2 = DAT_0365b988[2];
  *DAT_0365b988 = *DAT_0365b988 * param_1;
  pfVar3[1] = *pfVar1 * param_2;
  pfVar3[2] = fVar2 * param_3;
  pfVar3[3] = pfVar3[3] * param_1;
  pfVar3[4] = pfVar3[4] * param_2;
  pfVar3[5] = pfVar3[5] * param_3;
  pfVar3[6] = pfVar3[6] * param_1;
  pfVar3[7] = pfVar3[7] * param_2;
  pfVar3[8] = pfVar3[8] * param_3;
  return;
}

