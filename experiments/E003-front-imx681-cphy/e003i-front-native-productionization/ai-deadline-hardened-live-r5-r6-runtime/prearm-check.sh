#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ai-deadline-hardened-live-r5-r6-runtime
AE=$BASE/ae-bounded-live-trigger-iq-producer
E=$BASE/e-template-free-capsule
Z=$BASE/z-live-3a-runtime
AH=$BASE/ah-bounded-live-r5-r6-runtime/runtime-output
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
python3 "$E/inspect-template-free-composer.py" >/dev/null
if sudo -n python3 -c 'import capstone' >/dev/null 2>&1; then ROOT_CAPSTONE=PRESENT; else ROOT_CAPSTONE=ABSENT; fi

# Revalidate the fixture-free scheduling margin under root before any boot mutation.
T=$(mktemp -d); trap 'sudo -n rm -rf "$T"' EXIT
sudo -n python3 "$AE/prove-live-deadline-hardening.py" --iterations 20 --manifest "$T/deadline.json" > "$T/deadline.log"
sudo -n python3 - "$T/deadline.json" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]));assert j['status']=='PASS'
assert j['scheduler']=={'cpu':11,'nice':-20,'scheduler':0}
for g in ('G2','G3'):
 assert j['all_cpu_contention'][g]['p95_ms'] < j['frame_budget_ms']
 assert j['all_cpu_contention'][g]['max_ms'] < j['frame_budget_ms']
PY

# Exact consumed-AH G1-G3 evidence: prove current producer content on the stream that missed the deadline.
want_stats=(
 '9df1b384a8cedf9dd1eb09a644d186f0b5458844410df5beb1851c5dde0275cc'
 '05efbe907f527d27bacb58b388ba5e6a51faab22def18f3b127571997da4a70a'
 'b0fbfb45c87d9a883ff705d5c1a56be51018bc31f16bfbad937feba4725209b5'
)
want_tlbg=(
 '101031708a7d4c704b8265f30272071e14683ffb2af8bbc179d4d62d1ccc8efb'
 '143141b56fad0539db39dce92f6ff32c407535727af78eef6b7860c5a0144b36'
 '4d5d6c9794654750431c6b88336e97456d5fd93060baf7d239dfe811e8f168bb'
)
for i in 0 1 2; do
  got=$(sudo -n sha256sum "$AH/STATS3A-$i.bin" | awk '{print $1}'); [ "$got" = "${want_stats[$i]}" ] || fail "AH_stats_$i"
  got=$(sudo -n sha256sum "$AH/TLBG-$i.bin" | awk '{print $1}'); [ "$got" = "${want_tlbg[$i]}" ] || fail "AH_tlbg_$i"
done

gcc -O2 -std=c11 -Wall -Wextra -Werror "$AE/e003i-ae-six-frame-live-iq.c" -o "$T/capture-helper"
sudo -n python3 "$AE/live-iq-producer.py" --mode offline --snapshot-dir "$AH" \
  --output-dir "$T/root-producer" --manifest "$T/root-producer/RESULT.json" > "$T/root-producer.log"
R5=$(sudo -n sha256sum "$T/root-producer/R5-dynamic.bin" | awk '{print $1}')
R6=$(sudo -n sha256sum "$T/root-producer/R6-dynamic.bin" | awk '{print $1}')
[ "$R5" = '493117d029bac7910b41292e738685fdfe5a22ec52676fb415a27bfbb3c46ca5' ] || fail root_r5
[ "$R6" = 'dac798043c9d14e8118bbed803bb2b3aa7f1a7532d2e4838ee88790c69c18115' ] || fail root_r6
sudo -n python3 - "$T/root-producer/RESULT.json" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]));assert j['status']=='PASS' and j['mode']=='offline'
assert [(r['generation'],r['request_target']) for r in j['rows']]==[(1,None),(2,5),(3,6)]
assert all(r['lsc']['cct_selector_mode']=='gap_4500_5000' for r in j['rows'])
assert all(r['lsc']['aec_selector_mode']=='gap_390_490' for r in j['rows'])
PY
# Retained-Z must remain bit-identical after live-only hardening.
sudo -n python3 "$AE/prove-offline-producer.py" --snapshot-dir "$Z" --iterations 20 --manifest "$T/z.json" > "$T/z.log"
printf 'AI_ROOT_RUNTIME_PREFLIGHT=PASS ROOT_CAPSTONE=%s AH_R5=%s AH_R6=%s\n' "$ROOT_CAPSTONE" "$R5" "$R6"
