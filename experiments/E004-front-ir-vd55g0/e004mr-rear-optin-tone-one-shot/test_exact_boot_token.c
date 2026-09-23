/* SPDX-License-Identifier: MIT
 * Camera-free exact candidate string-positive/negative acceptance.
 * No camera function is invoked, no device access or OS sleep.
 */
#define SP11_RGB_NV12_VIDEO_RANGE 1
#define E004KQ_NO_MAIN
#if defined(SP11_TOKEN_CHECK_FRONT)
#include "front-direct-publisher.c"
#elif defined(SP11_TOKEN_CHECK_REAR)
#include "rear-direct-publisher.c"
#else
#error BOOT_TOKEN_TEST_CAMERA_MISSING
#endif
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(token_allowed("sp11_camera_e004mr_rgb_session=1"));
    assert(token_allowed("quiet sp11_camera_e004mr_rgb_session=1 root=UUID=fake"));
    assert(!token_allowed(""));
    assert(!token_allowed("sp11_camera_e004me_rgb_session=1"));
    assert(!token_allowed("sp11_camera_e004mr_rgb_session=2"));
    assert(!token_allowed("xsp11_camera_e004mr_rgb_session=1"));
    assert(!token_allowed("sp11_camera_e004mr_rgb_session=1x"));
    assert(!token_allowed("prefix_sp11_camera_e004mr_rgb_session=1"));
    puts("E004MR_EXACT_BOOT_TOKEN_COMPILED_AND_CHECKED=PASS NO_CAMERA_ACCESS");
    return 0;
}
