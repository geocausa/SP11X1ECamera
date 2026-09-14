/* SPDX-License-Identifier: GPL-2.0 */
/* E004dc: recovered same-machine Qualcomm SecurePD example ABI. */
#ifndef SP11_SECUREPD_WORKER_ABI_H
#define SP11_SECUREPD_WORKER_ABI_H

#include <stdint.h>

enum sp11_securepd_buffer_type {
	SP11_SECUREPD_ALGO        = 4,
	SP11_SECUREPD_HEAP        = 5,
	SP11_SECUREPD_POOL        = 6,
	SP11_SECUREPD_DATA        = 7,
	SP11_SECUREPD_STATIC_EXEC = 8,
};

/* libloadalgo_skel.so DWARF: loadalgo_packet_t, exactly 12 bytes. */
struct sp11_securepd_loadalgo_packet {
	uint32_t paddr; /* +0 */
	uint32_t len;   /* +4 */
	int32_t type;   /* +8: enum buffer_type_ext */
};

/* libloadalgo_skel.so DWARF: mem_handle, exactly 24 bytes. */
struct sp11_securepd_mem_handle {
	int32_t fd;       /* +0 */
	uint32_t size;    /* +4 */
	uint64_t addr;    /* +8 */
	int32_t ion_fd;   /* +16 */
	uint32_t _pad20;  /* +20 */
};

/* libloadalgo_skel.so DWARF: gaussian7x7_packet_t, exactly 96 bytes. */
struct sp11_securepd_gaussian_packet {
	struct sp11_securepd_mem_handle src;  /* +0 */
	uint32_t src_width;                   /* +24 */
	uint32_t src_height;                  /* +28 */
	uint32_t src_stride;                  /* +32 */
	uint32_t _pad36;                      /* +36 */
	struct sp11_securepd_mem_handle dst;  /* +40 */
	uint32_t dst_stride;                  /* +64 */
	uint32_t _pad68;                      /* +68 */
	struct sp11_securepd_mem_handle heap; /* +72 */
};

/* example_image_runner.so DWARF: persistent_buffer_data, 12 bytes. */
struct sp11_securepd_persistent_buffer {
	int32_t fd;       /* +0 */
	uint32_t length;  /* +4 */
	uint32_t offset;  /* +8 */
};

#endif
