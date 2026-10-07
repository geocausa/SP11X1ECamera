/* SPDX-License-Identifier: GPL-2.0-only */
#include "camss_x1e_helpers.h"

#include <array>
#include <cerrno>
#include <cmath>
#include <limits>
#include <utility>

#include <linux/videodev2.h>

namespace libcamera::ipa {

int camssX1EFrontControls(const e003i_t681_result &exposure,
                         const ControlInfoMap &sensorInfo,
                         ControlList *controls, float *ispGain)
{
    if (!controls || !ispGain)
        return -EINVAL;

    e003i_imx681_controls calculated{};
    if (e003i_imx681_controls_from_t681(&exposure, &calculated))
        return -EINVAL;

    const std::array<std::pair<unsigned int, uint32_t>, 4> values{{
        { V4L2_CID_VBLANK, calculated.vertical_blanking },
        { V4L2_CID_EXPOSURE, calculated.exposure_lines },
        { V4L2_CID_ANALOGUE_GAIN, calculated.analogue_gain_code },
        { V4L2_CID_DIGITAL_GAIN, calculated.digital_gain_code },
    }};

    /* Validate every field before publishing any output. ControlInfoMap
     * describes ranges; even-line quantization comes from the retained helper.
     */
    for (const auto &[id, value] : values) {
        const auto it = sensorInfo.find(id);
        if (it == sensorInfo.end() ||
            it->first->type() != ControlTypeInteger32 ||
            it->first->isArray() ||
            it->second.min().type() != ControlTypeInteger32 ||
            it->second.max().type() != ControlTypeInteger32 ||
            it->second.min().isArray() || it->second.max().isArray())
            return -EINVAL;

        const int64_t minimum = it->second.min().get<int32_t>();
        const int64_t maximum = it->second.max().get<int32_t>();
        if (value > std::numeric_limits<int32_t>::max() ||
            int64_t(value) < minimum || int64_t(value) > maximum)
            return -ERANGE;
    }

    ControlList pending(sensorInfo);
    for (const auto &[id, value] : values)
        pending.set(id, static_cast<int32_t>(value));

    *controls = std::move(pending);
    *ispGain = calculated.isp_gain;
    return 0;
}

int camssX1EFrontLuma(Span<const uint8_t> statistics,
                     uint64_t expectedGeneration, uint32_t expectedSequence,
                     float *luma)
{
    if (!luma || !expectedGeneration || !expectedSequence)
        return -EINVAL;

    e003i_stats3a_view view{};
    if (e003i_stats3a_open(statistics.data(), statistics.size(), &view))
        return -EINVAL;
    if (view.generation != expectedGeneration ||
        view.source_seq != expectedSequence)
        return -ESTALE;

    float pending;
    if (e003i_aecbe_frame_luma(view.aec_raw, &pending) ||
        !std::isfinite(pending) || pending < 0.0f)
        return -EINVAL;

    *luma = pending;
    return 0;
}

int camssX1EFrameLuma(Span<const uint8_t> statistics, uint64_t streamId,
                      uint32_t sequence, uint64_t timestampNs, float *luma)
{
    if (!luma || !timestampNs)
        return -EINVAL;
    int ret = native_front_stats_validate(statistics.data(), statistics.size(),
                                         streamId, sequence);
    if (ret)
        return ret;
    /* V4L2 timeval and libcamera FrameMetadata retain microsecond precision. */
    if (native_front_stats_u64(statistics.data() + 16) / 1000 != timestampNs / 1000)
        return -ESTALE;
    float pending;
    if (e003i_aecbe_frame_luma(statistics.data() + NATIVE_FRONT_STATS_HEADER_BYTES,
                              &pending) || !std::isfinite(pending) || pending < 0.0f)
        return -EINVAL;
    *luma = pending;
    return 0;
}

int camssX1EFrontParameters(uint64_t requestId, uint32_t updateMask,
                           Span<const uint16_t> demuxQ10,
                           Span<const uint32_t> pdpcQ12,
                           Span<const uint16_t> wbQ10,
                           native_front_params *output)
{
    if (!output || demuxQ10.size() != 4 || pdpcQ12.size() != 4 || wbQ10.size() != 2)
        return -EINVAL;
    native_front_params pending{};
    auto *bytes = reinterpret_cast<uint8_t *>(&pending);
    auto put = [bytes](size_t offset, uint64_t value, size_t width) {
        for (size_t i = 0; i < width; ++i)
            bytes[offset + i] = uint8_t(value >> (8*i));
    };
    put(0, NATIVE_FRONT_PARAMS_MAGIC, 4);
    put(4, NATIVE_FRONT_PARAMS_VERSION, 2);
    put(6, NATIVE_FRONT_PARAMS_BYTES, 2);
    put(8, requestId, 8);
    put(16, updateMask, 4);
    for (size_t i = 0; i < 4; ++i) {
        put(24 + 2*i, demuxQ10[i], 2);
        put(32 + 4*i, pdpcQ12[i], 4);
    }
    for (size_t i = 0; i < 2; ++i)
        put(48 + 2*i, wbQ10[i], 2);
    int ret = native_front_params_validate(bytes, sizeof(pending));
    if (ret)
        return ret;
    *output = pending;
    return 0;
}

int camssX1ERearScalars(const e012k_rear_scalar_input &input,
                       e012k_rear_scalar_output *output)
{
    if (!output)
        return -EINVAL;

    e012k_rear_scalar_output pending{};
    if (e012k_rear_scalar_calculate(&input, &pending))
        return -EINVAL;
    *output = pending;
    return 0;
}


int camssX1ERearStartupScalars(Span<const e012k_rear_scalar_input> inputs,
                              Span<const uint64_t> requestIds,
                              native_rear_startup_scalars *output)
{
    if (!output || inputs.size() != NATIVE_REAR_SCALARS_PACKETS ||
        requestIds.size() != NATIVE_REAR_SCALARS_PACKETS)
        return -EINVAL;
    native_rear_startup_scalars pending{};
    auto put = [&pending](size_t offset, uint64_t value, size_t width) {
        for (size_t i = 0; i < width; ++i)
            pending.data[offset + i] = uint8_t(value >> (8 * i));
    };
    put(0, NATIVE_REAR_SCALARS_MAGIC, 4);
    put(4, NATIVE_REAR_SCALARS_VERSION, 2);
    put(6, NATIVE_REAR_SCALARS_BYTES, 2);
    put(8, NATIVE_REAR_SCALARS_PACKETS, 4);
    for (size_t p = 0; p < NATIVE_REAR_SCALARS_PACKETS; ++p) {
        e012k_rear_scalar_output scalar{};
        int ret = camssX1ERearScalars(inputs[p], &scalar);
        if (ret)
            return ret;
        const size_t offset = 16 + p * NATIVE_REAR_SCALARS_SLOT_BYTES;
        put(offset, requestIds[p], 8);
        put(offset + 8, p, 4);
        for (size_t i = 0; i < 4; ++i) {
            put(offset + 16 + 2 * i, scalar.demux_q10[i], 2);
            put(offset + 24 + 4 * i, scalar.pdpc_q12[i], 4);
        }
        put(offset + 40, scalar.wb_b_q10, 2);
        put(offset + 42, scalar.wb_r_q10, 2);
    }
    int ret = native_rear_scalars_validate(pending.data, sizeof(pending));
    if (ret)
        return ret;
    *output = pending;
    return 0;
}

} /* namespace libcamera::ipa */
