/* SPDX-License-Identifier: MIT */
/*
 * Bounded, offline HLOS NV12 pixel-processing prototype.
 * Default input/output: exactly one 644x604 NV12 frame on stdin/stdout.
 * Optional --frames N: exactly 1..16 consecutive complete NV12 frames.
 * The whole bounded input is validated before any output is emitted.
 * No device access, face matching, trusted buffers or PAM integration.
 */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../sp11-camera-protected-worker/sp11-parity-worker.h"

enum { WIDTH = 644, HEIGHT = 604, MAX_FRAMES = 16 };

static void wipe(void *p, size_t n)
{
    volatile unsigned char *b = (volatile unsigned char *)p;
    while (n--) *b++ = 0;
}

static int frame_count(int argc, char **argv, size_t *count)
{
    char *end;
    unsigned long value;

    if (argc == 1) {
        *count = 1;
        return 0;
    }
    if (argc != 3 || strcmp(argv[1], "--frames") ||
        argv[2][0] < '0' || argv[2][0] > '9')
        return -1;

    errno = 0;
    value = strtoul(argv[2], &end, 10);
    if (errno || *end || value == 0 || value > MAX_FRAMES)
        return -1;
    *count = (size_t)value;
    return 0;
}

int main(int argc, char **argv)
{
    const size_t y = (size_t)WIDTH * HEIGHT;
    const size_t frame = y + y / 2;
    const size_t raw_off = (y + 1u) & ~(size_t)1u;
    const size_t scratch_len = raw_off + 4u * y;
    size_t count, total, i;
    uint8_t *src = NULL, *dst = NULL, *scratch = NULL;
    struct sp11_worker_request req = {0};
    int rc = 1;

    if (frame_count(argc, argv, &count)) {
        fputs("usage: sp11-hlos-ir [--frames 1..16]\n", stderr);
        return 2;
    }
    total = count * frame; /* MAX_FRAMES is fixed and bounds this product. */
    src = malloc(total);
    dst = malloc(total);
    scratch = malloc(scratch_len);
    if (!src || !dst || !scratch) {
        fputs("allocation failed\n", stderr);
        goto done;
    }
    if (fread(src, 1, total, stdin) != total) {
        fputs("incomplete NV12 frame sequence\n", stderr);
        goto done;
    }
    if (fgetc(stdin) != EOF || ferror(stdin)) {
        fputs("extra NV12 data or input read failure\n", stderr);
        goto done;
    }
    memset(dst, 0, total);
    req.dst_extent = frame;
    req.src_extent = frame;
    req.width = WIDTH;
    req.height = HEIGHT;
    req.request_id = 10; /* Windows-evidenced SWABF -> SWASF processing */
    req.payload_offset = 0;
    req.captured_extent = frame;
    req.serialized_extent = frame;
    req.work_base = scratch;
    req.work_extent = scratch_len;

    for (i = 0; i < count; i++) {
        memset(scratch, 0, scratch_len);
        req.src = src + i * frame;
        req.dst_base = dst + i * frame;
        if (sp11_parity_worker_run(&req) != SP11_WORKER_OK) {
            fprintf(stderr, "pixel core rejected frame %zu\n", i + 1);
            goto done;
        }
    }
    if (fwrite(dst, 1, total, stdout) != total || fflush(stdout) != 0) {
        fputs("output failure\n", stderr);
        goto done;
    }
    rc = 0;
done:
    if (scratch) { wipe(scratch, scratch_len); free(scratch); }
    if (dst) { wipe(dst, total); free(dst); }
    if (src) { wipe(src, total); free(src); }
    return rc;
}
