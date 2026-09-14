#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dp-unified-rgb-ir-receiver-coexistence
DO=$R/experiments/E004-front-ir-vd55g0/e004do-unified-rgb-ir-offline-authority
BOOT=/boot/sp11-7.1.5-camera-e004dp-unified-rgb-ir-receiver
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004dp_unified_rgb_ir_receiver
ID=sp11-camera-e004dp-unified-rgb-ir-receiver-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
HEAD=$(git -C "$R" rev-parse HEAD); ORIGIN=$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)
[ "$HEAD" = "$ORIGIN" ] || fail origin
[ "$(git -C "$R" branch --show-current)" = experiment/e004-front-ir-vd55g0 ] || fail branch
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process --expect-head "$HEAD" --expect-origin "$ORIGIN" || fail overlap
(cd "$R" && sha256sum -c "$D/KNOWN-DIRTY.sha256" >/dev/null) || fail dirty_hash
mapfile -t dirty < <(git -C "$R" diff --name-only | sort); expected=(CONTINUE.md HANDOFF.md PROJECT_STATE.md README.md state/project.yaml); [ "${dirty[*]}" = "${expected[*]}" ] || fail dirty_set
PYTHONDONTWRITEBYTECODE=1 python3 "$DO/verify_e004do.py" >/tmp/e004dp-e004do.txt || fail e004do
"$D/build-authority.sh" >/tmp/e004dp-build-authority.txt || fail build_authority
(cd "$D/build" && sha256sum -c AUTHORITY.sha256 >/dev/null) || fail build_hashes
[ "$(sha256sum "$DO/x1e80100-microsoft-denali-sp11-e004do-unified-rgb-ir.dtb"|awk '{print $1}')" = 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ] || fail dtb
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a ] || fail kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d ] || fail initrd
sudo -n test ! -e "$BOOT" || fail boot_exists
sudo -n test ! -e "$ENTRY" || fail entry_exists
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub_exists
for x in RUNTIME-PREFLIGHT.txt RUNTIME-DMESG.txt MEDIA.txt CONTROLS-IR.txt RECEIVER-READBACK.txt ATTEMPT1-CONSUMED.marker ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json; do [ ! -e "$D/$x" ] || fail prior_$x; done
for m in qcom_camss imx681 ov13858 sp11_vd55g0 e004t_csiphy_readback_test i2c_qcom_cci; do [ ! -d "/sys/module/$m" ] || fail module_$m; done
[ ! -e /dev/media0 ] || fail media
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
{
 echo schema=sp11-camera-e004dp-prearm-v1; echo status=PASS_READY_TO_INSTALL; echo time=$(date -Ins); echo head=$HEAD
 echo dtb_sha256=3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb
 cat "$D/build/AUTHORITY.sha256"
 echo action=three_sensor_bind_plus_csiphy0_receiver_readback_only
 echo sensor_stream=NO; echo capture=NO; echo illumination=NO; echo secureisp=NO; echo retry=NO
} > "$D/PREARM-LIVE.txt"
echo 'E004DP_PREARM=PASS THREE_SENSOR_BIND=PLANNED RECEIVER_ONLY=YES RETRY=NO'
