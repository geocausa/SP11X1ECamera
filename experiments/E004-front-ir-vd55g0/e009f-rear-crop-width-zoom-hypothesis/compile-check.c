/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "initial-zoom-candidate.h"
int main(void)
{
    float zoom;
    uint32_t bits;
    if (e009f_initial_zoom_candidate(4076, 4064, &zoom)) return 1;
    memcpy(&bits, &zoom, sizeof(bits));
    if (bits != 0x3f7f3f0f) return 2;
    if (e009f_initial_zoom_candidate(4076, 4077, &zoom) == 0 ||
        e009f_initial_zoom_candidate(0, 4064, &zoom) == 0 ||
        e009f_initial_zoom_candidate(4076, 0, &zoom) == 0) return 3;
    printf("0x%08x\n", bits);
    return 0;
}
