/* VOFF Winelib bridge header
 *
 * Maps Ghidra decompiler output types to compilable C
 * and provides proper linkage to the original binary's data sections.
 */

#ifndef VOFF_BRIDGE_H
#define VOFF_BRIDGE_H

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmsystem.h>
#include <commctrl.h>
#include <ddraw.h>
#include <d3d.h>
#include <dsound.h>
#include <dinput.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

/* ================================================================ */
/* Ghidra type aliases */
/* ================================================================ */
typedef uint8_t  u1;
typedef uint16_t u2;
typedef uint32_t u4;
typedef uint64_t u8;
typedef int8_t   i1;
typedef int16_t  i2;
typedef int32_t  i4;
typedef int64_t  i8;

/* Ghidra uses these names */
typedef uint8_t  undefined;
typedef uint16_t undefined2;
typedef uint32_t undefined4;
typedef uint64_t undefined8;

/* Microsoft types Ghidra resolves */
typedef uint8_t  byte;
typedef uint16_t word;
typedef uint32_t dword;
typedef int32_t  longint;

#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE 0
#endif

/* ================================================================ */
/* Original binary data sections mapped at their virtual addresses  */
/* ================================================================ */

/* ---- .rdata section (read-only data, 0x005F5000 - 0x0063E8E8) ---- */
extern const uint8_t *__rdata_start;
#define RDATA(offset) (*(const void **)(__rdata_start + (offset)))

/* ---- .data section (initialized data, 0x0063F000 - 0x00A00C00) ---- */
extern uint8_t *__data_start;
#define DATA(offset) (*(void **)(__data_start + (offset)))

/* Remember: image base is 0x00400000
 *   .rdata VA = 0x005F5000, RVA = 0x001F5000
 *   .data  VA = 0x0063F000, RVA = 0x0023F000
 */

/* ---- Global variable accessors ---- */
/* DAT_xxxxx vars live in .data section at offset (RVA - 0x0063F000) */
#define DAT_RVA(rva)  ((void *)(__data_start + ((rva) - 0x0063F000)))
#define DAT_VA(va)    DAT_RVA((va) - 0x00400000)

/* PTR_xxxx vars are function or data pointers */
#define PTR_AT(rva)   ((void *)(__data_start + ((rva) - 0x0063F000)))

/* ---- Cast helpers ---- */
#define PTR(type, rva)  (*(type *)(__data_start + ((rva) - 0x0063F000)))
#define DAT(type, rva)  (*(type *)(__data_start + ((rva) - 0x0063F000)))
#define ARR(type, rva)  ((type *)(__data_start + ((rva) - 0x0063F000)))

#define RDAT(type, rva) (*(const type *)(__rdata_start + ((rva) - 0x005F5000)))

/* ================================================================ */
/* Import declarations from original binary's import table          */
/* ================================================================ */

/* KERNEL32 */
extern HANDLE WINAPI GetProcessHeap(void);
extern LPVOID WINAPI HeapAlloc(HANDLE, DWORD, SIZE_T);
extern BOOL WINAPI HeapFree(HANDLE, DWORD, LPVOID);
/* ... more will be added as needed ... */

/* ================================================================ */
/* Logging                                                        */
/* ================================================================ */

#define VOFF_LOG 1

extern FILE *voff_log_fp;

#if VOFF_LOG
  #define LOG(fmt, ...) do { \
    fprintf(stderr, "[VOFF] " fmt "\n", ##__VA_ARGS__); \
    if (voff_log_fp) { fprintf(voff_log_fp, "[VOFF] " fmt "\n", ##__VA_ARGS__); fflush(voff_log_fp); } \
  } while(0)
  #define LOG_ENTER() LOG("ENTER %s", __func__)
  #define LOG_ENTER1(fmt, ...) LOG("ENTER %s " fmt, __func__, ##__VA_ARGS__)
  #define LOG_EXIT() LOG("EXIT  %s", __func__)
  #define LOG_EXIT1(fmt, ...) LOG("EXIT  %s " fmt, __func__, ##__VA_ARGS__)
#else
  #define LOG(...)           ((void)0)
  #define LOG_ENTER()        ((void)0)
  #define LOG_ENTER1(...)    ((void)0)
  #define LOG_EXIT()         ((void)0)
  #define LOG_EXIT1(...)     ((void)0)
#endif

void voff_log_init(const char *path);
void voff_log_close(void);

/* ================================================================ */
/* Function declarations                                           */
/* ================================================================ */

#endif /* VOFF_BRIDGE_H */
