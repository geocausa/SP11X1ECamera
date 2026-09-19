/* SPDX-License-Identifier: MIT */
/*
 * Single-frame HLOS demonstration of the maintained parity pixel core.
 * Input: one contiguous 644x604 NV12 frame on stdin.
 * Output: one processed 644x604 NV12 frame on stdout.
 * No device access, face matching, trusted buffer mapping or PAM integration.
 */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../sp11-camera-protected-worker/sp11-parity-worker.h"

enum { WIDTH = 644, HEIGHT = 604 };
static void wipe(void *p, size_t n)
{
    volatile unsigned char *b = (volatile unsigned char *)p;
    while (n--) *b++ = 0;
}
int main(void)
{
    const size_t y = (size_t)WIDTH * HEIGHT;
    const size_t frame = y + y / 2;
    const size_t raw_off = (y + 1u) & ~(size_t)1u;
    const size_t scratch_len = raw_off + 4u * y;
    uint8_t *src = NULL, *dst = NULL, *scratch = NULL;
    struct sp11_worker_request req = {0};
    int rc = 1;

    src = malloc(frame);
    dst = malloc(frame);
    scratch = malloc(scratch_len);
    if (!src || !dst || !scratch) {
        fputs("allocation failed\n", stderr);
        goto done;
    }
    if (fread(src, 1, frame, stdin) != frame) {
        fputs("expected exactly one 644x604 NV12 input frame\n", stderr);
        goto done;
    }
    if (fgetc(stdin) != EOF || ferror(stdin)) {
        fputs("input exceeds one frame or read failed\n", stderr);
        goto done;
    }
    memset(dst, 0, frame);
    memset(scratch, 0, scratch_len);
    req.dst_base = dst;
    req.dst_extent = frame;
    req.src = src;
    req.src_extent = frame;
    req.width = WIDTH;
    req.height = HEIGHT;
    req.request_id = 10; /* Windows-evidenced SWABF -> SWASF processing */
    req.payload_offset = 0;
    req.captured_extent = frame;
    req.serialized_extent = frame;
    req.work_base = scratch;
    req.work_extent = scratch_len;
    if (sp11_parity_worker_run(&req) != SP11_WORKER_OK) {
        fputs("pixel core rejected frame\n", stderr);
        goto done;
    }
    if (fwrite(dst, 1, frame, stdout) != frame || fflush(stdout) != 0) {
        fputs("output failure\n", stderr);
        goto done;
    }
    rc = 0;
done:
    if (scratch) { wipe(scratch, scratch_len); free(scratch); }
    if (dst) { wipe(dst, frame); free(dst); }
    if (src) { wipe(src, frame); free(src); }
    return rc;
}
