#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004u-csiphy0-readback-runtime
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process || fail guard
! grep -Fq 'sp11_camera_e004u_csiphy0_readback=1' /proc/cmdline || fail candidate_marker
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in qcom_camss sp11_vd55g0 e004t_csiphy_readback_test imx681 ov13858 vd55g0 i2c_qcom_cci; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ ! -e /dev/media0 ] || fail media
{
 echo 'schema=sp11-camera-e004u-golden-return-v1'; echo 'status=PASS'; echo "time=$(date -Ins)"
 echo "kernel=$(uname -r)"; echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
 echo 'saved_entry=sp11-audio-fullio-v19c'; echo 'next_entry='; echo 'camera_modules=absent'; echo 'media_nodes=absent'
} > "$D/GOLDEN-RETURN.txt"
echo 'E004U_GOLDEN_RETURN=PASS'
