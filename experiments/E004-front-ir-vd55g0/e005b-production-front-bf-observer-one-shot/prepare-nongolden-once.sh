#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E005a fresh, one-use nonGolden front-only diagnostic boot PREPARE, not arm.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e005b-production-front-bf-observer-one-shot"
HY="$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hy-production-one-stream-r27"
HV="$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hv-current-golden-camera-dtb-merge"
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e005b-production-front-bf-observer-build
BOOT=/boot/sp11-7.1.5-camera-e005b-prod-front-bf
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e005b_prod_front_bf
ID=sp11-camera-e005b-prod-front-bf-one-shot
fail(){ echo "E005B_PREPARE_FAIL_CLOSED: $*" >&2; exit 1; }
cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden \
 --require-no-camera-process \
 --expect-head 73c990762d2aadde4aed3e7cc6d3700366b0c07b \
 --expect-origin 73c990762d2aadde4aed3e7cc6d3700366b0c07b
test ! -e "$BOOT" && sudo -n test ! -e "$ENTRY" || fail previous_candidate_identity
test ! -e "$D/INSTALL.txt" && test ! -e "$D/ARM.txt" || fail consumed_marker
! modinfo -p "$B/qcom-camss.ko" | grep -q e003h_pix_runtime_arm || fail obsolete_front_arm_parameter
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub_entry_already_exists
[ "$(blkid -s UUID -o value "$(findmnt -n -o SOURCE /)")" = "33e842b7-0434-4749-b03a-299bdcdb8b9f" ] || fail root_uuid
test -s "$B/qcom-camss.ko" || fail compiled_candidate_missing
[ "$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1)" = \
 "f9a170c7add6f35621a9c9e4a64292cfc082b1c85a168a57ee52fb978b93a3b7" ] || fail candidate_sha
[ "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail candidate_abi
test -s "$B/E005B-CAMSS-BUILD.log" || fail candidate_build_log_missing
! grep -Ei '(warning:|error:)' "$B/E005B-CAMSS-BUILD.log" || fail candidate_W1_warning
(cd "$HY/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail trusted_front_package
[ "$(sha256sum "$HV/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb"|cut -d' ' -f1)" = \
 "34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7" ] || fail trusted_front_dtb
[ "$(sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|cut -d' ' -f1)" = \
 "bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a" ] || fail golden_kernel_sha
[ "$(sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|cut -d' ' -f1)" = \
 "ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d" ] || fail golden_initrd_sha
grep -qx 'saved_entry=sp11-audio-fullio-v19c' < <(sudo -n grub-editenv /boot/grub/grubenv list) || fail saved_golden
! sudo -n grub-editenv /boot/grub/grubenv list | grep -q '^next_entry=.' || fail next_entry_occupied
# Derived from exact previously accepted one-use front-only GRUB entry, but
# this is a NEW distinct ID, paths and one-shot boot; old task is not replayed.
python3 - "$HY/99zzzzzz_sp11_camera_e003i_hy_prod_stream_r27" "$D/E005B-GRUB-STAGED" <<'PY'
from pathlib import Path
import sys
old=Path(sys.argv[1]).read_text()
repls={
 "sp11-camera-e003i-hy-prod-stream-r27-one-shot":"sp11-camera-e005b-prod-front-bf-one-shot",
 "sp11-7.1.5-camera-e003i-hy-prod-stream-r27":"sp11-7.1.5-camera-e005b-prod-front-bf",
 "7.1.5-sp11-camera-e003i-hy-prod-stream-r27":"7.1.5-sp11-camera-e005b-prod-front-bf",
 "sp11_camera_e003i_hy_prod_stream_r27":"sp11_camera_e005b_prod_front_bf",
 "SP11 Camera E003i-HY — current-Golden production stream R27 one-shot":
   "SP11 Camera E005a — front-only BF scalar one-shot",
}
for old_value,new_value in repls.items():
 assert old_value in old,(old_value,"historical GRUB template changed")
 old=old.replace(old_value,new_value)
assert "sp11-camera-e003i" not in old and "e003i_hy_prod_stream_r27" not in old
new=Path(sys.argv[2])
assert not new.exists()
new.write_text(old)
print("E005B_FRESH_GRUB_BOOT_ID_AND_FRONT_ONLY_DTB_PASS")
PY
test -s "$D/E005B-GRUB-STAGED" || fail grub_template
# Only the new removable candidate identity is mutated; Golden untouched.
cleanup(){
 if [ ! -e "$D/INSTALL.txt" ];then
  sudo -n rm -f -- "$ENTRY"
  sudo -n rm -rf -- "$BOOT"
  sudo -n update-grub >/dev/null || true
 fi
}
trap cleanup EXIT
sudo -n mkdir -- "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ \
 "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c \
 "$BOOT/initrd.img-7.1.5-sp11-camera-e005b-prod-front-bf"
sudo -n cp "$HV/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb" \
 "$BOOT/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb"
sudo -n install -m 0755 "$D/E005B-GRUB-STAGED" "$ENTRY"
sudo -n update-grub >/dev/null
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail fresh_grub_entry_missing
[ "$(sudo -n grub-editenv /boot/grub/grubenv list | grep '^saved_entry=')" = \
 'saved_entry=sp11-audio-fullio-v19c' ] || fail saved_changed
! sudo -n grub-editenv /boot/grub/grubenv list | grep -q '^next_entry=.' || fail next_entry_changed
{ echo 'schema=E005a-fresh-nonGolden-front-only-boot-prepared-v1'; echo 'status=INSTALLED_NOT_ARMED';
  echo "created=$(date -Ins)"; echo "parent_git=73c990762d2aadde4aed3e7cc6d3700366b0c07b";
  echo "new_boot_id=$ID"; echo 'saved_entry=sp11-audio-fullio-v19c';
  sudo -n sha256sum "$BOOT"/vmlinuz-* "$BOOT"/initrd.* "$BOOT"/*.dtb "$ENTRY";
  sha256sum "$B/qcom-camss.ko" "$HY/package-root/PACKAGE-MANIFEST.sha256";
} > "$D/INSTALL.txt"
sync
echo E005B_FRESH_NON_GOLDEN_FRONT_BOOT_INSTALLED_NOT_ARMED_GOLDEN_PRESERVED
