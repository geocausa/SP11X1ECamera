// SPDX-License-Identifier: GPL-2.0
/*
 * camss.c
 *
 * Qualcomm MSM Camera Subsystem - Core
 *
 * Copyright (c) 2015, The Linux Foundation. All rights reserved.
 * Copyright (C) 2015-2018 Linaro Ltd.
 */
#include <asm/barrier.h>

#include <linux/clk.h>
#include <linux/interconnect.h>
#include <linux/interrupt.h>
#include <linux/ioport.h>
#include <linux/jiffies.h>
#include <linux/media-bus-format.h>
#include <linux/media.h>
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/of_device.h>
#include <linux/of_graph.h>
#include <linux/pm_runtime.h>
#include <linux/pm_domain.h>
#include <linux/slab.h>
#include <linux/sizes.h>
#include <linux/unaligned.h>
#include <linux/videodev2.h>

#include <media/media-device.h>
#include <media/v4l2-async.h>
#include <media/v4l2-device.h>
#include <media/v4l2-mc.h>
#include <media/v4l2-fwnode.h>

#include "camss.h"

#define CAMSS_CLOCK_MARGIN_NUMERATOR 105
#define CAMSS_CLOCK_MARGIN_DENOMINATOR 100

/*
 * C-PHY encodes data by 16/7 ~ 2.28 bits/symbol
 * D-PHY doesn't encode data, thus 16/16 = 1 b/s
 */
#define CAMSS_COMMON_PHY_DIVIDENT 16
#define CAMSS_CPHY_DIVISOR 7
#define CAMSS_DPHY_DIVISOR 16

static const struct parent_dev_ops vfe_parent_dev_ops;

static const struct camss_subdev_resources csiphy_res_8x16[] = {
	/* CSIPHY0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy0_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000 } },
		.reg = { "csiphy0", "csiphy0_clk_mux" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_2ph_1_0,
			.formats = &csiphy_formats_8x16
		}
	},

	/* CSIPHY1 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy1_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000 } },
		.reg = { "csiphy1", "csiphy1_clk_mux" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_2ph_1_0,
			.formats = &csiphy_formats_8x16
		}
	}
};

static const struct camss_subdev_resources csid_res_8x16[] = {
	/* CSID0 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 40000 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi0_ahb", "ahb",
			   "csi0", "csi0_phy", "csi0_pix", "csi0_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_4_1,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_1
		}
	},

	/* CSID1 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 40000 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi1_ahb", "ahb",
			   "csi1", "csi1_phy", "csi1_pix", "csi1_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_4_1,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_1
		}
	},
};

static const struct camss_subdev_resources ispif_res_8x16 = {
	/* ISPIF */
	.clock = { "top_ahb", "ahb", "ispif_ahb",
		   "csi0", "csi0_pix", "csi0_rdi",
		   "csi1", "csi1_pix", "csi1_rdi" },
	.clock_for_reset = { "vfe0", "csi_vfe0" },
	.reg = { "ispif", "csi_clk_mux" },
	.interrupt = { "ispif" },
};

static const struct camss_subdev_resources vfe_res_8x16[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "vfe0", "csi_vfe0",
			   "vfe_ahb", "vfe_axi", "ahb" },
		.clock_rate = { { 0 },
				{ 50000000, 80000000, 100000000, 160000000,
				  177780000, 200000000, 266670000, 320000000,
				  400000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.hw_ops = &vfe_ops_4_1,
			.formats_rdi = &vfe_formats_rdi_8x16,
			.formats_pix = &vfe_formats_pix_8x16
		}
	}
};

static const struct camss_subdev_resources csiphy_res_8x39[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 40000 }
		},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy0_timer" },
		.clock_rate = { { 0 },
				{ 40000000, 80000000 },
				{ 0 },
				{ 100000000, 200000000 } },
		.reg = { "csiphy0", "csiphy0_clk_mux" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_2ph_1_0,
			.formats = &csiphy_formats_8x16
		}
	},

	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 40000 }
		},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy1_timer" },
		.clock_rate = { { 0 },
				{ 40000000, 80000000 },
				{ 0 },
				{ 100000000, 200000000 } },
		.reg = { "csiphy1", "csiphy1_clk_mux" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_2ph_1_0,
			.formats = &csiphy_formats_8x16
		}
	}
};

static const struct camss_subdev_resources csid_res_8x39[] = {
	/* CSID0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "csi0_ahb", "ahb",
			   "csi0", "csi0_phy", "csi0_pix", "csi0_rdi" },
		.clock_rate = { { 0 },
				{ 40000000, 80000000 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_4_1,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_1
		}
	},

	/* CSID1 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "csi1_ahb", "ahb",
			   "csi1", "csi1_phy", "csi1_pix", "csi1_rdi" },
		.clock_rate = { { 0 },
				{ 40000000, 80000000 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_4_1,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_1
		}
	},

	/* CSID2 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "csi2_ahb", "ahb",
			   "csi2", "csi2_phy", "csi2_pix", "csi2_rdi" },
		.clock_rate = { { 0 },
				{ 40000000, 80000000 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.hw_ops = &csid_ops_4_1,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_1
		}
	},
};

static const struct camss_subdev_resources ispif_res_8x39 = {
	/* ISPIF */
	.clock = { "top_ahb", "ispif_ahb", "ahb",
		   "csi0", "csi0_pix", "csi0_rdi",
		   "csi1", "csi1_pix", "csi1_rdi",
		   "csi2", "csi2_pix", "csi2_rdi" },
	.clock_for_reset = { "vfe0", "csi_vfe0" },
	.reg = { "ispif", "csi_clk_mux" },
	.interrupt = { "ispif" },
};

static const struct camss_subdev_resources vfe_res_8x39[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "vfe0", "csi_vfe0",
			   "vfe_ahb", "vfe_axi", "ahb" },
		.clock_rate = { { 0 },
				{ 40000000, 80000000 },
				{ 50000000, 80000000, 100000000, 160000000,
				  177780000, 200000000, 266670000, 320000000,
				  400000000, 465000000, 480000000, 600000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.has_vbif = true,
			.vbif_name = "vfe0_vbif",
			.hw_ops = &vfe_ops_4_1,
			.formats_rdi = &vfe_formats_rdi_8x16,
			.formats_pix = &vfe_formats_pix_8x16
		}
	}
};

static const struct camss_subdev_resources csid_res_8x53[] = {
	/* CSID0 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 9900 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi0_ahb", "ahb",
			   "csi0", "csi0_phy", "csi0_pix", "csi0_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 310000000,
				  400000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},

	/* CSID1 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 9900 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi1_ahb", "ahb",
			   "csi1", "csi1_phy", "csi1_pix", "csi1_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 310000000,
				  400000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},

	/* CSID2 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 9900 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi2_ahb", "ahb",
			   "csi2", "csi2_phy", "csi2_pix", "csi2_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 310000000,
				  400000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},
};

static const struct camss_subdev_resources ispif_res_8x53 = {
	/* ISPIF */
	.clock = { "top_ahb", "ahb", "ispif_ahb",
		   "csi0", "csi0_pix", "csi0_rdi",
		   "csi1", "csi1_pix", "csi1_rdi",
		   "csi2", "csi2_pix", "csi2_rdi" },
	.clock_for_reset = { "vfe0", "csi_vfe0", "vfe1", "csi_vfe1" },
	.reg = { "ispif", "csi_clk_mux" },
	.interrupt = { "ispif" },
};

static const struct camss_subdev_resources vfe_res_8x53[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ahb", "ispif_ahb",
			   "vfe0", "csi_vfe0", "vfe0_ahb", "vfe0_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 50000000, 100000000, 133330000,
				  160000000, 200000000, 266670000,
				  310000000, 400000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.pd_name = "vfe0",
			.hw_ops = &vfe_ops_4_1,
			.formats_rdi = &vfe_formats_rdi_8x16,
			.formats_pix = &vfe_formats_pix_8x16
		}
	},

	/* VFE1 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ahb", "ispif_ahb",
			   "vfe1", "csi_vfe1", "vfe1_ahb", "vfe1_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 50000000, 100000000, 133330000,
				  160000000, 200000000, 266670000,
				  310000000, 400000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.pd_name = "vfe1",
			.hw_ops = &vfe_ops_4_1,
			.formats_rdi = &vfe_formats_rdi_8x16,
			.formats_pix = &vfe_formats_pix_8x16
		}
	}
};

static const struct resources_icc icc_res_8x53[] = {
	{
		.name = "cam_ahb",
		.icc_bw_tbl.avg = 38400,
		.icc_bw_tbl.peak = 76800,
	},
	{
		.name = "cam_vfe0_mem",
		.icc_bw_tbl.avg = 939524,
		.icc_bw_tbl.peak = 1342177,
	},
	{
		.name = "cam_vfe1_mem",
		.icc_bw_tbl.avg = 939524,
		.icc_bw_tbl.peak = 1342177,
	},
};

static const struct camss_subdev_resources csiphy_res_8x96[] = {
	/* CSIPHY0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy0_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 266666667 } },
		.reg = { "csiphy0", "csiphy0_clk_mux" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_8x96
		}
	},

	/* CSIPHY1 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy1_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 266666667 } },
		.reg = { "csiphy1", "csiphy1_clk_mux" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_8x96
		}
	},

	/* CSIPHY2 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy2_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 266666667 } },
		.reg = { "csiphy2", "csiphy2_clk_mux" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_8x96
		}
	}
};

static const struct camss_subdev_resources csid_res_8x96[] = {
	/* CSID0 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 80160 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi0_ahb", "ahb",
			   "csi0", "csi0_phy", "csi0_pix", "csi0_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 266666667 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},

	/* CSID1 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 80160 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi1_ahb", "ahb",
			   "csi1", "csi1_phy", "csi1_pix", "csi1_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 266666667 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},

	/* CSID2 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 80160 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi2_ahb", "ahb",
			   "csi2", "csi2_phy", "csi2_pix", "csi2_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 266666667 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},

	/* CSID3 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 80160 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi3_ahb", "ahb",
			   "csi3", "csi3_phy", "csi3_pix", "csi3_rdi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 266666667 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid3" },
		.interrupt = { "csid3" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	}
};

static const struct camss_subdev_resources ispif_res_8x96 = {
	/* ISPIF */
	.clock = { "top_ahb", "ahb", "ispif_ahb",
		   "csi0", "csi0_pix", "csi0_rdi",
		   "csi1", "csi1_pix", "csi1_rdi",
		   "csi2", "csi2_pix", "csi2_rdi",
		   "csi3", "csi3_pix", "csi3_rdi" },
	.clock_for_reset = { "vfe0", "csi_vfe0", "vfe1", "csi_vfe1" },
	.reg = { "ispif", "csi_clk_mux" },
	.interrupt = { "ispif" },
};

static const struct camss_subdev_resources vfe_res_8x96[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ahb", "vfe0", "csi_vfe0", "vfe_ahb",
			   "vfe0_ahb", "vfe_axi", "vfe0_stream"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 75000000, 100000000, 300000000,
				  320000000, 480000000, 600000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.hw_ops = &vfe_ops_4_7,
			.formats_rdi = &vfe_formats_rdi_8x96,
			.formats_pix = &vfe_formats_pix_8x96
		}
	},

	/* VFE1 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ahb", "vfe1", "csi_vfe1", "vfe_ahb",
			   "vfe1_ahb", "vfe_axi", "vfe1_stream"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 75000000, 100000000, 300000000,
				  320000000, 480000000, 600000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.hw_ops = &vfe_ops_4_7,
			.formats_rdi = &vfe_formats_rdi_8x96,
			.formats_pix = &vfe_formats_pix_8x96
		}
	}
};

static const struct camss_subdev_resources csiphy_res_2290[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 26700 },
			{ .supply = "vdd-csiphy-1p8", .init_load_uA = 2600 }
		},
		.clock = { "top_ahb", "ahb", "csiphy0", "csiphy0_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 240000000, 341330000, 384000000 },
				{ 100000000, 200000000, 268800000 }  },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},

	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 26700 },
			{ .supply = "vdd-csiphy-1p8", .init_load_uA = 2600 }
		},
		.clock = { "top_ahb", "ahb", "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 240000000, 341330000, 384000000 },
				{ 100000000, 200000000, 268800000 }  },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	}
};

static const struct camss_subdev_resources csid_res_2290[] = {
	/* CSID0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ahb", "csi0", "vfe0_cphy_rx", "vfe0" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 192000000, 240000000, 384000000, 426400000 },
				{ 0 },
				{ 0 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_340,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},

	/* CSID1 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ahb", "csi1", "vfe1_cphy_rx", "vfe1" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 192000000, 240000000, 384000000, 426400000 },
				{ 0 },
				{ 0 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_340,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	}
};

static const struct camss_subdev_resources vfe_res_2290[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ahb", "axi", "vfe0", "camnoc_rt_axi", "camnoc_nrt_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 153600000, 192000000, 256000000, 384000000, 460800000 },
				{ 0 },
				{ 0 }, },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 4,
			.hw_ops = &vfe_ops_340,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},

	/* VFE1 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ahb", "axi", "vfe1", "camnoc_rt_axi", "camnoc_nrt_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 153600000, 192000000, 256000000, 384000000, 460800000 },
				{ 0 },
				{ 0 }, },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 4,
			.hw_ops = &vfe_ops_340,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
};

static const struct resources_icc icc_res_2290[] = {
	{
		.name = "ahb",
		.icc_bw_tbl.avg = 150000,
		.icc_bw_tbl.peak = 300000,
	},
	{
		.name = "hf_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 3000000,
	},
	{
		.name = "sf_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 3000000,
	},
};

static const struct camss_subdev_resources csiphy_res_660[] = {
	/* CSIPHY0 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy0_timer",
			   "csi0_phy", "csiphy_ahb2crif" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 269333333 },
				{ 0 } },
		.reg = { "csiphy0", "csiphy0_clk_mux" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_8x96
		}
	},

	/* CSIPHY1 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy1_timer",
			   "csi1_phy", "csiphy_ahb2crif" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 269333333 },
				{ 0 } },
		.reg = { "csiphy1", "csiphy1_clk_mux" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_8x96
		}
	},

	/* CSIPHY2 */
	{
		.regulators = {},
		.clock = { "top_ahb", "ispif_ahb", "ahb", "csiphy2_timer",
			   "csi2_phy", "csiphy_ahb2crif" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 269333333 },
				{ 0 } },
		.reg = { "csiphy2", "csiphy2_clk_mux" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_8x96
		}
	}
};

static const struct camss_subdev_resources csid_res_660[] = {
	/* CSID0 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 0 },
			{ .supply = "vdd_sec", .init_load_uA = 0 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi0_ahb", "ahb",
			   "csi0", "csi0_phy", "csi0_pix", "csi0_rdi",
			   "cphy_csid0" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 310000000,
				  404000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},

	/* CSID1 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 0 },
			{ .supply = "vdd_sec", .init_load_uA = 0 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi1_ahb", "ahb",
			   "csi1", "csi1_phy", "csi1_pix", "csi1_rdi",
			   "cphy_csid1" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 310000000,
				  404000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},

	/* CSID2 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 0 },
			{ .supply = "vdd_sec", .init_load_uA = 0 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi2_ahb", "ahb",
			   "csi2", "csi2_phy", "csi2_pix", "csi2_rdi",
			   "cphy_csid2" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 310000000,
				  404000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	},

	/* CSID3 */
	{
		.regulators = {
			{ .supply = "vdda", .init_load_uA = 0 },
			{ .supply = "vdd_sec", .init_load_uA = 0 }
		},
		.clock = { "top_ahb", "ispif_ahb", "csi3_ahb", "ahb",
			   "csi3", "csi3_phy", "csi3_pix", "csi3_rdi",
			   "cphy_csid3" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 310000000,
				  404000000, 465000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid3" },
		.interrupt = { "csid3" },
		.csid = {
			.hw_ops = &csid_ops_4_7,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_4_7
		}
	}
};

static const struct camss_subdev_resources ispif_res_660 = {
	/* ISPIF */
	.clock = { "top_ahb", "ahb", "ispif_ahb",
		   "csi0", "csi0_pix", "csi0_rdi",
		   "csi1", "csi1_pix", "csi1_rdi",
		   "csi2", "csi2_pix", "csi2_rdi",
		   "csi3", "csi3_pix", "csi3_rdi" },
	.clock_for_reset = { "vfe0", "csi_vfe0", "vfe1", "csi_vfe1" },
	.reg = { "ispif", "csi_clk_mux" },
	.interrupt = { "ispif" },
};

static const struct camss_subdev_resources vfe_res_660[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "throttle_axi", "top_ahb", "ahb", "vfe0",
			   "csi_vfe0", "vfe_ahb", "vfe0_ahb", "vfe_axi",
			   "vfe0_stream"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 120000000, 200000000, 256000000,
				  300000000, 404000000, 480000000,
				  540000000, 576000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.hw_ops = &vfe_ops_4_8,
			.formats_rdi = &vfe_formats_rdi_8x96,
			.formats_pix = &vfe_formats_pix_8x96
		}
	},

	/* VFE1 */
	{
		.regulators = {},
		.clock = { "throttle_axi", "top_ahb", "ahb", "vfe1",
			   "csi_vfe1", "vfe_ahb", "vfe1_ahb", "vfe_axi",
			   "vfe1_stream"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 120000000, 200000000, 256000000,
				  300000000, 404000000, 480000000,
				  540000000, 576000000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.hw_ops = &vfe_ops_4_8,
			.formats_rdi = &vfe_formats_rdi_8x96,
			.formats_pix = &vfe_formats_pix_8x96
		}
	}
};

static const struct camss_subdev_resources csiphy_res_670[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 42800 },
			{ .supply = "vdda-pll", .init_load_uA = 13900 }
		},
		.clock = { "soc_ahb", "cpas_ahb",
			   "csiphy0", "csiphy0_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 240000000, 269333333 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},

	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 42800 },
			{ .supply = "vdda-pll", .init_load_uA = 13900 }
		},
		.clock = { "soc_ahb", "cpas_ahb",
			   "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 240000000, 269333333 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},

	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 42800 },
			{ .supply = "vdda-pll", .init_load_uA = 13900 }
		},
		.clock = { "soc_ahb", "cpas_ahb",
			   "csiphy2", "csiphy2_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 240000000, 269333333 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	}
};

static const struct camss_subdev_resources csid_res_670[] = {
	/* CSID0 */
	{
		.regulators = {},
		.clock = { "cpas_ahb", "soc_ahb", "vfe0",
			   "vfe0_cphy_rx", "csi0" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 384000000 },
				{ 19200000, 75000000, 384000000, 538666667 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},

	/* CSID1 */
	{
		.regulators = {},
		.clock = { "cpas_ahb", "soc_ahb", "vfe1",
			   "vfe1_cphy_rx", "csi1" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 384000000 },
				{ 19200000, 75000000, 384000000, 538666667 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},

	/* CSID2 */
	{
		.regulators = {},
		.clock = { "cpas_ahb", "soc_ahb", "vfe_lite",
			   "vfe_lite_cphy_rx", "csi2" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 384000000 },
				{ 19200000, 75000000, 384000000, 538666667 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	}
};

static const struct camss_subdev_resources vfe_res_670[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "cpas_ahb", "soc_ahb",
			   "vfe0", "vfe0_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 0 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 4,
			.has_pd = true,
			.pd_name = "ife0",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},

	/* VFE1 */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "cpas_ahb", "soc_ahb",
			   "vfe1", "vfe1_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 0 } },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 4,
			.has_pd = true,
			.pd_name = "ife1",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},

	/* VFE-lite */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "cpas_ahb", "soc_ahb",
			   "vfe_lite" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 100000000, 320000000, 404000000, 480000000, 600000000 } },
		.reg = { "vfe_lite" },
		.interrupt = { "vfe_lite" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	}
};

static const struct camss_subdev_resources csiphy_res_845[] = {
	/* CSIPHY0 */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "soc_ahb", "slow_ahb_src",
				"cpas_ahb", "cphy_rx_src", "csiphy0",
				"csiphy0_timer_src", "csiphy0_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 240000000, 269333333 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},

	/* CSIPHY1 */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "soc_ahb", "slow_ahb_src",
				"cpas_ahb", "cphy_rx_src", "csiphy1",
				"csiphy1_timer_src", "csiphy1_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 240000000, 269333333 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},

	/* CSIPHY2 */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "soc_ahb", "slow_ahb_src",
				"cpas_ahb", "cphy_rx_src", "csiphy2",
				"csiphy2_timer_src", "csiphy2_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 240000000, 269333333 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},

	/* CSIPHY3 */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "soc_ahb", "slow_ahb_src",
				"cpas_ahb", "cphy_rx_src", "csiphy3",
				"csiphy3_timer_src", "csiphy3_timer" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 19200000, 240000000, 269333333 } },
		.reg = { "csiphy3" },
		.interrupt = { "csiphy3" },
		.csiphy = {
			.id = 3,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	}
};

static const struct camss_subdev_resources csid_res_845[] = {
	/* CSID0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "cpas_ahb", "cphy_rx_src", "slow_ahb_src",
				"soc_ahb", "vfe0", "vfe0_src",
				"vfe0_cphy_rx", "csi0",
				"csi0_src" },
		.clock_rate = { { 0 },
				{ 384000000 },
				{ 80000000 },
				{ 0 },
				{ 19200000, 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 320000000 },
				{ 0 },
				{ 19200000, 75000000, 384000000, 538666667 },
				{ 384000000 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},

	/* CSID1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "cpas_ahb", "cphy_rx_src", "slow_ahb_src",
				"soc_ahb", "vfe1", "vfe1_src",
				"vfe1_cphy_rx", "csi1",
				"csi1_src" },
		.clock_rate = { { 0 },
				{ 384000000 },
				{ 80000000 },
				{ 0 },
				{ 19200000, 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 320000000 },
				{ 0 },
				{ 19200000, 75000000, 384000000, 538666667 },
				{ 384000000 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},

	/* CSID2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "cpas_ahb", "cphy_rx_src", "slow_ahb_src",
				"soc_ahb", "vfe_lite", "vfe_lite_src",
				"vfe_lite_cphy_rx", "csi2",
				"csi2_src" },
		.clock_rate = { { 0 },
				{ 384000000 },
				{ 80000000 },
				{ 0 },
				{ 19200000, 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 320000000 },
				{ 0 },
				{ 19200000, 75000000, 384000000, 538666667 },
				{ 384000000 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	}
};

static const struct camss_subdev_resources vfe_res_845[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "cpas_ahb", "slow_ahb_src",
				"soc_ahb", "vfe0", "vfe0_axi",
				"vfe0_src", "csi0",
				"csi0_src"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 80000000 },
				{ 0 },
				{ 19200000, 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 0 },
				{ 320000000 },
				{ 19200000, 75000000, 384000000, 538666667 },
				{ 384000000 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 4,
			.pd_name = "ife0",
			.has_pd = true,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},

	/* VFE1 */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "cpas_ahb", "slow_ahb_src",
				"soc_ahb", "vfe1", "vfe1_axi",
				"vfe1_src", "csi1",
				"csi1_src"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 80000000 },
				{ 0 },
				{ 19200000, 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 0 },
				{ 320000000 },
				{ 19200000, 75000000, 384000000, 538666667 },
				{ 384000000 } },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 4,
			.pd_name = "ife1",
			.has_pd = true,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},

	/* VFE-lite */
	{
		.regulators = {},
		.clock = { "camnoc_axi", "cpas_ahb", "slow_ahb_src",
				"soc_ahb", "vfe_lite",
				"vfe_lite_src", "csi2",
				"csi2_src"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 80000000 },
				{ 0 },
				{ 19200000, 100000000, 320000000, 404000000, 480000000, 600000000 },
				{ 320000000 },
				{ 19200000, 75000000, 384000000, 538666667 },
				{ 384000000 } },
		.reg = { "vfe_lite" },
		.interrupt = { "vfe_lite" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	}
};

static const struct camss_subdev_resources csiphy_res_sm6150[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 35000 },
			{ .supply = "vdd-csiphy-1p8", .init_load_uA = 5000 }
		},
		.clock = { "csiphy0", "csiphy0_timer" },
		.clock_rate = { { 269333333, 384000000 },
				{ 269333333 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 35000 },
			{ .supply = "vdd-csiphy-1p8", .init_load_uA = 5000 }
		},
		.clock = { "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 269333333, 384000000 },
				{ 269333333 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 35000 },
			{ .supply = "vdd-csiphy-1p8", .init_load_uA = 5000 }
		},
		.clock = { "csiphy2", "csiphy2_timer" },
		.clock_rate = { { 269333333, 384000000 },
				{ 269333333 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
};

static const struct camss_subdev_resources csid_res_sm6150[] = {
	/* CSID0 */
	{
		.regulators = {},
		.clock = { "vfe0_cphy_rx", "vfe0_csid" },
		.clock_rate = { { 269333333, 384000000 },
				{ 320000000, 540000000 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.is_lite = false,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID1 */
	{
		.regulators = {},
		.clock = { "vfe1_cphy_rx", "vfe1_csid" },
		.clock_rate = { { 269333333, 384000000 },
				{ 320000000, 540000000 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.is_lite = false,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID2 */
	{
		.regulators = {},
		.clock = { "vfe_lite_cphy_rx", "vfe_lite_csid" },
		.clock_rate = { { 269333333, 384000000 },
				{ 320000000, 540000000 } },
		.reg = { "csid_lite" },
		.interrupt = { "csid_lite" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
};

static const struct camss_subdev_resources vfe_res_sm6150[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "camnoc_axi", "cpas_ahb", "soc_ahb",
			   "vfe0", "vfe0_axi"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 80000000 },
				{ 37500000, 40000000 },
				{ 360000000, 432000000, 540000000, 600000000 },
				{ 265000000, 426000000 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = true,
			.pd_name = "ife0",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE1 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "camnoc_axi", "cpas_ahb", "soc_ahb",
			   "vfe1", "vfe1_axi"},
		.clock_rate = { { 0 },
				{ 0 },
				{ 80000000 },
				{ 37500000, 40000000 },
				{ 360000000, 432000000, 540000000, 600000000 },
				{ 265000000, 426000000 } },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = true,
			.pd_name = "ife1",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE2 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "camnoc_axi", "cpas_ahb", "soc_ahb",
			   "vfe_lite" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 80000000 },
				{ 37500000, 40000000 },
				{ 360000000, 432000000, 540000000, 600000000 } },
		.reg = { "vfe_lite" },
		.interrupt = { "vfe_lite" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
};

static const struct resources_icc icc_res_sm6150[] = {
	{
		.name = "ahb",
		.icc_bw_tbl.avg = 38400,
		.icc_bw_tbl.peak = 76800,
	},
	{
		.name = "hf_0",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct camss_subdev_resources csiphy_res_8250[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 17500 },
			{ .supply = "vdda-pll", .init_load_uA = 10000 }
		},
		.clock = { "csiphy0", "csiphy0_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 17500 },
			{ .supply = "vdda-pll", .init_load_uA = 10000 }
		},
		.clock = { "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 17500 },
			{ .supply = "vdda-pll", .init_load_uA = 10000 }
		},
		.clock = { "csiphy2", "csiphy2_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY3 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 17500 },
			{ .supply = "vdda-pll", .init_load_uA = 10000 }
		},
		.clock = { "csiphy3", "csiphy3_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy3" },
		.interrupt = { "csiphy3" },
		.csiphy = {
			.id = 3,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY4 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 17500 },
			{ .supply = "vdda-pll", .init_load_uA = 10000 }
		},
		.clock = { "csiphy4", "csiphy4_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy4" },
		.interrupt = { "csiphy4" },
		.csiphy = {
			.id = 4,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY5 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 17500 },
			{ .supply = "vdda-pll", .init_load_uA = 10000 }
		},
		.clock = { "csiphy5", "csiphy5_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy5" },
		.interrupt = { "csiphy5" },
		.csiphy = {
			.id = 5,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	}
};

static const struct camss_subdev_resources csid_res_8250[] = {
	/* CSID0 */
	{
		.regulators = {},
		.clock = { "vfe0_csid", "vfe0_cphy_rx", "vfe0", "vfe0_areg", "vfe0_ahb" },
		.clock_rate = { { 400000000 },
				{ 400000000 },
				{ 350000000, 475000000, 576000000, 720000000 },
				{ 100000000, 200000000, 300000000, 400000000 },
				{ 0 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID1 */
	{
		.regulators = {},
		.clock = { "vfe1_csid", "vfe1_cphy_rx", "vfe1", "vfe1_areg", "vfe1_ahb" },
		.clock_rate = { { 400000000 },
				{ 400000000 },
				{ 350000000, 475000000, 576000000, 720000000 },
				{ 100000000, 200000000, 300000000, 400000000 },
				{ 0 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID2 */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx", "vfe_lite",  "vfe_lite_ahb" },
		.clock_rate = { { 400000000 },
				{ 400000000 },
				{ 400000000, 480000000 },
				{ 0 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID3 */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx", "vfe_lite",  "vfe_lite_ahb" },
		.clock_rate = { { 400000000 },
				{ 400000000 },
				{ 400000000, 480000000 },
				{ 0 } },
		.reg = { "csid3" },
		.interrupt = { "csid3" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	}
};

static const struct camss_subdev_resources vfe_res_8250[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "camnoc_axi_src", "slow_ahb_src", "cpas_ahb",
			   "camnoc_axi", "vfe0_ahb", "vfe0_areg", "vfe0",
			   "vfe0_axi", "cam_hf_axi" },
		.clock_rate = { { 19200000, 300000000, 400000000, 480000000 },
				{ 19200000, 80000000 },
				{ 19200000 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 300000000, 400000000 },
				{ 350000000, 475000000, 576000000, 720000000 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.pd_name = "ife0",
			.hw_ops = &vfe_ops_480,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE1 */
	{
		.regulators = {},
		.clock = { "camnoc_axi_src", "slow_ahb_src", "cpas_ahb",
			   "camnoc_axi", "vfe1_ahb", "vfe1_areg", "vfe1",
			   "vfe1_axi", "cam_hf_axi" },
		.clock_rate = { { 19200000, 300000000, 400000000, 480000000 },
				{ 19200000, 80000000 },
				{ 19200000 },
				{ 0 },
				{ 0 },
				{ 100000000, 200000000, 300000000, 400000000 },
				{ 350000000, 475000000, 576000000, 720000000 },
				{ 0 },
				{ 0 } },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.pd_name = "ife1",
			.hw_ops = &vfe_ops_480,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE2 (lite) */
	{
		.regulators = {},
		.clock = { "camnoc_axi_src", "slow_ahb_src", "cpas_ahb",
			   "camnoc_axi", "vfe_lite_ahb", "vfe_lite_axi",
			   "vfe_lite", "cam_hf_axi" },
		.clock_rate = { { 19200000, 300000000, 400000000, 480000000 },
				{ 19200000, 80000000 },
				{ 19200000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 400000000, 480000000 },
				{ 0 } },
		.reg = { "vfe_lite0" },
		.interrupt = { "vfe_lite0" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_480,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE3 (lite) */
	{
		.regulators = {},
		.clock = { "camnoc_axi_src", "slow_ahb_src", "cpas_ahb",
			   "camnoc_axi", "vfe_lite_ahb", "vfe_lite_axi",
			   "vfe_lite", "cam_hf_axi" },
		.clock_rate = { { 19200000, 300000000, 400000000, 480000000 },
				{ 19200000, 80000000 },
				{ 19200000 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 400000000, 480000000 },
				{ 0 } },
		.reg = { "vfe_lite1" },
		.interrupt = { "vfe_lite1" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_480,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
};

static const struct resources_icc icc_res_sm8250[] = {
	{
		.name = "cam_ahb",
		.icc_bw_tbl.avg = 38400,
		.icc_bw_tbl.peak = 76800,
	},
	{
		.name = "cam_hf_0_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
	{
		.name = "cam_sf_0_mnoc",
		.icc_bw_tbl.avg = 0,
		.icc_bw_tbl.peak = 2097152,
	},
	{
		.name = "cam_sf_icp_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct camss_subdev_resources csiphy_res_7280[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 16100 },
			{ .supply = "vdda-pll", .init_load_uA = 9000 }
		},

		.clock = { "csiphy0", "csiphy0_timer" },
		.clock_rate = { { 300000000, 400000000 },
				{ 300000000 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		}
	},
	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 16100 },
			{ .supply = "vdda-pll", .init_load_uA = 9000 }
		},

		.clock = { "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 300000000, 400000000 },
				{ 300000000 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		}
	},
	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 16100 },
			{ .supply = "vdda-pll", .init_load_uA = 9000 }
		},

		.clock = { "csiphy2", "csiphy2_timer" },
		.clock_rate = { { 300000000, 400000000 },
				{ 300000000 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		}
	},
	/* CSIPHY3 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 16100 },
			{ .supply = "vdda-pll", .init_load_uA = 9000 }
		},

		.clock = { "csiphy3", "csiphy3_timer" },
		.clock_rate = { { 300000000, 400000000 },
				{ 300000000 } },
		.reg = { "csiphy3" },
		.interrupt = { "csiphy3" },
		.csiphy = {
			.id = 3,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		}
	},
	/* CSIPHY4 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 16100 },
			{ .supply = "vdda-pll", .init_load_uA = 9000 }
		},

		.clock = { "csiphy4", "csiphy4_timer" },
		.clock_rate = { { 300000000, 400000000 },
				{ 300000000 } },
		.reg = { "csiphy4" },
		.interrupt = { "csiphy4" },
		.csiphy = {
			.id = 4,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		}
	},
};

static const struct camss_subdev_resources csid_res_7280[] = {
	/* CSID0 */
	{
		.regulators = {},

		.clock = { "vfe0_csid", "vfe0_cphy_rx", "vfe0" },
		.clock_rate = { { 300000000, 400000000 },
				{ 0 },
				{ 380000000, 510000000, 637000000, 760000000 }
		},

		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.is_lite = false,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID1 */
	{
		.regulators = {},

		.clock = { "vfe1_csid", "vfe1_cphy_rx", "vfe1" },
		.clock_rate = { { 300000000, 400000000 },
				{ 0 },
				{ 380000000, 510000000, 637000000, 760000000 }
		},

		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.is_lite = false,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID2 */
	{
		.regulators = {},

		.clock = { "vfe2_csid", "vfe2_cphy_rx", "vfe2" },
		.clock_rate = { { 300000000, 400000000 },
				{ 0 },
				{ 380000000, 510000000, 637000000, 760000000 }
		},

		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.is_lite = false,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID3 */
	{
		.regulators = {},

		.clock = { "vfe_lite0_csid", "vfe_lite0_cphy_rx", "vfe_lite0" },
		.clock_rate = { { 300000000, 400000000 },
				{ 0 },
				{ 320000000, 400000000, 480000000, 600000000 }
		},

		.reg = { "csid_lite0" },
		.interrupt = { "csid_lite0" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID4 */
	{
		.regulators = {},

		.clock = { "vfe_lite1_csid", "vfe_lite1_cphy_rx", "vfe_lite1" },
		.clock_rate = { { 300000000, 400000000 },
				{ 0 },
				{ 320000000, 400000000, 480000000, 600000000 }
		},

		.reg = { "csid_lite1" },
		.interrupt = { "csid_lite1" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
};

static const struct camss_subdev_resources vfe_res_7280[] = {
	/* VFE0 */
	{
		.regulators = {},

		.clock = { "camnoc_axi", "cpas_ahb", "icp_ahb", "vfe0",
			   "vfe0_axi", "gcc_axi_hf", "gcc_axi_sf" },
		.clock_rate = { { 150000000, 240000000, 320000000, 400000000, 480000000 },
				{ 80000000 },
				{ 0 },
				{ 380000000, 510000000, 637000000, 760000000 },
				{ 0 },
				{ 0 },
				{ 0 } },

		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = true,
			.pd_name = "ife0",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE1 */
	{
		.regulators = {},

		.clock = { "camnoc_axi", "cpas_ahb", "icp_ahb", "vfe1",
			   "vfe1_axi", "gcc_axi_hf", "gcc_axi_sf" },
		.clock_rate = { { 150000000, 240000000, 320000000, 400000000, 480000000 },
				{ 80000000 },
				{ 0 },
				{ 380000000, 510000000, 637000000, 760000000 },
				{ 0 },
				{ 0 },
				{ 0 } },

		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = true,
			.pd_name = "ife1",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE2 */
	{
		.regulators = {},

		.clock = { "camnoc_axi", "cpas_ahb", "icp_ahb", "vfe2",
			   "vfe2_axi", "gcc_axi_hf", "gcc_axi_sf" },
		.clock_rate = { { 150000000, 240000000, 320000000, 400000000, 480000000 },
				{ 80000000 },
				{ 0 },
				{ 380000000, 510000000, 637000000, 760000000 },
				{ 0 },
				{ 0 },
				{ 0 } },

		.reg = { "vfe2" },
		.interrupt = { "vfe2" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.hw_ops = &vfe_ops_170,
			.has_pd = true,
			.pd_name = "ife2",
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE3 (lite) */
	{
		.clock = { "camnoc_axi", "cpas_ahb", "icp_ahb",
			   "vfe_lite0", "gcc_axi_hf", "gcc_axi_sf" },
		.clock_rate = { { 150000000, 240000000, 320000000, 400000000, 480000000 },
				{ 80000000 },
				{ 0 },
				{ 320000000, 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 } },

		.regulators = {},
		.reg = { "vfe_lite0" },
		.interrupt = { "vfe_lite0" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE4 (lite) */
	{
		.clock = { "camnoc_axi", "cpas_ahb", "icp_ahb",
			   "vfe_lite1", "gcc_axi_hf", "gcc_axi_sf" },
		.clock_rate = { { 150000000, 240000000, 320000000, 400000000, 480000000 },
				{ 80000000 },
				{ 0 },
				{ 320000000, 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 } },

		.regulators = {},
		.reg = { "vfe_lite1" },
		.interrupt = { "vfe_lite1" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
};

static const struct resources_icc icc_res_sc7280[] = {
	{
		.name = "ahb",
		.icc_bw_tbl.avg = 38400,
		.icc_bw_tbl.peak = 76800,
	},
	{
		.name = "hf_0",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct camss_subdev_resources csiphy_res_sc8280xp[] = {
	/* CSIPHY0 */
	{
		.regulators = {},
		.clock = { "csiphy0", "csiphy0_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY1 */
	{
		.regulators = {},
		.clock = { "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY2 */
	{
		.regulators = {},
		.clock = { "csiphy2", "csiphy2_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY3 */
	{
		.regulators = {},
		.clock = { "csiphy3", "csiphy3_timer" },
		.clock_rate = { { 400000000 },
				{ 300000000 } },
		.reg = { "csiphy3" },
		.interrupt = { "csiphy3" },
		.csiphy = {
			.id = 3,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
};

static const struct camss_subdev_resources csid_res_sc8280xp[] = {
	/* CSID0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "vfe0_csid", "vfe0_cphy_rx", "vfe0", "vfe0_axi" },
		.clock_rate = { { 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "vfe1_csid", "vfe1_cphy_rx", "vfe1", "vfe1_axi" },
		.clock_rate = { { 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "vfe2_csid", "vfe2_cphy_rx", "vfe2", "vfe2_axi" },
		.clock_rate = { { 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID3 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "vfe3_csid", "vfe3_cphy_rx", "vfe3", "vfe3_axi" },
		.clock_rate = { { 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 },
				{ 0 } },
		.reg = { "csid3" },
		.interrupt = { "csid3" },
		.csid = {
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID_LITE0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "vfe_lite0_csid", "vfe_lite0_cphy_rx", "vfe_lite0" },
		.clock_rate = { { 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 }, },
		.reg = { "csid0_lite" },
		.interrupt = { "csid0_lite" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID_LITE1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "vfe_lite1_csid", "vfe_lite1_cphy_rx", "vfe_lite1" },
		.clock_rate = { { 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 }, },
		.reg = { "csid1_lite" },
		.interrupt = { "csid1_lite" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID_LITE2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "vfe_lite2_csid", "vfe_lite2_cphy_rx", "vfe_lite2" },
		.clock_rate = { { 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 }, },
		.reg = { "csid2_lite" },
		.interrupt = { "csid2_lite" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID_LITE3 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 0 },
			{ .supply = "vdda-pll", .init_load_uA = 0 }
		},
		.clock = { "vfe_lite3_csid", "vfe_lite3_cphy_rx", "vfe_lite3" },
		.clock_rate = { { 400000000, 480000000, 600000000 },
				{ 0 },
				{ 0 }, },
		.reg = { "csid3_lite" },
		.interrupt = { "csid3_lite" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen2,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	}
};

static const struct camss_subdev_resources vfe_res_sc8280xp[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb", "camnoc_axi", "vfe0", "vfe0_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 19200000, 80000000},
				{ 19200000, 150000000, 266666667, 320000000, 400000000, 480000000 },
				{ 400000000, 558000000, 637000000, 760000000 },
				{ 0 }, },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 4,
			.pd_name = "ife0",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE1 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb", "camnoc_axi", "vfe1", "vfe1_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 19200000, 80000000},
				{ 19200000, 150000000, 266666667, 320000000, 400000000, 480000000 },
				{ 400000000, 558000000, 637000000, 760000000 },
				{ 0 }, },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 4,
			.pd_name = "ife1",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE2 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb", "camnoc_axi", "vfe2", "vfe2_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 19200000, 80000000},
				{ 19200000, 150000000, 266666667, 320000000, 400000000, 480000000 },
				{ 400000000, 558000000, 637000000, 760000000 },
				{ 0 }, },
		.reg = { "vfe2" },
		.interrupt = { "vfe2" },
		.vfe = {
			.line_num = 4,
			.pd_name = "ife2",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE3 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb", "camnoc_axi", "vfe3", "vfe3_axi" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 19200000, 80000000},
				{ 19200000, 150000000, 266666667, 320000000, 400000000, 480000000 },
				{ 400000000, 558000000, 637000000, 760000000 },
				{ 0 }, },
		.reg = { "vfe3" },
		.interrupt = { "vfe3" },
		.vfe = {
			.line_num = 4,
			.pd_name = "ife3",
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE_LITE_0 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb", "camnoc_axi", "vfe_lite0" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 19200000, 80000000},
				{ 19200000, 150000000, 266666667, 320000000, 400000000, 480000000 },
				{ 320000000, 400000000, 480000000, 600000000 }, },
		.reg = { "vfe_lite0" },
		.interrupt = { "vfe_lite0" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE_LITE_1 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb", "camnoc_axi", "vfe_lite1" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 19200000, 80000000},
				{ 19200000, 150000000, 266666667, 320000000, 400000000, 480000000 },
				{ 320000000, 400000000, 480000000, 600000000 }, },
		.reg = { "vfe_lite1" },
		.interrupt = { "vfe_lite1" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE_LITE_2 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb", "camnoc_axi", "vfe_lite2" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 19200000, 80000000},
				{ 19200000, 150000000, 266666667, 320000000, 400000000, 480000000 },
				{ 320000000, 400000000, 480000000, 600000000, }, },
		.reg = { "vfe_lite2" },
		.interrupt = { "vfe_lite2" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE_LITE_3 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb", "camnoc_axi", "vfe_lite3" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 19200000, 80000000},
				{ 19200000, 150000000, 266666667, 320000000, 400000000, 480000000 },
				{ 320000000, 400000000, 480000000, 600000000 }, },
		.reg = { "vfe_lite3" },
		.interrupt = { "vfe_lite3" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_170,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
};

static const struct resources_icc icc_res_sc8280xp[] = {
	{
		.name = "cam_ahb",
		.icc_bw_tbl.avg = 150000,
		.icc_bw_tbl.peak = 300000,
	},
	{
		.name = "cam_hf_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
	{
		.name = "cam_sf_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
	{
		.name = "cam_sf_icp_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct camss_subdev_resources csiphy_res_8550[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 32200 },
			{ .supply = "vdda-pll", .init_load_uA = 18000 }
		},
		.clock = { "csiphy0", "csiphy0_timer" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 32200 },
			{ .supply = "vdda-pll", .init_load_uA = 18000 }
		},
		.clock = { "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 32200 },
			{ .supply = "vdda-pll", .init_load_uA = 18000 }
		},
		.clock = { "csiphy2", "csiphy2_timer" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY3 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 32200 },
			{ .supply = "vdda-pll", .init_load_uA = 18000 }
		},
		.clock = { "csiphy3", "csiphy3_timer" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000 } },
		.reg = { "csiphy3" },
		.interrupt = { "csiphy3" },
		.csiphy = {
			.id = 3,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY4 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 37900 },
			{ .supply = "vdda-pll", .init_load_uA = 18600 }
		},
		.clock = { "csiphy4", "csiphy4_timer" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000 } },
		.reg = { "csiphy4" },
		.interrupt = { "csiphy4" },
		.csiphy = {
			.id = 4,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY5 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 32200 },
			{ .supply = "vdda-pll", .init_load_uA = 18000 }
		},
		.clock = { "csiphy5", "csiphy5_timer" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000 } },
		.reg = { "csiphy5" },
		.interrupt = { "csiphy5" },
		.csiphy = {
			.id = 5,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY6 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 37900 },
			{ .supply = "vdda-pll", .init_load_uA = 18600 }
		},
		.clock = { "csiphy6", "csiphy6_timer" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000 } },
		.reg = { "csiphy6" },
		.interrupt = { "csiphy6" },
		.csiphy = {
			.id = 6,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY7 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 32200 },
			{ .supply = "vdda-pll", .init_load_uA = 18000 }
		},
		.clock = { "csiphy7", "csiphy7_timer" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000 } },
		.reg = { "csiphy7" },
		.interrupt = { "csiphy7" },
		.csiphy = {
			.id = 7,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	}
};

static const struct resources_wrapper csid_wrapper_res_sm8550 = {
	.reg = "csid_wrapper",
};

static const struct camss_subdev_resources csid_res_8550[] = {
	/* CSID0 */
	{
		.regulators = {},
		.clock = { "csid", "csiphy_rx" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000, 480000000 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.is_lite = false,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID1 */
	{
		.regulators = {},
		.clock = { "csid", "csiphy_rx" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000, 480000000 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.is_lite = false,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID2 */
	{
		.regulators = {},
		.clock = { "csid", "csiphy_rx" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000, 480000000 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.is_lite = false,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID3 */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000, 480000000 } },
		.reg = { "csid_lite0" },
		.interrupt = { "csid_lite0" },
		.csid = {
			.is_lite = true,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID4 */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = { { 400000000, 480000000 },
				{ 400000000, 480000000 } },
		.reg = { "csid_lite1" },
		.interrupt = { "csid_lite1" },
		.csid = {
			.is_lite = true,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2
		}
	}
};

static const struct camss_subdev_resources vfe_res_8550[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "cpas_ahb", "cpas_fast_ahb_clk", "vfe0_fast_ahb",
			   "vfe0", "cpas_vfe0", "camnoc_axi" },
		.clock_rate = { { 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 },
				{ 466000000, 594000000, 675000000, 785000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 } },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = true,
			.pd_name = "ife0",
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE1 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "cpas_ahb", "cpas_fast_ahb_clk", "vfe1_fast_ahb",
			   "vfe1", "cpas_vfe1", "camnoc_axi" },
		.clock_rate = {	{ 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 },
				{ 466000000, 594000000, 675000000, 785000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 } },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = true,
			.pd_name = "ife1",
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE2 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "cpas_ahb", "cpas_fast_ahb_clk", "vfe2_fast_ahb",
			   "vfe2", "cpas_vfe2", "camnoc_axi" },
		.clock_rate = {	{ 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 },
				{ 466000000, 594000000, 675000000, 785000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 } },
		.reg = { "vfe2" },
		.interrupt = { "vfe2" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = true,
			.pd_name = "ife2",
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE3 lite */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "cpas_ahb", "vfe_lite_ahb",
			   "vfe_lite", "cpas_ife_lite", "camnoc_axi" },
		.clock_rate = {	{ 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 400000000, 480000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 } },
		.reg = { "vfe_lite0" },
		.interrupt = { "vfe_lite0" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE4 lite */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "cpas_ahb", "vfe_lite_ahb",
			   "vfe_lite", "cpas_ife_lite", "camnoc_axi" },
		.clock_rate = {	{ 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 400000000, 480000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 } },
		.reg = { "vfe_lite1" },
		.interrupt = { "vfe_lite1" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
};

static const struct resources_icc icc_res_sm8550[] = {
	{
		.name = "ahb",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
	{
		.name = "hf_0_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct camss_subdev_resources csiphy_res_sm8650[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy01-0p9", .init_load_uA = 88000 },
			{ .supply = "vdd-csiphy01-1p2", .init_load_uA = 17800 },
		},
		.clock = { "csiphy0", "csiphy0_timer" },
		.clock_rate = {	{ 400000000 },
				{ 400000000 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		},
	},
	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy01-0p9", .init_load_uA = 88000 },
			{ .supply = "vdd-csiphy01-1p2", .init_load_uA = 17800 },
		},
		.clock = { "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 400000000 },
				{ 400000000 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		},
	},
	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy24-0p9", .init_load_uA = 147000 },
			{ .supply = "vdd-csiphy24-1p2", .init_load_uA = 24400 },
		},
		.clock = { "csiphy2", "csiphy2_timer" },
		.clock_rate = { { 400000000 },
				{ 400000000 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		},
	},
	/* CSIPHY3 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy35-0p9", .init_load_uA = 88000 },
			{ .supply = "vdd-csiphy35-1p2", .init_load_uA = 17800 },
		},
		.clock = { "csiphy3", "csiphy3_timer" },
		.clock_rate = { { 400000000 },
				{ 400000000 } },
		.reg = { "csiphy3" },
		.interrupt = { "csiphy3" },
		.csiphy = {
			.id = 3,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		},
	},
	/* CSIPHY4 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy24-0p9", .init_load_uA = 147000 },
			{ .supply = "vdd-csiphy24-1p2", .init_load_uA = 24400 },
		},
		.clock = { "csiphy4", "csiphy4_timer" },
		.clock_rate = { { 400000000 },
				{ 400000000 } },
		.reg = { "csiphy4" },
		.interrupt = { "csiphy4" },
		.csiphy = {
			.id = 4,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		},
	},
	/* CSIPHY5 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy35-0p9", .init_load_uA = 88000 },
			{ .supply = "vdd-csiphy35-1p2", .init_load_uA = 17800 },
		},
		.clock = { "csiphy5", "csiphy5_timer" },
		.clock_rate = { { 400000000 },
				{ 400000000 } },
		.reg = { "csiphy5" },
		.interrupt = { "csiphy5" },
		.csiphy = {
			.id = 5,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		},
	},
};

static const struct camss_subdev_resources csid_res_sm8650[] = {
	/* CSID0 */
	{
		.regulators = { },
		.clock = { "csid", "csiphy_rx" },
		.clock_rate = { { 400000000 },
				{ 400000000, 480000000 } },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2,
		},
	},
	/* CSID1 */
	{
		.regulators = { },
		.clock = { "csid", "csiphy_rx" },
		.clock_rate = { { 400000000 },
				{ 400000000, 480000000 } },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2,
		},
	},
	/* CSID2 */
	{
		.regulators = { },
		.clock = { "csid", "csiphy_rx" },
		.clock_rate = { { 400000000 },
				{ 400000000, 480000000 } },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2,
		},
	},
	/* CSID3 lite */
	{
		.regulators = { },
		.clock = { "vfe_lite_ahb", "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = { { 0 },
				{ 400000000, 480000000 },
				{ 0 } },
		.reg = { "csid_lite0" },
		.interrupt = { "csid_lite0" },
		.csid = {
			.is_lite = true,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2,
		},
	},
	/* CSID4 lite */
	{
		.regulators = { },
		.clock = { "vfe_lite_ahb", "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = { { 0 },
				{ 400000000, 480000000 },
				{ 0 } },
		.reg = { "csid_lite1" },
		.interrupt = { "csid_lite1" },
		.csid = {
			.is_lite = true,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.hw_ops = &csid_ops_gen3,
			.formats = &csid_formats_gen2,
		},
	},
};

static const struct camss_subdev_resources vfe_res_sm8650[] = {
	/* VFE0 */
	{
		.regulators = { },
		.clock = { "gcc_axi_hf", "cpas_ahb", "cpas_fast_ahb",
			   "camnoc_axi", "vfe0_fast_ahb", "vfe0", "cpas_vfe0",
			   "qdss_debug_xo",
		},
		.clock_rate = {	{ 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 },
				{ 0 },
				{ 466000000, 594000000, 675000000, 785000000 },
				{ 0 },
				{ 0 },
		},
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.pd_name = "ife0",
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		},
	},
	/* VFE1 */
	{
		.regulators = { },
		.clock = { "gcc_axi_hf", "cpas_ahb", "cpas_fast_ahb",
			   "camnoc_axi", "vfe1_fast_ahb", "vfe1", "cpas_vfe1",
			   "qdss_debug_xo",
		},
		.clock_rate = {	{ 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 },
				{ 0 },
				{ 466000000, 594000000, 675000000, 785000000 },
				{ 0 },
				{ 0 },
		},
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.pd_name = "ife1",
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		},
	},
	/* VFE2 */
	{
		.regulators = { },
		.clock = { "gcc_axi_hf", "cpas_ahb", "cpas_fast_ahb",
			   "camnoc_axi", "vfe2_fast_ahb", "vfe2", "cpas_vfe2",
			   "qdss_debug_xo",
		},
		.clock_rate = { { 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 300000000, 400000000 },
				{ 0 },
				{ 466000000, 594000000, 675000000, 785000000 },
				{ 0 },
				{ 0 },
		},
		.reg = { "vfe2" },
		.interrupt = { "vfe2" },
		.vfe = {
			.line_num = 3,
			.has_pd = true,
			.pd_name = "ife2",
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		},
	},
	/* VFE3 lite */
	{
		.regulators = { },
		.clock = { "gcc_axi_hf", "cpas_ahb", "camnoc_axi",
			   "vfe_lite_ahb", "vfe_lite", "cpas_vfe_lite",
			   "qdss_debug_xo",
		},
		.clock_rate = { { 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 0 },
				{ 400000000, 480000000 },
				{ 0 },
				{ 0 },
		},
		.reg = { "vfe_lite0" },
		.interrupt = { "vfe_lite0" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		},
	},
	/* VFE4 lite */
	{
		.regulators = { },
		.clock = { "gcc_axi_hf", "cpas_ahb", "camnoc_axi",
			   "vfe_lite_ahb", "vfe_lite", "cpas_vfe_lite",
			   "qdss_debug_xo",
		},
		.clock_rate = {	{ 0 },
				{ 80000000 },
				{ 300000000, 400000000 },
				{ 0 },
				{ 400000000, 480000000 },
				{ 0 },
				{ 0 },
		},
		.reg = { "vfe_lite1" },
		.interrupt = { "vfe_lite1" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		},
	},
};

static const struct resources_icc icc_res_sm8650[] = {
	{
		.name = "ahb",
		.icc_bw_tbl.avg = 38400,
		.icc_bw_tbl.peak = 76800,
	},
	{
		.name = "hf_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct camss_subdev_resources csiphy_res_8300[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 15900 },
			{ .supply = "vdda-pll", .init_load_uA = 8900 }
		},

		.clock = { "csiphy_rx", "csiphy0", "csiphy0_timer" },
		.clock_rate = {
			{ 400000000 },
			{ 0 },
			{ 400000000 },
		},
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		}
	},
	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 15900 },
			{ .supply = "vdda-pll", .init_load_uA = 8900 }
		},

		.clock = { "csiphy_rx", "csiphy1", "csiphy1_timer" },
		.clock_rate = {
			{ 400000000 },
			{ 0 },
			{ 400000000 },
		},
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		}
	},
	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 15900 },
			{ .supply = "vdda-pll", .init_load_uA = 8900 }
		},

		.clock = { "csiphy_rx", "csiphy2", "csiphy2_timer" },
		.clock_rate = {
			{ 400000000 },
			{ 0 },
			{ 400000000 },
		},
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845,
		}
	},
};

static const struct camss_subdev_resources csiphy_res_8775p[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 15900 },
			{ .supply = "vdda-pll", .init_load_uA = 8900 }
		},
		.clock = { "csiphy_rx", "csiphy0", "csiphy0_timer"},
		.clock_rate = {
			{ 400000000 },
			{ 0 },
			{ 400000000 },
		},
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 15900 },
			{ .supply = "vdda-pll", .init_load_uA = 8900 }
		},
		.clock = { "csiphy_rx", "csiphy1", "csiphy1_timer"},
		.clock_rate = {
			{ 400000000 },
			{ 0 },
			{ 400000000 },
		},
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 15900 },
			{ .supply = "vdda-pll", .init_load_uA = 8900 }
		},
		.clock = { "csiphy_rx", "csiphy2", "csiphy2_timer"},
		.clock_rate = {
			{ 400000000 },
			{ 0 },
			{ 400000000 },
		},
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
	/* CSIPHY3 */
	{
		.regulators = {
			{ .supply = "vdda-phy", .init_load_uA = 15900 },
			{ .supply = "vdda-pll", .init_load_uA = 8900 }
		},
		.clock = { "csiphy_rx", "csiphy3", "csiphy3_timer"},
		.clock_rate = {
			{ 400000000 },
			{ 0 },
			{ 400000000 },
		},
		.reg = { "csiphy3" },
		.interrupt = { "csiphy3" },
		.csiphy = {
			.id = 3,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		}
	},
};

static const struct camss_subdev_resources csid_res_8775p[] = {
	/* CSID0 */
	{
		.regulators = {},
		.clock = { "csid", "csiphy_rx"},
		.clock_rate = {
			{ 400000000, 400000000},
			{ 400000000, 400000000}
		},
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.is_lite = false,
			.hw_ops = &csid_ops_gen3,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID1 */
	{
		.regulators = {},
		.clock = { "csid", "csiphy_rx"},
		.clock_rate = {
			{ 400000000, 400000000},
			{ 400000000, 400000000}
		},
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.is_lite = false,
			.hw_ops = &csid_ops_gen3,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},

	/* CSID2 (lite) */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = {
			{ 400000000, 480000000 },
			{ 400000000, 480000000 }
		},
		.reg = { "csid_lite0" },
		.interrupt = { "csid_lite0" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen3,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID3 (lite) */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = {
			{ 400000000, 480000000 },
			{ 400000000, 480000000 }
		},
		.reg = { "csid_lite1" },
		.interrupt = { "csid_lite1" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen3,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID4 (lite) */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = {
			{ 400000000, 480000000 },
			{ 400000000, 480000000 }
		},
		.reg = { "csid_lite2" },
		.interrupt = { "csid_lite2" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen3,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID5 (lite) */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = {
			{ 400000000, 480000000 },
			{ 400000000, 480000000 }
		},
		.reg = { "csid_lite3" },
		.interrupt = { "csid_lite3" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen3,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID6 (lite) */
	{
		.regulators = {},
		.clock = { "vfe_lite_csid", "vfe_lite_cphy_rx" },
		.clock_rate = {
			{ 400000000, 480000000 },
			{ 400000000, 480000000 }
		},
		.reg = { "csid_lite4" },
		.interrupt = { "csid_lite4" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_gen3,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
};

static const struct camss_subdev_resources vfe_res_8775p[] = {
	/* VFE0 */
	{
		.regulators = {},
		.clock = { "cpas_vfe0", "vfe0", "vfe0_fast_ahb",
			   "cpas_ahb", "gcc_axi_hf",
			   "cpas_fast_ahb_clk",
			   "camnoc_axi"},
		.clock_rate = {
			{ 0 },
			{ 480000000 },
			{ 300000000, 400000000 },
			{ 300000000, 400000000 },
			{ 0 },
			{ 300000000, 400000000 },
			{ 400000000 },
		},
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = false,
			.pd_name = NULL,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE1 */
	{
		.regulators = {},
		.clock = { "cpas_vfe1", "vfe1", "vfe1_fast_ahb",
			   "cpas_ahb", "gcc_axi_hf",
			   "cpas_fast_ahb_clk",
			   "camnoc_axi"},
		.clock_rate = {
			{ 0 },
			{ 480000000 },
			{ 300000000, 400000000 },
			{ 300000000, 400000000 },
			{ 0 },
			{ 300000000, 400000000 },
			{ 400000000 },
		},
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 3,
			.is_lite = false,
			.has_pd = false,
			.pd_name = NULL,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE2 (lite) */
	{
		.regulators = {},
		.clock = { "cpas_ahb", "cpas_vfe_lite", "vfe_lite_ahb",
			   "vfe_lite_csid", "vfe_lite_cphy_rx",
			   "vfe_lite", "camnoc_axi"},
		.clock_rate = {
			{ 0 },
			{ 0 },
			{ 300000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 480000000, 600000000, 600000000, 600000000 },
			{ 400000000 },
		},
		.reg = { "vfe_lite0" },
		.interrupt = { "vfe_lite0" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE3 (lite) */
	{
		.regulators = {},
		.clock = { "cpas_ahb", "cpas_vfe_lite", "vfe_lite_ahb",
			   "vfe_lite_csid", "vfe_lite_cphy_rx",
			   "vfe_lite", "camnoc_axi"},
		.clock_rate = {
			{ 0 },
			{ 0 },
			{ 300000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 480000000, 600000000, 600000000, 600000000 },
			{ 400000000 },
		},
		.reg = { "vfe_lite1" },
		.interrupt = { "vfe_lite1" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE4 (lite) */
	{
		.regulators = {},
		.clock = { "cpas_ahb", "cpas_vfe_lite", "vfe_lite_ahb",
			   "vfe_lite_csid", "vfe_lite_cphy_rx",
			   "vfe_lite", "camnoc_axi"},
		.clock_rate = {
			{ 0 },
			{ 0 },
			{ 300000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 480000000, 600000000, 600000000, 600000000 },
			{ 400000000 },
		},
		.reg = { "vfe_lite2" },
		.interrupt = { "vfe_lite2" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE5 (lite) */
	{
		.regulators = {},
		.clock = { "cpas_ahb", "cpas_vfe_lite", "vfe_lite_ahb",
			   "vfe_lite_csid", "vfe_lite_cphy_rx",
			   "vfe_lite", "camnoc_axi"},
		.clock_rate = {
			{ 0 },
			{ 0 },
			{ 300000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 480000000, 600000000, 600000000, 600000000 },
			{ 400000000 },
		},
		.reg = { "vfe_lite3" },
		.interrupt = { "vfe_lite3" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
	/* VFE6 (lite) */
	{
		.regulators = {},
		.clock = { "cpas_ahb", "cpas_vfe_lite", "vfe_lite_ahb",
			   "vfe_lite_csid", "vfe_lite_cphy_rx",
			   "vfe_lite", "camnoc_axi"},
		.clock_rate = {
			{ 0 },
			{ 0 },
			{ 300000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 400000000, 400000000, 400000000, 400000000 },
			{ 480000000, 600000000, 600000000, 600000000 },
			{ 400000000 },
		},
		.reg = { "vfe_lite4" },
		.interrupt = { "vfe_lite4" },
		.vfe = {
			.line_num = 4,
			.is_lite = true,
			.hw_ops = &vfe_ops_gen3,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		}
	},
};

static const struct resources_icc icc_res_qcs8300[] = {
	{
		.name = "ahb",
		.icc_bw_tbl.avg = 38400,
		.icc_bw_tbl.peak = 76800,
	},
	{
		.name = "hf_0",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct resources_icc icc_res_sa8775p[] = {
	{
		.name = "ahb",
		.icc_bw_tbl.avg = 38400,
		.icc_bw_tbl.peak = 76800,
	},
	{
		.name = "hf_0",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct camss_subdev_resources csiphy_res_x1e80100[] = {
	/* CSIPHY0 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-0p8", .init_load_uA = 105000 },
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 58900 }
		},
		.clock = { "csiphy0", "csiphy0_timer" },
		.clock_rate = { { 300000000, 400000000, 480000000 },
				{ 266666667, 400000000 } },
		.reg = { "csiphy0" },
		.interrupt = { "csiphy0" },
		.csiphy = {
			.id = 0,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		},
	},
	/* CSIPHY1 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-0p8", .init_load_uA = 105000 },
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 58900 }
		},
		.clock = { "csiphy1", "csiphy1_timer" },
		.clock_rate = { { 300000000, 400000000, 480000000 },
				{ 266666667, 400000000 } },
		.reg = { "csiphy1" },
		.interrupt = { "csiphy1" },
		.csiphy = {
			.id = 1,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		},
	},
	/* CSIPHY2 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-0p8", .init_load_uA = 105000 },
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 58900 }
		},
		.clock = { "csiphy2", "csiphy2_timer" },
		.clock_rate = { { 300000000, 400000000, 480000000 },
				{ 266666667, 400000000 } },
		.reg = { "csiphy2" },
		.interrupt = { "csiphy2" },
		.csiphy = {
			.id = 2,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		},
	},
	/* CSIPHY4 */
	{
		.regulators = {
			{ .supply = "vdd-csiphy-0p8", .init_load_uA = 105000 },
			{ .supply = "vdd-csiphy-1p2", .init_load_uA = 58900 }
		},
		.clock = { "csiphy4", "csiphy4_timer" },
		.clock_rate = { { 300000000, 400000000, 480000000 },
				{ 266666667, 400000000 } },
		.reg = { "csiphy4" },
		.interrupt = { "csiphy4" },
		.csiphy = {
			.id = 4,
			.hw_ops = &csiphy_ops_3ph_1_0,
			.formats = &csiphy_formats_sdm845
		},
	},
};

static const struct camss_subdev_resources csid_res_x1e80100[] = {
	/* CSID0 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb",
			   "cpas_fast_ahb", "csid", "csid_csiphy_rx" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 64000000, 80000000 },
				{ 80000000,  100000000, 200000000,
				  300000000, 400000000 },
				{ 300000000, 400000000, 480000000 },
				{ 300000000, 400000000, 480000000 }, },
		.reg = { "csid0" },
		.interrupt = { "csid0" },
		.csid = {
			.hw_ops = &csid_ops_680,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		},
	},
	/* CSID1 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb",
			   "cpas_fast_ahb", "csid", "csid_csiphy_rx" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 64000000, 80000000 },
				{ 80000000,  100000000, 200000000,
				  300000000, 400000000 },
				{ 300000000, 400000000, 480000000 },
				{ 300000000, 400000000, 480000000 }, },
		.reg = { "csid1" },
		.interrupt = { "csid1" },
		.csid = {
			.hw_ops = &csid_ops_680,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		},
	},
	/* CSID2 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb",
			   "cpas_fast_ahb", "csid", "csid_csiphy_rx" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 64000000, 80000000 },
				{ 80000000,  100000000, 200000000,
				  300000000, 400000000 },
				{ 300000000, 400000000, 480000000 },
				{ 300000000, 400000000, 480000000 }, },
		.reg = { "csid2" },
		.interrupt = { "csid2" },
		.csid = {
			.hw_ops = &csid_ops_680,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		},
	},
	/* CSID_LITE0 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb",
			   "cpas_fast_ahb", "csid", "csid_csiphy_rx" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 64000000, 80000000 },
				{ 80000000,  100000000, 200000000,
				  300000000, 400000000 },
				{ 300000000, 400000000, 480000000 },
				{ 300000000, 400000000, 480000000 }, },
		.reg = { "csid_lite0" },
		.interrupt = { "csid_lite0" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_680,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
	/* CSID_LITE1 */
	{
		.regulators = {},
		.clock = { "gcc_axi_hf", "gcc_axi_sf", "cpas_ahb",
			   "cpas_fast_ahb", "csid", "csid_csiphy_rx" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 64000000, 80000000 },
				{ 80000000,  100000000, 200000000,
				  300000000, 400000000 },
				{ 300000000, 400000000, 480000000 },
				{ 300000000, 400000000, 480000000 }, },

		.reg = { "csid_lite1" },
		.interrupt = { "csid_lite1" },
		.csid = {
			.is_lite = true,
			.hw_ops = &csid_ops_680,
			.parent_dev_ops = &vfe_parent_dev_ops,
			.formats = &csid_formats_gen2
		}
	},
};

static const struct camss_subdev_resources vfe_res_x1e80100[] = {
	/* IFE0 */
	{
		.regulators = {},
		.clock = {"camnoc_rt_axi", "camnoc_nrt_axi", "cpas_ahb",
			  "cpas_fast_ahb", "cpas_vfe0", "vfe0_fast_ahb",
			  "vfe0" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 345600000, 432000000, 594000000, 675000000,
				  727000000 }, },
		.reg = { "vfe0" },
		.interrupt = { "vfe0" },
		.vfe = {
			.line_num = 4,
			.pd_name = "ife0",
			.hw_ops = &vfe_ops_680,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		},
	},
	/* IFE1 */
	{
		.regulators = {},
		.clock = { "camnoc_rt_axi", "camnoc_nrt_axi", "cpas_ahb",
			   "cpas_fast_ahb", "cpas_vfe1", "vfe1_fast_ahb",
			   "vfe1"  },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 345600000, 432000000, 594000000, 675000000,
				  727000000 }, },
		.reg = { "vfe1" },
		.interrupt = { "vfe1" },
		.vfe = {
			.line_num = 4,
			.pd_name = "ife1",
			.hw_ops = &vfe_ops_680,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_x1e80100
		},
	},
	/* IFE_LITE_0 */
	{
		.regulators = {},
		.clock = { "camnoc_rt_axi", "camnoc_nrt_axi", "cpas_ahb",
			   "vfe_lite_ahb", "cpas_vfe_lite", "vfe_lite",
			   "vfe_lite_csid" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 266666667, 400000000, 480000000 },
				{ 266666667, 400000000, 480000000 }, },
		.reg = { "vfe_lite0" },
		.interrupt = { "vfe_lite0" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_680,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		},
	},
	/* IFE_LITE_1 */
	{
		.regulators = {},
		.clock = { "camnoc_rt_axi", "camnoc_nrt_axi", "cpas_ahb",
			   "vfe_lite_ahb", "cpas_vfe_lite", "vfe_lite",
			   "vfe_lite_csid" },
		.clock_rate = { { 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 0 },
				{ 266666667, 400000000, 480000000 },
				{ 266666667, 400000000, 480000000 }, },
		.reg = { "vfe_lite1" },
		.interrupt = { "vfe_lite1" },
		.vfe = {
			.is_lite = true,
			.line_num = 4,
			.hw_ops = &vfe_ops_680,
			.formats_rdi = &vfe_formats_rdi_845,
			.formats_pix = &vfe_formats_pix_845
		},
	},
};

static const struct resources_icc icc_res_x1e80100[] = {
	{
		.name = "ahb",
		.icc_bw_tbl.avg = 150000,
		.icc_bw_tbl.peak = 300000,
	},
	{
		.name = "hf_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
	{
		.name = "sf_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
	{
		.name = "sf_icp_mnoc",
		.icc_bw_tbl.avg = 2097152,
		.icc_bw_tbl.peak = 2097152,
	},
};

static const struct resources_wrapper csid_wrapper_res_x1e80100 = {
	.reg = "csid_wrapper",
};

/*
 * camss_add_clock_margin - Add margin to clock frequency rate
 * @rate: Clock frequency rate
 *
 * When making calculations with physical clock frequency values
 * some safety margin must be added. Add it.
 */
inline void camss_add_clock_margin(u64 *rate)
{
	*rate *= CAMSS_CLOCK_MARGIN_NUMERATOR;
	*rate = div_u64(*rate, CAMSS_CLOCK_MARGIN_DENOMINATOR);
}

/*
 * camss_enable_clocks - Enable multiple clocks
 * @nclocks: Number of clocks in clock array
 * @clock: Clock array
 * @dev: Device
 *
 * Return 0 on success or a negative error code otherwise
 */
int camss_enable_clocks(int nclocks, struct camss_clock *clock,
			struct device *dev)
{
	int ret;
	int i;

	for (i = 0; i < nclocks; i++) {
		ret = clk_prepare_enable(clock[i].clk);
		if (ret) {
			dev_err(dev, "clock enable failed: %d\n", ret);
			goto error;
		}
	}

	return 0;

error:
	for (i--; i >= 0; i--)
		clk_disable_unprepare(clock[i].clk);

	return ret;
}

/*
 * camss_disable_clocks - Disable multiple clocks
 * @nclocks: Number of clocks in clock array
 * @clock: Clock array
 */
void camss_disable_clocks(int nclocks, struct camss_clock *clock)
{
	int i;

	for (i = nclocks - 1; i >= 0; i--)
		clk_disable_unprepare(clock[i].clk);
}

/*
 * camss_find_sensor_pad - Find the media pad via which the sensor is linked
 * @entity: Media entity to start searching from
 *
 * Return a pointer to sensor media pad or NULL if not found
 */
struct media_pad *camss_find_sensor_pad(struct media_entity *entity)
{
	struct media_pad *pad;

	while (1) {
		pad = &entity->pads[0];
		if (!(pad->flags & MEDIA_PAD_FL_SINK))
			return NULL;

		pad = media_pad_remote_pad_first(pad);
		if (!pad || !is_media_entity_v4l2_subdev(pad->entity))
			return NULL;

		entity = pad->entity;

		if (entity->function == MEDIA_ENT_F_CAM_SENSOR)
			return pad;
	}
}

/**
 * camss_get_link_freq - Get link frequency from sensor
 * @entity: Media entity in the current pipeline
 * @bpp: Number of bits per pixel for the current format
 * @lanes: Number of lanes in the link to the sensor
 * @cphy: If C-PHY encoding is used.
 *
 * Return link frequency on success or a negative error code otherwise
 */
s64 camss_get_link_freq(struct media_entity *entity, unsigned int bpp,
			unsigned int lanes, const bool cphy)
{
	struct media_pad *sensor_pad;
	unsigned int div = lanes * 2 * (cphy ? CAMSS_CPHY_DIVISOR :
					       CAMSS_DPHY_DIVISOR);

	sensor_pad = camss_find_sensor_pad(entity);
	if (!sensor_pad)
		return -ENODEV;

	return v4l2_get_link_freq(sensor_pad, CAMSS_COMMON_PHY_DIVIDENT * bpp, div);
}

/*
 * camss_get_pixel_clock - Get pixel clock rate from sensor
 * @entity: Media entity in the current pipeline
 * @pixel_clock: Received pixel clock value
 *
 * Return 0 on success or a negative error code otherwise
 */
int camss_get_pixel_clock(struct media_entity *entity, u64 *pixel_clock)
{
	struct media_pad *sensor_pad;
	struct v4l2_subdev *subdev;
	struct v4l2_ctrl *ctrl;

	sensor_pad = camss_find_sensor_pad(entity);
	if (!sensor_pad)
		return -ENODEV;

	subdev = media_entity_to_v4l2_subdev(sensor_pad->entity);

	ctrl = v4l2_ctrl_find(subdev->ctrl_handler, V4L2_CID_PIXEL_RATE);

	if (!ctrl)
		return -EINVAL;

	*pixel_clock = v4l2_ctrl_g_ctrl_int64(ctrl);

	return 0;
}

int camss_pm_domain_on(struct camss *camss, int id)
{
	int ret = 0;

	if (id < camss->res->vfe_num) {
		struct vfe_device *vfe = &camss->vfe[id];

		ret = vfe->res->hw_ops->pm_domain_on(vfe);
	}

	return ret;
}

void camss_pm_domain_off(struct camss *camss, int id)
{
	if (id < camss->res->vfe_num) {
		struct vfe_device *vfe = &camss->vfe[id];

		vfe->res->hw_ops->pm_domain_off(vfe);
	}
}

static int vfe_parent_dev_ops_get(struct camss *camss, int id)
{
	int ret = -EINVAL;

	if (id < camss->res->vfe_num) {
		struct vfe_device *vfe = &camss->vfe[id];

		ret = vfe_get(vfe);
	}

	return ret;
}

static int vfe_parent_dev_ops_put(struct camss *camss, int id)
{
	if (id < camss->res->vfe_num) {
		struct vfe_device *vfe = &camss->vfe[id];

		vfe_put(vfe);
	}

	return 0;
}

static void __iomem
*vfe_parent_dev_ops_get_base_address(struct camss *camss, int id)
{
	if (id < camss->res->vfe_num) {
		struct vfe_device *vfe = &camss->vfe[id];

		return vfe->base;
	}

	return NULL;
}

static const struct parent_dev_ops vfe_parent_dev_ops = {
	.get = vfe_parent_dev_ops_get,
	.put = vfe_parent_dev_ops_put,
	.get_base_address = vfe_parent_dev_ops_get_base_address
};

/*
 * camss_parse_endpoint_node - Parse port endpoint node
 * @dev: CAMSS device
 * @ep: Device endpoint to be parsed
 * @csd: Parsed data from port endpoint node
 *
 * Return 0 on success or a negative error code on failure
 */
static int camss_parse_endpoint_node(struct device *dev,
				     struct fwnode_handle *ep,
				     struct camss_async_subdev *csd)
{
	struct csiphy_lanes_cfg *lncfg = &csd->interface.csi2.lane_cfg;
	struct v4l2_mbus_config_mipi_csi2 *mipi_csi2;
	struct v4l2_fwnode_endpoint vep = { { 0 } };
	unsigned int i;
	int ret;

	ret = v4l2_fwnode_endpoint_parse(ep, &vep);
	if (ret)
		return ret;

	switch (vep.bus_type) {
	case V4L2_MBUS_CSI2_CPHY:
	case V4L2_MBUS_CSI2_DPHY:
		break;
	default:
		dev_err(dev, "Unsupported bus type %d\n", vep.bus_type);
		return -EINVAL;
	}

	csd->interface.csiphy_id = vep.base.port;

	mipi_csi2 = &vep.bus.mipi_csi2;
	lncfg->num_data = mipi_csi2->num_data_lanes;
	lncfg->phy_cfg = vep.bus_type;

	if (lncfg->phy_cfg != V4L2_MBUS_CSI2_CPHY) {
		lncfg->clk.pos = mipi_csi2->clock_lane;
		lncfg->clk.pol = mipi_csi2->lane_polarities[0];
	}

	lncfg->data = devm_kcalloc(dev,
				   lncfg->num_data, sizeof(*lncfg->data),
				   GFP_KERNEL);
	if (!lncfg->data)
		return -ENOMEM;

	for (i = 0; i < lncfg->num_data; i++) {
		lncfg->data[i].pos = mipi_csi2->data_lanes[i];
		lncfg->data[i].pol = mipi_csi2->lane_polarities[i + 1];
	}

	return 0;
}

/*
 * camss_parse_ports - Parse ports node
 * @dev: CAMSS device
 *
 * Return 0 on success or a negative error code on failure
 */
static int camss_parse_ports(struct camss *camss)
{
	struct device *dev = camss->dev;
	struct fwnode_handle *fwnode = dev_fwnode(dev), *ep;
	int ret;

	fwnode_graph_for_each_endpoint(fwnode, ep) {
		struct camss_async_subdev *csd;

		csd = v4l2_async_nf_add_fwnode_remote(&camss->notifier, ep,
						      typeof(*csd));
		if (IS_ERR(csd)) {
			ret = PTR_ERR(csd);
			goto err_cleanup;
		}

		ret = camss_parse_endpoint_node(dev, ep, csd);
		if (ret < 0)
			goto err_cleanup;
	}

	return 0;

err_cleanup:
	fwnode_handle_put(ep);

	return ret;
}

/*
 * camss_init_subdevices - Initialize subdev structures and resources
 * @camss: CAMSS device
 *
 * Return 0 on success or a negative error code on failure
 */
static int camss_init_subdevices(struct camss *camss)
{
	struct platform_device *pdev = to_platform_device(camss->dev);
	const struct camss_resources *res = camss->res;
	unsigned int i;
	int ret;

	for (i = 0; i < camss->res->csiphy_num; i++) {
		ret = msm_csiphy_subdev_init(camss, &camss->csiphy[i],
					     &res->csiphy_res[i],
					     res->csiphy_res[i].csiphy.id);
		if (ret < 0) {
			dev_err(camss->dev,
				"Failed to init csiphy%d sub-device: %d\n",
				i, ret);
			return ret;
		}
	}

	/* note: SM8250 requires VFE to be initialized before CSID */
	for (i = 0; i < camss->res->vfe_num; i++) {
		ret = msm_vfe_subdev_init(camss, &camss->vfe[i],
					  &res->vfe_res[i], i);
		if (ret < 0) {
			dev_err(camss->dev,
				"Fail to init vfe%d sub-device: %d\n", i, ret);
			return ret;
		}
	}

	/* Get optional CSID wrapper regs shared between CSID devices */
	if (res->csid_wrapper_res) {
		char *reg = res->csid_wrapper_res->reg;
		void __iomem *base;

		base = devm_platform_ioremap_resource_byname(pdev, reg);
		if (IS_ERR(base))
			return PTR_ERR(base);
		camss->csid_wrapper_base = base;
	}

	for (i = 0; i < camss->res->csid_num; i++) {
		ret = msm_csid_subdev_init(camss, &camss->csid[i],
					   &res->csid_res[i], i);
		if (ret < 0) {
			dev_err(camss->dev,
				"Failed to init csid%d sub-device: %d\n",
				i, ret);
			return ret;
		}
	}

	ret = msm_ispif_subdev_init(camss, res->ispif_res);
	if (ret < 0) {
		dev_err(camss->dev, "Failed to init ispif sub-device: %d\n",
		ret);
		return ret;
	}

	return 0;
}

/*
 * camss_link_err - print error in case link creation fails
 * @src_name: name for source of the link
 * @sink_name: name for sink of the link
 */
inline void camss_link_err(struct camss *camss,
			   const char *src_name,
			   const char *sink_name,
			   int ret)
{
	dev_err(camss->dev,
		"Failed to link %s->%s entities: %d\n",
		src_name,
		sink_name,
		ret);
}

/*
 * camss_link_entities - Register subdev nodes and create links
 * @camss: CAMSS device
 *
 * Return 0 on success or a negative error code on failure
 */
static int camss_link_entities(struct camss *camss)
{
	int i, j, k;
	int ret;

	for (i = 0; i < camss->res->csiphy_num; i++) {
		for (j = 0; j < camss->res->csid_num; j++) {
			ret = media_create_pad_link(&camss->csiphy[i].subdev.entity,
						    MSM_CSIPHY_PAD_SRC,
						    &camss->csid[j].subdev.entity,
						    MSM_CSID_PAD_SINK,
						    0);
			if (ret < 0) {
				camss_link_err(camss,
					       camss->csiphy[i].subdev.entity.name,
					       camss->csid[j].subdev.entity.name,
					       ret);
				return ret;
			}
		}
	}

	if (camss->ispif) {
		for (i = 0; i < camss->res->csid_num; i++) {
			for (j = 0; j < camss->ispif->line_num; j++) {
				ret = media_create_pad_link(&camss->csid[i].subdev.entity,
							    MSM_CSID_PAD_SRC,
							    &camss->ispif->line[j].subdev.entity,
							    MSM_ISPIF_PAD_SINK,
							    0);
				if (ret < 0) {
					camss_link_err(camss,
						       camss->csid[i].subdev.entity.name,
						       camss->ispif->line[j].subdev.entity.name,
						       ret);
					return ret;
				}
			}
		}

		for (i = 0; i < camss->ispif->line_num; i++)
			for (k = 0; k < camss->res->vfe_num; k++)
				for (j = 0; j < camss->vfe[k].res->line_num; j++) {
					struct v4l2_subdev *ispif = &camss->ispif->line[i].subdev;
					struct v4l2_subdev *vfe = &camss->vfe[k].line[j].subdev;

					ret = media_create_pad_link(&ispif->entity,
								    MSM_ISPIF_PAD_SRC,
								    &vfe->entity,
								    MSM_VFE_PAD_SINK,
								    0);
					if (ret < 0) {
						camss_link_err(camss, ispif->entity.name,
							       vfe->entity.name,
							       ret);
						return ret;
					}
				}
	} else {
		for (i = 0; i < camss->res->csid_num; i++)
			for (k = 0; k < camss->res->vfe_num; k++)
				for (j = 0; j < camss->vfe[k].res->line_num; j++) {
					struct v4l2_subdev *csid = &camss->csid[i].subdev;
					struct v4l2_subdev *vfe = &camss->vfe[k].line[j].subdev;

					ret = media_create_pad_link(&csid->entity,
								    MSM_CSID_PAD_FIRST_SRC + j,
								    &vfe->entity,
								    MSM_VFE_PAD_SINK,
								    0);
					if (ret < 0) {
						camss_link_err(camss, csid->entity.name,
							       vfe->entity.name,
							       ret);
						return ret;
					}
				}
	}

	return 0;
}

void camss_reg_update(struct camss *camss, int hw_id, int port_id, bool is_clear)
{
	struct csid_device *csid;

	if (hw_id < camss->res->csid_num) {
		csid = &camss->csid[hw_id];

		csid->res->hw_ops->reg_update(csid, port_id, is_clear);
	}
}

void camss_buf_done(struct camss *camss, int hw_id, int port_id)
{
	struct vfe_device *vfe;

	if (hw_id < camss->res->vfe_num) {
		vfe = &camss->vfe[hw_id];

		vfe->res->hw_ops->vfe_buf_done(vfe, port_id);
	}
}

/*
 * camss_register_entities - Register subdev nodes and create links
 * @camss: CAMSS device
 *
 * Return 0 on success or a negative error code on failure
 */
static int camss_register_entities(struct camss *camss)
{
	int i;
	int ret;

	for (i = 0; i < camss->res->csiphy_num; i++) {
		ret = msm_csiphy_register_entity(&camss->csiphy[i],
						 &camss->v4l2_dev);
		if (ret < 0) {
			dev_err(camss->dev,
				"Failed to register csiphy%d entity: %d\n",
				i, ret);
			goto err_reg_csiphy;
		}
	}

	for (i = 0; i < camss->res->csid_num; i++) {
		ret = msm_csid_register_entity(&camss->csid[i],
					       &camss->v4l2_dev);
		if (ret < 0) {
			dev_err(camss->dev,
				"Failed to register csid%d entity: %d\n",
				i, ret);
			goto err_reg_csid;
		}
	}

	ret = msm_ispif_register_entities(camss->ispif,
					  &camss->v4l2_dev);
	if (ret < 0) {
		dev_err(camss->dev, "Failed to register ispif entities: %d\n", ret);
		goto err_reg_ispif;
	}

	for (i = 0; i < camss->res->vfe_num; i++) {
		ret = msm_vfe_register_entities(&camss->vfe[i],
						&camss->v4l2_dev);
		if (ret < 0) {
			dev_err(camss->dev,
				"Failed to register vfe%d entities: %d\n",
				i, ret);
			goto err_reg_vfe;
		}
	}

	return 0;

err_reg_vfe:
	for (i--; i >= 0; i--)
		msm_vfe_unregister_entities(&camss->vfe[i]);

err_reg_ispif:
	msm_ispif_unregister_entities(camss->ispif);

	i = camss->res->csid_num;
err_reg_csid:
	for (i--; i >= 0; i--)
		msm_csid_unregister_entity(&camss->csid[i]);

	i = camss->res->csiphy_num;
err_reg_csiphy:
	for (i--; i >= 0; i--)
		msm_csiphy_unregister_entity(&camss->csiphy[i]);

	return ret;
}

/*
 * camss_unregister_entities - Unregister subdev nodes
 * @camss: CAMSS device
 *
 * Return 0 on success or a negative error code on failure
 */
static void camss_unregister_entities(struct camss *camss)
{
	unsigned int i;

	for (i = 0; i < camss->res->csiphy_num; i++)
		msm_csiphy_unregister_entity(&camss->csiphy[i]);

	for (i = 0; i < camss->res->csid_num; i++)
		msm_csid_unregister_entity(&camss->csid[i]);

	msm_ispif_unregister_entities(camss->ispif);

	for (i = 0; i < camss->res->vfe_num; i++)
		msm_vfe_unregister_entities(&camss->vfe[i]);
}

static int camss_subdev_notifier_bound(struct v4l2_async_notifier *async,
				       struct v4l2_subdev *subdev,
				       struct v4l2_async_connection *asd)
{
	struct camss *camss = container_of(async, struct camss, notifier);
	struct camss_async_subdev *csd =
		container_of(asd, struct camss_async_subdev, asd);
	u8 id = csd->interface.csiphy_id;
	struct csiphy_device *csiphy = &camss->csiphy[id];

	csiphy->cfg.csi2 = &csd->interface.csi2;
	subdev->host_priv = csiphy;

	return 0;
}

static int camss_subdev_notifier_complete(struct v4l2_async_notifier *async)
{
	struct camss *camss = container_of(async, struct camss, notifier);
	struct v4l2_device *v4l2_dev = &camss->v4l2_dev;
	struct v4l2_subdev *sd;

	list_for_each_entry(sd, &v4l2_dev->subdevs, list) {
		struct csiphy_device *csiphy = sd->host_priv;
		struct media_entity *input, *sensor;
		unsigned int i;
		int ret;

		if (!csiphy)
			continue;

		input = &csiphy->subdev.entity;
		sensor = &sd->entity;

		for (i = 0; i < sensor->num_pads; i++) {
			if (sensor->pads[i].flags & MEDIA_PAD_FL_SOURCE)
				break;
		}
		if (i == sensor->num_pads) {
			dev_err(camss->dev,
				"No source pad in external entity\n");
			return -EINVAL;
		}

		ret = media_create_pad_link(sensor, i, input,
					    MSM_CSIPHY_PAD_SINK,
					    MEDIA_LNK_FL_IMMUTABLE | MEDIA_LNK_FL_ENABLED);
		if (ret < 0) {
			camss_link_err(camss, sensor->name, input->name, ret);
			return ret;
		}
	}

	return v4l2_device_register_subdev_nodes(&camss->v4l2_dev);
}

static const struct v4l2_async_notifier_operations camss_subdev_notifier_ops = {
	.bound = camss_subdev_notifier_bound,
	.complete = camss_subdev_notifier_complete,
};

static const struct media_device_ops camss_media_ops = {
	.link_notify = v4l2_pipeline_link_notify,
};

static int camss_configure_pd(struct camss *camss)
{
	const struct camss_resources *res = camss->res;
	struct device *dev = camss->dev;
	int vfepd_num;
	int i;
	int ret;

	camss->genpd_num = of_count_phandle_with_args(dev->of_node,
						      "power-domains",
						      "#power-domain-cells");
	if (camss->genpd_num < 0) {
		dev_err(dev, "Power domains are not defined for camss\n");
		return camss->genpd_num;
	}

	/*
	 * If a platform device has just one power domain, then it is attached
	 * at platform_probe() level, thus there shall be no need and even no
	 * option to attach it again, this is the case for CAMSS on MSM8916.
	 */
	if (camss->genpd_num == 1)
		return 0;

	/* count the # of VFEs which have flagged power-domain */
	for (vfepd_num = i = 0; i < camss->res->vfe_num; i++) {
		if (res->vfe_res[i].vfe.has_pd)
			vfepd_num++;
	}

	/*
	 * If the number of power-domains is greater than the number of VFEs
	 * then the additional power-domain is for the entire CAMSS block.
	 */
	if (!(camss->genpd_num > vfepd_num))
		return 0;

	/*
	 * If a power-domain name is defined try to use it.
	 * It is possible we are running a new kernel with an old dtb so
	 * fallback to indexes even if a pd_name is defined but not found.
	 */
	if (camss->res->pd_name) {
		camss->genpd = dev_pm_domain_attach_by_name(camss->dev,
							    camss->res->pd_name);
		if (IS_ERR(camss->genpd))
			return PTR_ERR(camss->genpd);
	}

	if (!camss->genpd) {
		/*
		 * Legacy magic index. TITAN_TOP GDSC must be the last
		 * item in the power-domain list.
		 */
		camss->genpd = dev_pm_domain_attach_by_id(camss->dev,
							  camss->genpd_num - 1);
		if (IS_ERR(camss->genpd))
			return PTR_ERR(camss->genpd);
	}

	if (!camss->genpd)
		return -ENODEV;

	camss->genpd_link = device_link_add(camss->dev, camss->genpd,
					    DL_FLAG_STATELESS | DL_FLAG_PM_RUNTIME |
					    DL_FLAG_RPM_ACTIVE);
	if (!camss->genpd_link) {
		ret = -EINVAL;
		goto fail_pm;
	}

	return 0;

fail_pm:
	dev_pm_domain_detach(camss->genpd, true);

	return ret;
}

static int camss_icc_get(struct camss *camss)
{
	const struct resources_icc *icc_res;
	int i;

	icc_res = camss->res->icc_res;

	for (i = 0; i < camss->res->icc_path_num; i++) {
		camss->icc_path[i] = devm_of_icc_get(camss->dev,
						     icc_res[i].name);
		if (IS_ERR(camss->icc_path[i]))
			return PTR_ERR(camss->icc_path[i]);
	}

	return 0;
}

static void camss_genpd_subdevice_cleanup(struct camss *camss)
{
	int i;

	for (i = 0; i < camss->res->vfe_num; i++)
		msm_vfe_genpd_cleanup(&camss->vfe[i]);
}

static void camss_genpd_cleanup(struct camss *camss)
{
	if (camss->genpd_num == 1)
		return;

	camss_genpd_subdevice_cleanup(camss);

	if (camss->genpd_link)
		device_link_del(camss->genpd_link);

	dev_pm_domain_detach(camss->genpd, true);
}

#define CAMSS_X1E80100_RTCDM1_PHYS_BASE 0x0ac26000
#define CAMSS_X1E80100_RTCDM1_SIZE      SZ_4K

/*
 * RT-CDM v2.1 layout. Public Qualcomm source names the registers only; every
 * value and ordering below is pinned to the same-machine Windows oracles.
 */
#define CAMSS_RTCDM_HW_VERSION          0x000
#define CAMSS_RTCDM_RST_CMD             0x010
#define CAMSS_RTCDM_CORE_CFG            0x018
#define CAMSS_RTCDM_CORE_EN             0x01c
#define CAMSS_RTCDM_FE_CFG              0x020
#define CAMSS_RTCDM_IRQ0_MASK           0x030
#define CAMSS_RTCDM_FIFO0_BASE          0x050
#define CAMSS_RTCDM_FIFO0_LEN           0x054
#define CAMSS_RTCDM_FIFO0_STORE         0x058
#define CAMSS_RTCDM_FIFO0_CFG           0x05c

#define CAMSS_RTCDM_WINDOWS_HW_VERSION  0x20010000
#define CAMSS_RTCDM_WINDOWS_FE_CFG      0x07ff000f
#define CAMSS_RTCDM_WINDOWS_FIFO0_CFG   0x01000000
#define CAMSS_RTCDM_WINDOWS_CORE_CFG    0x0000011f
#define CAMSS_RTCDM_WINDOWS_RESET_CMD   0x00000009
#define CAMSS_RTCDM_WINDOWS_RESET_MASK  0x00000001
#define CAMSS_RTCDM_WINDOWS_CORE_EN     0x00000001
#define CAMSS_RTCDM_WINDOWS_FIFO_LEN_HIGH    BIT(20)
#define CAMSS_RTCDM_WINDOWS_FIFO_LOW20  GENMASK(19, 0)
#define CAMSS_RTCDM_WINDOWS_WAIT_MS     500

/* RT-CDM v2.1 IRQ layout; Qualcomm source is naming/layout only. */
#define CAMSS_RTCDM_IRQ_CONTEXT_STATUS  0x02c
#define CAMSS_RTCDM_IRQ0_CLEAR          0x034
#define CAMSS_RTCDM_IRQ0_CLEAR_CMD      0x038
#define CAMSS_RTCDM_IRQ0_STATUS         0x044
#define CAMSS_RTCDM_USR_DATA            0x080

#define CAMSS_RTCDM_IRQ_RESET_DONE      BIT(0)
#define CAMSS_RTCDM_IRQ_INLINE          BIT(1)
#define CAMSS_RTCDM_IRQ_BL_DONE         BIT(2)
#define CAMSS_RTCDM_IRQ_INVALID_CMD     BIT(16)
#define CAMSS_RTCDM_IRQ_OVERFLOW        BIT(17)
#define CAMSS_RTCDM_IRQ_AHB_ERROR       BIT(18)
#define CAMSS_RTCDM_IRQ_ERRORS          (CAMSS_RTCDM_IRQ_INVALID_CMD | \
					 CAMSS_RTCDM_IRQ_OVERFLOW | \
					 CAMSS_RTCDM_IRQ_AHB_ERROR)
#define CAMSS_RTCDM_IRQ_KNOWN           (CAMSS_RTCDM_IRQ_RESET_DONE | \
					 CAMSS_RTCDM_IRQ_INLINE | \
					 CAMSS_RTCDM_IRQ_BL_DONE | \
					 CAMSS_RTCDM_IRQ_ERRORS)
#define CAMSS_RTCDM_WINDOWS_IRQ0_MASK   0x00070007

static_assert(CAMSS_RTCDM_IRQ_KNOWN == CAMSS_RTCDM_WINDOWS_IRQ0_MASK);

/*
 * The IRQ remains disabled in this E003h layer. There is intentionally no
 * public arm/enable function yet. The body below records the v2.1 FIFO0
 * status/clear mechanism for the next gate, but is unreachable while
 * irq_armed is false and the IRQ was requested with IRQF_NO_AUTOEN.
 */
static irqreturn_t camss_rtcdm1_isr(int irq, void *data)
{
	struct camss *camss = data;
	struct camss_rtcdm *rt = &camss->rtcdm1;
	u32 context;
	u32 status;
	u32 user_data;

	if (irq != rt->irq || !READ_ONCE(rt->irq_armed))
		return IRQ_NONE;

	context = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ_CONTEXT_STATUS);
	if (!(context & BIT(0)))
		return IRQ_NONE;

	/* The accepted front path is FIFO0-only. Fail closed on any other FIFO. */
	if (context & ~BIT(0)) {
		WRITE_ONCE(rt->faulted, true);
		disable_irq_nosync(rt->irq);
		WRITE_ONCE(rt->irq_armed, false);
		return IRQ_HANDLED;
	}

	status = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ0_STATUS);
	if (!status)
		return IRQ_NONE;

	user_data = readl_relaxed(rt->base + CAMSS_RTCDM_USR_DATA);
	writel_relaxed(status, rt->base + CAMSS_RTCDM_IRQ0_CLEAR);
	writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ0_CLEAR_CMD);

	WRITE_ONCE(rt->last_irq_context, context);
	WRITE_ONCE(rt->last_irq_status, status);
	WRITE_ONCE(rt->last_user_data, user_data);

	if ((status & ~CAMSS_RTCDM_IRQ_KNOWN) || (status & CAMSS_RTCDM_IRQ_ERRORS)) {
		WRITE_ONCE(rt->faulted, true);
		disable_irq_nosync(rt->irq);
		WRITE_ONCE(rt->irq_armed, false);
	}

	/* Windows blocks on reset-done and BL-done events; inline is informational. */
	if (status & (CAMSS_RTCDM_IRQ_RESET_DONE | CAMSS_RTCDM_IRQ_BL_DONE))
		complete(&rt->completion);

	return IRQ_HANDLED;
}

/*
 * E003h static-only Windows RT-CDM1 recipe.
 *
 * These helpers are retained through an internal __used ops table below, but
 * that table has no runtime reference in this patch. They therefore cannot be
 * reached by probe, media setup, stream-on/off, or teardown. The purpose of
 * this layer is to compile the exact already-proven state machine before any
 * live Linux authorization.
 *
 * In particular FE_CFG/FIFO0_CFG are never written. The two-cycle Windows
 * oracle proves that they reappear after power collapse before the front CDM
 * object performs its first MMIO write, so Linux may only validate them.
 */
static int camss_rtcdm1_windows_preflight(struct camss *camss)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;
	u32 hw_version;
	u32 fe_cfg;
	u32 fifo0_cfg;

	if (!rt->present || !rt->base)
		return -ENODEV;

	hw_version = readl_relaxed(rt->base + CAMSS_RTCDM_HW_VERSION);
	fe_cfg = readl_relaxed(rt->base + CAMSS_RTCDM_FE_CFG);
	fifo0_cfg = readl_relaxed(rt->base + CAMSS_RTCDM_FIFO0_CFG);

	if (hw_version != CAMSS_RTCDM_WINDOWS_HW_VERSION ||
	    fe_cfg != CAMSS_RTCDM_WINDOWS_FE_CFG ||
	    fifo0_cfg != CAMSS_RTCDM_WINDOWS_FIFO0_CFG)
		return -ENODEV;

	return 0;
}

static int camss_rtcdm1_windows_wait(struct camss_rtcdm *rt, u32 required)
{
	unsigned long left;
	u32 status;

	left = wait_for_completion_timeout(&rt->completion,
					msecs_to_jiffies(CAMSS_RTCDM_WINDOWS_WAIT_MS));
	if (!left)
		return -ETIMEDOUT;
	if (READ_ONCE(rt->faulted))
		return -EIO;

	status = READ_ONCE(rt->last_irq_status);
	if (!(status & required) || (status & ~CAMSS_RTCDM_IRQ_KNOWN))
		return -EIO;

	return 0;
}

static int camss_rtcdm1_windows_open_init(struct camss *camss)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;
	int ret;

	/* Positive Windows timing requires this read-only gate before any write. */
	ret = camss_rtcdm1_windows_preflight(camss);
	if (ret)
		return ret;

	mutex_lock(&rt->lock);
	if (READ_ONCE(rt->irq_armed)) {
		ret = -EBUSY;
		goto out_unlock;
	}

	reinit_completion(&rt->completion);
	WRITE_ONCE(rt->faulted, false);
	WRITE_ONCE(rt->last_irq_context, 0);
	WRITE_ONCE(rt->last_irq_status, 0);
	WRITE_ONCE(rt->last_user_data, 0);

	/* Linux interrupt-controller mechanics; no RT-CDM register is changed. */
	WRITE_ONCE(rt->irq_armed, true);
	enable_irq(rt->irq);

	/* Exact same-machine Windows open/init MMIO order. */
	writel_relaxed(CAMSS_RTCDM_WINDOWS_RESET_MASK,
		       rt->base + CAMSS_RTCDM_IRQ0_MASK);
	writel_relaxed(CAMSS_RTCDM_WINDOWS_RESET_CMD,
		       rt->base + CAMSS_RTCDM_RST_CMD);

	ret = camss_rtcdm1_windows_wait(rt, CAMSS_RTCDM_IRQ_RESET_DONE);
	if (ret) {
		disable_irq(rt->irq);
		WRITE_ONCE(rt->irq_armed, false);
		goto out_unlock;
	}

	/* qccamisp8380.sys executes DMB SY immediately before CORE_CFG. */
	dmb(sy);
	writel_relaxed(CAMSS_RTCDM_WINDOWS_CORE_CFG,
		       rt->base + CAMSS_RTCDM_CORE_CFG);

out_unlock:
	mutex_unlock(&rt->lock);
	return ret;
}

static int camss_rtcdm1_windows_start(struct camss *camss)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;
	int ret = 0;

	if (!rt->present || !rt->base)
		return -ENODEV;

	mutex_lock(&rt->lock);
	if (!READ_ONCE(rt->irq_armed) || READ_ONCE(rt->faulted)) {
		ret = -EIO;
		goto out_unlock;
	}

	writel_relaxed(CAMSS_RTCDM_WINDOWS_IRQ0_MASK,
		       rt->base + CAMSS_RTCDM_IRQ0_MASK);
	dmb(sy);
	writel_relaxed(CAMSS_RTCDM_WINDOWS_CORE_EN,
		       rt->base + CAMSS_RTCDM_CORE_EN);

out_unlock:
	mutex_unlock(&rt->lock);
	return ret;
}

static int camss_rtcdm1_windows_fifo0_commit(struct camss *camss,
					     u32 base, u32 len_low20)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;
	u32 encoded_len;
	int ret = 0;

	if (!rt->present || !rt->base)
		return -ENODEV;
	if (!base || !len_low20 || (len_low20 & ~CAMSS_RTCDM_WINDOWS_FIFO_LOW20))
		return -EINVAL;

	/* Windows BFI at RVA 0x2887c replaces bits 31:20 with 0x001. */
	encoded_len = len_low20 | CAMSS_RTCDM_WINDOWS_FIFO_LEN_HIGH;

	mutex_lock(&rt->lock);
	if (!READ_ONCE(rt->irq_armed) || READ_ONCE(rt->faulted)) {
		ret = -EIO;
		goto out_unlock;
	}

	reinit_completion(&rt->completion);
	WRITE_ONCE(rt->last_irq_context, 0);
	WRITE_ONCE(rt->last_irq_status, 0);
	WRITE_ONCE(rt->last_user_data, 0);

	/* Exact Windows dynamic FIFO0 commit: BASE -> encoded LEN -> STORE. */
	writel_relaxed(base, rt->base + CAMSS_RTCDM_FIFO0_BASE);
	writel_relaxed(encoded_len, rt->base + CAMSS_RTCDM_FIFO0_LEN);
	writel_relaxed(1, rt->base + CAMSS_RTCDM_FIFO0_STORE);

	ret = camss_rtcdm1_windows_wait(rt, CAMSS_RTCDM_IRQ_BL_DONE);

out_unlock:
	mutex_unlock(&rt->lock);
	return ret;
}

static void camss_rtcdm1_windows_stop(struct camss *camss)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;

	if (!rt->present || !rt->base)
		return;

	mutex_lock(&rt->lock);
	/* Exact DEVICE_STOP CDM action: mask IRQ0 only. No CORE_EN=0/reset. */
	writel_relaxed(0, rt->base + CAMSS_RTCDM_IRQ0_MASK);
	mutex_unlock(&rt->lock);
}

struct camss_rtcdm1_windows_static_ops {
	int (*preflight)(struct camss *camss);
	int (*open_init)(struct camss *camss);
	int (*start)(struct camss *camss);
	int (*fifo0_commit)(struct camss *camss, u32 base, u32 len_low20);
	void (*stop)(struct camss *camss);
};

/*
 * Deliberately retained for static/build inspection only. Search/call-graph
 * policy for E003h requires zero references to this object outside its own
 * definition until a later runtime gate is explicitly authorized.
 */
static const struct camss_rtcdm1_windows_static_ops
camss_rtcdm1_windows_recipe __used = {
	.preflight = camss_rtcdm1_windows_preflight,
	.open_init = camss_rtcdm1_windows_open_init,
	.start = camss_rtcdm1_windows_start,
	.fifo0_commit = camss_rtcdm1_windows_fifo0_commit,
	.stop = camss_rtcdm1_windows_stop,
};

/*
 * E003h static-only IFE command-corpus materializer.
 *
 * The exact command and DMI payload bytes remain local oracle inputs and are
 * intentionally not embedded in the kernel source. Callers must provide four
 * normalized command templates whose 46 DMI address fields and four
 * start-dependent period_cfg values are zero, plus the 16 exact DMI payload
 * byte strings and two logical period values explicitly: packet 0 and the shared
 * packet 1/2/3 value. The 16 startup words at
 * +0x3b70/+0x3d78..+0x3d84 remain exact template data: Windows proves their
 * startup values invariant even though some live registers mutate afterward.
 * This layer copies into Linux-owned coherent memory and replaces only the
 * proven DMI/period holes.
 *
 * Linux deliberately does not reproduce Windows' 0xa000 command-slot stride or
 * DMI source-window offsets. Main lists use independent 4 KiB Linux slots and
 * the 16 unique DMI payloads use a compact 64-byte-aligned Linux layout.
 * Nothing here submits FIFO0 or references the live RT-CDM recipe above.
 */
#define CAMSS_RTCDM1_CORPUS_PACKET_COUNT	4
#define CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT	16
#define CAMSS_RTCDM1_CORPUS_DMI_COUNT		46
#define CAMSS_RTCDM1_CORPUS_DYNAMIC_VALUE_COUNT	2
#define CAMSS_RTCDM1_CORPUS_DYNAMIC_PATCH_COUNT	4
#define CAMSS_RTCDM1_CORPUS_MAIN_SIZE		SZ_16K
#define CAMSS_RTCDM1_CORPUS_DMI_SIZE		0x3a00
#define CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID	GENMASK(1, 0)

struct camss_rtcdm1_corpus_blob {
	const void *data;
	size_t size;
};

struct camss_rtcdm1_corpus_input {
	struct camss_rtcdm1_corpus_blob main[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	struct camss_rtcdm1_corpus_blob payload[CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT];
	u32 dynamic[CAMSS_RTCDM1_CORPUS_DYNAMIC_VALUE_COUNT];
	u32 dynamic_valid;
};

struct camss_rtcdm1_corpus {
	void *main_cpu;
	dma_addr_t main_dma;
	void *dmi_cpu;
	dma_addr_t dmi_dma;
	u32 packet_dma[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	u16 packet_len[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	bool materialized;
};

struct camss_rtcdm1_corpus_payload_desc {
	u16 offset;
	u16 size;
};

struct camss_rtcdm1_corpus_dmi_ref {
	u16 field;
	u8 packet;
	u8 payload;
};

struct camss_rtcdm1_corpus_dynamic_patch {
	u16 field;
	u16 reg;
	u8 packet;
	u8 value;
};

static const u16 camss_rtcdm1_corpus_packet_used[CAMSS_RTCDM1_CORPUS_PACKET_COUNT] = {
	0x0e94,
	0x0e34,
	0x0904,
	0x04e8,
};

static const struct camss_rtcdm1_corpus_payload_desc
camss_rtcdm1_corpus_payloads[CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT] = {
	{ .offset = 0x0, .size = 0x200 }, /* 0 */
	{ .offset = 0x200, .size = 0x44 }, /* 1 */
	{ .offset = 0x280, .size = 0x300 }, /* 2 */
	{ .offset = 0x580, .size = 0x200 }, /* 3 */
	{ .offset = 0x780, .size = 0x400 }, /* 4 */
	{ .offset = 0xb80, .size = 0x50 }, /* 5 */
	{ .offset = 0xc00, .size = 0x374 }, /* 6 */
	{ .offset = 0xf80, .size = 0x374 }, /* 7 */
	{ .offset = 0x1300, .size = 0x374 }, /* 8 */
	{ .offset = 0x1680, .size = 0x180 }, /* 9 */
	{ .offset = 0x1800, .size = 0x374 }, /* 10 */
	{ .offset = 0x1b80, .size = 0x1000 }, /* 11 */
	{ .offset = 0x2b80, .size = 0x800 }, /* 12 */
	{ .offset = 0x3380, .size = 0x200 }, /* 13 */
	{ .offset = 0x3580, .size = 0x100 }, /* 14 */
	{ .offset = 0x3680, .size = 0x374 }, /* 15 */
};

static const struct camss_rtcdm1_corpus_dmi_ref
camss_rtcdm1_corpus_dmi_refs[CAMSS_RTCDM1_CORPUS_DMI_COUNT] = {
	{ .packet = 0, .payload = 0, .field = 0xe0 },
	{ .packet = 0, .payload = 6, .field = 0x150 },
	{ .packet = 0, .payload = 15, .field = 0x15c },
	{ .packet = 0, .payload = 8, .field = 0x168 },
	{ .packet = 0, .payload = 3, .field = 0x1dc },
	{ .packet = 0, .payload = 14, .field = 0x278 },
	{ .packet = 0, .payload = 1, .field = 0x2fc },
	{ .packet = 0, .payload = 1, .field = 0x308 },
	{ .packet = 0, .payload = 12, .field = 0x798 },
	{ .packet = 0, .payload = 4, .field = 0x7b8 },
	{ .packet = 0, .payload = 4, .field = 0x7c4 },
	{ .packet = 0, .payload = 4, .field = 0x7d0 },
	{ .packet = 0, .payload = 2, .field = 0xabc },
	{ .packet = 0, .payload = 2, .field = 0xac8 },
	{ .packet = 0, .payload = 9, .field = 0xad4 },
	{ .packet = 0, .payload = 9, .field = 0xae0 },
	{ .packet = 0, .payload = 11, .field = 0xd28 },
	{ .packet = 0, .payload = 5, .field = 0xd34 },
	{ .packet = 1, .payload = 0, .field = 0xe0 },
	{ .packet = 1, .payload = 10, .field = 0x13c },
	{ .packet = 1, .payload = 7, .field = 0x148 },
	{ .packet = 1, .payload = 8, .field = 0x154 },
	{ .packet = 1, .payload = 13, .field = 0x1c8 },
	{ .packet = 1, .payload = 14, .field = 0x264 },
	{ .packet = 1, .payload = 1, .field = 0x2d0 },
	{ .packet = 1, .payload = 1, .field = 0x2dc },
	{ .packet = 1, .payload = 12, .field = 0x76c },
	{ .packet = 1, .payload = 4, .field = 0x78c },
	{ .packet = 1, .payload = 4, .field = 0x798 },
	{ .packet = 1, .payload = 4, .field = 0x7a4 },
	{ .packet = 1, .payload = 2, .field = 0xa84 },
	{ .packet = 1, .payload = 2, .field = 0xa90 },
	{ .packet = 1, .payload = 9, .field = 0xa9c },
	{ .packet = 1, .payload = 9, .field = 0xaa8 },
	{ .packet = 2, .payload = 0, .field = 0xe0 },
	{ .packet = 2, .payload = 10, .field = 0x13c },
	{ .packet = 2, .payload = 7, .field = 0x148 },
	{ .packet = 2, .payload = 8, .field = 0x154 },
	{ .packet = 2, .payload = 13, .field = 0x1c8 },
	{ .packet = 2, .payload = 14, .field = 0x264 },
	{ .packet = 2, .payload = 12, .field = 0x6b8 },
	{ .packet = 2, .payload = 2, .field = 0x844 },
	{ .packet = 2, .payload = 2, .field = 0x850 },
	{ .packet = 2, .payload = 9, .field = 0x85c },
	{ .packet = 2, .payload = 9, .field = 0x868 },
	{ .packet = 3, .payload = 12, .field = 0x46c },
};

static const struct camss_rtcdm1_corpus_dynamic_patch
camss_rtcdm1_corpus_dynamic[CAMSS_RTCDM1_CORPUS_DYNAMIC_PATCH_COUNT] = {
	{ .packet = 0, .value = 0, .field = 0xe84, .reg = 0x8c },
	{ .packet = 1, .value = 1, .field = 0xe24, .reg = 0x8c },
	{ .packet = 2, .value = 1, .field = 0x8f4, .reg = 0x8c },
	{ .packet = 3, .value = 1, .field = 0x4d8, .reg = 0x8c },
};


static_assert(ARRAY_SIZE(camss_rtcdm1_corpus_packet_used) ==
	      CAMSS_RTCDM1_CORPUS_PACKET_COUNT);
static_assert(ARRAY_SIZE(camss_rtcdm1_corpus_payloads) ==
	      CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT);
static_assert(ARRAY_SIZE(camss_rtcdm1_corpus_dmi_refs) ==
	      CAMSS_RTCDM1_CORPUS_DMI_COUNT);
static_assert(ARRAY_SIZE(camss_rtcdm1_corpus_dynamic) ==
	      CAMSS_RTCDM1_CORPUS_DYNAMIC_PATCH_COUNT);

static int camss_rtcdm1_corpus_alloc(struct device *dev, size_t size,
				     void **cpu, dma_addr_t *dma)
{
	void *p;
	dma_addr_t d;

	p = dma_alloc_coherent(dev, size, &d, GFP_KERNEL);
	if (!p)
		return -ENOMEM;
	if ((u64)d + size - 1 > U32_MAX) {
		dma_free_coherent(dev, size, p, d);
		return -ERANGE;
	}

	memset(p, 0, size);
	*cpu = p;
	*dma = d;
	return 0;
}

static void camss_rtcdm1_corpus_release(struct camss *camss,
					struct camss_rtcdm1_corpus *corpus)
{
	if (!camss || !corpus)
		return;

	if (corpus->dmi_cpu) {
		memzero_explicit(corpus->dmi_cpu, CAMSS_RTCDM1_CORPUS_DMI_SIZE);
		dma_free_coherent(camss->dev, CAMSS_RTCDM1_CORPUS_DMI_SIZE,
				  corpus->dmi_cpu, corpus->dmi_dma);
	}
	if (corpus->main_cpu) {
		memzero_explicit(corpus->main_cpu, CAMSS_RTCDM1_CORPUS_MAIN_SIZE);
		dma_free_coherent(camss->dev, CAMSS_RTCDM1_CORPUS_MAIN_SIZE,
				  corpus->main_cpu, corpus->main_dma);
	}

	memset(corpus, 0, sizeof(*corpus));
}

static int camss_rtcdm1_corpus_validate_input(
	const struct camss_rtcdm1_corpus_input *input)
{
	unsigned int i;

	if (!input || input->dynamic_valid != CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID)
		return -EINVAL;

	for (i = 0; i < CAMSS_RTCDM1_CORPUS_PACKET_COUNT; i++)
		if (!input->main[i].data ||
		    input->main[i].size != camss_rtcdm1_corpus_packet_used[i])
			return -EINVAL;

	for (i = 0; i < CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT; i++)
		if (!input->payload[i].data ||
		    input->payload[i].size != camss_rtcdm1_corpus_payloads[i].size)
			return -EINVAL;

	/* Normalized templates must contain no captured Windows DMI address. */
	for (i = 0; i < CAMSS_RTCDM1_CORPUS_DMI_COUNT; i++) {
		const struct camss_rtcdm1_corpus_dmi_ref *ref =
			&camss_rtcdm1_corpus_dmi_refs[i];
		const u8 *main = input->main[ref->packet].data;

		if (ref->field + sizeof(u32) > input->main[ref->packet].size ||
		    get_unaligned_le32(main + ref->field))
			return -EINVAL;
	}

	/* Only start-dependent period_cfg values are caller inputs, never template data. */
	for (i = 0; i < CAMSS_RTCDM1_CORPUS_DYNAMIC_PATCH_COUNT; i++) {
		const struct camss_rtcdm1_corpus_dynamic_patch *patch =
			&camss_rtcdm1_corpus_dynamic[i];
		const u8 *main = input->main[patch->packet].data;

		if (patch->field + sizeof(u32) > input->main[patch->packet].size ||
		    get_unaligned_le32(main + patch->field))
			return -EINVAL;
	}

	return 0;
}

static int camss_rtcdm1_corpus_materialize(
	struct camss *camss, struct camss_rtcdm1_corpus *corpus,
	const struct camss_rtcdm1_corpus_input *input)
{
	u8 *main;
	u8 *dmi;
	unsigned int i;
	int ret;

	if (!camss || !camss->rtcdm1.present || !corpus)
		return -ENODEV;
	if (corpus->materialized || corpus->main_cpu || corpus->dmi_cpu)
		return -EBUSY;

	ret = camss_rtcdm1_corpus_validate_input(input);
	if (ret)
		return ret;

	ret = camss_rtcdm1_corpus_alloc(camss->dev,
					 CAMSS_RTCDM1_CORPUS_MAIN_SIZE,
					 &corpus->main_cpu, &corpus->main_dma);
	if (ret)
		return ret;
	ret = camss_rtcdm1_corpus_alloc(camss->dev,
					 CAMSS_RTCDM1_CORPUS_DMI_SIZE,
					 &corpus->dmi_cpu, &corpus->dmi_dma);
	if (ret)
		goto err_release;

	main = corpus->main_cpu;
	dmi = corpus->dmi_cpu;

	for (i = 0; i < CAMSS_RTCDM1_CORPUS_PACKET_COUNT; i++) {
		u32 slot = i * SZ_4K;
		u64 dma = (u64)corpus->main_dma + slot;

		memcpy(main + slot, input->main[i].data, input->main[i].size);
		corpus->packet_dma[i] = (u32)dma;
		corpus->packet_len[i] = camss_rtcdm1_corpus_packet_used[i];
	}

	for (i = 0; i < CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT; i++) {
		const struct camss_rtcdm1_corpus_payload_desc *desc =
			&camss_rtcdm1_corpus_payloads[i];

		memcpy(dmi + desc->offset, input->payload[i].data, desc->size);
	}

	for (i = 0; i < CAMSS_RTCDM1_CORPUS_DMI_COUNT; i++) {
		const struct camss_rtcdm1_corpus_dmi_ref *ref =
			&camss_rtcdm1_corpus_dmi_refs[i];
		const struct camss_rtcdm1_corpus_payload_desc *payload =
			&camss_rtcdm1_corpus_payloads[ref->payload];
		u8 *field = main + ref->packet * SZ_4K + ref->field;
		u64 dma = (u64)corpus->dmi_dma + payload->offset;

		put_unaligned_le32((u32)dma, field);
	}

	for (i = 0; i < CAMSS_RTCDM1_CORPUS_DYNAMIC_PATCH_COUNT; i++) {
		const struct camss_rtcdm1_corpus_dynamic_patch *patch =
			&camss_rtcdm1_corpus_dynamic[i];
		u8 *field = main + patch->packet * SZ_4K + patch->field;

		put_unaligned_le32(input->dynamic[patch->value], field);
	}

	corpus->materialized = true;
	return 0;

err_release:
	camss_rtcdm1_corpus_release(camss, corpus);
	return ret;
}

struct camss_rtcdm1_corpus_static_ops {
	int (*materialize)(struct camss *camss,
			   struct camss_rtcdm1_corpus *corpus,
			   const struct camss_rtcdm1_corpus_input *input);
	void (*release)(struct camss *camss, struct camss_rtcdm1_corpus *corpus);
};

/* Retention only: no probe, VFE, RT-CDM submit, or stream path references it. */
static const struct camss_rtcdm1_corpus_static_ops
camss_rtcdm1_corpus_recipe __used = {
	.materialize = camss_rtcdm1_corpus_materialize,
	.release = camss_rtcdm1_corpus_release,
};

/*
 * E003h front-start orchestration contract, retained and unreachable.
 *
 * This is deliberately a contract/validator rather than an execution path.
 * The exact same-machine Windows cross-order is now closed far enough to place
 * VFE1 BUS prepare between initial IFE packets 1 and 2, but Linux still has no
 * authorization to arm RT-CDM, submit FIFO0, start CSID1 IPP, enable VFE1 PIX,
 * start MIPI/CSIPHY, or transmit IMX681. The stage arrays below compose the
 * already-built private layers without calling any hardware-writing helper.
 */
#define CAMSS_X1E_FRONT_PREP_STAGE_COUNT	2
#define CAMSS_X1E_FRONT_START_STAGE_COUNT	10

/* Preparation is Linux-owned memory/state only; neither stage performs MMIO. */
enum camss_x1e_front_prepare_stage {
	CAMSS_X1E_FRONT_PREP_PIX_OWNERSHIP,
	CAMSS_X1E_FRONT_PREP_RTCDM_CORPUS,
};

/*
 * Hardware lifecycle markers. These identify where the retained 0011/0015/
 * 0017/0019 mechanics belong if a later runtime gate is authorized. They are
 * data only: this patch does not invoke those mechanics.
 */
enum camss_x1e_front_start_stage {
	CAMSS_X1E_FRONT_START_RTCDM_OPEN_INIT,
	CAMSS_X1E_FRONT_START_RTCDM_START,
	CAMSS_X1E_FRONT_START_IFE_RESOURCE_START,
	CAMSS_X1E_FRONT_START_IFE803_PACKET0,
	CAMSS_X1E_FRONT_START_IFE803_PACKET1,
	CAMSS_X1E_FRONT_START_VFE1_BUS_PREPARE,
	CAMSS_X1E_FRONT_START_IFE803_PACKET2,
	CAMSS_X1E_FRONT_START_IFE803_PACKET3,
	CAMSS_X1E_FRONT_START_CSID1_IPP_START,
	CAMSS_X1E_FRONT_START_ISP_START_DONE,
};

struct camss_x1e_front_start_contract {
	u8 csiphy_id;
	u8 csid_id;
	u8 vfe_id;
	u8 period_packet_map[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	u8 prepare_order[CAMSS_X1E_FRONT_PREP_STAGE_COUNT];
	u8 start_order[CAMSS_X1E_FRONT_START_STAGE_COUNT];
	bool hardware_execution_authorized;
	bool mipi_sensor_start_included;
};

static const struct camss_x1e_front_start_contract
camss_x1e_front_start_contract __used = {
	.csiphy_id = 2,
	.csid_id = 1,
	.vfe_id = 1,
	.period_packet_map = { 0, 1, 1, 1 },
	.prepare_order = {
		CAMSS_X1E_FRONT_PREP_PIX_OWNERSHIP,
		CAMSS_X1E_FRONT_PREP_RTCDM_CORPUS,
	},
	.start_order = {
		CAMSS_X1E_FRONT_START_RTCDM_OPEN_INIT,
		CAMSS_X1E_FRONT_START_RTCDM_START,
		CAMSS_X1E_FRONT_START_IFE_RESOURCE_START,
		CAMSS_X1E_FRONT_START_IFE803_PACKET0,
		CAMSS_X1E_FRONT_START_IFE803_PACKET1,
		CAMSS_X1E_FRONT_START_VFE1_BUS_PREPARE,
		CAMSS_X1E_FRONT_START_IFE803_PACKET2,
		CAMSS_X1E_FRONT_START_IFE803_PACKET3,
		CAMSS_X1E_FRONT_START_CSID1_IPP_START,
		CAMSS_X1E_FRONT_START_ISP_START_DONE,
	},
	.hardware_execution_authorized = false,
	.mipi_sensor_start_included = false,
};

static int camss_x1e_front_start_validate(struct camss *camss,
					  const struct camss_rtcdm1_corpus_input *input)
{
	struct v4l2_mbus_framefmt *fmt;
	struct csid_device *csid;
	struct vfe_device *vfe;

	if (!camss || !camss->res || camss->res->version != CAMSS_X1E80100)
		return -EINVAL;
	if (camss->res->csid_num <= 1 || camss->res->vfe_num <= 1)
		return -ENODEV;

	csid = &camss->csid[1];
	vfe = &camss->vfe[1];
	if (csid->id != 1 || vfe->id != 1 || vfe->res->is_lite)
		return -EINVAL;
	if (csid->phy.csiphy_id != 2 || csid->phy.phy_sel != CSID_PHY_SEL_CPHY ||
	    csid->phy.lane_cnt != 1 || !csid->phy.en_ipp)
		return -EINVAL;

	fmt = &csid->fmt[MSM_CSID_PAD_PIX];
	if (fmt->code != MEDIA_BUS_FMT_SRGGB10_1X10 ||
	    fmt->width != 3840 || fmt->height != 2640)
		return -EINVAL;

	/* 0021 keeps the two period values opaque and validates all corpus holes. */
	return camss_rtcdm1_corpus_validate_input(input);
}

struct camss_x1e_front_start_static_ops {
	int (*validate)(struct camss *camss,
			const struct camss_rtcdm1_corpus_input *input);
};

/* No probe, media, VFE, CSID, RT-CDM or sensor path references this table. */
static const struct camss_x1e_front_start_static_ops
camss_x1e_front_start_recipe __used = {
	.validate = camss_x1e_front_start_validate,
};

/*
 * Allocate a caller-sized coherent arena from the CAMSS DMA domain. The CAMSS
 * probe already installs a 32-bit coherent DMA mask. This helper independently
 * rejects any address that cannot be represented by RT-CDM's 32-bit BL base.
 * It does not populate the arena or submit it to hardware.
 */
int camss_rtcdm1_alloc_arena(struct camss *camss, size_t size)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;
	dma_addr_t dma;
	void *cpu;
	int ret = 0;

	if (!rt->present)
		return -ENODEV;
	if (!size || !IS_ALIGNED(size, sizeof(u32)) || size > U32_MAX)
		return -EINVAL;

	mutex_lock(&rt->lock);
	if (rt->arena_cpu) {
		ret = -EBUSY;
		goto out_unlock;
	}

	cpu = dma_alloc_coherent(camss->dev, size, &dma, GFP_KERNEL);
	if (!cpu) {
		ret = -ENOMEM;
		goto out_unlock;
	}

	if ((u64)dma > U32_MAX) {
		dma_free_coherent(camss->dev, size, cpu, dma);
		ret = -ERANGE;
		goto out_unlock;
	}

	memset(cpu, 0, size);
	rt->arena_cpu = cpu;
	rt->arena_dma = dma;
	rt->arena_size = size;

out_unlock:
	mutex_unlock(&rt->lock);
	return ret;
}

void camss_rtcdm1_free_arena(struct camss *camss)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;
	void *cpu;
	dma_addr_t dma;
	size_t size;

	if (!rt->present)
		return;

	mutex_lock(&rt->lock);
	cpu = rt->arena_cpu;
	dma = rt->arena_dma;
	size = rt->arena_size;
	rt->arena_cpu = NULL;
	rt->arena_dma = 0;
	rt->arena_size = 0;
	mutex_unlock(&rt->lock);

	if (!cpu)
		return;

	memzero_explicit(cpu, size);
	dma_free_coherent(camss->dev, size, cpu, dma);
}

void camss_rtcdm1_cleanup(struct camss *camss)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;

	if (!rt->present)
		return;

	/* No arm path exists in this layer; keep teardown fail-closed regardless. */
	if (READ_ONCE(rt->irq_armed)) {
		disable_irq(rt->irq);
		WRITE_ONCE(rt->irq_armed, false);
	}

	camss_rtcdm1_free_arena(camss);
}

/*
 * camss_rtcdm1_init - Resolve the optional Denali RT_CDM1 resource contract.
 *
 * Same-machine Windows proves RT_CDM1 at 0x0ac26000 with a dedicated IRQ.
 * This E003h layer maps the resource and registers a disabled IRQ handler.
 * It does not read/write RT-CDM registers, arm the IRQ, allocate command
 * memory, configure the engine, reset it, or expose a submission path.
 */
static int camss_rtcdm1_init(struct platform_device *pdev, struct camss *camss)
{
	struct resource *res;
	void __iomem *base;
	int irq;
	int ret;

	res = platform_get_resource_byname(pdev, IORESOURCE_MEM, "rt_cdm1");
	if (!res)
		return 0;

	if (camss->res->version != CAMSS_X1E80100)
		return dev_err_probe(camss->dev, -EINVAL,
				     "rt_cdm1 resource is X1E80100-only\n");

	if (res->start != CAMSS_X1E80100_RTCDM1_PHYS_BASE ||
	    resource_size(res) != CAMSS_X1E80100_RTCDM1_SIZE)
		return dev_err_probe(camss->dev, -EINVAL,
				     "unexpected rt_cdm1 resource %pr\n", res);

	irq = platform_get_irq_byname(pdev, "rt_cdm1");
	if (irq < 0)
		return dev_err_probe(camss->dev, irq,
				     "failed to resolve rt_cdm1 IRQ\n");

	base = devm_platform_ioremap_resource_byname(pdev, "rt_cdm1");
	if (IS_ERR(base))
		return dev_err_probe(camss->dev, PTR_ERR(base),
				     "failed to map rt_cdm1\n");

	camss->rtcdm1.base = base;
	camss->rtcdm1.irq = irq;
	init_completion(&camss->rtcdm1.completion);
	mutex_init(&camss->rtcdm1.lock);

	ret = devm_request_irq(camss->dev, irq, camss_rtcdm1_isr,
			       IRQF_TRIGGER_RISING | IRQF_NO_AUTOEN,
			       "camss-rt_cdm1", camss);
	if (ret)
		return dev_err_probe(camss->dev, ret,
				     "failed to request disabled rt_cdm1 IRQ\n");

	camss->rtcdm1.present = true;

	return 0;
}

/*
 * camss_probe - Probe CAMSS platform device
 * @pdev: Pointer to CAMSS platform device
 *
 * Return 0 on success or a negative error code on failure
 */
static int camss_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct camss *camss;
	int ret;

	camss = devm_kzalloc(dev, sizeof(*camss), GFP_KERNEL);
	if (!camss)
		return -ENOMEM;

	camss->res = of_device_get_match_data(dev);

	atomic_set(&camss->ref_count, 0);
	camss->dev = dev;
	platform_set_drvdata(pdev, camss);

	camss->csiphy = devm_kcalloc(dev, camss->res->csiphy_num,
				     sizeof(*camss->csiphy), GFP_KERNEL);
	if (!camss->csiphy)
		return -ENOMEM;

	camss->csid = devm_kcalloc(dev, camss->res->csid_num, sizeof(*camss->csid),
				   GFP_KERNEL);
	if (!camss->csid)
		return -ENOMEM;

	if (camss->res->version == CAMSS_8x16 ||
	    camss->res->version == CAMSS_8x39 ||
	    camss->res->version == CAMSS_8x53 ||
	    camss->res->version == CAMSS_8x96) {
		camss->ispif = devm_kcalloc(dev, 1, sizeof(*camss->ispif), GFP_KERNEL);
		if (!camss->ispif)
			return -ENOMEM;
	}

	camss->vfe = devm_kcalloc(dev, camss->res->vfe_num,
				  sizeof(*camss->vfe), GFP_KERNEL);
	if (!camss->vfe)
		return -ENOMEM;

	ret = camss_icc_get(camss);
	if (ret < 0)
		return ret;

	ret = camss_configure_pd(camss);
	if (ret < 0) {
		dev_err(dev, "Failed to configure power domains: %d\n", ret);
		return ret;
	}

	ret = camss_init_subdevices(camss);
	if (ret < 0)
		goto err_genpd_cleanup;

	ret = dma_set_mask_and_coherent(dev, 0xffffffff);
	if (ret)
		goto err_genpd_cleanup;

	ret = camss_rtcdm1_init(pdev, camss);
	if (ret)
		goto err_genpd_cleanup;

	camss->media_dev.dev = camss->dev;
	strscpy(camss->media_dev.model, "Qualcomm Camera Subsystem",
		sizeof(camss->media_dev.model));
	camss->media_dev.ops = &camss_media_ops;
	media_device_init(&camss->media_dev);

	camss->v4l2_dev.mdev = &camss->media_dev;
	ret = v4l2_device_register(camss->dev, &camss->v4l2_dev);
	if (ret < 0) {
		dev_err(dev, "Failed to register V4L2 device: %d\n", ret);
		goto err_media_device_cleanup;
	}

	v4l2_async_nf_init(&camss->notifier, &camss->v4l2_dev);

	pm_runtime_enable(dev);

	ret = camss_parse_ports(camss);
	if (ret < 0)
		goto err_v4l2_device_unregister;

	ret = camss_register_entities(camss);
	if (ret < 0)
		goto err_v4l2_device_unregister;

	ret = camss_link_entities(camss);
	if (ret < 0)
		goto err_register_subdevs;

	ret = media_device_register(&camss->media_dev);
	if (ret < 0) {
		dev_err(dev, "Failed to register media device: %d\n", ret);
		goto err_register_subdevs;
	}

	camss->notifier.ops = &camss_subdev_notifier_ops;
	ret = v4l2_async_nf_register(&camss->notifier);
	if (ret) {
		dev_err(dev,
			"Failed to register async subdev nodes: %d\n", ret);
		goto err_media_device_unregister;
	}

	return 0;

err_media_device_unregister:
	media_device_unregister(&camss->media_dev);
err_register_subdevs:
	camss_unregister_entities(camss);
err_v4l2_device_unregister:
	v4l2_device_unregister(&camss->v4l2_dev);
	v4l2_async_nf_cleanup(&camss->notifier);
	pm_runtime_disable(dev);
err_media_device_cleanup:
	media_device_cleanup(&camss->media_dev);
err_genpd_cleanup:
	camss_genpd_cleanup(camss);

	return ret;
}

void camss_delete(struct camss *camss)
{
	camss_rtcdm1_cleanup(camss);
	v4l2_device_unregister(&camss->v4l2_dev);
	media_device_unregister(&camss->media_dev);
	media_device_cleanup(&camss->media_dev);

	pm_runtime_disable(camss->dev);
}

/*
 * camss_remove - Remove CAMSS platform device
 * @pdev: Pointer to CAMSS platform device
 *
 * Always returns 0.
 */
static void camss_remove(struct platform_device *pdev)
{
	struct camss *camss = platform_get_drvdata(pdev);

	v4l2_async_nf_unregister(&camss->notifier);
	v4l2_async_nf_cleanup(&camss->notifier);
	camss_unregister_entities(camss);

	if (atomic_read(&camss->ref_count) == 0)
		camss_delete(camss);

	camss_genpd_cleanup(camss);
}

static const struct camss_resources msm8916_resources = {
	.version = CAMSS_8x16,
	.csiphy_res = csiphy_res_8x16,
	.csid_res = csid_res_8x16,
	.ispif_res = &ispif_res_8x16,
	.vfe_res = vfe_res_8x16,
	.csiphy_num = ARRAY_SIZE(csiphy_res_8x16),
	.csid_num = ARRAY_SIZE(csid_res_8x16),
	.vfe_num = ARRAY_SIZE(vfe_res_8x16),
};

static const struct camss_resources msm8939_resources = {
	.version = CAMSS_8x39,
	.csiphy_res = csiphy_res_8x39,
	.csid_res = csid_res_8x39,
	.ispif_res = &ispif_res_8x39,
	.vfe_res = vfe_res_8x39,
	.csiphy_num = ARRAY_SIZE(csiphy_res_8x39),
	.csid_num = ARRAY_SIZE(csid_res_8x39),
	.vfe_num = ARRAY_SIZE(vfe_res_8x39),
};

static const struct camss_resources msm8953_resources = {
	.version = CAMSS_8x53,
	.icc_res = icc_res_8x53,
	.icc_path_num = ARRAY_SIZE(icc_res_8x53),
	.csiphy_res = csiphy_res_8x96,
	.csid_res = csid_res_8x53,
	.ispif_res = &ispif_res_8x53,
	.vfe_res = vfe_res_8x53,
	.csiphy_num = ARRAY_SIZE(csiphy_res_8x96),
	.csid_num = ARRAY_SIZE(csid_res_8x53),
	.vfe_num = ARRAY_SIZE(vfe_res_8x53),
};

static const struct camss_resources msm8996_resources = {
	.version = CAMSS_8x96,
	.csiphy_res = csiphy_res_8x96,
	.csid_res = csid_res_8x96,
	.ispif_res = &ispif_res_8x96,
	.vfe_res = vfe_res_8x96,
	.csiphy_num = ARRAY_SIZE(csiphy_res_8x96),
	.csid_num = ARRAY_SIZE(csid_res_8x96),
	.vfe_num = ARRAY_SIZE(vfe_res_8x96),
};

static const struct camss_resources qcm2290_resources = {
	.version = CAMSS_2290,
	.csiphy_res = csiphy_res_2290,
	.csid_res = csid_res_2290,
	.vfe_res = vfe_res_2290,
	.icc_res = icc_res_2290,
	.icc_path_num = ARRAY_SIZE(icc_res_2290),
	.csiphy_num = ARRAY_SIZE(csiphy_res_2290),
	.csid_num = ARRAY_SIZE(csid_res_2290),
	.vfe_num = ARRAY_SIZE(vfe_res_2290),
};

static const struct camss_resources qcs8300_resources = {
	.version = CAMSS_8300,
	.pd_name = "top",
	.csiphy_res = csiphy_res_8300,
	.csid_res = csid_res_8775p,
	.csid_wrapper_res = &csid_wrapper_res_sm8550,
	.vfe_res = vfe_res_8775p,
	.icc_res = icc_res_qcs8300,
	.csiphy_num = ARRAY_SIZE(csiphy_res_8300),
	.csid_num = ARRAY_SIZE(csid_res_8775p),
	.vfe_num = ARRAY_SIZE(vfe_res_8775p),
	.icc_path_num = ARRAY_SIZE(icc_res_qcs8300),
};

static const struct camss_resources sa8775p_resources = {
	.version = CAMSS_8775P,
	.pd_name = "top",
	.csiphy_res = csiphy_res_8775p,
	.csid_res = csid_res_8775p,
	.csid_wrapper_res = &csid_wrapper_res_sm8550,
	.vfe_res = vfe_res_8775p,
	.icc_res = icc_res_sa8775p,
	.csiphy_num = ARRAY_SIZE(csiphy_res_8775p),
	.csid_num = ARRAY_SIZE(csid_res_8775p),
	.vfe_num = ARRAY_SIZE(vfe_res_8775p),
	.icc_path_num = ARRAY_SIZE(icc_res_sa8775p),
};

static const struct camss_resources sdm660_resources = {
	.version = CAMSS_660,
	.csiphy_res = csiphy_res_660,
	.csid_res = csid_res_660,
	.ispif_res = &ispif_res_660,
	.vfe_res = vfe_res_660,
	.csiphy_num = ARRAY_SIZE(csiphy_res_660),
	.csid_num = ARRAY_SIZE(csid_res_660),
	.vfe_num = ARRAY_SIZE(vfe_res_660),
};

static const struct camss_resources sdm670_resources = {
	.version = CAMSS_845,
	.csiphy_res = csiphy_res_670,
	.csid_res = csid_res_670,
	.vfe_res = vfe_res_670,
	.csiphy_num = ARRAY_SIZE(csiphy_res_670),
	.csid_num = ARRAY_SIZE(csid_res_670),
	.vfe_num = ARRAY_SIZE(vfe_res_670),
};

static const struct camss_resources sdm845_resources = {
	.version = CAMSS_845,
	.pd_name = "top",
	.csiphy_res = csiphy_res_845,
	.csid_res = csid_res_845,
	.vfe_res = vfe_res_845,
	.csiphy_num = ARRAY_SIZE(csiphy_res_845),
	.csid_num = ARRAY_SIZE(csid_res_845),
	.vfe_num = ARRAY_SIZE(vfe_res_845),
};

static const struct camss_resources sm6150_resources = {
	.version = CAMSS_6150,
	.pd_name = "top",
	.csiphy_res = csiphy_res_sm6150,
	.csid_res = csid_res_sm6150,
	.vfe_res = vfe_res_sm6150,
	.icc_res = icc_res_sm6150,
	.icc_path_num = ARRAY_SIZE(icc_res_sm6150),
	.csiphy_num = ARRAY_SIZE(csiphy_res_sm6150),
	.csid_num = ARRAY_SIZE(csid_res_sm6150),
	.vfe_num = ARRAY_SIZE(vfe_res_sm6150),
};

static const struct camss_resources sm8250_resources = {
	.version = CAMSS_8250,
	.pd_name = "top",
	.csiphy_res = csiphy_res_8250,
	.csid_res = csid_res_8250,
	.vfe_res = vfe_res_8250,
	.icc_res = icc_res_sm8250,
	.icc_path_num = ARRAY_SIZE(icc_res_sm8250),
	.csiphy_num = ARRAY_SIZE(csiphy_res_8250),
	.csid_num = ARRAY_SIZE(csid_res_8250),
	.vfe_num = ARRAY_SIZE(vfe_res_8250),
};

static const struct camss_resources sc8280xp_resources = {
	.version = CAMSS_8280XP,
	.pd_name = "top",
	.csiphy_res = csiphy_res_sc8280xp,
	.csid_res = csid_res_sc8280xp,
	.ispif_res = NULL,
	.vfe_res = vfe_res_sc8280xp,
	.icc_res = icc_res_sc8280xp,
	.icc_path_num = ARRAY_SIZE(icc_res_sc8280xp),
	.csiphy_num = ARRAY_SIZE(csiphy_res_sc8280xp),
	.csid_num = ARRAY_SIZE(csid_res_sc8280xp),
	.vfe_num = ARRAY_SIZE(vfe_res_sc8280xp),
};

static const struct camss_resources sc7280_resources = {
	.version = CAMSS_7280,
	.pd_name = "top",
	.csiphy_res = csiphy_res_7280,
	.csid_res = csid_res_7280,
	.vfe_res = vfe_res_7280,
	.icc_res = icc_res_sc7280,
	.icc_path_num = ARRAY_SIZE(icc_res_sc7280),
	.csiphy_num = ARRAY_SIZE(csiphy_res_7280),
	.csid_num = ARRAY_SIZE(csid_res_7280),
	.vfe_num = ARRAY_SIZE(vfe_res_7280),
};

static const struct camss_resources sm8550_resources = {
	.version = CAMSS_8550,
	.pd_name = "top",
	.csiphy_res = csiphy_res_8550,
	.csid_res = csid_res_8550,
	.vfe_res = vfe_res_8550,
	.csid_wrapper_res = &csid_wrapper_res_sm8550,
	.icc_res = icc_res_sm8550,
	.icc_path_num = ARRAY_SIZE(icc_res_sm8550),
	.csiphy_num = ARRAY_SIZE(csiphy_res_8550),
	.csid_num = ARRAY_SIZE(csid_res_8550),
	.vfe_num = ARRAY_SIZE(vfe_res_8550),
};

static const struct camss_resources sm8650_resources = {
	.version = CAMSS_8650,
	.pd_name = "top",
	.csiphy_res = csiphy_res_sm8650,
	.csid_res = csid_res_sm8650,
	.csid_wrapper_res = &csid_wrapper_res_sm8550,
	.vfe_res = vfe_res_sm8650,
	.icc_res = icc_res_sm8650,
	.icc_path_num = ARRAY_SIZE(icc_res_sm8650),
	.csiphy_num = ARRAY_SIZE(csiphy_res_sm8650),
	.csid_num = ARRAY_SIZE(csid_res_sm8650),
	.vfe_num = ARRAY_SIZE(vfe_res_sm8650),
};

static const struct camss_resources x1e80100_resources = {
	.version = CAMSS_X1E80100,
	.pd_name = "top",
	.csiphy_res = csiphy_res_x1e80100,
	.csid_res = csid_res_x1e80100,
	.vfe_res = vfe_res_x1e80100,
	.csid_wrapper_res = &csid_wrapper_res_x1e80100,
	.icc_res = icc_res_x1e80100,
	.icc_path_num = ARRAY_SIZE(icc_res_x1e80100),
	.csiphy_num = ARRAY_SIZE(csiphy_res_x1e80100),
	.csid_num = ARRAY_SIZE(csid_res_x1e80100),
	.vfe_num = ARRAY_SIZE(vfe_res_x1e80100),
};

static const struct of_device_id camss_dt_match[] = {
	{ .compatible = "qcom,msm8916-camss", .data = &msm8916_resources },
	{ .compatible = "qcom,msm8939-camss", .data = &msm8939_resources },
	{ .compatible = "qcom,msm8953-camss", .data = &msm8953_resources },
	{ .compatible = "qcom,msm8996-camss", .data = &msm8996_resources },
	{ .compatible = "qcom,qcm2290-camss", .data = &qcm2290_resources },
	{ .compatible = "qcom,qcs8300-camss", .data = &qcs8300_resources },
	{ .compatible = "qcom,sa8775p-camss", .data = &sa8775p_resources },
	{ .compatible = "qcom,sc7280-camss", .data = &sc7280_resources },
	{ .compatible = "qcom,sc8280xp-camss", .data = &sc8280xp_resources },
	{ .compatible = "qcom,sdm660-camss", .data = &sdm660_resources },
	{ .compatible = "qcom,sdm670-camss", .data = &sdm670_resources },
	{ .compatible = "qcom,sdm845-camss", .data = &sdm845_resources },
	{ .compatible = "qcom,sm6150-camss", .data = &sm6150_resources },
	{ .compatible = "qcom,sm8250-camss", .data = &sm8250_resources },
	{ .compatible = "qcom,sm8550-camss", .data = &sm8550_resources },
	{ .compatible = "qcom,sm8650-camss", .data = &sm8650_resources },
	{ .compatible = "qcom,x1e80100-camss", .data = &x1e80100_resources },
	{ }
};

MODULE_DEVICE_TABLE(of, camss_dt_match);

static int __maybe_unused camss_runtime_suspend(struct device *dev)
{
	struct camss *camss = dev_get_drvdata(dev);
	int i;
	int ret;

	for (i = 0; i < camss->res->icc_path_num; i++) {
		ret = icc_set_bw(camss->icc_path[i], 0, 0);
		if (ret)
			return ret;
	}

	return 0;
}

static int __maybe_unused camss_runtime_resume(struct device *dev)
{
	struct camss *camss = dev_get_drvdata(dev);
	const struct resources_icc *icc_res = camss->res->icc_res;
	int i;
	int ret;

	for (i = 0; i < camss->res->icc_path_num; i++) {
		ret = icc_set_bw(camss->icc_path[i],
				 icc_res[i].icc_bw_tbl.avg,
				 icc_res[i].icc_bw_tbl.peak);
		if (ret)
			return ret;
	}

	return 0;
}

static const struct dev_pm_ops camss_pm_ops = {
	SET_SYSTEM_SLEEP_PM_OPS(pm_runtime_force_suspend,
				pm_runtime_force_resume)
	SET_RUNTIME_PM_OPS(camss_runtime_suspend, camss_runtime_resume, NULL)
};

static struct platform_driver qcom_camss_driver = {
	.probe = camss_probe,
	.remove = camss_remove,
	.driver = {
		.name = "qcom-camss",
		.of_match_table = camss_dt_match,
		.pm = &camss_pm_ops,
	},
};

module_platform_driver(qcom_camss_driver);

MODULE_DESCRIPTION("Qualcomm Camera Subsystem driver");
MODULE_AUTHOR("Todor Tomov <todor.tomov@linaro.org>");
MODULE_LICENSE("GPL v2");
