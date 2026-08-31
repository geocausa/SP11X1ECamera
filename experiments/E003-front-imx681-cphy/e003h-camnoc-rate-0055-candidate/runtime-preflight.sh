#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-0055-candidate
AUTH=$NEW/AUTHORIZATION.json
RUN=$NEW/RUNTIME-CAMNOC-0055-RUN.txt
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_camnoc_0055=1' /proc/cmdline || fail 'not 0055 candidate'; grep -q '/boot/sp11-7.1.5-camera-e003h-camnoc-0055/' /proc/cmdline || fail 'wrong BOOT_IMAGE'
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'HEAD/origin divergence'; git -C "$REPO" diff --quiet || fail 'tracked dirty'; git -C "$REPO" diff --cached --quiet || fail 'staged dirty'
[ -f "$AUTH" ] || fail 'authorization absent'
python3 - "$AUTH" "$HEAD" "$REPO" "$NEW/asset-manifest.json" <<'PY'
import json,subprocess,sys,hashlib,pathlib
a=json.load(open(sys.argv[1])); head=sys.argv[2]; repo=sys.argv[3]; man=json.load(open(sys.argv[4])); root=pathlib.Path(sys.argv[4]).parent
assert a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']; assert a['purpose']=='0055 telemetry-only CAMNOC RT rate comparison'; ex=a['execution_contract']; assert ex['boot_count']==1 and ex['root_helper_invocation_count']==1 and ex['same_boot_retry'] is False and ex['camera_programming_delta']==0
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['package_commit'],head],stdout=subprocess.DEVNULL)
for r,h in man['assets'].items(): assert hashlib.sha256((root/r).read_bytes()).hexdigest()==h
PY
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'saved_entry drift'; ! grep -q '^next_entry=.' <<<"$ENV" || fail 'next_entry not empty after one-shot'
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module already loaded: $m"; done
for p in "$RUN" "$NEW/RUNTIME-CAMNOC-0055-CLOCK.txt" "$NEW/RUNTIME-CAMNOC-0055-CLOCK.ready" "$NEW/RUNTIME-CAMNOC-0055-RTCDM-STAGES.txt" "$NEW/RUNTIME-CAMNOC-0055-WATCHER.ready"; do sudo -n test ! -e "$p" || fail "preexisting runtime artifact: $p"; done
echo 'PASS: 0055 authorization-aware runtime preflight clean'
