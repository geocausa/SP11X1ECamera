/* SPDX-License-Identifier: MIT */
/*
 * E004gc: bounded, OFFLINE, unprotected IR image-signal telemetry.
 * No camera, LEDs, enrollment, face matching, login or stored image output.
 * Input: 1..16 exact 644x604 NV12 frames, neutral UV (128).
 * Output: aggregate luma statistics only, after entire batch validates.
 */
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { W = 644, H = 604, MAX_FRAMES = 16 };
#define Y_BYTES ((size_t)W * (size_t)H)
#define FRAME_BYTES (Y_BYTES + Y_BYTES / 2u)

static void wipe(void *ptr, size_t length)
{
    volatile unsigned char *p = ptr;
    while (length--)
        *p++ = 0;
}

static int parse_count(int argc, char **argv, size_t *out)
{
    char *end = NULL;
    unsigned long n;
    if (argc == 1) { *out = 1; return 0; }
    if (argc != 3 || strcmp(argv[1], "--frames") ||
        argv[2][0] < '0' || argv[2][0] > '9')
        return -1;
    errno = 0;
    n = strtoul(argv[2], &end, 10);
    if (errno || !end || *end || !n || n > MAX_FRAMES)
        return -1;
    *out = (size_t)n;
    return 0;
}

static unsigned int percentile(const size_t hist[256], size_t rank)
{
    size_t seen = 0;
    unsigned int i;
    for (i = 0; i < 256; i++) {
        seen += hist[i];
        if (seen >= rank)
            return i;
    }
    return 255; /* unreachable for nonempty frames */
}

static void frame_metrics(const uint8_t *y, size_t index)
{
    size_t hist[256] = {0};
    uint64_t sum = 0, neighbor_diff = 0;
    size_t low = 0, high = 0, edges = 0;
    size_t x, row;
    unsigned int p10, p90;
    for (row = 0; row < H; row++) {
        for (x = 0; x < W; x++) {
            const size_t at = row * W + x;
            unsigned int v = y[at];
            hist[v]++;
            sum += v;
            low += v <= 15;
            high += v >= 240;
            if (x) {
                unsigned int prev = y[at - 1];
                neighbor_diff += v > prev ? v - prev : prev - v;
                edges++;
            }
            if (row) {
                unsigned int prev = y[at - W];
                neighbor_diff += v > prev ? v - prev : prev - v;
                edges++;
            }
        }
    }
    p10 = percentile(hist, (Y_BYTES + 9u) / 10u);
    p90 = percentile(hist, (9u * Y_BYTES + 9u) / 10u);
    printf("%s{\"frame\":%zu,\"mean_milli\":%llu,\"p10\":%u,\"p90\":%u,"
           "\"dark_0_15_permille\":%llu,\"bright_240_255_permille\":%llu,"
           "\"neighbor_abs_diff_milli\":%llu}",
           index ? "," : "", index + 1,
           (unsigned long long)((sum * 1000u + Y_BYTES / 2u) / Y_BYTES),
           p10, p90,
           (unsigned long long)((low * 1000u + Y_BYTES / 2u) / Y_BYTES),
           (unsigned long long)((high * 1000u + Y_BYTES / 2u) / Y_BYTES),
           (unsigned long long)((neighbor_diff * 1000u + edges / 2u) / edges));
    wipe(hist, sizeof(hist));
}

int main(int argc, char **argv)
{
    uint8_t *batch = NULL;
    size_t count, total, i, j;
    int rc = 1;
    if (parse_count(argc, argv, &count)) {
        fputs("usage: sp11-ir-signal-metrics [--frames 1..16]\n", stderr);
        return 2;
    }
    total = count * FRAME_BYTES; /* bounded by MAX_FRAMES */
    batch = malloc(total);
    if (!batch) {
        fputs("allocation failed\n", stderr);
        return 1;
    }
    if (fread(batch, 1, total, stdin) != total ||
        fgetc(stdin) != EOF || ferror(stdin)) {
        fputs("invalid NV12 batch length/read error\n", stderr);
        goto done;
    }
    for (i = 0; i < count; i++) {
        const uint8_t *uv = batch + i * FRAME_BYTES + Y_BYTES;
        for (j = 0; j < Y_BYTES / 2u; j++) {
            if (uv[j] != 128) {
                fputs("non-neutral NV12 chroma rejected\n", stderr);
                goto done;
            }
        }
    }
    fputs("{\"kind\":\"unprotected-offline-signal-telemetry\","
          "\"face_authentication_proven\":false,"
          "\"frames\":[", stdout);
    for (i = 0; i < count; i++)
        frame_metrics(batch + i * FRAME_BYTES, i);
    puts("]}");
    if (fflush(stdout) != 0)
        goto done;
    rc = 0;
done:
    wipe(batch, total);
    free(batch);
    return rc;
}
