/* SPDX-License-Identifier: MIT */
/*
 * E004hi: bounded UNINSTALLED offline HLOS C streaming sidecar.
 *
 * Input: --frames N, 1 <= N <= 16. For i=1..N send 8-byte header
 * "IN01" + u32 little endian i, followed by exactly one 644x604 neutral
 * grayscale NV12 frame. Wait for an "OUT1" + index + one complete NV12
 * frame before sending another. Close input after the Nth output; only
 * "DONE" + u32 N followed by process exit 0 commits the session.
 *
 * Earlier outputs are PROVISIONAL until DONE. A late malformed frame/extra
 * input invalidates the WHOLE session, including all earlier outputs.
 * No camera, PMIC, LED, network, PAM, biometric check, watchdog or login.
 * Caller MUST enforce a time budget and terminate on protocol failure.
 */
#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../sp11-camera-protected-worker/sp11-parity-worker.h"

enum { WIDTH = 644, HEIGHT = 604, MAX_FRAMES = 16 };
enum { YLEN = WIDTH * HEIGHT, FRAME_LEN = YLEN + YLEN / 2 };
enum { RAW_OFF = (YLEN + 1u) & ~1u, SCRATCH_LEN = RAW_OFF + 4 * YLEN };

static void wipe(void *p, size_t n)
{
    volatile uint8_t *q = (volatile uint8_t *)p;
    while (n--) *q++ = 0;
}

static int frame_count(int argc, char **argv, uint32_t *count)
{
    char *end = NULL;
    unsigned long val;
    if (argc != 3 || strcmp(argv[1], "--frames") != 0 ||
        argv[2][0] < '0' || argv[2][0] > '9')
        return -1;
    errno = 0;
    val = strtoul(argv[2], &end, 10);
    if (errno || !end || *end != '\0' || val < 1 ||
        val > MAX_FRAMES)
        return -1;
    *count = (uint32_t)val;
    return 0;
}

static uint32_t little_u32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void encode_header(uint8_t header[8], const char kind[4],
                          uint32_t index)
{
    memcpy(header, kind, 4);
    header[4] = (uint8_t)index;
    header[5] = (uint8_t)(index >> 8);
    header[6] = (uint8_t)(index >> 16);
    header[7] = (uint8_t)(index >> 24);
}

static int neutral_uv(const uint8_t *nv12)
{
    size_t i;
    for (i = YLEN; i < FRAME_LEN; ++i)
        if (nv12[i] != 128)
            return 0;
    return 1;
}

int main(int argc, char **argv)
{
    uint32_t count = 0, index;
    uint8_t header[8];
    uint8_t *src = NULL, *dst = NULL, *scratch = NULL;
    struct sp11_worker_request req = {0};
    int success = 0;

    if (frame_count(argc, argv, &count) != 0) {
        fputs("invalid bounded offline frame count\n", stderr);
        return 2;
    }
    (void)signal(SIGPIPE, SIG_IGN); /* still wipe on a broken output pipe */
    src = malloc(FRAME_LEN);
    dst = malloc(FRAME_LEN);
    scratch = malloc(SCRATCH_LEN);
    if (!src || !dst || !scratch) {
        fputs("offline worker allocation failure\n", stderr);
        goto done;
    }
    req.src = src;
    req.src_extent = FRAME_LEN;
    req.dst_base = dst;
    req.dst_extent = FRAME_LEN;
    req.width = WIDTH;
    req.height = HEIGHT;
    req.request_id = 10;
    req.payload_offset = 0;
    req.captured_extent = FRAME_LEN;
    req.serialized_extent = FRAME_LEN;
    req.work_base = scratch;
    req.work_extent = SCRATCH_LEN;

    for (index = 1; index <= count; ++index) {
        if (fread(header, 1, sizeof(header), stdin) != sizeof(header) ||
            memcmp(header, "IN01", 4) != 0 ||
            little_u32(header + 4) != index) {
            fputs("offline stream invalid frame header/order\n", stderr);
            goto done;
        }
        if (fread(src, 1, FRAME_LEN, stdin) != FRAME_LEN ||
            !neutral_uv(src)) {
            fputs("offline stream incomplete or nonneutral frame\n", stderr);
            goto done;
        }
        memset(dst, 0, FRAME_LEN);
        memset(scratch, 0, SCRATCH_LEN);
        if (sp11_parity_worker_run(&req) != SP11_WORKER_OK ||
            !neutral_uv(dst)) {
            fputs("offline stream actual HLOS C rejected frame\n", stderr);
            goto done;
        }
        encode_header(header, "OUT1", index);
        if (fwrite(header, 1, sizeof(header), stdout) != sizeof(header) ||
            fwrite(dst, 1, FRAME_LEN, stdout) != FRAME_LEN ||
            fflush(stdout) != 0) {
            fputs("offline stream output incomplete\n", stderr);
            goto done;
        }
        /* Do not retain previous frames between provisional outputs. */
        wipe(src, FRAME_LEN);
        wipe(dst, FRAME_LEN);
        wipe(scratch, SCRATCH_LEN);
    }

    /* A complete session must include EOF with no trailing bytes. If the
     * client never closes stdin, it also cannot receive a DONE commitment. */
    if (fgetc(stdin) != EOF || ferror(stdin)) {
        fputs("offline stream excess input or read failure\n", stderr);
        goto done;
    }
    encode_header(header, "DONE", count);
    if (fwrite(header, 1, sizeof(header), stdout) != sizeof(header) ||
        fflush(stdout) != 0) {
        fputs("offline stream terminal marker failure\n", stderr);
        goto done;
    }
    success = 1;
done:
    wipe(header, sizeof(header));
    if (src) { wipe(src, FRAME_LEN); free(src); }
    if (dst) { wipe(dst, FRAME_LEN); free(dst); }
    if (scratch) { wipe(scratch, SCRATCH_LEN); free(scratch); }
    return success ? 0 : 1;
}
