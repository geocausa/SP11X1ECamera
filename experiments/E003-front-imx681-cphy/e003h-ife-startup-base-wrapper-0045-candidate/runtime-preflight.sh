#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-ife-startup-base-wrapper-0045-candidate
CAMSS=$NEW/qcom-camss.ko
SENSOR=$NEW/imx681.ko
DTB=$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
CAP=$NEW/firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin
HELPER=$NEW/e003h-pix-one-shot
AUTH=$NEW/AUTHORIZATION.json
PKG=$NEW/package-inspection.json
RUNLOG=$NEW/RUNTIME-IFE-BASE-0045-RUN.txt
OUT=$NEW/RUNTIME-IFE-BASE-0045-QC10C.bin
STAGES=$NEW/RUNTIME-IFE-BASE-0045-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-IFE-BASE-0045-WATCHER.ready
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_ife_base_0045=1' /proc/cmdline || fail 'not 0045 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-ife-base-0045/' /proc/cmdline || fail 'wrong candidate BOOT_IMAGE'
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
assert au['boot']['id']=='sp11-camera-e003h-ife-base-0045-one-shot'
assert au['boot']['cmdline_marker']=='sp11_camera_e003h_ife_base_0045=1'
actual={'camss_sha256':sha(camss),'sensor_sha256':sha(sensor),'dtb_sha256':sha(dtb),'capsule_sha256':sha(cap),'helper_sha256':sha(helper)}
for k,v in actual.items(): assert au['candidate'][k]==v, (k,au['candidate'][k],v)
assert pkg.get('accepted') is True and pkg.get('candidate_boot_installed') is True
assert pkg.get('candidate_boot_armed') is False and pkg.get('runtime_authorized') is False
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
[ "$(sha256sum "$CAMSS" | cut -d' ' -f1)" = cfdd66c9d2c56533993f5f73831d77b3f5018c1d552183da634971378aa06923 ] || fail 'CAMSS hash drift'
[ "$(sha256sum "$SENSOR" | cut -d' ' -f1)" = 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388 ] || fail 'sensor hash drift'
[ "$(sha256sum "$DTB" | cut -d' ' -f1)" = 019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f ] || fail 'DTB hash drift'
[ "$(sha256sum "$CAP" | cut -d' ' -f1)" = 6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20 ] || fail 'capsule hash drift'
[ "$(fdtget -l "$DTB" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail 'front-only CAMSS ports drift'
IOMMUS=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 iommus)
[ "$IOMMUS" = '3d 800 60 3d 820 60 3d 840 60 3d 860 60 3d 18a0 0' ] || fail "CAMSS IOMMU set drift: $IOMMUS"
echo 'PASS: 0045 authorization-aware runtime preflight is clean before module load'
