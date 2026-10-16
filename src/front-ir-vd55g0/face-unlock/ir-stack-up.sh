#!/bin/sh
# sp11-ir-flash-lab boot: load the camera stack (camss 50, sensors, Peter's vd55g1 + fixes, patched
# leds-qcom-flash) and a v4l2loopback node /dev/video42 for the grey IR feed. LED stays off.
D=/var/lib/sp11-camera-daily2; T=/root/imx681-test
grep -q sp11-ir-flash-lab /proc/cmdline || { echo 'not the flash lab boot'; exit 1; }
lsmod | grep -q '^vd55g1' && { echo 'already up'; exit 0; }
for m in i2c_qcom_cci mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg videobuf2_vmalloc v4l2_cci led_class_flash v4l2_flash_led_class; do modprobe $m; done
insmod $T/flashmod/leds-qcom-flash.ko
insmod $D/modules/qcom-camss.ko $(cat $D/camss-params.txt)
insmod $D/modules/imx681.ko
insmod $T/ovmod/ov13858.ko
insmod $T/vdflash/vd55g1.ko
insmod $D/modules/v4l2loopback.ko video_nr=42 exclusive_caps=1 card_label="SP11 IR Camera"
sleep 3
media-ctl -d /dev/media0 -p | grep -E '^- entity.*(vd55|illum)'
ls -la /dev/video42
