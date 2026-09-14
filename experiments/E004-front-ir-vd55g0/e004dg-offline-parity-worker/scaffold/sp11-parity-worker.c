/* SPDX-License-Identifier: MIT */
/*
 * E004dg OFFLINE parity worker.
 *
 * This is source-controlled algorithm work only. It is not signed, admitted,
 * installed or runnable in production CPZ.  It deliberately has no fallback
 * for the later SWABF/SWASF branch until that algorithm is reproduced exactly.
 */
#include "sp11-parity-worker.h"

static int sp11_mul_size(size_t a, size_t b, size_t *out)
{
	if (a && b > (size_t)-1 / a)
		return SP11_WORKER_EBOUNDS;
	*out = a * b;
	return SP11_WORKER_OK;
}

static void sp11_fill(uint8_t *dst, uint8_t value, size_t len)
{
	size_t i;
	for (i = 0; i < len; i++)
		dst[i] = value;
}

static void sp11_move(uint8_t *dst, const uint8_t *src, size_t len)
{
	size_t i;

	if (dst == src || !len)
		return;
	if (dst < src || dst >= src + len) {
		for (i = 0; i < len; i++)
			dst[i] = src[i];
	} else {
		for (i = len; i; i--)
			dst[i - 1] = src[i - 1];
	}
}

static int sp11_swab_two_pass_pending(uint8_t *dst, const uint8_t *src,
				      uint32_t width, uint32_t height)
{
	(void)dst;
	(void)src;
	(void)width;
	(void)height;
	/* Fail closed: never substitute a normal copy for Windows SWABF/SWASF. */
	return SP11_WORKER_ESWAB_PENDING;
}

int sp11_parity_worker_run(struct sp11_worker_request *req)
{
	size_t y_size, tail_size, frame_size, dst_end;
	uint8_t *dst;
	int ret;

	if (!req || !req->dst_base || !req->src || !req->width || !req->height)
		return SP11_WORKER_EINVAL;
	if (!req->captured_extent || req->serialized_extent > req->captured_extent ||
	    req->payload_offset > req->serialized_extent)
		return SP11_WORKER_EBOUNDS;
	if (req->captured_extent > req->dst_extent ||
	    req->serialized_extent > req->dst_extent)
		return SP11_WORKER_EBOUNDS;

	ret = sp11_mul_size((size_t)req->width, (size_t)req->height, &y_size);
	if (ret)
		return ret;
	tail_size = y_size / 2;
	if (y_size > (size_t)-1 - tail_size)
		return SP11_WORKER_EBOUNDS;
	frame_size = y_size + tail_size;
	if (req->payload_offset > (size_t)-1 - frame_size)
		return SP11_WORKER_EBOUNDS;
	dst_end = req->payload_offset + frame_size;
	if (dst_end > req->serialized_extent || dst_end > req->captured_extent ||
	    dst_end > req->dst_extent)
		return SP11_WORKER_EBOUNDS;
	if (req->src_extent < y_size)
		return SP11_WORKER_EBOUNDS;

	dst = req->dst_base + req->payload_offset;

	/* Windows FUN_1800033d8: Y=100, UV/tail=0x80; source unused. */
	if (req->synthetic_fill) {
		sp11_fill(dst, 100, y_size);
		sp11_fill(dst + y_size, 0x80, tail_size);
		return SP11_WORKER_OK;
	}

	/* Windows FUN_180003718: request IDs below 10 copy luma then neutral tail. */
	if (req->request_id < 10) {
		sp11_move(dst, req->src, y_size);
		sp11_fill(dst + y_size, 0x80, tail_size);
		return SP11_WORKER_OK;
	}

	/* Windows FUN_180003478: exact SWABF -> scratch -> SWASF is still pending. */
	ret = sp11_swab_two_pass_pending(dst, req->src, req->width, req->height);
	if (ret)
		return ret;
	sp11_fill(dst + y_size, 0x80, tail_size);
	return SP11_WORKER_OK;
}
