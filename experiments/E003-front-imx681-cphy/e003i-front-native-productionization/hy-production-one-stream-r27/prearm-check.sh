#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/hy-production-one-stream-r27
HX=$BASE/hx-production-one-stream-acceptance-policy
HV=$BASE/hv-current-golden-camera-dtb-merge
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
BOOT=/boot/sp11-7.1.5-camera-e003i-hy-prod-stream-r27
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e003i_hy_prod_stream_r27
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process || fail overlap_guard
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
python3 - <<PY || fail authority
import json
hx=json.load(open('$HX/RESULT.json')); hv=json.load(open('$HV/RESULT.json'))
assert hx['status']=='PASS_OFFLINE_PRODUCTION_ONE_STREAM_ACCEPTANCE_POLICY'
assert hx['future_candidate_stream_count']==1 and hx['frames']==27 and hx['post_g3_policy']=='shadow' and hx['post_g3_native_writes']==0
assert hx['same_stream_retry_authorized'] is False and hx['same_boot_retry_authorized'] is False
assert hv['status']=='PASS_OFFLINE_CURRENT_GOLDEN_CAMERA_DTB_MERGE'
assert hv['merged_dtb_sha256']=='34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7'
PY
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail golden_kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail golden_initrd
[ "$(sha256sum "$HV/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb"|awk '{print $1}')" = '34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7' ] || fail hv_dtb
sudo -n test ! -e "$BOOT" || fail candidate_boot_exists
sudo -n test ! -e "$ENTRY" || fail candidate_entry_exists
! sudo -n grep -Fq 'sp11-camera-e003i-hy-prod-stream-r27-one-shot' /boot/grub/grub.cfg || fail candidate_in_grub
[ ! -e "$D/runtime-output" ] || fail prior_runtime_output
[ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] && [ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || fail prior_attempt
rm -rf "$D/build" "$D/package-root"
KERNEL_BUILD="$K" "$R/src/front-imx681/build-production.sh" "$D/build" >/tmp/e003i-hy-build.log
for pair in \
 'front-imx681-capture 70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d' \
 'front-imx681-bootstrap-controls 4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce' \
 'qcom-camss.ko 7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95' \
 'imx681.ko ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6'; do
 set -- $pair; [ "$(sha256sum "$D/build/$1"|awk '{print $1}')" = "$2" ] || fail "build_hash_$1"
done
BUILD_DIR="$D/build" "$R/src/front-imx681/stage-package.sh" "$D/package-root" >/tmp/e003i-hy-package.log
[ "$(sha256sum "$D/package-root/PACKAGE-MANIFEST.sha256"|awk '{print $1}')" = '57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757' ] || fail package_manifest
(cd "$D/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail package_verify
python3 - <<'PY' || fail free_space
import os
v=os.statvfs('/home/geoca/Documents/SP11-PROJECT');free=v.f_bavail*v.f_frsize
assert free>=8589934592,free
PY
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true);grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved_entry;! grep -q '^next_entry=.'<<<"$ENV" || fail next_entry
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
echo 'HY_ROOT_PREARM=PASS GOLDEN=EXACT HV_DTB=PASS PACKAGE=57aa9cc2 POLICY=shadow STREAMS=1 FRAMES=27'
