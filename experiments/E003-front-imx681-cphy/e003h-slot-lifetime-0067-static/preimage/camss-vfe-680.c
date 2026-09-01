// SPDX-License-Identifier: GPL-2.0
/*
 * camss-vfe-680.c
 *
 * Qualcomm MSM Camera Subsystem - VFE (Video Front End) Module v680
 *
 * Copyright (C) 2025 Linaro Ltd.
 */

#include <linux/delay.h>
#include <linux/dma-mapping.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/iopoll.h>

#include "camss.h"
#include "camss-vfe.h"

#define VFE_TOP_IRQn_STATUS(vfe, n)		((vfe_is_lite(vfe) ? 0x1c : 0x44) + (n) * 4)
#define VFE_TOP_IRQn_MASK(vfe, n)		((vfe_is_lite(vfe) ? 0x24 : 0x34) + (n) * 4)
#define VFE_TOP_IRQn_CLEAR(vfe, n)		((vfe_is_lite(vfe) ? 0x2c : 0x3c) + (n) * 4)
#define		VFE_IRQ1_SOF(vfe, n)		((vfe_is_lite(vfe) ? BIT(2) : BIT(8)) << ((n) * 2))
#define		VFE_IRQ1_EOF(vfe, n)		((vfe_is_lite(vfe) ? BIT(3) : BIT(9)) << ((n) * 2))
#define VFE_TOP_IRQ_CMD(vfe)			(vfe_is_lite(vfe) ? 0x38 : 0x30)
#define		VFE_TOP_IRQ_CMD_GLOBAL_CLEAR	BIT(0)
#define VFE_TOP_DIAG_CONFIG			(vfe_is_lite(vfe) ? 0x40 : 0x50)

#define VFE_TOP_DEBUG_11(vfe)			(vfe_is_lite(vfe) ? 0x40 : 0xcc)
#define VFE_TOP_DEBUG_12(vfe)			(vfe_is_lite(vfe) ? 0x40 : 0xd0)
#define VFE_TOP_DEBUG_13(vfe)			(vfe_is_lite(vfe) ? 0x40 : 0xd4)

#define VFE_BUS_IRQn_MASK(vfe, n)		((vfe_is_lite(vfe) ? 0x218 : 0xc18) + (n) * 4)
#define VFE_BUS_IRQn_CLEAR(vfe, n)		((vfe_is_lite(vfe) ? 0x220 : 0xc20) + (n) * 4)
#define VFE_BUS_IRQn_STATUS(vfe, n)		((vfe_is_lite(vfe) ? 0x228 : 0xc28) + (n) * 4)
#define VFE_BUS_IRQ_GLOBAL_CLEAR(vfe)		(vfe_is_lite(vfe) ? 0x230 : 0xc30)
#define VFE_BUS_WR_VIOLATION_STATUS(vfe)	(vfe_is_lite(vfe) ? 0x264 : 0xc64)
#define VFE_BUS_WR_OVERFLOW_STATUS(vfe)		(vfe_is_lite(vfe) ? 0x268 : 0xc68)
#define VFE_BUS_WR_IMAGE_VIOLATION_STATUS(vfe)	(vfe_is_lite(vfe) ? 0x270 : 0xc70)

/* Same-machine Windows VFE1 live-stable startup markers; semantics unresolved. */
#define VFE680_X1E_STARTUP_MARKER0		0x0090
#define VFE680_X1E_STARTUP_MARKER1		0x0094
#define VFE680_X1E_STARTUP_MARKER2		0x0098

/* 0059 read-only VFE680 low-TOP parity telemetry offsets. */
#define VFE680_X1E_CORE_CFG2			0x002c
#define VFE680_X1E_CORE_CFG3			0x0068
#define VFE680_X1E_STATS_THROTTLE0		0x0070
#define VFE680_X1E_STATS_THROTTLE1		0x0074
#define VFE680_X1E_STATS_THROTTLE2		0x0078
#define VFE680_X1E_CORE_CFG4			0x0080
#define VFE680_X1E_CORE_CFG5			0x0084
#define VFE680_X1E_CORE_CFG6			0x0088
#define VFE680_X1E_PERIOD_CFG			0x008c
#define VFE680_X1E_EPOCH_HEIGHT_CFG		0x009c

/* 0060 read-only VFE680 BUS progression telemetry offsets. */
#define VFE680_X1E_BUS_UBWC_STATIC_CTRL		0x0c58
/* Same-machine qccamisp computes and writes this exact SP11 VFE1 value. */
#define VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL	0x00001046
#define VFE680_X1E_BUS_PWR_ISO_CFG		0x0c5c
#define VFE680_X1E_BUS_DEBUG_TOP_CFG		0x0cd4
#define VFE680_X1E_BUS_DEBUG_TOP		0x0cd8
#define VFE680_X1E_BUS_TEST_BUS_CTRL		0x0cdc
#define VFE680_X1E_BUS_ADDR_STATUS0		0x70
#define VFE680_X1E_BUS_ADDR_STATUS1		0x74
#define VFE680_X1E_BUS_ADDR_STATUS2		0x78
#define VFE680_X1E_BUS_ADDR_STATUS3		0x7c
#define VFE680_X1E_BUS_DEBUG_STATUS0		0x84
#define VFE680_X1E_BUS_DEBUG_STATUS1		0x88

#define VFE_BUS_WRITE_CLIENT_CFG(vfe, c)	((vfe_is_lite(vfe) ? 0x400 : 0xe00) + (c) * 0x100)
#define		VFE_BUS_WRITE_CLIENT_CFG_EN	BIT(0)
#define VFE_BUS_IMAGE_ADDR(vfe, c)		((vfe_is_lite(vfe) ? 0x404 : 0xe04) + (c) * 0x100)
#define VFE_BUS_FRAME_INCR(vfe, c)		((vfe_is_lite(vfe) ? 0x408 : 0xe08) + (c) * 0x100)
#define VFE_BUS_IMAGE_CFG0(vfe, c)		((vfe_is_lite(vfe) ? 0x40c : 0xe0c) + (c) * 0x100)
#define		VFE_BUS_IMAGE_CFG0_DATA(h, s)	(((h) << 16) | ((s) >> 4))
#define WM_IMAGE_CFG_0_DEFAULT_WIDTH		(0xFFFF)

#define VFE_BUS_IMAGE_CFG1(vfe, c)		((vfe_is_lite(vfe) ? 0x410 : 0xe10) + (c) * 0x100)
#define VFE_BUS_IMAGE_CFG2(vfe, c)		((vfe_is_lite(vfe) ? 0x414 : 0xe14) + (c) * 0x100)
#define VFE_BUS_PACKER_CFG(vfe, c)		((vfe_is_lite(vfe) ? 0x418 : 0xe18) + (c) * 0x100)
#define VFE_BUS_IRQ_SUBSAMPLE_PERIOD(vfe, c)	((vfe_is_lite(vfe) ? 0x430 : 0xe30) + (c) * 0x100)
#define VFE_BUS_IRQ_SUBSAMPLE_PATTERN(vfe, c)	((vfe_is_lite(vfe) ? 0x434 : 0xe34) + (c) * 0x100)
#define VFE_BUS_FRAMEDROP_PERIOD(vfe, c)	((vfe_is_lite(vfe) ? 0x438 : 0xe38) + (c) * 0x100)
#define VFE_BUS_FRAMEDROP_PATTERN(vfe, c)	((vfe_is_lite(vfe) ? 0x43c : 0xe3c) + (c) * 0x100)
#define VFE_BUS_MMU_PREFETCH_CFG(vfe, c)	((vfe_is_lite(vfe) ? 0x460 : 0xe60) + (c) * 0x100)
#define		VFE_BUS_MMU_PREFETCH_CFG_EN	BIT(0)
#define VFE_BUS_MMU_PREFETCH_MAX_OFFSET(vfe, c)	((vfe_is_lite(vfe) ? 0x464 : 0xe64) + (c) * 0x100)
#define VFE_BUS_ADDR_STATUS0(vfe, c)		((vfe_is_lite(vfe) ? 0x470 : 0xe70) + (c) * 0x100)

/* X1E80100 VFE1 BUS client register layout used by the private E003h recipe. */
#define VFE680_X1E_BUS_CLIENT_BASE		0x0e00
#define VFE680_X1E_BUS_CLIENT_STRIDE		0x0100
#define VFE680_X1E_BUS_CFG			0x00
#define VFE680_X1E_BUS_IMAGE_ADDR		0x04
#define VFE680_X1E_BUS_FRAME_INCR		0x08
#define VFE680_X1E_BUS_IMAGE_CFG0		0x0c
#define VFE680_X1E_BUS_IMAGE_CFG1		0x10
#define VFE680_X1E_BUS_IMAGE_CFG2		0x14
#define VFE680_X1E_BUS_PACKER_CFG		0x18
#define VFE680_X1E_BUS_BW_LIMIT		0x1c
#define VFE680_X1E_BUS_IRQ_SUBSAMPLE_PERIOD	0x30
#define VFE680_X1E_BUS_IRQ_SUBSAMPLE_PATTERN	0x34
#define VFE680_X1E_BUS_FRAMEDROP_PERIOD	0x38
#define VFE680_X1E_BUS_FRAMEDROP_PATTERN	0x3c
#define VFE680_X1E_BUS_META_ADDR		0x40
#define VFE680_X1E_BUS_META_CFG		0x44
#define VFE680_X1E_BUS_MODE_CFG		0x48
#define VFE680_X1E_BUS_STATS_CTRL		0x4c
#define VFE680_X1E_BUS_CTRL_2			0x50
#define VFE680_X1E_BUS_LOSSY_THRESH0		0x54
#define VFE680_X1E_BUS_LOSSY_THRESH1		0x58
#define VFE680_X1E_BUS_LOSSY_VAR_OFFSET	0x5c

/*
 * TODO: differentiate the port id based on requested type of RDI, BHIST etc
 *
 * IFE write master IDs
 *
 * VIDEO_FULL_Y		0
 * VIDEO_FULL_C		1
 * VIDEO_DS_4:1		2
 * VIDEO_DS_16:1	3
 * DISPLAY_FULL_Y	4
 * DISPLAY_FULL_C	5
 * DISPLAY_DS_4:1	6
 * DISPLAY_DS_16:1	7
 * FD_Y			8
 * FD_C			9
 * PIXEL_RAW		10
 * STATS_BE0		11
 * STATS_BHIST0		12
 * STATS_TINTLESS_BG	13
 * STATS_AWB_BG		14
 * STATS_AWB_BFW	15
 * STATS_BAF		16
 * STATS_BHIST		17
 * STATS_RS		18
 * STATS_IHIST		19
 * SPARSE_PD		20
 * PDAF_V2.0_PD_DATA	21
 * PDAF_V2.0_SAD	22
 * LCR			23
 * RDI0			24
 * RDI1			25
 * RDI2			26
 * LTM_STATS		27
 *
 * IFE Lite write master IDs
 *
 * RDI0			0
 * RDI1			1
 * RDI2			2
 * RDI3			3
 * GAMMA		4
 * BE			5
 */

/* TODO: assign an ENUM in resources and use the provided master
 *       id directly for RDI, STATS, AWB_BG, BHIST.
 *       This macro only works because RDI is all we support right now.
 */
#define RDI_WM(n)			((vfe_is_lite(vfe) ? 0 : 24) + (n))


/*
 * E003h same-machine Windows VFE1 PIX/FULL contract, static only.
 * Public VFE680 data is used only to confirm that FULL structurally owns WM0
 * + WM1 in one compression group. Every value below comes from the two-pass
 * Windows VFE1 oracle. Dynamic Windows IOVAs/status values are absent.
 */
#define VFE680_X1E_QC10C_WIDTH          2560
#define VFE680_X1E_QC10C_HEIGHT         1440
#define VFE680_X1E_QC10C_STRIDE         3584
#define VFE680_X1E_QC10C_SIZE           0x0076b000
#define VFE680_X1E_QC10C_Y_DATA_OFF     0x00006000
#define VFE680_X1E_QC10C_C_META_OFF     0x004f2000
#define VFE680_X1E_QC10C_C_DATA_OFF     0x004f5000
#define VFE680_X1E_WINDOWS_TOP_MASK0    0x0007f051
#define VFE680_X1E_WINDOWS_BUS_MASK0    0xd0000000
#define VFE680_X1E_SP11_DAL_CORE_CFG0   0x00000024
#define VFE680_X1E_SP11_DAL_CORE_CFG1   0x00000028
#define VFE680_X1E_SP11_DAL_BUS_CGC_OVD 0x00000c08
#define VFE680_X1E_SP11_DAL_CORE_CFG0_VALUE 0x00000007
#define VFE680_X1E_SP11_DAL_CORE_CFG1_VALUE 0x00000010
#define VFE680_X1E_SP11_DAL_BUS_MASK0   0xdc000000
#define VFE680_X1E_SP11_DAL_BUS_CGC_OVD_VALUE 0x000001ff
#define VFE680_X1E_WINDOWS_VIDEO_EVENT  3

struct vfe680_x1e_windows_client_contract {
	u8 client;
	u32 cfg;
	u32 frame_incr;
	u32 image_cfg0;
	u32 image_cfg1;
	u32 image_cfg2;
	u32 packer_cfg;
	u32 bw_limit;
	u32 irq_subsample_pattern;
	u32 framedrop_pattern;
	u32 meta_cfg;
	u32 mode_cfg;
	u32 ctrl_2;
	u32 lossy_thresh0;
	u32 lossy_thresh1;
};

#define VFE680_X1E_WINDOWS_CLIENT(_id, _cfg, _incr, _cfg0, _cfg2, \
				  _packer, _bw, _meta, _mode, _ctrl2, \
				  _loss0, _loss1) \
	{ .client = (_id), .cfg = (_cfg), .frame_incr = (_incr), .image_cfg0 = (_cfg0), \
	  .image_cfg1 = 0, .image_cfg2 = (_cfg2), .packer_cfg = (_packer), .bw_limit = (_bw), \
	  .irq_subsample_pattern = 1, .framedrop_pattern = 1, \
	  .meta_cfg = (_meta), .mode_cfg = (_mode), .ctrl_2 = (_ctrl2), \
	  .lossy_thresh0 = (_loss0), .lossy_thresh1 = (_loss1) }

static const struct vfe680_x1e_windows_client_contract
vfe680_x1e_windows_full_contract[] __used = {
	VFE680_X1E_WINDOWS_CLIENT(0, 0x11, 0x004f2000, 0x05a00a00, 0x0e00,
				  0x0b, 0x0b, 0x400, 0x23, 1, 0x06210022, 0x0000040a),
	VFE680_X1E_WINDOWS_CLIENT(1, 0x11, 0x00279000, 0x02d00a00, 0x0e00,
				  0x0b, 0x0b, 0x400, 0x33, 1, 0x06210022, 0x0000040a),
};

static const struct vfe680_x1e_windows_client_contract
vfe680_x1e_windows_aux_contract[] __used = {
	VFE680_X1E_WINDOWS_CLIENT(2, 0x11, 0x00084000, 0x00b40140, 0x0b00,
				  0x0a, 0, 0, 0, 0, 0, 0),
	VFE680_X1E_WINDOWS_CLIENT(3, 0x11, 0x0000c000, 0x002d0050, 0x0300,
				  0x0a, 0, 0, 0, 0, 0, 0),
	VFE680_X1E_WINDOWS_CLIENT(11, 0x00010001, 0x000a0000, 0, 1,
				  0x0a, 0, 0, 0, 0, 0, 0),
	VFE680_X1E_WINDOWS_CLIENT(12, 0x00010001, 0x00001800, 0, 1,
				  0x0a, 0, 0, 0, 0, 0, 0),
	VFE680_X1E_WINDOWS_CLIENT(13, 0x00010001, 0x00048000, 0, 1,
				  0x0a, 0, 0, 0, 0, 0, 0),
	VFE680_X1E_WINDOWS_CLIENT(14, 0x00010001, 0x00151800, 0, 1,
				  0x0a, 0, 0, 0, 0, 0, 0),
	VFE680_X1E_WINDOWS_CLIENT(18, 0x00010001, 0x00010000, 0, 1,
				  0x08, 0, 0, 0, 0, 0, 0),
};

struct vfe680_x1e_windows_pix_contract {
	u32 width;
	u32 height;
	u32 stride;
	u32 surface_size;
	u32 y_meta_offset;
	u32 y_data_offset;
	u32 c_meta_offset;
	u32 c_data_offset;
	u32 top_mask0;
	u32 bus_mask0;
	u32 video_event;
	u8 full_wm[2];
};

static const struct vfe680_x1e_windows_pix_contract
vfe680_x1e_windows_pix_contract __used = {
	.width = VFE680_X1E_QC10C_WIDTH,
	.height = VFE680_X1E_QC10C_HEIGHT,
	.stride = VFE680_X1E_QC10C_STRIDE,
	.surface_size = VFE680_X1E_QC10C_SIZE,
	.y_meta_offset = 0,
	.y_data_offset = VFE680_X1E_QC10C_Y_DATA_OFF,
	.c_meta_offset = VFE680_X1E_QC10C_C_META_OFF,
	.c_data_offset = VFE680_X1E_QC10C_C_DATA_OFF,
	.top_mask0 = VFE680_X1E_WINDOWS_TOP_MASK0,
	.bus_mask0 = VFE680_X1E_WINDOWS_BUS_MASK0,
	.video_event = VFE680_X1E_WINDOWS_VIDEO_EVENT,
	.full_wm = { 0, 1 },
};

/*
 * E003h same-machine Windows BUS recipe, retained and unreachable.
 *
 * The 2026-08-29 KD oracle closes the MMIO lifecycle as:
 *   static client config -> enable -> initial dynamic addresses -> ISP start done
 * followed by repeated per-frame dynamic-address updates. Stop clears the same
 * resource sequence. The exact Windows IOVAs are evidence only and never appear
 * here; callers must supply Linux DMA IOVAs for every backing allocation.
 */
struct vfe680_x1e_bus_iovas {
	dma_addr_t qc10c;
	dma_addr_t ds4;
	dma_addr_t ds16;
	dma_addr_t aec_be;
	dma_addr_t rs;
	dma_addr_t bhist;
	dma_addr_t awb_bg;
	dma_addr_t tl_bg;
};

struct vfe680_x1e_bus_addresses {
	u32 image[9];
	u32 full_meta[2];
};

static const u8 vfe680_x1e_windows_bus_client_order[] = {
	0, 1, 2, 3, 11, 18, 12, 14, 13,
};

static void __iomem *vfe680_x1e_bus_reg(struct vfe_device *vfe,
					u8 client, u32 reg)
{
	return vfe->base + VFE680_X1E_BUS_CLIENT_BASE +
		client * VFE680_X1E_BUS_CLIENT_STRIDE + reg;
}

static bool vfe680_x1e_bus_target(struct vfe_device *vfe)
{
	return vfe && vfe->camss &&
		vfe->camss->res->version == CAMSS_X1E80100 && vfe->id == 1 &&
		!vfe_is_lite(vfe);
}

static const struct vfe680_x1e_windows_client_contract *
vfe680_x1e_bus_contract(u8 client)
{
	switch (client) {
	case 0:
		return &vfe680_x1e_windows_full_contract[0];
	case 1:
		return &vfe680_x1e_windows_full_contract[1];
	case 2:
		return &vfe680_x1e_windows_aux_contract[0];
	case 3:
		return &vfe680_x1e_windows_aux_contract[1];
	case 11:
		return &vfe680_x1e_windows_aux_contract[2];
	case 12:
		return &vfe680_x1e_windows_aux_contract[3];
	case 13:
		return &vfe680_x1e_windows_aux_contract[4];
	case 14:
		return &vfe680_x1e_windows_aux_contract[5];
	case 18:
		return &vfe680_x1e_windows_aux_contract[6];
	default:
		return NULL;
	}
}

static void vfe680_x1e_bus_config_client(struct vfe_device *vfe,
					 const struct vfe680_x1e_windows_client_contract *c)
{
	void __iomem *cfg = vfe680_x1e_bus_reg(vfe, c->client, 0);

	/* Windows config is session-static; bit 0 is toggled only by enable. */
	writel_relaxed(c->cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN,
		       cfg + VFE680_X1E_BUS_CFG);
	writel_relaxed(0, cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PERIOD);
	writel_relaxed(c->irq_subsample_pattern,
		       cfg + VFE680_X1E_BUS_IRQ_SUBSAMPLE_PATTERN);
	writel_relaxed(0, cfg + VFE680_X1E_BUS_FRAMEDROP_PERIOD);
	writel_relaxed(c->framedrop_pattern,
		       cfg + VFE680_X1E_BUS_FRAMEDROP_PATTERN);
	writel_relaxed(c->frame_incr, cfg + VFE680_X1E_BUS_FRAME_INCR);
	writel_relaxed(c->image_cfg0, cfg + VFE680_X1E_BUS_IMAGE_CFG0);
	writel_relaxed(c->packer_cfg, cfg + VFE680_X1E_BUS_PACKER_CFG);
	writel_relaxed(c->image_cfg2, cfg + VFE680_X1E_BUS_IMAGE_CFG2);

	/* The compression/meta fields are present only on Windows FULL Y/C. */
	if (c->meta_cfg || c->mode_cfg || c->ctrl_2 || c->lossy_thresh0 ||
	    c->lossy_thresh1) {
		writel_relaxed(c->image_cfg1, cfg + VFE680_X1E_BUS_IMAGE_CFG1);
		writel_relaxed(c->bw_limit, cfg + VFE680_X1E_BUS_BW_LIMIT);
		writel_relaxed(c->meta_cfg, cfg + VFE680_X1E_BUS_META_CFG);
		writel_relaxed(c->mode_cfg, cfg + VFE680_X1E_BUS_MODE_CFG);
		writel_relaxed(0, cfg + VFE680_X1E_BUS_STATS_CTRL);
		writel_relaxed(c->ctrl_2, cfg + VFE680_X1E_BUS_CTRL_2);
		writel_relaxed(c->lossy_thresh0,
			       cfg + VFE680_X1E_BUS_LOSSY_THRESH0);
		writel_relaxed(c->lossy_thresh1,
			       cfg + VFE680_X1E_BUS_LOSSY_THRESH1);
		writel_relaxed(0, cfg + VFE680_X1E_BUS_LOSSY_VAR_OFFSET);
	}
}

static int vfe680_x1e_bus_addr32(dma_addr_t base, u32 offset, u32 *addr)
{
	if (base > U32_MAX || offset > U32_MAX - (u32)base)
		return -ERANGE;

	*addr = (u32)base + offset;
	return 0;
}

static int vfe680_x1e_bus_build_addresses(const struct vfe680_x1e_bus_iovas *iovas,
					  struct vfe680_x1e_bus_addresses *addr)
{
	int ret;

	ret = vfe680_x1e_bus_addr32(iovas->qc10c, 0,
				    &addr->full_meta[0]);
	if (ret)
		return ret;
	ret = vfe680_x1e_bus_addr32(iovas->qc10c,
				    VFE680_X1E_QC10C_Y_DATA_OFF,
					    &addr->image[0]);
	if (ret)
		return ret;
	ret = vfe680_x1e_bus_addr32(iovas->qc10c,
				    VFE680_X1E_QC10C_C_META_OFF,
					    &addr->full_meta[1]);
	if (ret)
		return ret;
	ret = vfe680_x1e_bus_addr32(iovas->qc10c,
				    VFE680_X1E_QC10C_C_DATA_OFF,
					    &addr->image[1]);
	if (ret)
		return ret;

	ret = vfe680_x1e_bus_addr32(iovas->ds4, 0, &addr->image[2]);
	if (ret)
		return ret;
	ret = vfe680_x1e_bus_addr32(iovas->ds16, 0, &addr->image[3]);
	if (ret)
		return ret;
	ret = vfe680_x1e_bus_addr32(iovas->aec_be, 0, &addr->image[4]);
	if (ret)
		return ret;
	ret = vfe680_x1e_bus_addr32(iovas->rs, 0, &addr->image[5]);
	if (ret)
		return ret;
	ret = vfe680_x1e_bus_addr32(iovas->bhist, 0, &addr->image[6]);
	if (ret)
		return ret;
	ret = vfe680_x1e_bus_addr32(iovas->awb_bg, 0, &addr->image[7]);
	if (ret)
		return ret;
	return vfe680_x1e_bus_addr32(iovas->tl_bg, 0, &addr->image[8]);
}

static void vfe680_x1e_bus_write_addresses(struct vfe_device *vfe,
					   const struct vfe680_x1e_bus_addresses *addr)
{
	unsigned int i;

	for (i = 0; i < ARRAY_SIZE(vfe680_x1e_windows_bus_client_order); i++) {
		u8 client = vfe680_x1e_windows_bus_client_order[i];
		void __iomem *cfg = vfe680_x1e_bus_reg(vfe, client, 0);

		writel_relaxed(addr->image[i], cfg + VFE680_X1E_BUS_IMAGE_ADDR);
		if (client == 0)
			writel_relaxed(addr->full_meta[0],
				       cfg + VFE680_X1E_BUS_META_ADDR);
		else if (client == 1)
			writel_relaxed(addr->full_meta[1],
				       cfg + VFE680_X1E_BUS_META_ADDR);
	}
}

static void vfe680_x1e_bus_set_enabled(struct vfe_device *vfe, bool enable)
{
	unsigned int i;

	for (i = 0; i < ARRAY_SIZE(vfe680_x1e_windows_bus_client_order); i++) {
		u8 client = vfe680_x1e_windows_bus_client_order[i];
		void __iomem *reg = vfe680_x1e_bus_reg(vfe, client,
							      VFE680_X1E_BUS_CFG);
		u32 cfg = readl_relaxed(reg);

		if (enable)
			cfg |= VFE_BUS_WRITE_CLIENT_CFG_EN;
		else
			cfg &= ~VFE_BUS_WRITE_CLIENT_CFG_EN;
		writel_relaxed(cfg, reg);
	}
}

static int vfe680_x1e_bus_prepare(struct vfe_device *vfe,
				  const struct vfe680_x1e_bus_iovas *iovas)
{
	struct vfe680_x1e_bus_addresses addr;
	unsigned int i;
	int ret;

	if (!vfe680_x1e_bus_target(vfe))
		return -ENODEV;

	/* Validate every dynamic address before the first MMIO write. */
	ret = vfe680_x1e_bus_build_addresses(iovas, &addr);
	if (ret)
		return ret;

	/* Exact SP11 qccamisp BUS-common UBWC static programming. */
	writel_relaxed(VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL,
		       vfe->base + VFE680_X1E_BUS_UBWC_STATIC_CTRL);

	for (i = 0; i < ARRAY_SIZE(vfe680_x1e_windows_bus_client_order); i++) {
		const struct vfe680_x1e_windows_client_contract *c;

		c = vfe680_x1e_bus_contract(vfe680_x1e_windows_bus_client_order[i]);
		if (!c)
			return -EINVAL;
		vfe680_x1e_bus_config_client(vfe, c);
	}

	/* Exact Windows lifecycle: all resources enabled before initial IOVAs. */
	vfe680_x1e_bus_set_enabled(vfe, true);
	vfe680_x1e_bus_write_addresses(vfe, &addr);

	return 0;
}

static int vfe680_x1e_bus_update(struct vfe_device *vfe,
				 const struct vfe680_x1e_bus_iovas *iovas)
{
	struct vfe680_x1e_bus_addresses addr;
	int ret;

	if (!vfe680_x1e_bus_target(vfe))
		return -ENODEV;

	ret = vfe680_x1e_bus_build_addresses(iovas, &addr);
	if (ret)
		return ret;

	vfe680_x1e_bus_write_addresses(vfe, &addr);
	return 0;
}

static void vfe680_x1e_bus_stop(struct vfe_device *vfe)
{
	if (!vfe680_x1e_bus_target(vfe))
		return;

	vfe680_x1e_bus_set_enabled(vfe, false);
}

struct vfe680_x1e_bus_static_ops {
	int (*prepare)(struct vfe_device *vfe,
		       const struct vfe680_x1e_bus_iovas *iovas);
	int (*update)(struct vfe_device *vfe,
		      const struct vfe680_x1e_bus_iovas *iovas);
	void (*stop)(struct vfe_device *vfe);
};

/* Private retention only: there is intentionally no runtime reference. */
static const struct vfe680_x1e_bus_static_ops
vfe680_x1e_windows_bus_recipe __used = {
	.prepare = vfe680_x1e_bus_prepare,
	.update = vfe680_x1e_bus_update,
	.stop = vfe680_x1e_bus_stop,
};


/*
 * E003h raw VFE1 PIX event polling, retained and unreachable.
 *
 * Same-machine Windows proves only two raw event identities needed by the
 * bounded first PIX experiment: Epoch0 is BUS status1 bit 21 and VIDEO is TOP
 * status1 bit 0. The KMD IRQ reader clears TOP/BUS status0 and status1 through
 * their matching clear registers, then issues each global clear. No other raw
 * event bit or IRQ mask is inferred here. Timeout remains a caller-owned bound.
 */
#define VFE680_X1E_RAW_EPOCH0	BIT(21)
#define VFE680_X1E_RAW_VIDEO	BIT(0)

struct vfe680_x1e_irq_snapshot {
	u32 top0;
	u32 top1;
	u32 bus0;
	u32 bus1;
};

static void vfe680_x1e_irq_snapshot(struct vfe_device *vfe,
				    struct vfe680_x1e_irq_snapshot *s)
{
	s->top0 = readl_relaxed(vfe->base + VFE_TOP_IRQn_STATUS(vfe, 0));
	s->top1 = readl_relaxed(vfe->base + VFE_TOP_IRQn_STATUS(vfe, 1));
	s->bus0 = readl_relaxed(vfe->base + VFE_BUS_IRQn_STATUS(vfe, 0));
	s->bus1 = readl_relaxed(vfe->base + VFE_BUS_IRQn_STATUS(vfe, 1));
}

static void vfe680_x1e_irq_clear_snapshot(struct vfe_device *vfe,
					 const struct vfe680_x1e_irq_snapshot *s)
{
	/* Exact Windows clear order from qccamisp8380 RVA 0x1dc20. */
	writel_relaxed(s->top0, vfe->base + VFE_TOP_IRQn_CLEAR(vfe, 0));
	writel_relaxed(s->top1, vfe->base + VFE_TOP_IRQn_CLEAR(vfe, 1));
	writel_relaxed(VFE_TOP_IRQ_CMD_GLOBAL_CLEAR,
		       vfe->base + VFE_TOP_IRQ_CMD(vfe));
	writel_relaxed(s->bus0, vfe->base + VFE_BUS_IRQn_CLEAR(vfe, 0));
	writel_relaxed(s->bus1, vfe->base + VFE_BUS_IRQn_CLEAR(vfe, 1));
	writel_relaxed(1, vfe->base + VFE_BUS_IRQ_GLOBAL_CLEAR(vfe));
}

static int vfe680_x1e_poll_raw_status1(struct vfe_device *vfe, bool bus,
				       u32 bit, unsigned long timeout_us,
				       struct vfe680_x1e_irq_snapshot *snapshot)
{
	void __iomem *reg;
	u32 status;
	int ret;

	if (!vfe680_x1e_bus_target(vfe) || !snapshot || !timeout_us)
		return -EINVAL;

	reg = vfe->base + (bus ? VFE_BUS_IRQn_STATUS(vfe, 1) :
				    VFE_TOP_IRQn_STATUS(vfe, 1));
	ret = readl_relaxed_poll_timeout(reg, status, status & bit, 10, timeout_us);
	if (ret)
		return ret;

	vfe680_x1e_irq_snapshot(vfe, snapshot);
	if (!((bus ? snapshot->bus1 : snapshot->top1) & bit))
		return -EIO;

	vfe680_x1e_irq_clear_snapshot(vfe, snapshot);
	return 0;
}

static int vfe680_x1e_poll_epoch0(struct vfe_device *vfe,
				  unsigned long timeout_us,
				  struct vfe680_x1e_irq_snapshot *snapshot)
{
	return vfe680_x1e_poll_raw_status1(vfe, true, VFE680_X1E_RAW_EPOCH0,
					    timeout_us, snapshot);
}

static int vfe680_x1e_poll_video(struct vfe_device *vfe,
				 unsigned long timeout_us,
				 struct vfe680_x1e_irq_snapshot *snapshot)
{
	return vfe680_x1e_poll_raw_status1(vfe, false, VFE680_X1E_RAW_VIDEO,
					    timeout_us, snapshot);
}

struct vfe680_x1e_raw_irq_static_ops {
	int (*epoch0)(struct vfe_device *vfe, unsigned long timeout_us,
		      struct vfe680_x1e_irq_snapshot *snapshot);
	int (*video)(struct vfe_device *vfe, unsigned long timeout_us,
		     struct vfe680_x1e_irq_snapshot *snapshot);
};

/* Private retention only: no ISR, VFE ops or stream path references it. */
static const struct vfe680_x1e_raw_irq_static_ops
vfe680_x1e_raw_irq_recipe __used = {
	.epoch0 = vfe680_x1e_poll_epoch0,
	.video = vfe680_x1e_poll_video,
};

/*
 * E003h PIX frame-bundle ownership, retained and unreachable.
 *
 * Five same-machine Windows cycles observed VIDEO -> AEC_BE_BHIST ->
 * TINTLESS_BG -> AWB_BG -> RS, but qccamisp8380+0x26460 proves those are
 * independent group FIFOs, not a required cross-group sequence. Each frame is
 * therefore queued into all five groups. A completion retires only that
 * group's oldest frame. VIDEO owns FULL Y/C plus DS4/DS16 and may return the
 * user QC10C buffer; the auxiliary slot remains busy until every group retires.
 */
#define VFE680_X1E_PIX_SLOT_COUNT	CAMSS_INIT_BUF_COUNT
#define VFE680_X1E_PIX_GROUP_COUNT	5
#define VFE680_X1E_AUX_DS4_SIZE		0x00084000
#define VFE680_X1E_AUX_DS16_SIZE	0x0000c000
#define VFE680_X1E_AUX_AEC_BE_SIZE	0x000a0000
#define VFE680_X1E_AUX_BHIST_SIZE	0x00001800
#define VFE680_X1E_AUX_TL_BG_SIZE	0x00048000
#define VFE680_X1E_AUX_AWB_BG_SIZE	0x00151800
#define VFE680_X1E_AUX_RS_SIZE		0x00010000

#define VFE680_X1E_DONE_VIDEO		BIT(0)
#define VFE680_X1E_DONE_AEC_BE_BHIST	BIT(1)
#define VFE680_X1E_DONE_TINTLESS_BG	BIT(2)
#define VFE680_X1E_DONE_AWB_BG		BIT(3)
#define VFE680_X1E_DONE_RS		BIT(4)
#define VFE680_X1E_DONE_ALL		GENMASK(4, 0)

enum vfe680_x1e_aux_id {
	VFE680_X1E_AUX_DS4,
	VFE680_X1E_AUX_DS16,
	VFE680_X1E_AUX_AEC_BE,
	VFE680_X1E_AUX_BHIST,
	VFE680_X1E_AUX_TL_BG,
	VFE680_X1E_AUX_AWB_BG,
	VFE680_X1E_AUX_RS,
	VFE680_X1E_AUX_NUM,
};

enum vfe680_x1e_completion_group {
	VFE680_X1E_GROUP_VIDEO,
	VFE680_X1E_GROUP_AEC_BE_BHIST,
	VFE680_X1E_GROUP_TINTLESS_BG,
	VFE680_X1E_GROUP_AWB_BG,
	VFE680_X1E_GROUP_RS,
};

static const size_t vfe680_x1e_aux_sizes[VFE680_X1E_AUX_NUM] = {
	[VFE680_X1E_AUX_DS4] = VFE680_X1E_AUX_DS4_SIZE,
	[VFE680_X1E_AUX_DS16] = VFE680_X1E_AUX_DS16_SIZE,
	[VFE680_X1E_AUX_AEC_BE] = VFE680_X1E_AUX_AEC_BE_SIZE,
	[VFE680_X1E_AUX_BHIST] = VFE680_X1E_AUX_BHIST_SIZE,
	[VFE680_X1E_AUX_TL_BG] = VFE680_X1E_AUX_TL_BG_SIZE,
	[VFE680_X1E_AUX_AWB_BG] = VFE680_X1E_AUX_AWB_BG_SIZE,
	[VFE680_X1E_AUX_RS] = VFE680_X1E_AUX_RS_SIZE,
};

struct vfe680_x1e_aux_buffer {
	void *cpu;
	dma_addr_t dma;
	size_t size;
};

struct vfe680_x1e_pix_slot {
	struct camss_buffer *video;
	struct vfe680_x1e_aux_buffer aux[VFE680_X1E_AUX_NUM];
	u8 pending_mask;
	bool in_use;
};

struct vfe680_x1e_group_fifo {
	u8 slot[VFE680_X1E_PIX_SLOT_COUNT];
	u8 head;
	u8 tail;
	u8 count;
};

struct vfe680_x1e_pix_ownership {
	struct vfe680_x1e_pix_slot slot[VFE680_X1E_PIX_SLOT_COUNT];
	struct vfe680_x1e_group_fifo group[VFE680_X1E_PIX_GROUP_COUNT];
	bool allocated;
};

static bool vfe680_x1e_dma_span_32bit(dma_addr_t dma, size_t size)
{
	if (!size || dma > U32_MAX)
		return false;

	return size - 1 <= U32_MAX - (u32)dma;
}

static int vfe680_x1e_group_from_event(u32 event_id)
{
	switch (event_id) {
	case 0x03:
		return VFE680_X1E_GROUP_VIDEO;
	case 0x0d:
		return VFE680_X1E_GROUP_AEC_BE_BHIST;
	case 0x0e:
		return VFE680_X1E_GROUP_TINTLESS_BG;
	case 0x10:
		return VFE680_X1E_GROUP_AWB_BG;
	case 0x12:
		return VFE680_X1E_GROUP_RS;
	default:
		return -EINVAL;
	}
}

static bool vfe680_x1e_group_fifo_full(const struct vfe680_x1e_group_fifo *fifo)
{
	return fifo->count >= VFE680_X1E_PIX_SLOT_COUNT;
}

static void vfe680_x1e_group_fifo_push(struct vfe680_x1e_group_fifo *fifo,
				       unsigned int index)
{
	fifo->slot[fifo->tail] = index;
	fifo->tail = (fifo->tail + 1) % VFE680_X1E_PIX_SLOT_COUNT;
	fifo->count++;
}

static int vfe680_x1e_group_fifo_peek(const struct vfe680_x1e_group_fifo *fifo)
{
	if (!fifo->count)
		return -ENOENT;

	return fifo->slot[fifo->head];
}

static void vfe680_x1e_group_fifo_pop(struct vfe680_x1e_group_fifo *fifo)
{
	fifo->head = (fifo->head + 1) % VFE680_X1E_PIX_SLOT_COUNT;
	fifo->count--;
}

static int vfe680_x1e_aux_alloc(struct device *dev,
				struct vfe680_x1e_aux_buffer *buf, size_t size)
{
	buf->cpu = dma_alloc_coherent(dev, size, &buf->dma, GFP_KERNEL);
	if (!buf->cpu)
		return -ENOMEM;

	if (!vfe680_x1e_dma_span_32bit(buf->dma, size)) {
		dma_free_coherent(dev, size, buf->cpu, buf->dma);
		memset(buf, 0, sizeof(*buf));
		return -ERANGE;
	}

	buf->size = size;
	memset(buf->cpu, 0, size);
	return 0;
}

static void vfe680_x1e_aux_free(struct device *dev,
				struct vfe680_x1e_aux_buffer *buf)
{
	if (!buf->cpu)
		return;

	memset(buf->cpu, 0, buf->size);
	dma_free_coherent(dev, buf->size, buf->cpu, buf->dma);
	memset(buf, 0, sizeof(*buf));
}

static void vfe680_x1e_pix_ownership_release(struct vfe_device *vfe,
					     struct vfe680_x1e_pix_ownership *own)
{
	unsigned int slot, aux;

	for (slot = 0; slot < VFE680_X1E_PIX_SLOT_COUNT; slot++)
		for (aux = 0; aux < VFE680_X1E_AUX_NUM; aux++)
			vfe680_x1e_aux_free(vfe->camss->dev, &own->slot[slot].aux[aux]);

	memset(own, 0, sizeof(*own));
}

static int vfe680_x1e_pix_ownership_alloc(struct vfe_device *vfe,
					  struct vfe680_x1e_pix_ownership *own)
{
	unsigned int slot, aux;
	int ret;

	if (!vfe680_x1e_bus_target(vfe) || !own)
		return -EINVAL;
	if (own->allocated)
		return -EBUSY;

	for (slot = 0; slot < VFE680_X1E_PIX_SLOT_COUNT; slot++) {
		for (aux = 0; aux < VFE680_X1E_AUX_NUM; aux++) {
			ret = vfe680_x1e_aux_alloc(vfe->camss->dev,
						   &own->slot[slot].aux[aux],
						    vfe680_x1e_aux_sizes[aux]);
			if (ret) {
				vfe680_x1e_pix_ownership_release(vfe, own);
				return ret;
			}
		}
	}

	own->allocated = true;
	return 0;
}

static int vfe680_x1e_pix_ownership_free(struct vfe_device *vfe,
					 struct vfe680_x1e_pix_ownership *own)
{
	unsigned int slot, group;

	if (!vfe680_x1e_bus_target(vfe) || !own || !own->allocated)
		return -EINVAL;

	for (slot = 0; slot < VFE680_X1E_PIX_SLOT_COUNT; slot++)
		if (own->slot[slot].in_use)
			return -EBUSY;
	for (group = 0; group < VFE680_X1E_PIX_GROUP_COUNT; group++)
		if (own->group[group].count)
			return -EBUSY;

	vfe680_x1e_pix_ownership_release(vfe, own);
	return 0;
}

static int vfe680_x1e_pix_ownership_begin(struct vfe680_x1e_pix_ownership *own,
					  unsigned int index,
					    struct camss_buffer *video,
					    struct vfe680_x1e_bus_iovas *iovas)
{
	struct vfe680_x1e_pix_slot *slot;
	unsigned int group;

	if (!own || !own->allocated || index >= VFE680_X1E_PIX_SLOT_COUNT ||
	    !video || !iovas)
		return -EINVAL;
	if (vb2_plane_size(&video->vb.vb2_buf, 0) < VFE680_X1E_QC10C_SIZE)
		return -EINVAL;
	if (!vfe680_x1e_dma_span_32bit(video->addr[0], VFE680_X1E_QC10C_SIZE))
		return -ERANGE;

	slot = &own->slot[index];
	if (slot->in_use)
		return -EBUSY;
	for (group = 0; group < VFE680_X1E_PIX_GROUP_COUNT; group++)
		if (vfe680_x1e_group_fifo_full(&own->group[group]))
			return -EBUSY;

	slot->video = video;
	slot->pending_mask = VFE680_X1E_DONE_ALL;
	slot->in_use = true;
	for (group = 0; group < VFE680_X1E_PIX_GROUP_COUNT; group++)
		vfe680_x1e_group_fifo_push(&own->group[group], index);

	memset(iovas, 0, sizeof(*iovas));
	iovas->qc10c = video->addr[0];
	iovas->ds4 = slot->aux[VFE680_X1E_AUX_DS4].dma;
	iovas->ds16 = slot->aux[VFE680_X1E_AUX_DS16].dma;
	iovas->aec_be = slot->aux[VFE680_X1E_AUX_AEC_BE].dma;
	iovas->bhist = slot->aux[VFE680_X1E_AUX_BHIST].dma;
	iovas->tl_bg = slot->aux[VFE680_X1E_AUX_TL_BG].dma;
	iovas->awb_bg = slot->aux[VFE680_X1E_AUX_AWB_BG].dma;
	iovas->rs = slot->aux[VFE680_X1E_AUX_RS].dma;

	return 0;
}

static int vfe680_x1e_pix_ownership_complete(struct vfe680_x1e_pix_ownership *own,
					     u32 event_id, unsigned int *index,
					       struct camss_buffer **video_done,
					       bool *slot_reusable)
{
	struct vfe680_x1e_group_fifo *fifo;
	struct vfe680_x1e_pix_slot *slot;
	int group, queued_index;
	u8 bit;

	if (!own || !own->allocated || !index || !video_done || !slot_reusable)
		return -EINVAL;

	*video_done = NULL;
	*slot_reusable = false;
	group = vfe680_x1e_group_from_event(event_id);
	if (group < 0)
		return group;

	fifo = &own->group[group];
	queued_index = vfe680_x1e_group_fifo_peek(fifo);
	if (queued_index < 0)
		return queued_index;
	if (queued_index >= VFE680_X1E_PIX_SLOT_COUNT)
		return -EPROTO;

	slot = &own->slot[queued_index];
	bit = BIT(group);
	if (!slot->in_use || !(slot->pending_mask & bit))
		return -EPROTO;

	vfe680_x1e_group_fifo_pop(fifo);
	slot->pending_mask &= ~bit;
	*index = queued_index;
	if (group == VFE680_X1E_GROUP_VIDEO) {
		*video_done = slot->video;
		slot->video = NULL;
	}

	if (!slot->pending_mask) {
		slot->in_use = false;
		*slot_reusable = true;
	}

	return 0;
}

struct vfe680_x1e_pix_ownership_ops {
	int (*alloc)(struct vfe_device *vfe, struct vfe680_x1e_pix_ownership *own);
	int (*free)(struct vfe_device *vfe, struct vfe680_x1e_pix_ownership *own);
	int (*begin)(struct vfe680_x1e_pix_ownership *own, unsigned int index,
		     struct camss_buffer *video, struct vfe680_x1e_bus_iovas *iovas);
	int (*complete)(struct vfe680_x1e_pix_ownership *own, u32 event_id,
			unsigned int *index, struct camss_buffer **video_done,
			bool *slot_reusable);
};

/* Private retention only: no ISR, VFE ops or stream path references this table. */
static const struct vfe680_x1e_pix_ownership_ops
vfe680_x1e_pix_ownership_recipe __used = {
	.alloc = vfe680_x1e_pix_ownership_alloc,
	.free = vfe680_x1e_pix_ownership_free,
	.begin = vfe680_x1e_pix_ownership_begin,
	.complete = vfe680_x1e_pix_ownership_complete,
};

/*
 * E003h module-internal VFE680 PIX runtime bridge.
 *
 * This object deliberately hides the private BUS/IRQ/ownership structures from
 * camss.c.  It is used only by the retained, unreferenced bounded PIX runner.
 * Allocation and begin are DMA/state-only.  BUS prepare/update/stop and raw
 * polling are the already-inspected Windows-parity helpers above.
 */
struct vfe680_x1e_pix_runtime {
	struct vfe680_x1e_pix_ownership ownership;
	struct vfe680_x1e_bus_iovas iovas[VFE680_X1E_PIX_SLOT_COUNT];
	bool bus_started;
};

int vfe680_x1e_pix_runtime_alloc(struct vfe_device *vfe,
				 struct camss_buffer *video0,
				 struct camss_buffer *video1,
				 struct vfe680_x1e_pix_runtime **runtime)
{
	struct vfe680_x1e_pix_runtime *rt;
	int ret;

	if (!vfe680_x1e_bus_target(vfe) || !video0 || !video1 || !runtime)
		return -EINVAL;
	*runtime = NULL;

	rt = kzalloc_obj(*rt, GFP_KERNEL);
	if (!rt)
		return -ENOMEM;

	ret = vfe680_x1e_pix_ownership_alloc(vfe, &rt->ownership);
	if (ret)
		goto err_free;
	ret = vfe680_x1e_pix_ownership_begin(&rt->ownership, 0, video0,
					     &rt->iovas[0]);
	if (ret)
		goto err_release;
	ret = vfe680_x1e_pix_ownership_begin(&rt->ownership, 1, video1,
					     &rt->iovas[1]);
	if (ret)
		goto err_release;

	*runtime = rt;
	return 0;

err_release:
	vfe680_x1e_pix_ownership_release(vfe, &rt->ownership);
err_free:
	kfree(rt);
	return ret;
}

void vfe680_x1e_pix_runtime_release(struct vfe_device *vfe,
				    struct vfe680_x1e_pix_runtime *runtime)
{
	if (!vfe680_x1e_bus_target(vfe) || !runtime)
		return;

	/* Caller must stop BUS/hardware before freeing in-flight auxiliary DMA. */
	if (WARN_ON(runtime->bus_started))
		return;
	vfe680_x1e_pix_ownership_release(vfe, &runtime->ownership);
	kfree(runtime);
}

int vfe680_x1e_pix_runtime_start_prefix(struct vfe_device *vfe)
{
	if (!vfe680_x1e_bus_target(vfe))
		return -ENODEV;

	/*
	 * Retain the separately proven Windows-live IRQ visibility masks. They are
	 * not owned by the active SP11 IFE1 DAL callback, whose generation selector
	 * is now proven to be zero.
	 */
	writel_relaxed(VFE680_X1E_WINDOWS_TOP_MASK0,
		       vfe->base + VFE_TOP_IRQn_MASK(vfe, 0));
	writel_relaxed(0, vfe->base + VFE_TOP_IRQn_MASK(vfe, 1));
	writel_relaxed(0, vfe->base + VFE_BUS_IRQn_MASK(vfe, 1));

	/* Retain the proven active SP11 IFE1 TOP/BUS mask writes. */
	writel_relaxed(VFE680_X1E_SP11_DAL_CORE_CFG0_VALUE,
		       vfe->base + VFE680_X1E_SP11_DAL_CORE_CFG0);
	writel_relaxed(VFE680_X1E_SP11_DAL_CORE_CFG1_VALUE,
		       vfe->base + VFE680_X1E_SP11_DAL_CORE_CFG1);
	writel_relaxed(VFE680_X1E_SP11_DAL_BUS_MASK0,
		       vfe->base + VFE_BUS_IRQn_MASK(vfe, 0));

	return 0;
}

int vfe680_x1e_pix_runtime_bus_prepare(struct vfe_device *vfe,
				       struct vfe680_x1e_pix_runtime *runtime)
{
	int ret;

	if (!runtime || runtime->bus_started)
		return -EINVAL;
	ret = vfe680_x1e_bus_prepare(vfe, &runtime->iovas[0]);
	if (!ret)
		runtime->bus_started = true;
	return ret;
}

int vfe680_x1e_pix_runtime_bus_update(struct vfe_device *vfe,
				      struct vfe680_x1e_pix_runtime *runtime,
				      unsigned int slot)
{
	if (!runtime || !runtime->bus_started || slot >= VFE680_X1E_PIX_SLOT_COUNT)
		return -EINVAL;
	return vfe680_x1e_bus_update(vfe, &runtime->iovas[slot]);
}

void vfe680_x1e_pix_runtime_bus_stop(struct vfe_device *vfe,
				     struct vfe680_x1e_pix_runtime *runtime)
{
	if (!runtime || !runtime->bus_started)
		return;
	vfe680_x1e_bus_stop(vfe);
	runtime->bus_started = false;
}

void vfe680_x1e_pix_runtime_dump(struct vfe_device *vfe,
				 struct vfe680_x1e_pix_runtime *runtime,
				 const char *reason)
{
	struct vfe680_x1e_bus_addresses expected;
	void __iomem *c0, *c1;
	const char *why = reason ? reason : "snapshot";
	unsigned int i;
	int ret;

	if (!vfe680_x1e_bus_target(vfe) || !runtime || !runtime->bus_started)
		return;

	ret = vfe680_x1e_bus_build_addresses(&runtime->iovas[0], &expected);
	if (ret) {
		dev_info(vfe->camss->dev,
			 "E003h VFE1 %s expected-address build failed: %d\n",
			 why, ret);
		return;
	}

	c0 = vfe680_x1e_bus_reg(vfe, 0, 0);
	c1 = vfe680_x1e_bus_reg(vfe, 1, 0);
	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s top=%08x/%08x mask=%08x/%08x bus=%08x/%08x bmask=%08x/%08x\n",
		 why, readl_relaxed(vfe->base + VFE_TOP_IRQn_STATUS(vfe, 0)),
		 readl_relaxed(vfe->base + VFE_TOP_IRQn_STATUS(vfe, 1)),
		 readl_relaxed(vfe->base + VFE_TOP_IRQn_MASK(vfe, 0)),
		 readl_relaxed(vfe->base + VFE_TOP_IRQn_MASK(vfe, 1)),
		 readl_relaxed(vfe->base + VFE_BUS_IRQn_STATUS(vfe, 0)),
		 readl_relaxed(vfe->base + VFE_BUS_IRQn_STATUS(vfe, 1)),
		 readl_relaxed(vfe->base + VFE_BUS_IRQn_MASK(vfe, 0)),
		 readl_relaxed(vfe->base + VFE_BUS_IRQn_MASK(vfe, 1)));
	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s viol=%08x/%08x/%08x marker=%08x/%08x/%08x\n",
		 why, readl_relaxed(vfe->base + VFE_BUS_WR_VIOLATION_STATUS(vfe)),
		 readl_relaxed(vfe->base + VFE_BUS_WR_OVERFLOW_STATUS(vfe)),
		 readl_relaxed(vfe->base + VFE_BUS_WR_IMAGE_VIOLATION_STATUS(vfe)),
		 readl_relaxed(vfe->base + VFE680_X1E_STARTUP_MARKER0),
		 readl_relaxed(vfe->base + VFE680_X1E_STARTUP_MARKER1),
		 readl_relaxed(vfe->base + VFE680_X1E_STARTUP_MARKER2));
	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s buscommon cgc=%08x ubwc=%08x piso=%08x dbgcfg=%08x dbg=%08x test=%08x\n",
		 why, readl_relaxed(vfe->base + VFE680_X1E_SP11_DAL_BUS_CGC_OVD),
		 readl_relaxed(vfe->base + VFE680_X1E_BUS_UBWC_STATIC_CTRL),
		 readl_relaxed(vfe->base + VFE680_X1E_BUS_PWR_ISO_CFG),
		 readl_relaxed(vfe->base + VFE680_X1E_BUS_DEBUG_TOP_CFG),
		 readl_relaxed(vfe->base + VFE680_X1E_BUS_DEBUG_TOP),
		 readl_relaxed(vfe->base + VFE680_X1E_BUS_TEST_BUS_CTRL));
	for (i = 0; i < ARRAY_SIZE(vfe680_x1e_windows_bus_client_order); i++) {
		u8 client = vfe680_x1e_windows_bus_client_order[i];
		void __iomem *cfg = vfe680_x1e_bus_reg(vfe, client, 0);

		dev_info(vfe->camss->dev,
			 "E003h VFE1 %s busc%u cfg=%08x image=%08x stat=%08x/%08x/%08x/%08x dbg=%08x/%08x\n",
			 why, client, readl_relaxed(cfg + VFE680_X1E_BUS_CFG),
			 readl_relaxed(cfg + VFE680_X1E_BUS_IMAGE_ADDR),
			 readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS0),
			 readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS1),
			 readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS2),
			 readl_relaxed(cfg + VFE680_X1E_BUS_ADDR_STATUS3),
			 readl_relaxed(cfg + VFE680_X1E_BUS_DEBUG_STATUS0),
			 readl_relaxed(cfg + VFE680_X1E_BUS_DEBUG_STATUS1));
	}
	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s cfg=%08x/%08x/%08x diag=%08x core3=%08x throttle=%08x/%08x/%08x\n",
		 why, readl_relaxed(vfe->base + VFE680_X1E_SP11_DAL_CORE_CFG0),
		 readl_relaxed(vfe->base + VFE680_X1E_SP11_DAL_CORE_CFG1),
		 readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG2),
		 readl_relaxed(vfe->base + VFE_TOP_DIAG_CONFIG),
		 readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG3),
		 readl_relaxed(vfe->base + VFE680_X1E_STATS_THROTTLE0),
		 readl_relaxed(vfe->base + VFE680_X1E_STATS_THROTTLE1),
		 readl_relaxed(vfe->base + VFE680_X1E_STATS_THROTTLE2));
	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s core456=%08x/%08x/%08x period=%08x epoch_height=%08x\n",
		 why, readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG4),
		 readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG5),
		 readl_relaxed(vfe->base + VFE680_X1E_CORE_CFG6),
		 readl_relaxed(vfe->base + VFE680_X1E_PERIOD_CFG),
		 readl_relaxed(vfe->base + VFE680_X1E_EPOCH_HEIGHT_CFG));
	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s full0=%08x addr=%08x/%08x meta=%08x/%08x incr=%08x cfg0=%08x cfg2=%08x pack=%08x mode=%08x\n",
		 why, readl_relaxed(c0 + VFE680_X1E_BUS_CFG),
		 readl_relaxed(c0 + VFE680_X1E_BUS_IMAGE_ADDR), expected.image[0],
		 readl_relaxed(c0 + VFE680_X1E_BUS_META_ADDR), expected.full_meta[0],
		 readl_relaxed(c0 + VFE680_X1E_BUS_FRAME_INCR),
		 readl_relaxed(c0 + VFE680_X1E_BUS_IMAGE_CFG0),
		 readl_relaxed(c0 + VFE680_X1E_BUS_IMAGE_CFG2),
		 readl_relaxed(c0 + VFE680_X1E_BUS_PACKER_CFG),
		 readl_relaxed(c0 + VFE680_X1E_BUS_MODE_CFG));
	dev_info(vfe->camss->dev,
		 "E003h VFE1 %s full1=%08x addr=%08x/%08x meta=%08x/%08x incr=%08x cfg0=%08x cfg2=%08x pack=%08x mode=%08x\n",
		 why, readl_relaxed(c1 + VFE680_X1E_BUS_CFG),
		 readl_relaxed(c1 + VFE680_X1E_BUS_IMAGE_ADDR), expected.image[1],
		 readl_relaxed(c1 + VFE680_X1E_BUS_META_ADDR), expected.full_meta[1],
		 readl_relaxed(c1 + VFE680_X1E_BUS_FRAME_INCR),
		 readl_relaxed(c1 + VFE680_X1E_BUS_IMAGE_CFG0),
		 readl_relaxed(c1 + VFE680_X1E_BUS_IMAGE_CFG2),
		 readl_relaxed(c1 + VFE680_X1E_BUS_PACKER_CFG),
		 readl_relaxed(c1 + VFE680_X1E_BUS_MODE_CFG));
}

int vfe680_x1e_pix_runtime_poll_epoch0(struct vfe_device *vfe,
				       unsigned long timeout_us)
{
	struct vfe680_x1e_irq_snapshot snapshot;

	return vfe680_x1e_poll_epoch0(vfe, timeout_us, &snapshot);
}

int vfe680_x1e_pix_runtime_poll_video(struct vfe_device *vfe,
				      unsigned long timeout_us)
{
	struct vfe680_x1e_irq_snapshot snapshot;

	return vfe680_x1e_poll_video(vfe, timeout_us, &snapshot);
}

int vfe680_x1e_pix_runtime_retire_video(struct vfe680_x1e_pix_runtime *runtime,
					unsigned int expected_slot,
					struct camss_buffer **video_done)
{
	struct camss_buffer *done;
	bool reusable;
	unsigned int index;
	int ret;

	if (!runtime || !video_done || expected_slot >= VFE680_X1E_PIX_SLOT_COUNT)
		return -EINVAL;
	ret = vfe680_x1e_pix_ownership_complete(&runtime->ownership, 0x03,
						&index, &done, &reusable);
	if (ret)
		return ret;
	if (index != expected_slot || !done || reusable)
		return -EPROTO;

	*video_done = done;
	return 0;
}

static void vfe_global_reset(struct vfe_device *vfe)
{
	/* VFE680 has no global reset, simply report a completion */
	complete(&vfe->reset_complete);
}

/*
 * vfe_isr - VFE module interrupt handler
 * @irq: Interrupt line
 * @dev: VFE device
 *
 * Return IRQ_HANDLED on success
 */
static irqreturn_t vfe_isr(int irq, void *dev)
{
	return IRQ_HANDLED;
}

/*
 * vfe_halt - Trigger halt on VFE module and wait to complete
 * @vfe: VFE device
 *
 * Return 0 on success or a negative error code otherwise
 */
static int vfe_halt(struct vfe_device *vfe)
{
	/* rely on vfe_disable_output() to stop the VFE */
	return 0;
}

static void vfe_disable_irq(struct vfe_device *vfe)
{
	writel(0u, vfe->base + VFE_TOP_IRQn_MASK(vfe, 0));
	writel(0u, vfe->base + VFE_TOP_IRQn_MASK(vfe, 1));
	writel(0u, vfe->base + VFE_BUS_IRQn_MASK(vfe, 0));
	writel(0u, vfe->base + VFE_BUS_IRQn_MASK(vfe, 1));
}

static void vfe_wm_update(struct vfe_device *vfe, u8 rdi, u32 addr,
			  struct vfe_line *line)
{
	u8 wm = RDI_WM(rdi);

	writel(addr, vfe->base + VFE_BUS_IMAGE_ADDR(vfe, wm));
}

static void vfe_wm_start(struct vfe_device *vfe, u8 rdi, struct vfe_line *line)
{
	struct v4l2_pix_format_mplane *pix =
		&line->video_out.active_fmt.fmt.pix_mp;
	u32 stride = pix->plane_fmt[0].bytesperline;
	u32 cfg;
	u8 wm;

	cfg = VFE_BUS_IMAGE_CFG0_DATA(pix->height, stride);
	wm = RDI_WM(rdi);

	writel(cfg, vfe->base + VFE_BUS_IMAGE_CFG0(vfe, wm));
	writel(0, vfe->base + VFE_BUS_IMAGE_CFG1(vfe, wm));
	writel(stride, vfe->base + VFE_BUS_IMAGE_CFG2(vfe, wm));
	writel(0, vfe->base + VFE_BUS_PACKER_CFG(vfe, wm));

	/* Set total frame increment value */
	writel(pix->plane_fmt[0].bytesperline * pix->height,
	       vfe->base + VFE_BUS_FRAME_INCR(vfe, wm));

	/* MMU */
	writel(VFE_BUS_MMU_PREFETCH_CFG_EN, vfe->base + VFE_BUS_MMU_PREFETCH_CFG(vfe, wm));
	writel(~0u, vfe->base + VFE_BUS_MMU_PREFETCH_MAX_OFFSET(vfe, wm));

	/* no dropped frames, one irq per frame */
	writel(1, vfe->base + VFE_BUS_FRAMEDROP_PATTERN(vfe, wm));
	writel(0, vfe->base + VFE_BUS_FRAMEDROP_PERIOD(vfe, wm));
	writel(1, vfe->base + VFE_BUS_IRQ_SUBSAMPLE_PATTERN(vfe, wm));
	writel(0, vfe->base + VFE_BUS_IRQ_SUBSAMPLE_PERIOD(vfe, wm));

	/* We don't process IRQs for VFE in RDI mode at the moment */
	vfe_disable_irq(vfe);

	/* Enable WM */
	writel(VFE_BUS_WRITE_CLIENT_CFG_EN,
	       vfe->base + VFE_BUS_WRITE_CLIENT_CFG(vfe, wm));

	dev_dbg(vfe->camss->dev, "RDI%d WM:%d width %d height %d stride %d\n",
		rdi, wm, pix->width, pix->height, stride);
}

static void vfe_wm_stop(struct vfe_device *vfe, u8 rdi)
{
	u8 wm = RDI_WM(rdi);

	writel(0, vfe->base + VFE_BUS_WRITE_CLIENT_CFG(vfe, wm));
}

static const struct camss_video_ops vfe_video_ops_680 = {
	.queue_buffer = vfe_queue_buffer_v2,
	.flush_buffers = vfe_flush_buffers,
};

static void vfe_subdev_init(struct device *dev, struct vfe_device *vfe)
{
	vfe->video_ops = vfe_video_ops_680;
}

static void vfe_reg_update(struct vfe_device *vfe, enum vfe_line_id line_id)
{
	int port_id = line_id;

	camss_reg_update(vfe->camss, vfe->id, port_id, false);
}

static inline void vfe_reg_update_clear(struct vfe_device *vfe,
					enum vfe_line_id line_id)
{
	int port_id = line_id;

	camss_reg_update(vfe->camss, vfe->id, port_id, true);
}

const struct vfe_hw_ops vfe_ops_680 = {
	.global_reset = vfe_global_reset,
	.hw_version = vfe_hw_version,
	.isr = vfe_isr,
	.pm_domain_off = vfe_pm_domain_off,
	.pm_domain_on = vfe_pm_domain_on,
	.subdev_init = vfe_subdev_init,
	.vfe_disable = vfe_disable,
	.vfe_enable = vfe_enable_v2,
	.vfe_halt = vfe_halt,
	.vfe_wm_start = vfe_wm_start,
	.vfe_wm_stop = vfe_wm_stop,
	.vfe_buf_done = vfe_buf_done,
	.vfe_wm_update = vfe_wm_update,
	.reg_update = vfe_reg_update,
	.reg_update_clear = vfe_reg_update_clear,
};
