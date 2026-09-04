#!/bin/bash
set -euo pipefail
fail=0
cmd=$(cat /proc/cmdline)
echo "CMDLINE=$cmd"
for tok in 'sp11_camera_e003h_request6_0074_bootdiag_pwrkeep=1' 'clk_ignore_unused' 'pd_ignore_unused' 'modprobe.blacklist=qcom_camss,imx681,ov13858'; do
  if [[ " $cmd " != *" $tok "* ]]; then echo "FAIL missing_cmdline=$tok"; fail=1; fi
done
mods=$(lsmod | awk 'NR>1{print $1}')
for m in qcom_camss imx681 ov13858; do
  if grep -qx "$m" <<<"$mods"; then echo "FAIL loaded_module=$m"; fail=1; fi
done
k=$(mktemp); trap 'rm -f "$k"' EXIT
journalctl -b -k --no-pager >"$k"
count(){ grep -Fic "$1" "$k" || true; }
tlb=$(count 'TLB sync timed out -- SMMU may be deadlocked')
vblank=$(count 'vblank wait timed out')
oops=$(count 'Internal error: Oops')
soft=$(count 'soft lockup')
die=$(grep -Eic 'kernel BUG|Unable to handle kernel|Internal error:' "$k" || true)
echo "COUNTS tlb=$tlb vblank=$vblank oops=$oops softlock=$soft fatal=$die"
if (( tlb || vblank || oops || soft || die )); then fail=1; fi
pistate=$(systemctl is-active pislave.service 2>/dev/null || true)
echo "PISLAVE=$pistate"
[[ "$pistate" == active ]] || fail=1
envout=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
printf 'GRUBENV=%q\n' "$envout"
grep -Fxq 'saved_entry=sp11-audio-fullio-v19c' <<<"$envout" || fail=1
if grep -Eq '^next_entry=.+' <<<"$envout"; then echo 'FAIL next_entry_not_consumed'; fail=1; fi
if (( fail )); then echo 'BOOTDIAG_RESULT=FAIL'; exit 1; fi
echo 'BOOTDIAG_RESULT=PASS'
