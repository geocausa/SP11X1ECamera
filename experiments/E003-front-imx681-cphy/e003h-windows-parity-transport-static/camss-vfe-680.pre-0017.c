// SPDX-License-Identifier: GPL-2.0
/*
 * camss-vfe-680.c
 *
 * Qualcomm MSM Camera Subsystem - VFE (Video Front End) Module v680
 *
 * Copyright (C) 2025 Linaro Ltd.
 */

#include <linux/delay.h>
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
