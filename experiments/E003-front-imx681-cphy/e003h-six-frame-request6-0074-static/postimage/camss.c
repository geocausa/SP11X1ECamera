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
#include <linux/dma-mapping.h>
#include <linux/firmware.h>
#include <linux/interconnect.h>
#include <linux/interrupt.h>
#include <linux/ioport.h>
#include <linux/jiffies.h>
#include <linux/ktime.h>
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
#include <media/videobuf2-dma-sg.h>

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

/* Disposable E003h PIX trigger. False by default and read-only after load. */
static bool camss_x1e_pix_runtime_arm;
module_param_named(e003h_pix_runtime_arm, camss_x1e_pix_runtime_arm, bool, 0400);
MODULE_PARM_DESC(e003h_pix_runtime_arm,
		 "Arm the disposable SP11 E003h one-shot PIX sysfs trigger");

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
#define CAMSS_RTCDM_IRQ1_CLEAR          0x134
#define CAMSS_RTCDM_IRQ1_CLEAR_CMD      0x138
#define CAMSS_RTCDM_IRQ1_STATUS         0x144
#define CAMSS_RTCDM_IRQ2_CLEAR          0x234
#define CAMSS_RTCDM_IRQ2_CLEAR_CMD      0x238
#define CAMSS_RTCDM_IRQ2_STATUS         0x244
#define CAMSS_RTCDM_IRQ3_CLEAR          0x334
#define CAMSS_RTCDM_IRQ3_CLEAR_CMD      0x338
#define CAMSS_RTCDM_IRQ3_STATUS         0x344

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

enum camss_rtcdm_diag_stage {
	CAMSS_RTCDM_DIAG_IDLE,
	CAMSS_RTCDM_DIAG_PREFLIGHT,
	CAMSS_RTCDM_DIAG_RESET_COMMAND,
	CAMSS_RTCDM_DIAG_RESET_WAIT,
	CAMSS_RTCDM_DIAG_RESET_DONE,
	CAMSS_RTCDM_DIAG_CORE_CONFIGURED,
	CAMSS_RTCDM_DIAG_CORE_STARTING,
	CAMSS_RTCDM_DIAG_CORE_STARTED,
	CAMSS_RTCDM_DIAG_FIFO_WAIT,
	CAMSS_RTCDM_DIAG_FIFO_DONE,
	CAMSS_RTCDM_DIAG_STOPPED,
};

static const char *camss_rtcdm1_diag_stage_name(u32 stage)
{
	switch (stage) {
	case CAMSS_RTCDM_DIAG_PREFLIGHT:
		return "preflight";
	case CAMSS_RTCDM_DIAG_RESET_COMMAND:
		return "reset-command";
	case CAMSS_RTCDM_DIAG_RESET_WAIT:
		return "reset-wait";
	case CAMSS_RTCDM_DIAG_RESET_DONE:
		return "reset-done";
	case CAMSS_RTCDM_DIAG_CORE_CONFIGURED:
		return "core-configured";
	case CAMSS_RTCDM_DIAG_CORE_STARTING:
		return "core-starting";
	case CAMSS_RTCDM_DIAG_CORE_STARTED:
		return "core-started";
	case CAMSS_RTCDM_DIAG_FIFO_WAIT:
		return "fifo-wait";
	case CAMSS_RTCDM_DIAG_FIFO_DONE:
		return "fifo-done";
	case CAMSS_RTCDM_DIAG_STOPPED:
		return "stopped";
	default:
		return "idle";
	}
}

static void camss_rtcdm1_diag_set(struct camss *camss, u32 stage,
				  u32 required, int error)
{
	struct camss_rtcdm *rt = &camss->rtcdm1;
	u32 seq;

	WRITE_ONCE(rt->diag_stage, stage);
	WRITE_ONCE(rt->diag_required_irq, required);
	WRITE_ONCE(rt->diag_last_error, error);
	if (error && rt->base) {
		WRITE_ONCE(rt->diag_mmio_context,
			   readl_relaxed(rt->base + CAMSS_RTCDM_IRQ_CONTEXT_STATUS));
		WRITE_ONCE(rt->diag_mmio_status,
			   readl_relaxed(rt->base + CAMSS_RTCDM_IRQ0_STATUS));
		WRITE_ONCE(rt->diag_mmio_user_data,
			   readl_relaxed(rt->base + CAMSS_RTCDM_USR_DATA));
	}

	seq = READ_ONCE(rt->diag_transition_seq) + 1;
	/* Pairs with e003h_pix_rtcdm_diag_show() acquire load. */
	smp_store_release(&rt->diag_transition_seq, seq);
	sysfs_notify(&camss->dev->kobj, NULL, "e003h_pix_rtcdm_diag");

	if (!error)
		return;
	dev_err(camss->dev,
		"E003h RT-CDM1 stage=%s error=%d fifo_seq=%u base=%#x len=%#x required=%#x raw_context=%#x raw_status=%#x raw_userdata=%#x last_context=%#x last_status=%#x last_userdata=%#x\n",
		camss_rtcdm1_diag_stage_name(stage), error,
		READ_ONCE(rt->diag_fifo_seq), READ_ONCE(rt->diag_base),
		READ_ONCE(rt->diag_len_low20), required,
		READ_ONCE(rt->diag_mmio_context), READ_ONCE(rt->diag_mmio_status),
		READ_ONCE(rt->diag_mmio_user_data), READ_ONCE(rt->last_irq_context),
		READ_ONCE(rt->last_irq_status), READ_ONCE(rt->last_user_data));
}

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
	u32 clear0, clear1, clear2, clear3;
	u32 status0, status1, status2, status3;
	u32 user_data;

	if (irq != rt->irq || !READ_ONCE(rt->irq_armed))
		return IRQ_NONE;

	/*
	 * Exact same-machine Windows handler RVA 0x29120 reads and masks all
	 * four FIFO status banks. Its clear/callback block is gated by masked
	 * FIFO0 status, not IRQ_CONTEXT_STATUS.
	 */
	status0 = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ0_STATUS);
	status1 = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ1_STATUS);
	status2 = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ2_STATUS);
	status3 = readl_relaxed(rt->base + CAMSS_RTCDM_IRQ3_STATUS);
	clear0 = status0 & CAMSS_RTCDM_IRQ_KNOWN;
	clear1 = status1 & CAMSS_RTCDM_IRQ_KNOWN;
	clear2 = status2 & CAMSS_RTCDM_IRQ_KNOWN;
	clear3 = status3 & CAMSS_RTCDM_IRQ_KNOWN;
	if (!clear0)
		return IRQ_NONE;

	user_data = readl_relaxed(rt->base + CAMSS_RTCDM_USR_DATA);
	writel_relaxed(clear0, rt->base + CAMSS_RTCDM_IRQ0_CLEAR);
	writel_relaxed(clear1, rt->base + CAMSS_RTCDM_IRQ1_CLEAR);
	writel_relaxed(clear2, rt->base + CAMSS_RTCDM_IRQ2_CLEAR);
	writel_relaxed(clear3, rt->base + CAMSS_RTCDM_IRQ3_CLEAR);
	writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ0_CLEAR_CMD);
	writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ1_CLEAR_CMD);
	writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ2_CLEAR_CMD);
	writel_relaxed(1, rt->base + CAMSS_RTCDM_IRQ3_CLEAR_CMD);

	WRITE_ONCE(rt->last_irq_context, 0);
	WRITE_ONCE(rt->last_irq_status, status0);
	WRITE_ONCE(rt->last_irq_status1, status1);
	WRITE_ONCE(rt->last_irq_status2, status2);
	WRITE_ONCE(rt->last_irq_status3, status3);
	WRITE_ONCE(rt->last_user_data, user_data);

	if ((status0 & ~CAMSS_RTCDM_IRQ_KNOWN) ||
	    (status0 & CAMSS_RTCDM_IRQ_ERRORS)) {
		WRITE_ONCE(rt->faulted, true);
		disable_irq_nosync(rt->irq);
		WRITE_ONCE(rt->irq_armed, false);
	}

	/* Windows completion callback is driven by the masked FIFO0 status. */
	if (clear0 & (CAMSS_RTCDM_IRQ_RESET_DONE | CAMSS_RTCDM_IRQ_BL_DONE))
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

	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_PREFLIGHT, 0, 0);
	hw_version = readl_relaxed(rt->base + CAMSS_RTCDM_HW_VERSION);
	fe_cfg = readl_relaxed(rt->base + CAMSS_RTCDM_FE_CFG);
	fifo0_cfg = readl_relaxed(rt->base + CAMSS_RTCDM_FIFO0_CFG);

	if (hw_version != CAMSS_RTCDM_WINDOWS_HW_VERSION ||
	    fe_cfg != CAMSS_RTCDM_WINDOWS_FE_CFG ||
	    fifo0_cfg != CAMSS_RTCDM_WINDOWS_FIFO0_CFG) {
		dev_err(camss->dev,
			"E003h RT-CDM1 preflight mismatch hw=%#x fe=%#x fifo0=%#x\n",
			hw_version, fe_cfg, fifo0_cfg);
		camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_PREFLIGHT, 0,
				      -ENODEV);
		return -ENODEV;
	}

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
	WRITE_ONCE(rt->last_irq_status1, 0);
	WRITE_ONCE(rt->last_irq_status2, 0);
	WRITE_ONCE(rt->last_irq_status3, 0);
	WRITE_ONCE(rt->last_user_data, 0);
	WRITE_ONCE(rt->diag_fifo_seq, 0);
	WRITE_ONCE(rt->diag_base, 0);
	WRITE_ONCE(rt->diag_len_low20, 0);
	WRITE_ONCE(rt->diag_mmio_context, 0);
	WRITE_ONCE(rt->diag_mmio_status, 0);
	WRITE_ONCE(rt->diag_mmio_user_data, 0);

	/* Linux interrupt-controller mechanics; no RT-CDM register is changed. */
	WRITE_ONCE(rt->irq_armed, true);
	enable_irq(rt->irq);

	/* Exact same-machine Windows open/init MMIO order. */
	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_RESET_COMMAND, 0, 0);
	writel_relaxed(CAMSS_RTCDM_WINDOWS_RESET_MASK,
		       rt->base + CAMSS_RTCDM_IRQ0_MASK);
	writel_relaxed(CAMSS_RTCDM_WINDOWS_RESET_CMD,
		       rt->base + CAMSS_RTCDM_RST_CMD);

	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_RESET_WAIT,
			      CAMSS_RTCDM_IRQ_RESET_DONE, 0);
	ret = camss_rtcdm1_windows_wait(rt, CAMSS_RTCDM_IRQ_RESET_DONE);
	if (ret) {
		camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_RESET_WAIT,
				      CAMSS_RTCDM_IRQ_RESET_DONE, ret);
		disable_irq(rt->irq);
		WRITE_ONCE(rt->irq_armed, false);
		goto out_unlock;
	}

	/* qccamisp8380.sys executes DMB SY immediately before CORE_CFG. */
	dmb(sy);
	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_RESET_DONE,
			      CAMSS_RTCDM_IRQ_RESET_DONE, 0);
	writel_relaxed(CAMSS_RTCDM_WINDOWS_CORE_CFG,
		       rt->base + CAMSS_RTCDM_CORE_CFG);
	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_CORE_CONFIGURED, 0, 0);

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
		camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_CORE_STARTED, 0, ret);
		goto out_unlock;
	}

	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_CORE_STARTING, 0, 0);
	writel_relaxed(CAMSS_RTCDM_WINDOWS_IRQ0_MASK,
		       rt->base + CAMSS_RTCDM_IRQ0_MASK);
	dmb(sy);
	writel_relaxed(CAMSS_RTCDM_WINDOWS_CORE_EN,
		       rt->base + CAMSS_RTCDM_CORE_EN);
	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_CORE_STARTED, 0, 0);

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
	WRITE_ONCE(rt->last_irq_status1, 0);
	WRITE_ONCE(rt->last_irq_status2, 0);
	WRITE_ONCE(rt->last_irq_status3, 0);
	WRITE_ONCE(rt->last_user_data, 0);
	WRITE_ONCE(rt->diag_fifo_seq, READ_ONCE(rt->diag_fifo_seq) + 1);
	WRITE_ONCE(rt->diag_base, base);
	WRITE_ONCE(rt->diag_len_low20, len_low20);
	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_FIFO_WAIT,
			      CAMSS_RTCDM_IRQ_BL_DONE, 0);

	/* Exact Windows dynamic FIFO0 commit: BASE -> encoded LEN -> STORE. */
	writel_relaxed(base, rt->base + CAMSS_RTCDM_FIFO0_BASE);
	writel_relaxed(encoded_len, rt->base + CAMSS_RTCDM_FIFO0_LEN);
	writel_relaxed(1, rt->base + CAMSS_RTCDM_FIFO0_STORE);

	ret = camss_rtcdm1_windows_wait(rt, CAMSS_RTCDM_IRQ_BL_DONE);
	if (ret)
		camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_FIFO_WAIT,
				      CAMSS_RTCDM_IRQ_BL_DONE, ret);
	else
		camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_FIFO_DONE,
				      CAMSS_RTCDM_IRQ_BL_DONE, 0);

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
	camss_rtcdm1_diag_set(camss, CAMSS_RTCDM_DIAG_STOPPED, 0, 0);
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
	    fmt->width != 3840 || fmt->height != 2160)
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
 * E003h post-ISP_START_DONE ownership/scheduling contract, retained and
 * unreachable. This object is intentionally data-only: no helper or ops table
 * can execute it.
 *
 * Exact same-machine Windows disassembly proves the IFE Epoch0 path runs before
 * completion dispatch. Epoch0 first invokes the BUS resource-update wrapper,
 * then invokes RT-CDM operation 2 to consume/program an already queued BL batch.
 * Two live sessions independently show one complete nine-client address bundle
 * before ISP_START_DONE, a second complete bundle after START_DONE but before
 * the first completion cycle, and a refill bundle after that cycle retires.
 *
 * The observed VIDEO/AEC-BHIST/Tintless/AWB/RS interrupt order is not encoded as
 * a dependency: the exact Windows completion helper owns an independent FIFO per
 * group. The later steady-state CDM oracle supersedes the earlier "no post-start
 * rewrite" interpretation for the six register identities below: Windows does
 * carry them in queued per-frame RT-CDM command lists. This still does not
 * authorize a separate direct-MMIO/polling rewrite path in Linux.
 */
#define CAMSS_X1E_FRONT_POST_START_STAGE_COUNT	4
#define CAMSS_X1E_FRONT_POST_START_BUNDLE_CLIENTS	9
#define CAMSS_X1E_FRONT_POST_START_COMPLETION_GROUPS	5
#define CAMSS_X1E_FRONT_POST_START_INITIAL_PRIME_BUNDLES	2
#define CAMSS_X1E_FRONT_POST_START_CDM_PROGRAMMED_REGS	6
#define CAMSS_X1E_FRONT_POST_START_LIVE_MUTABLE_REGS	4

enum camss_x1e_front_post_start_stage {
	CAMSS_X1E_FRONT_POST_START_EPOCH0,
	CAMSS_X1E_FRONT_POST_START_VFE1_BUS_UPDATE,
	CAMSS_X1E_FRONT_POST_START_RTCDM_BATCH_CONSUME,
	CAMSS_X1E_FRONT_POST_START_COMPLETION_RETIRE,
};

struct camss_x1e_front_post_start_contract {
	u8 stage_order[CAMSS_X1E_FRONT_POST_START_STAGE_COUNT];
	u8 address_bundle_clients;
	u8 observed_initial_prime_bundles;
	u8 completion_group_count;
	u16 cdm_programmed_regs[CAMSS_X1E_FRONT_POST_START_CDM_PROGRAMMED_REGS];
	u16 hardware_live_mutable_regs[CAMSS_X1E_FRONT_POST_START_LIVE_MUTABLE_REGS];
	bool second_bundle_before_first_completion;
	bool refill_after_first_completion_cycle;
	bool completion_cross_group_order_required;
	bool slot_reuse_requires_all_groups;
	bool bus_iova_update_software_owned;
	bool rtcdm_batch_consume_software_owned;
	bool completion_retirement_software_owned;
	bool direct_mmio_rewrite_authorized;
	bool hardware_execution_authorized;
};

static const struct camss_x1e_front_post_start_contract
camss_x1e_front_post_start_contract __used = {
	.stage_order = {
		CAMSS_X1E_FRONT_POST_START_EPOCH0,
		CAMSS_X1E_FRONT_POST_START_VFE1_BUS_UPDATE,
		CAMSS_X1E_FRONT_POST_START_RTCDM_BATCH_CONSUME,
		CAMSS_X1E_FRONT_POST_START_COMPLETION_RETIRE,
	},
	.address_bundle_clients = CAMSS_X1E_FRONT_POST_START_BUNDLE_CLIENTS,
	.observed_initial_prime_bundles = CAMSS_X1E_FRONT_POST_START_INITIAL_PRIME_BUNDLES,
	.completion_group_count = CAMSS_X1E_FRONT_POST_START_COMPLETION_GROUPS,
	.cdm_programmed_regs = {
		0x008c, 0x3b70, 0x3d78, 0x3d7c, 0x3d80, 0x3d84,
	},
	.hardware_live_mutable_regs = {
		0x3d78, 0x3d7c, 0x3d80, 0x3d84,
	},
	.second_bundle_before_first_completion = true,
	.refill_after_first_completion_cycle = true,
	.completion_cross_group_order_required = false,
	.slot_reuse_requires_all_groups = true,
	.bus_iova_update_software_owned = true,
	.rtcdm_batch_consume_software_owned = true,
	.completion_retirement_software_owned = true,
	.direct_mmio_rewrite_authorized = false,
	.hardware_execution_authorized = false,
};

/*
 * E003h steady-state Epoch0 RT-CDM batch topology, retained and unreachable.
 *
 * A hash-pinned same-machine Windows selector-2 capture contains 175 steady
 * Epoch0 batches. Every batch has five BL records: CHANGE_BASE(VFE1), one main
 * IFE BL selected from the five shapes below, CHANGE_BASE(companion), one fixed
 * two-register BL and one fixed register + GEN_IRQ BL. The queue-record length
 * field is byte_count - 1. Captured Windows IOVAs are not represented here.
 *
 * Main BLs carry per-batch DMI address words and variant-specific per-frame
 * register values. Their payload bytes are not closed by this contract, so the
 * contract cannot materialize or submit a command list. GEN_IRQ userdata tracks
 * the observed batch tag, but no Linux tag-production rule is invented here.
 */
#define CAMSS_X1E_EPOCH0_CDM_STEADY_BL_COUNT	5
#define CAMSS_X1E_EPOCH0_CDM_VARIANT_COUNT	5
#define CAMSS_X1E_EPOCH0_CDM_STEADY_BATCHES	175

struct camss_x1e_epoch0_cdm_variant_contract {
	u16 main_bytes;
	u16 command_count;
	u16 register_write_count;
	u8 dmi_count;
	u8 dynamic_register_count;
	u8 observed_samples;
};

struct camss_x1e_epoch0_cdm_batch_contract {
	u16 bl_bytes[CAMSS_X1E_EPOCH0_CDM_STEADY_BL_COUNT];
	u32 vfe1_change_base;
	u32 companion_change_base;
	struct camss_x1e_epoch0_cdm_variant_contract
		variant[CAMSS_X1E_EPOCH0_CDM_VARIANT_COUNT];
	u16 observed_steady_batches;
	bool encoded_length_is_byte_count_minus_one;
	bool main_dmi_addresses_per_batch;
	bool main_register_values_per_frame;
	bool genirq_userdata_tracks_batch_tag;
	bool dmi_payload_bytes_closed;
	bool direct_mmio_rewrite_authorized;
	bool fifo0_submission_authorized;
};

static const struct camss_x1e_epoch0_cdm_batch_contract
camss_x1e_epoch0_cdm_batch_contract __used = {
	/* BL1 is the variant-sized main IFE list and is represented as zero here. */
	.bl_bytes = { 0x0004, 0x0000, 0x0004, 0x0010, 0x0014 },
	.vfe1_change_base = 0x0000f000,
	.companion_change_base = 0x00057000,
	.variant = {
		{ .main_bytes = 0x0958, .command_count = 56,
		  .register_write_count = 472, .dmi_count = 14,
		  .dynamic_register_count = 24, .observed_samples = 8 },
		{ .main_bytes = 0x0868, .command_count = 45,
		  .register_write_count = 436, .dmi_count = 12,
		  .dynamic_register_count = 20, .observed_samples = 42 },
		{ .main_bytes = 0x083c, .command_count = 43,
		  .register_write_count = 429, .dmi_count = 12,
		  .dynamic_register_count = 14, .observed_samples = 46 },
		{ .main_bytes = 0x06b8, .command_count = 35,
		  .register_write_count = 352, .dmi_count = 8,
		  .dynamic_register_count = 10, .observed_samples = 24 },
		{ .main_bytes = 0x05a4, .command_count = 22,
		  .register_write_count = 315, .dmi_count = 2,
		  .dynamic_register_count = 6, .observed_samples = 55 },
	},
	.observed_steady_batches = CAMSS_X1E_EPOCH0_CDM_STEADY_BATCHES,
	.encoded_length_is_byte_count_minus_one = true,
	.main_dmi_addresses_per_batch = true,
	.main_register_values_per_frame = true,
	.genirq_userdata_tracks_batch_tag = true,
	.dmi_payload_bytes_closed = false,
	.direct_mmio_rewrite_authorized = false,
	.fifo0_submission_authorized = false,
};

/*
 * E003h steady-state Epoch0 consumer/materializer, retained and unreachable.
 *
 * The registered Windows DeviceMFT proves the values below are upstream CamX
 * IQ-module outputs, not values invented by qccamisp KMD. Consequently this
 * helper accepts a caller-provided normalized main template plus module-level
 * register values/DMI payloads. It validates only the five exact 0024 shapes,
 * rewrites proven holes into Linux-owned DMA, and derives GEN_IRQ userdata from
 * request_id. No captured Windows main template, payload, IOVA or ring geometry
 * is embedded here, and nothing submits these BLs to RT-CDM.
 */
#define CAMSS_X1E_EPOCH0_CMD_SIZE		SZ_4K
#define CAMSS_X1E_EPOCH0_DMI_SIZE		0x3000
#define CAMSS_X1E_EPOCH0_BL0_OFFSET		0x000
#define CAMSS_X1E_EPOCH0_MAIN_OFFSET		0x040
#define CAMSS_X1E_EPOCH0_BL2_OFFSET		0xa00
#define CAMSS_X1E_EPOCH0_BL3_OFFSET		0xa40
#define CAMSS_X1E_EPOCH0_BL4_OFFSET		0xa80
#define CAMSS_X1E_EPOCH0_MODULE_REG_MAX	6
#define CAMSS_X1E_EPOCH0_MODULE_PAYLOAD_MAX	4

/* Standard CDM encodings/values reproduced by the 0024 companion-BL hashes. */
#define CAMSS_X1E_EPOCH0_BL0_CHANGE_BASE	0x0800f000
#define CAMSS_X1E_EPOCH0_BL2_CHANGE_BASE	0x08057000
#define CAMSS_X1E_EPOCH0_BL3_REG_CONT		0x03000002
#define CAMSS_X1E_EPOCH0_BL3_REG_OFFSET	0x0000035c
#define CAMSS_X1E_EPOCH0_BL3_VALUE0		0x0eff0000
#define CAMSS_X1E_EPOCH0_BL3_VALUE1		0x086f0000
#define CAMSS_X1E_EPOCH0_BL4_REG_RANDOM	0x04000001
#define CAMSS_X1E_EPOCH0_BL4_REG_OFFSET	0x00000018
#define CAMSS_X1E_EPOCH0_BL4_REG_VALUE		0x01f501f5
#define CAMSS_X1E_EPOCH0_BL4_GEN_IRQ		0x06000000

enum camss_x1e_epoch0_iq_module {
	CAMSS_X1E_IQ_DEMUX_BLS,
	CAMSS_X1E_IQ_PDPC,
	CAMSS_X1E_IQ_LSC,
	CAMSS_X1E_IQ_WB,
	CAMSS_X1E_IQ_GIC,
	CAMSS_X1E_IQ_BPC_ABF,
	CAMSS_X1E_IQ_GTM,
	CAMSS_X1E_IQ_GAMMA,
	CAMSS_X1E_IQ_DSX,
	CAMSS_X1E_IQ_NUM,
};

struct camss_x1e_epoch0_iq_module_input {
	u32 value[CAMSS_X1E_EPOCH0_MODULE_REG_MAX];
	u8 value_valid;
	struct camss_rtcdm1_corpus_blob payload[CAMSS_X1E_EPOCH0_MODULE_PAYLOAD_MAX];
	u8 payload_valid;
};

struct camss_x1e_epoch0_input {
	struct camss_rtcdm1_corpus_blob normalized_main;
	struct camss_x1e_epoch0_iq_module_input module[CAMSS_X1E_IQ_NUM];
	u64 request_id;
	u32 subrequest;
};

struct camss_x1e_epoch0_materialized {
	void *cmd_cpu;
	dma_addr_t cmd_dma;
	void *dmi_cpu;
	dma_addr_t dmi_dma;
	u32 bl_dma[CAMSS_X1E_EPOCH0_CDM_STEADY_BL_COUNT];
	u16 bl_len[CAMSS_X1E_EPOCH0_CDM_STEADY_BL_COUNT];
	bool materialized;
};

struct camss_x1e_epoch0_payload_desc {
	u16 offset;
	u16 size;
	u8 module;
	u8 payload;
};

struct camss_x1e_epoch0_reg_patch {
	u16 field;
	u16 reg;
	u8 module;
	u8 value;
};

struct camss_x1e_epoch0_dmi_patch {
	u16 field;
	u16 dmi_reg;
	u8 module;
	u8 payload;
	u8 selector;
};

struct camss_x1e_epoch0_variant_desc {
	u16 main_bytes;
	const struct camss_x1e_epoch0_reg_patch *reg;
	u8 reg_count;
	const struct camss_x1e_epoch0_dmi_patch *dmi;
	u8 dmi_count;
};

/* Linux-only compact DMI layout; deliberately unrelated to the Windows ring. */
static const struct camss_x1e_epoch0_payload_desc camss_x1e_epoch0_payloads[] = {
	{ .module = CAMSS_X1E_IQ_PDPC, .payload = 0, .offset = 0x0000, .size = 0x0200 },
	{ .module = CAMSS_X1E_IQ_LSC, .payload = 0, .offset = 0x0200, .size = 0x0374 },
	{ .module = CAMSS_X1E_IQ_LSC, .payload = 1, .offset = 0x0580, .size = 0x0374 },
	{ .module = CAMSS_X1E_IQ_LSC, .payload = 2, .offset = 0x0900, .size = 0x0374 },
	{ .module = CAMSS_X1E_IQ_GIC, .payload = 0, .offset = 0x0c80, .size = 0x0200 },
	{ .module = CAMSS_X1E_IQ_BPC_ABF, .payload = 0, .offset = 0x0e80, .size = 0x0100 },
	{ .module = CAMSS_X1E_IQ_GTM, .payload = 0, .offset = 0x0f80, .size = 0x0800 },
	{ .module = CAMSS_X1E_IQ_GAMMA, .payload = 0, .offset = 0x1780, .size = 0x0400 },
	{ .module = CAMSS_X1E_IQ_GAMMA, .payload = 1, .offset = 0x1b80, .size = 0x0400 },
	{ .module = CAMSS_X1E_IQ_GAMMA, .payload = 2, .offset = 0x1f80, .size = 0x0400 },
	{ .module = CAMSS_X1E_IQ_DSX, .payload = 0, .offset = 0x2380, .size = 0x0300 },
	{ .module = CAMSS_X1E_IQ_DSX, .payload = 1, .offset = 0x2680, .size = 0x0300 },
	{ .module = CAMSS_X1E_IQ_DSX, .payload = 2, .offset = 0x2980, .size = 0x0180 },
	{ .module = CAMSS_X1E_IQ_DSX, .payload = 3, .offset = 0x2b00, .size = 0x0180 },
};

static const struct camss_x1e_epoch0_reg_patch camss_x1e_epoch0_reg_v0[] = {
	{ .field = 0x48, .reg = 0x3b70, .module = CAMSS_X1E_IQ_DEMUX_BLS, .value = 0 },
	{ .field = 0x4c, .reg = 0x3b74, .module = CAMSS_X1E_IQ_DEMUX_BLS, .value = 1 },
	{ .field = 0x78, .reg = 0x3d58, .module = CAMSS_X1E_IQ_PDPC, .value = 0 },
	{ .field = 0x7c, .reg = 0x3d5c, .module = CAMSS_X1E_IQ_PDPC, .value = 1 },
	{ .field = 0xa4, .reg = 0x3d78, .module = CAMSS_X1E_IQ_PDPC, .value = 2 },
	{ .field = 0xa8, .reg = 0x3d7c, .module = CAMSS_X1E_IQ_PDPC, .value = 3 },
	{ .field = 0xac, .reg = 0x3d80, .module = CAMSS_X1E_IQ_PDPC, .value = 4 },
	{ .field = 0xb0, .reg = 0x3d84, .module = CAMSS_X1E_IQ_PDPC, .value = 5 },
	{ .field = 0xf0, .reg = 0x4358, .module = CAMSS_X1E_IQ_LSC, .value = 0 },
	{ .field = 0xf4, .reg = 0x435c, .module = CAMSS_X1E_IQ_LSC, .value = 1 },
	{ .field = 0x168, .reg = 0x456c, .module = CAMSS_X1E_IQ_WB, .value = 0 },
	{ .field = 0x16c, .reg = 0x4570, .module = CAMSS_X1E_IQ_WB, .value = 1 },
	{ .field = 0x1a8, .reg = 0x4758, .module = CAMSS_X1E_IQ_GIC, .value = 0 },
	{ .field = 0x1ac, .reg = 0x475c, .module = CAMSS_X1E_IQ_GIC, .value = 1 },
	{ .field = 0x254, .reg = 0x4958, .module = CAMSS_X1E_IQ_BPC_ABF, .value = 0 },
	{ .field = 0x258, .reg = 0x495c, .module = CAMSS_X1E_IQ_BPC_ABF, .value = 1 },
	{ .field = 0x2d4, .reg = 0x5a58, .module = CAMSS_X1E_IQ_GTM, .value = 0 },
	{ .field = 0x2d8, .reg = 0x5a5c, .module = CAMSS_X1E_IQ_GTM, .value = 1 },
	{ .field = 0x704, .reg = 0x5f58, .module = CAMSS_X1E_IQ_GAMMA, .value = 0 },
	{ .field = 0x708, .reg = 0x5f5c, .module = CAMSS_X1E_IQ_GAMMA, .value = 1 },
	{ .field = 0x73c, .reg = 0xa058, .module = CAMSS_X1E_IQ_DSX, .value = 0 },
	{ .field = 0x740, .reg = 0xa05c, .module = CAMSS_X1E_IQ_DSX, .value = 1 },
	{ .field = 0x83c, .reg = 0xa258, .module = CAMSS_X1E_IQ_DSX, .value = 2 },
	{ .field = 0x840, .reg = 0xa25c, .module = CAMSS_X1E_IQ_DSX, .value = 3 },
};

static const struct camss_x1e_epoch0_dmi_patch camss_x1e_epoch0_dmi_v0[] = {
	{ .field = 0xe0, .dmi_reg = 0x3d08, .module = CAMSS_X1E_IQ_PDPC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x13c, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x148, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 1, .selector = 2 },
	{ .field = 0x154, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 2, .selector = 3 },
	{ .field = 0x1c8, .dmi_reg = 0x4708, .module = CAMSS_X1E_IQ_GIC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x264, .dmi_reg = 0x4908, .module = CAMSS_X1E_IQ_BPC_ABF,
	  .payload = 0, .selector = 1 },
	{ .field = 0x6f4, .dmi_reg = 0x5a08, .module = CAMSS_X1E_IQ_GTM,
	  .payload = 0, .selector = 1 },
	{ .field = 0x714, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 0, .selector = 1 },
	{ .field = 0x720, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 1, .selector = 2 },
	{ .field = 0x72c, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 2, .selector = 3 },
	{ .field = 0x8b8, .dmi_reg = 0xa008, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 0, .selector = 1 },
	{ .field = 0x8c4, .dmi_reg = 0xa008, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 1, .selector = 2 },
	{ .field = 0x8d0, .dmi_reg = 0xa208, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 2, .selector = 1 },
	{ .field = 0x8dc, .dmi_reg = 0xa208, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 3, .selector = 2 },
};

static const struct camss_x1e_epoch0_reg_patch camss_x1e_epoch0_reg_v1[] = {
	{ .field = 0x48, .reg = 0x3b70, .module = CAMSS_X1E_IQ_DEMUX_BLS, .value = 0 },
	{ .field = 0x4c, .reg = 0x3b74, .module = CAMSS_X1E_IQ_DEMUX_BLS, .value = 1 },
	{ .field = 0x78, .reg = 0x3d58, .module = CAMSS_X1E_IQ_PDPC, .value = 0 },
	{ .field = 0x7c, .reg = 0x3d5c, .module = CAMSS_X1E_IQ_PDPC, .value = 1 },
	{ .field = 0xa4, .reg = 0x3d78, .module = CAMSS_X1E_IQ_PDPC, .value = 2 },
	{ .field = 0xa8, .reg = 0x3d7c, .module = CAMSS_X1E_IQ_PDPC, .value = 3 },
	{ .field = 0xac, .reg = 0x3d80, .module = CAMSS_X1E_IQ_PDPC, .value = 4 },
	{ .field = 0xb0, .reg = 0x3d84, .module = CAMSS_X1E_IQ_PDPC, .value = 5 },
	{ .field = 0xf0, .reg = 0x4358, .module = CAMSS_X1E_IQ_LSC, .value = 0 },
	{ .field = 0xf4, .reg = 0x435c, .module = CAMSS_X1E_IQ_LSC, .value = 1 },
	{ .field = 0x168, .reg = 0x456c, .module = CAMSS_X1E_IQ_WB, .value = 0 },
	{ .field = 0x16c, .reg = 0x4570, .module = CAMSS_X1E_IQ_WB, .value = 1 },
	{ .field = 0x1e4, .reg = 0x5a58, .module = CAMSS_X1E_IQ_GTM, .value = 0 },
	{ .field = 0x1e8, .reg = 0x5a5c, .module = CAMSS_X1E_IQ_GTM, .value = 1 },
	{ .field = 0x614, .reg = 0x5f58, .module = CAMSS_X1E_IQ_GAMMA, .value = 0 },
	{ .field = 0x618, .reg = 0x5f5c, .module = CAMSS_X1E_IQ_GAMMA, .value = 1 },
	{ .field = 0x64c, .reg = 0xa058, .module = CAMSS_X1E_IQ_DSX, .value = 0 },
	{ .field = 0x650, .reg = 0xa05c, .module = CAMSS_X1E_IQ_DSX, .value = 1 },
	{ .field = 0x74c, .reg = 0xa258, .module = CAMSS_X1E_IQ_DSX, .value = 2 },
	{ .field = 0x750, .reg = 0xa25c, .module = CAMSS_X1E_IQ_DSX, .value = 3 },
};

static const struct camss_x1e_epoch0_dmi_patch camss_x1e_epoch0_dmi_v1[] = {
	{ .field = 0xe0, .dmi_reg = 0x3d08, .module = CAMSS_X1E_IQ_PDPC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x13c, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x148, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 1, .selector = 2 },
	{ .field = 0x154, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 2, .selector = 3 },
	{ .field = 0x604, .dmi_reg = 0x5a08, .module = CAMSS_X1E_IQ_GTM,
	  .payload = 0, .selector = 1 },
	{ .field = 0x624, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 0, .selector = 1 },
	{ .field = 0x630, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 1, .selector = 2 },
	{ .field = 0x63c, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 2, .selector = 3 },
	{ .field = 0x7c8, .dmi_reg = 0xa008, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 0, .selector = 1 },
	{ .field = 0x7d4, .dmi_reg = 0xa008, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 1, .selector = 2 },
	{ .field = 0x7e0, .dmi_reg = 0xa208, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 2, .selector = 1 },
	{ .field = 0x7ec, .dmi_reg = 0xa208, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 3, .selector = 2 },
};

static const struct camss_x1e_epoch0_reg_patch camss_x1e_epoch0_reg_v2[] = {
	{ .field = 0x78, .reg = 0x3d78, .module = CAMSS_X1E_IQ_PDPC, .value = 2 },
	{ .field = 0x7c, .reg = 0x3d7c, .module = CAMSS_X1E_IQ_PDPC, .value = 3 },
	{ .field = 0x80, .reg = 0x3d80, .module = CAMSS_X1E_IQ_PDPC, .value = 4 },
	{ .field = 0x84, .reg = 0x3d84, .module = CAMSS_X1E_IQ_PDPC, .value = 5 },
	{ .field = 0xc4, .reg = 0x4358, .module = CAMSS_X1E_IQ_LSC, .value = 0 },
	{ .field = 0xc8, .reg = 0x435c, .module = CAMSS_X1E_IQ_LSC, .value = 1 },
	{ .field = 0x13c, .reg = 0x456c, .module = CAMSS_X1E_IQ_WB, .value = 0 },
	{ .field = 0x140, .reg = 0x4570, .module = CAMSS_X1E_IQ_WB, .value = 1 },
	{ .field = 0x5e8, .reg = 0x5f58, .module = CAMSS_X1E_IQ_GAMMA, .value = 0 },
	{ .field = 0x5ec, .reg = 0x5f5c, .module = CAMSS_X1E_IQ_GAMMA, .value = 1 },
	{ .field = 0x620, .reg = 0xa058, .module = CAMSS_X1E_IQ_DSX, .value = 0 },
	{ .field = 0x624, .reg = 0xa05c, .module = CAMSS_X1E_IQ_DSX, .value = 1 },
	{ .field = 0x720, .reg = 0xa258, .module = CAMSS_X1E_IQ_DSX, .value = 2 },
	{ .field = 0x724, .reg = 0xa25c, .module = CAMSS_X1E_IQ_DSX, .value = 3 },
};

static const struct camss_x1e_epoch0_dmi_patch camss_x1e_epoch0_dmi_v2[] = {
	{ .field = 0xb4, .dmi_reg = 0x3d08, .module = CAMSS_X1E_IQ_PDPC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x110, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x11c, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 1, .selector = 2 },
	{ .field = 0x128, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 2, .selector = 3 },
	{ .field = 0x5d8, .dmi_reg = 0x5a08, .module = CAMSS_X1E_IQ_GTM,
	  .payload = 0, .selector = 1 },
	{ .field = 0x5f8, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 0, .selector = 1 },
	{ .field = 0x604, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 1, .selector = 2 },
	{ .field = 0x610, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 2, .selector = 3 },
	{ .field = 0x79c, .dmi_reg = 0xa008, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 0, .selector = 1 },
	{ .field = 0x7a8, .dmi_reg = 0xa008, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 1, .selector = 2 },
	{ .field = 0x7b4, .dmi_reg = 0xa208, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 2, .selector = 1 },
	{ .field = 0x7c0, .dmi_reg = 0xa208, .module = CAMSS_X1E_IQ_DSX,
	  .payload = 3, .selector = 2 },
};

static const struct camss_x1e_epoch0_reg_patch camss_x1e_epoch0_reg_v3[] = {
	{ .field = 0xa4, .reg = 0x3d78, .module = CAMSS_X1E_IQ_PDPC, .value = 2 },
	{ .field = 0xa8, .reg = 0x3d7c, .module = CAMSS_X1E_IQ_PDPC, .value = 3 },
	{ .field = 0xac, .reg = 0x3d80, .module = CAMSS_X1E_IQ_PDPC, .value = 4 },
	{ .field = 0xb0, .reg = 0x3d84, .module = CAMSS_X1E_IQ_PDPC, .value = 5 },
	{ .field = 0xf0, .reg = 0x4358, .module = CAMSS_X1E_IQ_LSC, .value = 0 },
	{ .field = 0xf4, .reg = 0x435c, .module = CAMSS_X1E_IQ_LSC, .value = 1 },
	{ .field = 0x168, .reg = 0x456c, .module = CAMSS_X1E_IQ_WB, .value = 0 },
	{ .field = 0x16c, .reg = 0x4570, .module = CAMSS_X1E_IQ_WB, .value = 1 },
	{ .field = 0x614, .reg = 0x5f58, .module = CAMSS_X1E_IQ_GAMMA, .value = 0 },
	{ .field = 0x618, .reg = 0x5f5c, .module = CAMSS_X1E_IQ_GAMMA, .value = 1 },
};

static const struct camss_x1e_epoch0_dmi_patch camss_x1e_epoch0_dmi_v3[] = {
	{ .field = 0xe0, .dmi_reg = 0x3d08, .module = CAMSS_X1E_IQ_PDPC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x13c, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x148, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 1, .selector = 2 },
	{ .field = 0x154, .dmi_reg = 0x4308, .module = CAMSS_X1E_IQ_LSC,
	  .payload = 2, .selector = 3 },
	{ .field = 0x604, .dmi_reg = 0x5a08, .module = CAMSS_X1E_IQ_GTM,
	  .payload = 0, .selector = 1 },
	{ .field = 0x624, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 0, .selector = 1 },
	{ .field = 0x630, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 1, .selector = 2 },
	{ .field = 0x63c, .dmi_reg = 0x5f08, .module = CAMSS_X1E_IQ_GAMMA,
	  .payload = 2, .selector = 3 },
};

static const struct camss_x1e_epoch0_reg_patch camss_x1e_epoch0_reg_v4[] = {
	{ .field = 0x78, .reg = 0x3d78, .module = CAMSS_X1E_IQ_PDPC, .value = 2 },
	{ .field = 0x7c, .reg = 0x3d7c, .module = CAMSS_X1E_IQ_PDPC, .value = 3 },
	{ .field = 0x80, .reg = 0x3d80, .module = CAMSS_X1E_IQ_PDPC, .value = 4 },
	{ .field = 0x84, .reg = 0x3d84, .module = CAMSS_X1E_IQ_PDPC, .value = 5 },
	{ .field = 0xc8, .reg = 0x456c, .module = CAMSS_X1E_IQ_WB, .value = 0 },
	{ .field = 0xcc, .reg = 0x4570, .module = CAMSS_X1E_IQ_WB, .value = 1 },
};

static const struct camss_x1e_epoch0_dmi_patch camss_x1e_epoch0_dmi_v4[] = {
	{ .field = 0xb4, .dmi_reg = 0x3d08, .module = CAMSS_X1E_IQ_PDPC,
	  .payload = 0, .selector = 1 },
	{ .field = 0x528, .dmi_reg = 0x5a08, .module = CAMSS_X1E_IQ_GTM,
	  .payload = 0, .selector = 1 },
};

static const struct camss_x1e_epoch0_variant_desc camss_x1e_epoch0_variants[] = {
	{ .main_bytes = 0x0958, .reg = camss_x1e_epoch0_reg_v0,
	  .reg_count = ARRAY_SIZE(camss_x1e_epoch0_reg_v0),
	  .dmi = camss_x1e_epoch0_dmi_v0,
	  .dmi_count = ARRAY_SIZE(camss_x1e_epoch0_dmi_v0) },
	{ .main_bytes = 0x0868, .reg = camss_x1e_epoch0_reg_v1,
	  .reg_count = ARRAY_SIZE(camss_x1e_epoch0_reg_v1),
	  .dmi = camss_x1e_epoch0_dmi_v1,
	  .dmi_count = ARRAY_SIZE(camss_x1e_epoch0_dmi_v1) },
	{ .main_bytes = 0x083c, .reg = camss_x1e_epoch0_reg_v2,
	  .reg_count = ARRAY_SIZE(camss_x1e_epoch0_reg_v2),
	  .dmi = camss_x1e_epoch0_dmi_v2,
	  .dmi_count = ARRAY_SIZE(camss_x1e_epoch0_dmi_v2) },
	{ .main_bytes = 0x06b8, .reg = camss_x1e_epoch0_reg_v3,
	  .reg_count = ARRAY_SIZE(camss_x1e_epoch0_reg_v3),
	  .dmi = camss_x1e_epoch0_dmi_v3,
	  .dmi_count = ARRAY_SIZE(camss_x1e_epoch0_dmi_v3) },
	{ .main_bytes = 0x05a4, .reg = camss_x1e_epoch0_reg_v4,
	  .reg_count = ARRAY_SIZE(camss_x1e_epoch0_reg_v4),
	  .dmi = camss_x1e_epoch0_dmi_v4,
	  .dmi_count = ARRAY_SIZE(camss_x1e_epoch0_dmi_v4) },
};

static_assert(ARRAY_SIZE(camss_x1e_epoch0_payloads) == 14);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_variants) ==
	      CAMSS_X1E_EPOCH0_CDM_VARIANT_COUNT);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v0) == 24);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v0) == 14);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v1) == 20);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v1) == 12);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v2) == 14);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v2) == 12);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v3) == 10);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v3) == 8);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_reg_v4) == 6);
static_assert(ARRAY_SIZE(camss_x1e_epoch0_dmi_v4) == 2);

static const struct camss_x1e_epoch0_payload_desc *
camss_x1e_epoch0_payload_desc(u8 module, u8 payload)
{
	unsigned int i;

	for (i = 0; i < ARRAY_SIZE(camss_x1e_epoch0_payloads); i++)
		if (camss_x1e_epoch0_payloads[i].module == module &&
		    camss_x1e_epoch0_payloads[i].payload == payload)
			return &camss_x1e_epoch0_payloads[i];

	return NULL;
}

static const struct camss_x1e_epoch0_variant_desc *
camss_x1e_epoch0_variant(size_t main_bytes)
{
	unsigned int i;

	for (i = 0; i < ARRAY_SIZE(camss_x1e_epoch0_variants); i++)
		if (camss_x1e_epoch0_variants[i].main_bytes == main_bytes)
			return &camss_x1e_epoch0_variants[i];

	return NULL;
}

static int camss_x1e_epoch0_validate_input(const struct camss_x1e_epoch0_input *input,
					   const struct camss_x1e_epoch0_variant_desc **variant_out)
{
	const struct camss_x1e_epoch0_variant_desc *variant;
	u8 expected_value[CAMSS_X1E_IQ_NUM] = { 0 };
	u8 expected_payload[CAMSS_X1E_IQ_NUM] = { 0 };
	unsigned int i;

	if (!input || !input->normalized_main.data || !input->request_id ||
	    input->subrequest)
		return -EINVAL;

	variant = camss_x1e_epoch0_variant(input->normalized_main.size);
	if (!variant)
		return -EINVAL;

	for (i = 0; i < variant->reg_count; i++) {
		const struct camss_x1e_epoch0_reg_patch *patch = &variant->reg[i];
		const u8 *main = input->normalized_main.data;

		if (patch->module >= CAMSS_X1E_IQ_NUM ||
		    patch->value >= CAMSS_X1E_EPOCH0_MODULE_REG_MAX ||
		    patch->field + sizeof(u32) > input->normalized_main.size ||
		    get_unaligned_le32(main + patch->field))
			return -EINVAL;
		expected_value[patch->module] |= BIT(patch->value);
	}

	for (i = 0; i < variant->dmi_count; i++) {
		const struct camss_x1e_epoch0_dmi_patch *patch = &variant->dmi[i];
		const struct camss_x1e_epoch0_payload_desc *payload;
		const u8 *main = input->normalized_main.data;

		if (patch->module >= CAMSS_X1E_IQ_NUM ||
		    patch->payload >= CAMSS_X1E_EPOCH0_MODULE_PAYLOAD_MAX ||
		    patch->field + sizeof(u32) > input->normalized_main.size ||
		    get_unaligned_le32(main + patch->field))
			return -EINVAL;
		payload = camss_x1e_epoch0_payload_desc(patch->module, patch->payload);
		if (!payload)
			return -EINVAL;
		expected_payload[patch->module] |= BIT(patch->payload);
	}

	for (i = 0; i < CAMSS_X1E_IQ_NUM; i++) {
		const struct camss_x1e_epoch0_iq_module_input *module = &input->module[i];
		unsigned int payload;

		if (module->value_valid != expected_value[i] ||
		    module->payload_valid != expected_payload[i])
			return -EINVAL;

		for (payload = 0; payload < CAMSS_X1E_EPOCH0_MODULE_PAYLOAD_MAX; payload++) {
			const struct camss_x1e_epoch0_payload_desc *desc;

			if (!(expected_payload[i] & BIT(payload)))
				continue;
			desc = camss_x1e_epoch0_payload_desc(i, payload);
			if (!desc || !module->payload[payload].data ||
			    module->payload[payload].size != desc->size)
				return -EINVAL;
		}
	}

	*variant_out = variant;
	return 0;
}

static void camss_x1e_epoch0_release(struct camss *camss,
				     struct camss_x1e_epoch0_materialized *out)
{
	if (!camss || !out)
		return;

	if (out->dmi_cpu) {
		memzero_explicit(out->dmi_cpu, CAMSS_X1E_EPOCH0_DMI_SIZE);
		dma_free_coherent(camss->dev, CAMSS_X1E_EPOCH0_DMI_SIZE,
				  out->dmi_cpu, out->dmi_dma);
	}
	if (out->cmd_cpu) {
		memzero_explicit(out->cmd_cpu, CAMSS_X1E_EPOCH0_CMD_SIZE);
		dma_free_coherent(camss->dev, CAMSS_X1E_EPOCH0_CMD_SIZE,
				  out->cmd_cpu, out->cmd_dma);
	}
	memset(out, 0, sizeof(*out));
}

static int camss_x1e_epoch0_materialize(struct camss *camss,
					struct camss_x1e_epoch0_materialized *out,
				 const struct camss_x1e_epoch0_input *input)
{
	const struct camss_x1e_epoch0_variant_desc *variant;
	u8 *cmd, *main, *dmi, *bl0, *bl2, *bl3, *bl4;
	unsigned int i;
	int ret;

	if (!camss || !camss->res || camss->res->version != CAMSS_X1E80100 ||
	    !camss->rtcdm1.present || !out)
		return -ENODEV;
	if (out->materialized || out->cmd_cpu || out->dmi_cpu)
		return -EBUSY;

	ret = camss_x1e_epoch0_validate_input(input, &variant);
	if (ret)
		return ret;

	ret = camss_rtcdm1_corpus_alloc(camss->dev,
					CAMSS_X1E_EPOCH0_CMD_SIZE,
					 &out->cmd_cpu, &out->cmd_dma);
	if (ret)
		return ret;
	ret = camss_rtcdm1_corpus_alloc(camss->dev,
					CAMSS_X1E_EPOCH0_DMI_SIZE,
					 &out->dmi_cpu, &out->dmi_dma);
	if (ret)
		goto err_release;

	cmd = out->cmd_cpu;
	dmi = out->dmi_cpu;
	bl0 = cmd + CAMSS_X1E_EPOCH0_BL0_OFFSET;
	main = cmd + CAMSS_X1E_EPOCH0_MAIN_OFFSET;
	bl2 = cmd + CAMSS_X1E_EPOCH0_BL2_OFFSET;
	bl3 = cmd + CAMSS_X1E_EPOCH0_BL3_OFFSET;
	bl4 = cmd + CAMSS_X1E_EPOCH0_BL4_OFFSET;

	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL0_CHANGE_BASE, bl0);
	memcpy(main, input->normalized_main.data, variant->main_bytes);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL2_CHANGE_BASE, bl2);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL3_REG_CONT, bl3 + 0x0);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL3_REG_OFFSET, bl3 + 0x4);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL3_VALUE0, bl3 + 0x8);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL3_VALUE1, bl3 + 0xc);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL4_REG_RANDOM, bl4 + 0x0);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL4_REG_OFFSET, bl4 + 0x4);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL4_REG_VALUE, bl4 + 0x8);
	put_unaligned_le32(CAMSS_X1E_EPOCH0_BL4_GEN_IRQ, bl4 + 0xc);
	put_unaligned_le32(lower_32_bits(input->request_id), bl4 + 0x10);

	for (i = 0; i < variant->dmi_count; i++) {
		const struct camss_x1e_epoch0_dmi_patch *patch = &variant->dmi[i];
		const struct camss_x1e_epoch0_payload_desc *payload =
			camss_x1e_epoch0_payload_desc(patch->module, patch->payload);
		const struct camss_rtcdm1_corpus_blob *blob =
			&input->module[patch->module].payload[patch->payload];
		u64 dma = (u64)out->dmi_dma + payload->offset;

		memcpy(dmi + payload->offset, blob->data, payload->size);
		put_unaligned_le32((u32)dma, main + patch->field);
	}

	for (i = 0; i < variant->reg_count; i++) {
		const struct camss_x1e_epoch0_reg_patch *patch = &variant->reg[i];
		u32 value = input->module[patch->module].value[patch->value];

		put_unaligned_le32(value, main + patch->field);
	}

	out->bl_dma[0] = (u32)out->cmd_dma + CAMSS_X1E_EPOCH0_BL0_OFFSET;
	out->bl_dma[1] = (u32)out->cmd_dma + CAMSS_X1E_EPOCH0_MAIN_OFFSET;
	out->bl_dma[2] = (u32)out->cmd_dma + CAMSS_X1E_EPOCH0_BL2_OFFSET;
	out->bl_dma[3] = (u32)out->cmd_dma + CAMSS_X1E_EPOCH0_BL3_OFFSET;
	out->bl_dma[4] = (u32)out->cmd_dma + CAMSS_X1E_EPOCH0_BL4_OFFSET;
	out->bl_len[0] = 0x0004;
	out->bl_len[1] = variant->main_bytes;
	out->bl_len[2] = 0x0004;
	out->bl_len[3] = 0x0010;
	out->bl_len[4] = 0x0014;
	out->materialized = true;
	return 0;

err_release:
	camss_x1e_epoch0_release(camss, out);
	return ret;
}

struct camss_x1e_epoch0_static_ops {
	int (*materialize)(struct camss *camss,
			   struct camss_x1e_epoch0_materialized *out,
			   const struct camss_x1e_epoch0_input *input);
	void (*release)(struct camss *camss, struct camss_x1e_epoch0_materialized *out);
};

/* Retention only: no ISR, VFE, CSID, RT-CDM submit or stream path references it. */
static const struct camss_x1e_epoch0_static_ops
camss_x1e_epoch0_recipe __used = {
	.materialize = camss_x1e_epoch0_materialize,
	.release = camss_x1e_epoch0_release,
};


/*
 * E003h disposable PIX oracle-capsule parser, retained and unreachable.
 *
 * The capsule bytes stay outside the kernel tree. This parser only maps the
 * versioned local capsule ABI onto the already-validated startup/priming corpus
 * inputs and one steady Epoch0 named-module input. It allocates no DMA, performs
 * no MMIO, submits no RT-CDM FIFO, and has no runtime caller.
 */
#define CAMSS_X1E_PIX_CAPSULE_MAGIC		"E3HPIX01"
#define CAMSS_X1E_PIX_CAPSULE_VERSION		1
#define CAMSS_X1E_PIX_CAPSULE_HEADER_BYTES	1024
#define CAMSS_X1E_PIX_CAPSULE_DESC_OFFSET	64
#define CAMSS_X1E_PIX_CAPSULE_DESC_BYTES	16
#define CAMSS_X1E_PIX_CAPSULE_SECTION_COUNT	36
#define CAMSS_X1E_PIX_CAPSULE_ALIGN		64
#define CAMSS_X1E_PIX_CAPSULE_TYPE_STARTUP_MAIN	1
#define CAMSS_X1E_PIX_CAPSULE_TYPE_STARTUP_PAYLOAD 2
#define CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MAIN	3
#define CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MODULES	4
#define CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_PAYLOAD	5
#define CAMSS_X1E_PIX_CAPSULE_MODULE_RECORD_BYTES	32

struct camss_x1e_pix_capsule_inputs {
	struct camss_rtcdm1_corpus_input startup;
	struct camss_rtcdm1_corpus_input priming;
	struct camss_x1e_epoch0_input steady;
};

static int camss_x1e_pix_capsule_validate_sections(const u8 *data, size_t size)
{
	u32 seen[6] = { 0 };
	unsigned int i, j;

	for (i = 0; i < CAMSS_X1E_PIX_CAPSULE_SECTION_COUNT; i++) {
		const u8 *d = data + CAMSS_X1E_PIX_CAPSULE_DESC_OFFSET +
			i * CAMSS_X1E_PIX_CAPSULE_DESC_BYTES;
		u32 type = get_unaligned_le32(d + 0x0);
		u32 index = get_unaligned_le32(d + 0x4);
		u32 offset = get_unaligned_le32(d + 0x8);
		u32 bytes = get_unaligned_le32(d + 0xc);
		u32 index_max;

		switch (type) {
		case CAMSS_X1E_PIX_CAPSULE_TYPE_STARTUP_MAIN:
			index_max = CAMSS_RTCDM1_CORPUS_PACKET_COUNT;
			break;
		case CAMSS_X1E_PIX_CAPSULE_TYPE_STARTUP_PAYLOAD:
			index_max = CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT;
			break;
		case CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MAIN:
		case CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MODULES:
			index_max = 1;
			break;
		case CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_PAYLOAD:
			index_max = ARRAY_SIZE(camss_x1e_epoch0_payloads);
			break;
		default:
			return -EINVAL;
		}

		if (index >= index_max || (seen[type] & BIT(index)) || !bytes ||
		    !IS_ALIGNED(offset, CAMSS_X1E_PIX_CAPSULE_ALIGN) ||
		    offset < CAMSS_X1E_PIX_CAPSULE_HEADER_BYTES || offset > size ||
		    bytes > size - offset)
			return -EINVAL;
		seen[type] |= BIT(index);

		for (j = 0; j < i; j++) {
			const u8 *p = data + CAMSS_X1E_PIX_CAPSULE_DESC_OFFSET +
				j * CAMSS_X1E_PIX_CAPSULE_DESC_BYTES;
			u32 poff = get_unaligned_le32(p + 0x8);
			u32 pbytes = get_unaligned_le32(p + 0xc);

			if (offset < poff + pbytes && poff < offset + bytes)
				return -EINVAL;
		}
	}

	if (seen[CAMSS_X1E_PIX_CAPSULE_TYPE_STARTUP_MAIN] != GENMASK(3, 0) ||
	    seen[CAMSS_X1E_PIX_CAPSULE_TYPE_STARTUP_PAYLOAD] != GENMASK(15, 0) ||
	    seen[CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MAIN] != BIT(0) ||
	    seen[CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MODULES] != BIT(0) ||
	    seen[CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_PAYLOAD] != GENMASK(13, 0))
		return -EINVAL;

	return 0;
}

static int camss_x1e_pix_capsule_section(const u8 *data, u32 type, u32 index,
					 const u8 **section, size_t *bytes)
{
	unsigned int i;

	for (i = 0; i < CAMSS_X1E_PIX_CAPSULE_SECTION_COUNT; i++) {
		const u8 *d = data + CAMSS_X1E_PIX_CAPSULE_DESC_OFFSET +
			i * CAMSS_X1E_PIX_CAPSULE_DESC_BYTES;

		if (get_unaligned_le32(d + 0x0) != type ||
		    get_unaligned_le32(d + 0x4) != index)
			continue;
		*section = data + get_unaligned_le32(d + 0x8);
		*bytes = get_unaligned_le32(d + 0xc);
		return 0;
	}

	return -ENOENT;
}

static int camss_x1e_pix_capsule_parse(const void *capsule, size_t size,
				       struct camss_x1e_pix_capsule_inputs *out)
{
	const struct camss_x1e_epoch0_variant_desc *variant;
	const u8 *data = capsule;
	const u8 *section;
	size_t bytes;
	unsigned int i, j;
	int ret;

	if (!data || !out || size < CAMSS_X1E_PIX_CAPSULE_HEADER_BYTES ||
	    memcmp(data, CAMSS_X1E_PIX_CAPSULE_MAGIC, 8) ||
	    get_unaligned_le32(data + 0x08) != CAMSS_X1E_PIX_CAPSULE_VERSION ||
	    get_unaligned_le32(data + 0x0c) != CAMSS_X1E_PIX_CAPSULE_HEADER_BYTES ||
	    get_unaligned_le32(data + 0x10) != size ||
	    get_unaligned_le32(data + 0x14) != CAMSS_X1E_PIX_CAPSULE_SECTION_COUNT ||
	    get_unaligned_le32(data + 0x38) || get_unaligned_le32(data + 0x3c))
		return -EINVAL;

	ret = camss_x1e_pix_capsule_validate_sections(data, size);
	if (ret)
		return ret;

	memset(out, 0, sizeof(*out));
	out->startup.dynamic[0] = get_unaligned_le32(data + 0x18);
	out->startup.dynamic[1] = get_unaligned_le32(data + 0x1c);
	out->priming.dynamic[0] = get_unaligned_le32(data + 0x20);
	out->priming.dynamic[1] = get_unaligned_le32(data + 0x24);
	out->startup.dynamic_valid = CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID;
	out->priming.dynamic_valid = CAMSS_RTCDM1_CORPUS_DYNAMIC_VALID;

	for (i = 0; i < CAMSS_RTCDM1_CORPUS_PACKET_COUNT; i++) {
		ret = camss_x1e_pix_capsule_section(data,
				CAMSS_X1E_PIX_CAPSULE_TYPE_STARTUP_MAIN, i,
				&section, &bytes);
		if (ret || bytes != camss_rtcdm1_corpus_packet_used[i])
			return -EINVAL;
		out->startup.main[i].data = section;
		out->startup.main[i].size = bytes;
		out->priming.main[i] = out->startup.main[i];
	}

	for (i = 0; i < CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT; i++) {
		ret = camss_x1e_pix_capsule_section(data,
				CAMSS_X1E_PIX_CAPSULE_TYPE_STARTUP_PAYLOAD, i,
				&section, &bytes);
		if (ret || bytes != camss_rtcdm1_corpus_payloads[i].size)
			return -EINVAL;
		out->startup.payload[i].data = section;
		out->startup.payload[i].size = bytes;
		out->priming.payload[i] = out->startup.payload[i];
	}

	ret = camss_x1e_pix_capsule_section(data,
			CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MAIN, 0,
			&section, &bytes);
	if (ret || bytes != get_unaligned_le32(data + 0x28))
		return -EINVAL;
	out->steady.normalized_main.data = section;
	out->steady.normalized_main.size = bytes;
	out->steady.request_id = get_unaligned_le64(data + 0x2c);
	out->steady.subrequest = get_unaligned_le32(data + 0x34);

	ret = camss_x1e_pix_capsule_section(data,
			CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MODULES, 0,
			&section, &bytes);
	if (ret || bytes != CAMSS_X1E_IQ_NUM * CAMSS_X1E_PIX_CAPSULE_MODULE_RECORD_BYTES)
		return -EINVAL;
	for (i = 0; i < CAMSS_X1E_IQ_NUM; i++) {
		const u8 *m = section + i * CAMSS_X1E_PIX_CAPSULE_MODULE_RECORD_BYTES;

		out->steady.module[i].value_valid = m[0];
		out->steady.module[i].payload_valid = m[1];
		if (get_unaligned_le16(m + 2) || get_unaligned_le32(m + 28))
			return -EINVAL;
		for (j = 0; j < CAMSS_X1E_EPOCH0_MODULE_REG_MAX; j++)
			out->steady.module[i].value[j] = get_unaligned_le32(m + 4 + j * 4);
	}

	for (i = 0; i < ARRAY_SIZE(camss_x1e_epoch0_payloads); i++) {
		const struct camss_x1e_epoch0_payload_desc *d = &camss_x1e_epoch0_payloads[i];

		ret = camss_x1e_pix_capsule_section(data,
				CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_PAYLOAD, i,
				&section, &bytes);
		if (ret || bytes != d->size)
			return -EINVAL;
		out->steady.module[d->module].payload[d->payload].data = section;
		out->steady.module[d->module].payload[d->payload].size = bytes;
	}

	ret = camss_rtcdm1_corpus_validate_input(&out->startup);
	if (ret)
		return ret;
	ret = camss_rtcdm1_corpus_validate_input(&out->priming);
	if (ret)
		return ret;
	return camss_x1e_epoch0_validate_input(&out->steady, &variant);
}

struct camss_x1e_pix_capsule_static_ops {
	int (*parse)(const void *capsule, size_t size,
		     struct camss_x1e_pix_capsule_inputs *out);
};

/* Retention only: no firmware loader, ioctl, probe or stream path references it. */
static const struct camss_x1e_pix_capsule_static_ops
camss_x1e_pix_capsule_recipe __used = {
	.parse = camss_x1e_pix_capsule_parse,
};


/*
 * E003h parsed PIX capsule -> Linux-owned DMA materialization, retained and
 * unreachable. This composes only 0019/0021 startup/priming materialization and
 * 0025 steady Epoch0 materialization. It performs no MMIO or FIFO submission.
 *
 * Selector-2 priming is not a one-BL replay of the main corpus packet. The
 * same-machine Windows queue capture proves four complete priming batches:
 * packet0 has four BLs, while packets1..3 have five. Keep their small companion
 * command lists in a separate Linux-owned coherent arena; BL1 always points at
 * the already-materialized priming main packet with Linux-patched DMI IOVAs.
 */
#define CAMSS_X1E_PIX_PRIMING_PACKET_COUNT	4
#define CAMSS_X1E_PIX_PRIMING_MAX_BL_COUNT	5
#define CAMSS_X1E_PIX_PRIMING_COMPANION_SIZE	SZ_4K
#define CAMSS_X1E_PIX_PRIMING_PACKET_STRIDE	0x100
#define CAMSS_X1E_PIX_STARTUP_WRAPPER_SIZE	SZ_4K
#define CAMSS_X1E_PIX_STARTUP_PACKET_STRIDE	0x100
#define CAMSS_X1E_PIX_STARTUP_VFE_BASE_OFFSET	0x00
#define CAMSS_X1E_PIX_STARTUP_CSID_BASE_OFFSET	0x40
#define CAMSS_X1E_PIX_STARTUP_COMPANION_OFFSET	0x80
#define CAMSS_X1E_PIX_STARTUP_CHANGE_BASE	0x0800f000
#define CAMSS_X1E_PIX_STARTUP_CSID_CHANGE_BASE	0x08057000

struct camss_x1e_pix_startup_wrapper {
	void *cpu;
	dma_addr_t dma;
	u32 vfe_base_dma[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	u16 vfe_base_len[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	u32 csid_base_dma[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	u16 csid_base_len[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	u32 companion_dma[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	u16 companion_len[CAMSS_RTCDM1_CORPUS_PACKET_COUNT];
	bool materialized;
};

struct camss_x1e_pix_prime {
	void *cpu;
	dma_addr_t dma;
	u32 bl_dma[CAMSS_X1E_PIX_PRIMING_PACKET_COUNT]
		  [CAMSS_X1E_PIX_PRIMING_MAX_BL_COUNT];
	u16 bl_len[CAMSS_X1E_PIX_PRIMING_PACKET_COUNT]
		  [CAMSS_X1E_PIX_PRIMING_MAX_BL_COUNT];
	u8 bl_count[CAMSS_X1E_PIX_PRIMING_PACKET_COUNT];
	bool materialized;
};

struct camss_x1e_pix_capsule_materialized {
	struct camss_rtcdm1_corpus startup;
	struct camss_x1e_pix_startup_wrapper startup_wrapper;
	struct camss_rtcdm1_corpus priming;
	struct camss_x1e_pix_prime prime;
	struct camss_x1e_epoch0_materialized steady;
	bool materialized;
};

static void camss_x1e_pix_startup_wrapper_release(struct camss *camss,
						  struct camss_x1e_pix_startup_wrapper *wrapper)
{
	if (!camss || !wrapper)
		return;

	if (wrapper->cpu) {
		memzero_explicit(wrapper->cpu, CAMSS_X1E_PIX_STARTUP_WRAPPER_SIZE);
		dma_free_coherent(camss->dev, CAMSS_X1E_PIX_STARTUP_WRAPPER_SIZE,
				  wrapper->cpu, wrapper->dma);
	}
	memset(wrapper, 0, sizeof(*wrapper));
}

static int camss_x1e_pix_startup_wrapper_materialize(struct camss *camss,
						     struct camss_x1e_pix_startup_wrapper *out)
{
	static const u32 companion_packet0[] = {
		0x03000001, 0x00000330, 0x00000000,
		0x03000002, 0x0000037c, 0x00000001, 0x00000000,
		0x03000002, 0x0000035c, 0x0eff0000, 0x086f0000,
		0x03000002, 0x00000384, 0x0000001f, 0x08700f00,
	};
	static const u32 companion_common[] = {
		0x03000002, 0x0000035c, 0x0eff0000, 0x086f0000,
	};
	u8 *cpu;
	unsigned int packet;
	unsigned int i;
	int ret;

	if (!camss || !out || out->materialized || out->cpu)
		return -EINVAL;

	ret = camss_rtcdm1_corpus_alloc(camss->dev,
					CAMSS_X1E_PIX_STARTUP_WRAPPER_SIZE,
					&out->cpu, &out->dma);
	if (ret)
		return ret;

	cpu = out->cpu;
	for (packet = 0; packet < CAMSS_RTCDM1_CORPUS_PACKET_COUNT; packet++) {
		u32 base = packet * CAMSS_X1E_PIX_STARTUP_PACKET_STRIDE;
		u8 *vfe_base = cpu + base + CAMSS_X1E_PIX_STARTUP_VFE_BASE_OFFSET;
		u8 *csid_base = cpu + base + CAMSS_X1E_PIX_STARTUP_CSID_BASE_OFFSET;
		u8 *companion = cpu + base + CAMSS_X1E_PIX_STARTUP_COMPANION_OFFSET;
		u64 dma = (u64)out->dma + base;
		const u32 *words;
		unsigned int count;

		put_unaligned_le32(CAMSS_X1E_PIX_STARTUP_CHANGE_BASE, vfe_base);
		put_unaligned_le32(CAMSS_X1E_PIX_STARTUP_CSID_CHANGE_BASE, csid_base);
		out->vfe_base_dma[packet] = (u32)dma + CAMSS_X1E_PIX_STARTUP_VFE_BASE_OFFSET;
		out->vfe_base_len[packet] = sizeof(u32);
		out->csid_base_dma[packet] = (u32)dma + CAMSS_X1E_PIX_STARTUP_CSID_BASE_OFFSET;
		out->csid_base_len[packet] = sizeof(u32);

		if (!packet) {
			words = companion_packet0;
			count = ARRAY_SIZE(companion_packet0);
		} else {
			words = companion_common;
			count = ARRAY_SIZE(companion_common);
		}
		for (i = 0; i < count; i++)
			put_unaligned_le32(words[i], companion + i * sizeof(u32));
		out->companion_dma[packet] = (u32)dma + CAMSS_X1E_PIX_STARTUP_COMPANION_OFFSET;
		out->companion_len[packet] = count * sizeof(u32);
	}
	out->materialized = true;
	return 0;
}

static void camss_x1e_pix_prime_write(u8 *dst, const u32 *words,
				      unsigned int count)
{
	unsigned int i;

	for (i = 0; i < count; i++)
		put_unaligned_le32(words[i], dst + i * sizeof(u32));
}

static void camss_x1e_pix_prime_release(struct camss *camss,
					struct camss_x1e_pix_prime *prime)
{
	if (!camss || !prime)
		return;
	if (prime->cpu) {
		memzero_explicit(prime->cpu, CAMSS_X1E_PIX_PRIMING_COMPANION_SIZE);
		dma_free_coherent(camss->dev, CAMSS_X1E_PIX_PRIMING_COMPANION_SIZE,
				  prime->cpu, prime->dma);
	}
	memset(prime, 0, sizeof(*prime));
}

static int camss_x1e_pix_prime_materialize(struct camss *camss,
					   struct camss_x1e_pix_prime *out,
					   const struct camss_rtcdm1_corpus *main)
{
	static const u32 change_vfe1[] = { 0x0800f000 };
	static const u32 change_companion[] = { 0x08057000 };
	static const u32 companion_common[] = {
		0x03000002, 0x0000035c, 0x0eff0000, 0x086f0000,
	};
	static const u32 companion_packet0[] = {
		0x03000001, 0x00000330, 0x00000000,
		0x03000002, 0x0000037c, 0x00000001, 0x00000000,
		0x03000002, 0x0000035c, 0x0eff0000, 0x086f0000,
		0x03000002, 0x00000384, 0x0000001f, 0x08700f00,
	};
	static const u32 irq_prefix[] = {
		0x04000001, 0x00000018, 0x01f501f5, 0x06000000,
	};
	u8 *cpu;
	unsigned int packet;
	int ret;

	if (!camss || !out || !main || !main->materialized || out->materialized)
		return -EINVAL;

	ret = camss_rtcdm1_corpus_alloc(camss->dev,
					CAMSS_X1E_PIX_PRIMING_COMPANION_SIZE,
					 &out->cpu, &out->dma);
	if (ret)
		return ret;
	cpu = out->cpu;

	for (packet = 0; packet < CAMSS_X1E_PIX_PRIMING_PACKET_COUNT; packet++) {
		u32 base = packet * CAMSS_X1E_PIX_PRIMING_PACKET_STRIDE;
		u8 *bl0 = cpu + base;
		u8 *bl2 = cpu + base + 0x40;
		u8 *bl3 = cpu + base + 0x80;
		u8 *bl4 = cpu + base + 0xc0;
		u64 dma = (u64)out->dma + base;

		camss_x1e_pix_prime_write(bl0, change_vfe1,
					  ARRAY_SIZE(change_vfe1));
		camss_x1e_pix_prime_write(bl2, change_companion,
					  ARRAY_SIZE(change_companion));
		out->bl_dma[packet][0] = (u32)dma;
		out->bl_len[packet][0] = sizeof(change_vfe1);
		out->bl_dma[packet][1] = main->packet_dma[packet];
		out->bl_len[packet][1] = main->packet_len[packet];
		out->bl_dma[packet][2] = (u32)dma + 0x40;
		out->bl_len[packet][2] = sizeof(change_companion);

		if (!packet) {
			camss_x1e_pix_prime_write(bl3, companion_packet0,
						  ARRAY_SIZE(companion_packet0));
			out->bl_dma[packet][3] = (u32)dma + 0x80;
			out->bl_len[packet][3] = sizeof(companion_packet0);
			out->bl_count[packet] = 4;
			continue;
		}

		camss_x1e_pix_prime_write(bl3, companion_common,
					  ARRAY_SIZE(companion_common));
		camss_x1e_pix_prime_write(bl4, irq_prefix,
					  ARRAY_SIZE(irq_prefix));
		put_unaligned_le32(packet, bl4 + sizeof(irq_prefix));
		out->bl_dma[packet][3] = (u32)dma + 0x80;
		out->bl_len[packet][3] = sizeof(companion_common);
		out->bl_dma[packet][4] = (u32)dma + 0xc0;
		out->bl_len[packet][4] = sizeof(irq_prefix) + sizeof(u32);
		out->bl_count[packet] = 5;
	}

	out->materialized = true;
	return 0;
}

static void camss_x1e_pix_capsule_materialized_release(
	struct camss *camss, struct camss_x1e_pix_capsule_materialized *out)
{
	if (!camss || !out)
		return;

	camss_x1e_epoch0_release(camss, &out->steady);
	camss_x1e_pix_prime_release(camss, &out->prime);
	camss_rtcdm1_corpus_release(camss, &out->priming);
	camss_x1e_pix_startup_wrapper_release(camss, &out->startup_wrapper);
	camss_rtcdm1_corpus_release(camss, &out->startup);
	memset(out, 0, sizeof(*out));
}

static int camss_x1e_pix_capsule_materialize(
	struct camss *camss, struct camss_x1e_pix_capsule_materialized *out,
	const struct camss_x1e_pix_capsule_inputs *input)
{
	int ret;

	if (!camss || !out || !input || out->materialized ||
	    out->startup.materialized || out->startup_wrapper.materialized ||
	    out->priming.materialized || out->prime.materialized ||
	    out->steady.materialized)
		return -EINVAL;

	ret = camss_rtcdm1_corpus_materialize(camss, &out->startup,
					       &input->startup);
	if (ret)
		return ret;

	ret = camss_x1e_pix_startup_wrapper_materialize(camss, &out->startup_wrapper);
	if (ret)
		goto err_release;

	ret = camss_rtcdm1_corpus_materialize(camss, &out->priming,
					       &input->priming);
	if (ret)
		goto err_release;

	ret = camss_x1e_pix_prime_materialize(camss, &out->prime,
					      &out->priming);
	if (ret)
		goto err_release;

	ret = camss_x1e_epoch0_materialize(camss, &out->steady, &input->steady);
	if (ret)
		goto err_release;

	out->materialized = true;
	return 0;

err_release:
	camss_x1e_pix_capsule_materialized_release(camss, out);
	return ret;
}

struct camss_x1e_pix_capsule_materialize_static_ops {
	int (*materialize)(struct camss *camss,
			   struct camss_x1e_pix_capsule_materialized *out,
			   const struct camss_x1e_pix_capsule_inputs *input);
	void (*release)(struct camss *camss,
			struct camss_x1e_pix_capsule_materialized *out);
};

/* Retention only: no probe, VFE, RT-CDM submit, firmware or stream reference. */
static const struct camss_x1e_pix_capsule_materialize_static_ops
camss_x1e_pix_capsule_materialize_recipe __used = {
	.materialize = camss_x1e_pix_capsule_materialize,
	.release = camss_x1e_pix_capsule_materialized_release,
};


/*
 * E003h bounded PIX RT-CDM submission primitives, retained and unreachable.
 *
 * These wrappers compose only the already-proven Windows RT-CDM recipe with
 * Linux-owned materialized command buffers. Queue lengths are passed exactly as
 * Windows encodes them: byte_count - 1 in FIFO0 bits 19:0. The software close
 * corresponds to the later manager/session delete phase: it disables the Linux
 * IRQ ownership only and performs no RT-CDM MMIO.
 */
static void camss_x1e_pix_rtcdm_close_sw(struct camss *camss)
{
	struct camss_rtcdm *rt;

	if (!camss)
		return;
	rt = &camss->rtcdm1;
	if (!rt->present)
		return;

	mutex_lock(&rt->lock);
	if (READ_ONCE(rt->irq_armed)) {
		disable_irq(rt->irq);
		WRITE_ONCE(rt->irq_armed, false);
	}
	mutex_unlock(&rt->lock);
}

static int camss_x1e_pix_rtcdm_open_start(struct camss *camss)
{
	int ret;

	if (!camss || !camss->res || camss->res->version != CAMSS_X1E80100)
		return -EINVAL;

	ret = camss_rtcdm1_windows_open_init(camss);
	if (ret) {
		dev_err(camss->dev, "E003h PIX RT-CDM open/init failed: %d\n", ret);
		return ret;
	}
	ret = camss_rtcdm1_windows_start(camss);
	if (ret) {
		dev_err(camss->dev, "E003h PIX RT-CDM core start failed: %d\n", ret);
		camss_x1e_pix_rtcdm_close_sw(camss);
	}
	return ret;
}

static int camss_x1e_pix_submit_startup(struct camss *camss,
	const struct camss_x1e_pix_startup_wrapper *wrapper,
	const struct camss_rtcdm1_corpus *corpus, unsigned int packet)
{
	int ret;

	if (!wrapper || !wrapper->materialized || !corpus ||
	    !corpus->materialized || packet >= CAMSS_RTCDM1_CORPUS_PACKET_COUNT ||
	    !wrapper->vfe_base_dma[packet] ||
	    wrapper->vfe_base_len[packet] != sizeof(u32) ||
	    !corpus->packet_dma[packet] || !corpus->packet_len[packet] ||
	    !wrapper->csid_base_dma[packet] ||
	    wrapper->csid_base_len[packet] != sizeof(u32) ||
	    !wrapper->companion_dma[packet] || !wrapper->companion_len[packet])
		return -EINVAL;

	/*
	 * Match the captured Windows startup ownership exactly: establish the VFE1
	 * base, submit the IFE main BL, switch RT-CDM to CSID1, then submit the
	 * descriptor-1 CSID companion BL. The companion bytes are unchanged from
	 * the prior CPU-MMIO replay; only their hardware owner/transport changes.
	 */
	ret = camss_rtcdm1_windows_fifo0_commit(camss,
						wrapper->vfe_base_dma[packet],
						wrapper->vfe_base_len[packet] - 1);
	if (ret) {
		dev_err(camss->dev,
			"E003h PIX startup packet%u VFE CHANGE_BASE failed: %d\n",
			packet, ret);
		return ret;
	}

	ret = camss_rtcdm1_windows_fifo0_commit(camss, corpus->packet_dma[packet],
						corpus->packet_len[packet] - 1);
	if (ret) {
		dev_err(camss->dev, "E003h PIX startup packet%u failed: %d\n",
			packet, ret);
		return ret;
	}

	ret = camss_rtcdm1_windows_fifo0_commit(camss,
						wrapper->csid_base_dma[packet],
						wrapper->csid_base_len[packet] - 1);
	if (ret) {
		dev_err(camss->dev,
			"E003h PIX startup packet%u CSID CHANGE_BASE failed: %d\n",
			packet, ret);
		return ret;
	}

	ret = camss_rtcdm1_windows_fifo0_commit(camss,
						wrapper->companion_dma[packet],
						wrapper->companion_len[packet] - 1);
	if (ret)
		dev_err(camss->dev,
			"E003h PIX startup packet%u CSID companion failed: %d\n",
			packet, ret);
	return ret;
}

static int camss_x1e_pix_submit_prime(struct camss *camss,
				      const struct camss_x1e_pix_prime *prime,
				      unsigned int packet)
{
	unsigned int i;
	int ret;

	if (!prime || !prime->materialized ||
	    packet >= CAMSS_X1E_PIX_PRIMING_PACKET_COUNT ||
	    !prime->bl_count[packet])
		return -EINVAL;

	for (i = 0; i < prime->bl_count[packet]; i++) {
		if (!prime->bl_dma[packet][i] || !prime->bl_len[packet][i])
			return -EINVAL;
		ret = camss_rtcdm1_windows_fifo0_commit(camss,
							prime->bl_dma[packet][i],
							prime->bl_len[packet][i] - 1);
		if (ret) {
			dev_err(camss->dev,
				"E003h PIX prime packet%u BL%u failed: %d\n",
				packet, i, ret);
			return ret;
		}
	}

	return 0;
}

static int camss_x1e_pix_rtcdm_submit_epoch0_batch(
	struct camss *camss, const struct camss_x1e_epoch0_materialized *steady)
{
	unsigned int i;
	int ret;

	if (!steady || !steady->materialized)
		return -EINVAL;

	for (i = 0; i < CAMSS_X1E_EPOCH0_CDM_STEADY_BL_COUNT; i++) {
		if (!steady->bl_dma[i] || !steady->bl_len[i])
			return -EINVAL;
		ret = camss_rtcdm1_windows_fifo0_commit(camss, steady->bl_dma[i],
							steady->bl_len[i] - 1);
		if (ret) {
			dev_err(camss->dev, "E003h PIX steady BL%u failed: %d\n", i, ret);
			return ret;
		}
	}

	return 0;
}

static void camss_x1e_pix_rtcdm_stop_close(struct camss *camss)
{
	camss_rtcdm1_windows_stop(camss);
	camss_x1e_pix_rtcdm_close_sw(camss);
}

struct camss_x1e_pix_rtcdm_static_ops {
	int (*open_start)(struct camss *camss);
	int (*submit_startup)(struct camss *camss,
		const struct camss_x1e_pix_startup_wrapper *wrapper,
		const struct camss_rtcdm1_corpus *corpus, unsigned int packet);
	int (*submit_prime)(struct camss *camss,
			    const struct camss_x1e_pix_prime *prime,
			    unsigned int packet);
	int (*submit_epoch0_batch)(struct camss *camss,
				   const struct camss_x1e_epoch0_materialized *steady);
	void (*stop_close)(struct camss *camss);
};

/* Retention only: the bounded PIX hardware-order runner does not exist yet. */
static const struct camss_x1e_pix_rtcdm_static_ops
camss_x1e_pix_rtcdm_recipe __used = {
	.open_start = camss_x1e_pix_rtcdm_open_start,
	.submit_startup = camss_x1e_pix_submit_startup,
	.submit_prime = camss_x1e_pix_submit_prime,
	.submit_epoch0_batch = camss_x1e_pix_rtcdm_submit_epoch0_batch,
	.stop_close = camss_x1e_pix_rtcdm_stop_close,
};

/*
 * E003h bounded VFE1 PIX cross-file hardware-order/rollback contract.
 *
 * This is intentionally data only.  The successful RDI runtime already proved
 * the normal V4L2 prepare/unprepare power ownership on this exact front graph.
 * A future PIX start callback can therefore reuse v4l2_pipeline_pm_get/put for
 * VFE1/CSID1/CSIPHY2 resource power and must not acquire duplicate power refs.
 * The generic VFE1 PIX s_stream path remains forbidden because it still maps
 * PIX to the RDI-style WM27 path; VFE1 activation is RT-CDM + BUS owned.
 *
 * Same-machine cross-order now places all four selector-2 priming replays:
 * packet0 -> replay0 -> packet1 -> BUS prepare -> replay1 -> packet2/3 ->
 * CSID1 -> ISP done -> CSIPHY2 -> sensor -> replay2 -> replay3 -> steady.
 * This contract remains data-only; callable execution is still a later gate.
 */
#define CAMSS_X1E_PIX_HW_HOST_STAGE_COUNT	16
#define CAMSS_X1E_PIX_HW_STOP_STAGE_COUNT	5
#define CAMSS_X1E_PIX_HW_ROLLBACK_STAGE_COUNT	7

enum camss_x1e_pix_hw_op {
	CAMSS_X1E_PIX_HW_PIPELINE_PM_PREPARE,
	CAMSS_X1E_PIX_HW_RTCDM_OPEN_START,
	CAMSS_X1E_PIX_HW_IFE1_RESOURCE_HELD,
	CAMSS_X1E_PIX_HW_STARTUP_PACKET0,
	CAMSS_X1E_PIX_HW_PRIMING_REPLAY0,
	CAMSS_X1E_PIX_HW_STARTUP_PACKET1,
	CAMSS_X1E_PIX_HW_BUS_PREPARE,
	CAMSS_X1E_PIX_HW_PRIMING_REPLAY1,
	CAMSS_X1E_PIX_HW_STARTUP_PACKET2,
	CAMSS_X1E_PIX_HW_STARTUP_PACKET3,
	CAMSS_X1E_PIX_HW_CSID1_IPP_START,
	CAMSS_X1E_PIX_HW_ISP_START_DONE,
	CAMSS_X1E_PIX_HW_CSIPHY2_START,
	CAMSS_X1E_PIX_HW_SENSOR_START,
	CAMSS_X1E_PIX_HW_PRIMING_REPLAY2,
	CAMSS_X1E_PIX_HW_PRIMING_REPLAY3,
	CAMSS_X1E_PIX_HW_STEADY_READY,
	CAMSS_X1E_PIX_HW_EPOCH0_POLL,
	CAMSS_X1E_PIX_HW_BUS_UPDATE,
	CAMSS_X1E_PIX_HW_STEADY_CDM,
	CAMSS_X1E_PIX_HW_VIDEO_POLL,
	CAMSS_X1E_PIX_HW_CSID1_IPP_STOP,
	CAMSS_X1E_PIX_HW_BUS_STOP,
	CAMSS_X1E_PIX_HW_RTCDM_STOP_CLOSE,
	CAMSS_X1E_PIX_HW_CSIPHY2_STOP,
	CAMSS_X1E_PIX_HW_SENSOR_STOP,
	CAMSS_X1E_PIX_HW_PIPELINE_PM_RELEASE,
};

enum camss_x1e_pix_hw_rollback_owner {
	CAMSS_X1E_PIX_ROLLBACK_SENSOR,
	CAMSS_X1E_PIX_ROLLBACK_CSIPHY2,
	CAMSS_X1E_PIX_ROLLBACK_CSID1,
	CAMSS_X1E_PIX_ROLLBACK_BUS,
	CAMSS_X1E_PIX_ROLLBACK_RTCDM,
	CAMSS_X1E_PIX_ROLLBACK_CAPSULE_DMA,
	CAMSS_X1E_PIX_ROLLBACK_PIPELINE_PM,
};

struct camss_x1e_pix_hw_order_contract {
	u8 host_order[CAMSS_X1E_PIX_HW_HOST_STAGE_COUNT];
	u8 stop_order[CAMSS_X1E_PIX_HW_STOP_STAGE_COUNT];
	u8 rollback_order[CAMSS_X1E_PIX_HW_ROLLBACK_STAGE_COUNT];
	bool pipeline_pm_owns_resource_power;
	bool vfe1_resource_power_reuses_vfe_get;
	bool csid1_power_reuses_subdev_power;
	bool csid1_ipp_reuses_hw_configure_stream;
	bool csiphy2_power_reuses_subdev_power;
	bool csiphy2_lanes_reuse_subdev_stream;
	bool sensor_reuses_subdev_stream;
	bool generic_vfe1_pix_stream_forbidden;
	bool epoch0_order_closed;
	bool stop_host_order_closed;
	bool sensor_vs_csiphy_stop_order_required;
	bool replay01_before_isp_done;
	bool replay23_after_isp_done;
	bool replay01_vs_csid_start_closed;
	bool replay23_vs_mipi_sensor_start_closed;
	bool startup_priming_interleave_closed;
	bool callable_runner_authorized;
};

static const struct camss_x1e_pix_hw_order_contract
camss_x1e_pix_hw_order_contract __used = {
	.host_order = {
		CAMSS_X1E_PIX_HW_RTCDM_OPEN_START,
		CAMSS_X1E_PIX_HW_IFE1_RESOURCE_HELD,
		CAMSS_X1E_PIX_HW_STARTUP_PACKET0,
		CAMSS_X1E_PIX_HW_PRIMING_REPLAY0,
		CAMSS_X1E_PIX_HW_STARTUP_PACKET1,
		CAMSS_X1E_PIX_HW_BUS_PREPARE,
		CAMSS_X1E_PIX_HW_PRIMING_REPLAY1,
		CAMSS_X1E_PIX_HW_STARTUP_PACKET2,
		CAMSS_X1E_PIX_HW_STARTUP_PACKET3,
		CAMSS_X1E_PIX_HW_CSID1_IPP_START,
		CAMSS_X1E_PIX_HW_ISP_START_DONE,
		CAMSS_X1E_PIX_HW_CSIPHY2_START,
		CAMSS_X1E_PIX_HW_SENSOR_START,
		CAMSS_X1E_PIX_HW_PRIMING_REPLAY2,
		CAMSS_X1E_PIX_HW_PRIMING_REPLAY3,
		CAMSS_X1E_PIX_HW_STEADY_READY,
	},
	/* One Windows-observed valid serialization of the unordered MIPI/sensor tail. */
	.stop_order = {
		CAMSS_X1E_PIX_HW_CSID1_IPP_STOP,
		CAMSS_X1E_PIX_HW_BUS_STOP,
		CAMSS_X1E_PIX_HW_RTCDM_STOP_CLOSE,
		CAMSS_X1E_PIX_HW_CSIPHY2_STOP,
		CAMSS_X1E_PIX_HW_SENSOR_STOP,
	},
	.rollback_order = {
		CAMSS_X1E_PIX_ROLLBACK_SENSOR,
		CAMSS_X1E_PIX_ROLLBACK_CSIPHY2,
		CAMSS_X1E_PIX_ROLLBACK_CSID1,
		CAMSS_X1E_PIX_ROLLBACK_BUS,
		CAMSS_X1E_PIX_ROLLBACK_RTCDM,
		CAMSS_X1E_PIX_ROLLBACK_CAPSULE_DMA,
		CAMSS_X1E_PIX_ROLLBACK_PIPELINE_PM,
	},
	.pipeline_pm_owns_resource_power = true,
	.vfe1_resource_power_reuses_vfe_get = true,
	.csid1_power_reuses_subdev_power = true,
	.csid1_ipp_reuses_hw_configure_stream = true,
	.csiphy2_power_reuses_subdev_power = true,
	.csiphy2_lanes_reuse_subdev_stream = true,
	.sensor_reuses_subdev_stream = true,
	.generic_vfe1_pix_stream_forbidden = true,
	.epoch0_order_closed = true,
	.stop_host_order_closed = true,
	.sensor_vs_csiphy_stop_order_required = false,
	.replay01_before_isp_done = true,
	.replay23_after_isp_done = true,
	.replay01_vs_csid_start_closed = true,
	.replay23_vs_mipi_sensor_start_closed = true,
	.startup_priming_interleave_closed = true,
	.callable_runner_authorized = false,
};

/*
 * E003h bounded first-QC10C runner, callable but deliberately unarmed.
 *
 * No probe, vb2, ioctl or media stream path references this recipe.  It exists
 * only so the complete first-frame hardware call graph can be compiled and
 * inspected before a later disposable runtime gate is allowed to reference it.
 *
 * The first-frame prefix is intentionally shorter than the full 0031 steady
 * lifecycle.  Same-machine Windows proves that replay2 belongs to Epoch0 #0,
 * after the complete slot1 BUS retarget, and that the first VIDEO then retires
 * slot0.  Replay3 belongs to Epoch0 #1 and must not be pre-submitted here.
 */
#define CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US	500000
#define CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US	500000

struct camss_x1e_pix_runner_request {
	const void *capsule;
	size_t capsule_size;
	const void *capsule_next;
	size_t capsule_next_size;
	const void *capsule_next_next;
	size_t capsule_next_next_size;
	struct v4l2_subdev *sensor;
	struct camss_buffer *video[6];
	struct camss_video *live_video;
	bool live_requeue;
};

struct camss_x1e_pix_runner_result {
	struct camss_buffer *video_done;
	struct camss_buffer *video_done_next;
	struct camss_buffer *video_done_third;
	struct camss_buffer *video_done_fourth;
	struct camss_buffer *video_done_fifth;
	struct camss_buffer *video_done_sixth;
	bool epoch0_seen;
	bool epoch0_next_seen;
	bool epoch0_steady_seen;
	bool epoch0_steady_next_seen;
	bool epoch0_steady_third_seen;
	bool video_seen;
	bool video_next_seen;
	bool video_third_seen;
	bool video_fourth_seen;
	bool video_fifth_seen;
	bool video_sixth_seen;
	bool slot0_reusable;
	bool slot1_reusable;
	bool slot0_reused;
	bool slot1_reused;
	bool slot0_reused_again;
	bool slot1_reused_again;
	bool slot0_reusable_again;
	bool slot1_reusable_again;
	bool slot0_reusable_third;
	bool slot1_reusable_third;
	struct camss_buffer *video_requeued;
	struct camss_buffer *video_requeued_next;
	unsigned int live_completed;
	bool live_requeue_acquired;
	bool live_requeue_next_acquired;
	bool teardown_safe;
};

static int camss_x1e_pix_runner_stream(struct v4l2_subdev *sd, bool enable)
{
	int ret;

	if (!sd)
		return -EINVAL;

	ret = v4l2_subdev_call(sd, video, s_stream, enable);
	if (ret == -ENOIOCTLCMD)
		return -EOPNOTSUPP;

	return ret;
}

static bool camss_x1e_pix_link(const struct media_pad *local,
			       const struct media_entity *remote,
			       unsigned int remote_pad)
{
	struct media_pad *pad;

	pad = media_pad_remote_pad_first(local);
	return pad && pad->entity == remote && pad->index == remote_pad;
}

static int camss_x1e_pix_runner_validate(struct camss *camss,
					 const struct camss_x1e_pix_runner_request *req)
{
	struct media_pad *sensor_pad;
	struct media_pad *csiphy_src;
	struct media_pad *csid_pix;
	struct media_pad *vfe_pix_src;
	struct csiphy_device *csiphy;
	struct csid_device *csid;
	struct vfe_device *vfe;

	if (!camss || !req || !req->capsule || !req->capsule_size || !req->sensor ||
	    !req->video[0] || !req->video[1] || req->video[0] == req->video[1] ||
	    !camss->res || camss->res->version != CAMSS_X1E80100 ||
	    camss->res->vfe_num <= 1 || camss->res->csid_num <= 1 ||
	    camss->res->csiphy_num <= 2)
		return -EINVAL;

	vfe = &camss->vfe[1];
	csid = &camss->csid[1];
	csiphy = &camss->csiphy[2];
	if (vfe->id != 1 || vfe->res->is_lite || csid->id != 1 || csiphy->id != 2 ||
	    req->sensor->entity.function != MEDIA_ENT_F_CAM_SENSOR ||
	    req->sensor->host_priv != csiphy)
		return -EINVAL;
	if (csid->phy.csiphy_id != 2 || csid->phy.phy_sel != CSID_PHY_SEL_CPHY ||
	    csid->phy.lane_cnt != 1 || !csid->phy.en_ipp)
		return -EINVAL;
	if (csid->fmt[MSM_CSID_PAD_PIX].code != MEDIA_BUS_FMT_SRGGB10_1X10 ||
	    csid->fmt[MSM_CSID_PAD_PIX].width != 3840 ||
	    csid->fmt[MSM_CSID_PAD_PIX].height != 2160)
		return -EINVAL;
	if (vfe->line[VFE_LINE_PIX].fmt[MSM_VFE_PAD_SINK].code !=
	    MEDIA_BUS_FMT_SRGGB10_1X10)
		return -EINVAL;

	/* Fail closed unless the exact front PIX media route is already enabled. */
	sensor_pad = media_pad_remote_pad_first(&csiphy->pads[MSM_CSIPHY_PAD_SINK]);
	if (!sensor_pad || sensor_pad->entity != &req->sensor->entity)
		return -ENOLINK;
	csiphy_src = &csiphy->pads[MSM_CSIPHY_PAD_SRC];
	csid_pix = &csid->pads[MSM_CSID_PAD_PIX];
	vfe_pix_src = &vfe->line[VFE_LINE_PIX].pads[MSM_VFE_PAD_SRC];
	if (!camss_x1e_pix_link(csiphy_src, &csid->subdev.entity, MSM_CSID_PAD_SINK))
		return -ENOLINK;
	if (!camss_x1e_pix_link(csid_pix, &vfe->line[VFE_LINE_PIX].subdev.entity,
				MSM_VFE_PAD_SINK))
		return -ENOLINK;
	if (!camss_x1e_pix_link(vfe_pix_src,
				&vfe->line[VFE_LINE_PIX].video_out.vdev.entity, 0))
		return -ENOLINK;

	return 0;
}

static int camss_x1e_pix_v4l2_buffer(struct camss_video *video,
				     struct camss_buffer *buffer);

static void camss_x1e_pix_v4l2_complete_live(struct camss_x1e_pix_runner_result *result,
					      struct camss_buffer *buffer,
					      unsigned int sequence)
{
	buffer->vb.vb2_buf.timestamp = ktime_get_ns();
	buffer->vb.sequence = sequence;
	vb2_buffer_done(&buffer->vb.vb2_buf, VB2_BUF_STATE_DONE);
	result->live_completed++;
}

static bool camss_x1e_pix_v4l2_pending(struct camss_video *video)
{
	struct vfe_output *output;
	struct vfe_device *vfe;
	unsigned long flags;
	bool pending;

	vfe = &video->camss->vfe[1];
	output = &vfe->line[VFE_LINE_PIX].output;
	spin_lock_irqsave(&vfe->output_lock, flags);
	pending = !list_empty(&output->pending_bufs);
	spin_unlock_irqrestore(&vfe->output_lock, flags);
	return pending;
}

static struct camss_buffer *
camss_x1e_pix_v4l2_wait_pending(struct camss_video *video, unsigned int timeout_us)
{
	struct vfe_output *output;
	struct camss_buffer *buffer;
	struct vfe_device *vfe;
	unsigned long flags;
	long left;

	left = wait_event_timeout(video->x1e_pix_buf_wait,
				  READ_ONCE(video->x1e_pix_stop_requested) ||
				  camss_x1e_pix_v4l2_pending(video),
				  usecs_to_jiffies(timeout_us));
	if (READ_ONCE(video->x1e_pix_stop_requested))
		return ERR_PTR(-ECANCELED);
	if (!left)
		return ERR_PTR(-ETIMEDOUT);

	vfe = &video->camss->vfe[1];
	output = &vfe->line[VFE_LINE_PIX].output;
	spin_lock_irqsave(&vfe->output_lock, flags);
	buffer = vfe_buf_get_pending(output);
	spin_unlock_irqrestore(&vfe->output_lock, flags);
	return buffer ? buffer : ERR_PTR(-EAGAIN);
}

#define CAMSS_X1E_FRONT_CAMNOC_RT_RATE 300000000UL

static int camss_x1e_front_camnoc_rt_set_rate(struct vfe_device *vfe)
{
	int i;

	if (!vfe || !vfe->camss || !vfe->camss->res ||
	    vfe->camss->res->version != CAMSS_X1E80100 || vfe->id != 1)
		return -EINVAL;

	for (i = 0; i < vfe->nclocks; i++) {
		struct camss_clock *clock = &vfe->clock[i];
		long rounded;

		if (strcmp(clock->name, "camnoc_rt_axi"))
			continue;

		rounded = clk_round_rate(clock->clk,
					 CAMSS_X1E_FRONT_CAMNOC_RT_RATE);
		if (rounded < 0)
			return rounded;
		if (rounded != CAMSS_X1E_FRONT_CAMNOC_RT_RATE)
			return -EINVAL;

		return clk_set_rate(clock->clk, rounded);
	}

	return -ENOENT;
}

static int camss_x1e_pix_runner_frames(struct camss *camss,
				       const struct camss_x1e_pix_runner_request *req,
				       struct camss_x1e_pix_runner_result *result,
				       unsigned int frame_limit)
{
	struct camss_x1e_pix_capsule_materialized *materialized;
	struct camss_x1e_pix_capsule_materialized *materialized_next = NULL;
	struct camss_x1e_pix_capsule_materialized *materialized_next_next = NULL;
	struct camss_x1e_pix_capsule_inputs *inputs;
	struct camss_x1e_pix_capsule_inputs *inputs_next = NULL;
	struct camss_x1e_pix_capsule_inputs *inputs_next_next = NULL;
	struct vfe680_x1e_pix_runtime *pix = NULL;
	struct media_entity *video_entity;
	struct csiphy_device *csiphy;
	struct csid_device *csid;
	struct vfe_device *vfe;
	struct camss_buffer *fifth = req ? req->video[4] : NULL;
	struct camss_buffer *sixth = req ? req->video[5] : NULL;
	bool sensor_streaming = false;
	bool csiphy_streaming = false;
	bool csid_streaming = false;
	bool csid_configured = false;
	bool pipeline_powered = false;
	bool rtcdm_started = false;
	bool bus_started = false;
	bool frame_done = false;
	bool teardown_safe = true;
	u32 epoch0_seq;
	u32 video_seq;
	int stop_ret;
	int ret;

	if (!result || (frame_limit != 1 && frame_limit != 2 &&
			frame_limit != 3 && frame_limit != 4 && frame_limit != 5 &&
			frame_limit != 6))
		return -EINVAL;
	memset(result, 0, sizeof(*result));
	/* Pre-hardware failures are safe; only a failed unwind clears this. */
	result->teardown_safe = true;

	ret = camss_x1e_pix_runner_validate(camss, req);
	if (ret)
		return ret;
	if (frame_limit >= 3 && (!req->video[2] || req->video[2] == req->video[0] ||
				 req->video[2] == req->video[1]))
		return -EINVAL;
	if (frame_limit >= 4 && (!req->video[3] || req->video[3] == req->video[0] ||
				 req->video[3] == req->video[1] ||
				 req->video[3] == req->video[2]))
		return -EINVAL;
	if (frame_limit >= 5 && (!req->capsule_next || !req->capsule_next_size))
		return -EINVAL;
	if (frame_limit == 6 && (!req->capsule_next_next || !req->capsule_next_next_size))
		return -EINVAL;
	if (frame_limit >= 5 && req->live_requeue) {
		if (!req->live_video || req->video[4] || (frame_limit == 6 && req->video[5]))
			return -EINVAL;
	} else if (frame_limit >= 5 &&
		   (!req->video[4] || req->video[4] == req->video[0] ||
		    req->video[4] == req->video[1] || req->video[4] == req->video[2] ||
		    req->video[4] == req->video[3])) {
		return -EINVAL;
	}
	if (frame_limit == 6 && !req->live_requeue &&
	    (!req->video[5] || req->video[5] == req->video[0] ||
	     req->video[5] == req->video[1] || req->video[5] == req->video[2] ||
	     req->video[5] == req->video[3] || req->video[5] == req->video[4]))
		return -EINVAL;

	vfe = &camss->vfe[1];
	csid = &camss->csid[1];
	csiphy = &camss->csiphy[2];
	video_entity = &vfe->line[VFE_LINE_PIX].video_out.vdev.entity;

	inputs = kzalloc_obj(*inputs, GFP_KERNEL);
	materialized = kzalloc_obj(*materialized, GFP_KERNEL);
	if (frame_limit >= 5) {
		inputs_next = kzalloc_obj(*inputs_next, GFP_KERNEL);
		materialized_next = kzalloc_obj(*materialized_next, GFP_KERNEL);
	}
	if (frame_limit == 6) {
		inputs_next_next = kzalloc_obj(*inputs_next_next, GFP_KERNEL);
		materialized_next_next = kzalloc_obj(*materialized_next_next, GFP_KERNEL);
	}
	if (!inputs || !materialized ||
	    (frame_limit >= 5 && (!inputs_next || !materialized_next)) ||
	    (frame_limit == 6 && (!inputs_next_next || !materialized_next_next))) {
		ret = -ENOMEM;
		goto out_free_inputs;
	}

	ret = camss_x1e_pix_capsule_parse(req->capsule, req->capsule_size, inputs);
	if (ret)
		goto out_free_inputs;
	if (frame_limit >= 4 && inputs->steady.request_id != 4) {
		ret = -EINVAL;
		goto out_free_inputs;
	}
	ret = camss_x1e_pix_capsule_materialize(camss, materialized, inputs);
	if (ret)
		goto out_free_inputs;
	if (frame_limit >= 5) {
		ret = camss_x1e_pix_capsule_parse(req->capsule_next,
					       req->capsule_next_size, inputs_next);
		if (ret || inputs_next->steady.request_id != 5) {
			if (!ret)
				ret = -EINVAL;
			goto out_materialized;
		}
		ret = camss_x1e_pix_capsule_materialize(camss, materialized_next, inputs_next);
		if (ret)
			goto out_materialized;
	}
	if (frame_limit == 6) {
		ret = camss_x1e_pix_capsule_parse(req->capsule_next_next,
						  req->capsule_next_next_size, inputs_next_next);
		if (ret || inputs_next_next->steady.request_id != 6) {
			if (!ret)
				ret = -EINVAL;
			goto out_materialized;
		}
		ret = camss_x1e_pix_capsule_materialize(camss, materialized_next_next,
							inputs_next_next);
		if (ret)
			goto out_materialized;
	}

	/* Same power owner used by the already-proven RDI video prepare path. */
	ret = v4l2_pipeline_pm_get(video_entity);
	if (ret)
		goto out_materialized;
	pipeline_powered = true;

	ret = camss_x1e_front_camnoc_rt_set_rate(vfe);
	if (ret)
		goto out_unwind;
	csid_configured = true;

	ret = vfe680_x1e_pix_runtime_alloc(vfe, req->video[0], req->video[1], &pix);
	if (ret)
		goto out_unwind;

	ret = camss_x1e_pix_rtcdm_open_start(camss);
	if (ret)
		goto out_unwind;
	rtcdm_started = true;

	/* Exact 0031 pre-CSID startup/priming interleave, now with whole replay batches. */
	ret = camss_x1e_pix_submit_startup(camss,
					   &materialized->startup_wrapper,
					   &materialized->startup, 0);
	if (ret)
		goto out_unwind;
	ret = camss_x1e_pix_submit_prime(camss, &materialized->prime, 0);
	if (ret)
		goto out_unwind;
	ret = camss_x1e_pix_submit_startup(camss,
					   &materialized->startup_wrapper,
					   &materialized->startup, 1);
	if (ret)
		goto out_unwind;
	ret = vfe680_x1e_pix_runtime_start_prefix(vfe);
	if (ret)
		goto out_unwind;
	ret = vfe680_x1e_pix_runtime_bus_prepare(vfe, pix);
	if (ret)
		goto out_unwind;
	bus_started = true;

	ret = camss_x1e_pix_submit_prime(camss, &materialized->prime, 1);
	if (ret)
		goto out_unwind;
	ret = camss_x1e_pix_submit_startup(camss,
					   &materialized->startup_wrapper,
					   &materialized->startup, 2);
	if (ret)
		goto out_unwind;
	ret = camss_x1e_pix_submit_startup(camss,
					   &materialized->startup_wrapper,
					   &materialized->startup, 3);
	if (ret)
		goto out_unwind;

	ret = csid680_x1e_front_ipp_enable(csid);
	if (ret)
		goto out_unwind;
	csid_streaming = true;
	ret = camss_x1e_pix_runner_stream(&csiphy->subdev, true);
	if (ret)
		goto out_unwind;
	csiphy_streaming = true;
	ret = camss_x1e_pix_runner_stream(req->sensor, true);
	if (ret)
		goto out_unwind;
	sensor_streaming = true;

	/* First-frame pacing: Epoch0 #0 -> BUS slot1 -> replay2/request2 -> VIDEO. */
	ret = csid680_x1e_front_ipp_poll_epoch0(csid,
						 CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);
	if (ret) {
		vfe680_x1e_pix_runtime_dump(vfe, pix, "epoch0-timeout");
		csid680_x1e_front_runtime_dump(csid, "epoch0-timeout");
		goto out_unwind;
	}
	result->epoch0_seen = true;
	epoch0_seq = csid680_x1e_front_epoch0_seq(csid);
	if (!epoch0_seq) {
		ret = -EPROTO;
		goto out_unwind;
	}
	/* Ignore the first VIDEO bit0 co-latched with Epoch0; wait for the next. */
	video_seq = csid680_x1e_front_video_seq(csid);
	ret = vfe680_x1e_pix_runtime_bus_update(vfe, pix, 1);
	if (ret)
		goto out_unwind;
	ret = camss_x1e_pix_submit_prime(camss, &materialized->prime, 2);
	if (ret)
		goto out_unwind;
	ret = csid680_x1e_front_poll_video(csid, video_seq,
					      CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
	if (ret)
		goto out_unwind;
	result->video_seen = true;
	ret = vfe680_x1e_pix_runtime_retire_video(pix, 0, &result->video_done);
	if (ret)
		goto out_unwind;
	ret = csid680_x1e_front_poll_all_done(csid, video_seq + 1,
					       CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
	if (ret)
		goto out_unwind;
	ret = vfe680_x1e_pix_runtime_retire_aux(pix, 0);
	if (ret)
		goto out_unwind;
	result->slot0_reusable = true;
	frame_done = true;
	if (req->live_requeue)
		camss_x1e_pix_v4l2_complete_live(result, req->video[0], 0);

	/*
	 * 0068 bounded refill proof. Windows refills the oldest two-slot bundle
	 * only after all five completion groups retire it. The next Epoch0 then
	 * performs one complete BUS retarget before replay3/request3. Rebind only
	 * software ownership here; the two hardware actions remain explicitly below.
	 */
	if (frame_limit >= 3) {
		ret = csid680_x1e_front_poll_next_epoch0(csid, epoch0_seq,
						       CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		result->epoch0_next_seen = true;
		epoch0_seq = csid680_x1e_front_epoch0_seq(csid);
		ret = vfe680_x1e_pix_runtime_rebind(pix, 0, req->video[2]);
		if (ret)
			goto out_unwind;
		result->slot0_reused = true;
		ret = vfe680_x1e_pix_runtime_bus_update(vfe, pix, 0);
		if (ret)
			goto out_unwind;
		ret = camss_x1e_pix_submit_prime(camss, &materialized->prime, 3);
		if (ret)
			goto out_unwind;
	}

	/*
	 * 0066 bounded second-frame proof: slot1 and replay2 were already
	 * programmed before slot0 completed. Add no hardware operation here;
	 * simply wait for the next Windows-proven CSID VIDEO generation and
	 * retire the already-queued slot1 before the same proven teardown.
	 */
	if (frame_limit >= 2) {
		u32 next_seq = csid680_x1e_front_video_seq(csid);
		u32 delta = next_seq - video_seq;

		/*
		 * Do not lose frame 2 if it lands between the first wait and this
		 * check. The original pre-replay2 generation is our fixed baseline:
		 * delta==1 means wait once more; delta==2 means it already arrived.
		 * Any larger jump is outside the bounded two-frame experiment.
		 */
		if (delta > 2) {
			ret = -EPROTO;
			goto out_unwind;
		}
		if (delta < 2) {
			ret = csid680_x1e_front_poll_video(csid, next_seq,
						      CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
			if (ret)
				goto out_unwind;
			next_seq = csid680_x1e_front_video_seq(csid);
			delta = next_seq - video_seq;
		}
		if (delta != 2) {
			ret = -EPROTO;
			goto out_unwind;
		}
		result->video_next_seen = true;
		ret = vfe680_x1e_pix_runtime_retire_video(pix, 1,
						   &result->video_done_next);
		if (ret)
			goto out_unwind;
		ret = csid680_x1e_front_poll_all_done(csid, video_seq + 2,
						       CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		ret = vfe680_x1e_pix_runtime_retire_aux(pix, 1);
		if (ret)
			goto out_unwind;
		result->slot1_reusable = true;
		if (req->live_requeue)
			camss_x1e_pix_v4l2_complete_live(result, req->video[1], 1);
	}

	/*
	 * 0069 bounded first-steady proof. Windows' first steady request follows
	 * replay3 as request4. After slot1's five groups retire, the next Epoch0
	 * performs one complete BUS refill to that reusable slot, then consumes the
	 * 0x958 five-BL steady batch. The capsule binds the captured steady sample
	 * to request_id 4; no variant-selection or production IQ rule is invented.
	 */
	if (frame_limit >= 4) {
		ret = csid680_x1e_front_poll_next_epoch0(csid, epoch0_seq,
						       CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		result->epoch0_steady_seen = true;
		epoch0_seq = csid680_x1e_front_epoch0_seq(csid);
		ret = vfe680_x1e_pix_runtime_rebind(pix, 1, req->video[3]);
		if (ret)
			goto out_unwind;
		result->slot1_reused = true;
		ret = vfe680_x1e_pix_runtime_bus_update(vfe, pix, 1);
		if (ret)
			goto out_unwind;
		ret = camss_x1e_pix_rtcdm_submit_epoch0_batch(camss,
							 &materialized->steady);
		if (ret)
			goto out_unwind;
	}

	if (frame_limit >= 3) {
		u32 third_seq = csid680_x1e_front_video_seq(csid);
		u32 delta = third_seq - video_seq;

		if (delta > 3) {
			ret = -EPROTO;
			goto out_unwind;
		}
		if (delta < 3) {
			ret = csid680_x1e_front_poll_video(csid, third_seq,
						      CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
			if (ret)
				goto out_unwind;
			third_seq = csid680_x1e_front_video_seq(csid);
			delta = third_seq - video_seq;
		}
		if (delta != 3) {
			ret = -EPROTO;
			goto out_unwind;
		}
		result->video_third_seen = true;
		ret = vfe680_x1e_pix_runtime_retire_video(pix, 0,
						   &result->video_done_third);
		if (ret)
			goto out_unwind;
		ret = csid680_x1e_front_poll_all_done(csid, video_seq + 3,
						       CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		ret = vfe680_x1e_pix_runtime_retire_aux(pix, 0);
		if (ret)
			goto out_unwind;
		result->slot0_reusable_again = true;
		if (req->live_requeue)
			camss_x1e_pix_v4l2_complete_live(result, req->video[2], 2);
	}

	if (frame_limit >= 5 && req->live_requeue) {
		fifth = camss_x1e_pix_v4l2_wait_pending(req->live_video,
						 CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (IS_ERR(fifth)) {
			ret = PTR_ERR(fifth);
			fifth = NULL;
			goto out_unwind;
		}
		ret = camss_x1e_pix_v4l2_buffer(req->live_video, fifth);
		if (ret)
			goto out_unwind;
		if (fifth != req->video[0]) {
			ret = -EPROTO;
			goto out_unwind;
		}
		result->video_requeued = fifth;
		result->live_requeue_acquired = true;
	}

	/*
	 * 0070 bounded second-steady proof. The exact Windows request5 oracle
	 * keeps request4's per-stream period_cfg but supplies request5 IQ values
	 * and DMI payloads. After frame3 fully retires slot0, refill that freed
	 * slot at the next Epoch0 and submit exactly one request5 0x958 batch.
	 */
	if (frame_limit >= 5) {
		ret = csid680_x1e_front_poll_next_epoch0(csid, epoch0_seq,
						       CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		result->epoch0_steady_next_seen = true;
		epoch0_seq = csid680_x1e_front_epoch0_seq(csid);
		ret = vfe680_x1e_pix_runtime_rebind(pix, 0, fifth);
		if (ret)
			goto out_unwind;
		result->slot0_reused_again = true;
		ret = vfe680_x1e_pix_runtime_bus_update(vfe, pix, 0);
		if (ret)
			goto out_unwind;
		ret = camss_x1e_pix_rtcdm_submit_epoch0_batch(camss,
							 &materialized_next->steady);
		if (ret)
			goto out_unwind;
	}

	if (frame_limit >= 4) {
		u32 fourth_seq = csid680_x1e_front_video_seq(csid);
		u32 delta = fourth_seq - video_seq;

		if (delta > 4) {
			ret = -EPROTO;
			goto out_unwind;
		}
		if (delta < 4) {
			ret = csid680_x1e_front_poll_video(csid, fourth_seq,
						      CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
			if (ret)
				goto out_unwind;
			fourth_seq = csid680_x1e_front_video_seq(csid);
			delta = fourth_seq - video_seq;
		}
		if (delta != 4) {
			ret = -EPROTO;
			goto out_unwind;
		}
		result->video_fourth_seen = true;
		ret = vfe680_x1e_pix_runtime_retire_video(pix, 1,
						   &result->video_done_fourth);
		if (ret)
			goto out_unwind;
		ret = csid680_x1e_front_poll_all_done(csid, video_seq + 4,
						       CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		ret = vfe680_x1e_pix_runtime_retire_aux(pix, 1);
		if (ret)
			goto out_unwind;
		result->slot1_reusable_again = true;
		if (req->live_requeue)
			camss_x1e_pix_v4l2_complete_live(result, req->video[3], 3);
	}

	if (frame_limit == 6 && req->live_requeue) {
		sixth = camss_x1e_pix_v4l2_wait_pending(req->live_video,
							CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (IS_ERR(sixth)) {
			ret = PTR_ERR(sixth);
			sixth = NULL;
			goto out_unwind;
		}
		ret = camss_x1e_pix_v4l2_buffer(req->live_video, sixth);
		if (ret)
			goto out_unwind;
		if (sixth != req->video[1]) {
			ret = -EPROTO;
			goto out_unwind;
		}
		result->video_requeued_next = sixth;
		result->live_requeue_next_acquired = true;
	}

	/*
	 * 0074 bounded third-steady proof. After frame4 retires slot1, consume
	 * exactly request6 from the monotonic IQ FIFO, retarget only reusable
	 * slot1 to the second live-requeued V4L2 buffer, and submit one 0x958
	 * steady batch. No startup, sensor, CSID, VFE or unrelated MMIO changes.
	 */
	if (frame_limit == 6) {
		ret = csid680_x1e_front_poll_next_epoch0(csid, epoch0_seq,
							 CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		result->epoch0_steady_third_seen = true;
		epoch0_seq = csid680_x1e_front_epoch0_seq(csid);
		ret = vfe680_x1e_pix_runtime_rebind(pix, 1, sixth);
		if (ret)
			goto out_unwind;
		result->slot1_reused_again = true;
		ret = vfe680_x1e_pix_runtime_bus_update(vfe, pix, 1);
		if (ret)
			goto out_unwind;
		ret = camss_x1e_pix_rtcdm_submit_epoch0_batch(camss,
							      &materialized_next_next->steady);
		if (ret)
			goto out_unwind;
	}

	if (frame_limit >= 5) {
		u32 fifth_seq = csid680_x1e_front_video_seq(csid);
		u32 delta = fifth_seq - video_seq;

		if (delta > 5) {
			ret = -EPROTO;
			goto out_unwind;
		}
		if (delta < 5) {
			ret = csid680_x1e_front_poll_video(csid, fifth_seq,
						      CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
			if (ret)
				goto out_unwind;
			fifth_seq = csid680_x1e_front_video_seq(csid);
			delta = fifth_seq - video_seq;
		}
		if (delta != 5) {
			ret = -EPROTO;
			goto out_unwind;
		}
		result->video_fifth_seen = true;
		ret = vfe680_x1e_pix_runtime_retire_video(pix, 0,
						   &result->video_done_fifth);
		if (ret)
			goto out_unwind;
		ret = csid680_x1e_front_poll_all_done(csid, video_seq + 5,
						       CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		ret = vfe680_x1e_pix_runtime_retire_aux(pix, 0);
		if (ret)
			goto out_unwind;
		result->slot0_reusable_third = true;
		if (req->live_requeue)
			camss_x1e_pix_v4l2_complete_live(result, fifth, 4);
	}

	if (frame_limit == 6) {
		u32 sixth_seq = csid680_x1e_front_video_seq(csid);
		u32 delta = sixth_seq - video_seq;

		if (delta > 6) {
			ret = -EPROTO;
			goto out_unwind;
		}
		if (delta < 6) {
			ret = csid680_x1e_front_poll_video(csid, sixth_seq,
							   CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
			if (ret)
				goto out_unwind;
			sixth_seq = csid680_x1e_front_video_seq(csid);
			delta = sixth_seq - video_seq;
		}
		if (delta != 6) {
			ret = -EPROTO;
			goto out_unwind;
		}
		result->video_sixth_seen = true;
		ret = vfe680_x1e_pix_runtime_retire_video(pix, 1,
							  &result->video_done_sixth);
		if (ret)
			goto out_unwind;
		ret = csid680_x1e_front_poll_all_done(csid, video_seq + 6,
						      CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (ret)
			goto out_unwind;
		ret = vfe680_x1e_pix_runtime_retire_aux(pix, 1);
		if (ret)
			goto out_unwind;
		result->slot1_reusable_third = true;
		if (req->live_requeue)
			camss_x1e_pix_v4l2_complete_live(result, sixth, 5);
	}

out_unwind:
	if (frame_done) {
		/* Proven normal host stop prefix: CSID1 -> BUS/IFE -> RT-CDM. */
		if (csid_streaming || csid_configured) {
			stop_ret = csid680_x1e_front_ipp_stop(csid);
			if (stop_ret) {
				teardown_safe = false;
				if (!ret)
					ret = stop_ret;
			}
		}
		if (bus_started) {
			vfe680_x1e_pix_runtime_bus_stop(vfe, pix);
			bus_started = false;
		}
		if (rtcdm_started)
			camss_x1e_pix_rtcdm_stop_close(camss);

		/* One Windows-observed valid ordering of the unordered tail. */
		if (csiphy_streaming) {
			stop_ret = camss_x1e_pix_runner_stream(&csiphy->subdev, false);
			if (stop_ret) {
				teardown_safe = false;
				if (!ret)
					ret = stop_ret;
			}
		}
		if (sensor_streaming) {
			stop_ret = camss_x1e_pix_runner_stream(req->sensor, false);
			if (stop_ret) {
				teardown_safe = false;
				if (!ret)
					ret = stop_ret;
			}
		}
	} else {
		/* Start failure rolls back the exact reverse ownership order. */
		if (sensor_streaming) {
			stop_ret = camss_x1e_pix_runner_stream(req->sensor, false);
			if (stop_ret) {
				teardown_safe = false;
				if (!ret)
					ret = stop_ret;
			}
		}
		if (csiphy_streaming) {
			stop_ret = camss_x1e_pix_runner_stream(&csiphy->subdev, false);
			if (stop_ret) {
				teardown_safe = false;
				if (!ret)
					ret = stop_ret;
			}
		}
		if (csid_streaming || csid_configured) {
			stop_ret = csid680_x1e_front_ipp_stop(csid);
			if (stop_ret) {
				teardown_safe = false;
				if (!ret)
					ret = stop_ret;
			}
		}
		if (bus_started) {
			vfe680_x1e_pix_runtime_bus_stop(vfe, pix);
			bus_started = false;
		}
		if (rtcdm_started)
			camss_x1e_pix_rtcdm_stop_close(camss);
	}

	result->teardown_safe = teardown_safe;
	if (!teardown_safe) {
		result->video_done = NULL;
		result->video_done_next = NULL;
		result->video_done_third = NULL;
		result->video_done_fourth = NULL;
		result->video_done_fifth = NULL;
		result->video_done_sixth = NULL;
		dev_err(camss->dev,
			"E003h PIX teardown failed; DMA/power intentionally pinned until reboot\n");
		return ret ? ret : -EIO;
	}

	/* Hardware producers are stopped before force-releasing pending aux slots. */
	if (pix)
		vfe680_x1e_pix_runtime_release(vfe, pix);
	if (pipeline_powered)
		v4l2_pipeline_pm_put(video_entity);

out_materialized:
	camss_x1e_pix_capsule_materialized_release(camss, materialized_next_next);
	camss_x1e_pix_capsule_materialized_release(camss, materialized_next);
	camss_x1e_pix_capsule_materialized_release(camss, materialized);
out_free_inputs:
	kfree(materialized_next_next);
	kfree(inputs_next_next);
	kfree(materialized_next);
	kfree(inputs_next);
	kfree(materialized);
	kfree(inputs);
	return ret;
}

static int camss_x1e_pix_runner_once(struct camss *camss,
				     const struct camss_x1e_pix_runner_request *req,
				     struct camss_x1e_pix_runner_result *result)
{
	return camss_x1e_pix_runner_frames(camss, req, result, 1);
}

struct camss_x1e_pix_runner_static_ops {
	int (*run_once)(struct camss *camss,
			const struct camss_x1e_pix_runner_request *req,
			struct camss_x1e_pix_runner_result *result);
};

/* Retention only: no probe, vb2, ioctl or stream path references this table. */
static const struct camss_x1e_pix_runner_static_ops
camss_x1e_pix_runner_recipe __used = {
	.run_once = camss_x1e_pix_runner_once,
};

/*
 * E003h one-shot PIX caller/preflight gate, retained and unreferenced.
 *
 * This is the final in-kernel boundary before a disposable runtime trigger is
 * allowed to exist. It does not discover, allocate, queue, or start vb2
 * buffers. A later experiment must hand it exactly two caller-owned QC10C
 * buffers that are still under userspace control, plus the separately
 * SHA-verified local oracle capsule. The latch is intentionally irreversible
 * until module reload/reboot, including on validation or runner failure.
 */
#define CAMSS_X1E_PIX_GATE_CAPSULE_BYTES	41088
#define CAMSS_X1E_PIX_GATE_QC10C_WIDTH		2560
#define CAMSS_X1E_PIX_GATE_QC10C_HEIGHT	1440
#define CAMSS_X1E_PIX_GATE_QC10C_STRIDE	3584
#define CAMSS_X1E_PIX_GATE_QC10C_BYTES		0x0076b000
#define CAMSS_X1E_PIX_GATE_VFE1_BASE		0x0ac71000
#define CAMSS_X1E_PIX_GATE_VFE1_BYTES		0x0000f000
#define CAMSS_X1E_PIX_GATE_RTCDM1_BASE		0x0ac26000
#define CAMSS_X1E_PIX_GATE_RTCDM1_BYTES	SZ_4K

static const u8 camss_x1e_pix_gate_capsule_sha256[32] = {
	0x6a, 0xed, 0x02, 0x8d, 0x1c, 0xaa, 0xf0, 0x36,
	0x6b, 0x00, 0x40, 0x38, 0xae, 0xe3, 0xe9, 0x54,
	0xca, 0x95, 0xa9, 0x5c, 0x11, 0x7e, 0x26, 0x19,
	0x55, 0x5b, 0xdd, 0x96, 0x05, 0x74, 0x6a, 0x20,
};

struct camss_x1e_pix_gate_request {
	struct camss_x1e_pix_runner_request runner;
	u8 capsule_sha256[ARRAY_SIZE(camss_x1e_pix_gate_capsule_sha256)];
};

static atomic_t camss_x1e_pix_gate_once = ATOMIC_INIT(0);

static int camss_x1e_pix_gate_buffer(struct camss_video *video,
				     struct camss_buffer *buffer)
{
	const struct v4l2_pix_format_mplane *fmt;
	struct vb2_buffer *vb;
	u64 end;

	if (!video || !buffer)
		return -EINVAL;
	fmt = &video->active_fmt.fmt.pix_mp;
	vb = &buffer->vb.vb2_buf;

	if (fmt->pixelformat != V4L2_PIX_FMT_QC10C ||
	    fmt->width != CAMSS_X1E_PIX_GATE_QC10C_WIDTH ||
	    fmt->height != CAMSS_X1E_PIX_GATE_QC10C_HEIGHT ||
	    fmt->num_planes != 1 ||
	    fmt->plane_fmt[0].bytesperline != CAMSS_X1E_PIX_GATE_QC10C_STRIDE ||
	    fmt->plane_fmt[0].sizeimage != CAMSS_X1E_PIX_GATE_QC10C_BYTES)
		return -EINVAL;
	if (vb->vb2_queue != &video->vb2_q || vb->num_planes != 1 ||
	    vb->state != VB2_BUF_STATE_DEQUEUED || vb2_plane_size(vb, 0) <
	    CAMSS_X1E_PIX_GATE_QC10C_BYTES)
		return -EBUSY;
	if (!buffer->addr[0] || !IS_ALIGNED(buffer->addr[0], PAGE_SIZE))
		return -EINVAL;
	end = (u64)buffer->addr[0] + CAMSS_X1E_PIX_GATE_QC10C_BYTES - 1;
	if (end > U32_MAX)
		return -ERANGE;

	return 0;
}

static int camss_x1e_pix_gate_resources(struct camss *camss)
{
	struct platform_device *pdev;
	struct resource *vfe1;
	struct resource *rtcdm1;

	if (!camss || !camss->dev || !camss->rtcdm1.present)
		return -ENODEV;
	pdev = to_platform_device(camss->dev);
	vfe1 = platform_get_resource_byname(pdev, IORESOURCE_MEM, "vfe1");
	rtcdm1 = platform_get_resource_byname(pdev, IORESOURCE_MEM, "rt_cdm1");
	if (!vfe1 || vfe1->start != CAMSS_X1E_PIX_GATE_VFE1_BASE ||
	    resource_size(vfe1) != CAMSS_X1E_PIX_GATE_VFE1_BYTES)
		return -ENODEV;
	if (!rtcdm1 || rtcdm1->start != CAMSS_X1E_PIX_GATE_RTCDM1_BASE ||
	    resource_size(rtcdm1) != CAMSS_X1E_PIX_GATE_RTCDM1_BYTES)
		return -ENODEV;
	if (!camss->rtcdm1.base)
		return -ENODEV;

	return 0;
}

static int camss_x1e_pix_gate_validate(struct camss *camss,
				       const struct camss_x1e_pix_gate_request *req)
{
	struct camss_video *video;
	u64 a0, a1;
	int ret;

	if (!req || req->runner.capsule_size != CAMSS_X1E_PIX_GATE_CAPSULE_BYTES ||
	    memcmp(req->capsule_sha256, camss_x1e_pix_gate_capsule_sha256,
		   sizeof(camss_x1e_pix_gate_capsule_sha256)))
		return -EINVAL;
	ret = camss_x1e_pix_runner_validate(camss, &req->runner);
	if (ret)
		return ret;
	ret = camss_x1e_pix_gate_resources(camss);
	if (ret)
		return ret;

	video = &camss->vfe[1].line[VFE_LINE_PIX].video_out;
	if (video->vb2_q.streaming || video->vb2_q.start_streaming_called ||
	    atomic_read(&video->vb2_q.owned_by_drv_count))
		return -EBUSY;
	ret = camss_x1e_pix_gate_buffer(video, req->runner.video[0]);
	if (ret)
		return ret;
	ret = camss_x1e_pix_gate_buffer(video, req->runner.video[1]);
	if (ret)
		return ret;
	if (req->runner.video[0]->vb.vb2_buf.index ==
	    req->runner.video[1]->vb.vb2_buf.index)
		return -EINVAL;

	a0 = req->runner.video[0]->addr[0];
	a1 = req->runner.video[1]->addr[0];
	if (a0 < a1 + CAMSS_X1E_PIX_GATE_QC10C_BYTES &&
	    a1 < a0 + CAMSS_X1E_PIX_GATE_QC10C_BYTES)
		return -EINVAL;

	/* The disposable front-only DT must not have a rear sensor link. */
	if (media_pad_remote_pad_first(&camss->csiphy[1].pads[MSM_CSIPHY_PAD_SINK]))
		return -EBUSY;

	return 0;
}

static int camss_x1e_pix_gate_run_once(struct camss *camss,
				       const struct camss_x1e_pix_gate_request *req,
				       struct camss_x1e_pix_runner_result *result)
{
	int ret;

	if (atomic_cmpxchg(&camss_x1e_pix_gate_once, 0, 1))
		return -EALREADY;
	ret = camss_x1e_pix_gate_validate(camss, req);
	if (ret)
		return ret;

	return camss_x1e_pix_runner_once(camss, &req->runner, result);
}

struct camss_x1e_pix_gate_static_ops {
	int (*run_once)(struct camss *camss,
			const struct camss_x1e_pix_gate_request *req,
			struct camss_x1e_pix_runner_result *result);
};

/* Retention only: no probe, vb2, ioctl, debugfs or firmware path references it. */
static const struct camss_x1e_pix_gate_static_ops
camss_x1e_pix_gate_recipe __used = {
	.run_once = camss_x1e_pix_gate_run_once,
};

/*
 * E003h disposable sysfs trigger. The attribute is created only when the module
 * is explicitly loaded with e003h_pix_runtime_arm=1 on X1E80100. It accepts
 * exactly "RUN", discovers only the two preallocated DEQUEUED buffers 0/1,
 * loads the fixed local capsule firmware, and invokes the irreversible 0034
 * gate. It never QBUFs or STREAMONs the normal vb2 path.
 */
#define CAMSS_X1E_PIX_TRIGGER_FW "sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin"
#define CAMSS_X1E_PIX_TRIGGER_FW_R5 "sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R5.bin"
#define CAMSS_X1E_PIX_TRIGGER_FW_R6 "sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R6.bin"


/*
 * E003h 0072 steady-IQ provider FIFO.
 *
 * This is deliberately a software-only ownership boundary between an upstream
 * per-request IQ producer and the already-proven steady materializer/runner.
 * Queue entries own a private copy of the existing capsule ABI so producer
 * lifetime cannot race the camera worker. The queue enforces request5+ strict
 * monotonic ordering and bounded depth. It has no MMIO, RT-CDM submission,
 * IRQ, sensor, CSID or VFE operation.
 */
#define CAMSS_X1E_PIX_IQ_QUEUE_DEPTH_MAX	8
#define CAMSS_X1E_PIX_IQ_FIRST_STEADY_REQUEST	5
#define CAMSS_X1E_PIX_IQ_WAIT_TIMEOUT_US	500000

struct camss_x1e_pix_iq_packet {
	struct list_head node;
	u64 request_id;
	size_t capsule_size;
	u8 capsule[];
};

static void camss_x1e_pix_iq_packet_release(struct camss_x1e_pix_iq_packet *packet)
{
	if (!packet)
		return;
	memzero_explicit(packet->capsule, packet->capsule_size);
	kfree(packet);
}

static void camss_x1e_pix_iq_provider_purge(struct camss_video *video)
{
	struct camss_x1e_pix_iq_packet *packet, *tmp;

	if (!video)
		return;

	mutex_lock(&video->x1e_pix_iq_lock);
	list_for_each_entry_safe(packet, tmp, &video->x1e_pix_iq_pending, node) {
		list_del(&packet->node);
		camss_x1e_pix_iq_packet_release(packet);
	}
	video->x1e_pix_iq_depth = 0;
	mutex_unlock(&video->x1e_pix_iq_lock);
	wake_up_all(&video->x1e_pix_iq_wait);
}

static int camss_x1e_pix_iq_provider_open(struct camss_video *video,
					  u64 first_request_id)
{
	if (!video || first_request_id < CAMSS_X1E_PIX_IQ_FIRST_STEADY_REQUEST)
		return -EINVAL;

	mutex_lock(&video->x1e_pix_iq_lock);
	if (!list_empty(&video->x1e_pix_iq_pending) || video->x1e_pix_iq_depth) {
		mutex_unlock(&video->x1e_pix_iq_lock);
		return -EBUSY;
	}
	video->x1e_pix_iq_last_enqueued = first_request_id - 1;
	video->x1e_pix_iq_last_dequeued = first_request_id - 1;
	video->x1e_pix_iq_closed = false;
	mutex_unlock(&video->x1e_pix_iq_lock);
	return 0;
}

static void camss_x1e_pix_iq_provider_close(struct camss_video *video)
{
	if (!video)
		return;
	mutex_lock(&video->x1e_pix_iq_lock);
	video->x1e_pix_iq_closed = true;
	mutex_unlock(&video->x1e_pix_iq_lock);
	wake_up_all(&video->x1e_pix_iq_wait);
}

static int camss_x1e_pix_iq_provider_enqueue(struct camss_video *video,
					     const void *capsule, size_t capsule_size)
{
	struct camss_x1e_pix_capsule_inputs *inputs;
	struct camss_x1e_pix_iq_packet *packet;
	u64 request_id;
	int ret;

	if (!video || !capsule || capsule_size != CAMSS_X1E_PIX_GATE_CAPSULE_BYTES)
		return -EINVAL;

	packet = kmalloc(struct_size(packet, capsule, capsule_size), GFP_KERNEL);
	inputs = kzalloc_obj(*inputs, GFP_KERNEL);
	if (!packet || !inputs) {
		ret = -ENOMEM;
		goto out_free;
	}
	INIT_LIST_HEAD(&packet->node);
	packet->capsule_size = capsule_size;
	memcpy(packet->capsule, capsule, capsule_size);

	ret = camss_x1e_pix_capsule_parse(packet->capsule, packet->capsule_size,
					   inputs);
	if (ret)
		goto out_free;
	request_id = inputs->steady.request_id;
	if (inputs->steady.subrequest ||
	    request_id < CAMSS_X1E_PIX_IQ_FIRST_STEADY_REQUEST) {
		ret = -EINVAL;
		goto out_free;
	}
	packet->request_id = request_id;

	mutex_lock(&video->x1e_pix_iq_lock);
	if (video->x1e_pix_iq_closed) {
		ret = -ESHUTDOWN;
	} else if (video->x1e_pix_iq_depth >= CAMSS_X1E_PIX_IQ_QUEUE_DEPTH_MAX) {
		ret = -ENOSPC;
	} else if (request_id != video->x1e_pix_iq_last_enqueued + 1) {
		ret = -EPROTO;
	} else {
		list_add_tail(&packet->node, &video->x1e_pix_iq_pending);
		video->x1e_pix_iq_last_enqueued = request_id;
		video->x1e_pix_iq_depth++;
		ret = 0;
	}
	mutex_unlock(&video->x1e_pix_iq_lock);
	if (!ret) {
		wake_up_all(&video->x1e_pix_iq_wait);
		kfree(inputs);
		return 0;
	}

out_free:
	kfree(inputs);
	camss_x1e_pix_iq_packet_release(packet);
	return ret;
}

static int camss_x1e_pix_iq_provider_next(struct camss_video *video,
					  u64 expected_request_id,
					  unsigned int timeout_us,
					  struct camss_x1e_pix_iq_packet **out)
{
	struct camss_x1e_pix_iq_packet *packet;
	long waited;
	int ret = 0;

	if (!video || !out || expected_request_id < CAMSS_X1E_PIX_IQ_FIRST_STEADY_REQUEST)
		return -EINVAL;
	*out = NULL;

	waited = wait_event_timeout(video->x1e_pix_iq_wait,
		READ_ONCE(video->x1e_pix_iq_depth) ||
		READ_ONCE(video->x1e_pix_iq_closed) ||
		READ_ONCE(video->x1e_pix_stop_requested),
		usecs_to_jiffies(timeout_us));
	if (!waited && !READ_ONCE(video->x1e_pix_iq_depth))
		return -ETIMEDOUT;
	if (READ_ONCE(video->x1e_pix_stop_requested))
		return -ECANCELED;

	mutex_lock(&video->x1e_pix_iq_lock);
	if (list_empty(&video->x1e_pix_iq_pending)) {
		ret = video->x1e_pix_iq_closed ? -ESHUTDOWN : -EAGAIN;
		goto out_unlock;
	}
	packet = list_first_entry(&video->x1e_pix_iq_pending,
				  struct camss_x1e_pix_iq_packet, node);
	list_del(&packet->node);
	video->x1e_pix_iq_depth--;
	if (packet->request_id != expected_request_id ||
	    packet->request_id != video->x1e_pix_iq_last_dequeued + 1) {
		ret = -EPROTO;
		camss_x1e_pix_iq_packet_release(packet);
		goto out_unlock;
	}
	video->x1e_pix_iq_last_dequeued = packet->request_id;
	*out = packet;

out_unlock:
	mutex_unlock(&video->x1e_pix_iq_lock);
	return ret;
}

static int camss_x1e_pix_iq_provider_seed_firmware(struct camss_video *video,
						    const char *name)
{
	const struct firmware *fw;
	int ret;

	if (!video || !video->camss || !name)
		return -EINVAL;
	ret = request_firmware_direct(&fw, name, video->camss->dev);
	if (ret)
		return ret;
	ret = camss_x1e_pix_iq_provider_enqueue(video, fw->data, fw->size);
	release_firmware(fw);
	return ret;
}

struct camss_x1e_pix_iq_provider_static_ops {
	int (*open)(struct camss_video *video, u64 first_request_id);
	int (*enqueue)(struct camss_video *video, const void *capsule, size_t capsule_size);
	int (*next)(struct camss_video *video, u64 expected_request_id,
		    unsigned int timeout_us, struct camss_x1e_pix_iq_packet **out);
	void (*close)(struct camss_video *video);
	void (*purge)(struct camss_video *video);
	void (*release)(struct camss_x1e_pix_iq_packet *packet);
};

static const struct camss_x1e_pix_iq_provider_static_ops
camss_x1e_pix_iq_provider_recipe __used = {
	.open = camss_x1e_pix_iq_provider_open,
	.enqueue = camss_x1e_pix_iq_provider_enqueue,
	.next = camss_x1e_pix_iq_provider_next,
	.close = camss_x1e_pix_iq_provider_close,
	.purge = camss_x1e_pix_iq_provider_purge,
	.release = camss_x1e_pix_iq_packet_release,
};

static int camss_x1e_pix_trigger_buffer(struct camss_video *video,
					unsigned int index,
					struct camss_buffer **buffer)
{
	struct vb2_v4l2_buffer *vbuf;
	struct vb2_buffer *vb;

	if (!video || !buffer || index >= video->vb2_q.max_num_buffers ||
	    !video->vb2_q.bufs || !video->vb2_q.bufs[index])
		return -EINVAL;
	vb = video->vb2_q.bufs[index];
	if (vb->vb2_queue != &video->vb2_q)
		return -EINVAL;
	vbuf = to_vb2_v4l2_buffer(vb);
	*buffer = container_of(vbuf, struct camss_buffer, vb);
	return 0;
}

static int camss_x1e_pix_trigger_sync(struct camss *camss,
				      struct camss_buffer *buffer, bool for_device)
{
	struct vb2_buffer *vb = &buffer->vb.vb2_buf;
	struct sg_table *sgt;
	struct scatterlist *sg;
	dma_addr_t next;
	u64 total = 0;
	unsigned int i;

	sgt = vb2_dma_sg_plane_desc(vb, 0);
	if (!sgt || !sgt->nents)
		return -EFAULT;
	next = buffer->addr[0];
	for_each_sg(sgt->sgl, sg, sgt->nents, i) {
		if (sg_dma_address(sg) != next || !sg_dma_len(sg))
			return -ERANGE;
		next += sg_dma_len(sg);
		total += sg_dma_len(sg);
	}
	if (total < CAMSS_X1E_PIX_GATE_QC10C_BYTES)
		return -ERANGE;

	if (for_device)
		dma_sync_sgtable_for_device(camss->dev, sgt, DMA_FROM_DEVICE);
	else
		dma_sync_sgtable_for_cpu(camss->dev, sgt, DMA_FROM_DEVICE);
	return 0;
}

static int camss_x1e_pix_v4l2_buffer(struct camss_video *video,
				     struct camss_buffer *buffer)
{
	const struct v4l2_pix_format_mplane *fmt;
	struct vb2_buffer *vb;
	u64 end;

	if (!video || !buffer)
		return -EINVAL;
	fmt = &video->active_fmt.fmt.pix_mp;
	vb = &buffer->vb.vb2_buf;
	if (fmt->pixelformat != V4L2_PIX_FMT_QC10C ||
	    fmt->width != CAMSS_X1E_PIX_GATE_QC10C_WIDTH ||
	    fmt->height != CAMSS_X1E_PIX_GATE_QC10C_HEIGHT || fmt->num_planes != 1 ||
	    fmt->plane_fmt[0].bytesperline != CAMSS_X1E_PIX_GATE_QC10C_STRIDE ||
	    fmt->plane_fmt[0].sizeimage != CAMSS_X1E_PIX_GATE_QC10C_BYTES)
		return -EINVAL;
	if (vb->vb2_queue != &video->vb2_q || vb->num_planes != 1 ||
	    vb->state != VB2_BUF_STATE_ACTIVE ||
	    vb2_plane_size(vb, 0) < CAMSS_X1E_PIX_GATE_QC10C_BYTES)
		return -EBUSY;
	if (!buffer->addr[0] || !IS_ALIGNED(buffer->addr[0], PAGE_SIZE))
		return -EINVAL;
	end = (u64)buffer->addr[0] + CAMSS_X1E_PIX_GATE_QC10C_BYTES - 1;
	if (end > U32_MAX)
		return -ERANGE;

	return 0;
}

static void camss_x1e_pix_v4l2_error_buffer(struct camss_buffer *buffer)
{
	if (buffer && buffer->vb.vb2_buf.state == VB2_BUF_STATE_ACTIVE)
		vb2_buffer_done(&buffer->vb.vb2_buf, VB2_BUF_STATE_ERROR);
}

int camss_x1e_pix_v4l2_queue_buffer(struct camss_video *video,
				     struct camss_buffer *buffer)
{
	struct vfe_output *output;
	struct vfe_device *vfe;
	unsigned long flags;

	if (!video || !buffer || !video->camss || !video->camss->res ||
	    video->camss->res->version != CAMSS_X1E80100 ||
	    video->camss->res->vfe_num <= 1 ||
	    video != &video->camss->vfe[1].line[VFE_LINE_PIX].video_out)
		return -EINVAL;

	vfe = &video->camss->vfe[1];
	output = &vfe->line[VFE_LINE_PIX].output;
	spin_lock_irqsave(&vfe->output_lock, flags);
	vfe_buf_add_pending(output, buffer);
	spin_unlock_irqrestore(&vfe->output_lock, flags);

	if (READ_ONCE(video->x1e_pix_worker_started))
		wake_up_all(&video->x1e_pix_buf_wait);
	return 0;
}

static void camss_x1e_pix_v4l2_live_work(struct work_struct *work)
{
	struct camss_video *video = container_of(work, struct camss_video, x1e_pix_work);
	struct camss_x1e_pix_runner_result result = { 0 };
	struct camss_x1e_pix_runner_request req = { 0 };
	struct camss_buffer *video0 = NULL, *video1 = NULL;
	struct camss_buffer *video2 = NULL, *video3 = NULL;
	struct camss_x1e_pix_iq_packet *iq5 = NULL, *iq6 = NULL;
	const struct firmware *fw = NULL;
	bool iq_provider_open = false;
	struct media_pad *sensor_pad;
	struct vfe_output *output;
	struct v4l2_subdev *sensor;
	struct vfe_device *vfe;
	struct camss *camss;
	unsigned long flags;
	bool runner_called = false;
	int ret;

	camss = video->camss;
	vfe = &camss->vfe[1];
	output = &vfe->line[VFE_LINE_PIX].output;

	ret = camss_x1e_pix_iq_provider_open(video,
					 CAMSS_X1E_PIX_IQ_FIRST_STEADY_REQUEST);
	if (ret)
		goto out_done;
	iq_provider_open = true;

	ret = request_firmware_direct(&fw, CAMSS_X1E_PIX_TRIGGER_FW, camss->dev);
	if (ret)
		goto out_iq;
	if (fw->size != CAMSS_X1E_PIX_GATE_CAPSULE_BYTES) {
		ret = -EINVAL;
		goto out_fw;
	}

	/* 0072 compatibility producer: feed exact request5 through the provider FIFO. */
	ret = camss_x1e_pix_iq_provider_seed_firmware(video,
						   CAMSS_X1E_PIX_TRIGGER_FW_R5);
	if (ret)
		goto out_fw;
	ret = camss_x1e_pix_iq_provider_next(video, 5,
					 CAMSS_X1E_PIX_IQ_WAIT_TIMEOUT_US, &iq5);
	if (ret)
		goto out_fw;

	/* 0074: strict FIFO continuation, exact request6 follows request5. */
	ret = camss_x1e_pix_iq_provider_seed_firmware(video,
						      CAMSS_X1E_PIX_TRIGGER_FW_R6);
	if (ret)
		goto out_iq_packet;
	ret = camss_x1e_pix_iq_provider_next(video, 6,
					     CAMSS_X1E_PIX_IQ_WAIT_TIMEOUT_US, &iq6);
	if (ret)
		goto out_iq_packet;

	spin_lock_irqsave(&vfe->output_lock, flags);
	video0 = vfe_buf_get_pending(output);
	video1 = vfe_buf_get_pending(output);
	video2 = vfe_buf_get_pending(output);
	video3 = vfe_buf_get_pending(output);
	spin_unlock_irqrestore(&vfe->output_lock, flags);
	if (!video0 || !video1 || !video2 || !video3) {
		ret = -ENOBUFS;
		goto out_error_buffers;
	}
	ret = camss_x1e_pix_v4l2_buffer(video, video0);
	if (ret)
		goto out_error_buffers;
	ret = camss_x1e_pix_v4l2_buffer(video, video1);
	if (ret)
		goto out_error_buffers;
	ret = camss_x1e_pix_v4l2_buffer(video, video2);
	if (ret)
		goto out_error_buffers;
	ret = camss_x1e_pix_v4l2_buffer(video, video3);
	if (ret)
		goto out_error_buffers;

	sensor_pad = media_pad_remote_pad_first(&camss->csiphy[2].pads[MSM_CSIPHY_PAD_SINK]);
	if (!sensor_pad || !is_media_entity_v4l2_subdev(sensor_pad->entity)) {
		ret = -ENOLINK;
		goto out_error_buffers;
	}
	sensor = media_entity_to_v4l2_subdev(sensor_pad->entity);
	req.capsule = fw->data;
	req.capsule_size = fw->size;
	req.capsule_next = iq5->capsule;
	req.capsule_next_size = iq5->capsule_size;
	req.capsule_next_next = iq6->capsule;
	req.capsule_next_next_size = iq6->capsule_size;
	req.sensor = sensor;
	req.video[0] = video0;
	req.video[1] = video1;
	req.video[2] = video2;
	req.video[3] = video3;
	req.live_video = video;
	req.live_requeue = true;
	ret = camss_x1e_pix_runner_validate(camss, &req);
	if (ret)
		goto out_error_buffers;

	runner_called = true;
	ret = camss_x1e_pix_runner_frames(camss, &req, &result, 6);
	if (!result.teardown_safe) {
		video->x1e_pix_runner_pinned = true;
		dev_err(camss->dev,
			"E003h 0071 teardown unsafe; live-requeue DMA ownership pinned until reboot\n");
		if (!ret)
			ret = -EIO;
		/* Keep provider-owned bytes pinned with the failed hardware state. */
		iq5 = NULL;
		iq6 = NULL;
		iq_provider_open = false;
		goto out_fw;
	}
	if (ret || result.video_done != video0 || result.video_done_next != video1 ||
	    result.video_done_third != video2 || result.video_done_fourth != video3 ||
	    result.video_done_fifth != video0 || result.video_done_sixth != video1 ||
	    result.video_requeued != video0 || result.video_requeued_next != video1 ||
	    result.live_completed != 6 || !result.live_requeue_acquired ||
	    !result.live_requeue_next_acquired || !result.epoch0_seen ||
	    !result.epoch0_next_seen || !result.epoch0_steady_seen ||
	    !result.epoch0_steady_next_seen || !result.epoch0_steady_third_seen ||
	    !result.video_seen || !result.video_next_seen || !result.video_third_seen ||
	    !result.video_fourth_seen || !result.video_fifth_seen || !result.video_sixth_seen ||
	    !result.slot0_reusable || !result.slot1_reusable || !result.slot0_reused ||
	    !result.slot1_reused || !result.slot0_reused_again || !result.slot1_reused_again ||
	    !result.slot0_reusable_again || !result.slot1_reusable_again ||
	    !result.slot0_reusable_third || !result.slot1_reusable_third) {
		if (!ret)
			ret = -EIO;
		goto out_error_buffers;
	}

	video->x1e_pix_runner_stopped = true;
	dev_info(camss->dev,
		 "E003h 0074 completed bounded six-frame live requeue; request5/6 used buffers0/1\n");
	ret = 0;
	goto out_iq_packet;

out_error_buffers:
	/* Hardware is stopped (or never started) before returning any held buffer. */
	if (!runner_called || result.teardown_safe) {
		if (result.live_completed < 1)
			camss_x1e_pix_v4l2_error_buffer(video0);
		if (result.live_completed < 2)
			camss_x1e_pix_v4l2_error_buffer(video1);
		if (result.live_completed < 3)
			camss_x1e_pix_v4l2_error_buffer(video2);
		if (result.live_completed < 4)
			camss_x1e_pix_v4l2_error_buffer(video3);
		if (result.live_requeue_acquired && result.live_completed < 5)
			camss_x1e_pix_v4l2_error_buffer(result.video_requeued);
		if (result.live_requeue_next_acquired && result.live_completed < 6)
			camss_x1e_pix_v4l2_error_buffer(result.video_requeued_next);
		video->x1e_pix_runner_stopped = true;
	}
out_iq_packet:
	camss_x1e_pix_iq_packet_release(iq6);
	iq6 = NULL;
	camss_x1e_pix_iq_packet_release(iq5);
	iq5 = NULL;
out_fw:
	release_firmware(fw);
out_iq:
	if (iq_provider_open) {
		camss_x1e_pix_iq_provider_close(video);
		camss_x1e_pix_iq_provider_purge(video);
	}
out_done:
	video->x1e_pix_worker_ret = ret;
	WRITE_ONCE(video->x1e_pix_live_active, false);
}

int camss_x1e_pix_v4l2_start(struct camss_video *video, unsigned int count)
{
	struct camss *camss;

	if (!camss_x1e_pix_runtime_arm || !video || !video->camss || count != 4)
		return -EPERM;
	camss = video->camss;
	if (!camss->res || camss->res->version != CAMSS_X1E80100 ||
	    camss->res->vfe_num <= 1 ||
	    video != &camss->vfe[1].line[VFE_LINE_PIX].video_out)
		return -ENODEV;
	if (atomic_cmpxchg(&camss_x1e_pix_gate_once, 0, 1))
		return -EALREADY;

	init_waitqueue_head(&video->x1e_pix_buf_wait);
	INIT_WORK(&video->x1e_pix_work, camss_x1e_pix_v4l2_live_work);
	video->x1e_pix_runner_stopped = false;
	video->x1e_pix_runner_pinned = false;
	video->x1e_pix_stop_requested = false;
	video->x1e_pix_worker_ret = -EINPROGRESS;
	WRITE_ONCE(video->x1e_pix_live_active, true);
	WRITE_ONCE(video->x1e_pix_worker_started, true);
	if (!schedule_work(&video->x1e_pix_work)) {
		WRITE_ONCE(video->x1e_pix_worker_started, false);
		WRITE_ONCE(video->x1e_pix_live_active, false);
		return -EBUSY;
	}

	return 0;
}

static ssize_t e003h_pix_rtcdm_diag_show(struct device *dev,
					 struct device_attribute *attr, char *buf)
{
	struct camss *camss = dev_get_drvdata(dev);
	struct camss_rtcdm *rt;
	u32 seq;

	if (!camss || !camss->res || camss->res->version != CAMSS_X1E80100)
		return -ENODEV;
	rt = &camss->rtcdm1;
	/* Pairs with camss_rtcdm1_diag_set() release store. */
	seq = smp_load_acquire(&rt->diag_transition_seq);

	return sysfs_emit(buf,
		"seq=%u stage=%u name=%s fifo_seq=%u base=%#x len=%#x required=%#x error=%d irq_armed=%u faulted=%u last_status=%#x/%#x/%#x/%#x last_userdata=%#x\n",
		seq, READ_ONCE(rt->diag_stage),
		camss_rtcdm1_diag_stage_name(READ_ONCE(rt->diag_stage)),
		READ_ONCE(rt->diag_fifo_seq), READ_ONCE(rt->diag_base),
		READ_ONCE(rt->diag_len_low20), READ_ONCE(rt->diag_required_irq),
		READ_ONCE(rt->diag_last_error), READ_ONCE(rt->irq_armed),
		READ_ONCE(rt->faulted), READ_ONCE(rt->last_irq_status),
		READ_ONCE(rt->last_irq_status1), READ_ONCE(rt->last_irq_status2),
		READ_ONCE(rt->last_irq_status3), READ_ONCE(rt->last_user_data));
}
static DEVICE_ATTR_RO(e003h_pix_rtcdm_diag);

static ssize_t e003h_pix_run_once_store(struct device *dev,
					struct device_attribute *attr,
					const char *buf, size_t count)
{
	struct camss_x1e_pix_runner_result result = { 0 };
	struct camss_x1e_pix_gate_request req = { 0 };
	struct camss_buffer *video0 = NULL;
	struct camss_buffer *video1 = NULL;
	const struct firmware *fw = NULL;
	struct media_pad *sensor_pad;
	struct camss_video *video;
	struct v4l2_subdev *sensor;
	struct camss *camss;
	bool synced0 = false;
	bool synced1 = false;
	int ret;

	if (!camss_x1e_pix_runtime_arm || !sysfs_streq(buf, "RUN"))
		return -EPERM;
	camss = dev_get_drvdata(dev);
	if (!camss || !camss->res || camss->res->version != CAMSS_X1E80100)
		return -ENODEV;

	ret = request_firmware_direct(&fw, CAMSS_X1E_PIX_TRIGGER_FW, dev);
	if (ret)
		return ret;
	if (fw->size != CAMSS_X1E_PIX_GATE_CAPSULE_BYTES) {
		ret = -EINVAL;
		goto out_fw;
	}

	video = &camss->vfe[1].line[VFE_LINE_PIX].video_out;
	mutex_lock(&video->lock);
	mutex_lock(&video->q_lock);
	if (vb2_get_num_buffers(&video->vb2_q) != 2) {
		ret = -EINVAL;
		goto out_unlock;
	}
	ret = camss_x1e_pix_trigger_buffer(video, 0, &video0);
	if (ret)
		goto out_unlock;
	ret = camss_x1e_pix_trigger_buffer(video, 1, &video1);
	if (ret)
		goto out_unlock;

	sensor_pad = media_pad_remote_pad_first(&camss->csiphy[2].pads[MSM_CSIPHY_PAD_SINK]);
	if (!sensor_pad || !is_media_entity_v4l2_subdev(sensor_pad->entity)) {
		ret = -ENOLINK;
		goto out_unlock;
	}
	sensor = media_entity_to_v4l2_subdev(sensor_pad->entity);

	ret = camss_x1e_pix_trigger_sync(camss, video0, true);
	if (ret)
		goto out_unlock;
	synced0 = true;
	ret = camss_x1e_pix_trigger_sync(camss, video1, true);
	if (ret)
		goto out_sync_cpu;
	synced1 = true;

	req.runner.capsule = fw->data;
	req.runner.capsule_size = fw->size;
	req.runner.sensor = sensor;
	req.runner.video[0] = video0;
	req.runner.video[1] = video1;
	memcpy(req.capsule_sha256, camss_x1e_pix_gate_capsule_sha256,
	       sizeof(req.capsule_sha256));
	ret = camss_x1e_pix_gate_run_once(camss, &req, &result);
	if (!result.teardown_safe)
		goto out_unlock;

out_sync_cpu:
	if (synced1)
		camss_x1e_pix_trigger_sync(camss, video1, false);
	if (synced0)
		camss_x1e_pix_trigger_sync(camss, video0, false);
out_unlock:
	mutex_unlock(&video->q_lock);
	mutex_unlock(&video->lock);
out_fw:
	release_firmware(fw);
	if (ret)
		return ret;
	if (result.video_done != video0 || !result.epoch0_seen || !result.video_seen ||
	    !result.teardown_safe)
		return -EIO;

	dev_info(dev, "E003h PIX one-shot completed: VIDEO slot0 returned safely\n");
	return count;
}
static DEVICE_ATTR_WO(e003h_pix_run_once);

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

	if (camss_x1e_pix_runtime_arm && camss->res->version == CAMSS_X1E80100) {
		ret = device_create_file(dev, &dev_attr_e003h_pix_rtcdm_diag);
		if (ret) {
			v4l2_async_nf_unregister(&camss->notifier);
			goto err_media_device_unregister;
		}
		ret = device_create_file(dev, &dev_attr_e003h_pix_run_once);
		if (ret) {
			device_remove_file(dev, &dev_attr_e003h_pix_rtcdm_diag);
			v4l2_async_nf_unregister(&camss->notifier);
			goto err_media_device_unregister;
		}
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

	if (camss_x1e_pix_runtime_arm && camss->res->version == CAMSS_X1E80100) {
		device_remove_file(&pdev->dev, &dev_attr_e003h_pix_run_once);
		device_remove_file(&pdev->dev, &dev_attr_e003h_pix_rtcdm_diag);
	}
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
