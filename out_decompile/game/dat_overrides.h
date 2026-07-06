/* Manual overrides for DAT_ macros that need pointer (not scalar) access.
 * These globals are used as arrays or pointers in the decompiled code
 * and need a different macro form than the auto-generated scalar deref.
 *
 * Format:
 *   #undef DAT_XXXXXXXX
 *   #define DAT_XXXXXXXX ((type*)(__data_start + offset))
 *
 * Put overrides here, then run 'make gen' to regenerate game.h which
 * includes this file after the auto-generated macros.
 */

/* Matrix stack: used as float array with subscript [0..11] and pointer assign */
#undef  DAT_0365b988
#define DAT_0365b988 ((float*)(__data_start + (0x0365B988 - 0x0063F000)))

/* Add more overrides as needed:
 * #undef  DAT_XXXXXXXX
 * #define DAT_XXXXXXXX ((specific_type*)(__data_start + (0xXXXXXXXX - 0x0063F000)))
 */
