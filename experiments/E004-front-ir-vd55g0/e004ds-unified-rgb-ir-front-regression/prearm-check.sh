#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004ds-unified-rgb-ir-front-regression
DR=$R/experiments/E004-front-ir-vd55g0/e004dr-unified-rgb-ir-rear-regression-r2
DO=$R/experiments/E004-front-ir-vd55g0/e004do-unified-rgb-ir-offline-authority
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
IG=$BASE/ig-unified-rear-to-front-r16-r27
BOOT=/boot/sp11-7.1.5-camera-e004ds-unified-rgb-ir-front
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004ds_unified_rgb_ir_front
ID=sp11-camera-e004ds-unified-rgb-ir-front-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
HEAD=$(git -C "$R" rev-parse HEAD); ORIGIN=$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)
[ "$HEAD" = "$ORIGIN" ] || fail origin; [ "$(git -C "$R" branch --show-current)" = experiment/e004-front-ir-vd55g0 ] || fail branch
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process --expect-head "$HEAD" --expect-origin "$ORIGIN" || fail overlap
(cd "$R" && sha256sum -c "$D/KNOWN-DIRTY.sha256" >/dev/null) || fail dirty_hash
mapfile -t dirty < <(git -C "$R" diff --name-only | sort); expected=(CONTINUE.md HANDOFF.md PROJECT_STATE.md README.md state/project.yaml); [ "${dirty[*]}" = "${expected[*]}" ] || fail dirty_set
PYTHONDONTWRITEBYTECODE=1 python3 "$DR/verify-close.py" >/tmp/e004ds-parent.txt || fail parent
PYTHONDONTWRITEBYTECODE=1 python3 "$R/experiments/E004-front-ir-vd55g0/e004dm-front-awb-windows-fallback-port/verify_e004dm.py" >/tmp/e004ds-awb.txt || fail awb
[ "$(sha256sum "$DO/x1e80100-microsoft-denali-sp11-e004do-unified-rgb-ir.dtb"|awk '{print $1}')" = 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ] || fail dtb
"$D/build-authority.sh" >/tmp/e004ds-build-authority.txt || fail authority
(cd "$D/build" && sha256sum -c AUTHORITY.sha256 >/dev/null) || fail authority_hashes
# Stage the exact accepted E004dn front package from committed source + accepted RGB artifacts.
rm -rf "$D/front-package-build" "$D/package-root"; mkdir -p "$D/front-package-build"
cp "$IG/build/front-imx681-capture" "$IG/build/front-imx681-bootstrap-controls" "$IG/build/qcom-camss.ko" "$IG/build/imx681.ko" "$D/front-package-build/"
for pair in \
 'front-imx681-capture 70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d' \
 'front-imx681-bootstrap-controls 4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce' \
 'qcom-camss.ko 7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95' \
 'imx681.ko ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6'; do set -- $pair; [ "$(sha256sum "$D/front-package-build/$1"|awk '{print $1}')" = "$2" ] || fail front_artifact_$1; done
BUILD_DIR="$D/front-package-build" "$R/src/front-imx681/stage-package.sh" "$D/package-root" >/tmp/e004ds-stage-package.txt
[ "$(sha256sum "$D/package-root/PACKAGE-MANIFEST.sha256"|awk '{print $1}')" = 60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a ] || fail package_manifest
(cd "$D/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail package_verify
P=$D/package-root/usr/lib/sp11-front-imx681
[ "$(sha256sum "$P/bin/front-imx681-launcher.py"|awk '{print $1}')" = 5583724848f5fc09684a779b90e0a5b4cea4e4cffe2f91859a6332623c1de424 ] || fail launcher
[ "$(sha256sum "$P/userspace/iq/live-iq-producer.py"|awk '{print $1}')" = 7c13bc25517698cf53a8b362857852de7dd674de5c108eed4c9f5b788eed3f61 ] || fail producer
[ "$(sha256sum "$P/userspace/iq/vendor/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/el-calibrated-awb-scalar-join/awb_scalar.py"|awk '{print $1}')" = 06bfd6cd4dc4b059e2aa021d3f261b90ed2ceff90450af4bcbe4545fc5c14c0f ] || fail awb_source
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a ] || fail kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d ] || fail initrd
sudo -n test ! -e "$BOOT" || fail boot_exists; sudo -n test ! -e "$ENTRY" || fail entry_exists; ! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub_exists
for x in RUNTIME-PREFLIGHT.txt UNIFIED-DISCOVERY.json LOAD-MEDIA.txt DMESG.txt ATTEMPT1-CONSUMED.marker ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json; do [ ! -e "$D/$x" ] || fail prior_$x; done
for m in qcom_camss imx681 ov13858 sp11_vd55g0 e004t_csiphy_readback_test i2c_qcom_cci; do [ ! -d "/sys/module/$m" ] || fail module_$m; done
[ ! -e /dev/media0 ] || fail media
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
{
 echo schema=sp11-camera-e004ds-prearm-v1; echo status=PASS_READY_TO_INSTALL; echo time=$(date -Ins); echo head=$HEAD
 echo dtb_sha256=3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb
 cat "$D/build/AUTHORITY.sha256"
 echo front_package_manifest_sha256=60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a
 echo action=one_front_r27_production_run_under_three_camera_bind
 echo post_g3_policy=shadow; echo rear_stream=NO; echo ir_stream=NO; echo illumination=NO; echo secureisp=NO; echo retry=NO
} > "$D/PREARM-LIVE.txt"
echo 'E004DS_PREARM=PASS FRONT_R27=PLANNED PACKAGE=60a34901 REAR_IR_STREAM=NO RETRY=NO'
