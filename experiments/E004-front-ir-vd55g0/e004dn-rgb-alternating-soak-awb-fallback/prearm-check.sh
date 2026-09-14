#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dn-rgb-alternating-soak-awb-fallback
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
IG=$BASE/ig-unified-rear-to-front-r16-r27
IB=$BASE/ib-unified-current-golden-rear-front-dtb
R3=$R/experiments/E002-rear-ov13858-dphy/e002k-rear-native-productionization/d-source-integration/r3-source-integrated-runtime
BOOT=/boot/sp11-7.1.5-camera-e004dn-rgb-alternating-soak-awb-fallback
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004dn_rgb_alternating_soak_awb_fallback
ID=sp11-camera-e004dn-rgb-alternating-soak-awb-fallback-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process || fail overlap
[ "$(git -C "$R" branch --show-current)" = experiment/e004-front-ir-vd55g0 ] || fail branch
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ] || fail origin
(cd "$R" && sha256sum -c "$D/KNOWN-DIRTY.sha256" >/dev/null) || fail dirty_hash
mapfile -t dirty < <(git -C "$R" diff --name-only | sort)
expected=(CONTINUE.md HANDOFF.md PROJECT_STATE.md README.md state/project.yaml)
[ "${dirty[*]}" = "${expected[*]}" ] || fail dirty_set
PYTHONDONTWRITEBYTECODE=1 python3 "$R/experiments/E004-front-ir-vd55g0/e004dm-front-awb-windows-fallback-port/verify_e004dm.py" >/tmp/e004dn-e004dm-verify.txt || fail e004dm
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a ] || fail kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d ] || fail initrd
[ "$(sha256sum "$IB/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb"|awk '{print $1}')" = 5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321 ] || fail dtb
sudo -n test ! -e "$BOOT" || fail boot_exists
sudo -n test ! -e "$ENTRY" || fail entry_exists
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub_exists
[ ! -e "$D/runtime-output" ] && [ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] && [ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] || fail prior_attempt
rm -rf "$D/build" "$D/package-root"; mkdir -p "$D/build"
cp "$IG/build/front-imx681-capture" "$IG/build/front-imx681-bootstrap-controls" "$IG/build/qcom-camss.ko" "$IG/build/imx681.ko" "$D/build/"
cp "$R3/ov13858-production.ko" "$D/build/ov13858-production.ko"
for pair in \
 'front-imx681-capture 70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d' \
 'front-imx681-bootstrap-controls 4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce' \
 'qcom-camss.ko 7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95' \
 'imx681.ko ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6' \
 'ov13858-production.ko 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309'; do set -- $pair; [ "$(sha256sum "$D/build/$1"|awk '{print $1}')" = "$2" ] || fail artifact_$1; done
BUILD_DIR="$D/build" "$R/src/front-imx681/stage-package.sh" "$D/package-root" >/tmp/e004dn-stage-package.txt
[ "$(sha256sum "$D/package-root/PACKAGE-MANIFEST.sha256"|awk '{print $1}')" = 60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a ] || fail package_manifest
(cd "$D/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail package_verify
P=$D/package-root/usr/lib/sp11-front-imx681
[ "$(sha256sum "$P/build/qcom-camss.ko"|awk '{print $1}')" = 7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95 ] || fail package_camss
[ "$(sha256sum "$P/build/imx681.ko"|awk '{print $1}')" = ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ] || fail package_imx681
[ "$(sha256sum "$P/userspace/iq/live-iq-producer.py"|awk '{print $1}')" = 7c13bc25517698cf53a8b362857852de7dd674de5c108eed4c9f5b788eed3f61 ] || fail package_producer
[ "$(sha256sum "$P/userspace/iq/vendor/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/el-calibrated-awb-scalar-join/awb_scalar.py"|awk '{print $1}')" = 06bfd6cd4dc4b059e2aa021d3f261b90ed2ceff90450af4bcbe4545fc5c14c0f ] || fail package_awb
python3 - <<'PY' || fail free_space
import os
v=os.statvfs('/home/geoca/Documents/SP11-PROJECT');assert v.f_bavail*v.f_frsize>=8589934592
PY
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail module_$m; done
echo 'E004DN_PREARM=PASS E004DM=PASS MODULES=ACCEPTED PACKAGE=60a34901 LEGS=6 TRANSITIONS=5 RETRY=NO'
