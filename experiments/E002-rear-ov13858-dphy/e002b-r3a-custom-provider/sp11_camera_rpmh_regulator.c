// SPDX-License-Identifier: GPL-2.0
/*
 * SP11 camera-only RPMh regulator provider.
 *
 * Bring-up shim for the four Surface Pro 11 camera resources that are absent
 * from the Golden Linux regulator topology.  It deliberately lives in a
 * separate DT provider under the RPMh RSC so failures cannot remove any
 * existing Golden PM8550 regulator provider.
 */
#include <linux/module.h>
#include <linux/of.h>
#include <linux/platform_device.h>
#include <linux/regulator/driver.h>
#include <linux/regulator/machine.h>
#include <soc/qcom/cmd-db.h>
#include <soc/qcom/rpmh.h>

#define SP11_VRM_VOLTAGE 0x0
#define SP11_VRM_ENABLE  0x4
#define SP11_VRM_MODE    0x8

struct sp11_camera_rail {
	struct device *dev;
	struct regulator_desc desc;
	struct regulator_dev *rdev;
	const char *resource;
	const char *name;
	u32 target_uv;
	u32 mode;
	u32 addr;
	int cached_uv;
	bool enabled;
};

struct sp11_camera_provider {
	struct sp11_camera_rail *rails;
	unsigned int nrails;
};

static int sp11_rail_write(struct sp11_camera_rail *rail,
			   struct tcs_cmd *cmd, u32 n)
{
	/* rail->dev is the provider platform device; its parent is the RPMh RSC. */
	return rpmh_write(rail->dev, RPMH_ACTIVE_ONLY_STATE, cmd, n);
}

static int sp11_rail_set_voltage(struct regulator_dev *rdev, int min_uv,
				 int max_uv, unsigned int *selector)
{
	struct sp11_camera_rail *rail = rdev_get_drvdata(rdev);
	struct tcs_cmd cmd;
	int ret;

	if (rail->target_uv < min_uv || rail->target_uv > max_uv)
		return -EINVAL;

	if (selector)
		*selector = 0;

	/* Cache while off. The first enable sends voltage + HPM mode + enable. */
	if (!rail->enabled) {
		rail->cached_uv = rail->target_uv;
		return 0;
	}

	cmd.addr = rail->addr + SP11_VRM_VOLTAGE;
	cmd.data = DIV_ROUND_UP(rail->target_uv, 1000);
	cmd.wait = 0;
	ret = sp11_rail_write(rail, &cmd, 1);
	if (!ret)
		rail->cached_uv = rail->target_uv;
	return ret;
}

static int sp11_rail_get_voltage(struct regulator_dev *rdev)
{
	struct sp11_camera_rail *rail = rdev_get_drvdata(rdev);

	return rail->cached_uv > 0 ? rail->cached_uv : -ENOTRECOVERABLE;
}

static int sp11_rail_enable(struct regulator_dev *rdev)
{
	struct sp11_camera_rail *rail = rdev_get_drvdata(rdev);
	struct tcs_cmd cmd[3] = { };
	int ret;

	if (rail->cached_uv <= 0)
		return -EINVAL;

	cmd[0].addr = rail->addr + SP11_VRM_VOLTAGE;
	cmd[0].data = DIV_ROUND_UP(rail->cached_uv, 1000);
	cmd[1].addr = rail->addr + SP11_VRM_MODE;
	cmd[1].data = rail->mode;
	cmd[2].addr = rail->addr + SP11_VRM_ENABLE;
	cmd[2].data = 1;

	ret = sp11_rail_write(rail, cmd, ARRAY_SIZE(cmd));
	if (!ret) {
		rail->enabled = true;
		dev_info(rail->dev, "%s enabled %duV mode=%u\n",
			 rail->name, rail->cached_uv, rail->mode);
	}
	return ret;
}

static int sp11_rail_disable(struct regulator_dev *rdev)
{
	struct sp11_camera_rail *rail = rdev_get_drvdata(rdev);
	struct tcs_cmd cmd = {
		.addr = rail->addr + SP11_VRM_ENABLE,
		.data = 0,
	};
	int ret;

	ret = sp11_rail_write(rail, &cmd, 1);
	if (!ret) {
		rail->enabled = false;
		dev_info(rail->dev, "%s disabled\n", rail->name);
	}
	return ret;
}

static int sp11_rail_is_enabled(struct regulator_dev *rdev)
{
	struct sp11_camera_rail *rail = rdev_get_drvdata(rdev);

	return rail->enabled;
}

static const struct regulator_ops sp11_camera_reg_ops = {
	.set_voltage = sp11_rail_set_voltage,
	.get_voltage = sp11_rail_get_voltage,
	.enable = sp11_rail_enable,
	.disable = sp11_rail_disable,
	.is_enabled = sp11_rail_is_enabled,
};

static int sp11_camera_rpmh_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct sp11_camera_provider *provider;
	struct device_node *child;
	unsigned int i = 0, count;

	if (!dev->parent)
		return dev_err_probe(dev, -ENODEV, "RPMh RSC parent missing\n");

	count = of_get_available_child_count(dev->of_node);
	if (!count)
		return dev_err_probe(dev, -EINVAL, "no camera rail children\n");

	provider = devm_kzalloc(dev, sizeof(*provider), GFP_KERNEL);
	if (!provider)
		return -ENOMEM;
	provider->rails = devm_kcalloc(dev, count, sizeof(*provider->rails),
				      GFP_KERNEL);
	if (!provider->rails)
		return -ENOMEM;
	provider->nrails = count;
	platform_set_drvdata(pdev, provider);

	for_each_available_child_of_node(dev->of_node, child) {
		struct sp11_camera_rail *rail = &provider->rails[i++];
		struct regulator_init_data init = { };
		struct regulator_config cfg = { };
		int ret;

		rail->dev = dev;
		ret = of_property_read_string(child, "microsoft,rpmh-resource",
					      &rail->resource);
		if (ret)
			return dev_err_probe(dev, ret,
					     "%pOF: missing rpmh resource\n", child);
		ret = of_property_read_string(child, "regulator-name", &rail->name);
		if (ret)
			rail->name = child->name;
		ret = of_property_read_u32(child, "microsoft,target-microvolt",
					   &rail->target_uv);
		if (ret)
			return dev_err_probe(dev, ret,
					     "%s: missing target voltage\n", rail->name);
		if (of_property_read_u32(child, "microsoft,vrm-mode", &rail->mode))
			rail->mode = 7; /* PMIC5 HPM, matches Windows PMICVREGVOTE. */

		rail->addr = cmd_db_read_addr(rail->resource);
		if (!rail->addr)
			return dev_err_probe(dev, -ENOENT,
					     "%s: cmd-db resource %s not found\n",
					     rail->name, rail->resource);

		rail->desc.name = rail->name;
		rail->desc.id = i - 1;
		rail->desc.ops = &sp11_camera_reg_ops;
		rail->desc.type = REGULATOR_VOLTAGE;
		rail->desc.owner = THIS_MODULE;
		/* Intentionally no of_match: keep programmatic init_data below. */

		init.constraints.name = rail->name;
		init.constraints.min_uV = rail->target_uv;
		init.constraints.max_uV = rail->target_uv;
		init.constraints.valid_ops_mask = REGULATOR_CHANGE_VOLTAGE |
						  REGULATOR_CHANGE_STATUS;
		init.constraints.apply_uV = false;

		cfg.dev = dev;
		cfg.driver_data = rail;
		cfg.init_data = &init;
		cfg.of_node = child;

		rail->rdev = devm_regulator_register(dev, &rail->desc, &cfg);
		if (IS_ERR(rail->rdev))
			return dev_err_probe(dev, PTR_ERR(rail->rdev),
					     "%s: regulator register failed\n",
					     rail->name);

		dev_info(dev, "%s ready resource=%s addr=0x%08x target=%uuV mode=%u (no vote sent)\n",
			 rail->name, rail->resource, rail->addr,
			 rail->target_uv, rail->mode);
	}

	dev_info(dev, "SP11 camera RPMh provider ready: %u rails, no votes sent\n",
		 provider->nrails);
	return 0;
}

static const struct of_device_id sp11_camera_rpmh_of_match[] = {
	{ .compatible = "microsoft,sp11-camera-rpmh-regulators" },
	{ }
};
MODULE_DEVICE_TABLE(of, sp11_camera_rpmh_of_match);

static struct platform_driver sp11_camera_rpmh_driver = {
	.probe = sp11_camera_rpmh_probe,
	.driver = {
		.name = "sp11-camera-rpmh-regulator",
		.of_match_table = sp11_camera_rpmh_of_match,
	},
};
module_platform_driver(sp11_camera_rpmh_driver);

MODULE_DESCRIPTION("SP11 camera-only RPMh regulator provider");
MODULE_AUTHOR("SP11X1ECamera project");
MODULE_LICENSE("GPL");
