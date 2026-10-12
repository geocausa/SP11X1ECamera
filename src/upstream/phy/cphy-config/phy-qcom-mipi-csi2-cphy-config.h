/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef __PHY_QCOM_MIPI_CSI2_CPHY_CONFIG_H__
#define __PHY_QCOM_MIPI_CSI2_CPHY_CONFIG_H__

#include <linux/types.h>

/*
 * Internal CSIPHY2.1.2 preparation, not a generic PHY ABI.
 * link_freq_hz is the explicit sensor frequency (symbol rate / 2).
 * settle_count must be derived and qualified separately for this receiver;
 * checking its register width does not validate MIPI timing.
 */
struct mipi_csi2phy_cphy_request {
	u64 link_freq_hz;
	u32 settle_count;
	u32 num_trios;
	u32 data_lanes[3];
};

struct mipi_csi2phy_cphy_config {
	u64 link_freq_hz;
	u64 symbol_rate;
	u16 settle_count;
	u8 num_trios;
	u8 lane_mask;
	u8 rate_index;
	u8 data_lanes[3];
};

int mipi_csi2phy_cphy_prepare(const struct mipi_csi2phy_cphy_request *request,
			    struct mipi_csi2phy_cphy_config *config);

#endif /* __PHY_QCOM_MIPI_CSI2_CPHY_CONFIG_H__ */
