// SPDX-License-Identifier: GPL-2.0
#include <linux/device.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <media/v4l2-subdev.h>

static int __init e003c_test_init(void)
{
	struct device *dev;
	struct i2c_client *client;
	struct v4l2_subdev *sd;
	int ret;

	dev = bus_find_device_by_name(&i2c_bus_type, NULL, "3-0010");
	if (!dev)
		return -ENODEV;
	client = to_i2c_client(dev);
	sd = i2c_get_clientdata(client);
	if (!sd) {
		put_device(dev);
		return -ENODEV;
	}
	ret = v4l2_subdev_call(sd, video, s_stream, 1);
	pr_info("E003C_STREAM_BLOCK_TEST: s_stream(1) ret=%d expected=%d\n",
		ret, -EOPNOTSUPP);
	put_device(dev);
	return ret == -EOPNOTSUPP ? 0 : -EINVAL;
}
static void __exit e003c_test_exit(void) {}
module_init(e003c_test_init);
module_exit(e003c_test_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("SP11 E003c direct V4L2 s_stream block verifier");
