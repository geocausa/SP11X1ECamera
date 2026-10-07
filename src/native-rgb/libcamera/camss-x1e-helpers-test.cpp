/* SPDX-License-Identifier: GPL-2.0-only */
#include <array>
#include <cerrno>
#include <cmath>
#include <cstring>
#include <iostream>
#include <limits>
#include <vector>

#include <linux/videodev2.h>
#include "camera_sensor_helper.h"
#include "camss_x1e_helpers.h"
#include "test.h"

using namespace libcamera;
using namespace libcamera::ipa;

namespace {

const Control<int32_t> blank(V4L2_CID_VBLANK, "VBlank", "v4l2", ControlId::Direction::In);
const Control<int32_t> exposure(V4L2_CID_EXPOSURE, "Exposure", "v4l2", ControlId::Direction::In);
const Control<int32_t> analogue(V4L2_CID_ANALOGUE_GAIN, "AnalogueGain", "v4l2", ControlId::Direction::In);
const Control<int32_t> digital(V4L2_CID_DIGITAL_GAIN, "DigitalGain", "v4l2", ControlId::Direction::In);
const ControlIdMap ids{
    { blank.id(), &blank }, { exposure.id(), &exposure },
    { analogue.id(), &analogue }, { digital.id(), &digital },
};

void le(std::vector<uint8_t> &bytes, size_t offset, uint64_t value, size_t width)
{
    for (size_t i = 0; i < width; ++i)
        bytes[offset + i] = uint8_t(value >> (8 * i));
}

} /* namespace */

class CamssX1EHelpersTest : public Test
{
protected:
    int run() override
    {
        auto helper = CameraSensorHelperFactoryBase::create("imx681");
        if (!helper || helper->blackLevel()) {
            std::cerr << "IMX681 registration or unknown-black-level policy failed\n";
            return TestFail;
        }
        const std::array<std::pair<uint32_t, double>, 5> points{{
            { 0, 1.0 }, { 512, 2.0 }, { 768, 4.0 },
            { 896, 8.0 }, { 960, 16.0 },
        }};
        for (const auto &[code, gain] : points) {
            if (helper->gainCode(gain) != code ||
                std::abs(helper->gain(code) - gain) > 1e-12)
                return TestFail;
        }

        const ControlInfoMap info({
            { &blank, ControlInfo(1394, 0xffffff - 2160, 1394) },
            { &exposure, ControlInfo(4, 0xfffffa, 3546) },
            { &analogue, ControlInfo(0, 960, 0) },
            { &digital, ControlInfo(256, 3840, 256) },
        }, ids);
        ControlList controls(info);
        float ispGain = -1.0f;
        e003i_t681_result request{};
        request.gain = 2.0f;
        request.exposure_time_ns = 9379103;
        if (camssX1EFrontControls(request, info, &controls, &ispGain) ||
            controls.size() != 4 ||
            controls.get(blank) != 1394 || controls.get(exposure) != 1000 ||
            controls.get(analogue) != 512 || controls.get(digital) != 256 ||
            ispGain != 1.0f)
            return TestFail;

        request.gain = 32.0f;
        request.exposure_time_ns = 66666664;
        if (camssX1EFrontControls(request, info, &controls, &ispGain) ||
            controls.get(blank) != 4956 || controls.get(exposure) != 7108 ||
            controls.get(analogue) != 960 || controls.get(digital) != 512 ||
            ispGain != 1.0f)
            return TestFail;

        const auto savedExposure = controls.get(exposure);
        request.gain = std::numeric_limits<float>::quiet_NaN();
        if (camssX1EFrontControls(request, info, &controls, &ispGain) != -EINVAL ||
            controls.get(exposure) != savedExposure || ispGain != 1.0f)
            return TestFail;
        request.gain = 2.0f;
        request.exposure_time_ns = 9379103;
        const ControlInfoMap limited({
            { &blank, info.at(blank.id()) },
            { &exposure, ControlInfo(4, 998, 4) },
            { &analogue, info.at(analogue.id()) },
            { &digital, info.at(digital.id()) },
        }, ids);
        if (camssX1EFrontControls(request, limited, &controls, &ispGain) != -ERANGE ||
            controls.get(exposure) != savedExposure || ispGain != 1.0f)
            return TestFail;
        const ControlInfoMap missing({
            { &blank, info.at(blank.id()) },
            { &exposure, info.at(exposure.id()) },
            { &analogue, info.at(analogue.id()) },
        }, ids);
        if (camssX1EFrontControls(request, missing, &controls, &ispGain) != -EINVAL ||
            controls.get(exposure) != savedExposure)
            return TestFail;

        e012k_rear_scalar_input rear{};
        rear.demux_gain = rear.awb_g = rear.awb_b = rear.awb_r = rear.predictive_gain = 1.0f;
        rear.bayer = 2;
        for (float &channel : rear.channel)
            channel = 1.0f;
        e012k_rear_scalar_output scalar{};
        if (camssX1ERearScalars(rear, &scalar))
            return TestFail;
        for (uint16_t value : scalar.demux_q10)
            if (value != 1024)
                return TestFail;
        for (uint32_t value : scalar.pdpc_q12)
            if (value != 4096)
                return TestFail;
        if (scalar.wb_b_q10 != 1024 || scalar.wb_r_q10 != 1024)
            return TestFail;
        rear.awb_b = 2.0f;
        rear.awb_r = 1.5f;
        if (camssX1ERearScalars(rear, &scalar) ||
            scalar.wb_b_q10 != 2048 || scalar.wb_r_q10 != 1536 ||
            scalar.pdpc_q12[0] != 6144 || scalar.pdpc_q12[1] != 8192 ||
            scalar.pdpc_q12[2] != 2731 || scalar.pdpc_q12[3] != 2048)
            return TestFail;
        const auto savedScalar = scalar;
        rear.awb_b = std::numeric_limits<float>::infinity();
        if (camssX1ERearScalars(rear, &scalar) != -EINVAL ||
            std::memcmp(&savedScalar, &scalar, sizeof(scalar)))
            return TestFail;
        rear.awb_b = 2.0f;
        rear.demux_gain = 1.0f;
        rear.channel[3] = 100000.0f; /* Fail after earlier demux fields were calculated. */
        if (camssX1ERearScalars(rear, &scalar) != -EINVAL ||
            std::memcmp(&savedScalar, &scalar, sizeof(scalar)))
            return TestFail;

        std::vector<uint8_t> stats(E003I_STATS3A_BYTES);
        le(stats, 0, E003I_STATS3A_MAGIC, 4);
        le(stats, 4, 1, 2);
        le(stats, 6, E003I_STATS3A_HEADER_BYTES, 2);
        le(stats, 8, 17, 8);
        le(stats, 16, 12, 4);
        le(stats, 20, 0, 4);
        le(stats, 28, E003I_STATS3A_AEC_BYTES, 4);
        le(stats, 32, E003I_STATS3A_AEC_BYTES, 4);
        le(stats, 36, E003I_STATS3A_BHIST_BYTES, 4);
        le(stats, 40, E003I_STATS3A_AEC_BYTES + E003I_STATS3A_BHIST_BYTES, 4);
        le(stats, 44, E003I_STATS3A_AWB_BYTES, 4);
        le(stats, 48, 1, 4);
        for (size_t region = 0; region < 1024; ++region)
            for (size_t offset : { 0x06, 0x0e, 0x16, 0x1e })
                le(stats, E003I_STATS3A_HEADER_BYTES + region * 0x50 + offset, 1980, 2);
        float luma = 42.0f;
        if (camssX1EFrontLuma(stats, 17, 12, &luma) || luma != 0.0f)
            return TestFail;
        /* A nonzero uniform grid also exercises the byte parser and the
         * metering reduction; zero alone would miss arithmetic regressions.
         */
        for (size_t region = 0; region < 1024; ++region)
            for (size_t offset : { 0x00, 0x08, 0x10, 0x18 })
                le(stats, E003I_STATS3A_HEADER_BYTES + region * 0x50 + offset,
                   100000000, 5);
        if (camssX1EFrontLuma(stats, 17, 12, &luma) ||
            std::abs(luma - 49.32134f) > 0.001f)
            return TestFail;
        luma = 42.0f;
        if (camssX1EFrontLuma(stats, 18, 12, &luma) != -ESTALE || luma != 42.0f ||
            camssX1EFrontLuma(stats, 17, 13, &luma) != -ESTALE || luma != 42.0f ||
            camssX1EFrontLuma(Span<const uint8_t>(stats.data(), stats.size() - 1),
                               17, 12, &luma) != -EINVAL || luma != 42.0f)
            return TestFail;
        std::vector<uint8_t> frame(NATIVE_FRONT_STATS_BYTES);
        le(frame, 0, NATIVE_FRONT_STATS_MAGIC, 4);
        le(frame, 4, 1, 2);
        le(frame, 6, NATIVE_FRONT_STATS_HEADER_BYTES, 2);
        le(frame, 8, 71, 8);
        le(frame, 16, 1000000999, 8);
        le(frame, 24, 0, 4); /* First video buffer is sequence zero. */
        le(frame, 28, 19, 4);
        le(frame, 44, NATIVE_FRONT_STATS_AEC_BYTES, 4);
        le(frame, 48, NATIVE_FRONT_STATS_BHIST_BYTES, 4);
        le(frame, 52, NATIVE_FRONT_STATS_AWB_BYTES, 4);
        le(frame, 56, NATIVE_FRONT_STATS_TLBG_BYTES, 4);
        std::copy(stats.begin() + E003I_STATS3A_HEADER_BYTES, stats.end(),
                  frame.begin() + NATIVE_FRONT_STATS_HEADER_BYTES);
        if (camssX1EFrameLuma(frame, 71, 0, 1000000000, &luma) ||
            std::abs(luma - 49.32134f) > 0.001f)
            return TestFail;
        luma = 42.0f;
        if (camssX1EFrameLuma(frame, 72, 0, 1000000000, &luma) != -ESTALE ||
            camssX1EFrameLuma(frame, 71, 1, 1000000000, &luma) != -ESTALE ||
            camssX1EFrameLuma(frame, 71, 0, 1000001000, &luma) != -ESTALE ||
            luma != 42.0f)
            return TestFail;
        le(frame, 40, NATIVE_FRONT_STATS_F_DISCONTINUITY, 4);
        if (camssX1EFrameLuma(frame, 71, 0, 1000000000, &luma) != -EPIPE ||
            luma != 42.0f)
            return TestFail;
        le(frame, 40, 0, 4);
        le(frame, 44, NATIVE_FRONT_STATS_AEC_BYTES - 1, 4);
        if (camssX1EFrameLuma(frame, 71, 0, 1000000000, &luma) != -EINVAL ||
            luma != 42.0f)
            return TestFail;
        le(stats, E003I_STATS3A_HEADER_BYTES + 0x06, 0, 2);
        if (camssX1EFrontLuma(stats, 17, 12, &luma) != -EINVAL || luma != 42.0f)
            return TestFail;

        const std::array<uint16_t, 4> demuxQ10{1024, 2048, 4096, 8192};
        const std::array<uint32_t, 4> pdpcQ12{8192, 6144, 2048, 2731};
        const std::array<uint16_t, 2> wbQ10{1536, 2048};
        native_front_params parameters{};
        if (camssX1EFrontParameters(81, 7, demuxQ10, pdpcQ12, wbQ10, &parameters) ||
            native_front_params_validate(&parameters, sizeof(parameters)))
            return TestFail;
        const auto savedParameters = parameters;
        if (camssX1EFrontParameters(4, 7, demuxQ10, pdpcQ12, wbQ10, &parameters) != -ERANGE ||
            camssX1EFrontParameters(81, 4, demuxQ10, pdpcQ12, wbQ10, &parameters) != -EINVAL ||
            std::memcmp(&savedParameters, &parameters, sizeof(parameters)))
            return TestFail;
        auto invalidGains = demuxQ10;
        invalidGains[0] = 32768;
        if (camssX1EFrontParameters(81, 7, invalidGains, pdpcQ12, wbQ10, &parameters) != -ERANGE ||
            std::memcmp(&savedParameters, &parameters, sizeof(parameters)))
            return TestFail;

        std::cout << "PASS: registered gain helper, atomic four-field controls, "
                     "range admission, rear scalar forwarding, stats identity and error preservation\n";
        return TestPass;
    }
};

TEST_REGISTER(CamssX1EHelpersTest)
