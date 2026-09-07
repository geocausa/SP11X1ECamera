#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ah-bounded-live-r5-r6-runtime
AE=$BASE/ae-bounded-live-trigger-iq-producer
E=$BASE/e-template-free-capsule
Z=$BASE/z-live-3a-runtime
AG=$BASE/ag-bounded-live-r5-r6-runtime/runtime-output
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

# The fresh AH selector is authorized by the actual consumed-AG G1-G3 evidence, not just retained Z.
want_stats=(
 '61d1890aaf16b5bb5d31712d0fe2ad94878e04abead7ba74c22ccec29e7f2f8b'
 'd9a8f5eb88f1282e9d98d396baba8d711f5725d0714b66d0d6be12f6c8e77290'
 '865b1bdfca72a304c809e3e4e070fe198076478cf8949a41467f4bfc507aae24'
)
want_tlbg=(
 'f4a34cc542d5d48a1304423f98a0a49e77734acf9a60cc2dfd782d5ceffe63b4'
 '25d2812fb9b114f18a2a459c58a27eb773a09669af7935c3bde2504c0ce9b67d'
 '4c13b9f63b8b2c569fce60f0ec086ca248b9ce86a16a438715dede5a9e9aaf40'
)
for i in 0 1 2; do
  got=$(sudo -n sha256sum "$AG/STATS3A-$i.bin" | awk '{print $1}'); [ "$got" = "${want_stats[$i]}" ] || fail "AG_stats_$i"
  got=$(sudo -n sha256sum "$AG/TLBG-$i.bin" | awk '{print $1}'); [ "$got" = "${want_tlbg[$i]}" ] || fail "AG_tlbg_$i"
done

T=$(mktemp -d); trap 'sudo -n rm -rf "$T"' EXIT
gcc -O2 -std=c11 -Wall -Wextra -Werror "$AE/e003i-ae-six-frame-live-iq.c" -o "$T/capture-helper"
# Full root producer on actual AG captures must now pass and generate the corrected identities.
sudo -n python3 "$AE/live-iq-producer.py" --mode offline --snapshot-dir "$AG" \
  --output-dir "$T/root-producer" --manifest "$T/root-producer/RESULT.json" > "$T/root-producer.log"
R5=$(sudo -n sha256sum "$T/root-producer/R5-dynamic.bin" | awk '{print $1}')
R6=$(sudo -n sha256sum "$T/root-producer/R6-dynamic.bin" | awk '{print $1}')
[ "$R5" = 'b05698889f607d5786a441a7c85ef07b6f61852d20a1894ff8f4919b07051d94' ] || fail root_r5
[ "$R6" = 'f694734412fe7cf4669fd1bfadb0f7eecc4d8f4b34f94f60a4a9068537dc546e' ] || fail root_r6
sudo -n python3 - "$T/root-producer/RESULT.json" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]))
assert j['status']=='PASS' and j['mode']=='offline'
assert [(r['generation'],r['request_target']) for r in j['rows']]==[(1,None),(2,5),(3,6)]
assert all(r['lsc']['cct_selector_mode']=='gap_4500_5000' for r in j['rows'])
assert all(r['lsc']['aec_selector_mode']=='gap_390_490' for r in j['rows'])
PY
# Cross-domain proof must also preserve retained-Z identities.
sudo -n python3 "$AE/prove-expanded-selector.py" --retained-z-dir "$Z" --actual-ag-dir "$AG" --iterations 20 --manifest "$T/selector.json" > "$T/selector.log"
sudo -n python3 - "$T/selector.json" <<'PY'
import json,sys
j=json.load(open(sys.argv[1]));assert j['status']=='PASS'
assert j['claims']['retained_z_unchanged'] and j['claims']['actual_ag_gap_supported']
PY
printf 'AH_ROOT_RUNTIME_PREFLIGHT=PASS ROOT_CAPSTONE=%s R5=%s R6=%s\n' "$ROOT_CAPSTONE" "$R5" "$R6"
