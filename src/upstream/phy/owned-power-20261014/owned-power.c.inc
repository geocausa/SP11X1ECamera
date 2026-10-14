static int phy_qcom_mipi_csi2_release_owned(struct mipi_csi2phy_device *csi2phy)
{
	const struct mipi_csi2phy_hw_ops *ops = csi2phy->soc_cfg->ops;
	int i, ret;

	if (csi2phy->power_fault)
		return -EUCLEAN;

	if (csi2phy->irq_enabled) {
		disable_irq(csi2phy->irq);
		csi2phy->irq_enabled = false;
	}
	if (csi2phy->lanes_owned) {
		ops->lanes_disable(csi2phy, &csi2phy->stream_cfg);
		csi2phy->lanes_owned = false;
	}
	if (csi2phy->clocks_owned) {
		clk_bulk_disable_unprepare(csi2phy->soc_cfg->num_clk, csi2phy->clks);
		csi2phy->clocks_owned = false;
	}
	if (csi2phy->opp_owned) {
		ret = dev_pm_opp_set_rate(csi2phy->dev, 0);
		if (ret)
			goto fault;
		csi2phy->opp_owned = false;
	}
	for (i = csi2phy->pd_list->num_pds - 1; i >= 0; i--) {
		if (!(csi2phy->perf_owned & BIT(i)))
			continue;
		ret = dev_pm_genpd_set_performance_state(csi2phy->pd_list->pd_devs[i], 0);
		if (ret)
			goto fault;
		csi2phy->perf_owned &= ~BIT(i);
	}
	if (csi2phy->pm_owned) {
		ret = pm_runtime_put_sync(csi2phy->dev);
		csi2phy->pm_owned = false;
		if (ret < 0) {
			/* put consumed our count even when runtime suspend failed. */
			pm_runtime_get_noresume(csi2phy->dev);
			csi2phy->pm_owned = true;
			goto fault;
		}
	}
	while (csi2phy->supplies_owned) {
		i = csi2phy->supplies_owned - 1;
		ret = regulator_disable(csi2phy->supplies[i].consumer);
		if (ret)
			goto fault;
		csi2phy->supplies_owned--;
	}

	return 0;

fault:
	csi2phy->power_fault = true;
	/* Reboot-only quarantine also protects failed-start owned references. */
	if (!csi2phy->fault_module_held) {
		__module_get(THIS_MODULE);
		csi2phy->fault_module_held = true;
	}
	dev_err(csi2phy->dev, "PHY release failed: %d; ownership retained until reboot\n", ret);
	return ret;
}

static int phy_qcom_mipi_csi2_power_on(struct phy *phy)
{
	struct mipi_csi2phy_device *csi2phy = phy_get_drvdata(phy);
	const struct mipi_csi2phy_hw_ops *ops = csi2phy->soc_cfg->ops;
	int cleanup_ret, ret;
	unsigned int i;

	if (csi2phy->power_fault)
		return -EUCLEAN;
	if (csi2phy->supplies_owned || csi2phy->pm_owned || csi2phy->perf_owned ||
	    csi2phy->opp_owned || csi2phy->clocks_owned || csi2phy->lanes_owned ||
	    csi2phy->irq_enabled)
		return -EBUSY;

	if (csi2phy->phy_mode == PHY_MODE_MIPI_CPHY) {
		ret = mipi_csi2phy_cphy_validate(csi2phy, &csi2phy->stream_cfg);
		if (ret)
			return ret;
		if (csi2phy->irq <= 0)
			return -ENODEV;
	}

	for (i = 0; i < csi2phy->soc_cfg->num_supplies; i++) {
		ret = regulator_enable(csi2phy->supplies[i].consumer);
		if (ret)
			goto unwind;
		csi2phy->supplies_owned++;
	}
	ret = pm_runtime_resume_and_get(csi2phy->dev);
	if (ret < 0)
		goto unwind;
	csi2phy->pm_owned = true;

	ret = phy_qcom_mipi_csi2_set_clock_rates(csi2phy, csi2phy->stream_cfg.link_freq);
	if (ret)
		goto unwind;
	ret = clk_bulk_prepare_enable(csi2phy->soc_cfg->num_clk, csi2phy->clks);
	if (ret)
		goto unwind;
	csi2phy->clocks_owned = true;

	if (csi2phy->phy_mode != PHY_MODE_MIPI_CPHY) {
		ops->reset(csi2phy);
		ops->hw_version_read(csi2phy);
	}
	ret = ops->lanes_enable(csi2phy, &csi2phy->stream_cfg);
	if (ret)
		goto unwind;
	csi2phy->lanes_owned = true;

	if (csi2phy->phy_mode == PHY_MODE_MIPI_CPHY) {
		enable_irq(csi2phy->irq);
		csi2phy->irq_enabled = true;
	}
	return 0;

unwind:
	cleanup_ret = phy_qcom_mipi_csi2_release_owned(csi2phy);
	if (cleanup_ret) {
		dev_err(csi2phy->dev, "PHY start error %d, cleanup error %d\n", ret, cleanup_ret);
		/* Tell CAMSS the failed stage retained resources, before VB2 cancels. */
		return -EUCLEAN;
	}
	return ret;
}

static int phy_qcom_mipi_csi2_power_off(struct phy *phy)
{
	return phy_qcom_mipi_csi2_release_owned(phy_get_drvdata(phy));
}
