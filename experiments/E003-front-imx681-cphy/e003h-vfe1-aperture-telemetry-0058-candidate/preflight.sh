#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera; NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate; STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-static; BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-candidate/runtime-0057-analysis.json; STATIC_COMMIT=d7fe3bc4b98fab0b39c6f2681459f4acf28f3a72
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail authorization; [ ! -e "$NEW/RUNTIME-VFEAP-0058-RUN.txt" ] || fail RUN
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git; git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged; git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail static
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail provenance
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail Golden; [ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0058-static-inspection.json" "$BASE" <<'PY'
import hashlib,json,sys,pathlib
mp,new,sp,bp=sys.argv[1:]; new=pathlib.Path(new); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp)); si=json.load(open(sp)); b=json.load(open(bp))
assert m['accepted'] and not m['runtime_authorized'] and m['static_commit']=='d7fe3bc4b98fab0b39c6f2681459f4acf28f3a72'
for r,h in m['assets'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
assert sha(sp)==m['static_inspection_sha256'] and si['accepted'] and si['hardware_programming_delta']=='none'; assert sha(bp)==m['consumed_0057_analysis_sha256'] and b['accepted'] and b['authorization_consumed']
assert m['assets']['qcom-camss.ko']=='3fd0ebdc8a3f17fdc49e117d77fa10e03711dfbd27bc552e79230540f1cef80c'; assert m['assets']['imx681.ko']=='a12693a18bf2e4108dd309af68da189a2ea394a734a0c6a3c1d624ac44dea3dc'; assert m['behavior_delta']['camera_programming']=='none_vs_0057' and m['behavior_delta']['new_mmio_writes']==0
PY
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail vermagic
ENV=$(grub-editenv list); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail armed
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail module; done
[ "$(fdtget -l "$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" /soc@0/isp@acb7000/ports | tr '
' ' ' | xargs)" = 'port@2' ] || fail DT
! grep -q 'O_RDWR\|PROT_WRITE\|mm\.write' "$NEW/watch-vfe1-aperture.py" || fail watcher_write
for x in preflight.sh install-candidate.sh runtime-preflight.sh load-candidate.sh setup-pix-media.sh start-observer.sh start-vfe-observer.sh run-once.sh; do bash -n "$NEW/$x"; done
echo 'PASS: 0058 exact 0057 camera assets + read-only aperture telemetry package unarmed'
