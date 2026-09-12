// SPDX-License-Identifier: GPL-2.0
#include <linux/device.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/of.h>
#include <media/v4l2-ctrls.h>
#include <media/v4l2-subdev.h>

#define E004S_COMPAT "microsoft,sp11-vd55g0"
#define E004S_ADDR 0x60

static int __init e004s_test_init(void)
{
	struct v4l2_mbus_config cfg = {};
	struct v4l2_ctrl *link, *pixel, *hblank, *vblank;
	struct device_node *np;
	struct device *dev;
	struct i2c_client *client;
	struct v4l2_subdev *sd;
	s64 link_val, pixel_val;
	s32 link_idx, hblank_val, vblank_val;
	int cfg_ret, stream_ret;

	np = of_find_compatible_node(NULL, NULL, E004S_COMPAT);
	if (!np)
		return -ENODEV;

	dev = bus_find_device_by_of_node(&i2c_bus_type, np);
	of_node_put(np);
	if (!dev)
		return -EPROBE_DEFER;

	client = to_i2c_client(dev);
	if (client->addr != E004S_ADDR) {
		put_device(dev);
		return -ENODEV;
	}

	sd = i2c_get_clientdata(client);
	if (!sd || !sd->ctrl_handler) {
		put_device(dev);
		return -ENODEV;
	}

	pr_info("E004S_DEVICE_IDENTITY: dev=%s addr=0x%02x compatible=%s\n",
		dev_name(dev), client->addr, E004S_COMPAT);

	link = v4l2_ctrl_find(sd->ctrl_handler, V4L2_CID_LINK_FREQ);
	pixel = v4l2_ctrl_find(sd->ctrl_handler, V4L2_CID_PIXEL_RATE);
	hblank = v4l2_ctrl_find(sd->ctrl_handler, V4L2_CID_HBLANK);
	vblank = v4l2_ctrl_find(sd->ctrl_handler, V4L2_CID_VBLANK);
	if (!link || !pixel || !hblank || !vblank) {
		put_device(dev);
		return -ENOENT;
	}

	if (link->type != V4L2_CTRL_TYPE_INTEGER_MENU || !link->qmenu_int) {
		put_device(dev);
		return -EINVAL;
	}

	link_idx = v4l2_ctrl_g_ctrl(link);
	if (link_idx < link->minimum || link_idx > link->maximum) {
		put_device(dev);
		return -ERANGE;
	}
	link_val = link->qmenu_int[link_idx];
	pixel_val = v4l2_ctrl_g_ctrl_int64(pixel);
	hblank_val = v4l2_ctrl_g_ctrl(hblank);
	vblank_val = v4l2_ctrl_g_ctrl(vblank);

	cfg_ret = v4l2_subdev_call(sd, pad, get_mbus_config, 0, &cfg);
	pr_info("E004S_V4L2_CONTRACT: link_idx=%d link_freq=%lld pixel_rate=%lld hblank=%d vblank=%d mbus_ret=%d type=%u lanes=%u mbus_link_freq=%lld\n",
		link_idx, (long long)link_val, (long long)pixel_val,
		hblank_val, vblank_val, cfg_ret, cfg.type,
		cfg.bus.mipi_csi2.num_data_lanes, (long long)cfg.link_freq);

	stream_ret = v4l2_subdev_call(sd, video, s_stream, 1);
	pr_info("E004S_STREAM_BLOCK_TEST: s_stream(1) ret=%d expected=%d\n",
		stream_ret, -EOPNOTSUPP);

	put_device(dev);

	if (link_idx != 0 ||
	    link_val != 420000000LL ||
	    pixel_val != 84000000LL ||
	    hblank_val != 556 ||
	    vblank_val != 1351 ||
	    cfg_ret ||
	    cfg.type != V4L2_MBUS_CSI2_DPHY ||
	    cfg.bus.mipi_csi2.num_data_lanes != 1 ||
	    cfg.link_freq != 420000000LL ||
	    stream_ret != -EOPNOTSUPP)
		return -EINVAL;

	return 0;
}

static void __exit e004s_test_exit(void) {}

module_init(e004s_test_init);
module_exit(e004s_test_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("SP11 E004s dynamic-identity VD55G0 V4L2 contract + stream-block verifier");
