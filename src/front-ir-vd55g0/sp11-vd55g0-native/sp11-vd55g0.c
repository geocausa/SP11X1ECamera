// SPDX-License-Identifier: GPL-2.0
/*
 * Surface Pro 11 VD55G0 native bind-only V4L2 sensor driver.
 *
 * Sensor programming authority: same-machine Surface Windows package/runtime.
 * V4L2 plumbing follows normal Linux sensor-driver patterns only.
 *
 * E004l safety boundary:
 *   - exact Windows Surface patch/setup/boot sequence;
 *   - exact final Windows sensor state reached with the proven safe-42 replay;
 *   - fixed 644x604 RAW10, 420 MHz D-PHY link, 84 MHz pixel rate;
 *   - software standby only;
 *   - .s_stream(1) is deliberately refused.
 */
#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/pm_runtime.h>
#include <linux/regulator/consumer.h>
#include <linux/string.h>

#include <media/v4l2-ctrls.h>
#include <media/v4l2-device.h>
#include <media/v4l2-mediabus.h>

#include "surface-windows.generated.h"

#define SP11_VD55G0_XCLK_HZ              19200000UL
#define SP11_VD55G0_LINK_FREQ_HZ        420000000LL
#define SP11_VD55G0_PIXEL_RATE_HZ        84000000LL
#define SP11_VD55G0_WIDTH                      644
#define SP11_VD55G0_HEIGHT                     604
#define SP11_VD55G0_LINE_LENGTH               1200
#define SP11_VD55G0_FRAME_LENGTH              1955
#define SP11_VD55G0_HBLANK  (SP11_VD55G0_LINE_LENGTH - SP11_VD55G0_WIDTH)
#define SP11_VD55G0_VBLANK  (SP11_VD55G0_FRAME_LENGTH - SP11_VD55G0_HEIGHT)

#define SP11_VCORE_UV                        1152000
#define SP11_VDDIO_UV                        1800000
#define SP11_VANA_UV                         2800000
#define SP11_SAFE_DELAY_US                      5000

#define VD55G0_REG_MODEL_ID                   0x0000
#define VD55G0_REG_REVISION                   0x0004
#define VD55G0_REG_SYSTEM_FSM                 0x002c
#define VD55G0_REG_BOOT                       0x0200
#define VD55G0_PATCH_START                    0x2000

#define VD55G0_FSM_READY_TO_BOOT                0x01
#define VD55G0_FSM_SW_STBY                       0x02
#define VD55G0_BOOT_PATCH_SETUP                  0x02
#define VD55G0_BOOT_BOOT                         0x01

struct sp11_vd55g0 {
	struct device *dev;
	struct i2c_client *client;
	struct v4l2_subdev sd;
	struct media_pad pad;
	struct v4l2_ctrl_handler ctrls;
	struct clk *xclk;
	struct gpio_desc *reset;
	struct regulator *vcore;
	struct regulator *vddio;
	struct regulator *vana;
	bool clock_on;
	bool vddio_on;
	bool vcore_on;
	bool vana_on;
	bool initialized;
};

static const s64 sp11_vd55g0_link_freq_menu[] = {
	SP11_VD55G0_LINK_FREQ_HZ,
};

static inline struct sp11_vd55g0 *to_sp11_vd55g0(struct v4l2_subdev *sd)
{
	return container_of_const(sd, struct sp11_vd55g0, sd);
}

static void sp11_safe_delay(void)
{
	usleep_range(SP11_SAFE_DELAY_US, SP11_SAFE_DELAY_US + 500);
}

static int sp11_read(struct sp11_vd55g0 *sensor, u16 reg, u8 *data, u16 len)
{
	struct i2c_client *client = sensor->client;
	u8 addr[2] = { reg >> 8, reg & 0xff };
	struct i2c_msg msgs[2] = {
		{
			.addr = client->addr,
			.flags = client->flags,
			.buf = addr,
			.len = sizeof(addr),
		},
		{
			.addr = client->addr,
			.flags = client->flags | I2C_M_RD,
			.buf = data,
			.len = len,
		},
	};
	int ret = i2c_transfer(client->adapter, msgs, ARRAY_SIZE(msgs));

	if (ret == ARRAY_SIZE(msgs))
		return 0;
	return ret >= 0 ? -EIO : ret;
}

/* Exact Windows transport shape: one 16-bit register + one 8-bit data byte. */
static int sp11_write8(struct sp11_vd55g0 *sensor, u16 reg, u8 data)
{
	struct i2c_client *client = sensor->client;
	u8 buf[3] = { reg >> 8, reg & 0xff, data };
	struct i2c_msg msg = {
		.addr = client->addr,
		.flags = client->flags,
		.buf = buf,
		.len = sizeof(buf),
	};
	int ret = i2c_transfer(client->adapter, &msg, 1);

	if (ret == 1)
		return 0;
	return ret >= 0 ? -EIO : ret;
}

static int sp11_poll8(struct sp11_vd55g0 *sensor, u16 reg, u8 expected,
		      unsigned int attempts, const char *name)
{
	u8 value = 0;
	unsigned int i;
	int ret;

	for (i = 0; i < attempts; i++) {
		ret = sp11_read(sensor, reg, &value, 1);
		if (ret)
			return ret;
		if (value == expected) {
			dev_info(sensor->dev,
				 "SP11_VD55G0_NATIVE_POLL name=%s reg=0x%04x expected=0x%02x timeout_ms=%u reads=%u result=PASS\n",
				 name, reg, expected, attempts, i + 1);
			return 0;
		}
		usleep_range(1000, 1100);
	}

	dev_err(sensor->dev,
		"SP11_VD55G0_NATIVE_POLL name=%s reg=0x%04x expected=0x%02x timeout_ms=%u last=0x%02x result=TIMEOUT\n",
		name, reg, expected, attempts, value);
	return -ETIMEDOUT;
}

static int sp11_expect_voltage(struct sp11_vd55g0 *sensor,
			       struct regulator *reg, const char *name,
			       int expected_uv)
{
	int uv = regulator_get_voltage(reg);

	if (uv < 0)
		return uv;
	dev_info(sensor->dev, "SP11_VD55G0_NATIVE_%s_uV=%d expected_uV=%d\n",
		 name, uv, expected_uv);
	return uv == expected_uv ? 0 : -ERANGE;
}

static void sp11_vd55g0_power_off_hw(struct sp11_vd55g0 *sensor)
{
	if (sensor->reset) {
		gpiod_set_value_cansleep(sensor->reset, 1);
		sp11_safe_delay();
	}
	if (sensor->vana_on) {
		regulator_disable(sensor->vana);
		sensor->vana_on = false;
		sp11_safe_delay();
	}
	if (sensor->vcore_on) {
		regulator_disable(sensor->vcore);
		sensor->vcore_on = false;
	}
	if (sensor->vddio_on) {
		regulator_disable(sensor->vddio);
		sensor->vddio_on = false;
	}
	if (sensor->clock_on) {
		clk_disable_unprepare(sensor->xclk);
		sensor->clock_on = false;
	}
	sensor->initialized = false;
	dev_info(sensor->dev,
		 "SP11_VD55G0_NATIVE_POWER_OFF reset_asserted=1 stream=0 illumination=0\n");
}

static int sp11_vd55g0_windows_init(struct sp11_vd55g0 *sensor)
{
	u8 model[2] = { 0 }, revision[2] = { 0 };
	u8 gpio_before = 0, gpio_after = 0;
	u8 transport[8] = { 0 }, timing[4] = { 0 }, exposure[6] = { 0 };
	u8 frame[2] = { 0 }, gpio_ctrl[4] = { 0 };
	u8 roi[8] = { 0 }, y_window[4] = { 0 }, pedestal = 0;
	unsigned int writes = 0;
	unsigned int i;
	int ret;

	ret = sp11_read(sensor, VD55G0_REG_MODEL_ID, model, 2);
	if (ret)
		return ret;
	ret = sp11_read(sensor, VD55G0_REG_REVISION, revision, 2);
	if (ret)
		return ret;

	dev_info(sensor->dev,
		 "SP11_VD55G0_NATIVE_ID model_raw=%02x,%02x model_be=0x%04x revision_raw=%02x,%02x revision=0x%04x\n",
		 model[0], model[1], ((u16)model[0] << 8) | model[1],
		 revision[0], revision[1],
		 ((u16)revision[0] << 8) | revision[1]);
	if (model[0] != 0x30 || model[1] != 0x47 ||
	    revision[0] != 0x11 || revision[1] != 0x11)
		return -ENODEV;

	dev_info(sensor->dev,
		 "SP11_VD55G0_NATIVE_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0\n");

	ret = sp11_poll8(sensor, VD55G0_REG_SYSTEM_FSM,
			 VD55G0_FSM_READY_TO_BOOT, 6, "READY_TO_BOOT");
	if (ret)
		return ret;

	dev_info(sensor->dev,
		 "SP11_VD55G0_NATIVE_PATCH_BEGIN start=0x2000 bytes=%u sha256=%s\n",
		 SP11_SURFACE_PATCH_SIZE, SP11_SURFACE_PATCH_SHA256);
	for (i = 0; i < SP11_SURFACE_PATCH_SIZE; i++) {
		ret = sp11_write8(sensor, VD55G0_PATCH_START + i,
				  sp11_surface_patch[i]);
		if (ret)
			return ret;
		writes++;
	}

	ret = sp11_write8(sensor, VD55G0_REG_BOOT, VD55G0_BOOT_PATCH_SETUP);
	if (ret)
		return ret;
	writes++;
	ret = sp11_poll8(sensor, VD55G0_REG_BOOT, 0x00, 28,
			 "PATCH_SETUP_COMPLETE");
	if (ret)
		return ret;

	ret = sp11_write8(sensor, VD55G0_REG_BOOT, VD55G0_BOOT_BOOT);
	if (ret)
		return ret;
	writes++;
	ret = sp11_poll8(sensor, VD55G0_REG_BOOT, 0x00, 6, "BOOT_COMPLETE");
	if (ret)
		return ret;
	ret = sp11_poll8(sensor, VD55G0_REG_SYSTEM_FSM,
			 VD55G0_FSM_SW_STBY, 4, "SW_STBY");
	if (ret)
		return ret;

	ret = sp11_read(sensor, SP11_WINDOWS_ISOLATED_STROBE_REG,
			&gpio_before, 1);
	if (ret)
		return ret;
	if (gpio_before != SP11_WINDOWS_ISOLATED_STROBE_VALUE) {
		dev_err(sensor->dev,
			"SP11_VD55G0_NATIVE_STROBE_BASELINE=FAIL reg=0x0468 value=0x%02x expected=0x%02x write_authorized=0\n",
			gpio_before, SP11_WINDOWS_ISOLATED_STROBE_VALUE);
		return -EIO;
	}
	dev_info(sensor->dev,
		 "SP11_VD55G0_NATIVE_STROBE_BASELINE=PASS reg=0x0468 value=0x%02x write_authorized=0\n",
		 gpio_before);

	for (i = 0; i < SP11_WINDOWS_SAFE42_COUNT; i++) {
		if (sp11_windows_safe42[i].reg == SP11_WINDOWS_ISOLATED_STROBE_REG)
			return -EPERM;
		ret = sp11_write8(sensor, sp11_windows_safe42[i].reg,
				  sp11_windows_safe42[i].data);
		if (ret)
			return ret;
		writes++;
	}

	ret = sp11_read(sensor, SP11_WINDOWS_ISOLATED_STROBE_REG,
			&gpio_after, 1);
	if (ret)
		return ret;
	if (gpio_after != gpio_before)
		return -EIO;

	ret = sp11_read(sensor, 0x0220, transport, sizeof(transport));
	if (ret)
		return ret;
	ret = sp11_read(sensor, 0x0300, timing, sizeof(timing));
	if (ret)
		return ret;
	ret = sp11_read(sensor, 0x0416, &pedestal, 1);
	if (ret)
		return ret;
	ret = sp11_read(sensor, 0x044c, exposure, sizeof(exposure));
	if (ret)
		return ret;
	ret = sp11_read(sensor, 0x0458, frame, sizeof(frame));
	if (ret)
		return ret;
	ret = sp11_read(sensor, 0x0467, gpio_ctrl, sizeof(gpio_ctrl));
	if (ret)
		return ret;
	ret = sp11_read(sensor, 0x045e, roi, sizeof(roi));
	if (ret)
		return ret;
	ret = sp11_read(sensor, 0x045a, y_window, sizeof(y_window));
	if (ret)
		return ret;

	if (memcmp(transport, (u8[]){0x00,0xf8,0x24,0x01,0x00,0x62,0x11,0x32}, 8) ||
	    memcmp(timing, (u8[]){0xb0,0x04,0x00,0x00}, 4) ||
	    pedestal != 0x40 ||
	    memcmp(exposure, (u8[]){0x02,0x00,0x64,0x00,0x00,0x00}, 6) ||
	    memcmp(frame, (u8[]){0xa3,0x07}, 2) ||
	    memcmp(gpio_ctrl, (u8[]){0x01,0x02,0x01,0x01}, 4) ||
	    memcmp(roi, (u8[]){0x00,0x00,0x83,0x02,0x00,0x00,0x5b,0x02}, 8) ||
	    memcmp(y_window, (u8[]){0x00,0x00,0x5b,0x02}, 4))
		return -EIO;

	if (writes != 596)
		return -EIO;

	sensor->initialized = true;
	dev_info(sensor->dev,
		 "SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596 patch=552 safe_config=42 extclk=19200000 mipi=840000000 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01 final_state=SW_STBY stream=0 illumination=0\n");
	return 0;
}

static int sp11_vd55g0_power_on(struct device *dev)
{
	struct v4l2_subdev *sd = dev_get_drvdata(dev);
	struct sp11_vd55g0 *sensor = to_sp11_vd55g0(sd);
	unsigned long rate;
	int ret;

	gpiod_set_value_cansleep(sensor->reset, 1);
	sp11_safe_delay();

	ret = clk_set_rate(sensor->xclk, SP11_VD55G0_XCLK_HZ);
	if (ret)
		return ret;
	ret = clk_prepare_enable(sensor->xclk);
	if (ret)
		return ret;
	sensor->clock_on = true;

	rate = clk_get_rate(sensor->xclk);
	if (rate != SP11_VD55G0_XCLK_HZ) {
		ret = -ERANGE;
		goto fail;
	}
	sp11_safe_delay();

	ret = regulator_enable(sensor->vddio);
	if (ret)
		goto fail;
	sensor->vddio_on = true;
	ret = regulator_enable(sensor->vcore);
	if (ret)
		goto fail;
	sensor->vcore_on = true;
	sp11_safe_delay();
	ret = regulator_enable(sensor->vana);
	if (ret)
		goto fail;
	sensor->vana_on = true;
	sp11_safe_delay();

	ret = sp11_expect_voltage(sensor, sensor->vddio, "VDDIO", SP11_VDDIO_UV);
	if (ret)
		goto fail;
	ret = sp11_expect_voltage(sensor, sensor->vcore, "VCORE", SP11_VCORE_UV);
	if (ret)
		goto fail;
	ret = sp11_expect_voltage(sensor, sensor->vana, "VANA", SP11_VANA_UV);
	if (ret)
		goto fail;

	gpiod_set_value_cansleep(sensor->reset, 0);
	sp11_safe_delay();

	ret = sp11_vd55g0_windows_init(sensor);
	if (ret)
		goto fail;

	dev_info(sensor->dev,
		 "SP11_VD55G0_NATIVE_POWER_ON=PASS xclk=19200000 initialized=1 final_state=SW_STBY stream=0 illumination=0\n");
	return 0;

fail:
	sp11_vd55g0_power_off_hw(sensor);
	return ret;
}

static int sp11_vd55g0_power_off(struct device *dev)
{
	struct v4l2_subdev *sd = dev_get_drvdata(dev);
	struct sp11_vd55g0 *sensor = to_sp11_vd55g0(sd);

	sp11_vd55g0_power_off_hw(sensor);
	return 0;
}

static void sp11_vd55g0_fill_format(struct v4l2_mbus_framefmt *fmt)
{
	fmt->width = SP11_VD55G0_WIDTH;
	fmt->height = SP11_VD55G0_HEIGHT;
	fmt->code = MEDIA_BUS_FMT_Y10_1X10;
	fmt->field = V4L2_FIELD_NONE;
	fmt->colorspace = V4L2_COLORSPACE_RAW;
	fmt->ycbcr_enc = V4L2_YCBCR_ENC_601;
	fmt->quantization = V4L2_QUANTIZATION_FULL_RANGE;
	fmt->xfer_func = V4L2_XFER_FUNC_NONE;
}

static int sp11_vd55g0_init_state(struct v4l2_subdev *sd,
				   struct v4l2_subdev_state *state)
{
	sp11_vd55g0_fill_format(v4l2_subdev_state_get_format(state, 0));
	return 0;
}

static int sp11_vd55g0_enum_mbus_code(struct v4l2_subdev *sd,
				       struct v4l2_subdev_state *state,
				       struct v4l2_subdev_mbus_code_enum *code)
{
	if (code->index)
		return -EINVAL;
	code->code = MEDIA_BUS_FMT_Y10_1X10;
	return 0;
}

static int sp11_vd55g0_enum_frame_size(struct v4l2_subdev *sd,
					struct v4l2_subdev_state *state,
					struct v4l2_subdev_frame_size_enum *fse)
{
	if (fse->index || fse->code != MEDIA_BUS_FMT_Y10_1X10)
		return -EINVAL;
	fse->min_width = SP11_VD55G0_WIDTH;
	fse->max_width = SP11_VD55G0_WIDTH;
	fse->min_height = SP11_VD55G0_HEIGHT;
	fse->max_height = SP11_VD55G0_HEIGHT;
	return 0;
}

static int sp11_vd55g0_set_fmt(struct v4l2_subdev *sd,
				struct v4l2_subdev_state *state,
				struct v4l2_subdev_format *fmt)
{
	struct v4l2_mbus_framefmt *state_fmt;

	if (fmt->pad)
		return -EINVAL;
	sp11_vd55g0_fill_format(&fmt->format);
	state_fmt = v4l2_subdev_state_get_format(state, 0);
	*state_fmt = fmt->format;
	return 0;
}

static int sp11_vd55g0_get_mbus_config(struct v4l2_subdev *sd,
				       unsigned int pad,
				       struct v4l2_mbus_config *config)
{
	if (pad)
		return -EINVAL;

	config->type = V4L2_MBUS_CSI2_DPHY;
	config->bus.mipi_csi2.num_data_lanes = 1;
	config->link_freq = SP11_VD55G0_LINK_FREQ_HZ;
	return 0;
}

static int sp11_vd55g0_s_stream(struct v4l2_subdev *sd, int enable)
{
	struct sp11_vd55g0 *sensor = to_sp11_vd55g0(sd);

	if (!enable)
		return 0;
	dev_warn(sensor->dev,
		 "SP11_VD55G0_NATIVE_STREAM_BLOCK=PASS requested=1 reason=E004l_bind_only stream=0 illumination=0\n");
	return -EOPNOTSUPP;
}

static const struct v4l2_subdev_video_ops sp11_vd55g0_video_ops = {
	.s_stream = sp11_vd55g0_s_stream,
};

static const struct v4l2_subdev_pad_ops sp11_vd55g0_pad_ops = {
	.enum_mbus_code = sp11_vd55g0_enum_mbus_code,
	.enum_frame_size = sp11_vd55g0_enum_frame_size,
	.get_fmt = v4l2_subdev_get_fmt,
	.set_fmt = sp11_vd55g0_set_fmt,
	.get_mbus_config = sp11_vd55g0_get_mbus_config,
};

static const struct v4l2_subdev_ops sp11_vd55g0_subdev_ops = {
	.video = &sp11_vd55g0_video_ops,
	.pad = &sp11_vd55g0_pad_ops,
};

static const struct v4l2_subdev_internal_ops sp11_vd55g0_internal_ops = {
	.init_state = sp11_vd55g0_init_state,
};

static int sp11_vd55g0_init_controls(struct sp11_vd55g0 *sensor)
{
	struct v4l2_ctrl *ctrl;
	int ret;

	ret = v4l2_ctrl_handler_init(&sensor->ctrls, 4);
	if (ret)
		return ret;

	ctrl = v4l2_ctrl_new_int_menu(&sensor->ctrls, NULL, V4L2_CID_LINK_FREQ,
				      ARRAY_SIZE(sp11_vd55g0_link_freq_menu) - 1,
				      0, sp11_vd55g0_link_freq_menu);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;

	ctrl = v4l2_ctrl_new_std(&sensor->ctrls, NULL, V4L2_CID_PIXEL_RATE,
				 SP11_VD55G0_PIXEL_RATE_HZ,
				 SP11_VD55G0_PIXEL_RATE_HZ, 1,
				 SP11_VD55G0_PIXEL_RATE_HZ);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;

	ctrl = v4l2_ctrl_new_std(&sensor->ctrls, NULL, V4L2_CID_HBLANK,
				 SP11_VD55G0_HBLANK, SP11_VD55G0_HBLANK, 1,
				 SP11_VD55G0_HBLANK);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;

	ctrl = v4l2_ctrl_new_std(&sensor->ctrls, NULL, V4L2_CID_VBLANK,
				 SP11_VD55G0_VBLANK, SP11_VD55G0_VBLANK, 1,
				 SP11_VD55G0_VBLANK);
	if (ctrl)
		ctrl->flags |= V4L2_CTRL_FLAG_READ_ONLY;

	if (sensor->ctrls.error) {
		ret = sensor->ctrls.error;
		v4l2_ctrl_handler_free(&sensor->ctrls);
		return ret;
	}

	sensor->sd.ctrl_handler = &sensor->ctrls;
	return 0;
}

static int sp11_vd55g0_probe(struct i2c_client *client)
{
	struct sp11_vd55g0 *sensor;
	int ret;

	sensor = devm_kzalloc(&client->dev, sizeof(*sensor), GFP_KERNEL);
	if (!sensor)
		return -ENOMEM;

	sensor->dev = &client->dev;
	sensor->client = client;
	v4l2_i2c_subdev_init(&sensor->sd, client, &sp11_vd55g0_subdev_ops);

	sensor->reset = devm_gpiod_get(sensor->dev, "reset", GPIOD_OUT_HIGH);
	if (IS_ERR(sensor->reset))
		return dev_err_probe(sensor->dev, PTR_ERR(sensor->reset),
				     "get GPIO109 reset failed\n");
	sensor->xclk = devm_clk_get(sensor->dev, NULL);
	if (IS_ERR(sensor->xclk))
		return dev_err_probe(sensor->dev, PTR_ERR(sensor->xclk),
				     "get MCLK0 failed\n");
	sensor->vcore = devm_regulator_get(sensor->dev, "VCORE");
	if (IS_ERR(sensor->vcore))
		return dev_err_probe(sensor->dev, PTR_ERR(sensor->vcore),
				     "get LDO2_M/VCORE failed\n");
	sensor->vddio = devm_regulator_get(sensor->dev, "VDDIO");
	if (IS_ERR(sensor->vddio))
		return dev_err_probe(sensor->dev, PTR_ERR(sensor->vddio),
				     "get LDO4_M/VDDIO failed\n");
	sensor->vana = devm_regulator_get(sensor->dev, "VANA");
	if (IS_ERR(sensor->vana))
		return dev_err_probe(sensor->dev, PTR_ERR(sensor->vana),
				     "get LDO7_M/VANA failed\n");

	ret = sp11_vd55g0_power_on(sensor->dev);
	if (ret)
		return dev_err_probe(sensor->dev, ret,
				     "Windows-authority power/init failed\n");

	sensor->sd.flags |= V4L2_SUBDEV_FL_HAS_DEVNODE;
	sensor->sd.entity.function = MEDIA_ENT_F_CAM_SENSOR;
	sensor->sd.internal_ops = &sp11_vd55g0_internal_ops;
	sensor->pad.flags = MEDIA_PAD_FL_SOURCE;

	ret = sp11_vd55g0_init_controls(sensor);
	if (ret)
		goto err_power;
	ret = media_entity_pads_init(&sensor->sd.entity, 1, &sensor->pad);
	if (ret)
		goto err_ctrls;
	ret = v4l2_subdev_init_finalize(&sensor->sd);
	if (ret)
		goto err_entity;
	ret = v4l2_async_register_subdev_sensor(&sensor->sd);
	if (ret)
		goto err_subdev;

	pm_runtime_set_active(sensor->dev);
	pm_runtime_enable(sensor->dev);
	pm_runtime_idle(sensor->dev);

	dev_info(sensor->dev,
		 "SP11_VD55G0_NATIVE_BIND=PASS format=Y10_1X10 size=644x604 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 stream_capable=0 illumination_capable=0\n");
	return 0;

err_subdev:
	v4l2_subdev_cleanup(&sensor->sd);
err_entity:
	media_entity_cleanup(&sensor->sd.entity);
err_ctrls:
	v4l2_ctrl_handler_free(&sensor->ctrls);
err_power:
	sp11_vd55g0_power_off_hw(sensor);
	return ret;
}

static void sp11_vd55g0_remove(struct i2c_client *client)
{
	struct v4l2_subdev *sd = i2c_get_clientdata(client);
	struct sp11_vd55g0 *sensor = to_sp11_vd55g0(sd);

	v4l2_async_unregister_subdev(sd);
	v4l2_subdev_cleanup(sd);
	media_entity_cleanup(&sd->entity);
	v4l2_ctrl_handler_free(&sensor->ctrls);
	pm_runtime_disable(sensor->dev);
	if (!pm_runtime_status_suspended(sensor->dev))
		sp11_vd55g0_power_off_hw(sensor);
	pm_runtime_set_suspended(sensor->dev);
}

static DEFINE_RUNTIME_DEV_PM_OPS(sp11_vd55g0_pm_ops,
				 sp11_vd55g0_power_off,
				 sp11_vd55g0_power_on, NULL);

static const struct of_device_id sp11_vd55g0_of_match[] = {
	{ .compatible = "microsoft,sp11-vd55g0" },
	{ }
};
MODULE_DEVICE_TABLE(of, sp11_vd55g0_of_match);

static const struct i2c_device_id sp11_vd55g0_i2c_ids[] = {
	{ "sp11-vd55g0" },
	{ }
};
MODULE_DEVICE_TABLE(i2c, sp11_vd55g0_i2c_ids);

static struct i2c_driver sp11_vd55g0_driver = {
	.driver = {
		.name = "sp11-vd55g0",
		.pm = pm_ptr(&sp11_vd55g0_pm_ops),
		.of_match_table = sp11_vd55g0_of_match,
	},
	.probe = sp11_vd55g0_probe,
	.remove = sp11_vd55g0_remove,
	.id_table = sp11_vd55g0_i2c_ids,
};
module_i2c_driver(sp11_vd55g0_driver);

MODULE_AUTHOR("SP11X1ECamera clean-room same-machine Windows integration");
MODULE_DESCRIPTION("Surface Pro 11 VD55G0 Windows-parity bind-only V4L2 sensor driver");
MODULE_LICENSE("GPL");
