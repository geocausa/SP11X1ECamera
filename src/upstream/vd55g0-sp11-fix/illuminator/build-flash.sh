#!/bin/sh
# Test build of leds-qcom-flash with our four external-strobe safety patches (current/timeout programmed
# before arming, disable-before-trigger-change, timer encoding, disarm on error) for 7.1.5.
set -e
P=/home/geoca/Documents/SP11-PROJECT
R=$P/06-camera/SP11X1ECamera-driver/src/front-ir-vd55g0/illumination
B=/root/imx681-test/flashmod
rm -rf $B; mkdir -p $B/drivers/leds/flash
cp $P/02-kernel/e003i-front-production-src/drivers/leds/flash/leds-qcom-flash.c $B/drivers/leds/flash/
cd $B
for p in $R/000*.patch; do patch -s -p1 < $p; echo "applied $(basename $p)"; done
cp drivers/leds/flash/leds-qcom-flash.c .
python3 /root/imx681-test/flash-ee67.py leds-qcom-flash.c
python3 /root/imx681-test/flash-remove-fix.py leds-qcom-flash.c
echo 'obj-m := leds-qcom-flash.o' > Makefile
make -s -C $P/02-kernel/e003i-front-production-src O=$P/02-kernel/build-runtime-v4-headers-20260826 M=$B W=1 modules 2>&1 | grep -E 'error|warning' | head -20
ls -la $B/leds-qcom-flash.ko && modinfo -F vermagic $B/leds-qcom-flash.ko
