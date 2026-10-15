#!/bin/sh
# Test build of the upstream-candidate ov13858 (mainline + power patch + our DT patch) for the running 7.1.5 kernel.
set -e
P=/home/geoca/Documents/SP11-PROJECT
B=/root/imx681-test/ovmod
rm -rf $B; mkdir -p $B
cp $P/06-camera/linux-sparse/drivers/media/i2c/ov13858.c $B/ov13858.c
echo 'obj-m := ov13858.o' > $B/Makefile
make -s -C $P/02-kernel/e003i-front-production-src O=$P/02-kernel/build-runtime-v4-headers-20260826 M=$B W=1 KCFLAGS=-Werror modules 2>&1 | tail -20
ls -la $B/ov13858.ko && sha256sum $B/ov13858.ko
