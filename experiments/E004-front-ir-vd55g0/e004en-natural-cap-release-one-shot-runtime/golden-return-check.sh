#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004en-natural-cap-release-one-shot-runtime
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process || fail overlap
! grep -Fq 'sp11_camera_e004en_natural_cap_release=1' /proc/cmdline || fail marker
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858 sp11_vd55g0 e004t_csiphy_readback_test i2c_qcom_cci; do [ ! -d "/sys/module/$m" ] || fail module_$m; done
[ ! -e /dev/media0 ] || fail media
PYTHONDONTWRITEBYTECODE=1 python3 "$R/src/sp11-camera-stack/verify-live-unactivated.py" >/dev/null || fail package_live
{ echo schema=sp11-camera-e004en-golden-return-v1; echo status=PASS_GOLDEN_RETURN; echo time=$(date -Ins); echo boot_id=$(cat /proc/sys/kernel/random/boot_id); echo kernel=$(uname -r); echo saved_entry=sp11-audio-fullio-v19c; echo next_entry=; echo package_still_installed=YES; } > "$D/GOLDEN-RETURN.txt"
echo E004EN_GOLDEN_RETURN=PASS PACKAGE=STILL_INSTALLED
