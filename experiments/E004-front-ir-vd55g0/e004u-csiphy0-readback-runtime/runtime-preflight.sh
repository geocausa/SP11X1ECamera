#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004u-csiphy0-readback-runtime
K=$R/experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module
COMPAT=microsoft,sp11-vd55g0
fail(){ echo "FAIL: $*" >&2; exit 1; }

discover_ir_client() {
	local found=()
	local p c
	for p in /sys/bus/i2c/devices/*-0060; do
		[ -e "$p" ] || continue
		c=$p/of_node/compatible
		[ -r "$c" ] || continue
		if [ "$(tr -d '\0' < "$c")" = "$COMPAT" ]; then
			found+=("$p")
		fi
	done
	[ "${#found[@]}" -eq 1 ] || return 1
	printf '%s\n' "${found[0]}"
}

grep -Fq 'sp11_camera_e004u_csiphy0_readback=1' /proc/cmdline || fail candidate_marker
[ "$(uname -r)" = '7.1.5-sp11-render-parity-v4+' ] || fail kernel
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail one_shot_not_consumed
for x in RUNTIME-DMESG.txt MEDIA.txt CONTROLS.txt STREAM-BLOCK.txt ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json; do
	[ ! -e "$D/$x" ] || fail "already_$x"
done
for m in qcom_camss sp11_vd55g0 e004t_csiphy_readback_test; do
	[ ! -d "/sys/module/$m" ] || fail "module_$m"
done
for m in imx681 ov13858 vd55g0; do
	[ ! -d "/sys/module/$m" ] || fail "other_camera_$m"
done
if pgrep -af 'libcamera|v4l2-ctl.*stream|ffmpeg|gst-launch' >/dev/null; then
	fail camera_process
fi
[ ! -e /dev/media0 ] || fail media_node_present

COMP=/proc/device-tree/soc@0/cci@ac15000/i2c-bus@0/camera@60/compatible
[ -r "$COMP" ] || fail ir_dt_node
[ "$(tr -d '\0' < "$COMP")" = "$COMPAT" ] || fail compatible

sudo -n modprobe i2c_qcom_cci
DEV=
for _ in $(seq 1 50); do
	DEV=$(discover_ir_client 2>/dev/null || true)
	[ -n "$DEV" ] && break
	sleep 0.1
done
[ -n "$DEV" ] || fail dynamic_i2c_client_not_unique
CLIENT=$(basename "$DEV")
[[ "$CLIENT" =~ ^[0-9]+-0060$ ]] || fail dynamic_client_name
[ "$(tr -d '\0' < "$DEV/of_node/compatible")" = "$COMPAT" ] || fail dynamic_client_compatible
[ ! -e "$DEV/driver" ] || fail unexpected_sensor_driver

[ "$(sha256sum "$D/build/sp11-vd55g0.ko"|awk '{print $1}')" = '4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72' ] || fail sensor_hash
[ "$(sha256sum "$D/build/e004t_csiphy_readback_test.ko"|awk '{print $1}')" = '6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e' ] || fail harness_hash
[ "$(sha256sum "$K/qcom-camss.ko"|awk '{print $1}')" = 'bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba' ] || fail camss_hash

{
	echo 'schema=sp11-camera-e004u-runtime-preflight-v1'
	echo 'status=PASS_READY_FOR_RECEIVER_READBACK'
	echo "time=$(date -Ins)"
	echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
	echo "i2c_client_path=$DEV"
	echo "i2c_client_name=$CLIENT"
	echo 'i2c_address=0x60'
	echo "compatible=$COMPAT"
	echo 'sensor_driver=unbound'
	echo 'qcom_camss=absent'
	echo 'media_node=absent'
	echo 'sensor_stream=NO'
	echo 'capture_stream=NO'
	echo 'illumination=NO'
} > "$D/RUNTIME-PREFLIGHT.txt"
echo "E004U_RUNTIME_PREFLIGHT=PASS CLIENT=$CLIENT COMPAT=$COMPAT ADDR=0x60 UNBOUND=YES MEDIA=ABSENT"
