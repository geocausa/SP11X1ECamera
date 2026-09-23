/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E004ns: rear-only CSID1 physical register target captured by same-SP11
 * OEM Windows E004nq SP7 KD dd /p, LIVE1 and LIVE2.
 *
 * ISOLATED SOURCE-ONLY. No call site, probe, V4L2, sysfs, module param or
 * streaming hook. The standalone runtime authorization always denies.
 * These are observed final live-register TARGETS, NOT proof of Windows'
 * temporal startup order or of a Linux-ready 4K ISP IQ/DMA pipeline.
 */
#ifndef CAMSS_E004NS_REAR_CSID1_IPP_INC
#define CAMSS_E004NS_REAR_CSID1_IPP_INC

#define CSID_E004NS_REAR_RX_CFG0			0x10232103U
#define CSID_E004NS_REAR_RX_CFG1			0x00000001U
#define CSID_E004NS_REAR_IPP_CFG0		0x802b2000U
#define CSID_E004NS_REAR_IPP_CFG1		0x00007241U
#define CSID_E004NS_REAR_IPP_HCROP		0x0fdf0000U
#define CSID_E004NS_REAR_IPP_VCROP		0x08ed0000U
#define CSID_E004NS_REAR_IPP_FORMAT_CFG0		0x0000001fU
#define CSID_E004NS_REAR_IPP_FORMAT_CFG1		0x08ee0fe0U
#define CSID_E004NS_REAR_PARITY_ZERO0		0x00000000U
#define CSID_E004NS_REAR_PARITY_ZERO1		0x02000000U
#define CSID_E004NS_REAR_EPOCH_IRQ_CFG		0x00130013U
#define CSID_E004NS_REAR_EPOCH_PATTERN		0xffffffffU
#define CSID_E004NS_REAR_FRAME_DROP_PATTERN	0x00000000U
#define CSID_E004NS_REAR_FRAME_DROP_PERIOD	0x00000001U
#define CSID_E004NS_REAR_PIX_DROP_PATTERN	0x00000000U
#define CSID_E004NS_REAR_PIX_DROP_PERIOD		0x00000001U
#define CSID_E004NS_REAR_LINE_DROP_PATTERN	0x00000000U
#define CSID_E004NS_REAR_LINE_DROP_PERIOD	0x00000001U
#define CSID_E004NS_REAR_IRQ_SUBSAMPLE_PATTERN	0x00000001U
#define CSID_E004NS_REAR_IRQ_SUBSAMPLE_PERIOD	0x00000000U
#define CSID_E004NS_REAR_RX_IRQ_MASK		0x019fb800U
#define CSID_E004NS_REAR_BUF_DONE_IRQ_MASK	0x0001ffffU
#define CSID_E004NS_REAR_IPP_IRQ_MASK		0x3cbc601cU
#define CSID_E004NS_REAR_TOP_IRQ_MASK		0x00000001U
#define CSID_E004NS_REAR_WRAPPER_CFG0		0x00000101U
#define CSID_E004NS_REAR_LANE_ASSIGN		0x00003210U

/* The 0x10000000 TPG_NUM_SEL field is present even on this OEM rear
 * D-PHY receiver. Existing __csid_configure_rx only preserves that field
 * for front C-PHY. TPG mux itself is NOT enabled by setting the selector.
 * Do not copy E003g front C-PHY mode's 0x11300000 RX word.
 */
static bool __used
csid_e004ns_rear_ipp_mode0(const struct csid_device *csid)
{
	const struct v4l2_mbus_framefmt *fmt;

	if (!csid || !csid->camss || !csid->camss->res ||
	    csid->camss->res->version != CAMSS_X1E80100 ||
	    csid->id != 1 || !csid->base ||
	    !csid->camss->csid_wrapper_base ||
	    csid->phy.csiphy_id != 1 ||
	    csid->phy.phy_sel != CSID_PHY_SEL_DPHY ||
	    csid->phy.lane_cnt != 4 ||
	    csid->phy.lane_assign != CSID_E004NS_REAR_LANE_ASSIGN ||
	    !csid->phy.en_ipp || csid->phy.en_vc)
		return false;

	fmt = &csid->fmt[MSM_CSID_PAD_PIX];
	return fmt->code == MEDIA_BUS_FMT_SGRBG10_1X10 &&
	       fmt->width == 4076 && fmt->height == 2806;
}

/* Derived from the real rear Linux PHY identity AND verified bit fields
 * (PHY_NUM_SEL=2, 4 D-PHY lanes, DL0..3=0,1,2,3, TPG_NUM_SEL=1).
 * Source-only arithmetic means a mismatched CSIPHY lane map FAILS CLOSED.
 */
static u32 __used csid_e004ns_rear_rx_cfg0(const struct csid_device *csid)
{
	u32 val;

	val = (csid->phy.lane_cnt - 1) << CSI2_RX_CFG0_NUM_ACTIVE_LANES;
	val |= csid->phy.lane_assign << CSI2_RX_CFG0_DL0_INPUT_SEL;
	val |= (csid->phy.csiphy_id + CSI2_RX_CFG0_PHY_SEL_BASE_IDX)
	       << CSI2_RX_CFG0_PHY_NUM_SEL;
	val |= csid->phy.phy_sel << CSI2_RX_CFG0_PHY_TYPE_SEL;
	val |= 1U << CSI2_RX_CFG0_TPG_NUM_SEL;

	return val;
}

/* Complete final-state CSID1 rear configuration TARGET, never called.
 * The E003g front startup sequence is NOT assumed to be the Windows rear
 * startup sequence. The separate rear 4K RT-CDM/IQ/DMA/ownership state
 * machine must be validated before connecting any call site to this code.
 */
static int __used
csid_e004ns_rear_ipp_prepare(struct csid_device *csid)
{
	const struct v4l2_mbus_framefmt *fmt;
	const struct csid_format_info *format;
	u32 cfg0, rx_cfg0;

	if (!csid_e004ns_rear_ipp_mode0(csid))
		return -EINVAL;

	fmt = &csid->fmt[MSM_CSID_PAD_PIX];
	format = csid_get_fmt_entry(csid->res->formats->formats,
				    csid->res->formats->nformats, fmt->code);
	if (!format)
		return -EINVAL;

	cfg0 = (format->decode_format << IPP_CFG0_DECODE_FORMAT) |
	       (format->data_type << IPP_CFG0_DATA_TYPE) |
	       IPP_CFG0_ENABLE;
	rx_cfg0 = csid_e004ns_rear_rx_cfg0(csid);
	if (cfg0 != CSID_E004NS_REAR_IPP_CFG0 ||
	    format->data_type != 0x2b ||
	    rx_cfg0 != CSID_E004NS_REAR_RX_CFG0)
		return -EINVAL;

	/* Every value below was read in BOTH Windows rear live phases.
	 * Only the final register state has been observed, not the order.
	 */
	writel(rx_cfg0, csid->base + CSID_CSI2_RX_CFG0);
	writel(CSID_E004NS_REAR_RX_CFG1,
	       csid->base + CSID_CSI2_RX_CFG1);
	writel(CSID_E004NS_REAR_RX_IRQ_MASK,
	       csid->base + CSID_CSI2_RX_IRQ_MASK);
	writel(CSID_E004NS_REAR_BUF_DONE_IRQ_MASK,
	       csid->base + CSID_BUF_DONE_IRQ_MASK);
	writel(CSID_E004NS_REAR_FRAME_DROP_PATTERN,
	       csid->base + CSID_IPP_FRM_DROP_PATTERN);
	writel(CSID_E004NS_REAR_FRAME_DROP_PERIOD,
	       csid->base + CSID_IPP_FRM_DROP_PERIOD);
	writel(CSID_E004NS_REAR_PIX_DROP_PATTERN,
	       csid->base + CSID_IPP_PIX_DROP_PATTERN);
	writel(CSID_E004NS_REAR_PIX_DROP_PERIOD,
	       csid->base + CSID_IPP_PIX_DROP_PERIOD);
	writel(CSID_E004NS_REAR_LINE_DROP_PATTERN,
	       csid->base + CSID_IPP_LINE_DROP_PATTERN);
	writel(CSID_E004NS_REAR_LINE_DROP_PERIOD,
	       csid->base + CSID_IPP_LINE_DROP_PERIOD);
	writel(CSID_E004NS_REAR_IRQ_SUBSAMPLE_PATTERN,
	       csid->base + CSID_IPP_IRQ_SUBSAMPLE_PATTERN);
	writel(CSID_E004NS_REAR_IRQ_SUBSAMPLE_PERIOD,
	       csid->base + CSID_IPP_IRQ_SUBSAMPLE_PERIOD);
	writel(CSID_E004NS_REAR_EPOCH_IRQ_CFG,
	       csid->base + CSID_IPP_EPOCH_IRQ_CFG);
	writel(CSID_E004NS_REAR_EPOCH_PATTERN,
	       csid->base + CSID_IPP_EPOCH0_SUBSAMPLE_PATTERN);
	writel(CSID_E004NS_REAR_EPOCH_PATTERN,
	       csid->base + CSID_IPP_EPOCH1_SUBSAMPLE_PATTERN);
	writel(CSID_E004NS_REAR_IPP_HCROP,
	       csid->base + CSID_IPP_HCROP);
	writel(CSID_E004NS_REAR_IPP_VCROP,
	       csid->base + CSID_IPP_VCROP);
	writel(CSID_E004NS_REAR_IPP_FORMAT_CFG0,
	       csid->base + CSID_IPP_FORMAT_MEASURE_CFG0);
	writel(CSID_E004NS_REAR_IPP_FORMAT_CFG1,
	       csid->base + CSID_IPP_FORMAT_MEASURE_CFG1);
	writel(CSID_E004NS_REAR_PARITY_ZERO0,
	       csid->base + CSID_IPP_SP11_PARITY_ZERO0);
	writel(CSID_E004NS_REAR_PARITY_ZERO1,
	       csid->base + CSID_IPP_SP11_PARITY_ZERO1);
	writel(cfg0, csid->base + CSID_IPP_CFG0);
	writel(CSID_E004NS_REAR_IPP_CFG1,
	       csid->base + CSID_IPP_CFG1);

	return 0;
}

/* Separated from prepare: mode matching does NOT imply it is safe to
 * enable an ISP path; exclusivity, valid 4K/metadata DMA and rear ISP IQ
 * control are independent and still unimplemented.
 */
static int __used
csid_e004ns_rear_ipp_enable(struct csid_device *csid)
{
	if (!csid_e004ns_rear_ipp_mode0(csid))
		return -EINVAL;

	writel(CSID_E004NS_REAR_WRAPPER_CFG0,
	       csid->camss->csid_wrapper_base +
	       CSID_TOP_IO_PATH_CFG0(csid->id));
	writel(1, csid->base + CSID_IPP_CTRL);
	writel(CSID_E004NS_REAR_IPP_IRQ_MASK,
	       csid->base + CSID_IPP_IRQ_MASK);
	writel(CSID_E004NS_REAR_TOP_IRQ_MASK,
	       csid->base + CSID_TOP_IRQ_MASK);

	return 0;
}

/* Isolated rear runtime has no call site and MUST remain unconditionally
 * unavailable even when all physical identity/format checks pass.
 */
static int __used
csid_e004ns_rear_ipp_runtime_authorization(struct csid_device *csid)
{
	if (!csid_e004ns_rear_ipp_mode0(csid))
		return -EINVAL;
	return -EOPNOTSUPP;
}
#endif /* CAMSS_E004NS_REAR_CSID1_IPP_INC */
