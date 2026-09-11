#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/eo-bounded-r5-r9-live-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(uname -r)" = '7.1.5-sp11-render-parity-v4+' ] || fail kernel
! grep -Fq 'sp11_camera_e003i_eo_r5_r9=1' /proc/cmdline || fail still_candidate
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
{
 echo 'schema=sp11-e003i-eo-golden-return-v1'
 echo 'status=PASS'
 echo "time=$(date -Ins)"
 echo "kernel=$(uname -r)"
 echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
 echo 'saved_entry=sp11-audio-fullio-v19c'
 echo 'next_entry='
 echo 'camera_modules=absent'
} > "$D/GOLDEN-RETURN.txt"
echo 'EO_GOLDEN_RETURN=PASS'
