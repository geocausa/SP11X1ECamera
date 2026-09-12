#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ig-unified-rear-to-front-r16-r27
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process || fail guard
! grep -Fq 'sp11_camera_ig_rear_to_front_r16_r27=1' /proc/cmdline || fail candidate_token
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true);grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved;! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
{ echo 'schema=sp11-camera-ig-rear-to-front-r16-r27-golden-return-v1'; echo 'status=PASS'; echo "time=$(date -Ins)"; echo "kernel=$(uname -r)"; echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"; echo 'saved_entry=sp11-audio-fullio-v19c'; echo 'next_entry='; echo 'camera_modules=absent'; } > "$D/GOLDEN-RETURN.txt"
echo 'IG_GOLDEN_RETURN=PASS'
