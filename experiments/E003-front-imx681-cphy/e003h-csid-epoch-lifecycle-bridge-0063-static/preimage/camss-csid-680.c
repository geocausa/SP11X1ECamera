// SPDX-License-Identifier: GPL-2.0
/*
 * Qualcomm MSM Camera Subsystem - CSID (CSI Decoder) Module
 *
 * Copyright (C) 2020-2025 Linaro Ltd.
 */
#include <linux/completion.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/kernel.h>

#include "camss.h"
#include "camss-csid.h"
#include "camss-csid-gen2.h"

#define CSID_TOP_IO_PATH_CFG0(csid)				(0x4 * (csid))
#define		CSID_TOP_IO_PATH_CFG0_INTERNAL_CSID		BIT(0)
#define		CSID_TOP_IO_PATH_CFG0_SFE_0			BIT(1)
#define		CSID_TOP_IO_PATH_CFG0_SFE_1			GENMASK(1, 0)
#define		CSID_TOP_IO_PATH_CFG0_SBI_0			BIT(4)
#define		CSID_TOP_IO_PATH_CFG0_SBI_1			GENMASK(3, 0)
#define		CSID_TOP_IO_PATH_CFG0_SBI_2			GENMASK(3, 1)
#define		CSID_TOP_IO_PATH_CFG0_OUTPUT_IFE_EN		BIT(8)
#define		CSID_TOP_IO_PATH_CFG0_SFE_OFFLINE_EN		BIT(12)

#define CSID_RESET_CMD						0x10
#define		CSID_RESET_CMD_HW_RESET				BIT(0)
#define		CSID_RESET_CMD_SW_RESET				BIT(1)
#define		CSID_RESET_CMD_IRQ_CTRL				BIT(2)

#define CSID_IRQ_CMD						0x14
#define		CSID_IRQ_CMD_CLEAR				BIT(0)
#define		CSID_IRQ_CMD_SET				BIT(4)

#define CSID_REG_UPDATE_CMD					0x18

#define CSID_CSI2_RDIN_IRQ_STATUS(rdi)					(0xec + 0x10 * (rdi))
#define		CSID_CSI2_RDIN_CCIF_VIOLATION				BIT(29)
#define		CSID_CSI2_RDIN_SENSOR_SWITCH_OUT_OF_SYNC_FRAME_DROP	BIT(28)
#define		CSID_CSI2_RDIN_ERROR_REC_WIDTH_VIOLATION		BIT(27)
#define		CSID_CSI2_RDIN_ERROR_REC_HEIGHT_VIOLATION		BIT(26)
#define		CSID_CSI2_RDIN_BATCH_END_MISSING_VIOLATION		BIT(25)
#define		CSID_CSI2_RDIN_ILLEGAL_BATCH_ID_IRQ			BIT(24)
#define		CSID_CSI2_RDIN_RUP_DONE					BIT(23)
#define		CSID_CSI2_RDIN_CAMIF_EPOCH_1_IRQ			BIT(22)
#define		CSID_CSI2_RDIN_CAMIF_EPOCH_0_IRQ			BIT(21)
#define		CSID_CSI2_RDIN_ERROR_REC_OVERFLOW_IRQ			BIT(19)
#define		CSID_CSI2_RDIN_ERROR_REC_FRAME_DROP			BIT(18)
#define		CSID_CSI2_RDIN_VCDT_GRP_CHANG				BIT(17)
#define		CSID_CSI2_RDIN_VCDT_GRP_0_SEL				BIT(16)
#define		CSID_CSI2_RDIN_VCDT_GRP_1_SEL				BIT(15)
#define		CSID_CSI2_RDIN_ERROR_LINE_COUNT				BIT(14)
#define		CSID_CSI2_RDIN_ERROR_PIX_COUNT				BIT(13)
#define		CSID_CSI2_RDIN_INFO_INPUT_SOF				BIT(12)
#define		CSID_CSI2_RDIN_INFO_INPUT_SOL				BIT(11)
#define		CSID_CSI2_RDIN_INFO_INPUT_EOL				BIT(10)
#define		CSID_CSI2_RDIN_INFO_INPUT_EOF				BIT(9)
#define		CSID_CSI2_RDIN_INFO_FRAME_DROP_SOF			BIT(8)
#define		CSID_CSI2_RDIN_INFO_FRAME_DROP_SOL			BIT(7)
#define		CSID_CSI2_RDIN_INFO_FRAME_DROP_EOL			BIT(6)
#define		CSID_CSI2_RDIN_INFO_FRAME_DROP_EOF			BIT(5)
#define		CSID_CSI2_RDIN_INFO_CAMIF_SOF				BIT(4)
#define		CSID_CSI2_RDIN_INFO_CAMIF_EOF				BIT(3)
#define		CSID_CSI2_RDIN_INFO_FIFO_OVERFLOW			BIT(2)
#define		CSID_CSI2_RDIN_RES1					BIT(1)
#define		CSID_CSI2_RDIN_RES0					BIT(0)

#define CSID_CSI2_RDIN_IRQ_MASK(rdi)				(0xf0 + 0x10 * (rdi))
#define CSID_CSI2_RDIN_IRQ_CLEAR(rdi)				(0xf4 + 0x10 * (rdi))
#define CSID_CSI2_RDIN_IRQ_SET(rdi)				(0xf8 + 0x10 * (rdi))

#define CSID_TOP_IRQ_STATUS					0x7c
#define CSID_TOP_IRQ_MASK					0x80
#define CSID_TOP_IRQ_CLEAR					0x84
#define		CSID_TOP_IRQ_RESET				BIT(0)
#define		CSID_TOP_IRQ_RX					BIT(2)
#define		CSID_TOP_IRQ_LONG_PKT(rdi)			(BIT(8) << (rdi))
#define		CSID_TOP_IRQ_BUF_DONE				BIT(13)

#define CSID_BUF_DONE_IRQ_STATUS				0x8c
#define	BUF_DONE_IRQ_STATUS_RDI_OFFSET				(csid_is_lite(csid) ? 1 : 14)
#define CSID_BUF_DONE_IRQ_MASK					0x90
#define CSID_BUF_DONE_IRQ_CLEAR					0x94

#define CSID_CSI2_RX_IRQ_STATUS					0x9c
#define CSID_CSI2_RX_IRQ_MASK					0xa0
#define CSID_CSI2_RX_IRQ_CLEAR					0xa4

#define CSID_RESET_CFG						0xc
#define		CSID_RESET_CFG_MODE_IMMEDIATE			BIT(0)
#define		CSID_RESET_CFG_LOCATION_COMPLETE		BIT(4)

#define CSID_CSI2_RDI_IRQ_STATUS(rdi)				(0xec + 0x10 * (rdi))
#define CSID_CSI2_RDI_IRQ_MASK(rdi)				(0xf0 + 0x10 * (rdi))
#define CSID_CSI2_RDI_IRQ_CLEAR(rdi)				(0xf4 + 0x10 * (rdi))

#define CSID_CSI2_RX_CFG0					0x200
#define		CSI2_RX_CFG0_NUM_ACTIVE_LANES			0
#define		CSI2_RX_CFG0_DL0_INPUT_SEL			4
#define		CSI2_RX_CFG0_DL1_INPUT_SEL			8
#define		CSI2_RX_CFG0_DL2_INPUT_SEL			12
#define		CSI2_RX_CFG0_DL3_INPUT_SEL			16
#define		CSI2_RX_CFG0_PHY_NUM_SEL			20
#define		CSI2_RX_CFG0_PHY_SEL_BASE_IDX			1
#define		CSI2_RX_CFG0_PHY_TYPE_SEL			24
#define		CSI2_RX_CFG0_TPG_NUM_SEL			28

#define CSID_CSI2_RX_CFG1					0x204
#define		CSI2_RX_CFG1_PACKET_ECC_CORRECTION_EN		BIT(0)
#define		CSI2_RX_CFG1_DE_SCRAMBLE_EN			BIT(1)
#define		CSI2_RX_CFG1_VC_MODE				BIT(2)
#define		CSI2_RX_CFG1_COMPLETE_STREAM_EN			BIT(4)
#define		CSI2_RX_CFG1_COMPLETE_STREAM_FRAME_TIMING	BIT(5)
#define		CSI2_RX_CFG1_MISR_EN				BIT(6)
#define		CSI2_RX_CFG1_CGC_MODE				BIT(7)

#define CSID_CSI2_RX_CAPTURE_CTRL				0x208
#define		CSI2_RX_CAPTURE_CTRL_LONG_PKT_EN		BIT(0)
#define		CSI2_RX_CAPTURE_CTRL_SHORT_PKT_EN		BIT(1)
#define		CSI2_RX_CAPTURE_CTRL_CPHY_PKT_EN		BIT(2)
#define		CSI2_RX_CAPTURE_CTRL_LONG_PKT_DT		GENMASK(9, 4)
#define		CSI2_RX_CAPTURE_CTRL_LONG_PKT_VC		GENMASK(14, 10)
#define		CSI2_RX_CAPTURE_CTRL_SHORT_PKT_VC		GENMASK(19, 15)
#define		CSI2_RX_CAPTURE_CTRL_CPHY_PKT_DT		GENMASK(20, 25)
#define		CSI2_RX_CAPTURE_CTRL_CPHY_PKT_VC		GENMASK(30, 26)

#define CSID_CSI2_RX_TOTAL_PKTS_RCVD				0x240
#define CSID_CSI2_RX_STATS_ECC					0x244
#define CSID_CSI2_RX_CRC_ERRORS					0x248

/* Full-CSID IPP path, Qualcomm CSID680 register layout. */
#define CSID_IPP_IRQ_STATUS					0xac
#define CSID_IPP_IRQ_MASK					0xb0
#define CSID_IPP_IRQ_CLEAR					0xb4
#define		CSID_IPP_RUP_DONE				BIT(23)

#define CSID_IPP_CFG0						0x300
#define		IPP_CFG0_DECODE_FORMAT				12
#define		IPP_CFG0_DATA_TYPE				16
#define		IPP_CFG0_VIRTUAL_CHANNEL			22
#define		IPP_CFG0_DT_ID					27
#define		IPP_CFG0_ENABLE					BIT(31)
#define CSID_IPP_CTRL						0x304
#define CSID_IPP_CFG1						0x310
/* Exact same-machine Windows writes; semantic names are not yet proven. */
#define CSID_IPP_SP11_PARITY_ZERO0				0x324
#define CSID_IPP_SP11_PARITY_ZERO1				0x330
#define CSID_IPP_EPOCH_IRQ_CFG					0x334
#define CSID_IPP_EPOCH0_SUBSAMPLE_PATTERN			0x338
#define CSID_IPP_EPOCH1_SUBSAMPLE_PATTERN			0x33c
#define CSID_IPP_HCROP						0x35c
#define CSID_IPP_VCROP						0x360
#define CSID_IPP_PIX_DROP_PATTERN				0x364
#define CSID_IPP_PIX_DROP_PERIOD				0x368
#define CSID_IPP_LINE_DROP_PATTERN				0x36c
#define CSID_IPP_LINE_DROP_PERIOD				0x370
#define CSID_IPP_FRM_DROP_PATTERN				0x374
#define CSID_IPP_FRM_DROP_PERIOD				0x378
#define CSID_IPP_IRQ_SUBSAMPLE_PATTERN				0x37c
#define CSID_IPP_IRQ_SUBSAMPLE_PERIOD				0x380
#define CSID_IPP_FORMAT_MEASURE_CFG0				0x384
#define CSID_IPP_FORMAT_MEASURE_CFG1				0x388
#define CSID_IPP_FORMAT_MEASURE0				0x38c
#define CSID_IPP_FORMAT_MEASURE1				0x390
#define CSID_IPP_FORMAT_MEASURE2				0x394
#define		CSID_IPP_ERROR_LINE_COUNT			BIT(14)
/* Read-only timeout telemetry offsets; never replay these values. */
#define CSID_IPP_OBSERVED_STATUS0				0x340
#define CSID_IPP_OBSERVED_READBACK0				0x398
#define CSID_IPP_OBSERVED_READBACK1				0x39c

/* Exact same-machine Windows front mode-0 IPP stable configuration. */
#define SP11_IPP_CFG1_MODE0					0x00007241
#define SP11_IPP_EPOCH_IRQ_MODE0				0x00130013
#define SP11_IPP_EPOCH_SUBSAMPLE_MODE0				0xffffffff
#define SP11_IPP_HCROP_MODE0					0x0eff0000
#define SP11_IPP_VCROP_MODE0					0x086f0000
#define SP11_IPP_DROP_PERIOD_MODE0				0x00000001
#define SP11_IPP_IRQ_SUBSAMPLE_PATTERN_MODE0			0x00000001
#define SP11_IPP_FORMAT_MEASURE_CFG0_MODE0			0x0000001f
#define SP11_IPP_FORMAT_MEASURE_CFG1_MODE0			0x08700f00
#define SP11_CSID_TOP_IRQ_MASK_MODE0				0x00000001
#define SP11_CSID_BUF_DONE_IRQ_MASK_MODE0			0x0001ffff
#define SP11_CSID_RX_IRQ_MASK_MODE0				0x019fb800
#define SP11_CSID_IPP_IRQ_MASK_PREP_MODE0			0x3c1c7004
#define SP11_CSID_IPP_IRQ_MASK_MODE0				0x3cbc601c
#define SP11_CSID_RESET_TIMEOUT_MS				50

#define CSID_RDI_CFG0(rdi)					(0x500 + 0x100 * (rdi))
#define		RDI_CFG0_DECODE_FORMAT				12
#define		RDI_CFG0_DATA_TYPE				16
#define		RDI_CFG0_VIRTUAL_CHANNEL			22
#define		RDI_CFG0_DT_ID					27
#define		RDI_CFG0_ENABLE					BIT(31)

#define CSID_RDI_CTRL(rdi)					(0x504 + 0x100 * (rdi))
#define		CSID_RDI_CTRL_HALT_CMD_HALT_AT_FRAME_BOUNDARY	0
#define		CSID_RDI_CTRL_HALT_CMD_RESUME_AT_FRAME_BOUNDARY	1

#define CSID_RDI_CFG1(rdi)					(0x510 + 0x100 * (rdi))
#define		RDI_CFG1_TIMESTAMP_STB_FRAME			BIT(0)
#define		RDI_CFG1_TIMESTAMP_STB_IRQ			BIT(1)
#define		RDI_CFG1_BYTE_CNTR_EN				BIT(2)
#define		RDI_CFG1_TIMESTAMP_EN				BIT(4)
#define		RDI_CFG1_DROP_H_EN				BIT(5)
#define		RDI_CFG1_DROP_V_EN				BIT(6)
#define		RDI_CFG1_CROP_H_EN				BIT(7)
#define		RDI_CFG1_CROP_V_EN				BIT(8)
#define		RDI_CFG1_MISR_EN				BIT(9)
#define		RDI_CFG1_PLAIN_ALIGN_MSB			BIT(11)
#define		RDI_CFG1_EARLY_EOF_EN				BIT(14)
#define		RDI_CFG1_PACKING_MIPI				BIT(15)

#define CSID_RDI_ERR_RECOVERY_CFG0(rdi)				(0x514 + 0x100 * (rdi))
#define CSID_RDI_EPOCH_IRQ_CFG(rdi)				(0x52c + 0x100 * (rdi))
#define CSID_RDI_FRM_DROP_PATTERN(rdi)				(0x540 + 0x100 * (rdi))
#define CSID_RDI_FRM_DROP_PERIOD(rdi)				(0x544 + 0x100 * (rdi))
#define CSID_RDI_IRQ_SUBSAMPLE_PATTERN(rdi)			(0x548 + 0x100 * (rdi))
#define CSID_RDI_IRQ_SUBSAMPLE_PERIOD(rdi)			(0x54c + 0x100 * (rdi))
#define CSID_RDI_PIX_DROP_PATTERN(rdi)				(0x558 + 0x100 * (rdi))
#define CSID_RDI_PIX_DROP_PERIOD(rdi)				(0x55c + 0x100 * (rdi))
#define CSID_RDI_LINE_DROP_PATTERN(rdi)				(0x560 + 0x100 * (rdi))
#define CSID_RDI_LINE_DROP_PERIOD(rdi)				(0x564 + 0x100 * (rdi))

static inline int reg_update_rdi(struct csid_device *csid, int n)
{
	return BIT(4 + n) + BIT(20 + n);
}

static inline int reg_update_ipp(void)
{
	return BIT(0) | BIT(16);
}

static void csid_reg_update(struct csid_device *csid, int port_id)
{
	if (csid->camss->res->version == CAMSS_X1E80100 &&
	    port_id == MSM_CSID_STREAM_PIX && csid->phy.en_ipp)
		csid->reg_update |= reg_update_ipp();
	else
		csid->reg_update |= reg_update_rdi(csid, port_id);

	writel(csid->reg_update, csid->base + CSID_REG_UPDATE_CMD);
}

static inline void csid_reg_update_clear(struct csid_device *csid,
					 int port_id)
{
	if (csid->camss->res->version == CAMSS_X1E80100 &&
	    port_id == MSM_CSID_STREAM_PIX && csid->phy.en_ipp)
		csid->reg_update &= ~reg_update_ipp();
	else
		csid->reg_update &= ~reg_update_rdi(csid, port_id);

	writel(csid->reg_update, csid->base + CSID_REG_UPDATE_CMD);
}

static void __csid_configure_rx(struct csid_device *csid,
				struct csid_phy_config *phy, int vc)
{
	u32 val;

	val = (phy->lane_cnt - 1) << CSI2_RX_CFG0_NUM_ACTIVE_LANES;
	val |= phy->lane_assign << CSI2_RX_CFG0_DL0_INPUT_SEL;
	val |= (phy->csiphy_id + CSI2_RX_CFG0_PHY_SEL_BASE_IDX) << CSI2_RX_CFG0_PHY_NUM_SEL;
	val |= phy->phy_sel << CSI2_RX_CFG0_PHY_TYPE_SEL;

	/*
	 * Same-machine SP11 Windows programs TPG_NUM_SEL=1 for the active
	 * one-trio C-PHY receiver while leaving TPG mux disabled. Preserve
	 * that otherwise-inert field on X1E80100 rather than normalizing it
	 * away: CSIPHY2 C-PHY must produce RX_CFG0 == 0x11300000.
	 */
	if (csid->camss->res->version == CAMSS_X1E80100 &&
	    phy->phy_sel == CSID_PHY_SEL_CPHY)
		val |= 1 << CSI2_RX_CFG0_TPG_NUM_SEL;

	writel(val, csid->base + CSID_CSI2_RX_CFG0);

	val = CSI2_RX_CFG1_PACKET_ECC_CORRECTION_EN;
	if (vc > 3)
		val |= CSI2_RX_CFG1_VC_MODE;
	writel(val, csid->base + CSID_CSI2_RX_CFG1);
}

static void __csid_ctrl_rdi(struct csid_device *csid, int enable, u8 rdi)
{
	u32 val;

	if (enable)
		val = CSID_RDI_CTRL_HALT_CMD_RESUME_AT_FRAME_BOUNDARY;
	else
		val = CSID_RDI_CTRL_HALT_CMD_HALT_AT_FRAME_BOUNDARY;

	writel(val, csid->base + CSID_RDI_CTRL(rdi));
}

static bool __csid_sp11_front_ipp_mode0(struct csid_device *csid)
{
	struct v4l2_mbus_framefmt *fmt = &csid->fmt[MSM_CSID_PAD_PIX];

	return csid->camss->res->version == CAMSS_X1E80100 &&
	       csid->id == 1 && csid->phy.csiphy_id == 2 &&
	       csid->phy.phy_sel == CSID_PHY_SEL_CPHY &&
	       csid->phy.lane_cnt == 1 &&
	       fmt->code == MEDIA_BUS_FMT_SRGGB10_1X10 &&
	       fmt->width == 3840 && fmt->height == 2160;
}

static void __csid_ctrl_ipp(struct csid_device *csid, int enable)
{
	writel(enable ? 1 : 0, csid->base + CSID_IPP_CTRL);
}

static int __csid_sp11_front_ipp_full_config(struct csid_device *csid)
{
	struct v4l2_mbus_framefmt *input_format = &csid->fmt[MSM_CSID_PAD_PIX];
	const struct csid_format_info *format;
	u32 val;

	if (!__csid_sp11_front_ipp_mode0(csid))
		return -EINVAL;

	format = csid_get_fmt_entry(csid->res->formats->formats,
				    csid->res->formats->nformats,
				    input_format->code);

	/* qccamisp8380 full-CSID builder RVA 0x1a870, exact write order. */
	__csid_configure_rx(csid, &csid->phy, 0);
	writel(SP11_CSID_RX_IRQ_MASK_MODE0, csid->base + CSID_CSI2_RX_IRQ_MASK);
	writel(SP11_CSID_BUF_DONE_IRQ_MASK_MODE0,
	       csid->base + CSID_BUF_DONE_IRQ_MASK);
	writel(0, csid->base + CSID_IPP_FRM_DROP_PATTERN);
	writel(SP11_IPP_DROP_PERIOD_MODE0, csid->base + CSID_IPP_FRM_DROP_PERIOD);
	writel(SP11_IPP_IRQ_SUBSAMPLE_PATTERN_MODE0,
	       csid->base + CSID_IPP_IRQ_SUBSAMPLE_PATTERN);
	writel(0, csid->base + CSID_IPP_IRQ_SUBSAMPLE_PERIOD);
	writel(0, csid->base + CSID_IPP_PIX_DROP_PATTERN);
	writel(SP11_IPP_DROP_PERIOD_MODE0, csid->base + CSID_IPP_PIX_DROP_PERIOD);
	writel(0, csid->base + CSID_IPP_LINE_DROP_PATTERN);
	writel(SP11_IPP_DROP_PERIOD_MODE0, csid->base + CSID_IPP_LINE_DROP_PERIOD);
	writel(SP11_IPP_EPOCH_IRQ_MODE0, csid->base + CSID_IPP_EPOCH_IRQ_CFG);
	writel(SP11_IPP_EPOCH_SUBSAMPLE_MODE0,
	       csid->base + CSID_IPP_EPOCH0_SUBSAMPLE_PATTERN);
	writel(SP11_IPP_EPOCH_SUBSAMPLE_MODE0,
	       csid->base + CSID_IPP_EPOCH1_SUBSAMPLE_PATTERN);
	writel(SP11_IPP_HCROP_MODE0, csid->base + CSID_IPP_HCROP);
	writel(SP11_IPP_VCROP_MODE0, csid->base + CSID_IPP_VCROP);

	val = format->decode_format << IPP_CFG0_DECODE_FORMAT;
	val |= format->data_type << IPP_CFG0_DATA_TYPE;
	val |= IPP_CFG0_ENABLE;
	writel(val, csid->base + CSID_IPP_CFG0);
	writel(SP11_IPP_CFG1_MODE0, csid->base + CSID_IPP_CFG1);
	writel(0, csid->base + CSID_IPP_SP11_PARITY_ZERO0);
	writel(SP11_CSID_IPP_IRQ_MASK_PREP_MODE0,
	       csid->base + CSID_IPP_IRQ_MASK);

	return 0;
}

static void __csid_configure_top(struct csid_device *csid)
{
	u32 val;

	val = CSID_TOP_IO_PATH_CFG0_OUTPUT_IFE_EN | CSID_TOP_IO_PATH_CFG0_INTERNAL_CSID;
	writel(val, csid->camss->csid_wrapper_base +
	    CSID_TOP_IO_PATH_CFG0(csid->id));
}

static void __csid_configure_rdi_stream(struct csid_device *csid, u8 enable, u8 vc)
{
	struct v4l2_mbus_framefmt *input_format = &csid->fmt[MSM_CSID_PAD_FIRST_SRC + vc];
	const struct csid_format_info *format = csid_get_fmt_entry(csid->res->formats->formats,
								   csid->res->formats->nformats,
								   input_format->code);
	u8 lane_cnt = csid->phy.lane_cnt;
	u8 dt_id;
	u32 val;

	if (!lane_cnt)
		lane_cnt = 4;

	val = 0;
	writel(val, csid->base + CSID_RDI_FRM_DROP_PERIOD(vc));

	/*
	 * DT_ID is a two bit bitfield that is concatenated with
	 * the four least significant bits of the five bit VC
	 * bitfield to generate an internal CID value.
	 *
	 * CSID_RDI_CFG0(vc)
	 * DT_ID : 28:27
	 * VC    : 26:22
	 * DT    : 21:16
	 *
	 * CID   : VC 3:0 << 2 | DT_ID 1:0
	 */
	dt_id = vc & 0x03;

	/* note: for non-RDI path, this should be format->decode_format */
	val |= DECODE_FORMAT_PAYLOAD_ONLY << RDI_CFG0_DECODE_FORMAT;
	val |= format->data_type << RDI_CFG0_DATA_TYPE;
	val |= vc << RDI_CFG0_VIRTUAL_CHANNEL;
	val |= dt_id << RDI_CFG0_DT_ID;
	writel(val, csid->base + CSID_RDI_CFG0(vc));

	val = RDI_CFG1_TIMESTAMP_STB_FRAME;
	val |= RDI_CFG1_BYTE_CNTR_EN;
	val |= RDI_CFG1_TIMESTAMP_EN;
	val |= RDI_CFG1_DROP_H_EN;
	val |= RDI_CFG1_DROP_V_EN;
	val |= RDI_CFG1_CROP_H_EN;
	val |= RDI_CFG1_CROP_V_EN;
	val |= RDI_CFG1_PACKING_MIPI;

	writel(val, csid->base + CSID_RDI_CFG1(vc));

	val = 0;
	writel(val, csid->base + CSID_RDI_IRQ_SUBSAMPLE_PERIOD(vc));

	val = 1;
	writel(val, csid->base + CSID_RDI_IRQ_SUBSAMPLE_PATTERN(vc));

	val = 0;
	writel(val, csid->base + CSID_RDI_CTRL(vc));

	val = readl(csid->base + CSID_RDI_CFG0(vc));
	if (enable)
		val |= RDI_CFG0_ENABLE;
	else
		val &= ~RDI_CFG0_ENABLE;
	writel(val, csid->base + CSID_RDI_CFG0(vc));
}

int csid680_x1e_front_ipp_companion(struct csid_device *csid, unsigned int packet)
{
	if (!csid || !csid->phy.en_ipp || !__csid_sp11_front_ipp_mode0(csid) ||
	    packet >= 4)
		return -EINVAL;

	/* Exact CSID descriptor-1 companion writes after each IFE 0x803 packet. */
	if (!packet) {
		writel(0, csid->base + CSID_IPP_SP11_PARITY_ZERO1);
		writel(SP11_IPP_IRQ_SUBSAMPLE_PATTERN_MODE0,
		       csid->base + CSID_IPP_IRQ_SUBSAMPLE_PATTERN);
		writel(0, csid->base + CSID_IPP_IRQ_SUBSAMPLE_PERIOD);
	}

	writel(SP11_IPP_HCROP_MODE0, csid->base + CSID_IPP_HCROP);
	writel(SP11_IPP_VCROP_MODE0, csid->base + CSID_IPP_VCROP);

	if (!packet) {
		writel(SP11_IPP_FORMAT_MEASURE_CFG0_MODE0,
		       csid->base + CSID_IPP_FORMAT_MEASURE_CFG0);
		writel(SP11_IPP_FORMAT_MEASURE_CFG1_MODE0,
		       csid->base + CSID_IPP_FORMAT_MEASURE_CFG1);
	}

	return 0;
}

int csid680_x1e_front_ipp_enable(struct csid_device *csid)
{
	if (!csid || !csid->phy.en_ipp || !__csid_sp11_front_ipp_mode0(csid))
		return -EINVAL;

	/* Windows CSID 0x804 path-5 enable: CTRL -> final IPP mask -> TOP mask. */
	__csid_ctrl_ipp(csid, true);
	writel(SP11_CSID_IPP_IRQ_MASK_MODE0, csid->base + CSID_IPP_IRQ_MASK);
	writel(SP11_CSID_TOP_IRQ_MASK_MODE0, csid->base + CSID_TOP_IRQ_MASK);

	return 0;
}

static void csid_configure_stream(struct csid_device *csid, u8 enable)
{
	int i;

	if (csid->phy.en_ipp && __csid_sp11_front_ipp_mode0(csid)) {
		if (enable)
			csid680_x1e_front_ipp_enable(csid);
	} else {
		__csid_configure_top(csid);
	}

       /* Loop through all enabled RDI VCs and configure stream for each */
	for (i = 0; i < MSM_CSID_MAX_SRC_STREAMS; i++) {
		if (csid->phy.en_vc & BIT(i)) {
			__csid_configure_rdi_stream(csid, enable, i);
			__csid_configure_rx(csid, &csid->phy, i);
			__csid_ctrl_rdi(csid, enable, i);
		}
	}
}

void csid680_x1e_front_runtime_dump(struct csid_device *csid, const char *reason)
{
	const char *why = reason ? reason : "snapshot";
	u32 wrapper;
	u32 i;

	if (!csid || !csid->base || !csid->camss->csid_wrapper_base ||
	    !__csid_sp11_front_ipp_mode0(csid))
		return;

	wrapper = readl_relaxed(csid->camss->csid_wrapper_base +
				CSID_TOP_IO_PATH_CFG0(csid->id));
	dev_info(csid->camss->dev,
		 "E003h CSID1 %s route=%08x regupd=%08x top=%08x/%08x buf=%08x/%08x\n",
		 why, wrapper, readl_relaxed(csid->base + CSID_REG_UPDATE_CMD),
		 readl_relaxed(csid->base + CSID_TOP_IRQ_STATUS),
		 readl_relaxed(csid->base + CSID_TOP_IRQ_MASK),
		 readl_relaxed(csid->base + CSID_BUF_DONE_IRQ_STATUS),
		 readl_relaxed(csid->base + CSID_BUF_DONE_IRQ_MASK));
	dev_info(csid->camss->dev,
		 "E003h CSID1 %s rx=%08x/%08x cfg=%08x/%08x pkts=%08x ecc=%08x crc=%08x\n",
		 why, readl_relaxed(csid->base + CSID_CSI2_RX_IRQ_STATUS),
		 readl_relaxed(csid->base + CSID_CSI2_RX_IRQ_MASK),
		 readl_relaxed(csid->base + CSID_CSI2_RX_CFG0),
		 readl_relaxed(csid->base + CSID_CSI2_RX_CFG1),
		 readl_relaxed(csid->base + CSID_CSI2_RX_TOTAL_PKTS_RCVD),
		 readl_relaxed(csid->base + CSID_CSI2_RX_STATS_ECC),
		 readl_relaxed(csid->base + CSID_CSI2_RX_CRC_ERRORS));
	dev_info(csid->camss->dev,
		 "E003h CSID1 %s ipp=%08x/%08x ctrl=%08x cfg=%08x/%08x z324=%08x z330=%08x epoch=%08x\n",
		 why, readl_relaxed(csid->base + CSID_IPP_IRQ_STATUS),
		 readl_relaxed(csid->base + CSID_IPP_IRQ_MASK),
		 readl_relaxed(csid->base + CSID_IPP_CTRL),
		 readl_relaxed(csid->base + CSID_IPP_CFG0),
		 readl_relaxed(csid->base + CSID_IPP_CFG1),
		 readl_relaxed(csid->base + CSID_IPP_SP11_PARITY_ZERO0),
		 readl_relaxed(csid->base + CSID_IPP_SP11_PARITY_ZERO1),
		 readl_relaxed(csid->base + CSID_IPP_EPOCH_IRQ_CFG));
	dev_info(csid->camss->dev,
		 "E003h CSID1 %s ipp-history=%08x/%08x/%u line-error=%08x/%08x/%08x\n",
		 why, csid->x1e_ipp_irq_seen_or, csid->x1e_ipp_irq_last,
		 csid->x1e_ipp_irq_count, csid->x1e_ipp_line_error_frame,
		 csid->x1e_ipp_line_error_hbi, csid->x1e_ipp_line_error_vbi);
	for (i = 0; i < csid->x1e_ipp_irq_trace_count &&
	     i < X1E_IPP_IRQ_TRACE_MAX; i++)
		dev_info(csid->camss->dev,
			 "E003h CSID1 %s ipp-seq[%u]=%08x/%08x\n",
			 why, i, csid->x1e_ipp_irq_trace_status[i],
			 csid->x1e_ipp_irq_trace_actual[i]);
	dev_info(csid->camss->dev,
		 "E003h CSID1 %s crop=%08x/%08x drop=%08x/%08x/%08x/%08x/%08x/%08x measure=%08x/%08x obs=%08x/%08x/%08x\n",
		 why, readl_relaxed(csid->base + CSID_IPP_HCROP),
		 readl_relaxed(csid->base + CSID_IPP_VCROP),
		 readl_relaxed(csid->base + CSID_IPP_PIX_DROP_PATTERN),
		 readl_relaxed(csid->base + CSID_IPP_PIX_DROP_PERIOD),
		 readl_relaxed(csid->base + CSID_IPP_LINE_DROP_PATTERN),
		 readl_relaxed(csid->base + CSID_IPP_LINE_DROP_PERIOD),
		 readl_relaxed(csid->base + CSID_IPP_FRM_DROP_PATTERN),
		 readl_relaxed(csid->base + CSID_IPP_FRM_DROP_PERIOD),
		 readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE_CFG0),
		 readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE_CFG1),
		 readl_relaxed(csid->base + CSID_IPP_OBSERVED_STATUS0),
		 readl_relaxed(csid->base + CSID_IPP_OBSERVED_READBACK0),
		 readl_relaxed(csid->base + CSID_IPP_OBSERVED_READBACK1));
}

/*
 * csid_reset - Trigger reset on CSID module and wait to complete
 * @csid: CSID device
 *
 * Return 0 on success or a negative error code otherwise
 */
static int csid_reset(struct csid_device *csid)
{
	bool front_mode0 = __csid_sp11_front_ipp_mode0(csid);
	unsigned long time;
	u32 val;
	int i;

	reinit_completion(&csid->reset_complete);

	if (front_mode0) {
		/*
		 * Same-machine Windows DEVICE_CONFIG:
		 * wrapper route -> TOP mask -> RESET_CFG -> SW reset -> full builder.
		 */
		__csid_configure_top(csid);
		writel(SP11_CSID_TOP_IRQ_MASK_MODE0,
		       csid->base + CSID_TOP_IRQ_MASK);
		val = CSID_RESET_CFG_MODE_IMMEDIATE |
		      CSID_RESET_CFG_LOCATION_COMPLETE;
		writel(val, csid->base + CSID_RESET_CFG);
		writel(CSID_RESET_CMD_SW_RESET, csid->base + CSID_RESET_CMD);

		time = wait_for_completion_timeout(&csid->reset_complete,
						   msecs_to_jiffies(SP11_CSID_RESET_TIMEOUT_MS));
		if (!time) {
			dev_err(csid->camss->dev, "SP11 CSID1 software reset timeout\n");
			return -EIO;
		}

		/* Start a software-only history epoch before any front startup traffic. */
		csid->x1e_ipp_irq_seen_or = 0;
		csid->x1e_ipp_irq_last = 0;
		csid->x1e_ipp_irq_count = 0;
		csid->x1e_ipp_irq_trace_count = 0;
		csid->x1e_ipp_line_error_frame = 0;
		csid->x1e_ipp_line_error_hbi = 0;
		csid->x1e_ipp_line_error_vbi = 0;

		return __csid_sp11_front_ipp_full_config(csid);
	}

	writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);

	/* preserve registers */
	val = CSID_RESET_CFG_MODE_IMMEDIATE | CSID_RESET_CFG_LOCATION_COMPLETE;
	writel(val, csid->base + CSID_RESET_CFG);

	val = CSID_RESET_CMD_HW_RESET | CSID_RESET_CMD_SW_RESET;
	writel(val, csid->base + CSID_RESET_CMD);

	time = wait_for_completion_timeout(&csid->reset_complete,
					   msecs_to_jiffies(CSID_RESET_TIMEOUT_MS));
	if (!time) {
		dev_err(csid->camss->dev, "CSID reset timeout\n");
		return -EIO;
	}

	for (i = 0; i < MSM_CSID_MAX_SRC_STREAMS; i++) {
		/* Enable RUP done for the client port */
		writel(CSID_CSI2_RDIN_RUP_DONE, csid->base + CSID_CSI2_RDIN_IRQ_MASK(i));
	}

	if (!csid_is_lite(csid))
		writel(CSID_IPP_RUP_DONE, csid->base + CSID_IPP_IRQ_MASK);

	/* Clear RDI status */
	writel(~0u, csid->base + CSID_BUF_DONE_IRQ_CLEAR);

	/* Enable BUF_DONE bit for all write-master client ports */
	writel(~0u, csid->base + CSID_BUF_DONE_IRQ_MASK);

	/* Unmask all TOP interrupts */
	writel(~0u, csid->base + CSID_TOP_IRQ_MASK);

	return 0;
}

int csid680_x1e_front_ipp_stop(struct csid_device *csid)
{
	unsigned long time;
	u32 val;

	if (!csid || !csid->phy.en_ipp || !__csid_sp11_front_ipp_mode0(csid))
		return -EINVAL;

	reinit_completion(&csid->reset_complete);
	writel(SP11_CSID_TOP_IRQ_MASK_MODE0, csid->base + CSID_TOP_IRQ_MASK);
	val = CSID_RESET_CFG_MODE_IMMEDIATE | CSID_RESET_CFG_LOCATION_COMPLETE;
	writel(val, csid->base + CSID_RESET_CFG);
	writel(CSID_RESET_CMD_HW_RESET, csid->base + CSID_RESET_CMD);

	time = wait_for_completion_timeout(&csid->reset_complete,
					   msecs_to_jiffies(SP11_CSID_RESET_TIMEOUT_MS));
	if (!time) {
		dev_err(csid->camss->dev, "SP11 CSID1 hardware stop reset timeout\n");
		return -EIO;
	}

	return 0;
}

static void csid_rup_complete(struct csid_device *csid, int rdi)
{
	csid_reg_update_clear(csid, rdi);
}

/*
 * csid_isr - CSID module interrupt service routine
 * @irq: Interrupt line
 * @dev: CSID device
 *
 * Return IRQ_HANDLED on success
 */
static irqreturn_t csid_isr(int irq, void *dev)
{
	struct csid_device *csid = dev;
	u32 buf_done_val, ipp_val = 0, val, val_top;
	int i;

	/* Latch and clear TOP status */
	val_top = readl(csid->base + CSID_TOP_IRQ_STATUS);
	writel(val_top, csid->base + CSID_TOP_IRQ_CLEAR);

	/* Latch and clear CSID_CSI2 status */
	val = readl(csid->base + CSID_CSI2_RX_IRQ_STATUS);
	writel(val, csid->base + CSID_CSI2_RX_IRQ_CLEAR);

	/* Latch and clear top level BUF_DONE status */
	buf_done_val = readl(csid->base + CSID_BUF_DONE_IRQ_STATUS);
	writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);

	if (!csid_is_lite(csid)) {
		ipp_val = readl(csid->base + CSID_IPP_IRQ_STATUS);
		if (ipp_val && __csid_sp11_front_ipp_mode0(csid)) {
			u32 trace_idx;

			csid->x1e_ipp_irq_seen_or |= ipp_val;
			csid->x1e_ipp_irq_last = ipp_val;
			csid->x1e_ipp_irq_count++;
			if (csid->x1e_ipp_irq_trace_count < X1E_IPP_IRQ_TRACE_MAX) {
				trace_idx = csid->x1e_ipp_irq_trace_count++;
				csid->x1e_ipp_irq_trace_status[trace_idx] = ipp_val;
				csid->x1e_ipp_irq_trace_actual[trace_idx] =
					readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE0);
			}
			if (ipp_val & CSID_IPP_ERROR_LINE_COUNT) {
				csid->x1e_ipp_line_error_frame =
					readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE0);
				csid->x1e_ipp_line_error_hbi =
					readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE1);
				csid->x1e_ipp_line_error_vbi =
					readl_relaxed(csid->base + CSID_IPP_FORMAT_MEASURE2);
			}
		}
		if (ipp_val)
			writel(ipp_val, csid->base + CSID_IPP_IRQ_CLEAR);

		if (ipp_val & CSID_IPP_RUP_DONE) {
			if (csid->phy.en_ipp && __csid_sp11_front_ipp_mode0(csid))
				csid->reg_update &= ~reg_update_ipp();
			else
				csid_reg_update_clear(csid, MSM_CSID_STREAM_PIX);
		}
	}

	/* Process state for each RDI channel */
	for (i = 0; i < MSM_CSID_MAX_SRC_STREAMS; i++) {
		val = readl(csid->base + CSID_CSI2_RDIN_IRQ_STATUS(i));
		if (val)
			writel(val, csid->base + CSID_CSI2_RDIN_IRQ_CLEAR(i));

		if (val & CSID_CSI2_RDIN_RUP_DONE)
			csid_rup_complete(csid, i);

		if (buf_done_val & BIT(BUF_DONE_IRQ_STATUS_RDI_OFFSET + i))
			camss_buf_done(csid->camss, csid->id, i);
	}

	/* Issue clear command */
	writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);

	/* Reset complete */
	if (val_top & CSID_TOP_IRQ_RESET)
		complete(&csid->reset_complete);

	return IRQ_HANDLED;
}

static void csid_subdev_reg_update(struct csid_device *csid, int port_id, bool is_clear)
{
	if (is_clear)
		csid_reg_update_clear(csid, port_id);
	else
		csid_reg_update(csid, port_id);
}

static void csid_subdev_init(struct csid_device *csid) {}

const struct csid_hw_ops csid_ops_680 = {
	.configure_testgen_pattern = NULL,
	.configure_stream = csid_configure_stream,
	.hw_version = csid_hw_version,
	.isr = csid_isr,
	.reset = csid_reset,
	.src_pad_code = csid_src_pad_code,
	.subdev_init = csid_subdev_init,
	.reg_update = csid_subdev_reg_update,
};
