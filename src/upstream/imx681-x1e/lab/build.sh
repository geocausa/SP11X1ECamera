#!/bin/sh
# Test build of the upstream-candidate imx681 (v8 + our patches) for the running 7.1.5 kernel.
# Compat only for testing: 7.1 lacks the v4l2_subdev_client_info pad-op argument from media next.
set -e
P=/home/geoca/Documents/SP11-PROJECT
B=/root/imx681-test/mod
rm -rf $B; mkdir -p $B
cp $P/06-camera/imx681-upstream/drivers/media/i2c/imx681.c $B/imx681.c
sed -i '/const struct v4l2_subdev_client_info \*ci,/d' $B/imx681.c
echo 'obj-m := imx681.o' > $B/Makefile
make -s -C $P/02-kernel/e003i-front-production-src O=$P/02-kernel/build-runtime-v4-headers-20260826 M=$B W=1 KCFLAGS=-Werror modules 2>&1 | tail -20
ls -la $B/imx681.ko && sha256sum $B/imx681.ko
