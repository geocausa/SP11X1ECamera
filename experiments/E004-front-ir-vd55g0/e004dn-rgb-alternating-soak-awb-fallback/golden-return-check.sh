#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dn-rgb-alternating-soak-awb-fallback
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ]
! grep -Fq 'sp11_camera_e004dn_rgb_alternating_soak_awb_fallback=1' /proc/cmdline
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || exit 1; done
[ -f "$D/ATTEMPT1-PASS.json" ]
{ echo schema=sp11-camera-e004dn-golden-return-v1; echo status=PASS_GOLDEN_RETURN; echo time=$(date -Ins); echo boot_id=$(cat /proc/sys/kernel/random/boot_id); echo head=$(git -C "$R" rev-parse HEAD); } > "$D/GOLDEN-RETURN.txt"
echo E004DN_GOLDEN_RETURN=PASS
