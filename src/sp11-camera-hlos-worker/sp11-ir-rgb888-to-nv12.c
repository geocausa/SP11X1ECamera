/* SPDX-License-Identifier: MIT */
/*
 * Offline format bridge for the proven E004fe 644x604 neutral RGB888 frames.
 * Accept exactly one frame with 1936 bytes/row (4 zero padding bytes/row).
 * Produce contiguous 644x604 NV12: copy grayscale luma, neutral chroma.
 * This does not access camera hardware or perform identity authentication.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { WIDTH = 644, HEIGHT = 604, RGB_STRIDE = 1936 };
static void wipe(void *ptr, size_t len)
{
    volatile unsigned char *p = (volatile unsigned char *)ptr;
    while (len--) *p++ = 0;
}
int main(void)
{
    const size_t ybytes = (size_t)WIDTH * HEIGHT;
    const size_t rgbbytes = (size_t)RGB_STRIDE * HEIGHT;
    const size_t nvbytes = ybytes + ybytes / 2;
    uint8_t *rgb = malloc(rgbbytes), *nv = malloc(nvbytes);
    size_t row, col;
    int result = 1;

    if (!rgb || !nv) {
        fputs("allocation failure\n", stderr);
        goto end;
    }
    if (fread(rgb, 1, rgbbytes, stdin) != rgbbytes ||
        fgetc(stdin) != EOF || ferror(stdin)) {
        fputs("expected exactly one 644x604 RGB888 frame, stride 1936\n", stderr);
        goto end;
    }
    for (row = 0; row < HEIGHT; row++) {
        const uint8_t *src = rgb + row * RGB_STRIDE;
        for (col = 0; col < WIDTH; col++) {
            size_t off = col * 3;
            if (src[off] != src[off + 1] || src[off] != src[off + 2]) {
                fputs("non-neutral RGB888 pixel: unexpected capture format\n", stderr);
                goto end;
            }
            nv[row * WIDTH + col] = src[off];
        }
        for (col = WIDTH * 3; col < RGB_STRIDE; col++)
            if (src[col] != 0) {
                fputs("nonzero RGB888 row padding\n", stderr);
                goto end;
            }
    }
    for (col = ybytes; col < nvbytes; col++)
        nv[col] = 128;
    if (fwrite(nv, 1, nvbytes, stdout) != nvbytes || fflush(stdout)) {
        fputs("NV12 output failure\n", stderr);
        goto end;
    }
    result = 0;
end:
    if (rgb) { wipe(rgb, rgbbytes); free(rgb); }
    if (nv) { wipe(nv, nvbytes); free(nv); }
    return result;
}
