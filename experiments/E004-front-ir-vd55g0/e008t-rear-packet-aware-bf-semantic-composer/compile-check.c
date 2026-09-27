/* SPDX-License-Identifier: MIT */
/* Host-only semantic/type harness for E008t. Never linked into qcom-camss. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>

typedef uint8_t u8;
typedef int8_t s8;
typedef uint16_t u16;
typedef int16_t s16;
typedef uint32_t u32;
typedef int32_t s32;
typedef uint64_t u64;

#define BIT(n) (1U << (n))
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define static_assert _Static_assert
#define __used __attribute__((used))

static inline void put_unaligned_le32(u32 v, void *p)
{
    u8 *d = p;
    d[0] = v;
    d[1] = v >> 8;
    d[2] = v >> 16;
    d[3] = v >> 24;
}

#include "../e007b-rear-bfstats25-calculated-provider/camss-e007b-bfstats25.inc"
#include "../e007e-rear-bfstats25-dmi-provider/camss-e007e-bfstats25-dmi.inc"

/* Only the exact nesting needed to reach E007f::bfstats25. */
struct e007f_rear_dmi_state { struct e007e_bf_dmi_state bfstats25; };
struct e007i_rear_dmi_state { struct e007f_rear_dmi_state dmi; };
struct e007q_rear_dmi_state { struct e007i_rear_dmi_state dmi; };
struct e007s_rear_dmi_state { struct e007q_rear_dmi_state dmi; };
struct e007t_rear_dmi_state { struct e007s_rear_dmi_state dmi; };
struct e007u_rear_dmi_state { struct e007t_rear_dmi_state dmi; };
struct e007v_rear_dmi_state { struct e007u_rear_dmi_state dmi; };

struct e007d_rear_register_state {
    struct e007b_bfstats25_calc_state bfstats;
};

struct e008o_rear_packet_state {
    struct e007d_rear_register_state regs;
    struct e007v_rear_dmi_state dmi;
    bool consumed;
};

struct e008o_rear_bootstrap {
    struct e008o_rear_packet_state packet[4];
    u8 next_packet;
    bool initialized;
};

#include "camss-vfe-e008t-rear-bf-semantic.inc"

static int require(bool ok)
{
    return ok ? 0 : 1;
}

int main(void)
{
    struct e008o_rear_bootstrap s;
    u8 roi[E007E_BF_ROI_BYTES];
    u8 gamma[E007E_BF_GAMMA_BYTES];
    u32 cfg0, cfg1;
    unsigned int i;

    memset(&s, 0, sizeof(s));
    s.initialized = true;

    if (e008t_rear_seed_bootstrap_bf(&s, 4076, 2806))
        return 10;

    for (i = 0; i < 4; i++) {
        struct e007e_bf_dmi_state *d = e008t_rear_bf_dmi(&s.packet[i].dmi);
        if (require(d && d->roi_count == 25))
            return 20 + i;
        if (require(s.packet[i].regs.bfstats.dmi_lut_bank == (i & 1) &&
                    s.packet[i].regs.bfstats.module_lut_bank == (i & 1)))
            return 30 + i;
        memset(roi, 0, sizeof(roi));
        if (e007e_bfstats25_dmi(d, 1, roi, sizeof(roi)))
            return 40 + i;
    }

    if (require(!e008t_rear_bf_dmi(&s.packet[0].dmi)->gamma_valid &&
                s.packet[0].regs.bfstats.signed4[0] == -3 &&
                s.packet[0].regs.bfstats.signed4[1] == 0 &&
                s.packet[0].regs.bfstats.filter0_enable == 1))
        return 50;

    if (e007e_bfstats25_dmi(e008t_rear_bf_dmi(&s.packet[0].dmi),
                            2, gamma, sizeof(gamma)) != -EOPNOTSUPP)
        return 51;

    for (i = 1; i < 4; i++) {
        struct e007e_bf_dmi_state *d = e008t_rear_bf_dmi(&s.packet[i].dmi);
        if (require(d->gamma_valid &&
                    s.packet[i].regs.bfstats.signed4[0] == 3 &&
                    s.packet[i].regs.bfstats.signed4[1] == 3 &&
                    s.packet[i].regs.bfstats.filter0_enable == 0))
            return 60 + i;
        memset(gamma, 0, sizeof(gamma));
        if (e007e_bfstats25_dmi(d, 2, gamma, sizeof(gamma)))
            return 70 + i;
    }

    if (e007b_bfstats25_lookup(&s.packet[0].regs.bfstats, 0xbc60, &cfg0) ||
        e007b_bfstats25_lookup(&s.packet[1].regs.bfstats, 0xbc60, &cfg1))
        return 80;

    if (require(!(cfg0 & BIT(9)) && (cfg0 & BIT(16)) &&
                (cfg0 & BIT(17)) && (cfg0 & BIT(21)) &&
                (cfg1 & BIT(9)) && !(cfg1 & BIT(16)) &&
                (cfg1 & BIT(17)) && (cfg1 & BIT(21))))
        return 81;

    return 0;
}
