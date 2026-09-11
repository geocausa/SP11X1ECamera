// SPDX-License-Identifier: GPL-2.0-only
#ifndef E003I_DX_GAIN_FEED_H
#define E003I_DX_GAIN_FEED_H
#include <stdint.h>
#define E003I_GAIN_FEED_MAGIC UINT32_C(0x31464749) /* bytes: I G F 1 */
#define E003I_GAIN_FEED_VERSION UINT16_C(1)
#define E003I_GAIN_FEED_RECORD_BYTES UINT16_C(24)
struct e003i_gain_feed_record {
    uint32_t magic;
    uint16_t version;
    uint16_t bytes;
    uint32_t generation;
    uint32_t request;
    uint32_t isp_gain_bits;
    uint32_t reserved;
};
_Static_assert(sizeof(struct e003i_gain_feed_record) == 24, "gain-feed ABI size");
int e003i_gain_feed_publish(int fd, uint32_t generation, uint32_t request, float isp_gain);
#endif
