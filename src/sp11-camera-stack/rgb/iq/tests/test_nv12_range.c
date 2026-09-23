/* Camera-free exhaustive range and neutral-chroma contract. */
#include "../nv12_range.h"
#include <assert.h>
#include <stdio.h>
int main(void)
{
    assert(sp11_rgb_y_to_video(0)==16);
    assert(sp11_rgb_y_to_video(16)==30);
    assert(sp11_rgb_y_to_video(27)==39);
    assert(sp11_rgb_y_to_video(128)==126);
    assert(sp11_rgb_y_to_video(255)==235);
    assert(sp11_rgb_uv_to_video(0)==16);
    assert(sp11_rgb_uv_to_video(128)==128);
    assert(sp11_rgb_uv_to_video(255)==240);
    for (int v=0;v<=255;v++) {
        assert(sp11_rgb_y_to_video((uint8_t)v)>=16);
        assert(sp11_rgb_y_to_video((uint8_t)v)<=235);
        assert(sp11_rgb_uv_to_video((uint8_t)v)>=16);
        assert(sp11_rgb_uv_to_video((uint8_t)v)<=240);
        if (v>0) {
            assert(sp11_rgb_y_to_video((uint8_t)(v-1))<=
                   sp11_rgb_y_to_video((uint8_t)v));
            assert(sp11_rgb_uv_to_video((uint8_t)(v-1))<=
                   sp11_rgb_uv_to_video((uint8_t)v));
        }
    }
    puts("RGB_NV12_OPTIN_STUDIO_RANGE_OFFLINE_TEST=PASS ALL_256_Y_UV_ENDPOINTS_MONOTONIC");
    return 0;
}
