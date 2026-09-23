/* SPDX-License-Identifier: MIT
 * Camera-free exact candidate string-positive/negative acceptance.
 * No camera function is invoked, no device access or OS sleep.
 */
#define SP11_RGB_NV12_VIDEO_RANGE 1
#define SP11_RGB_NV12_BT601_TAG 1
#define E004KQ_NO_MAIN
#if defined(SP11_TOKEN_CHECK_FRONT)
#define SP11_RGB_FRONT_PREVIEW_TONE 1
#include "front-direct-publisher.c"
#elif defined(SP11_TOKEN_CHECK_REAR)
/* Source-only token test must satisfy the exact opt-in rear compile guard.
 * The normal build and front test remain explicitly tone disabled. */
#define SP11_RGB_REAR_PREVIEW_TONE 1
#define SP11_CAMERA_ALLOW_TEMPORAL_RAW10 1
#define SP11_CAMERA_ALLOW_REAR_TEMPORAL_PREVIEW 1
#define SP11_REAR_TEMPORAL_ENABLE_NEON 1
#define SP11_CAMERA_ALLOW_RAW_PROFILE 1
#include "rear-direct-publisher.c"
#else
#error BOOT_TOKEN_TEST_CAMERA_MISSING
#endif
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(token_allowed("sp11_camera_e004nh_rgb_session=1"));
    assert(token_allowed("quiet sp11_camera_e004nh_rgb_session=1 root=UUID=fake"));
    assert(!token_allowed(""));
    assert(!token_allowed("sp11_camera_e004me_rgb_session=1"));
    assert(!token_allowed("sp11_camera_e004nh_rgb_session=2"));
    assert(!token_allowed("xsp11_camera_e004nh_rgb_session=1"));
    assert(!token_allowed("sp11_camera_e004nh_rgb_session=1x"));
    assert(!token_allowed("prefix_sp11_camera_e004nh_rgb_session=1"));
    puts("E004NH_EXACT_BOOT_TOKEN_COMPILED_AND_CHECKED=PASS NO_CAMERA_ACCESS");
    return 0;
}
