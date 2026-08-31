// SPDX-License-Identifier: GPL-2.0
/*
 * Sony IMX681 Windows-selected mode2 V4L2 sensor driver for SP11 E003h.
 *
 * V4L2 structure follows the public linux-surface IMX681 RFC lineage
 * (linux-surface/kernel PRs #164/#176).  SP11 X1E power, identity and mode
 * metadata come from this machine's independently decoded Windows oracle.
 *
 * E003h bounded runtime diagnostic: the same-machine Windows init +
 * 3840x2160@30 mode2 tables are re-applied after every runtime resume, then
 * MODE_SELECT is toggled only for an explicitly requested stream. This copy is
 * for a disposable one-shot boot; accepted E003e standby source is untouched.
 */

#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/pm_runtime.h>
#include <linux/regulator/consumer.h>

#include <media/v4l2-cci.h>
#include <media/v4l2-device.h>
#include <media/v4l2-mediabus.h>

#define IMX681_REG_WINDOWS_ID	CCI_REG16(0x0004)
#define IMX681_WINDOWS_ID	0x0aff
#define IMX681_REG_SONY_ID	CCI_REG16(0x0016)
#define IMX681_SONY_ID		0x0681
#define IMX681_XCLK_HZ		19200000UL
#define IMX681_PAD_SOURCE	0
#define IMX681_REG_MODE_SELECT	CCI_REG8(0x0100)
#define IMX681_MODE_STANDBY	0x00
#define IMX681_MODE_STREAMING	0x01
#define IMX681_CPHY_TRIOS	1
/* Windows mode2 PLL2: 19.2 MHz * 0x177 / 3 = 2.400 GHz symbol rate.
 * V4L2 CSI-2 C-PHY link frequency is half the operating symbol rate. */
#define IMX681_CPHY_SYMBOL_RATE_HZ 2400000000ULL
#define IMX681_CPHY_LINK_FREQ_HZ   1200000000ULL

struct imx681_mode {
	u32 width;
	u32 height;
	u32 line_length;
	u32 frame_length;
	u32 pixel_rate;
	u32 fps;
};

/* Same-machine Windows Camera proves resolution record 2; expose only that proven mode. */
static const struct imx681_mode imx681_modes[] = {
	{ 3840, 2160, 6752, 3554, 548570000, 30 },
};

#include "imx681-sp11-mode2-regs.h"

struct imx681 {
	struct device *dev;
	struct regmap *cci;
	struct v4l2_subdev sd;
	struct media_pad pad;
	struct clk *xclk;
	struct regulator *dovdd;
	struct regulator *avdd;
	struct gpio_desc *reset;
};

static inline struct imx681 *to_imx681(struct v4l2_subdev *sd)
{
	return container_of_const(sd, struct imx681, sd);
}

static int imx681_power_on(struct device *dev)
{
	struct v4l2_subdev *sd = dev_get_drvdata(dev);
	struct imx681 *imx681 = to_imx681(sd);
	int ret;

	/* Windows D0: reset low -> MCLK4 -> LDO3_M -> LDO7_B -> 1ms -> reset high -> 10ms. */
	gpiod_set_value_cansleep(imx681->reset, 1);

	ret = clk_set_rate(imx681->xclk, IMX681_XCLK_HZ);
	if (ret)
		return ret;
	ret = clk_prepare_enable(imx681->xclk);
	if (ret)
		return ret;

	ret = regulator_enable(imx681->dovdd);
	if (ret)
		goto err_clk;
	ret = regulator_enable(imx681->avdd);
	if (ret)
		goto err_dovdd;

	usleep_range(1000, 1500);
	gpiod_set_value_cansleep(imx681->reset, 0);
	usleep_range(10000, 11000);
	dev_info(imx681->dev, "SP11 E003c: runtime power-on complete\n");
	return 0;

err_dovdd:
	regulator_disable(imx681->dovdd);
err_clk:
	clk_disable_unprepare(imx681->xclk);
	return ret;
}

static int imx681_power_off(struct device *dev)
{
	struct v4l2_subdev *sd = dev_get_drvdata(dev);
	struct imx681 *imx681 = to_imx681(sd);

	/* Windows D3 reverse lifecycle. */
	gpiod_set_value_cansleep(imx681->reset, 1);
	usleep_range(1000, 1500);
	clk_disable_unprepare(imx681->xclk);
	regulator_disable(imx681->avdd);
	regulator_disable(imx681->dovdd);
	dev_info(imx681->dev, "SP11 E003c: runtime power-off complete\n");
	return 0;
}

static int imx681_identify(struct imx681 *imx681)
{
	u64 windows_id, sony_id;
	int ret;

	ret = cci_read(imx681->cci, IMX681_REG_WINDOWS_ID, &windows_id, NULL);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "read Windows identity failed\n");
	if (windows_id != IMX681_WINDOWS_ID)
		return dev_err_probe(imx681->dev, -ENODEV,
				     "Windows identity mismatch 0x%04llx != 0x%04x\n",
				     windows_id, IMX681_WINDOWS_ID);

	ret = cci_read(imx681->cci, IMX681_REG_SONY_ID, &sony_id, NULL);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "read Sony identity failed\n");
	if (sony_id != IMX681_SONY_ID)
		return dev_err_probe(imx681->dev, -ENODEV,
				     "Sony identity mismatch 0x%04llx != 0x%04x\n",
				     sony_id, IMX681_SONY_ID);

	dev_info(imx681->dev,
		 "SP11 E003c PASS: IMX681 Windows ID 0x%04llx, Sony ID 0x%04llx\n",
		 windows_id, sony_id);
	return 0;
}

static int imx681_expect(struct imx681 *imx681, u32 reg, u64 expected,
			 const char *name)
{
	u64 val;
	int ret;

	ret = cci_read(imx681->cci, reg, &val, NULL);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "readback %s failed\n", name);
	if (val != expected)
		return dev_err_probe(imx681->dev, -EIO,
				     "readback %s mismatch 0x%llx != 0x%llx\n",
				     name, val, expected);
	return 0;
}

static int imx681_program_mode2_standby(struct imx681 *imx681)
{
	u64 mode_select;
	int ret;

	ret = cci_read(imx681->cci, IMX681_REG_MODE_SELECT, &mode_select, NULL);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "pre-program MODE_SELECT read failed\n");
	if (mode_select != IMX681_MODE_STANDBY)
		return dev_err_probe(imx681->dev, -EBUSY,
				     "refuse programming: MODE_SELECT is 0x%02llx, not standby\n",
				     mode_select);

	ret = cci_multi_reg_write(imx681->cci, imx681_sp11_init_regs,
				  ARRAY_SIZE(imx681_sp11_init_regs), NULL);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "Windows init table write failed\n");
	ret = cci_multi_reg_write(imx681->cci, imx681_sp11_mode2_regs,
				  ARRAY_SIZE(imx681_sp11_mode2_regs), NULL);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "Windows mode2 table write failed\n");

	/* The gate is successful only if the sensor never left software standby. */
	ret = imx681_expect(imx681, IMX681_REG_MODE_SELECT, IMX681_MODE_STANDBY,
			    "MODE_SELECT");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG8(0x0111), 0x03, "CSI signaling C-PHY");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG16(0x0112), 0x0a0a, "RAW10 format");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG8(0x0114), 0x00, "one-trio lane mode");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG16(0x0342), 0x1a60, "line length 6752");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG24(0x033d), 0x000de2, "frame length 3554");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG16(0x0344), 0x0068, "crop X start 104");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG16(0x0346), 0x01f0, "crop Y start 496");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG32(0x034c), 0x0f000870,
			    "output 3840x2160");
	if (ret)
		return ret;
	ret = imx681_expect(imx681, CCI_REG24(0x030d), 0x030177, "PLL2 3/375");
	if (ret)
		return ret;

	dev_info(imx681->dev,
		 "SP11 E003h PASS: Windows init=%zu + selected mode2=%zu programmed in standby; MODE_SELECT=0; C-PHY symbol=2400MHz link=1200MHz\n",
		 ARRAY_SIZE(imx681_sp11_init_regs), ARRAY_SIZE(imx681_sp11_mode2_regs));
	return 0;
}

static int imx681_get_mbus_config(struct v4l2_subdev *sd, unsigned int pad,
				  struct v4l2_mbus_config *cfg)
{
	if (pad != IMX681_PAD_SOURCE)
		return -EINVAL;

	cfg->type = V4L2_MBUS_CSI2_CPHY;
	cfg->link_freq = IMX681_CPHY_LINK_FREQ_HZ;
	cfg->bus.mipi_csi2.num_data_lanes = IMX681_CPHY_TRIOS;
	cfg->bus.mipi_csi2.data_lanes[0] = 0;
	cfg->bus.mipi_csi2.line_orders[0] = V4L2_MBUS_CSI2_CPHY_LINE_ORDER_ABC;
	return 0;
}

static int imx681_enum_mbus_code(struct v4l2_subdev *sd,
				 struct v4l2_subdev_state *state,
				 struct v4l2_subdev_mbus_code_enum *code)
{
	if (code->index)
		return -EINVAL;

	/* Native IMX681 CFA is RGGB; E003c performs no orientation write. */
	code->code = MEDIA_BUS_FMT_SRGGB10_1X10;
	return 0;
}

static int imx681_enum_frame_size(struct v4l2_subdev *sd,
				  struct v4l2_subdev_state *state,
				  struct v4l2_subdev_frame_size_enum *fse)
{
	const struct imx681_mode *mode;

	if (fse->code != MEDIA_BUS_FMT_SRGGB10_1X10 ||
	    fse->index >= ARRAY_SIZE(imx681_modes))
		return -EINVAL;
	mode = &imx681_modes[fse->index];
	fse->min_width = mode->width;
	fse->max_width = mode->width;
	fse->min_height = mode->height;
	fse->max_height = mode->height;
	return 0;
}

static const struct imx681_mode *imx681_nearest_mode(u32 width, u32 height)
{
	const struct imx681_mode *best = &imx681_modes[0];
	u64 best_delta = U64_MAX;
	unsigned int i;

	for (i = 0; i < ARRAY_SIZE(imx681_modes); i++) {
		u64 dw = abs((s64)imx681_modes[i].width - width);
		u64 dh = abs((s64)imx681_modes[i].height - height);
		u64 delta = dw + dh;

		if (delta < best_delta) {
			best_delta = delta;
			best = &imx681_modes[i];
		}
	}
	return best;
}

static void imx681_fill_format(struct v4l2_mbus_framefmt *fmt,
			       const struct imx681_mode *mode)
{
	fmt->width = mode->width;
	fmt->height = mode->height;
	fmt->code = MEDIA_BUS_FMT_SRGGB10_1X10;
	fmt->field = V4L2_FIELD_NONE;
	fmt->colorspace = V4L2_COLORSPACE_RAW;
	fmt->ycbcr_enc = V4L2_YCBCR_ENC_601;
	fmt->quantization = V4L2_QUANTIZATION_FULL_RANGE;
	fmt->xfer_func = V4L2_XFER_FUNC_NONE;
}

static int imx681_init_state(struct v4l2_subdev *sd,
			     struct v4l2_subdev_state *state)
{
	imx681_fill_format(v4l2_subdev_state_get_format(state, IMX681_PAD_SOURCE),
			   &imx681_modes[0]);
	return 0;
}

static int imx681_set_fmt(struct v4l2_subdev *sd,
			  struct v4l2_subdev_state *state,
			  struct v4l2_subdev_format *fmt)
{
	const struct imx681_mode *mode = imx681_nearest_mode(fmt->format.width,
							     fmt->format.height);
	struct v4l2_mbus_framefmt *state_fmt;

	imx681_fill_format(&fmt->format, mode);
	state_fmt = v4l2_subdev_state_get_format(state, fmt->pad);
	*state_fmt = fmt->format;
	return 0;
}

static int imx681_s_stream(struct v4l2_subdev *sd, int enable)
{
	struct imx681 *imx681 = to_imx681(sd);
	int ret;

	if (enable) {
		ret = pm_runtime_resume_and_get(imx681->dev);
		if (ret < 0)
			return ret;

		/* Runtime power collapse loses sensor programming: restore verified mode. */
		ret = imx681_program_mode2_standby(imx681);
		if (ret)
			goto err_pm;

		ret = cci_write(imx681->cci, IMX681_REG_MODE_SELECT,
				IMX681_MODE_STREAMING, NULL);
		if (ret)
			goto err_pm;

		usleep_range(1000, 1500);
		dev_info(imx681->dev,
			 "SP11 E003h: MODE_SELECT=1 front transmission started\n");
		return 0;
	err_pm:
		pm_runtime_put_sync(imx681->dev);
		return ret;
	}

	/* Stop transmission before allowing runtime power collapse. */
	ret = cci_write(imx681->cci, IMX681_REG_MODE_SELECT,
			IMX681_MODE_STANDBY, NULL);
	if (ret)
		dev_err(imx681->dev, "SP11 E003h: MODE_SELECT=0 failed: %d\n", ret);
	else
		dev_info(imx681->dev, "SP11 E003h: MODE_SELECT=0 front transmission stopped\n");
	pm_runtime_put_sync(imx681->dev);
	return ret;
}

static const struct v4l2_subdev_video_ops imx681_video_ops = {
	.s_stream = imx681_s_stream,
};

static const struct v4l2_subdev_pad_ops imx681_pad_ops = {
	.enum_mbus_code = imx681_enum_mbus_code,
	.enum_frame_size = imx681_enum_frame_size,
	.get_fmt = v4l2_subdev_get_fmt,
	.set_fmt = imx681_set_fmt,
	.get_mbus_config = imx681_get_mbus_config,
};

static const struct v4l2_subdev_ops imx681_subdev_ops = {
	.video = &imx681_video_ops,
	.pad = &imx681_pad_ops,
};

static const struct v4l2_subdev_internal_ops imx681_internal_ops = {
	.init_state = imx681_init_state,
};

static int imx681_probe(struct i2c_client *client)
{
	struct imx681 *imx681;
	int ret;

	imx681 = devm_kzalloc(&client->dev, sizeof(*imx681), GFP_KERNEL);
	if (!imx681)
		return -ENOMEM;
	imx681->dev = &client->dev;

	v4l2_i2c_subdev_init(&imx681->sd, client, &imx681_subdev_ops);
	imx681->cci = devm_cci_regmap_init_i2c(client, 16);
	if (IS_ERR(imx681->cci))
		return dev_err_probe(imx681->dev, PTR_ERR(imx681->cci),
				     "CCI regmap init failed\n");

	imx681->xclk = devm_clk_get(imx681->dev, "xclk");
	if (IS_ERR(imx681->xclk))
		return dev_err_probe(imx681->dev, PTR_ERR(imx681->xclk),
				     "get MCLK4 failed\n");
	imx681->dovdd = devm_regulator_get(imx681->dev, "dovdd");
	if (IS_ERR(imx681->dovdd))
		return dev_err_probe(imx681->dev, PTR_ERR(imx681->dovdd),
				     "get LDO3_M/dovdd failed\n");
	imx681->avdd = devm_regulator_get(imx681->dev, "avdd");
	if (IS_ERR(imx681->avdd))
		return dev_err_probe(imx681->dev, PTR_ERR(imx681->avdd),
				     "get LDO7_B/avdd failed\n");
	imx681->reset = devm_gpiod_get(imx681->dev, "reset", GPIOD_OUT_HIGH);
	if (IS_ERR(imx681->reset))
		return dev_err_probe(imx681->dev, PTR_ERR(imx681->reset),
				     "get GPIO237 reset failed\n");

	ret = regulator_set_voltage(imx681->dovdd, 1800000, 1800000);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "set dovdd 1.8 V failed\n");
	ret = regulator_set_voltage(imx681->avdd, 2800000, 2800000);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "set avdd 2.8 V failed\n");

	ret = imx681_power_on(imx681->dev);
	if (ret)
		return dev_err_probe(imx681->dev, ret, "power-on failed\n");
	ret = imx681_identify(imx681);
	if (ret)
		goto err_power;
	ret = imx681_program_mode2_standby(imx681);
	if (ret)
		goto err_power;

	imx681->sd.flags |= V4L2_SUBDEV_FL_HAS_DEVNODE;
	imx681->sd.entity.function = MEDIA_ENT_F_CAM_SENSOR;
	imx681->sd.internal_ops = &imx681_internal_ops;
	imx681->pad.flags = MEDIA_PAD_FL_SOURCE;
	ret = media_entity_pads_init(&imx681->sd.entity, 1, &imx681->pad);
	if (ret)
		goto err_power;
	ret = v4l2_subdev_init_finalize(&imx681->sd);
	if (ret)
		goto err_entity;
	ret = v4l2_async_register_subdev_sensor(&imx681->sd);
	if (ret)
		goto err_subdev;

	pm_runtime_set_active(imx681->dev);
	pm_runtime_enable(imx681->dev);
	pm_runtime_idle(imx681->dev);

	dev_info(imx681->dev,
		 "SP11 E003h bounded-runtime V4L2 bind complete; stream requests enabled only in disposable candidate\n");
	return 0;

err_subdev:
	v4l2_subdev_cleanup(&imx681->sd);
err_entity:
	media_entity_cleanup(&imx681->sd.entity);
err_power:
	imx681_power_off(imx681->dev);
	return ret;
}

static void imx681_remove(struct i2c_client *client)
{
	struct v4l2_subdev *sd = i2c_get_clientdata(client);
	struct imx681 *imx681 = to_imx681(sd);

	v4l2_async_unregister_subdev(sd);
	v4l2_subdev_cleanup(sd);
	media_entity_cleanup(&sd->entity);
	pm_runtime_disable(imx681->dev);
	if (!pm_runtime_status_suspended(imx681->dev))
		imx681_power_off(imx681->dev);
	pm_runtime_set_suspended(imx681->dev);
}

static DEFINE_RUNTIME_DEV_PM_OPS(imx681_pm_ops, imx681_power_off,
				 imx681_power_on, NULL);

static const struct of_device_id imx681_of_match[] = {
	{ .compatible = "sony,imx681" },
	{ }
};
MODULE_DEVICE_TABLE(of, imx681_of_match);

static const struct i2c_device_id imx681_i2c_ids[] = {
	{ "imx681" },
	{ }
};
MODULE_DEVICE_TABLE(i2c, imx681_i2c_ids);

static struct i2c_driver imx681_i2c_driver = {
	.driver = {
		.name = "imx681",
		.pm = pm_ptr(&imx681_pm_ops),
		.of_match_table = imx681_of_match,
	},
	.probe = imx681_probe,
	.remove = imx681_remove,
	.id_table = imx681_i2c_ids,
};
module_i2c_driver(imx681_i2c_driver);

MODULE_AUTHOR("SP11X1ECamera clean-room integration; V4L2 structure informed by linux-surface IMX681 RFC");
MODULE_DESCRIPTION("Sony IMX681 Windows-selected mode2 V4L2 sensor driver for SP11 E003h");
MODULE_LICENSE("GPL");
