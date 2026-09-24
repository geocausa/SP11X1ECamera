#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E005b read-only candidate runtime preflight. Does not load camera or stream.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e005b-production-front-bf-observer-one-shot"
HY="$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hy-production-one-stream-r27"
PKG="$HY/package-root/usr/lib/sp11-front-imx681"
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e005b-production-front-bf-observer-build
BOOT=/boot/sp11-7.1.5-camera-e005b-prod-front-bf
fail(){ echo "E005B_RUNTIME_PREFLIGHT_FAIL: $*" >&2; exit 1; }
cd "$R"
[ "$(git rev-parse HEAD)" = "73c990762d2aadde4aed3e7cc6d3700366b0c07b" ] || fail head
[ "$(git rev-parse '@{u}')" = "73c990762d2aadde4aed3e7cc6d3700366b0c07b" ] || fail origin
git diff --quiet && git diff --cached --quiet || fail dirty_tracked
[ "$(uname -r)" = "7.1.5-sp11-render-parity-v4+" ] || fail kernel
cmdline="$(cat /proc/cmdline)"
for flag in sp11_camera_e005b_prod_front_bf=1 \
 sp11_entry=7.1.5-sp11-camera-e005b-prod-front-bf \
 modprobe.blacklist=qcom_camss,imx681,ov13858 \
 clk_ignore_unused pd_ignore_unused;do
 [[ "$cmdline" == *"$flag"* ]] || fail "cmdline_missing_$flag"
done
[[ "$cmdline" == *"BOOT_IMAGE=/boot/sp11-7.1.5-camera-e005b-prod-front-bf/vmlinuz-7.1.5-sp11-render-parity-v4+"* ]] || fail wrong_boot_image
[[ "$cmdline" != *"firmware_class.path="* ]] || fail obsolete_firmware_loader
[ "$(sudo -n grub-editenv /boot/grub/grubenv list|grep '^saved_entry=')" = \
 'saved_entry=sp11-audio-fullio-v19c' ] || fail golden_saved_changed
! sudo -n grub-editenv /boot/grub/grubenv list | grep -q '^next_entry=.' || fail next_entry_not_cleared
[ -s "$D/INSTALL.txt" ] && [ -s "$D/ARM.txt" ] || fail unplanned_candidate
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || fail previously_consumed
[ ! -e /home/geoca/Documents/SP11-PROJECT/02-kernel/e005b-production-front-bf-private-attempt1 ] || fail previous_output
for mod in qcom_camss imx681 ov13858;do
 [ ! -d "/sys/module/$mod" ] || fail "module_premature_$mod"
done
! compgen -G '/dev/video*' >/dev/null || fail video_nodes_before_loading
! compgen -G '/dev/media*' >/dev/null || fail media_nodes_before_loading
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked \
 --require-no-camera-process --expect-head 73c990762d2aadde4aed3e7cc6d3700366b0c07b \
 --expect-origin 73c990762d2aadde4aed3e7cc6d3700366b0c07b
[ "$(sha256sum "$B/qcom-camss.ko"|cut -d' ' -f1)" = \
 f9a170c7add6f35621a9c9e4a64292cfc082b1c85a168a57ee52fb978b93a3b7 ] || fail compiled_prod_module_identity
! modinfo -p "$B/qcom-camss.ko" | grep -q e003h_pix_runtime_arm || fail nonproduction_source
[ "$(modinfo -F vermagic "$B/qcom-camss.ko")" = \
 '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail module_vermagic
(cd "$HY/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail trusted_front_assets
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb"|cut -d' ' -f1)" = \
 "34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7" ] || fail candidate_front_dtb
[ "$(sudo -n sha256sum "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"|cut -d' ' -f1)" = \
 "bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a" ] || fail candidate_golden_kernel
test -x "$PKG/bin/front-imx681-launcher.py" &&
 test -x "$PKG/build/front-imx681-capture" || fail trusted_launcher_missing
log="$(mktemp /tmp/e005b-candidate-kernel-health-XXXXXX)"
trap 'rm -f -- "$log"' EXIT
journalctl -b -k --no-pager > "$log"
for fatal in 'TLB sync timed out -- SMMU may be deadlocked' \
 'vblank wait timed out' 'Internal error: Oops' \
 'soft lockup' 'Kernel panic';do
 ! grep -Fiq "$fatal" "$log" || fail "kernel_health_$fatal"
done
echo E005B_PRODUCTION_FRONT_ONLY_NEW_BOOT_PREFLIGHT_PASS_GOLDEN_RETURN_PENDING
