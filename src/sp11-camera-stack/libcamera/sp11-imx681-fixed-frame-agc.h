/* SPDX-License-Identifier: MIT
 * E004lu: source-only IMX681 fixed-30fps frame-length contract.
 * These constants are tied to the independently physically accepted
 * E004le 3840x2160 sensor mode, not all future IMX681 modes.
 */
#pragma once
#include <algorithm>
#include <cstdint>
#include <optional>

namespace sp11 {
struct Imx681FixedFrameAgc {
    static constexpr uint32_t kHeight = 2160;
    static constexpr uint32_t kFrameLength = 3554;
    static constexpr int32_t kExposureMinimum = 4;
    static constexpr int32_t kExposureMargin = 4;
    static constexpr int32_t kExposureStep = 2;

    static std::optional<int32_t> exposureMaximum(uint32_t height,
                                                   uint32_t frameLength,
                                                   int32_t advertisedMinimum,
                                                   int32_t advertisedMaximum)
    {
        /* Do not extrapolate into an unvalidated alternate sensor mode
         * or assume the very large hardware MAX is active VBLANK.
         */
        if (height != kHeight || frameLength != kFrameLength ||
            advertisedMinimum != kExposureMinimum ||
            advertisedMaximum < kExposureMinimum ||
            advertisedMaximum < static_cast<int32_t>(kFrameLength - kExposureMargin))
            return std::nullopt;
        return static_cast<int32_t>(kFrameLength - kExposureMargin);
    }

    static int32_t quantize(int32_t proposed, int32_t activeMaximum)
    {
        /* Preconditions: admission checked exposureMaximum() and no
         * dynamic frame-length/VBLANK change was made after admission.
         */
        const int32_t maximum = std::clamp(activeMaximum,
                                          kExposureMinimum,
                                          static_cast<int32_t>(
                                              kFrameLength-kExposureMargin));
        const int32_t bounded = std::clamp(proposed, kExposureMinimum,
                                          maximum);
        return kExposureMinimum +
               ((bounded-kExposureMinimum)/kExposureStep)*kExposureStep;
    }
};
} /* namespace sp11 */
