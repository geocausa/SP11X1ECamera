// SPDX-License-Identifier: GPL-2.0-only
/* Bounded standalone PHY API diagnostic; never starts CAMSS or the sensor. */
#include <linux/delay.h>
#include <linux/err.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/phy/phy.h>

#define CYCLE_COUNT 3
static bool execute;
module_param(execute, bool, 0400);
static int result;
module_param(result, int, 0444);
static unsigned int completed;
module_param(completed, uint, 0444);
static unsigned int stage;
module_param(stage, uint, 0444);
static unsigned int pinned;
module_param(pinned, uint, 0444);

static struct phy *owned_phy;
static bool initialized;
static bool powered;

static void quarantine(int error)
{
	result = error;
	pinned = 1;
	__module_get(THIS_MODULE);
	pr_err("SP11_PHY_OWNED_CYCLE fault stage=%u error=%d; held until reboot\n",
	       stage, error);
}

static int __init sp11_phy_owned_cycle_init(void)
{
	union phy_configure_opts opts = { };
	struct device_node *np;
	unsigned int i;
	int ret;

	if (!execute)
		return -EPERM;

	stage = 1;
	np = of_find_node_by_path("/soc@0/phy@ace8000");
	if (!np) {
		result = -ENODEV;
		return 0;
	}
	if (!of_device_is_available(np) ||
	    !of_device_is_compatible(np, "qcom,x1e80100-csi2-phy")) {
		of_node_put(np);
		result = -EINVAL;
		return 0;
	}
	owned_phy = phy_get_by_of_node(np);
	of_node_put(np);
	if (IS_ERR(owned_phy)) {
		result = PTR_ERR(owned_phy);
		owned_phy = NULL;
		return 0;
	}

	mutex_lock(&owned_phy->mutex);
	ret = owned_phy->power_count ? -EBUSY : 0;
	mutex_unlock(&owned_phy->mutex);
	if (ret)
		goto clean_failure;

	stage = 2;
	ret = phy_init(owned_phy);
	if (ret)
		goto clean_failure;
	initialized = true;
	stage = 3;
	ret = phy_set_mode(owned_phy, PHY_MODE_MIPI_CPHY);
	if (ret)
		goto clean_failure;
	opts.mipi_cphy.num_trios = 1;
	opts.mipi_cphy.symbol_rate = 2406000000ULL;
	stage = 4;
	ret = phy_configure(owned_phy, &opts);
	if (ret)
		goto clean_failure;

	for (i = 0; i < CYCLE_COUNT; i++) {
		stage = 5;
		ret = phy_power_on(owned_phy);
		if (ret) {
			if (ret == -EUCLEAN) {
				quarantine(ret);
				return 0;
			}
			goto clean_failure;
		}
		powered = true;
		msleep(20);
		stage = 6;
		ret = phy_power_off(owned_phy);
		if (ret) {
			quarantine(ret);
			return 0;
		}
		powered = false;
		completed++;
	}

	stage = 7;
	ret = phy_exit(owned_phy);
	if (ret) {
		quarantine(ret);
		return 0;
	}
	initialized = false;
	stage = 8;
	of_phy_put(owned_phy);
	owned_phy = NULL;
	stage = 9;
	result = 1;
	pr_info("SP11_PHY_OWNED_CYCLE PASS cycles=%u no_sensor_stream no_camss_stream\n",
		completed);
	return 0;

clean_failure:
	result = ret;
	if (ret == -EUCLEAN || powered) {
		quarantine(ret);
		return 0;
	}
	if (initialized) {
		ret = phy_exit(owned_phy);
		if (ret) {
			quarantine(ret);
			return 0;
		}
		initialized = false;
	}
	of_phy_put(owned_phy);
	owned_phy = NULL;
	return 0;
}

static void __exit sp11_phy_owned_cycle_exit(void)
{
	/* Successful/clean-failure init released only its own references. */
}

module_init(sp11_phy_owned_cycle_init);
module_exit(sp11_phy_owned_cycle_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Bounded SP11 standalone PHY owned-power-cycle diagnostic");
