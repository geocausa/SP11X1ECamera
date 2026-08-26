// SPDX-License-Identifier: GPL-2.0
/*
 * SP11 E002b probe-only OV13858 power/identity oracle.
 *
 * Deliberately NOT a camera/V4L2 driver. It reproduces the Windows-derived
 * Surface rear-camera D0 ordering far enough to read silicon identity, then
 * immediately tears power down in reverse order. No streaming is possible.
 */
#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/regulator/consumer.h>

#define OV13858_ID_REG          0x300a
#define OV13858_ID_EXPECTED     0x00d855
#define SP11_XCLK_HZ            19200000UL

struct sp11_ov13858_probe {
	struct regulator *ldo6m;
	struct regulator *ldo1m;
	struct regulator *ldo5m;
	struct regulator *ldo16b;
	struct clk *xclk;
	struct gpio_desc *reset;
	bool powered;
};

static void sp11_ov13858_power_off(struct sp11_ov13858_probe *p)
{
	if (!p->powered)
		return;

	/* Windows D3: reset low, delay, MCLK off, rails off in reverse order. */
	gpiod_set_value_cansleep(p->reset, 1); /* active-low reset => physical low */
	usleep_range(1000, 1500);
	clk_disable_unprepare(p->xclk);
	regulator_disable(p->ldo16b);
	regulator_disable(p->ldo5m);
	regulator_disable(p->ldo1m);
	regulator_disable(p->ldo6m);
	p->powered = false;
}

static int sp11_ov13858_power_on(struct device *dev,
				 struct sp11_ov13858_probe *p)
{
	int ret;

	/* Reset is acquired asserted. Windows D0 drives GPIO110 low first. */
	ret = regulator_enable(p->ldo6m); /* LDO6_M = 1.8 V */
	if (ret)
		return dev_err_probe(dev, ret, "enable LDO6_M failed\n");

	ret = regulator_enable(p->ldo1m); /* LDO1_M = 1.2 V */
	if (ret)
		goto err_l6;

	ret = regulator_enable(p->ldo5m); /* LDO5_M = 2.8 V */
	if (ret)
		goto err_l1;

	/* AeoB has DELAY 1 here. Use a conservative 1 ms probe delay. */
	usleep_range(1000, 1500);

	ret = regulator_enable(p->ldo16b); /* LDO16_B = 2.9 V */
	if (ret)
		goto err_l5;

	ret = clk_set_rate(p->xclk, SP11_XCLK_HZ);
	if (ret)
		goto err_l16;

	if (clk_get_rate(p->xclk) != SP11_XCLK_HZ) {
		ret = -EINVAL;
		dev_err(dev, "MCLK1 rate is %lu, expected %lu\n",
			clk_get_rate(p->xclk), SP11_XCLK_HZ);
		goto err_l16;
	}

	ret = clk_prepare_enable(p->xclk);
	if (ret)
		goto err_l16;

	gpiod_set_value_cansleep(p->reset, 0); /* release reset => physical high */
	/* AeoB has DELAY 10 here. 10 ms is deliberately conservative for probe. */
	usleep_range(10000, 12000);
	p->powered = true;
	return 0;

err_l16:
	regulator_disable(p->ldo16b);
err_l5:
	regulator_disable(p->ldo5m);
err_l1:
	regulator_disable(p->ldo1m);
err_l6:
	regulator_disable(p->ldo6m);
	return ret;
}

static int sp11_ov13858_read_id(struct i2c_client *client, u32 *id)
{
	u8 addr[2] = { OV13858_ID_REG >> 8, OV13858_ID_REG & 0xff };
	u8 data[3] = { 0 };
	struct i2c_msg msg[2] = {
		{
			.addr = client->addr,
			.flags = 0,
			.len = sizeof(addr),
			.buf = addr,
		},
		{
			.addr = client->addr,
			.flags = I2C_M_RD,
			.len = sizeof(data),
			.buf = data,
		},
	};
	int ret = i2c_transfer(client->adapter, msg, ARRAY_SIZE(msg));

	if (ret < 0)
		return ret;
	if (ret != ARRAY_SIZE(msg))
		return -EIO;

	*id = ((u32)data[0] << 16) | ((u32)data[1] << 8) | data[2];
	return 0;
}

static int sp11_ov13858_probe(struct i2c_client *client)
{
	struct device *dev = &client->dev;
	struct sp11_ov13858_probe *p;
	u32 id = 0;
	int ret;

	p = devm_kzalloc(dev, sizeof(*p), GFP_KERNEL);
	if (!p)
		return -ENOMEM;

	p->ldo6m = devm_regulator_get(dev, "ldo6m");
	if (IS_ERR(p->ldo6m))
		return dev_err_probe(dev, PTR_ERR(p->ldo6m), "get LDO6_M failed\n");
	p->ldo1m = devm_regulator_get(dev, "ldo1m");
	if (IS_ERR(p->ldo1m))
		return dev_err_probe(dev, PTR_ERR(p->ldo1m), "get LDO1_M failed\n");
	p->ldo5m = devm_regulator_get(dev, "ldo5m");
	if (IS_ERR(p->ldo5m))
		return dev_err_probe(dev, PTR_ERR(p->ldo5m), "get LDO5_M failed\n");
	p->ldo16b = devm_regulator_get(dev, "ldo16b");
	if (IS_ERR(p->ldo16b))
		return dev_err_probe(dev, PTR_ERR(p->ldo16b), "get LDO16_B failed\n");

	p->xclk = devm_clk_get(dev, "xclk");
	if (IS_ERR(p->xclk))
		return dev_err_probe(dev, PTR_ERR(p->xclk), "get MCLK1 failed\n");

	/* GPIO_ACTIVE_LOW in DT makes logical 1 = physical low/asserted. */
	p->reset = devm_gpiod_get(dev, "reset", GPIOD_OUT_HIGH);
	if (IS_ERR(p->reset))
		return dev_err_probe(dev, PTR_ERR(p->reset), "get GPIO110 reset failed\n");

	ret = regulator_set_voltage(p->ldo6m, 1800000, 1800000);
	if (ret)
		return dev_err_probe(dev, ret, "set LDO6_M 1.8 V failed\n");
	ret = regulator_set_voltage(p->ldo1m, 1200000, 1200000);
	if (ret)
		return dev_err_probe(dev, ret, "set LDO1_M 1.2 V failed\n");
	ret = regulator_set_voltage(p->ldo5m, 2800000, 2800000);
	if (ret)
		return dev_err_probe(dev, ret, "set LDO5_M 2.8 V failed\n");
	ret = regulator_set_voltage(p->ldo16b, 2900000, 2900000);
	if (ret)
		return dev_err_probe(dev, ret, "set LDO16_B 2.9 V failed\n");

	ret = sp11_ov13858_power_on(dev, p);
	if (ret)
		return ret;

	ret = sp11_ov13858_read_id(client, &id);
	if (ret)
		dev_err(dev, "SP11 E002b: chip-ID transfer failed: %d\n", ret);
	else if (id != OV13858_ID_EXPECTED) {
		dev_err(dev, "SP11 E002b: chip-ID mismatch: read 0x%06x expected 0x%06x\n",
			id, OV13858_ID_EXPECTED);
		ret = -ENODEV;
	} else {
		dev_info(dev, "SP11 E002b PASS: OV13858 chip ID 0x%06x at 0x%02x\n",
			 id, client->addr);
	}

	sp11_ov13858_power_off(p);
	dev_info(dev, "SP11 E002b: probe power sequence torn down\n");
	return ret;
}

static const struct of_device_id sp11_ov13858_of_match[] = {
	{ .compatible = "microsoft,sp11-ov13858-probe" },
	{ }
};
MODULE_DEVICE_TABLE(of, sp11_ov13858_of_match);

static const struct i2c_device_id sp11_ov13858_ids[] = {
	{ "sp11-ov13858-probe" },
	{ }
};
MODULE_DEVICE_TABLE(i2c, sp11_ov13858_ids);

static struct i2c_driver sp11_ov13858_driver = {
	.driver = {
		.name = "sp11-ov13858-probe",
		.of_match_table = sp11_ov13858_of_match,
	},
	.probe = sp11_ov13858_probe,
	.id_table = sp11_ov13858_ids,
};
module_i2c_driver(sp11_ov13858_driver);

MODULE_AUTHOR("SP11X1ECamera E002b");
MODULE_DESCRIPTION("SP11 rear OV13858 probe-only Windows power oracle");
MODULE_LICENSE("GPL");
