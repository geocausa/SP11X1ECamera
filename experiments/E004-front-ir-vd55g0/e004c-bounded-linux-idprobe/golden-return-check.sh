#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process || fail guard
! grep -Fq 'sp11_camera_e004c_ir_idprobe=1' /proc/cmdline || fail candidate_marker
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in sp11_vd55g0_idprobe qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
[ ! -e /dev/media0 ] || fail media
{
 echo 'schema=sp11-camera-e004c-golden-return-v1'
 echo 'status=PASS'
 echo "time=$(date -Ins)"
 echo "kernel=$(uname -r)"
 echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
 echo 'saved_entry=sp11-audio-fullio-v19c'
 echo 'next_entry='
 echo 'idprobe_module=absent'
 echo 'camera_nodes=absent'
} > "$D/GOLDEN-RETURN.txt"
echo 'E004C_GOLDEN_RETURN=PASS'
