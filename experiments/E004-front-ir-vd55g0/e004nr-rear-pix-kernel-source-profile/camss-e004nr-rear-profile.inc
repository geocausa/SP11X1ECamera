/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E004nr: same-SP11 OEM Windows rear 4K physical-register source contract.
 *
 * SOURCE-ONLY. This file is included into an ISOLATED qcom-camss build after
 * camss_x1e_pix_link(), not into the booted Golden or default front runner.
 * The function tests the Linux media graph and existing Linux sensor mode.
 * Returning zero means GRAPH PREFLIGHT ONLY, never hardware, IQ, memory,
 * image quality, stream ownership or optical-frame validation.
 */
#ifndef CAMSS_E004NR_REAR_PROFILE_INC
#define CAMSS_E004NR_REAR_PROFILE_INC

#define CAMSS_E004NR_REAR_SENSOR_WIDTH		4076U
#define CAMSS_E004NR_REAR_SENSOR_HEIGHT		2806U
#define CAMSS_E004NR_REAR_IPP_CROP_WIDTH		4064U
#define CAMSS_E004NR_REAR_IPP_CROP_HEIGHT	2286U
#define CAMSS_E004NR_REAR_FULL_WIDTH		3840U
#define CAMSS_E004NR_REAR_FULL_Y_HEIGHT		2160U
#define CAMSS_E004NR_REAR_FULL_C_HEIGHT		1080U
#define CAMSS_E004NR_REAR_FULL_WM_STRIDE		5120U
#define CAMSS_E004NR_REAR_FULL_PACKER_CFG	0x0bU
#define CAMSS_E004NR_REAR_FULL_Y_FRAME_INCR	0x00a9d000U
#define CAMSS_E004NR_REAR_FULL_C_FRAME_INCR	0x00559000U
#define CAMSS_E004NR_REAR_FULL_META_CFG		0x00000800U
#define CAMSS_E004NR_REAR_FULL_Y_MODE		0x00000023U
#define CAMSS_E004NR_REAR_FULL_C_MODE		0x00000033U
#define CAMSS_E004NR_REAR_DS4_FRAME_INCR	0x0010e000U
#define CAMSS_E004NR_REAR_DS16_FRAME_INCR	0x00018000U
#define CAMSS_E004NR_REAR_RX_CFG0		0x10232103U
#define CAMSS_E004NR_REAR_IPP_CFG0		0x802b2000U
#define CAMSS_E004NR_REAR_IPP_CFG1		0x00007241U
#define CAMSS_E004NR_REAR_IPP_HCROP		0x0fdf0000U
#define CAMSS_E004NR_REAR_IPP_VCROP		0x08ed0000U
#define CAMSS_E004NR_REAR_IPP_FORMAT_MEASURE	0x08ee0fe0U

/* The same Windows CSID1/VFE1 physical cores serve the IMX681 front mode;
 * this rear mode must never share the live core with the front camera.
 * Not an active DMA/format contract: e.g. WM stride does NOT prove an NV12
 * V4L2 user buffer layout, UBWC metadata allocation or Linux IOMMU mapping.
 */
struct camss_e004nr_rear_pix_profile {
	u32 sensor_width;
	u32 sensor_height;
	u32 ipp_crop_width;
	u32 ipp_crop_height;
	u32 full_width;
	u32 full_y_height;
	u32 full_c_height;
	u32 full_wm_stride;
	u32 full_wm_packer_cfg;
	u32 full_y_frame_increment;
	u32 full_c_frame_increment;
	u32 full_metadata_config;
	u32 full_y_mode;
	u32 full_c_mode;
	u32 ds4_frame_increment;
	u32 ds16_frame_increment;
	u32 csid_rx_cfg0;
	u32 csid_ipp_cfg0;
	u32 csid_ipp_cfg1;
	u32 csid_ipp_hcrop;
	u32 csid_ipp_vcrop;
	u32 csid_ipp_format_measure;
	u8 csiphy_id;
	u8 csid_id;
	u8 vfe_id;
	u8 lane_count;
	u8 first_full_wm;
	u8 second_full_wm;
	bool dphy;
	bool linux_rear_4k_hardware_authorized;
};

static const struct camss_e004nr_rear_pix_profile
camss_e004nr_rear_oem_profile __used = {
	.sensor_width = CAMSS_E004NR_REAR_SENSOR_WIDTH,
	.sensor_height = CAMSS_E004NR_REAR_SENSOR_HEIGHT,
	.ipp_crop_width = CAMSS_E004NR_REAR_IPP_CROP_WIDTH,
	.ipp_crop_height = CAMSS_E004NR_REAR_IPP_CROP_HEIGHT,
	.full_width = CAMSS_E004NR_REAR_FULL_WIDTH,
	.full_y_height = CAMSS_E004NR_REAR_FULL_Y_HEIGHT,
	.full_c_height = CAMSS_E004NR_REAR_FULL_C_HEIGHT,
	.full_wm_stride = CAMSS_E004NR_REAR_FULL_WM_STRIDE,
	.full_wm_packer_cfg = CAMSS_E004NR_REAR_FULL_PACKER_CFG,
	.full_y_frame_increment = CAMSS_E004NR_REAR_FULL_Y_FRAME_INCR,
	.full_c_frame_increment = CAMSS_E004NR_REAR_FULL_C_FRAME_INCR,
	.full_metadata_config = CAMSS_E004NR_REAR_FULL_META_CFG,
	.full_y_mode = CAMSS_E004NR_REAR_FULL_Y_MODE,
	.full_c_mode = CAMSS_E004NR_REAR_FULL_C_MODE,
	.ds4_frame_increment = CAMSS_E004NR_REAR_DS4_FRAME_INCR,
	.ds16_frame_increment = CAMSS_E004NR_REAR_DS16_FRAME_INCR,
	.csid_rx_cfg0 = CAMSS_E004NR_REAR_RX_CFG0,
	.csid_ipp_cfg0 = CAMSS_E004NR_REAR_IPP_CFG0,
	.csid_ipp_cfg1 = CAMSS_E004NR_REAR_IPP_CFG1,
	.csid_ipp_hcrop = CAMSS_E004NR_REAR_IPP_HCROP,
	.csid_ipp_vcrop = CAMSS_E004NR_REAR_IPP_VCROP,
	.csid_ipp_format_measure = CAMSS_E004NR_REAR_IPP_FORMAT_MEASURE,
	.csiphy_id = 1,
	.csid_id = 1,
	.vfe_id = 1,
	.lane_count = 4,
	.first_full_wm = 0,
	.second_full_wm = 1,
	.dphy = true,
	.linux_rear_4k_hardware_authorized = false,
};

/* Existing Linux OV13858 mode0 exposes the full 4076x2806 CSI2 RAW10
 * frame on the media pads. Windows' 4064x2286 crop is programmed at
 * CSID1 IPP INSIDE the sensor frame, NOT a made-up 3840x2160 sensor pad.
 * The 0,0 origin keeps GRBG phase unchanged.
 *
 * Fail closed on wrong sensor, PHY, CSI, VFE, conflicting front links,
 * Bayer code, or absent media-entity links. This function is intentionally
 * NOT used by any runtime ioctl, probe, streaming callback or sysfs path.
 */
static int __used
camss_e004nr_rear_pix_graph_preflight(struct camss *camss,
				     struct v4l2_subdev *sensor)
{
	struct csiphy_device *csiphy;
	struct csid_device *csid;
	struct vfe_device *vfe;
	struct media_pad *pad;

	if (!camss || !sensor || !camss->res ||
	    camss->res->version != CAMSS_X1E80100 ||
	    camss->res->csiphy_num <= 2 ||
	    camss->res->csid_num <= 1 ||
	    camss->res->vfe_num <= 1)
		return -EINVAL;

	csiphy = &camss->csiphy[1];
	csid = &camss->csid[1];
	vfe = &camss->vfe[1];
	if (csiphy->id != 1 || csid->id != 1 || vfe->id != 1 ||
	    vfe->res->is_lite ||
	    sensor->entity.function != MEDIA_ENT_F_CAM_SENSOR ||
	    sensor->host_priv != csiphy)
		return -EINVAL;
	if (csid->phy.csiphy_id != 1 ||
	    csid->phy.phy_sel != CSID_PHY_SEL_DPHY ||
	    csid->phy.lane_cnt != 4 || !csid->phy.en_ipp)
		return -EINVAL;

	if (csid->fmt[MSM_CSID_PAD_PIX].code !=
			MEDIA_BUS_FMT_SGRBG10_1X10 ||
	    csid->fmt[MSM_CSID_PAD_PIX].width !=
			CAMSS_E004NR_REAR_SENSOR_WIDTH ||
	    csid->fmt[MSM_CSID_PAD_PIX].height !=
			CAMSS_E004NR_REAR_SENSOR_HEIGHT ||
	    vfe->line[VFE_LINE_PIX].fmt[MSM_VFE_PAD_SINK].code !=
			MEDIA_BUS_FMT_SGRBG10_1X10)
		return -EINVAL;

	pad = media_pad_remote_pad_first(&csiphy->pads[MSM_CSIPHY_PAD_SINK]);
	if (!pad || pad->entity != &sensor->entity)
		return -ENOLINK;
	if (!camss_x1e_pix_link(&csiphy->pads[MSM_CSIPHY_PAD_SRC],
				&csid->subdev.entity, MSM_CSID_PAD_SINK) ||
	    !camss_x1e_pix_link(&csid->pads[MSM_CSID_PAD_SINK],
				&csiphy->subdev.entity, MSM_CSIPHY_PAD_SRC) ||
	    !camss_x1e_pix_link(&csid->pads[MSM_CSID_PAD_PIX],
				&vfe->line[VFE_LINE_PIX].subdev.entity,
				MSM_VFE_PAD_SINK) ||
	    !camss_x1e_pix_link(&vfe->line[VFE_LINE_PIX].pads[MSM_VFE_PAD_SINK],
				&csid->subdev.entity, MSM_CSID_PAD_PIX) ||
	    !camss_x1e_pix_link(&vfe->line[VFE_LINE_PIX].pads[MSM_VFE_PAD_SRC],
				&vfe->line[VFE_LINE_PIX].video_out.vdev.entity,
				0))
		return -ENOLINK;

	return 0; /* ONLY identity and graph; no hardware start authorized. */
}

/* Separate opt-in must remain fail-closed until independent Linux rear
 * IQ/3A, actual 4K DMA/UBWC allocation, CSID1 mode selector, RT-CDM and
 * exclusive front/rear core ownership are implemented and validated.
 */
static int __used
camss_e004nr_rear_pix_runtime_authorization(struct camss *camss,
					    struct v4l2_subdev *sensor)
{
	int ret = camss_e004nr_rear_pix_graph_preflight(camss, sensor);

	if (ret)
		return ret;

	return -EOPNOTSUPP;
}
#endif /* CAMSS_E004NR_REAR_PROFILE_INC */
