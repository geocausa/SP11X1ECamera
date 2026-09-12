#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ic-unified-dtb-rear-regression-r16
BOOT=/boot/sp11-7.1.5-camera-ic-unified-rear-r16
fail(){ echo "FAIL: $*" >&2; exit 1; }
CMD=$(cat /proc/cmdline)
for t in sp11_camera_ic_unified_rear_r16=1 sp11_entry=7.1.5-sp11-camera-ic-unified-rear-r16 modprobe.blacklist=qcom_camss,imx681,ov13858 clk_ignore_unused pd_ignore_unused; do grep -Fq "$t"<<<"$CMD" || fail "cmdline_$t"; done
grep -Fq 'BOOT_IMAGE=/boot/sp11-7.1.5-camera-ic-unified-rear-r16/vmlinuz-7.1.5-sp11-render-parity-v4+'<<<"$CMD" || fail boot_image
! grep -Fq 'firmware_class.path='<<<"$CMD" || fail firmware_path
K=$(mktemp); trap 'rm -f "$K"' EXIT; journalctl -b -k --no-pager >"$K"
for n in 'TLB sync timed out -- SMMU may be deadlocked' 'vblank wait timed out' 'Internal error: Oops' 'soft lockup' 'Kernel panic'; do ! grep -Fiq "$n" "$K" || fail "boot_$n"; done
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin
git -C "$R" diff --quiet || fail tracked_dirty; git -C "$R" diff --cached --quiet || fail staged
[ ! -e "$D/runtime-output" ] && [ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] || fail prior_attempt
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb"|awk '{print $1}')" = '5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321' ] || fail installed_dtb
[ "$(sha256sum "$D/build/ov13858-production.ko"|awk '{print $1}')" = '13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309' ] || fail rear_module
echo 'IC_RUNTIME_PREFLIGHT=PASS REAR_REGRESSION=R16 FRONT_STREAM=NO RETRY=NO'
