/* SPDX-License-Identifier: MIT */
/*
 * Offline, bounded bridge for the proven 644x604 greyscale RGB888
 * libcamera output (1936-byte row stride, 4 zero padding bytes/row).
 * Default: one frame; --frames N accepts exactly 1..16 complete frames.
 * Validate the ENTIRE input before writing ANY output. No camera device I/O.
 */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { WIDTH = 644, HEIGHT = 604, RGB_STRIDE = 1936, MAX_FRAMES = 16 };

static void wipe(void *ptr, size_t len)
{
    volatile unsigned char *p = (volatile unsigned char *)ptr;
    while (len--) *p++ = 0;
}
static int parse_count(int argc, char **argv, size_t *count)
{
    unsigned long v;
    char *end;
    if (argc == 1) {
        *count = 1;
        return 0;
    }
    if (argc != 3 || strcmp(argv[1], "--frames") ||
        argv[2][0] < '0' || argv[2][0] > '9')
        return -1;
    errno = 0;
    v = strtoul(argv[2], &end, 10);
    if (errno || *end || v == 0 || v > MAX_FRAMES)
        return -1;
    *count = (size_t)v;
    return 0;
}
int main(int argc, char **argv)
{
    const size_t ybytes = (size_t)WIDTH * HEIGHT;
    const size_t rgbbytes = (size_t)RGB_STRIDE * HEIGHT;
    const size_t nvbytes = ybytes + ybytes / 2;
    size_t count = 0, total_rgb, total_nv, i, row, col;
    uint8_t *rgb = NULL, *nv = NULL;
    int result = 1;

    if (parse_count(argc, argv, &count)) {
        fputs("usage: sp11-ir-rgb888-to-nv12 [--frames 1..16]\n", stderr);
        return 2;
    }
    total_rgb = count * rgbbytes;
    total_nv = count * nvbytes;
    rgb = malloc(total_rgb);
    nv = malloc(total_nv);
    if (!rgb || !nv) {
        fputs("allocation failure\n", stderr);
        goto end;
    }
    if (fread(rgb, 1, total_rgb, stdin) != total_rgb ||
        fgetc(stdin) != EOF || ferror(stdin)) {
        fputs("expected exactly N complete 644x604 RGB888 frames, stride 1936\n",
              stderr);
        goto end;
    }
    for (i = 0; i < count; i++) {
        const uint8_t *input = rgb + i * rgbbytes;
        uint8_t *output = nv + i * nvbytes;
        for (row = 0; row < HEIGHT; row++) {
            const uint8_t *src = input + row * RGB_STRIDE;
            for (col = 0; col < WIDTH; col++) {
                size_t off = col * 3;
                if (src[off] != src[off+1] || src[off] != src[off+2]) {
                    fputs("non-neutral RGB888 pixel: unexpected capture format\n",
                          stderr);
                    goto end;
                }
                output[row*WIDTH + col] = src[off];
            }
            for (col = WIDTH*3; col < RGB_STRIDE; col++)
                if (src[col] != 0) {
                    fputs("nonzero RGB888 row padding\n", stderr);
                    goto end;
                }
        }
        memset(output + ybytes, 128, nvbytes - ybytes);
    }
    if (fwrite(nv, 1, total_nv, stdout) != total_nv || fflush(stdout)) {
        fputs("NV12 output failure\n", stderr);
        goto end;
    }
    result = 0;
end:
    if (rgb) { wipe(rgb, total_rgb); free(rgb); }
    if (nv) { wipe(nv, total_nv); free(nv); }
    return result;
}
