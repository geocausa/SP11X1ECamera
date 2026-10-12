// SPDX-License-Identifier: GPL-2.0-only
/*
 * CSIPHY2.1.2 C-PHY configuration preparation. No MMIO, power or reset.
 * Nominal rate bins: public Qualcomm cam_csiphy_2_1_2_hwreg.h,
 * GPL-2.0-only, revision 9f97a168359d55d3e1806a6c568bb285cfd6a906.
 */
#include <linux/bitops.h>
#include <linux/errno.h>
#include <linux/kernel.h>

#include "phy-qcom-mipi-csi2-cphy-config.h"

static const u64 cphy_symbol_rates[] = {
	100000000ULL,
	200000000ULL,
	300000000ULL,
	350000000ULL,
	400000000ULL,
	500000000ULL,
	600000000ULL,
	700000000ULL,
	800000000ULL,
	900000000ULL,
	1000000000ULL,
	1200000000ULL,
	1500000000ULL,
	1700000000ULL,
	2000000000ULL,
	2100000000ULL,
	2350000000ULL,
	2500000000ULL,
	2600000000ULL,
	2800000000ULL,
	3000000000ULL,
	3300000000ULL,
	3500000000ULL,
	4000000000ULL,
	4500000000ULL,
	5000000000ULL,
	5500000000ULL,
	6000000000ULL,
};

int mipi_csi2phy_cphy_prepare(const struct mipi_csi2phy_cphy_request *request,
			    struct mipi_csi2phy_cphy_config *config)
{
	struct mipi_csi2phy_cphy_config prepared = { 0 };
	unsigned int i;
	u8 mask = 0;

	if (!request || !config)
		return -EINVAL;

	if (!request->num_trios || request->num_trios > 3 ||
	    !request->settle_count || request->settle_count > 0xffff)
		return -EINVAL;

	/* Bound the explicit frequency before doubling it. */
	if (request->link_freq_hz < cphy_symbol_rates[0] / 2 ||
	    request->link_freq_hz >
	    cphy_symbol_rates[ARRAY_SIZE(cphy_symbol_rates) - 1] / 2)
		return -ERANGE;

	for (i = 0; i < request->num_trios; i++) {
		u32 lane = request->data_lanes[i];
		u8 bit;

		if (lane < 1 || lane > 3)
			return -EINVAL;
		bit = BIT(2 * lane - 1);
		if (mask & bit)
			return -EINVAL;
		mask |= bit;
		prepared.data_lanes[i] = lane;
	}
	for (; i < ARRAY_SIZE(request->data_lanes); i++)
		if (request->data_lanes[i])
			return -EINVAL;

	prepared.link_freq_hz = request->link_freq_hz;
	prepared.symbol_rate = request->link_freq_hz * 2;
	prepared.settle_count = request->settle_count;
	prepared.num_trios = request->num_trios;
	prepared.lane_mask = mask;

	for (i = 0; i < ARRAY_SIZE(cphy_symbol_rates); i++)
		if (prepared.symbol_rate <= cphy_symbol_rates[i])
			break;
	if (i == ARRAY_SIZE(cphy_symbol_rates))
		return -ERANGE;
	prepared.rate_index = i;

	/* Publish only after all route, rate and register-width checks pass. */
	*config = prepared;
	return 0;
}
