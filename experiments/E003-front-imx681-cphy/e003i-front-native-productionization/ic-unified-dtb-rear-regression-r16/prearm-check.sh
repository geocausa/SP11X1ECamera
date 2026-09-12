#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ic-unified-dtb-rear-regression-r16
IB=$BASE/ib-unified-current-golden-rear-front-dtb
R3=$R/experiments/E002-rear-ov13858-dphy/e002k-rear-native-productionization/d-source-integration/r3-source-integrated-runtime
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
BOOT=/boot/sp11-7.1.5-camera-ic-unified-rear-r16
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_ic_unified_rear_r16
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process || fail overlap_guard
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
python3 - <<PY || fail authority
import json
ib=json.load(open('$IB/RESULT.json'))
assert ib['status']=='PASS_OFFLINE_UNIFIED_CURRENT_GOLDEN_REAR_FRONT_DTB'
assert ib['unified_dtb_sha256']=='5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321'
assert ib['runtime_authorized'] is False
PY
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail golden_kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail golden_initrd
[ "$(sha256sum "$IB/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb"|awk '{print $1}')" = '5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321' ] || fail ib_dtb
[ "$(sha256sum "$R3/ov13858-production.ko"|awk '{print $1}')" = '13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309' ] || fail rear_module
sudo -n test ! -e "$BOOT" || fail candidate_boot_exists
sudo -n test ! -e "$ENTRY" || fail candidate_entry_exists
! sudo -n grep -Fq 'sp11-camera-ic-unified-rear-r16-one-shot' /boot/grub/grub.cfg || fail candidate_in_grub
[ ! -e "$D/runtime-output" ] && [ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] && [ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] || fail prior_attempt
rm -rf "$D/build" "$D/package-root"; mkdir -p "$D/build"
KERNEL_BUILD="$K" "$R/src/front-imx681/build-production.sh" "$D/build" >/tmp/ic-front-build.log
cp "$R3/ov13858-production.ko" "$D/build/ov13858-production.ko"
for pair in \
 'qcom-camss.ko 7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95' \
 'imx681.ko ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6' \
 'ov13858-production.ko 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309'; do
 set -- $pair; [ "$(sha256sum "$D/build/$1"|awk '{print $1}')" = "$2" ] || fail "module_hash_$1"
done
BUILD_DIR="$D/build" "$R/src/front-imx681/stage-package.sh" "$D/package-root" >/tmp/ic-package.log
[ "$(sha256sum "$D/package-root/PACKAGE-MANIFEST.sha256"|awk '{print $1}')" = '57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757' ] || fail package_manifest
(cd "$D/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail package_verify
python3 - <<'PY' || fail free_space
import os
v=os.statvfs('/home/geoca/Documents/SP11-PROJECT'); assert v.f_bavail*v.f_frsize>=8589934592
PY
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
echo 'IC_ROOT_PREARM=PASS GOLDEN=EXACT IB_DTB=PASS MODULES=CAMSS+IMX681+OV13858 REAR_REGRESSION=R16 FRONT_STREAM=NO'
