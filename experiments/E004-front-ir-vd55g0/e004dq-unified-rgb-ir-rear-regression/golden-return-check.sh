#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dq-unified-rgb-ir-rear-regression
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process || fail overlap
! grep -Fq 'sp11_camera_e004dq_unified_rgb_ir_rear=1' /proc/cmdline || fail marker
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858 sp11_vd55g0 e004t_csiphy_readback_test i2c_qcom_cci; do [ ! -d "/sys/module/$m" ] || fail module_$m; done
[ ! -e /dev/media0 ] || fail media
{ echo schema=sp11-camera-e004dq-golden-return-v1; echo status=PASS_GOLDEN_RETURN; echo time=$(date -Ins); echo boot_id=$(cat /proc/sys/kernel/random/boot_id); echo kernel=$(uname -r); echo saved_entry=sp11-audio-fullio-v19c; echo next_entry=; } > "$D/GOLDEN-RETURN.txt"
echo E004DQ_GOLDEN_RETURN=PASS
