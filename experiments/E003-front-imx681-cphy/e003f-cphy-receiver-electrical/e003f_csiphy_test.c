// SPDX-License-Identifier: GPL-2.0
/* SP11 E003f: direct receiver-only CSIPHY2 C-PHY electrical verifier. */
#include <linux/device.h>
#include <linux/io.h>
#include <linux/ioport.h>
#include <linux/module.h>
#include <linux/platform_device.h>
#include <media/v4l2-subdev.h>
#include "camss.h"
#include "csiphy2-windows-final.h"

#define E003F_PHY_ID 2
#define E003F_COMMON_CTRL5 0x1014
#define E003F_COMMON_CTRL6 0x1018

static int __init e003f_test_init(void)
{
	struct device *dev;
	struct platform_device *pdev;
	struct resource *res;
	struct camss *camss;
	struct csiphy_device *phy;
	struct vfe_device *vfe;
	struct v4l2_subdev *sd, *vfe_sd;
	unsigned int i, mismatches = 0;
	bool host_powered = false, powered = false, streamed = false;
	int ret = 0, off_ret;
	u32 actual;

	dev = bus_find_device_by_name(&platform_bus_type, NULL, "acb7000.isp");
	if (!dev)
		return -ENODEV;
	pdev = to_platform_device(dev);
	res = platform_get_resource_byname(pdev, IORESOURCE_MEM, "csiphy2");
	if (!res || resource_size(res) < 0x2000) {
		pr_err("E003F_PREFLIGHT_FAIL: csiphy2 MMIO size=0x%llx, need >=0x2000\n",
		       res ? (unsigned long long)resource_size(res) : 0ULL);
		ret = -EINVAL;
		goto out_put;
	}
	pr_info("E003F_MMIO_PREFLIGHT_PASS: csiphy2 start=%pa size=0x%llx\n",
		 &res->start, (unsigned long long)resource_size(res));

	camss = dev_get_drvdata(dev);
	if (!camss || !camss->csiphy || camss->res->csiphy_num <= E003F_PHY_ID) {
		ret = -ENODEV;
		goto out_put;
	}
	phy = &camss->csiphy[E003F_PHY_ID];
	sd = &phy->subdev;
	if (!camss->vfe || camss->res->vfe_num < 1 || !camss->vfe[0].line) {
		ret = -ENODEV;
		goto out_put;
	}
	vfe = &camss->vfe[0];
	vfe_sd = &vfe->line[0].subdev;
	if (phy->id != E003F_PHY_ID || !phy->base || !phy->cfg.csi2) {
		ret = -EINVAL;
		goto out_put;
	}
	if (phy->cfg.csi2->lane_cfg.phy_cfg != V4L2_MBUS_CSI2_CPHY ||
	    phy->cfg.csi2->lane_cfg.num_data != 1 ||
	    phy->cfg.csi2->lane_cfg.data[0].pos != 0) {
		pr_err("E003F_PREFLIGHT_FAIL: phy=%u cfg=%u trios=%d pos0=%u\n",
		       phy->id, phy->cfg.csi2->lane_cfg.phy_cfg,
		       phy->cfg.csi2->lane_cfg.num_data,
		       phy->cfg.csi2->lane_cfg.data[0].pos);
		ret = -EINVAL;
		goto out_put;
	}
	pr_info("E003F_PREFLIGHT_PASS: csiphy=%u CPHY trios=1 pos0=0 expected_regs=%zu\n",
		phy->id, ARRAY_SIZE(e003f_windows_expected));

	/*
	 * Normal CAMSS pipeline power brings up a VFE parent before CSID/PHY
	 * activity.  Reproduce only that host-side prerequisite here: no CSID
	 * stream and no sensor callback are invoked.  VFE0 supplies the X1E
	 * IFE domain plus CAMNOC/CPAS AHB clock context needed by CSIPHY MMIO.
	 */
	ret = v4l2_subdev_call(vfe_sd, core, s_power, 1);
	if (ret < 0) {
		pr_err("E003F_HOST_POWER_ON_FAIL: ret=%d\n", ret);
		goto out_put;
	}
	host_powered = true;
	pr_info("E003F_HOST_POWER_ON_PASS: vfe0 power_count=%d\n", vfe->power_count);

	ret = v4l2_subdev_call(sd, core, s_power, 1);
	if (ret < 0) {
		pr_err("E003F_POWER_ON_FAIL: ret=%d\n", ret);
		goto out_put;
	}
	powered = true;
	pr_info("E003F_POWER_ON_PASS: timer_clk_rate=%u\n", phy->timer_clk_rate);

	ret = v4l2_subdev_call(sd, video, s_stream, 1);
	if (ret < 0) {
		pr_err("E003F_STREAM_ON_FAIL: ret=%d\n", ret);
		goto out_unwind;
	}
	streamed = true;

	for (i = 0; i < ARRAY_SIZE(e003f_windows_expected); i++) {
		actual = readl_relaxed(phy->base + e003f_windows_expected[i].off);
		if (actual != e003f_windows_expected[i].val) {
			if (mismatches < 12)
				pr_err("E003F_MMIO_MISMATCH: off=0x%04x actual=0x%08x expected=0x%08x\n",
				       e003f_windows_expected[i].off, actual,
				       e003f_windows_expected[i].val);
			mismatches++;
		}
	}
	pr_info("E003F_LIVE_COMPARE: expected=%zu mismatches=%u ctrl5=0x%08x ctrl6=0x%08x ctrl7=0x%08x\n",
		ARRAY_SIZE(e003f_windows_expected), mismatches,
		readl_relaxed(phy->base + 0x1014), readl_relaxed(phy->base + 0x1018),
		readl_relaxed(phy->base + 0x101c));
	if (mismatches) {
		ret = -EIO;
		goto out_unwind;
	}

	v4l2_subdev_call(sd, video, s_stream, 0);
	streamed = false;
	if (readl_relaxed(phy->base + E003F_COMMON_CTRL5) != 0 ||
	    readl_relaxed(phy->base + E003F_COMMON_CTRL6) != 0) {
		pr_err("E003F_STREAM_OFF_FAIL: ctrl5=0x%08x ctrl6=0x%08x\n",
		       readl_relaxed(phy->base + E003F_COMMON_CTRL5),
		       readl_relaxed(phy->base + E003F_COMMON_CTRL6));
		ret = -EIO;
		goto out_unwind;
	}
	pr_info("E003F_STREAM_OFF_PASS: ctrl5=0 ctrl6=0\n");

out_unwind:
	if (streamed)
		v4l2_subdev_call(sd, video, s_stream, 0);
	if (powered) {
		off_ret = v4l2_subdev_call(sd, core, s_power, 0);
		if (off_ret < 0 && !ret)
			ret = off_ret;
		powered = false;
	}
	if (host_powered) {
		off_ret = v4l2_subdev_call(vfe_sd, core, s_power, 0);
		if (off_ret < 0 && !ret)
			ret = off_ret;
		host_powered = false;
		pr_info("E003F_HOST_POWER_OFF: vfe0 power_count=%d\n", vfe->power_count);
	}
	if (!ret)
		pr_info("E003F_RECEIVER_ONLY_PASS: 121/121 Windows-live registers exact; receiver stopped and powered off\n");
out_put:
	put_device(dev);
	return ret;
}
static void __exit e003f_test_exit(void) {}
module_init(e003f_test_init);
module_exit(e003f_test_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("SP11 E003f receiver-only X1E CSIPHY2 C-PHY verifier");
