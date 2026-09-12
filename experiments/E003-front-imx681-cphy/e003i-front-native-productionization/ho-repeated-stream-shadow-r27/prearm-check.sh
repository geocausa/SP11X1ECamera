#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ho-repeated-stream-shadow-r27
HN=$BASE/hn-snapshot-generation-reset-package
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
HC_MEDIA=/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hc/attempt1-pass-no-cap-release-20260912T060723/runtime-output/MEDIA.txt
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process || fail overlap_guard
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
python3 - <<PY || fail hn_result
import json
r=json.load(open('$HN/RESULT.json'))
assert r['status']=='PASS_OFFLINE_SNAPSHOT_GENERATION_RESET_PACKAGE'
assert r['package']['default_post_g3_policy']=='shadow'
assert r['build']['hashes']['qcom-camss.ko']=='7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95'
assert r['package']['manifest_sha256']=='8a2bf3116a9b37fbe4b213dae51cb0ff33968e591ff54c8235c36341607c32cf'
PY
[ ! -e "$D/runtime-output" ] || fail prior_runtime_output
[ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] || fail prior_attempt
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null || fail verify
rm -rf "$D/build" "$D/package-root"
KERNEL_BUILD="$K" "$R/src/front-imx681/build-production.sh" "$D/build" >/tmp/e003i-ho-build.log
for pair in \
 'front-imx681-capture 70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d' \
 'front-imx681-bootstrap-controls 4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce' \
 'qcom-camss.ko 7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95' \
 'imx681.ko ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6'; do
 set -- $pair; [ "$(sha256sum "$D/build/$1"|awk '{print $1}')" = "$2" ] || fail "build_hash_$1"
done
BUILD_DIR="$D/build" "$R/src/front-imx681/stage-package.sh" "$D/package-root" >/tmp/e003i-ho-package.log
[ "$(sha256sum "$D/package-root/PACKAGE-MANIFEST.sha256"|awk '{print $1}')" = '8a2bf3116a9b37fbe4b213dae51cb0ff33968e591ff54c8235c36341607c32cf' ] || fail package_manifest
(cd "$D/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail package_verify
P=$D/package-root/usr/lib/sp11-front-imx681
PLAN=$("$P/bin/front-imx681-launcher.py" --topology-file "$HC_MEDIA" --build-dir "$P/build" --output-dir /tmp/e003i-ho-dry)
grep -q '"post_g3_write_policy": "shadow"' <<<"$PLAN" || fail shadow_default
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved_entry
! grep -q '^next_entry=.'<<<"$ENV" || fail next_entry
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
echo 'HO_ROOT_PREARM=PASS HN_PACKAGE=PASS POLICY=shadow STREAMS=2 MODULES=production-stable'
