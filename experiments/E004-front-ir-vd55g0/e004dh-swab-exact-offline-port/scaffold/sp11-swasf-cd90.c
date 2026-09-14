/* SPDX-License-Identifier: MIT */
/*
 * Scalar transcription of the active shipping-Windows SWASF final combine
 * (QcISPTrustlet8380.dll FUN_18001cd90, DAT_18003d23a == 0 path).
 * Live Windows runtime state is normative.  The generated LUTs are exact
 * bytes/dwords from the same shipping DLL and were re-dumped after SWASF proc.
 */
#include "sp11-swasf-cd90.h"
#include "sp11-swasf-cd90-tables.h"

static int32_t clamp32(int32_t v, int32_t lo, int32_t hi)
{
    return v < lo ? lo : (v > hi ? hi : v);
}
static uint32_t urshr32(uint32_t v, unsigned s)
{
    return (v + (1u << (s - 1))) >> s;
}
static int32_t srshr64(int64_t v, unsigned s)
{
    return (int32_t)((v + ((int64_t)1 << (s - 1))) >> s);
}
static int32_t abs32(int32_t v) { return v < 0 ? -v : v; }

void sp11_swasf_cd90(const int16_t p1[8], uint8_t out[8], const uint8_t p3[8],
                     const int16_t p4[8], const int16_t p5[8], const int16_t p6[8],
                     const int16_t p7[8], const int32_t p8[8], const uint8_t p9[8],
                     const int16_t p10[8], const int16_t p11[8], const int16_t p12[8],
                     const uint32_t tune[513])
{
    int i;
    (void)p10; /* shipping runtime DAT_18003d239-DAT_18003d23c == 0 */
    for (i = 0; i < 8; ++i) {
        uint32_t alpha, q, wa, w, mag, x, c, idx, l, diff, z, gain;
        int32_t selected, blended, corr, final;

        /* Live post-proc tables: T0[p9]=0, T1[p9]=1, T2[q]=0. */
        alpha = p3[i];
        q = urshr32((uint32_t)(uint16_t)p11[i] * alpha, 8) & 0xffu;
        mag = (uint32_t)abs32(p8[i]);
        x = mag > 4u ? mag - 4u : 0u;

        wa = urshr32((256u - (tune[256u + q] & 0xffffu)) *
                     (tune[p9[i]] & 0xffffu), 8);
        w = urshr32((uint32_t)(uint16_t)p12[i] * wa, 8);
        if (w > 255u) w = 255u;
        c = (uint32_t)clamp32(srshr64((int64_t)x * w, 7), 0, 1023);

        idx = (uint32_t)(((int32_t)p4[i] + (int32_t)p5[i]) >> 2);
        if (idx > 255u) idx = 255u; /* valid Windows camera domain is 0..255 */

        if (idx != 0u) {
            int32_t bound = p8[i] > 0 ? p4[i] : p5[i];
            selected = bound < (int32_t)c ? bound : (int32_t)c;
            if (selected < 0) selected = 0;

            l = sp11_cd90_small[p9[i]];
            diff = (uint32_t)abs32(((int32_t)p4[i] + p5[i]) -
                                   ((int32_t)p6[i] + p7[i])) >> 2;
            z = diff * (uint32_t)sp11_cd90_large_a[idx] * l;
            z >>= sp11_cd90_large_b[idx];
            gain = z + (256u - l);
            if (gain > 256u) gain = 256u;
            blended = selected + (int32_t)urshr32((uint32_t)((int32_t)c - selected) * gain, 8);
        } else {
            blended = (int32_t)c;
        }

        corr = p8[i] < 0 ? -blended : blended;
        corr = clamp32(corr, -116, 60);
        final = clamp32((int32_t)p1[i] + corr, 0, 1023);
        out[i] = (uint8_t)(final >> 2);
    }
}
