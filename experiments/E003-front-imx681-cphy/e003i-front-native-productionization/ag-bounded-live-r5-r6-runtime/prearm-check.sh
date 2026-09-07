#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ag-bounded-live-r5-r6-runtime
AE=$BASE/ae-bounded-live-trigger-iq-producer
E=$BASE/e-template-free-capsule
Z=$BASE/z-live-3a-runtime
fail(){ echo "FAIL: $*" >&2; exit 1; }

python3 "$D/verify.py"
test "$(uname -r)" = '7.1.5-sp11-render-parity-v4+' || fail kernel
systemctl is-active --quiet pislave.service || fail pislave
sudo -n true || fail sudo
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
if grep -q '^next_entry=.' <<<"$ENV"; then fail next; fi
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged
K=$(mktemp); trap 'rm -f "$K"' EXIT
journalctl -b -k --no-pager > "$K"
for n in 'TLB sync timed out -- SMMU may be deadlocked' 'vblank wait timed out' 'Internal error: Oops' 'soft lockup'; do ! grep -Fiq "$n" "$K" || fail "boot_$n"; done
rm -f "$K"; trap - EXIT

# Production composition must stay byte-exact without the broad disassembly extractor.
python3 "$E/inspect-template-free-composer.py" >/dev/null

# Reproduce the environment that failed AF: root Python, retained Z G1-G3 paired stats.
# Capstone presence is informational only; AG must not depend on it either way.
if sudo -n python3 -c 'import capstone' >/dev/null 2>&1; then ROOT_CAPSTONE=PRESENT; else ROOT_CAPSTONE=ABSENT; fi
T=$(mktemp -d); trap 'sudo -n rm -rf "$T"' EXIT
gcc -O2 -std=c11 -Wall -Wextra -Werror "$AE/e003i-ae-six-frame-live-iq.c" -o "$T/capture-helper"
sudo -n python3 "$AE/live-iq-producer.py" --mode offline --snapshot-dir "$Z" \
  --output-dir "$T/root-producer" --manifest "$T/root-producer/RESULT.json" > "$T/root-producer.log"
R5=$(sudo -n sha256sum "$T/root-producer/R5-dynamic.bin" | awk '{print $1}')
R6=$(sudo -n sha256sum "$T/root-producer/R6-dynamic.bin" | awk '{print $1}')
[ "$R5" = '350fed1aaa4c6c3e9fbed8d3e63f14fcaf7a6cf80be9e8f800536a0ddfa14795' ] || fail root_r5
[ "$R6" = 'e85dbe7b8b46837e09207586b56e4e648d674ea4663d18ea6b46d1b1f885dd8c' ] || fail root_r6
sudo -n python3 - "$T/root-producer/RESULT.json" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]))
assert j['status']=='PASS' and j['mode']=='offline'
assert [(r['generation'],r['request_target']) for r in j['rows']]==[(1,None),(2,5),(3,6)]
PY
printf 'AG_ROOT_RUNTIME_PREFLIGHT=PASS ROOT_CAPSTONE=%s R5=%s R6=%s\n' "$ROOT_CAPSTONE" "$R5" "$R6"
