// SPDX-License-Identifier: GPL-2.0
/*
 * Surface Pro 11 VD55G0 bounded identity/revision probe.
 *
 * This is deliberately NOT a camera driver.  It performs one bounded
 * same-machine parity diagnostic and powers the sensor back off before
 * probe returns.  It never writes sensor register data, uploads firmware,
 * boots/configures the sensor, registers V4L2, streams, or controls LEDs.
 */
#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/regulator/consumer.h>

#define SP11_XCLK_HZ        19200000UL
#define SP11_VCORE_UV        1152000
#define SP11_VDDIO_UV        1800000
#define SP11_VANA_UV         2800000
#define SP11_SAFE_DELAY_US       5000

struct sp11_vd55g0_probe {
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

/*
 * Read exactly two data bytes after placing a 16-bit register address on
 * the bus.  The first message changes only the sensor's read pointer; it
 * does not contain sensor register data.
 */
static int sp11_read16(struct i2c_client *client, u16 reg, u8 raw[2])
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
			.buf = raw,
			.len = 2,
		},
	};
	int ret;

	ret = i2c_transfer(client->adapter, msgs, ARRAY_SIZE(msgs));
	if (ret == ARRAY_SIZE(msgs))
		return 0;
	if (ret >= 0)
		return -EIO;
	return ret;
}

static void sp11_power_off(struct device *dev, struct sp11_vd55g0_probe *p)
{
	/* Windows D3 order: reset low, VANA off, VCORE/VDDIO off, MCLK off. */
	if (p->reset) {
		gpiod_set_value_cansleep(p->reset, 1); /* active-low: assert */
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
	dev_info(dev, "SP11_VD55G0_IDPROBE_POWER_OFF reset_asserted=1\n");
}

static int sp11_expect_voltage(struct device *dev, struct regulator *reg,
			       const char *name, int expected_uv)
{
	int uv = regulator_get_voltage(reg);

	if (uv < 0) {
		dev_err(dev, "SP11_VD55G0_IDPROBE_%s voltage_read_error=%d\n",
			name, uv);
		return uv;
	}
	dev_info(dev, "SP11_VD55G0_IDPROBE_%s_uV=%d expected_uV=%d\n",
		 name, uv, expected_uv);
	if (uv != expected_uv)
		return -ERANGE;
	return 0;
}

static int sp11_vd55g0_probe(struct i2c_client *client)
{
	struct device *dev = &client->dev;
	struct sp11_vd55g0_probe *p;
	u8 model[2] = { 0 }, revision[2] = { 0 };
	unsigned long rate;
	int ret;

	dev_info(dev,
		 "SP11_VD55G0_IDPROBE_BEGIN addr=0x%02x safe_delay_us=%u sensor_data_writes=0 stream=0 illumination=0\n",
		 client->addr, SP11_SAFE_DELAY_US);

	p = devm_kzalloc(dev, sizeof(*p), GFP_KERNEL);
	if (!p)
		return -ENOMEM;

	p->reset = devm_gpiod_get(dev, "reset", GPIOD_OUT_HIGH);
	if (IS_ERR(p->reset))
		return dev_err_probe(dev, PTR_ERR(p->reset),
				     "SP11_VD55G0_IDPROBE reset gpio\n");

	p->xclk = devm_clk_get(dev, NULL);
	if (IS_ERR(p->xclk))
		return dev_err_probe(dev, PTR_ERR(p->xclk),
				     "SP11_VD55G0_IDPROBE xclk\n");

	p->vcore = devm_regulator_get(dev, "VCORE");
	if (IS_ERR(p->vcore))
		return dev_err_probe(dev, PTR_ERR(p->vcore),
				     "SP11_VD55G0_IDPROBE VCORE\n");
	p->vddio = devm_regulator_get(dev, "VDDIO");
	if (IS_ERR(p->vddio))
		return dev_err_probe(dev, PTR_ERR(p->vddio),
				     "SP11_VD55G0_IDPROBE VDDIO\n");
	p->vana = devm_regulator_get(dev, "VANA");
	if (IS_ERR(p->vana))
		return dev_err_probe(dev, PTR_ERR(p->vana),
				     "SP11_VD55G0_IDPROBE VANA\n");

	/* Keep reset asserted while establishing and checking resources. */
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
	dev_info(dev, "SP11_VD55G0_IDPROBE_MCLK_Hz=%lu expected_Hz=%lu\n",
		 rate, SP11_XCLK_HZ);
	if (rate != SP11_XCLK_HZ) {
		ret = -ERANGE;
		goto out;
	}
	sp11_safe_delay();

	/* Windows D0 rail order: LDO4_M(VDDIO), LDO2_M(VCORE), then LDO7_M(VANA). */
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

	/* Windows releases reset after all three rails are established. */
	gpiod_set_value_cansleep(p->reset, 0); /* active-low: deassert */
	sp11_safe_delay();

	ret = sp11_read16(client, 0x0000, model);
	if (ret) {
		dev_err(dev, "SP11_VD55G0_IDPROBE_MODEL_READ_ERROR=%d\n", ret);
		goto out;
	}
	ret = sp11_read16(client, 0x0004, revision);
	if (ret) {
		dev_err(dev, "SP11_VD55G0_IDPROBE_REVISION_READ_ERROR=%d\n", ret);
		goto out;
	}

	dev_info(dev,
		 "SP11_VD55G0_IDPROBE_MODEL raw=%02x,%02x le=0x%04x be=0x%04x windows_qti_expected_be=0x3047\n",
		 model[0], model[1],
		 (u16)model[0] | ((u16)model[1] << 8),
		 ((u16)model[0] << 8) | model[1]);
	dev_info(dev,
		 "SP11_VD55G0_IDPROBE_REVISION raw=%02x,%02x le=0x%04x be=0x%04x\n",
		 revision[0], revision[1],
		 (u16)revision[0] | ((u16)revision[1] << 8),
		 ((u16)revision[0] << 8) | revision[1]);
	dev_info(dev,
		 "SP11_VD55G0_IDPROBE_READS_COMPLETE sensor_data_writes=0 patch=0 boot=0 configure=0 stream=0 illumination=0\n");
	ret = 0;

out:
	sp11_power_off(dev, p);
	if (ret)
		dev_err(dev, "SP11_VD55G0_IDPROBE_END status=%d powered_off=1\n", ret);
	else
		dev_info(dev, "SP11_VD55G0_IDPROBE_END status=0 powered_off=1\n");
	return ret;
}

static void sp11_vd55g0_remove(struct i2c_client *client)
{
	dev_info(&client->dev,
		 "SP11_VD55G0_IDPROBE_REMOVE powered_state=already_off\n");
}

static const struct of_device_id sp11_vd55g0_of_match[] = {
	{ .compatible = "microsoft,sp11-vd55g0-idprobe" },
	{ }
};
MODULE_DEVICE_TABLE(of, sp11_vd55g0_of_match);

static struct i2c_driver sp11_vd55g0_driver = {
	.driver = {
		.name = "sp11-vd55g0-idprobe",
		.of_match_table = sp11_vd55g0_of_match,
	},
	.probe = sp11_vd55g0_probe,
	.remove = sp11_vd55g0_remove,
};
module_i2c_driver(sp11_vd55g0_driver);

MODULE_DESCRIPTION("Surface Pro 11 VD55G0 bounded identity/revision probe only");
MODULE_LICENSE("GPL");
