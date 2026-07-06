/* FUN_00442ce1 at VA 00442ce1 — input polling (DirectInput)
 * Stubbed: COM vtable calls can't be directly compiled.
 * The original reads DInput device state at DAT_006536cc.
 */
#include "../voff_bridge.h"
#include "game.h"

void FUN_00442ce1__input_poll(void)
{
  /* Original code:
   *   DAT_01cb14c2 = 0xffff;
   *   _DAT_01cb14c4 = 0xffff;
   *   _DAT_01cb14c6 = 0xffff;
   *   if (lpDIDevice && SUCCEEDED(lpDIDevice->GetDeviceState(...))) {
   *     // read input globals
   *   }
   */

  DAT_01cb14c2 = 0xffff;
  _DAT_01cb14c4 = 0xffff;
  _DAT_01cb14c6 = 0xffff;

  /* DInput device at DAT_006536cc — not available, skip */
  return;
}
