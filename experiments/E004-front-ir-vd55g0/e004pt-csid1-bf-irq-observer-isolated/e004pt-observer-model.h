/* SPDX-License-Identifier: MIT */
/* E004pt offline observer: status-only predicate, NEVER a DMA fence. */
#ifndef E004PT_OBSERVER_MODEL_H
#define E004PT_OBSERVER_MODEL_H
#include <stdbool.h>
#include <stdint.h>
#define E004PT_BF_BIT (UINT32_C(1) << 7)
struct e004pt_model {
    uint64_t count;
    uint32_t last_status;
    bool ever_seen;
};
static inline bool e004pt_observe(struct e004pt_model *m, unsigned int csid_id,
                                  bool is_lite, uint32_t already_latched_status)
{
    if (!m || csid_id != 1 || is_lite ||
        !(already_latched_status & E004PT_BF_BIT))
        return false;
    m->last_status = already_latched_status;
    m->count++;
    m->ever_seen = true;
    return true;
}
/* Deliberately no buffer identity, VB2, DMA, IRQ ACK, or arm API. */
#endif
