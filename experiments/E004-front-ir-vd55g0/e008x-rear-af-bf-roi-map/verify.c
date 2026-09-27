/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include "af-bf-roi-map.h"

int main(void)
{
    struct e008x_roi r[25];
    struct e008x_rect input = {700, 221, 520, 365};
    unsigned int row, col;

    assert(e008x_normal_roi_map(input, r) == 0);
    for (row = 0; row < 5; row++) {
        for (col = 0; col < 5; col++) {
            struct e008x_roi *v = &r[row * 5 + col];

            assert(v->left == 700 + col * 104);
            assert(v->top == ((221 + row * 73) & ~1U));
            assert(v->width == 103);
            assert(v->height == 71);
        }
    }
    assert(e008x_normal_roi_map((struct e008x_rect){0,0,0,0}, r) != 0);
    puts("E008X_SOURCE_MAP_SYNTHETIC_PASS");
    return 0;
}
