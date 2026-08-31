#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-0055-candidate
BOOT=/boot/sp11-7.1.5-camera-e003h-camnoc-0055
ENTRY=/etc/grub.d/99s_sp11_camera_e003h_camnoc_0055
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail 'not Golden'
[ "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'HEAD/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'; git -C "$REPO" diff --cached --quiet || fail 'staged dirty'
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'saved_entry not Golden'; ! grep -q '^next_entry=.' <<<"$ENV" || fail 'next_entry armed'
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module loaded: $m"; done
[ ! -e "$BOOT" ] || fail '0055 boot directory exists'; sudo -n test ! -e "$ENTRY" || fail '0055 grub entry exists'
python3 - "$NEW/asset-manifest.json" "$NEW" <<'PY'
import hashlib,json,sys,pathlib
m=json.load(open(sys.argv[1])); root=pathlib.Path(sys.argv[2]); assert m['accepted'] and not m['runtime_authorized']; assert m['behavior_delta']['telemetry_only'] and m['behavior_delta']['camera_programming_changes']==0
for r,h in m['assets'].items(): assert hashlib.sha256((root/r).read_bytes()).hexdigest()==h,(r,h)
assert hashlib.sha256((root/'WINDOWS-E003H-CAMNOC-RATE-20260831.log').read_bytes()).hexdigest()==m['windows_camnoc_kd_sha256']
PY
sudo -n python3 - <<'PY'
import os,mmap,struct
fd=os.open('/dev/mem',os.O_RDONLY|os.O_SYNC); m=mmap.mmap(fd,0x20000,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ,offset=0x0ADE0000)
print('IDLE_CMD=0x%08x IDLE_CFG=0x%08x IDLE_BRANCH=0x%08x'%tuple(struct.unpack_from('<I',m,o)[0] for o in (0x138f8,0x138fc,0x13910)))
m.close();os.close(fd)
PY
echo 'PASS: 0055 telemetry-only package preflight on Golden'
