#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate
D=$R/experiments/E003-front-imx681-cphy/e003h-0075a-hardened-0072-control
AUTH=$D/AUTHORIZATION.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
CMD=$(cat /proc/cmdline)
for t in sp11_camera_e003h_0075a=1 clk_ignore_unused pd_ignore_unused modprobe.blacklist=qcom_camss,imx681,ov13858; do grep -Fq "$t" <<<"$CMD" || fail "cmdline_$t"; done
K=$(mktemp); trap 'rm -f "$K"' EXIT; journalctl -b -k --no-pager >"$K"
for n in 'TLB sync timed out -- SMMU may be deadlocked' 'vblank wait timed out' 'Internal error: Oops' 'soft lockup'; do ! grep -Fiq "$n" "$K" || fail "boot_$n"; done
systemctl is-active --quiet pislave.service || fail pislave
sudo -n true || fail sudo
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
python3 - "$D/MANIFEST.json" "$AUTH" "$R" <<'PY'
import json,hashlib,pathlib,sys
mp,ap,R=sys.argv[1:]; m=json.load(open(mp)); a=json.load(open(ap)); R=pathlib.Path(R); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert m['accepted_base']=='0072' and not m['request6'] and m['same_boot_retry'] is False
assert a['accepted'] and a['runtime_authorized'] and not a['request6'] and a['helper_invocations']==1
assert a['manifest_sha256']==sha(pathlib.Path(mp)) and a['accepted_0072_analysis_sha256']==m['asset_sha256']['analysis']
for k,p in m['asset_paths'].items(): assert sha(R/p)==m['asset_sha256'][k],k
a=json.load(open(R/m['asset_paths']['analysis'])); assert a['accepted'] and a['execution']['helper_rc_zero'] and a['execution']['dqbuf_indices']==[0,1,2,3,0]
PY
for f in "$D"/RUN.txt "$D"/HELPER-CONSUMED.marker "$D"/WATCHER.ready "$D"/RTCDM-STAGES.txt "$D"/QC10C-{0,1,2,3,4}.bin; do sudo -n test ! -e "$f" || fail prior_output; done
echo 'PASS: 0075a hardened accepted-0072 control preflight'
