#!/usr/bin/env bash
# E004lq: root-private, non-default, not-armed camera-capable diagnostic assets.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004lq-guarded-rgb-configure-one-shot
SRC=/tmp/sp11-e004lq-hardware
PROBE=/var/lib/sp11-e004lq-build/configure-only-probe
D=/var/lib/sp11-camera-e004lq
BOOT=/boot/sp11-7.1.5-camera-e004lq-configure
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004lq
SERVICE=/etc/systemd/system/sp11-camera-e004lq-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004lq-run-once
ID=sp11-camera-e004lq-configure-one-shot
cd "$R"
[[ $EUID -ne 0 ]]
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$H/CONSUMED.json" && ! -e "$H/RESULT.json" && ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]]
[[ ! -e "$D" && ! -e "$BOOT" && ! -e "$ENTRY" && ! -e "$SERVICE" && ! -e "$RUNNER" ]]
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
[[ "$(sudo -n stat -c '%u:%g:%a' /var/lib/sp11-e004lq-build)" == "0:0:700" ]]
sudo -n test -f /var/lib/sp11-e004lq-build/build/src/ipa/simple/ipa_soft_simple.so.sign
[[ "$(sha256sum /tmp/sp11-e004ld-kernel-_ai7a8ph/source/camss/qcom-camss.ko | awk '{print $1}')" == 8aa3e7cb3ce790a0b37b6494f540e4075d78f8b3fed69ed415e81f4da5cfb75d ]]
[[ "$(sha256sum /tmp/sp11-e004ld-kernel-_ai7a8ph/source/imx681/imx681.ko | awk '{print $1}')" == 448bd926193c003cdf3c1407382c3de0af7ba0ebfdca7cb36d8c797797c0bc6c ]]

[[ "$(sha256sum "$SRC/HARDWARE-MANIFEST.sha256" | awk '{print $1}')" == ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c ]]
( cd "$SRC"; sha256sum -c HARDWARE-MANIFEST.sha256 >/dev/null )
[[ "$(sudo -n sha256sum "$PROBE" | awk '{print $1}')" == 7b391148bc4356cad6897871eae022864a63ccc84b3f37275b3b98bbe15f236d ]]
[[ "$(sha256sum "$SRC/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" | awk '{print $1}')" == 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ]]
[[ "$(sudo -n sha256sum "/var/lib/sp11-e004lq-build/source/src/libcamera/pipeline/simple/simple.cpp" | awk '{print $1}')" == 248a7c65f7997951b36923753fec8f1a247b253217062456a964b157569c94e2 ]]
[[ "$(sha256sum "$H/sp11-libcamera-e004lq-lease.h" | awk '{print $1}')" == 050cb4e9453f47785c60e69abc37441ae7779948f60b03b7a9d464ce9b7e31c9 ]]
bash -n "$H/run-once.sh" "$H/arm-once.sh" "$H/retire-after-golden.sh"
tail -n +3 "$H/99zzzzzz_sp11_camera_e004lq" | grub-script-check
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
[[ "$(systemctl show grub2-common.service -p DropInPaths --value)" == /etc/systemd/system/grub2-common.service.d/90-sp11-serialize-grubenv-writers.conf ]]
# All new install destinations are private and isolated; the Golden kernel,
# original DTB/initrd, saved_entry and /lib/modules are never modified.
sudo -n install -d -m 0700 "$D" "$D/modules" "$D/output" "$D/candidate"
for name in qcom-camss imx681 ov13858 sp11-vd55g0; do
  sudo -n install -m 0600 "$SRC/modules/$name.ko" "$D/modules/$name.ko"
done
# Exact byte-identical E004le IMX681/CAMSS pair is separate from
# the canonical production package; do not alter package authority.
sudo -n install -m 0600 /tmp/sp11-e004ld-kernel-_ai7a8ph/source/camss/qcom-camss.ko "$D/candidate/qcom-camss.ko"
sudo -n install -m 0600 /tmp/sp11-e004ld-kernel-_ai7a8ph/source/imx681/imx681.ko "$D/candidate/imx681.ko"
# Bundle the exact built source/binaries into root-only nondefault stage.
sudo -n install -d -m 0700 "$D/bundle"
sudo -n cp -a "/var/lib/sp11-e004lq-build/build" "$D/bundle/build"
sudo -n cp -a "/var/lib/sp11-e004lq-build/source" "$D/bundle/source"
sudo -n chown -R root:root "$D/bundle"
sudo -n chmod -R go-rwx "$D/bundle"
sudo -n test -x "$D/bundle/build/src/apps/cam/cam"
sudo -n install -m 0700 "$PROBE" "$D/bundle/configure-only-probe"
sudo -n test -f "$D/bundle/build/src/ipa/simple/ipa_soft_simple.so.sign"
sudo -n install -m 0600 "$H/run-once.sh" "$D/run-once.sh"
sudo -n install -m 0600 "$H/sp11-camera-e004lq-one-shot.service" "$D/service.txt"
sudo -n install -m 0600 "$H/99zzzzzz_sp11_camera_e004lq" "$D/entry.txt"
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
sudo -n sh -c 'cd /var/lib/sp11-camera-e004lq && sha256sum modules/*.ko candidate/*.ko bundle/configure-only-probe bundle/build/src/apps/cam/cam bundle/build/src/libcamera/libcamera.so.0.7.0 bundle/build/src/libcamera/base/libcamera-base.so.0.7.0 bundle/build/src/ipa/simple/ipa_soft_simple.so bundle/build/src/ipa/simple/ipa_soft_simple.so.sign bundle/source/src/libcamera/pipeline/simple/simple.cpp bundle/source/src/libcamera/pipeline/simple/sp11-libcamera-e004lq-lease.h run-once.sh service.txt entry.txt > SESSION-ASSETS.sha256'
sudo -n sh -c 'cd /var/lib/sp11-camera-e004lq && sha256sum -c SESSION-ASSETS.sha256 >/dev/null'
sudo -n install -d -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004lq-configure"
sudo -n install -m 0644 "$SRC/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
[[ "$(sudo -n sha256sum "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" | awk '{print $1}')" == bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a ]]
[[ "$(sudo -n sha256sum "$BOOT/initrd.img-7.1.5-sp11-camera-e004lq-configure" | awk '{print $1}')" == ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d ]]
sudo -n install -m 0755 "$H/99zzzzzz_sp11_camera_e004lq" "$ENTRY"
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-camera-e004lq-one-shot.service" "$SERVICE"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-camera-e004lq-one-shot.service
sudo -n update-grub >/dev/null
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
echo E004LQ_INSTALLED_UNARMED=PASS_GOLDEN_SAVED_UNCHANGED
