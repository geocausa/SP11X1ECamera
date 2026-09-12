// SPDX-License-Identifier: GPL-2.0
#include <linux/device.h>
#include <linux/i2c.h>
#include <linux/io.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/pm_runtime.h>
#include <media/media-entity.h>
#include <media/v4l2-mediabus.h>
#include <media/v4l2-subdev.h>

#include "camss-csiphy.h"
#include "csiphy0-windows-expected.generated.h"

#define E004T_COMPAT "microsoft,sp11-vd55g0"
#define E004T_ADDR 0x60

static int __init e004t_test_init(void)
{
	struct v4l2_subdev_format fmt = {
		.which = V4L2_SUBDEV_FORMAT_ACTIVE,
		.pad = MSM_CSIPHY_PAD_SINK,
		.format = {
			.width = 644,
			.height = 604,
			.code = MEDIA_BUS_FMT_Y10_1X10,
			.field = V4L2_FIELD_NONE,
			.colorspace = V4L2_COLORSPACE_RAW,
		},
	};
	struct device_node *np;
	struct device *dev;
	struct i2c_client *client;
	struct v4l2_subdev *sensor_sd, *csiphy_sd;
	struct media_pad *remote, *downstream;
	struct csiphy_device *csiphy;
	unsigned int i, matches = 0, mismatches = 0;
	bool powered = false, receiver_on = false;
	int ret;

	np = of_find_compatible_node(NULL, NULL, E004T_COMPAT);
	if (!np)
		return -ENODEV;
	dev = bus_find_device_by_of_node(&i2c_bus_type, np);
	of_node_put(np);
	if (!dev)
		return -EPROBE_DEFER;

	client = to_i2c_client(dev);
	if (client->addr != E004T_ADDR) {
		ret = -ENODEV;
		goto out_put;
	}
	if (!pm_runtime_status_suspended(&client->dev)) {
		ret = -EBUSY;
		goto out_put;
	}

	sensor_sd = i2c_get_clientdata(client);
	if (!sensor_sd || sensor_sd->entity.num_pads != 1) {
		ret = -ENODEV;
		goto out_put;
	}

	remote = media_pad_remote_pad_first(&sensor_sd->entity.pads[0]);
	if (!remote || strcmp(remote->entity->name, "msm_csiphy0") ||
	    remote->index != MSM_CSIPHY_PAD_SINK) {
		ret = -ENOLINK;
		goto out_put;
	}

	csiphy_sd = media_entity_to_v4l2_subdev(remote->entity);
	csiphy = v4l2_get_subdevdata(csiphy_sd);
	if (!csiphy || csiphy->id != 0 || !csiphy->base ||
	    !csiphy->cfg.csi2 ||
	    csiphy->cfg.csi2->lane_cfg.phy_cfg != V4L2_MBUS_CSI2_DPHY ||
	    csiphy->cfg.csi2->lane_cfg.num_data != 1 ||
	    csiphy->cfg.csi2->lane_cfg.data[0].pos != 0) {
		ret = -EINVAL;
		goto out_put;
	}

	downstream = media_pad_remote_pad_first(&csiphy->pads[MSM_CSIPHY_PAD_SRC]);
	if (downstream) {
		ret = -EBUSY;
		goto out_put;
	}

	ret = v4l2_subdev_call(csiphy_sd, pad, set_fmt, NULL, &fmt);
	if (ret)
		goto out_put;
	if (fmt.format.code != MEDIA_BUS_FMT_Y10_1X10 ||
	    fmt.format.width != 644 || fmt.format.height != 604) {
		ret = -EINVAL;
		goto out_put;
	}

	pr_info("E004T_RECEIVER_PRECHECK: sensor=%s sensor_pm=suspended csiphy=%s id=%u phy=DPHY lanes=1 lane0_pos=0 downstream_link=none fmt=Y10_1X10/644x604\n",
		dev_name(dev), csiphy_sd->name, csiphy->id);

	ret = v4l2_subdev_call(csiphy_sd, core, s_power, 1);
	if (ret)
		goto out_put;
	powered = true;

	ret = v4l2_subdev_call(csiphy_sd, video, s_stream, 1);
	if (ret)
		goto out_cleanup;
	receiver_on = true;

	for (i = 0; i < ARRAY_SIZE(e004t_windows_csiphy0_expected); i++) {
		u32 got = readl_relaxed(csiphy->base +
				       e004t_windows_csiphy0_expected[i].offset);
		u32 expected = e004t_windows_csiphy0_expected[i].value;

		if (got == expected) {
			matches++;
		} else {
			mismatches++;
			pr_err("E004T_CSIPHY0_MISMATCH offset=0x%04x expected=0x%08x got=0x%08x\n",
			       e004t_windows_csiphy0_expected[i].offset,
			       expected, got);
		}
	}

	pr_info("E004T_CSIPHY0_READBACK: expected=96 matches=%u mismatches=%u timer_clk_rate=%u lane_mask_reg=0x%08x settle_lane0=0x%08x common_ctrl7=0x%08x\n",
		matches, mismatches, csiphy->timer_clk_rate,
		readl_relaxed(csiphy->base + 0x1014),
		readl_relaxed(csiphy->base + 0x0008),
		readl_relaxed(csiphy->base + 0x101c));

	ret = mismatches ? -EIO : 0;

out_cleanup:
	if (receiver_on)
		v4l2_subdev_call(csiphy_sd, video, s_stream, 0);
	if (powered)
		v4l2_subdev_call(csiphy_sd, core, s_power, 0);

	if (!pm_runtime_status_suspended(&client->dev)) {
		pr_err("E004T_SENSOR_PM_CHANGED: sensor=%s no_longer_suspended=1\n",
		       dev_name(dev));
		if (!ret)
			ret = -EBUSY;
	}

	pr_info("E004T_RECEIVER_END: result=%d receiver_off=1 csiphy_power_off=1 sensor_pm_suspended=%u sensor_stream_call=0 csid_stream_call=0 vfe_stream_call=0 illumination=0\n",
		ret, pm_runtime_status_suspended(&client->dev) ? 1 : 0);
out_put:
	put_device(dev);
	return ret;
}

static void __exit e004t_test_exit(void) {}

module_init(e004t_test_init);
module_exit(e004t_test_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("SP11 E004t receiver-only CSIPHY0 Windows-register readback verifier");
