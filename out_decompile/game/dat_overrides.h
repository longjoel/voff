/* Manual overrides for DAT_ macros that need pointer (not scalar) access.
 * Put overrides here, then run 'make gen' to regenerate game.h.
 * These are included AFTER the auto-generated macros, so they take precedence.
 */

/* Matrix stack: used as float array with subscript [0..11] and pointer assign */
#undef  DAT_0365b988
#define DAT_0365b988 ((float*)(__data_start + (0x0365B988 - 0x0063F000)))

/* Pointer-style globals (dereferenced as *DAT_xxx or &DAT_xxx used for address) */
#undef  DAT_01ae61e0
#define DAT_01ae61e0 ((void**)(__data_start + (0x01AE61E0 - 0x0063F000)))

/* DAT_03656878: used as char* for string lookups (pointer arith + deref) */
#undef  DAT_03656878
#define DAT_03656878 ((char*)(__data_start + (0x03656878 - 0x0063F000)))

/* DAT_006536cc: used as DInput device pointer (double deref via COM vtable) */
#undef  DAT_006536cc
#define DAT_006536cc ((void**)(__data_start + (0x006536CC - 0x0063F000)))

/* DAT_02b05c40 and friends: used as char* for file paths */
#undef  DAT_0058894
#define DAT_0058894 ((double*)(__data_start + (0x005F8894 - 0x0063F000)))
#undef  DAT_0058890
#define DAT_0058890 ((double*)(__data_start + (0x005F8890 - 0x0063F000)))
/* Wait — these are 0x005Fxxxx which is in .rdata, not .data!
   Actually 0x005F8894 < 0x0063F000, so they're in .rdata.
   Need __rdata_start instead. */
#undef  DAT_005f8894
#define DAT_005f8894 (*(double*)(__rdata_start + (0x005F8894 - 0x005F5000)))
#undef  DAT_005f8890
#define DAT_005f8890 (*(double*)(__rdata_start + (0x005F8890 - 0x005F5000)))
#undef PTR_DAT_00646ff0
#define PTR_DAT_00646ff0 (*(uint32_t(*)[256])(__data_start + (0x00646FF0 - 0x0063F000)))
