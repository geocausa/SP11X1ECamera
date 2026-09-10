#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/dp-bounded-native-aec-cap-sensor-loop
fail(){ echo "FAIL: $*" >&2; exit 1; }
CMD=$(cat /proc/cmdline)
for t in sp11_camera_e003i_dp_cap_aec=1 clk_ignore_unused pd_ignore_unused modprobe.blacklist=qcom_camss,imx681,ov13858; do grep -Fq "$t" <<<"$CMD" || fail "cmdline_$t"; done
K=$(mktemp); trap 'rm -f "$K"' EXIT
journalctl -b -k --no-pager >"$K"
for n in 'TLB sync timed out -- SMMU may be deadlocked' 'vblank wait timed out' 'Internal error: Oops' 'soft lockup'; do ! grep -Fiq "$n" "$K" || fail "boot_$n"; done
systemctl is-active --quiet pislave.service || fail pislave
sudo -n true || fail sudo
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged
python3 "$D/verify.py"
sudo -n test ! -e "$D/runtime-output" || fail prior_runtime_output
echo 'PASS: E003i-DP one-shot runtime preflight clean'
