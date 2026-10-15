#!/usr/bin/env python3
"""X1E80100 C-PHY on the upstream PHY-API path. Exact-match edits on a linux-next tree.
Usage: x1e-cphy-edits.py <tree> phycore|csid|camss|phydrv"""
import sys
from pathlib import Path
T, what = Path(sys.argv[1]), sys.argv[2]


def edit(rel, pairs):
    p = T / rel
    s = p.read_text()
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit("%s: %d matches for %r" % (rel, s.count(old), old[:70]))
        s = s.replace(old, new)
    p.write_text(s)


if what == "phycore":
    (T / "include/linux/phy/phy-mipi-cphy.h").write_text("""/* SPDX-License-Identifier: GPL-2.0 */
#ifndef __PHY_MIPI_CPHY_H_
#define __PHY_MIPI_CPHY_H_

/**
 * struct phy_configure_opts_mipi_cphy - MIPI C-PHY configuration set
 *
 * This structure is used to represent the configuration state of a
 * MIPI C-PHY phy.
 */
struct phy_configure_opts_mipi_cphy {
	/**
	 * @symbol_rate:
	 *
	 * Symbol rate on each trio, in symbols per second.
	 */
	unsigned long		symbol_rate;

	/**
	 * @lanes:
	 *
	 * Number of active trios.
	 */
	unsigned char		lanes;
};

#endif /* __PHY_MIPI_CPHY_H_ */
""")
    edit("include/linux/phy/phy.h", [
        ("#include <linux/phy/phy-mipi-dphy.h>\n", "#include <linux/phy/phy-mipi-cphy.h>\n#include <linux/phy/phy-mipi-dphy.h>\n"),
        ("\tPHY_MODE_MIPI_DPHY,\n", "\tPHY_MODE_MIPI_DPHY,\n\tPHY_MODE_MIPI_CPHY,\n"),
        (" * @mipi_dphy:\tConfiguration set applicable for phys supporting\n *\t\tthe MIPI_DPHY phy mode.\n",
         " * @mipi_dphy:\tConfiguration set applicable for phys supporting\n *\t\tthe MIPI_DPHY phy mode.\n * @mipi_cphy:\tConfiguration set applicable for phys supporting\n *\t\tthe MIPI_CPHY phy mode.\n"),
        ("\tstruct phy_configure_opts_mipi_dphy\tmipi_dphy;\n",
         "\tstruct phy_configure_opts_mipi_dphy\tmipi_dphy;\n\tstruct phy_configure_opts_mipi_cphy\tmipi_cphy;\n"),
    ])

elif what == "csid":
    edit("drivers/media/platform/qcom/camss/camss-csid-680.c", [
        ("""		val |= (phy->csiphy_id + CSI2_RX_CFG0_PHY_SEL_BASE_IDX)
			<< CSI2_RX_CFG0_PHY_NUM_SEL;
	}
""", """		val |= (phy->csiphy_id + CSI2_RX_CFG0_PHY_SEL_BASE_IDX)
			<< CSI2_RX_CFG0_PHY_NUM_SEL;
	}

	val |= phy->phy_sel << CSI2_RX_CFG0_PHY_TYPE_SEL;
""")])

elif what == "camss":
    edit("drivers/media/platform/qcom/camss/camss-csiphy.c", [
        ("""	struct csiphy_lanes_cfg *lncfg = &csiphy->cfg.csi2->lane_cfg;
	struct phy_configure_opts_mipi_dphy *dphy_cfg;
	union phy_configure_opts dphy_opts = { 0 };
	struct device *dev = csiphy->camss->dev;
	u8 num_lanes = lncfg->num_data;
	s64 link_freq;
	int ret;

	dphy_cfg = &dphy_opts.mipi_dphy;

	link_freq = camss_get_link_freq(&csiphy->subdev.entity, bpp, num_lanes,
					csiphy->cfg.csi2->lane_cfg.phy_cfg == V4L2_MBUS_CSI2_CPHY);

	if (link_freq <= 0) {
		dev_err(dev,
			"Cannot get CSI2 transmitter's link frequency\\n");
		return -EINVAL;
	}

	ret = phy_mipi_dphy_get_default_config_for_hsclk(link_freq, num_lanes,
							 dphy_cfg);
	if (ret < 0) {
		dev_err(dev, "Invalid config for link frequency %lld\\n",
			link_freq);
		return ret;
	}

	ret = phy_set_mode(csiphy->phy, PHY_MODE_MIPI_DPHY);
	if (ret) {
		dev_err(dev, "Failed to set phy mode\\n");
		return ret;
	}

	ret = phy_configure(csiphy->phy, &dphy_opts);
	if (ret) {
		dev_err(dev, "failed to configure MIPI D-PHY\\n");
		goto error;
	}
""", """	struct csiphy_lanes_cfg *lncfg = &csiphy->cfg.csi2->lane_cfg;
	const bool cphy = lncfg->phy_cfg == V4L2_MBUS_CSI2_CPHY;
	union phy_configure_opts opts = { 0 };
	struct device *dev = csiphy->camss->dev;
	u8 num_lanes = lncfg->num_data;
	s64 link_freq;
	int ret;

	link_freq = camss_get_link_freq(&csiphy->subdev.entity, bpp, num_lanes,
					cphy);

	if (link_freq <= 0) {
		dev_err(dev,
			"Cannot get CSI2 transmitter's link frequency\\n");
		return -EINVAL;
	}

	if (cphy) {
		/* A C-PHY link frequency is half the symbol rate. */
		opts.mipi_cphy.symbol_rate = link_freq * 2;
		opts.mipi_cphy.lanes = num_lanes;
	} else {
		ret = phy_mipi_dphy_get_default_config_for_hsclk(link_freq,
								 num_lanes,
								 &opts.mipi_dphy);
		if (ret < 0) {
			dev_err(dev, "Invalid config for link frequency %lld\\n",
				link_freq);
			return ret;
		}
	}

	ret = phy_set_mode(csiphy->phy,
			   cphy ? PHY_MODE_MIPI_CPHY : PHY_MODE_MIPI_DPHY);
	if (ret) {
		dev_err(dev, "Failed to set phy mode\\n");
		return ret;
	}

	ret = phy_configure(csiphy->phy, &opts);
	if (ret) {
		dev_err(dev, "failed to configure MIPI %s\\n",
			cphy ? "C-PHY" : "D-PHY");
		goto error;
	}
""")])

elif what == "phydrv":
    H = "drivers/phy/qualcomm/phy-qcom-mipi-csi2.h"
    edit(H, [
        ("#define CSI2_MAX_DATA_LANES\t4\n", "#define CSI2_MAX_DATA_LANES\t4\n#define CSI2_MAX_TRIOS\t\t3\n"),
        ("""struct mipi_csi2phy_device_regs {
	const struct mipi_csi2phy_lane_regs *init_seq;
	const int lane_array_size;
""", """struct mipi_csi2phy_device_regs {
	const struct mipi_csi2phy_lane_regs *init_seq;
	const int lane_array_size;
	const struct mipi_csi2phy_lane_regs *cphy_init_seq;
	const int cphy_lane_array_size;
"""),
        ("\tstruct device *dev;\n\tu8 phy_mode;\n", "\tstruct device *dev;\n\tu8 phy_mode;\n\tu32 bus_type;\n"),
    ])
    C = "drivers/phy/qualcomm/phy-qcom-mipi-csi2-core.c"
    edit(C, [
        ("""	struct phy_configure_opts_mipi_dphy *dphy_cfg = &opts->mipi_dphy;
	struct mipi_csi2phy_stream_cfg *stream_cfg = &csi2phy->stream_cfg;
	int ret;

	ret = phy_mipi_dphy_config_validate(dphy_cfg);
""", """	struct phy_configure_opts_mipi_dphy *dphy_cfg = &opts->mipi_dphy;
	struct mipi_csi2phy_stream_cfg *stream_cfg = &csi2phy->stream_cfg;
	int ret;

	if (csi2phy->phy_mode == PHY_MODE_MIPI_CPHY) {
		struct phy_configure_opts_mipi_cphy *cphy_cfg = &opts->mipi_cphy;

		if (!cphy_cfg->symbol_rate ||
		    cphy_cfg->lanes != stream_cfg->num_data_lanes)
			return -EINVAL;

		/* As for V4L2, a C-PHY link frequency is half the symbol rate. */
		stream_cfg->link_freq = cphy_cfg->symbol_rate / 2;

		return 0;
	}

	ret = phy_mipi_dphy_config_validate(dphy_cfg);
"""),
        ("""	if (mode != PHY_MODE_MIPI_DPHY)
		return -EOPNOTSUPP;

	csi2phy->phy_mode = mode;
""", """	/* The mode has to be the bus the endpoint describes. */
	switch (mode) {
	case PHY_MODE_MIPI_DPHY:
		if (csi2phy->bus_type != MEDIA_BUS_TYPE_CSI2_DPHY)
			return -EINVAL;
		break;
	case PHY_MODE_MIPI_CPHY:
		if (csi2phy->bus_type != MEDIA_BUS_TYPE_CSI2_CPHY)
			return -EINVAL;
		break;
	default:
		return -EOPNOTSUPP;
	}

	csi2phy->phy_mode = mode;
"""),
        ("""	if (bus_type != MEDIA_BUS_TYPE_CSI2_DPHY) {
		ret = -EOPNOTSUPP;
		dev_err(dev, "Unsupported bus-type %u\\n", bus_type);
		goto out_put;
	}

	num_data_lanes = fwnode_property_count_u32(ep, "data-lanes");
	if (num_data_lanes < 1 || num_data_lanes > CSI2_MAX_DATA_LANES) {
""", """	switch (bus_type) {
	case MEDIA_BUS_TYPE_CSI2_DPHY:
		max_lanes = CSI2_MAX_DATA_LANES;
		break;
	case MEDIA_BUS_TYPE_CSI2_CPHY:
		if (csi2phy->soc_cfg->reg_info.cphy_init_seq) {
			max_lanes = CSI2_MAX_TRIOS;
			break;
		}
		fallthrough;
	default:
		ret = -EOPNOTSUPP;
		dev_err(dev, "Unsupported bus-type %u\\n", bus_type);
		goto out_put;
	}
	csi2phy->bus_type = bus_type;

	num_data_lanes = fwnode_property_count_u32(ep, "data-lanes");
	if (num_data_lanes < 1 || num_data_lanes > max_lanes) {
"""),
        ("""	num_polarities = fwnode_property_count_u32(ep, "lane-polarities");
	if (num_polarities > 0) {
""", """	num_polarities = fwnode_property_count_u32(ep, "lane-polarities");
	if (num_polarities > 0 && bus_type == MEDIA_BUS_TYPE_CSI2_CPHY) {
		ret = -EINVAL;
		dev_err(dev, "lane-polarities do not apply to C-PHY\\n");
		goto out_put;
	}
	if (num_polarities > 0) {
"""),
        ("""		if (data_lanes[i] < 1 || data_lanes[i] > CSI2_MAX_DATA_LANES) {""",
         """		if (data_lanes[i] < 1 || data_lanes[i] > max_lanes) {"""),
        ("""	int num_polarities;
	int num_data_lanes;
	u32 bus_type;
""", """	int num_polarities;
	int num_data_lanes;
	int max_lanes;
	u32 bus_type;
"""),
    ])
    P = "drivers/phy/qualcomm/phy-qcom-mipi-csi2-3ph-dphy.c"
    s = (T / P).read_text()
    cph = open(Path(__file__).with_name("x1e-cphy-table.inc")).read()
    edit(P, [
        ("""static inline const struct mipi_csi2phy_device_regs *
csi2phy_dev_to_regs(""", cph + """
static inline const struct mipi_csi2phy_device_regs *
csi2phy_dev_to_regs("""),
        ("""static void
phy_qcom_mipi_csi2_gen2_config_lanes(struct mipi_csi2phy_device *csi2phy,
				     u8 settle_cnt)
{
	const struct mipi_csi2phy_device_regs *regs = csi2phy_dev_to_regs(csi2phy);
	const struct mipi_csi2phy_lane_regs *r = regs->init_seq;
	int i, array_size = regs->lane_array_size;
""", """static void
phy_qcom_mipi_csi2_gen2_config_lanes(struct mipi_csi2phy_device *csi2phy,
				     u8 settle_cnt)
{
	const struct mipi_csi2phy_device_regs *regs = csi2phy_dev_to_regs(csi2phy);
	const bool cphy = csi2phy->bus_type == MEDIA_BUS_TYPE_CSI2_CPHY;
	const struct mipi_csi2phy_lane_regs *r = cphy ? regs->cphy_init_seq :
								regs->init_seq;
	int i, array_size = cphy ? regs->cphy_lane_array_size :
				   regs->lane_array_size;
"""),
        ("""	struct mipi_csi2phy_lanes_cfg *lane_cfg = &cfg->lane_cfg;
	u8 settle_cnt;
	u8 val;
	int i;

	if (cfg->link_freq <= 0)
		return -EINVAL;

	settle_cnt = phy_qcom_mipi_csi2_settle_cnt_calc(cfg->link_freq, csi2phy->timer_clk_rate);
	if (!settle_cnt)
		return -ENODEV;
""", """	struct mipi_csi2phy_lanes_cfg *lane_cfg = &cfg->lane_cfg;
	const bool cphy = csi2phy->bus_type == MEDIA_BUS_TYPE_CSI2_CPHY;
	u8 settle_cnt = 0;
	u8 val;
	int i;

	if (cfg->link_freq <= 0)
		return -EINVAL;

	if (cphy) {
		/* The C-PHY sequence carries its own timing; trios are the odd bits. */
		val = 0;
		for (i = 0; i < cfg->num_data_lanes; i++)
			val |= BIT(lane_cfg->data[i].pos * 2 + 1);

		writel(val, csi2phy->base +
		       CSIPHY_3PH_CMN_CSI_COMMON_CTRLn(regs->common_regs_offset, 5));

		goto common;
	}

	settle_cnt = phy_qcom_mipi_csi2_settle_cnt_calc(cfg->link_freq, csi2phy->timer_clk_rate);
	if (!settle_cnt)
		return -ENODEV;
"""),
        ("""	if (lane_cfg->clk.pol)
		writel(BIT(2), csi2phy->base + CSIPHY_2PH_LN_CSI_2PHASE_CTRL9n(lane_cfg->clk.pos));

	val = CSIPHY_3PH_CMN_CSI_COMMON_CTRL6_COMMON_PWRDN_B;
""", """	if (lane_cfg->clk.pol)
		writel(BIT(2), csi2phy->base + CSIPHY_2PH_LN_CSI_2PHASE_CTRL9n(lane_cfg->clk.pos));

common:
	val = CSIPHY_3PH_CMN_CSI_COMMON_CTRL6_COMMON_PWRDN_B;
"""),
        ("""		.init_seq = lane_regs_x1e80100,
		.lane_array_size = ARRAY_SIZE(lane_regs_x1e80100),
""", """		.init_seq = lane_regs_x1e80100,
		.lane_array_size = ARRAY_SIZE(lane_regs_x1e80100),
		.cphy_init_seq = lane_regs_x1e80100_cphy,
		.cphy_lane_array_size = ARRAY_SIZE(lane_regs_x1e80100_cphy),
"""),
    ])
    s = (T / P).read_text()
    if "#include <dt-bindings/media/video-interfaces.h>" not in s:
        s = s.replace("#include <linux/delay.h>\n", "#include <dt-bindings/media/video-interfaces.h>\n#include <linux/delay.h>\n", 1)
        (T / P).write_text(s)
else:
    sys.exit("unknown " + what)
print("ok", what)
