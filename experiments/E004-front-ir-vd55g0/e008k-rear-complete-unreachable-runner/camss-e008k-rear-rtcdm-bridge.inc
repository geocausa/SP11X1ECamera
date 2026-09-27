/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008k cross-TU bridge. Included in camss.c after accepted front/RT-CDM
 * helper definitions. No call site is installed by this bridge.
 */
#ifndef CAMSS_E008K_REAR_RTCDM_BRIDGE_INC
#define CAMSS_E008K_REAR_RTCDM_BRIDGE_INC

#include "camss-e008k-rear-bridge.h"

int e008k_rear_validate_route(struct camss *camss, struct v4l2_subdev *sensor)
{
	struct media_pad *sensor_pad;
	struct csiphy_device *csiphy;
	struct csid_device *csid;
	struct vfe_device *vfe;

	if (!camss || !sensor || !camss->res ||
	    camss->res->version != CAMSS_X1E80100 ||
	    camss->res->vfe_num <= 1 || camss->res->csid_num <= 1 ||
	    camss->res->csiphy_num <= 1)
		return -EINVAL;

	vfe = &camss->vfe[1];
	csid = &camss->csid[1];
	csiphy = &camss->csiphy[1];
	if (vfe->id != 1 || vfe->res->is_lite || csid->id != 1 ||
	    csiphy->id != 1 || sensor->entity.function != MEDIA_ENT_F_CAM_SENSOR ||
	    sensor->host_priv != csiphy || !csid680_e008k_rear_mode0(csid))
		return -EINVAL;

	sensor_pad = media_pad_remote_pad_first(&csiphy->pads[MSM_CSIPHY_PAD_SINK]);
	if (!sensor_pad || sensor_pad->entity != &sensor->entity)
		return -ENOLINK;
	if (!camss_x1e_pix_link(&csiphy->pads[MSM_CSIPHY_PAD_SRC],
				&csid->subdev.entity, MSM_CSID_PAD_SINK))
		return -ENOLINK;
	if (!camss_x1e_pix_link(&csid->pads[MSM_CSID_PAD_PIX],
				&vfe->line[VFE_LINE_PIX].subdev.entity,
				MSM_VFE_PAD_SINK))
		return -ENOLINK;
	if (!camss_x1e_pix_link(&vfe->line[VFE_LINE_PIX].pads[MSM_VFE_PAD_SRC],
				&vfe->line[VFE_LINE_PIX].video_out.vdev.entity, 0))
		return -ENOLINK;
	return 0;
}

int e008k_rear_rtcdm_open_start(struct camss *camss)
{
	return camss_x1e_pix_rtcdm_open_start(camss);
}

int e008k_rear_rtcdm_submit_bl(struct camss *camss, u32 dma, u16 bytes)
{
	if (!camss || !dma || !bytes)
		return -EINVAL;
	return camss_rtcdm1_windows_fifo0_commit(camss, dma, bytes - 1);
}

void e008k_rear_rtcdm_stop_close(struct camss *camss)
{
	camss_x1e_pix_rtcdm_stop_close(camss);
}

bool e008k_rear_rtcdm_stopped(struct camss *camss)
{
	struct camss_rtcdm *rt;

	if (!camss || !camss->rtcdm1.present || !camss->rtcdm1.base)
		return false;
	rt = &camss->rtcdm1;
	mutex_lock(&rt->lock);
	{
		bool stopped = !READ_ONCE(rt->irq_armed) &&
			       readl(rt->base + CAMSS_RTCDM_IRQ0_MASK) == 0;
		mutex_unlock(&rt->lock);
		return stopped;
	}
}

int e008k_rear_subdev_stream(struct v4l2_subdev *sd, bool enable)
{
	return camss_x1e_pix_runner_stream(sd, enable);
}

int e008k_rear_pipeline_pm_get(struct media_entity *entity)
{
	return v4l2_pipeline_pm_get(entity);
}

void e008k_rear_pipeline_pm_put(struct media_entity *entity)
{
	v4l2_pipeline_pm_put(entity);
}

#endif
