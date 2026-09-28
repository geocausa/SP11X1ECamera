/* SPDX-License-Identifier: MIT */
/* Host-only harness; no camera/module/MMIO access. */
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
typedef uint32_t u32;
typedef uint64_t u64;
typedef uint16_t u16;
#define __used __attribute__((used))
typedef int (*e006m_scalar_fn)(void *, u16, u32 *);
#include "../e006u-rear-bhist16-provider/camss-e006u-bhist16.inc"
#include "bhist-request.h"

static int read_u32(const char *arg, u32 *out)
{
	char *end;
	unsigned long value;
	errno = 0;
	value = strtoul(arg, &end, 10);
	if (errno || end == arg || *end || value > UINT32_MAX)
		return -1;
	*out = (u32)value;
	return 0;
}

int main(int argc, char **argv)
{
	struct e009g_bhist_word state = {0};
	struct e009g_bhist_request req = {
		.request_id = 7, .crop_width = 4064, .crop_height = 2286,
		.aec_roi_valid = true,
	};
	u32 word = 0;
	if (argc != 5 || read_u32(argv[1], &req.aec_roi.left) ||
	    read_u32(argv[2], &req.aec_roi.top) ||
	    read_u32(argv[3], &req.aec_roi.width) ||
	    read_u32(argv[4], &req.aec_roi.height))
		return 2;
	if (e009g_bhist_prepare(&state, &req) ||
	    e009g_bhist_consume(&state, req.request_id, &word) ||
	    e009g_bhist_consume(&state, req.request_id, &word) != -EINVAL ||
	    e009g_bhist_prepare(&state, &req) != -EBUSY)
		return 3;
	printf("%08x\n", word);
	return 0;
}
