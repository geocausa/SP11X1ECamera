// SPDX-License-Identifier: GPL-2.0-only
#include <errno.h>
#include <time.h>
#include <linux/videodev2.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <sys/ioctl.h>

#define CID_IQ   (V4L2_CID_USER_BASE + 0x1240)
#define CID_TLBG (V4L2_CID_USER_BASE + 0x1241)
#define CID_3A   (V4L2_CID_USER_BASE + 0x1242)
#define IQ_BYTES 41088u
#define TLBG_BYTES 0xf020u
#define STATS3A_BYTES 0x51040u

static int ext_get(int fd, uint32_t id, void *buf, size_t n)
{
    struct v4l2_ext_control c = { .id = id, .size = (uint32_t)n, .ptr = buf };
    struct v4l2_ext_controls cs = { .count = 1, .controls = &c };
    if (!buf || n > UINT32_MAX) return -EINVAL;
    if (ioctl(fd, VIDIOC_G_EXT_CTRLS, &cs) < 0) return -errno;
    return 0;
}
int e003i_get_tlbg(int fd, void *buf, size_t n)
{
    if (n != TLBG_BYTES) return -EINVAL;
    return ext_get(fd, CID_TLBG, buf, n);
}
int e003i_get_3a(int fd, void *buf, size_t n)
{
    if (n != STATS3A_BYTES) return -EINVAL;
    return ext_get(fd, CID_3A, buf, n);
}
int e003i_submit_iq(int fd, const void *buf, size_t n)
{
    struct v4l2_ext_control c;
    struct v4l2_ext_controls cs;
    if (!buf || n != IQ_BYTES) return -EINVAL;
    memset(&c, 0, sizeof(c)); memset(&cs, 0, sizeof(cs));
    c.id = CID_IQ; c.size = (uint32_t)n; c.ptr = (void *)buf;
    cs.count = 1; cs.controls = &c;
    if (ioctl(fd, VIDIOC_S_EXT_CTRLS, &cs) < 0) return -errno;
    return 0;
}
