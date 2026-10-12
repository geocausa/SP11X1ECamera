// SPDX-License-Identifier: GPL-2.0-only
/* Dormant parent power ownership. No DT values, clock rates or DMA release. */
#include <linux/pm_runtime.h>
#include "camss-cdm-power.h"

int camss_cdm21_power_init(struct camss_cdm21_power *power,
			  struct camss_cdm21 *cdm, struct device *dev,
			  const struct clk_bulk_data *clocks, int num_clocks)
{
	int i, j, ret = 0;

	if (!power || !cdm || !dev || IS_ERR(dev) || !clocks || num_clocks <= 0)
		return -EINVAL;
	if (power->initialized)
		return -EBUSY;
	for (i = 0; i < num_clocks; i++) {
		if (!clocks[i].clk || IS_ERR(clocks[i].clk))
			return -EINVAL;
		for (j = 0; j < i; j++)
			if (clocks[j].clk == clocks[i].clk)
				return -EINVAL;
	}
	if (!cdm->initialized)
		return -EINVAL;
	mutex_lock(&cdm->lock);
	if (cdm->power_owner || cdm->active || cdm->reset.epoch ||
	    cdm->quarantined || !cdm->irq_disabled) {
		ret = -EBUSY;
		goto unlock;
	}
	power->cdm = cdm;
	power->dev = dev;
	power->clocks = clocks;
	power->num_clocks = num_clocks;
	mutex_init(&power->lock);
	power->initialized = true;
	cdm->power_owner = power;
unlock:
	mutex_unlock(&cdm->lock);
	return ret;
}

static int cdm21_power_hold_locked(struct camss_cdm21_power *power)
{
	int ret;

	if (power->fault || power->cdm->quarantined)
		return -EIO;
	if (power->cdm->power_owner != power)
		return -EPERM;
	if (power->held)
		return 0;
	ret = pm_runtime_resume_and_get(power->dev);
	if (ret < 0)
		return ret;
	ret = clk_bulk_prepare_enable(power->num_clocks, power->clocks);
	if (ret) {
		/* Bulk helper rolls back its partial clocks. Drop only our PM ref. */
		if (pm_runtime_put_sync(power->dev) < 0)
			power->fault = true;
		return ret;
	}
	power->held = true;
	return 0;
}

int camss_cdm21_power_hold(struct camss_cdm21_power *power)
{
	int ret;

	if (!power || !power->initialized)
		return -EINVAL;
	mutex_lock(&power->lock);
	ret = cdm21_power_hold_locked(power);
	mutex_unlock(&power->lock);
	return ret;
}

int camss_cdm21_power_reset(struct camss_cdm21_power *power)
{
	int ret;

	if (!power || !power->initialized)
		return -EINVAL;
	mutex_lock(&power->lock);
	ret = cdm21_power_hold_locked(power);
	if (!ret) {
		/* Even timeout or unsupported version must not drop power implicitly. */
		power->touched = true;
		ret = camss_cdm21_reset_paused_owned(power->cdm, power);
	}
	mutex_unlock(&power->lock);
	return ret;
}

int camss_cdm21_power_release_unused(struct camss_cdm21_power *power)
{
	int ret = 0;

	if (!power || !power->initialized)
		return -EINVAL;
	mutex_lock(&power->lock);
	if (power->touched || power->cdm->quarantined) {
		ret = -EBUSY;
		goto unlock;
	}
	if (power->cdm->power_owner != power) {
		ret = -EPERM;
		goto unlock;
	}
	if (power->held) {
		clk_bulk_disable_unprepare(power->num_clocks, power->clocks);
		ret = pm_runtime_put_sync(power->dev);
		power->held = false;
		if (ret < 0)
			power->fault = true;
		else
			ret = 0;
	}
unlock:
	mutex_unlock(&power->lock);
	return ret;
}
