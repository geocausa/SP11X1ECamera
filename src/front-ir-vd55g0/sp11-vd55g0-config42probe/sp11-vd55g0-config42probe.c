// SPDX-License-Identifier: GPL-2.0
/*
 * Surface Pro 11 VD55G0 bounded safe-42 Windows configuration probe.
 *
 * This is deliberately not a V4L2 camera driver. It replays the proven
 * Windows patch/boot prefix, then applies the 42 final Windows configuration
 * writes excluding the illumination-coupled GPIO1 strobe selector 0x0468.
 * It remains in software standby, performs readback, then powers off.
 */
#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/regulator/consumer.h>
#include <linux/string.h>

#include "surface-windows.generated.h"

#define SP11_XCLK_HZ              19200000UL
#define SP11_VCORE_UV              1152000
#define SP11_VDDIO_UV              1800000
#define SP11_VANA_UV               2800000
#define SP11_SAFE_DELAY_US             5000

#define VD55G0_REG_MODEL_ID         0x0000
#define VD55G0_REG_REVISION         0x0004
#define VD55G0_REG_SYSTEM_FSM       0x002c
#define VD55G0_REG_BOOT             0x0200
#define VD55G0_PATCH_START          0x2000

#define VD55G0_FSM_READY_TO_BOOT      0x01
#define VD55G0_FSM_SW_STBY             0x02
#define VD55G0_BOOT_PATCH_SETUP        0x02
#define VD55G0_BOOT_BOOT               0x01

struct sp11_config42_probe {
	struct clk *xclk;
	struct gpio_desc *reset;
	struct regulator *vcore;
	struct regulator *vddio;
	struct regulator *vana;
	bool clock_on;
	bool vddio_on;
	bool vcore_on;
	bool vana_on;
};

static void sp11_safe_delay(void)
{
	usleep_range(SP11_SAFE_DELAY_US, SP11_SAFE_DELAY_US + 500);
}

static int sp11_read(struct i2c_client *client, u16 reg, u8 *data, u16 len)
{
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
static int sp11_write8(struct i2c_client *client, u16 reg, u8 data)
{
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

/*
 * Mirror the exact Windows poll-loop shape: up to N reads, one 1 ms
 * relative delay after each mismatch (including the final mismatch).
 */
static int sp11_poll8(struct i2c_client *client, u16 reg, u8 expected,
		      unsigned int attempts, const char *name)
{
	struct device *dev = &client->dev;
	u8 value = 0;
	unsigned int i;
	int ret;

	for (i = 0; i < attempts; i++) {
		ret = sp11_read(client, reg, &value, 1);
		if (ret)
			return ret;
		if (value == expected) {
			dev_info(dev,
				 "SP11_VD55G0_CONFIG42_POLL name=%s reg=0x%04x expected=0x%02x timeout_ms=%u reads=%u result=PASS\n",
				 name, reg, expected, attempts, i + 1);
			return 0;
		}
		usleep_range(1000, 1100);
	}

	dev_err(dev,
		"SP11_VD55G0_CONFIG42_POLL name=%s reg=0x%04x expected=0x%02x timeout_ms=%u last=0x%02x result=TIMEOUT\n",
		name, reg, expected, attempts, value);
	return -ETIMEDOUT;
}

static void sp11_power_off(struct device *dev, struct sp11_config42_probe *p)
{
	if (p->reset) {
		gpiod_set_value_cansleep(p->reset, 1);
		sp11_safe_delay();
	}
	if (p->vana_on) {
		regulator_disable(p->vana);
		p->vana_on = false;
		sp11_safe_delay();
	}
	if (p->vcore_on) {
		regulator_disable(p->vcore);
		p->vcore_on = false;
	}
	if (p->vddio_on) {
		regulator_disable(p->vddio);
		p->vddio_on = false;
	}
	if (p->clock_on) {
		clk_disable_unprepare(p->xclk);
		p->clock_on = false;
	}
	dev_info(dev, "SP11_VD55G0_CONFIG42_POWER_OFF reset_asserted=1\n");
}

static int sp11_expect_voltage(struct device *dev, struct regulator *reg,
			       const char *name, int expected_uv)
{
	int uv = regulator_get_voltage(reg);

	if (uv < 0)
		return uv;
	dev_info(dev, "SP11_VD55G0_CONFIG42_%s_uV=%d expected_uV=%d\n",
		 name, uv, expected_uv);
	return uv == expected_uv ? 0 : -ERANGE;
}

static int sp11_config42_probe(struct i2c_client *client)
{
	struct device *dev = &client->dev;
	struct sp11_config42_probe *p;
	u8 model[2] = { 0 }, revision[2] = { 0 };
	u8 gpio_before = 0, gpio_after = 0;
	u8 transport[8] = { 0 }, timing[4] = { 0 }, exposure[6] = { 0 };
	u8 frame[2] = { 0 }, gpio_ctrl[4] = { 0 };
	u8 roi[8] = { 0 }, y_window[4] = { 0 }, pedestal = 0;
	unsigned long rate;
	unsigned int i;
	unsigned int writes = 0;
	int ret;

	dev_info(dev,
		 "SP11_VD55G0_CONFIG42_BEGIN addr=0x%02x patch_bytes=%u patch_sha256=%s safe42_sha256=%s full43_sha256=%s safe_config_writes=42 isolated_strobe_reg=0x0468 strobe_write=0 stream=0 illumination=0\n",
		 client->addr, SP11_SURFACE_PATCH_SIZE, SP11_SURFACE_PATCH_SHA256,
		 SP11_WINDOWS_SAFE42_SHA256, SP11_WINDOWS_FULL43_SHA256);

	p = devm_kzalloc(dev, sizeof(*p), GFP_KERNEL);
	if (!p)
		return -ENOMEM;

	p->reset = devm_gpiod_get(dev, "reset", GPIOD_OUT_HIGH);
	if (IS_ERR(p->reset))
		return dev_err_probe(dev, PTR_ERR(p->reset), "prefix reset gpio\n");
	p->xclk = devm_clk_get(dev, NULL);
	if (IS_ERR(p->xclk))
		return dev_err_probe(dev, PTR_ERR(p->xclk), "prefix xclk\n");
	p->vcore = devm_regulator_get(dev, "VCORE");
	if (IS_ERR(p->vcore))
		return dev_err_probe(dev, PTR_ERR(p->vcore), "prefix VCORE\n");
	p->vddio = devm_regulator_get(dev, "VDDIO");
	if (IS_ERR(p->vddio))
		return dev_err_probe(dev, PTR_ERR(p->vddio), "prefix VDDIO\n");
	p->vana = devm_regulator_get(dev, "VANA");
	if (IS_ERR(p->vana))
		return dev_err_probe(dev, PTR_ERR(p->vana), "prefix VANA\n");

	gpiod_set_value_cansleep(p->reset, 1);
	sp11_safe_delay();

	ret = clk_set_rate(p->xclk, SP11_XCLK_HZ);
	if (ret)
		goto out;
	ret = clk_prepare_enable(p->xclk);
	if (ret)
		goto out;
	p->clock_on = true;
	rate = clk_get_rate(p->xclk);
	dev_info(dev, "SP11_VD55G0_CONFIG42_MCLK_Hz=%lu expected_Hz=%lu\n",
		 rate, SP11_XCLK_HZ);
	if (rate != SP11_XCLK_HZ) {
		ret = -ERANGE;
		goto out;
	}
	sp11_safe_delay();

	ret = regulator_enable(p->vddio);
	if (ret)
		goto out;
	p->vddio_on = true;
	ret = regulator_enable(p->vcore);
	if (ret)
		goto out;
	p->vcore_on = true;
	sp11_safe_delay();
	ret = regulator_enable(p->vana);
	if (ret)
		goto out;
	p->vana_on = true;
	sp11_safe_delay();

	ret = sp11_expect_voltage(dev, p->vddio, "VDDIO", SP11_VDDIO_UV);
	if (ret)
		goto out;
	ret = sp11_expect_voltage(dev, p->vcore, "VCORE", SP11_VCORE_UV);
	if (ret)
		goto out;
	ret = sp11_expect_voltage(dev, p->vana, "VANA", SP11_VANA_UV);
	if (ret)
		goto out;

	gpiod_set_value_cansleep(p->reset, 0);
	sp11_safe_delay();

	ret = sp11_read(client, VD55G0_REG_MODEL_ID, model, 2);
	if (ret)
		goto out;
	ret = sp11_read(client, VD55G0_REG_REVISION, revision, 2);
	if (ret)
		goto out;

	dev_info(dev,
		 "SP11_VD55G0_CONFIG42_ID model_raw=%02x,%02x model_be=0x%04x revision_raw=%02x,%02x revision=0x%04x\n",
		 model[0], model[1], ((u16)model[0] << 8) | model[1],
		 revision[0], revision[1],
		 ((u16)revision[0] << 8) | revision[1]);
	if (model[0] != 0x30 || model[1] != 0x47 ||
	    revision[0] != 0x11 || revision[1] != 0x11) {
		ret = -ENODEV;
		dev_err(dev, "SP11_VD55G0_CONFIG42_ID_GATE=FAIL writes=0\n");
		goto out;
	}
	dev_info(dev, "SP11_VD55G0_CONFIG42_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0\n");

	ret = sp11_poll8(client, VD55G0_REG_SYSTEM_FSM,
			 VD55G0_FSM_READY_TO_BOOT, 6, "READY_TO_BOOT");
	if (ret)
		goto out;

	dev_info(dev,
		 "SP11_VD55G0_CONFIG42_PATCH_BEGIN start=0x2000 bytes=%u sha256=%s\n",
		 SP11_SURFACE_PATCH_SIZE, SP11_SURFACE_PATCH_SHA256);
	for (i = 0; i < SP11_SURFACE_PATCH_SIZE; i++) {
		ret = sp11_write8(client, VD55G0_PATCH_START + i,
				  sp11_surface_patch[i]);
		if (ret)
			goto out;
		writes++;
	}

	ret = sp11_write8(client, VD55G0_REG_BOOT, VD55G0_BOOT_PATCH_SETUP);
	if (ret)
		goto out;
	writes++;
	dev_info(dev, "SP11_VD55G0_CONFIG42_PATCH_SETUP writes=%u reg=0x0200 value=0x02\n", writes);

	ret = sp11_poll8(client, VD55G0_REG_BOOT, 0x00, 28,
			 "PATCH_SETUP_COMPLETE");
	if (ret)
		goto out;

	ret = sp11_write8(client, VD55G0_REG_BOOT, VD55G0_BOOT_BOOT);
	if (ret)
		goto out;
	writes++;
	dev_info(dev, "SP11_VD55G0_CONFIG42_BOOT writes=%u reg=0x0200 value=0x01\n", writes);

	ret = sp11_poll8(client, VD55G0_REG_BOOT, 0x00, 6,
			 "BOOT_COMPLETE");
	if (ret)
		goto out;
	ret = sp11_poll8(client, VD55G0_REG_SYSTEM_FSM,
			 VD55G0_FSM_SW_STBY, 4, "SW_STBY");
	if (ret)
		goto out;

	/* Isolate the illumination-coupled Windows GPIO1 strobe selector. */
	ret = sp11_read(client, SP11_WINDOWS_ISOLATED_STROBE_REG, &gpio_before, 1);
	if (ret)
		goto out;
	dev_info(dev,
		 "SP11_VD55G0_CONFIG42_STROBE_ISOLATION_BEFORE reg=0x0468 value=0x%02x write_authorized=0\n",
		 gpio_before);

	for (i = 0; i < SP11_WINDOWS_SAFE42_COUNT; i++) {
		if (sp11_windows_safe42[i].reg == SP11_WINDOWS_ISOLATED_STROBE_REG) {
			ret = -EPERM;
			goto out;
		}
		ret = sp11_write8(client, sp11_windows_safe42[i].reg,
				  sp11_windows_safe42[i].data);
		if (ret)
			goto out;
		writes++;
	}

	ret = sp11_read(client, SP11_WINDOWS_ISOLATED_STROBE_REG, &gpio_after, 1);
	if (ret)
		goto out;
	dev_info(dev,
		 "SP11_VD55G0_CONFIG42_STROBE_ISOLATION_AFTER reg=0x0468 before=0x%02x after=0x%02x unchanged=%u write_authorized=0\n",
		 gpio_before, gpio_after, gpio_before == gpio_after);
	if (gpio_before != gpio_after) {
		ret = -EIO;
		goto out;
	}

	/* Read back the Windows-programmed non-strobe configuration groups. */
	ret = sp11_read(client, 0x0220, transport, sizeof(transport));
	if (ret) goto out;
	ret = sp11_read(client, 0x0300, timing, sizeof(timing));
	if (ret) goto out;
	ret = sp11_read(client, 0x0416, &pedestal, 1);
	if (ret) goto out;
	ret = sp11_read(client, 0x044c, exposure, sizeof(exposure));
	if (ret) goto out;
	ret = sp11_read(client, 0x0458, frame, sizeof(frame));
	if (ret) goto out;
	ret = sp11_read(client, 0x0467, gpio_ctrl, sizeof(gpio_ctrl));
	if (ret) goto out;
	ret = sp11_read(client, 0x045e, roi, sizeof(roi));
	if (ret) goto out;
	ret = sp11_read(client, 0x045a, y_window, sizeof(y_window));
	if (ret) goto out;

	if (memcmp(transport, (u8[]){0x00,0xf8,0x24,0x01,0x00,0x62,0x11,0x32}, 8) ||
	    memcmp(timing, (u8[]){0xb0,0x04,0x00,0x00}, 4) ||
	    pedestal != 0x40 ||
	    memcmp(exposure, (u8[]){0x02,0x00,0x64,0x00,0x00,0x00}, 6) ||
	    memcmp(frame, (u8[]){0xa3,0x07}, 2) ||
	    gpio_ctrl[0] != 0x01 || gpio_ctrl[1] != gpio_before ||
	    gpio_ctrl[2] != 0x01 || gpio_ctrl[3] != 0x01 ||
	    memcmp(roi, (u8[]){0x00,0x00,0x83,0x02,0x00,0x00,0x5b,0x02}, 8) ||
	    memcmp(y_window, (u8[]){0x00,0x00,0x5b,0x02}, 4)) {
		ret = -EIO;
		goto out;
	}

	dev_info(dev,
		 "SP11_VD55G0_CONFIG42_READBACK=PASS extclk=19200000 mipi=840000000 line=1200 frame=1955 roi=644x604 gpio=%02x,%02x,%02x,%02x\n",
		 gpio_ctrl[0], gpio_ctrl[1], gpio_ctrl[2], gpio_ctrl[3]);

	dev_info(dev,
		 "SP11_VD55G0_CONFIG42_COMPLETE writes=%u patch_writes=552 setup_writes=1 boot_writes=1 safe_config_writes=42 isolated_strobe_writes=0 final_state=SW_STBY stream=0 illumination=0\n",
		 writes);
	if (writes != 596)
		ret = -EIO;
	else
		ret = 0;

out:
	sp11_power_off(dev, p);
	if (ret)
		dev_err(dev,
			"SP11_VD55G0_CONFIG42_END status=%d writes=%u powered_off=1 stream=0 illumination=0\n",
			ret, writes);
	else
		dev_info(dev,
			 "SP11_VD55G0_CONFIG42_END status=0 writes=%u powered_off=1 stream=0 illumination=0\n",
			 writes);
	return ret;
}

static void sp11_config42_remove(struct i2c_client *client)
{
	dev_info(&client->dev, "SP11_VD55G0_CONFIG42_REMOVE powered_state=already_off\n");
}

static const struct of_device_id sp11_config42_of_match[] = {
	{ .compatible = "microsoft,sp11-vd55g0-config42probe" },
	{ }
};
MODULE_DEVICE_TABLE(of, sp11_config42_of_match);

static struct i2c_driver sp11_config42_driver = {
	.driver = {
		.name = "sp11-vd55g0-config42probe",
		.of_match_table = sp11_config42_of_match,
	},
	.probe = sp11_config42_probe,
	.remove = sp11_config42_remove,
};
module_i2c_driver(sp11_config42_driver);

MODULE_DESCRIPTION("Surface Pro 11 VD55G0 bounded Windows InitialConfig safe-42 configuration probe");
MODULE_LICENSE("GPL");
