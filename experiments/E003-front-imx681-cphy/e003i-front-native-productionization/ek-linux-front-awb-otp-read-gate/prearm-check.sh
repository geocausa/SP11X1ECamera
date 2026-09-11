#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ek-linux-front-awb-otp-read-gate
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
make -C "$K" M="$D" clean >/dev/null
make -C "$K" M="$D" W=1 -j4 >/tmp/e003i-ek-build.log 2>&1 || { cat /tmp/e003i-ek-build.log; fail build; }
python3 "$D/verify-ek.py" >/dev/null
sha256sum "$D/imx681.ko" | grep -Fxq 'e610beaa8d0248e85dff48a13ede8aeed21800a9ab8f574623136426f9940d04  '"$D/imx681.ko" || fail module_sha
sha256sum "$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" | grep -q '^019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f ' || fail dtb_sha
sha256sum "$BASE/z-live-3a-runtime/qcom-camss-e003i-y.ko" | grep -q '^42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b ' || fail camss_sha
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved_entry
! grep -q '^next_entry=.' <<<"$ENV" || fail next_entry
[ ! -d /sys/module/qcom_camss ] || fail golden_camss_loaded
[ ! -d /sys/module/imx681 ] || fail golden_imx681_loaded
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged_dirty
echo 'PASS: EK offline/prearm; Golden unchanged'
