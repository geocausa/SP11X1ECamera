#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004en-natural-cap-release-one-shot-runtime
BOOT=/boot/sp11-7.1.5-camera-e004en-natural-cap-release-one-shot-runtime
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004en_natural_cap_release
ID=sp11-camera-e004en-natural-cap-release-one-shot-runtime-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process || fail overlap
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ] || fail origin
(cd "$R" && sha256sum -c "$D/KNOWN-DIRTY.sha256" >/dev/null) || fail dirty_hash
mapfile -t dirty < <(git -C "$R" diff --name-only | sort); expected=(CONTINUE.md HANDOFF.md PROJECT_STATE.md README.md state/project.yaml); [ "${dirty[*]}" = "${expected[*]}" ] || fail dirty_set
PYTHONDONTWRITEBYTECODE=1 python3 "$R/src/sp11-camera-stack/verify-live-unactivated.py" >/dev/null || fail package_live
[ "$(sha256sum /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256|awk '{print $1}')" = 3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71 ] || fail package_manifest
sudo -n test ! -e "$BOOT" || fail boot_exists; sudo -n test ! -e "$ENTRY" || fail entry_exists; ! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub_exists
for x in RUNTIME-PREFLIGHT.txt UNIFIED-DISCOVERY.json LOAD-MEDIA.txt DMESG.txt ATTEMPT1-CONSUMED.marker ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json GOLDEN-RETURN.txt RETIRE.txt; do [ ! -e "$D/$x" ] || fail prior_$x; done
for m in qcom_camss imx681 ov13858 sp11_vd55g0 e004t_csiphy_readback_test i2c_qcom_cci; do [ ! -d "/sys/module/$m" ] || fail module_$m; done
[ ! -e /dev/media0 ] || fail media
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
{
 echo schema=sp11-camera-e004en-prearm-live-v1; echo status=PASS_READY_TO_INSTALL; echo time=$(date -Ins); echo head=$(git -C "$R" rev-parse HEAD)
 echo package_manifest_sha256=3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71
 echo action=front_r27_natural_cap_release_one_shot; echo ir_stream=NO; echo illumination=NO; echo secureisp=NO; echo retry=NO
} > "$D/PREARM-LIVE.txt"
echo E004EN_PREARM=PASS PACKAGE=INSTALLED_UNACTIVATED NATURAL_CAP_RELEASE_ONE_SHOT=PLANNED RETRY=NO
