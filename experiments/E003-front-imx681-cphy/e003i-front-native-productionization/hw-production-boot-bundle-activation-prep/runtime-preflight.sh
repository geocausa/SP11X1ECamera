#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hw-production-boot-bundle-activation-prep
BOOT=/boot/sp11-7.1.5-camera-e003i-hw-prod-activation
fail(){ echo "FAIL: $*" >&2; exit 1; }
CMD=$(cat /proc/cmdline)
for t in sp11_camera_e003i_hw_prod_activation=1 sp11_entry=7.1.5-sp11-camera-e003i-hw-prod-activation modprobe.blacklist=qcom_camss,imx681,ov13858 clk_ignore_unused pd_ignore_unused; do grep -Fq "$t"<<<"$CMD" || fail "cmdline_$t"; done
grep -Fq 'BOOT_IMAGE=/boot/sp11-7.1.5-camera-e003i-hw-prod-activation/vmlinuz-7.1.5-sp11-render-parity-v4+'<<<"$CMD" || fail boot_image
! grep -Fq 'firmware_class.path='<<<"$CMD" || fail legacy_firmware_path
K=$(mktemp);trap 'rm -f "$K"' EXIT;journalctl -b -k --no-pager >"$K"
for n in 'TLB sync timed out -- SMMU may be deadlocked' 'vblank wait timed out' 'Internal error: Oops' 'soft lockup' 'Kernel panic'; do ! grep -Fiq "$n" "$K" || fail "boot_$n"; done
sudo -n true || fail sudo
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true);grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved;! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
git -C "$R" diff --quiet || fail tracked_dirty;git -C "$R" diff --cached --quiet || fail staged
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin
[ ! -e "$D/ACTIVATION.txt" ] || fail prior_activation
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb"|awk '{print $1}')" = '34880dc20d349bf966ebf62d6d8bb3f0130f436c88d9e4838585624a869e04c7' ] || fail installed_dtb
P=$D/package-root;[ -d "$P/usr/lib/sp11-front-imx681" ] || fail package_missing
[ "$(sha256sum "$P/PACKAGE-MANIFEST.sha256"|awk '{print $1}')" = '57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757' ] || fail package_manifest
(cd "$P" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail package_verify
echo 'HW_RUNTIME_PREFLIGHT=PASS ACTIVATION_ONLY=YES STREAM_AUTHORIZED=NO FIRMWARE_PATH=NONE'
