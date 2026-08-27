// SPDX-License-Identifier: GPL-2.0
/*
 * SP11 E003b probe-only Sony IMX681 power/identity oracle.
 *
 * Deliberately NOT a camera/V4L2 driver. It reproduces the Windows-derived
 * Surface front-camera D0 ordering only far enough to read silicon identity,
 * then immediately tears power down in Windows D3 order. No CSI endpoint is
 * present in E003b, so streaming is impossible.
 */
#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/regulator/consumer.h>

#define IMX681_ID_REG           0x0004
#define IMX681_ID_EXPECTED      0x0aff
#define SP11_XCLK_HZ            19200000UL

struct sp11_imx681_probe {
	struct regulator *ldo3m;
	struct regulator *ldo7b;
	struct clk *xclk;
	struct gpio_desc *reset;
	bool clock_on;
	bool ldo3m_on;
	bool ldo7b_on;
};

static void sp11_imx681_power_off(struct sp11_imx681_probe *p)
{
	/* Windows D3: reset low, delay 1, MCLK4 off, LDO7_B off, LDO3_M off. */
	gpiod_set_value_cansleep(p->reset, 1); /* active-low => physical low */
	usleep_range(1000, 1500);

	if (p->clock_on) {
		clk_disable_unprepare(p->xclk);
		p->clock_on = false;
	}
	if (p->ldo7b_on) {
		regulator_disable(p->ldo7b);
		p->ldo7b_on = false;
	}
	if (p->ldo3m_on) {
		regulator_disable(p->ldo3m);
		p->ldo3m_on = false;
	}
}

static int sp11_imx681_power_on(struct device *dev,
				struct sp11_imx681_probe *p)
{
	int ret;

	/* Reset was acquired asserted. Windows next enables MCLK4 at 19.2 MHz. */
	ret = clk_set_rate(p->xclk, SP11_XCLK_HZ);
	if (ret)
		return dev_err_probe(dev, ret, "set MCLK4 19.2 MHz failed\n");
	if (clk_get_rate(p->xclk) != SP11_XCLK_HZ)
		return dev_err_probe(dev, -EINVAL,
				     "MCLK4 rate is %lu, expected %lu\n",
				     clk_get_rate(p->xclk), SP11_XCLK_HZ);

	ret = clk_prepare_enable(p->xclk);
	if (ret)
		return dev_err_probe(dev, ret, "enable MCLK4 failed\n");
	p->clock_on = true;

	ret = regulator_enable(p->ldo3m); /* Windows LDO3_M = 1.8 V */
	if (ret)
		goto err;
	p->ldo3m_on = true;

	ret = regulator_enable(p->ldo7b); /* Windows LDO7_B = 2.8 V */
	if (ret)
		goto err;
	p->ldo7b_on = true;

	/* AeoB DELAY 1. Keep conservative 1 ms identity-gate timing. */
	usleep_range(1000, 1500);
	gpiod_set_value_cansleep(p->reset, 0); /* release reset => physical high */
	/* AeoB DELAY 10. Keep conservative 10 ms before first CCI read. */
	usleep_range(10000, 12000);
	return 0;

err:
	sp11_imx681_power_off(p);
	return ret;
}

static int sp11_imx681_read_id(struct i2c_client *client, u16 *id)
{
	u8 addr[2] = { IMX681_ID_REG >> 8, IMX681_ID_REG & 0xff };
	u8 data[2] = { 0 };
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

	*id = ((u16)data[0] << 8) | data[1];
	return 0;
}

static int sp11_imx681_probe(struct i2c_client *client)
{
	struct device *dev = &client->dev;
	struct sp11_imx681_probe *p;
	u16 id = 0;
	int ret;

	p = devm_kzalloc(dev, sizeof(*p), GFP_KERNEL);
	if (!p)
		return -ENOMEM;

	p->ldo3m = devm_regulator_get(dev, "ldo3m");
	if (IS_ERR(p->ldo3m))
		return dev_err_probe(dev, PTR_ERR(p->ldo3m), "get LDO3_M failed\n");
	p->ldo7b = devm_regulator_get(dev, "ldo7b");
	if (IS_ERR(p->ldo7b))
		return dev_err_probe(dev, PTR_ERR(p->ldo7b), "get LDO7_B failed\n");
	p->xclk = devm_clk_get(dev, "xclk");
	if (IS_ERR(p->xclk))
		return dev_err_probe(dev, PTR_ERR(p->xclk), "get MCLK4 failed\n");

	/* GPIO_ACTIVE_LOW makes logical 1 = physical low/asserted. */
	p->reset = devm_gpiod_get(dev, "reset", GPIOD_OUT_HIGH);
	if (IS_ERR(p->reset))
		return dev_err_probe(dev, PTR_ERR(p->reset), "get GPIO237 reset failed\n");

	ret = regulator_set_voltage(p->ldo3m, 1800000, 1800000);
	if (ret)
		return dev_err_probe(dev, ret, "set LDO3_M 1.8 V failed\n");
	ret = regulator_set_voltage(p->ldo7b, 2800000, 2800000);
	if (ret)
		return dev_err_probe(dev, ret, "set LDO7_B 2.8 V failed\n");

	ret = sp11_imx681_power_on(dev, p);
	if (ret)
		return ret;

	ret = sp11_imx681_read_id(client, &id);
	if (ret)
		dev_err(dev, "SP11 E003b: chip-ID transfer failed: %d\n", ret);
	else if (id != IMX681_ID_EXPECTED) {
		dev_err(dev, "SP11 E003b: chip-ID mismatch: read 0x%04x expected 0x%04x\n",
			id, IMX681_ID_EXPECTED);
		ret = -ENODEV;
	} else {
		dev_info(dev, "SP11 E003b PASS: IMX681 chip ID 0x%04x at 0x%02x\n",
			 id, client->addr);
	}

	sp11_imx681_power_off(p);
	dev_info(dev, "SP11 E003b: probe power sequence torn down\n");
	return ret;
}

static const struct of_device_id sp11_imx681_of_match[] = {
	{ .compatible = "microsoft,sp11-imx681-probe" },
	{ }
};
MODULE_DEVICE_TABLE(of, sp11_imx681_of_match);

static const struct i2c_device_id sp11_imx681_ids[] = {
	{ "sp11-imx681-probe" },
	{ }
};
MODULE_DEVICE_TABLE(i2c, sp11_imx681_ids);

static struct i2c_driver sp11_imx681_driver = {
	.driver = {
		.name = "sp11-imx681-probe",
		.of_match_table = sp11_imx681_of_match,
	},
	.probe = sp11_imx681_probe,
	.id_table = sp11_imx681_ids,
};
module_i2c_driver(sp11_imx681_driver);

MODULE_AUTHOR("SP11X1ECamera E003b");
MODULE_DESCRIPTION("SP11 front IMX681 probe-only Windows power oracle");
MODULE_LICENSE("GPL");
