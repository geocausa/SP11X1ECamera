#!/bin/sh
# Test build of mainline vd55g1.c + Peter Marshall's VD55G0 v2 + Jizhou Tong's fix (+ our patches) for 7.1.5.
# Compat only: drop the media-next v4l2_subdev_client_info pad-op argument.
set -e
P=/home/geoca/Documents/SP11-PROJECT
B=/root/imx681-test/vdflash
rm -rf $B; mkdir -p $B
cp $P/06-camera/linux-sparse/drivers/media/i2c/vd55g1.c $B/
cp $P/06-camera/linux-sparse/drivers/media/i2c/vd55g*.h $B/ 2>/dev/null || true
sed -i -e '/^[[:space:]]*const struct v4l2_subdev_client_info \*ci,$/d' \
       -e 's/const struct v4l2_subdev_client_info \*ci, //' \
       -e 's/_fmt(sd, NULL, sd_state/_fmt(sd, sd_state/' -e 's/(sd, ci, sd_state/(sd, sd_state/' $B/vd55g1.c
python3 -c "import sys;p=sys.argv[1];s=open(p).read();o='ret = v4l2_async_register_subdev(&sensor->sd);';assert s.count(o)==1;open(p,'w').write(s.replace(o,'ret = v4l2_async_register_subdev_sensor(&sensor->sd);'))" $B/vd55g1.c
echo 'obj-m := vd55g1.o' > $B/Makefile
make -s -C $P/02-kernel/e003i-front-production-src O=$P/02-kernel/build-runtime-v4-headers-20260826 M=$B W=1 modules 2>&1 | grep -E 'error|warning' | head -20
ls -la $B/vd55g1.ko && modinfo -F alias $B/vd55g1.ko | grep -i of: 
