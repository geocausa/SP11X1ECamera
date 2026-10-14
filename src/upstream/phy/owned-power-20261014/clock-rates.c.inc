static int
phy_qcom_mipi_csi2_set_clock_rates(struct mipi_csi2phy_device *csi2phy,
				   s64 link_freq)
{
	struct device *dev = csi2phy->dev;
	unsigned long opp_rate = link_freq / 4;
	struct dev_pm_opp *opp;
	long timer_rate;
	int i, pstate = 0;
	int ret;

	if (csi2phy->phy_mode == PHY_MODE_MIPI_CPHY)
		opp_rate = csi2phy->soc_cfg->cphy_core_rate;

	opp = dev_pm_opp_find_freq_ceil(dev, &opp_rate);
	if (IS_ERR(opp))
		return PTR_ERR(opp);

	if (csi2phy->phy_mode == PHY_MODE_MIPI_CPHY &&
	    opp_rate != csi2phy->soc_cfg->cphy_core_rate) {
		dev_pm_opp_put(opp);
		return -ERANGE;
	}

	for (i = 0; i < csi2phy->pd_list->num_pds; i++) {
		unsigned int perf;

		if (!csi2phy->soc_cfg->genpds[i].scaled)
			continue;
		perf = dev_pm_opp_get_required_pstate(opp, pstate++);
		ret = dev_pm_genpd_set_performance_state(csi2phy->pd_list->pd_devs[i], perf);
		if (ret) {
			dev_pm_opp_put(opp);
			return ret;
		}
		csi2phy->perf_owned |= BIT(i);
	}
	dev_pm_opp_put(opp);

	ret = dev_pm_opp_set_rate(dev, opp_rate);
	if (ret)
		return ret;
	csi2phy->opp_owned = true;

	timer_rate = clk_round_rate(csi2phy->timer_clk,
				    csi2phy->phy_mode == PHY_MODE_MIPI_CPHY ?
				    csi2phy->soc_cfg->cphy_timer_rate : link_freq / 4);
	if (timer_rate <= 0)
		return -ENODEV;
	if (csi2phy->phy_mode == PHY_MODE_MIPI_CPHY &&
	    timer_rate != csi2phy->soc_cfg->cphy_timer_rate)
		return -ERANGE;

	ret = clk_set_rate(csi2phy->timer_clk, timer_rate);
	if (ret)
		return ret;
	csi2phy->timer_clk_rate = timer_rate;

	return 0;
}
