/* SPDX-License-Identifier: MIT */
#include "e004pt-observer-model.h"
#include <assert.h>
#include <stdio.h>
#include <inttypes.h>

int main(void)
{
    struct e004pt_model m = {0};
    uint64_t expected = 0, checks = 0;
    for (unsigned int id = 0; id < 2; ++id)
        for (unsigned int lite = 0; lite < 2; ++lite)
            for (uint32_t value = 0; value <= 65535u; ++value) {
                uint64_t prior = m.count;
                uint32_t old_status = m.last_status;
                bool should = id == 1 && lite == 0 &&
                              (value & E004PT_BF_BIT) != 0;
                bool observed = e004pt_observe(&m, id, lite != 0, value);
                assert(observed == should);
                assert(m.count == prior + (should ? 1u : 0u));
                assert(m.last_status == (should ? value : old_status));
                if (should) ++expected;
                ++checks;
            }
    assert(checks == 262144u);
    assert(expected == 32768u && m.count == expected);
    assert(m.ever_seen && m.last_status == 0xffffu);
    /* A status bit, even observed on the correct CSID, is not a WM16 fence. */
    assert(!e004pt_observe(NULL, 1, false, E004PT_BF_BIT));
    assert(!e004pt_observe(&m, 0, false, E004PT_BF_BIT));
    assert(!e004pt_observe(&m, 1, true, E004PT_BF_BIT));
    assert(m.count == expected);
    puts("PASS_E004PT_OFFLINE_262144_STATUS_DOMAIN_CASES_32768_BF_OBSERVATIONS_NO_DMA_RETIRE");
    return 0;
}
