/* SPDX-License-Identifier: MIT
 * Offline numerical verification only; physical ERANGE source remains to
 * be confirmed in a fresh guarded one-shot after integration.
 */
#include "../sp11-imx681-fixed-frame-agc.h"
#include <cassert>
#include <iostream>

int main()
{
    using G = sp11::Imx681FixedFrameAgc;
    auto max = G::exposureMaximum(2160, 3554, 4, 16777210);
    assert(max && *max == 3550);
    assert(!G::exposureMaximum(2160, 3555, 4, 16777210));
    assert(!G::exposureMaximum(2159, 3554, 4, 16777210));
    assert(!G::exposureMaximum(2160, 3554, 0, 16777210));
    assert(!G::exposureMaximum(2160, 3554, 4, 3549));
    assert(G::quantize(3546, *max) == 3546);
    assert(G::quantize(3900, *max) == 3550);
    assert(G::quantize(3551, *max) == 3550);
    assert(G::quantize(3549, *max) == 3548);
    assert(G::quantize(5, *max) == 4);
    assert(G::quantize(-1, *max) == 4);
    assert(G::quantize(16777210, *max) == 3550);
    for (int requested = -3; requested < 4000; requested++) {
        int actual = G::quantize(requested, *max);
        assert(actual >= 4 && actual <= 3550);
        assert((actual - 4) % 2 == 0);
        assert(actual <= (int)G::kFrameLength-G::kExposureMargin);
    }
    std::cout << "PASS E004lu fixed 3554-line IMX681 mode: "
                 "active-frame exposure max 3550, 2-line quantization, "
                 "unknown modes fail closed; numeric test only\n";
}
