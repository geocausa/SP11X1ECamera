// SPDX-License-Identifier: GPL-2.0
#include <linux/device.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <media/v4l2-subdev.h>
#include <media/v4l2-mediabus.h>

static char *client_name;
module_param(client_name, charp, 0444);
MODULE_PARM_DESC(client_name, "Bound IMX681 I2C client name, e.g. 5-0010");

static int __init e003e_test_init(void)
{
	struct device *dev;
	struct i2c_client *client;
	struct v4l2_subdev *sd;
	struct v4l2_mbus_config cfg = {};
	int mbus_ret, stream_ret;

	if (!client_name)
		return -EINVAL;
	dev = bus_find_device_by_name(&i2c_bus_type, NULL, client_name);
	if (!dev)
		return -ENODEV;
	client = to_i2c_client(dev);
	sd = i2c_get_clientdata(client);
	if (!sd) {
		put_device(dev);
		return -ENODEV;
	}
	mbus_ret = v4l2_subdev_call(sd, pad, get_mbus_config, 0, &cfg);
	pr_info("E003E_MBUS_TEST: ret=%d type=%u link_freq=%llu trios=%u data0=%u order0=%u\n",
		mbus_ret, cfg.type, cfg.link_freq,
		cfg.bus.mipi_csi2.num_data_lanes,
		cfg.bus.mipi_csi2.data_lanes[0],
		cfg.bus.mipi_csi2.line_orders[0]);
	stream_ret = v4l2_subdev_call(sd, video, s_stream, 1);
	pr_info("E003E_STREAM_BLOCK_TEST: s_stream(1) ret=%d expected=%d\n",
		stream_ret, -EOPNOTSUPP);
	put_device(dev);

	if (mbus_ret || cfg.type != V4L2_MBUS_CSI2_CPHY ||
	    cfg.link_freq != 1200000000ULL ||
	    cfg.bus.mipi_csi2.num_data_lanes != 1 ||
	    cfg.bus.mipi_csi2.data_lanes[0] != 0 ||
	    cfg.bus.mipi_csi2.line_orders[0] != V4L2_MBUS_CSI2_CPHY_LINE_ORDER_ABC ||
	    stream_ret != -EOPNOTSUPP)
		return -EINVAL;
	return 0;
}
static void __exit e003e_test_exit(void) {}
module_init(e003e_test_init);
module_exit(e003e_test_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("SP11 E003e C-PHY mbus and direct stream-block verifier");
