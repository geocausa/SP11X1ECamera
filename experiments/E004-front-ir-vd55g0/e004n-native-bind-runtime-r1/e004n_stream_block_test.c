// SPDX-License-Identifier: GPL-2.0
#include <linux/device.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <media/v4l2-ctrls.h>
#include <media/v4l2-subdev.h>

static int __init e004n_test_init(void)
{
	struct v4l2_mbus_config cfg = {};
	struct v4l2_ctrl *link, *pixel, *hblank, *vblank;
	struct device *dev;
	struct i2c_client *client;
	struct v4l2_subdev *sd;
	s64 link_val, pixel_val, hblank_val, vblank_val;
	int cfg_ret, stream_ret;

	dev = bus_find_device_by_name(&i2c_bus_type, NULL, "2-0060");
	if (!dev)
		return -ENODEV;

	client = to_i2c_client(dev);
	sd = i2c_get_clientdata(client);
	if (!sd || !sd->ctrl_handler) {
		put_device(dev);
		return -ENODEV;
	}

	link = v4l2_ctrl_find(sd->ctrl_handler, V4L2_CID_LINK_FREQ);
	pixel = v4l2_ctrl_find(sd->ctrl_handler, V4L2_CID_PIXEL_RATE);
	hblank = v4l2_ctrl_find(sd->ctrl_handler, V4L2_CID_HBLANK);
	vblank = v4l2_ctrl_find(sd->ctrl_handler, V4L2_CID_VBLANK);
	if (!link || !pixel || !hblank || !vblank) {
		put_device(dev);
		return -ENOENT;
	}

	link_val = v4l2_ctrl_g_ctrl_int64(link);
	pixel_val = v4l2_ctrl_g_ctrl_int64(pixel);
	hblank_val = v4l2_ctrl_g_ctrl_int64(hblank);
	vblank_val = v4l2_ctrl_g_ctrl_int64(vblank);

	cfg_ret = v4l2_subdev_call(sd, pad, get_mbus_config, 0, &cfg);
	pr_info("E004N_V4L2_CONTRACT: link_freq=%lld pixel_rate=%lld hblank=%lld vblank=%lld mbus_ret=%d type=%u lanes=%u mbus_link_freq=%lld\n",
		(long long)link_val, (long long)pixel_val,
		(long long)hblank_val, (long long)vblank_val,
		cfg_ret, cfg.type, cfg.bus.mipi_csi2.num_data_lanes,
		(long long)cfg.link_freq);

	stream_ret = v4l2_subdev_call(sd, video, s_stream, 1);
	pr_info("E004N_STREAM_BLOCK_TEST: s_stream(1) ret=%d expected=%d\n",
		stream_ret, -EOPNOTSUPP);

	put_device(dev);

	if (link_val != 420000000LL ||
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

static void __exit e004n_test_exit(void) {}

module_init(e004n_test_init);
module_exit(e004n_test_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("SP11 E004n VD55G0 V4L2 contract + direct s_stream block verifier");
