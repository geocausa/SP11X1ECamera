#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004r-ir-only-bind-runtime-r3
K=$R/experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -Fq 'sp11_camera_e004r_ir_only_bind_r3=1' /proc/cmdline || fail candidate_marker
[ "$(uname -r)" = '7.1.5-sp11-render-parity-v4+' ] || fail kernel
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail one_shot_not_consumed
for x in RUNTIME-DMESG.txt MEDIA.txt CONTROLS.txt STREAM-BLOCK.txt ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json; do [ ! -e "$D/$x" ] || fail "already_$x"; done
for m in qcom_camss sp11_vd55g0 e004r_stream_block_test; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
for m in imx681 ov13858 vd55g0; do [ ! -d "/sys/module/$m" ] || fail "other_camera_$m"; done
if pgrep -af 'libcamera|v4l2-ctl.*stream|ffmpeg|gst-launch' >/dev/null; then fail camera_process; fi
[ ! -e /dev/media0 ] || fail media_node_present
COMP=/proc/device-tree/soc@0/cci@ac15000/i2c-bus@0/camera@60/compatible
[ -r "$COMP" ] || fail ir_dt_node
[ "$(tr -d '\0' < "$COMP")" = 'microsoft,sp11-vd55g0' ] || fail compatible
sudo -n modprobe i2c_qcom_cci
for _ in $(seq 1 50); do [ -e /sys/bus/i2c/devices/2-0060 ] && break; sleep 0.1; done
[ -e /sys/bus/i2c/devices/2-0060 ] || fail i2c_client_2_0060
[ ! -e /sys/bus/i2c/devices/2-0060/driver ] || fail unexpected_sensor_driver
[ "$(sha256sum "$D/build/sp11-vd55g0.ko"|awk '{print $1}')" = '4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72' ] || fail sensor_hash
[ "$(sha256sum "$D/build/e004r_stream_block_test.ko"|awk '{print $1}')" = '2cacc5e1336ac77b32c7e67e8c6f05cfdbaf6d54e9424cede1168f69c25f3303' ] || fail harness_hash
[ "$(sha256sum "$K/qcom-camss.ko"|awk '{print $1}')" = 'bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba' ] || fail camss_hash
{
 echo 'schema=sp11-camera-e004r-runtime-preflight-v1'; echo 'status=PASS_READY_FOR_NATIVE_BIND'; echo "time=$(date -Ins)"
 echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"; echo 'i2c_client=/sys/bus/i2c/devices/2-0060'
 echo 'sensor_driver=unbound'; echo 'qcom_camss=absent'; echo 'media_node=absent'; echo 'capture_stream=NO'; echo 'illumination=NO'
} > "$D/RUNTIME-PREFLIGHT.txt"
echo 'E004R_RUNTIME_PREFLIGHT=PASS CLIENT=2-0060 UNBOUND=YES MEDIA=ABSENT'
