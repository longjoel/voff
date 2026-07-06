/* FUN_0040ef60 at VA 0040ef60 */
#include "../voff_bridge.h"
#include "game.h"


void FUN_0040ef60__matrix_translate(float param_1,float param_2,float param_3)

{
  float *pfVar1;
  
  pfVar1 = DAT_0365b988;
  DAT_0365b988[9] =
       DAT_0365b988[2] * param_3 + DAT_0365b988[1] * param_2 +
       *DAT_0365b988 * param_1 + DAT_0365b988[9];
  pfVar1[10] = pfVar1[5] * param_3 + pfVar1[4] * param_2 + pfVar1[3] * param_1 + pfVar1[10];
  pfVar1[0xb] = pfVar1[8] * param_3 + pfVar1[7] * param_2 + pfVar1[6] * param_1 + pfVar1[0xb];
  return;
}

