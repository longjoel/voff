/* VOFF data sections -- embedding the original binary data */

/* Initialize GUIDs for DirectX (must be in exactly one .c file) */
#include <initguid.h>
#include "voff_bridge.h"
#include <string.h>

/* Embedded init data (generated from .data.bin and .rdata.bin via objcopy) */
extern const char _binary_data_init_bin_start[];
extern const char _binary_data_init_bin_end[];
extern const char _binary__rdata_bin_start[];
extern const char _binary__rdata_bin_end[];

/* Full virtual memory layout matching the original PE:
 * .data:  0x0063F000 - 0x00940DB8 (50MB total, first 3.9MB init, rest BSS)  
 * .rdata: 0x005F5000 - 0x0063E8E8 (301KB)
 *
 * Allocated at runtime to avoid 50MB BSS statically.
 */
uint8_t *__data_start = NULL;
uint8_t *__rdata_start_ptr = NULL;
const uint8_t *__rdata_start = NULL;

/* Base symbol for DAT_xxx macros */
volatile char _voff_data_base __attribute__((aligned(4096)));

/* Log file */
FILE *voff_log_fp = NULL;

void voff_log_init(const char *path)
{
    size_t data_size, rdata_size;

    voff_log_fp = fopen(path, "w");

    /* Allocate data section (58MB to cover high BSS globals) */
    __data_start = (uint8_t*)calloc(1, 0x03700000);
    if (!__data_start) {
        if (voff_log_fp) fprintf(voff_log_fp, "[VOFF] FATAL: cannot allocate data section\n");
        return;
    }

    /* Allocate rdata section (301KB) */
    __rdata_start_ptr = (uint8_t*)calloc(1, 0x049A00);
    if (!__rdata_start_ptr) {
        if (voff_log_fp) fprintf(voff_log_fp, "[VOFF] FATAL: cannot allocate rdata section\n");
        return;
    }
    __rdata_start = __rdata_start_ptr;

    /* Copy initialized .data section */
    data_size = _binary_data_init_bin_end - _binary_data_init_bin_start;
    if (data_size <= 0x301DB28) {
        memcpy(__data_start, _binary_data_init_bin_start, data_size);
        if (voff_log_fp) {
            fprintf(voff_log_fp, "[VOFF] Loaded %zu bytes of .data section\n", data_size);
            fflush(voff_log_fp);
        }
    }

    /* Copy .rdata section */
    rdata_size = _binary__rdata_bin_end - _binary__rdata_bin_start;
    if (rdata_size <= 0x049A00) {
        memcpy(__rdata_start_ptr, _binary__rdata_bin_start, rdata_size);
        if (voff_log_fp) {
            fprintf(voff_log_fp, "[VOFF] Loaded %zu bytes of .rdata section\n", rdata_size);
            fflush(voff_log_fp);
        }
    }
}

void voff_log_close(void)
{
    if (voff_log_fp) {
        fprintf(voff_log_fp, "=== VOFF Log End ===\n");
        fclose(voff_log_fp);
        voff_log_fp = NULL;
    }
}
