#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-common-lifecycle-0044-candidate
OLD=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate
CAMSS=$ROOT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko
SENSOR=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-front-first-frame-runtime/imx681.ko
DTB=$OLD/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
CAP=$OLD/firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin
HELPER=$OLD/e003h-pix-one-shot
AUTH=$NEW/AUTHORIZATION.json
PKG=$NEW/package-inspection.json
RUNLOG=$NEW/RUNTIME-CSID1-0044-RUN.txt
OUT=$NEW/RUNTIME-CSID1-0044-QC10C.bin
STAGES=$NEW/RUNTIME-CSID1-0044-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-CSID1-0044-WATCHER.ready
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_csid1_0044=1' /proc/cmdline || fail 'not 0044 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-csid1-0044/' /proc/cmdline || fail 'wrong candidate BOOT_IMAGE'
HEAD=$(git -C "$REPO" rev-parse HEAD)
[ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'
git -C "$REPO" diff --cached --quiet || fail 'staged worktree dirty'
[ -f "$AUTH" ] || fail 'authorization file absent'
[ -f "$PKG" ] || fail 'package inspection absent'
python3 - "$AUTH" "$HEAD" "$PKG" "$REPO/provenance/front-parity.json" "$CAMSS" "$SENSOR" "$DTB" "$CAP" "$HELPER" "$REPO" <<'PY' || exit 1
import hashlib,json,subprocess,sys
au_path,head,pkg_path,prov_path,camss,sensor,dtb,cap,helper,repo=sys.argv[1:]
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
au=json.load(open(au_path)); pkg=json.load(open(pkg_path))
assert au.get('accepted') is True and au.get('runtime_authorized') is True
assert au.get('production_parity_authorized') is False
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',au['package_commit'],head],stdout=subprocess.DEVNULL)
ex=au['execution_contract']
assert ex['boot_count']==1 and ex['root_helper_invocation_count']==1 and ex['same_boot_retry'] is False
assert ex['persistent_rtcdm_observer_required'] is True
assert au['package_inspection_sha256']==sha(pkg_path)
assert au['bounded_provenance_sha256']==sha(prov_path)
assert au['boot']['id']=='sp11-camera-e003h-csid1-0044-one-shot'
assert au['boot']['cmdline_marker']=='sp11_camera_e003h_csid1_0044=1'
actual={'camss_sha256':sha(camss),'sensor_sha256':sha(sensor),'dtb_sha256':sha(dtb),'capsule_sha256':sha(cap),'helper_sha256':sha(helper)}
for k,v in actual.items(): assert au['candidate'][k]==v, (k,au['candidate'][k],v)
assert pkg.get('accepted') is True and pkg.get('candidate_boot_installed') is True
PY
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail 'bounded provenance not green'
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'Golden saved_entry drift'
if grep -q '^next_entry=.' <<<"$ENV"; then fail 'next_entry must be empty after candidate one-shot boot'; fi
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module already loaded: $m"; done
[ ! -e "$RUNLOG" ] || fail 'RUN log already exists; refusing retry'
[ ! -e "$OUT" ] || fail 'output path already exists'
sudo -n test ! -e "$STAGES" || fail 'stages file already exists'
sudo -n test ! -e "$READY" || fail 'watcher ready file already exists'
[ "$(fdtget -l "$DTB" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail 'front-only CAMSS ports drift'
REG=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 reg)
grep -q 'ac71000 0 f000' <<<"$REG" || fail 'VFE1 span drift'
grep -q 'ac26000 0 1000' <<<"$REG" || fail 'RT-CDM1 resource drift'
IOMMUS=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 iommus)
[ "$IOMMUS" = '3d 800 60 3d 820 60 3d 840 60 3d 860 60 3d 18a0 0' ] || fail "CAMSS IOMMU set drift: $IOMMUS"
echo 'PASS: 0044 authorization-aware runtime preflight is clean before module load'
