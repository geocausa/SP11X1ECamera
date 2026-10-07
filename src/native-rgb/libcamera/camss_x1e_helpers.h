/* SPDX-License-Identifier: GPL-2.0-only */
#pragma once

#include <cstdint>
#include <libcamera/base/span.h>
#include <libcamera/controls.h>

extern "C" {
#include "native-imx681-control.h"
#include "native-stats3a.h"
#include "rear-neutral-scalar.h"
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

/* Pure quantized ISP state from caller-owned semantic inputs. */
int camssX1ERearScalars(const e012k_rear_scalar_input &input,
                       e012k_rear_scalar_output *output);

} /* namespace libcamera::ipa */
