// SPDX-License-Identifier: GPL-2.0
/* SP11 rear-camera MCLK diagnostic: deliberately never enables the clock. */
#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/clk.h>

#define TARGET_HZ 19200000UL

static int sp11_mclk_diag_probe(struct i2c_client *client)
{
	struct device *dev = &client->dev;
	struct clk *xclk, *parent;
	unsigned long before, after, parent_rate = 0;
	long rounded;
	int ret;

	xclk = devm_clk_get(dev, "xclk");
	if (IS_ERR(xclk))
		return dev_err_probe(dev, PTR_ERR(xclk), "DIAG: devm_clk_get(xclk) failed\n");

	before = clk_get_rate(xclk);
	parent = clk_get_parent(xclk);
	if (parent)
		parent_rate = clk_get_rate(parent);
	rounded = clk_round_rate(xclk, TARGET_HZ);
	dev_info(dev, "DIAG: before=%lu target=%lu round=%ld parent_rate=%lu\n",
		 before, TARGET_HZ, rounded, parent_rate);

	ret = clk_set_rate(xclk, TARGET_HZ);
	after = clk_get_rate(xclk);
	dev_info(dev, "DIAG: branch clk_set_rate(%lu) ret=%d after=%lu; clock NOT enabled\n",
		 TARGET_HZ, ret, after);

	if (parent) {
		long parent_round = clk_round_rate(parent, TARGET_HZ);
		int parent_ret = clk_set_rate(parent, TARGET_HZ);
		unsigned long parent_after = clk_get_rate(parent);
		unsigned long branch_after_parent = clk_get_rate(xclk);
		int branch_retry = clk_set_rate(xclk, TARGET_HZ);
		dev_info(dev, "DIAG: parent round=%ld set_ret=%d parent_after=%lu branch_after_parent=%lu branch_retry_ret=%d branch_final=%lu; branch NEVER enabled\n",
			 parent_round, parent_ret, parent_after, branch_after_parent, branch_retry, clk_get_rate(xclk));
	}

	/* Bind successfully so the result remains inspectable. Never prepare/enable. */
	return 0;
}

static const struct of_device_id sp11_mclk_diag_of_match[] = {
	{ .compatible = "microsoft,sp11-ov13858-probe" },
	{ }
};
MODULE_DEVICE_TABLE(of, sp11_mclk_diag_of_match);

static struct i2c_driver sp11_mclk_diag_driver = {
	.driver = {
		.name = "sp11-mclk-diag",
		.of_match_table = sp11_mclk_diag_of_match,
	},
	.probe = sp11_mclk_diag_probe,
};
module_i2c_driver(sp11_mclk_diag_driver);

MODULE_DESCRIPTION("SP11 rear MCLK rate-only diagnostic; never enables clock");
MODULE_LICENSE("GPL");
