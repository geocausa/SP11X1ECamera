#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0076-longpoll-candidate
fail(){ echo "FAIL: $*" >&2; exit 1; }
CMD=$(cat /proc/cmdline)
for t in sp11_camera_e003h_request6_0076=1 clk_ignore_unused pd_ignore_unused modprobe.blacklist=qcom_camss,imx681,ov13858; do grep -Fq "$t" <<<"$CMD" || fail "cmdline_$t"; done
grep -Fq 'firmware_class.path=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate/firmware' <<<"$CMD" || fail firmware_path
K=$(mktemp); trap 'rm -f "$K"' EXIT; journalctl -b -k --no-pager >"$K"
for n in 'TLB sync timed out -- SMMU may be deadlocked' 'vblank wait timed out' 'Internal error: Oops' 'soft lockup'; do ! grep -Fiq "$n" "$K" || fail "boot_$n"; done
systemctl is-active --quiet pislave.service || fail pislave
sudo -n true || fail sudo
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
git -C "$R" diff --quiet || fail tracked_dirty; git -C "$R" diff --cached --quiet || fail staged
python3 "$D/verify.py"
for f in "$D"/RUN.txt "$D"/HELPER-CONSUMED.marker "$D"/WATCHER.ready "$D"/RTCDM-STAGES.txt "$D"/QC10C-{0,1,2,3,4,5}.bin; do sudo -n test ! -e "$f" || fail prior_output; done
echo 'PASS: 0076 exact-0074 long-poll preflight clean'
