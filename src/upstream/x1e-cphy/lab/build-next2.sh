#!/bin/sh
# Build linux-next's CAMSS and qcom-mipi-csi2 PHY driver as external modules for the running 7.1.5 kernel.
# Test-only compat: drop the media-next v4l2_subdev_client_info pad-op argument, add a 7.1-missing helper.
# Usage: build-next.sh [src-dir-with-patched-files]  (defaults to linux-next-sparse)
P=/home/geoca/Documents/SP11-PROJECT
N=${1:-$P/06-camera/linux-next-sparse}
B=${B:-/root/imx681-test/next2}
rm -rf $B; mkdir -p $B/camss $B/phy
cp $N/drivers/media/platform/qcom/camss/*.c $N/drivers/media/platform/qcom/camss/*.h $B/camss/
sed 's/^obj-\$(CONFIG_VIDEO_QCOM_CAMSS)/obj-m/' $N/drivers/media/platform/qcom/camss/Makefile > $B/camss/Makefile
cp $N/drivers/phy/qualcomm/phy-qcom-mipi-csi2* $B/phy/
cat >> $B/phy/phy-qcom-mipi-csi2-core.c <<'EOF2'

/* SP11 lab test shim only: 7.1 has no devm_phy_get_by_of_node(); camss test build calls this. */
#include <linux/of_platform.h>
struct phy *sp11_test_csi2phy_get(struct device_node *np)
{
	struct platform_device *pdev = of_find_device_by_node(np);
	struct mipi_csi2phy_device *csi2phy;

	if (!pdev)
		return ERR_PTR(-EPROBE_DEFER);
	csi2phy = platform_get_drvdata(pdev);
	put_device(&pdev->dev);
	if (!csi2phy || !csi2phy->phy)
		return ERR_PTR(-EPROBE_DEFER);
	return csi2phy->phy;
}
EXPORT_SYMBOL_GPL(sp11_test_csi2phy_get);
EOF2
python3 - $B/phy/phy-qcom-mipi-csi2-3ph-dphy.c <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
old="\tsettle_cnt = phy_qcom_mipi_csi2_settle_cnt_calc(cfg->link_freq, csi2phy->timer_clk_rate);\n"
assert s.count(old)==1
s=s.replace(old, old + "\tdev_info(csi2phy->dev, \"SP11 test: mode %u link %lld timer %u settle %u (override %u)\\n\", csi2phy->phy_mode, cfg->link_freq, csi2phy->timer_clk_rate, settle_cnt, test_settle);\n\tif (test_settle)\n\t\tsettle_cnt = test_settle;\n")
s=s.replace('#include "phy-qcom-mipi-csi2.h"\n', '#include "phy-qcom-mipi-csi2.h"\n#include <linux/moduleparam.h>\nstatic unsigned int test_settle;\nmodule_param(test_settle, uint, 0644);\n',1)
open(p,'w').write(s)
PY
printf 'obj-m := phy-qcom-mipi-csi2.o\nphy-qcom-mipi-csi2-objs := phy-qcom-mipi-csi2-core.o phy-qcom-mipi-csi2-3ph-dphy.o\n' > $B/phy/Makefile
cat > $B/compat.h <<'EOF'
#include <linux/phy/phy.h>
#include <linux/of.h>
struct phy *sp11_test_csi2phy_get(struct device_node *np);
#define devm_phy_get_by_of_node(dev, np) sp11_test_csi2phy_get(np)
#include <linux/property.h>
#include <linux/cleanup.h>
#ifndef fwnode_graph_for_each_endpoint_scoped
#define fwnode_graph_for_each_endpoint_scoped(fwnode, child)			\
	for (struct fwnode_handle *child __free(fwnode_handle) =		\
		fwnode_graph_get_next_endpoint(fwnode, NULL);			\
	     child; child = fwnode_graph_get_next_endpoint(fwnode, child))
#endif
EOF
for f in $B/camss/*.c; do
  sed -i -e '/^[[:space:]]*const struct v4l2_subdev_client_info \*ci,$/d' \
         -e 's/const struct v4l2_subdev_client_info \*ci, //' -e 's/_format(sd, NULL, fh/_format(sd, fh/' -e 's/(sd, ci, sd_state/(sd, sd_state/' $f
done
echo "ccflags-y += -include $B/compat.h" >> $B/camss/Makefile
echo "KBUILD_EXTRA_SYMBOLS := $B/phy/Module.symvers" >> $B/camss/Makefile
K=$P/02-kernel/e003i-front-production-src
mkdir -p $B/inctree/include/linux/phy
cp $K/include/linux/phy/phy.h $B/inctree/include/linux/phy/phy.h
python3 $P/06-camera/imx681-ref/x1e-cphy-edits.py $B/inctree phycore
cp $N/include/linux/phy/phy-mipi-cphy.h $B/inctree/include/linux/phy/phy-mipi-cphy.h
for d in phy camss; do echo "NOSTDINC_FLAGS += -I$B/inctree/include" >> $B/$d/Makefile; done
for d in phy camss; do
  echo "=== $d"
  make -s -j8 -C $P/02-kernel/e003i-front-production-src O=$P/02-kernel/build-runtime-v4-headers-20260826 M=$B/$d modules 2>&1 | grep -E 'error|warning: ' | head -30
done
ls -la $B/*/*.ko 2>/dev/null
