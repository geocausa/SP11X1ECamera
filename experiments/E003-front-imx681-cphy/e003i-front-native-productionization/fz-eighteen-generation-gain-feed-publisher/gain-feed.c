// SPDX-License-Identifier: GPL-2.0-only
#include "gain-feed.h"
#include <errno.h>
#include <math.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>

int e003i_gain_feed_publish(int fd, uint32_t generation, uint32_t request, float isp_gain)
{
    struct e003i_gain_feed_record r = {0};
    const unsigned char *p = (const unsigned char *)&r;
    size_t left = sizeof(r);
    uint32_t bits;

#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error DX gain feed requires little-endian host
#endif
    if (fd < 0 || generation < 1U || generation > 18U || request != generation + 3U ||
        !isfinite(isp_gain) || !(isp_gain > 0.0f))
        return -EINVAL;
    memcpy(&bits, &isp_gain, sizeof(bits));
    r.magic = E003I_GAIN_FEED_MAGIC;
    r.version = E003I_GAIN_FEED_VERSION;
    r.bytes = E003I_GAIN_FEED_RECORD_BYTES;
    r.generation = generation;
    r.request = request;
    r.isp_gain_bits = bits;

    while (left) {
        ssize_t n = write(fd, p, left);
        if (n < 0 && errno == EINTR)
            continue;
        if (n <= 0)
            return n < 0 ? -errno : -EIO;
        p += (size_t)n;
        left -= (size_t)n;
    }
    return 0;
}
