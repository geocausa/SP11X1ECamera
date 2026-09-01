#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera; NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid-epoch-lifecycle-bridge-0063-candidate; VIDEO=${1:-/dev/video7}; TRIGGER=/sys/bus/platform/devices/acb7000.isp/e003h_pix_run_once; DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
OUT=$NEW/RUNTIME-CSIDEPOCH-0063-QC10C.bin; RUNLOG=$NEW/RUNTIME-CSIDEPOCH-0063-RUN.txt; POST=$NEW/RUNTIME-CSIDEPOCH-0063-POST.txt; DMESG=$NEW/RUNTIME-CSIDEPOCH-0063-DMESG.txt; HASHES=$NEW/RUNTIME-CSIDEPOCH-0063-HASHES.txt; STAGES=$NEW/RUNTIME-CSIDEPOCH-0063-RTCDM-STAGES.txt; READY=$NEW/RUNTIME-CSIDEPOCH-0063-WATCHER.ready; AUTH=$NEW/AUTHORIZATION.json; HELPER=$NEW/e003h-pix-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git; git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
python3 - "$AUTH" "$HEAD" "$REPO" <<'PY'
import json,subprocess,sys
a,head,repo=sys.argv[1:]; x=json.load(open(a)); assert x['accepted'] and x['runtime_authorized'] and not x['production_parity_authorized']; subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',x['package_commit'],head]); e=x['execution_contract']; assert e['boot_count']==1 and e['root_helper_invocation_count']==1 and e['same_boot_retry'] is False and e['hardware_delta']=='NONE' and e['software_delta']=='CSID_EPOCH_LIFECYCLE_BRIDGE_0063_ONLY'
PY
grep -q 'sp11_camera_e003h_csidepoch_0063=1' /proc/cmdline || fail boot; sudo -n test -w "$TRIGGER" || fail trigger; [ -c "$VIDEO" ] || fail video; sudo -n grep -qx READY "$READY" || fail watcher; grep -q 'name=idle' "$DIAG" || fail idle; [ ! -e "$RUNLOG" ] || fail retry; [ ! -e "$OUT" ] || fail output
: > "$RUNLOG"; { echo "START=$(date -Ins)"; echo "VIDEO=$VIDEO"; echo "HEAD=$HEAD"; echo HELPER_INVOCATION_COUNT=1; echo HARDWARE_DELTA=NONE; echo SOFTWARE_DELTA=CSID_EPOCH_LIFECYCLE_BRIDGE_0063_ONLY; } >> "$RUNLOG"; sync
trap 'sync; sudo -n systemctl reboot' EXIT
set +e; sudo -n "$HELPER" "$VIDEO" "$TRIGGER" "$OUT" >> "$RUNLOG" 2>&1; RC=$?; set -e
{ echo "RUN_RC=$RC"; echo "END=$(date -Ins)"; } >> "$RUNLOG"
{ echo "RUN_RC=$RC"; echo "POST_TIME=$(date -Ins)"; echo -n LIVE_DIAG=; cat "$DIAG" 2>&1 || true; [ -f "$OUT" ] && stat -c 'QC10C_BYTES=%s' "$OUT" || echo QC10C_OUTPUT=absent; echo WATCHER:; sudo -n cat "$STAGES" 2>/dev/null || true; } > "$POST"
sudo -n dmesg -T | grep -Ei 'E003h|CSID1|VFE1|RT-CDM|imx681|qcom.*cam|CAMSS|SMMU|IOMMU|panic|oops|SError|BUG:' | tail -n 1200 > "$DMESG" || true
sha256sum "$RUNLOG" "$POST" "$DMESG" > "$HASHES"; sudo -n test -f "$STAGES" && sudo -n sha256sum "$STAGES" >> "$HASHES"; sync; echo "ARCHIVED_RC=$RC"
