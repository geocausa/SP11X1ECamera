/* SPDX-License-Identifier: GPL-2.0-only */
#pragma once

#include <array>
#include <cstdint>
#include <libcamera/base/span.h>
#include <libcamera/controls.h>
#include <libcamera/geometry.h>

extern "C" {
#include "native-imx681-control.h"
#include "native-stats3a.h"
#include "native-front-stats.h"
#include "native-front-params.h"
#include "rear-neutral-scalar.h"
#include "native-rear-startup-scalars.h"
}

namespace libcamera::ipa {

/* No device access. The caller owns request scheduling and applies this list
 * as one extended-control transaction, preserving the sensor's atomic cluster.
 * The sensor info map must outlive the returned ControlList.
 */
int camssX1EFrontControls(const e003i_t681_result &exposure,
                         const ControlInfoMap &sensorInfo,
                         ControlList *controls, float *ispGain);

/* Existing bounded-front stats envelope, not a new public kernel ABI.
 * The pipeline supplies its expected identity; stale observations are rejected.
 */
int camssX1EFrontLuma(Span<const uint8_t> statistics,
                     uint64_t expectedGeneration, uint32_t expectedSequence,
                     float *luma);

/* Exact per-frame metadata, including stream and pixel timestamp admission. */
int camssX1EFrameLuma(Span<const uint8_t> statistics, uint64_t streamId,
                      uint32_t sequence, uint64_t timestampNs, float *luma);

/* Encode caller-owned quantized scalar values. Outputs are atomic on error. */
int camssX1EFrontParameters(uint64_t requestId, uint32_t updateMask,
                           Span<const uint16_t> demuxQ10,
                           Span<const uint32_t> pdpcQ12,
                           Span<const uint16_t> wbQ10,
                           native_front_params *output);

/* Pure quantized ISP state from caller-owned semantic inputs. */
int camssX1ERearScalars(const e012k_rear_scalar_input &input,
                       e012k_rear_scalar_output *output);


/* Internal startup scalar envelope for four caller-owned semantic inputs.
 * Explicit request IDs are preserved, including a repeated ID across phases.
 * No full rear bootstrap, kernel public ABI or hardware access is implied.
 */
int camssX1ERearStartupScalars(Span<const e012k_rear_scalar_input> inputs,
                              Span<const uint64_t> requestIds,
                              native_rear_startup_scalars *output);


/* Caller-owned AF policy. No request-dependent zoom or tuning is inferred. */
struct CamssX1ERearAfInput {
    Size active;
    float widthFraction, heightFraction, modeScale;
    float zoom, pdWidthScale, pdHeightScale;
    bool alternateMode, pdScaleEnabled, sparsePd;
};

/* Source default ROI, before kernel BAF/BF finalization. */
int camssX1ERearAfRectangle(const CamssX1ERearAfInput &input,
                           Rectangle *output);

struct CamssX1ERearBgControls {
    std::array<uint8_t, 3> aecWeightQ4;
    uint8_t awbQuad;
};

/* Source float-to-Q4 conversion; caller owns metering/quad policy. */
int camssX1ERearBgWeights(Span<const float> weights, bool awbQuad,
                          CamssX1ERearBgControls *output);

} /* namespace libcamera::ipa */
