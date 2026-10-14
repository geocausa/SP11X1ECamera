// SPDX-License-Identifier: GPL-2.0-only
/* Lab-only read-only observer; never modifies PM, queues, registers or DMA. */
#include <linux/device.h>
#include <linux/io.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/platform_device.h>

#include "camss.h"
#include "camss-csid.h"
#include "camss-vfe.h"

/* Exact FULL RDI0 CFG definition retained in the pinned Linaro VFE680 source. */
#define FULL_RDI0_WM_CFG (0xe00 + 24 * 0x100)

static bool execute;
module_param(execute, bool, 0400);
static int result;
module_param(result, int, 0400);
static unsigned int active;
module_param(active, uint, 0400);
static bool paused;
module_param(paused, bool, 0400);
static unsigned int wm_cfg;
module_param(wm_cfg, uint, 0400);

static int read_snapshot(struct camss *camss)
{
	struct camss_video *video;
	struct vfe_device *vfe;
	struct vfe_line *line;
	struct vfe_output *output;
	struct csid_device *csid;
	unsigned long flags;
	int ret = -EINVAL;

	if (!camss || !camss->res ||
	    camss->res->version != CAMSS_X1E80100 ||
	    camss->res->vfe_num <= 1 || camss->res->csid_num <= 1 ||
	    !camss->vfe || !camss->csid)
		return -ENODEV;

	vfe = &camss->vfe[1];
	csid = &camss->csid[1];
	line = &vfe->line[0];
	output = &line->output[0];
	video = &output->video_out;
	mutex_lock(&camss->stream_guard);
	mutex_lock(&vfe->stream_lock);
	spin_lock_irqsave(&vfe->output_lock, flags);
	if (vfe->camss != camss || vfe->id != 1 || !vfe->base ||
	    vfe->power_count <= 0 || vfe->stream_count != 1 ||
	    line->is_pix || line->num_outputs != 1 ||
	    READ_ONCE(camss->stream_owner) != video ||
	    READ_ONCE(camss->stream_fault) ||
	    !video->module_held || !video->pm_held || !video->pipeline_started ||
	    READ_ONCE(video->lifecycle.fault) ||
	    video->vb2_q.memory != VB2_MEMORY_MMAP ||
	    csid->phy.csiphy_id != 2 || csid->phy.en_vc != BIT(0) ||
	    !csid->stream_owned || csid->stream_owner != video ||
	    csid->stream_fault || csid->stream_quiesced ||
	    output->wm_num != 1 || output->wm[0].bus_client != 24)
		goto out;

	active = output->gen2.active_num;
	paused = output->gen2.wm_stopped;
	if (output->state != VFE_OUTPUT_ON || active || !paused ||
	    output->buf[0] || output->buf[1] || output->last_buffer ||
	    !list_empty(&output->pending_bufs)) {
		ret = -EBUSY;
		goto out;
	}

	/* Owned active pipeline keeps the FULL VFE clocks/domain available. */
	wm_cfg = readl(vfe->base + FULL_RDI0_WM_CFG);
	ret = wm_cfg ? -EBUSY : 1;
out:
	spin_unlock_irqrestore(&vfe->output_lock, flags);
	mutex_unlock(&vfe->stream_lock);
	mutex_unlock(&camss->stream_guard);
	return ret;
}

static int match_device(struct device *dev, const void *unused)
{
	return of_device_is_compatible(dev->of_node, "qcom,x1e80100-camss");
}

static int __init sp11_rdi_idle_probe_init(void)
{
	struct device *dev;
	struct module *owner;

	if (!execute)
		return -EPERM;
	dev = bus_find_device(&platform_bus_type, NULL, NULL, match_device);
	if (!dev)
		return -ENODEV;

	device_lock(dev);
	if (!dev->driver || strcmp(dev->driver->name, "qcom-camss")) {
		result = -ENODEV;
		goto unlock;
	}
	owner = dev->driver->owner;
	if (!try_module_get(owner)) {
		result = -ENODEV;
		goto unlock;
	}
	result = read_snapshot(dev_get_drvdata(dev));
	module_put(owner);
unlock:
	device_unlock(dev);
	put_device(dev);
	pr_info("SP11_RDI_IDLE_PROBE result=%d active=%u paused=%u wm_cfg=%u\n",
		result, active, paused, wm_cfg);
	return 0;
}

static void __exit sp11_rdi_idle_probe_exit(void)
{
	/* No retained device, PM, DMA, register or camera-module ownership. */
}
module_init(sp11_rdi_idle_probe_init);
module_exit(sp11_rdi_idle_probe_exit);
MODULE_DESCRIPTION("Read-only bounded SP11 owned RDI starvation observer");
MODULE_LICENSE("GPL v2");
