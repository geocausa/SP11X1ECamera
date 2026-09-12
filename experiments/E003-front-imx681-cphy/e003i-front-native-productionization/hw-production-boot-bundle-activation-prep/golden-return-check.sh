#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hw-production-boot-bundle-activation-prep
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process || fail guard
CMD=$(cat /proc/cmdline);grep -Fq 'sp11_entry=7.1.5-sp11-fullio-v19c'<<<"$CMD" || fail cmdline
! grep -Fq 'sp11_camera_e003i_hw_prod_activation=1'<<<"$CMD" || fail candidate_token
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
{ echo 'schema=sp11-e003i-hw-golden-return-v1'; echo 'status=PASS_GOLDEN_RETURN'; echo "time=$(date -Ins)"; echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"; } > "$D/GOLDEN-RETURN.txt"
echo 'HW_GOLDEN_RETURN=PASS'
