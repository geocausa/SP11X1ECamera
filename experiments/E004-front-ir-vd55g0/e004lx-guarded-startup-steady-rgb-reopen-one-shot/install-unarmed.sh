#!/usr/bin/env bash
# E004lx: isolated root-private fixed-frame Soft IPA capture diagnostic.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004lx-guarded-startup-steady-rgb-reopen-one-shot
SRC=/tmp/sp11-e004lx-hardware
PROBE=/var/lib/sp11-e004lx-build/build/src/apps/cam/cam
D=/var/lib/sp11-camera-e004lx
BOOT=/boot/sp11-7.1.5-camera-e004lx-xrgb8888
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004lx
SERVICE=/etc/systemd/system/sp11-camera-e004lx-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004lx-run-once
ID=sp11-camera-e004lx-xrgb8888-one-shot
cd "$R"
[[ $EUID -ne 0 ]]
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$H/CONSUMED.json" && ! -e "$H/RESULT.json" && ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]]
[[ ! -e "$D" && ! -e "$BOOT" && ! -e "$ENTRY" && ! -e "$SERVICE" && ! -e "$RUNNER" ]]
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
[[ "$(sudo -n stat -c '%u:%g:%a' /var/lib/sp11-e004lx-build)" == "0:0:700" ]]
sudo -n test -f /var/lib/sp11-e004lx-build/build/src/ipa/simple/ipa_soft_simple.so.sign
[[ "$(sha256sum /tmp/sp11-e004ld-kernel-_ai7a8ph/source/camss/qcom-camss.ko | awk '{print $1}')" == 8aa3e7cb3ce790a0b37b6494f540e4075d78f8b3fed69ed415e81f4da5cfb75d ]]
[[ "$(sha256sum /tmp/sp11-e004ld-kernel-_ai7a8ph/source/imx681/imx681.ko | awk '{print $1}')" == 448bd926193c003cdf3c1407382c3de0af7ba0ebfdca7cb36d8c797797c0bc6c ]]

[[ "$(sha256sum "$SRC/HARDWARE-MANIFEST.sha256" | awk '{print $1}')" == ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c ]]
( cd "$SRC"; sha256sum -c HARDWARE-MANIFEST.sha256 >/dev/null )
[[ "$(sudo -n sha256sum "$PROBE" | awk '{print $1}')" == e980c4ba7e091c8ff3c4899f4c09086faa11d18cb0c1c508bb6dfbe5d54efc5b ]]
[[ "$(sha256sum "$SRC/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" | awk '{print $1}')" == 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ]]
[[ "$(sudo -n sha256sum "/var/lib/sp11-e004lx-build/source/src/libcamera/pipeline/simple/simple.cpp" | awk '{print $1}')" == 3b581ec2812ed08262f8e7f2fefaada0acd56ac70f279149e5d08eeaf04f5e9b ]]
[[ "$(sudo -n sha256sum "/var/lib/sp11-e004lx-build/source/src/ipa/simple/soft_simple.cpp" | awk '{print $1}')" == f9a9f417976fe99a593c3d68dde85659a20be860d19a1c61df61732efd78b4e0 ]]
[[ "$(sudo -n sha256sum "/var/lib/sp11-e004lx-build/source/src/ipa/simple/sp11-imx681-fixed-frame-agc.h" | awk '{print $1}')" == af58a47d4a2101d97841c2933040bc94d8c5d2a31c46ada346d47e9501b2f997 ]]
[[ "$(sha256sum "$H/sp11-libcamera-e004lx-lease.h" | awk '{print $1}')" == 1816890fee0cc4a3887ad74927825fe1b4efb44113990ef49fb626ff8b571f36 ]]
[[ "$(sha256sum /tmp/sp11-e004lx-neutral-probe | awk '{print $1}')" == 59d70f48e79ee79a4a14dd3502c6aa0f10ac80670b5725ef74ab4e3a41864c0d ]]
[[ "$(sha256sum "$H/validate-cam-output.py" | awk '{print $1}')" == 298e787551b2d7e9adcc726d6e7e7c146a8bf0ef754d4352b96609c3f5a4390b ]]
[[ "$(sha256sum /tmp/sp11-e004lx-neutral-probe | awk '{print $1}')" == 59d70f48e79ee79a4a14dd3502c6aa0f10ac80670b5725ef74ab4e3a41864c0d ]]
[[ "$(sha256sum "$H/validate-cam-output.py" | awk '{print $1}')" == 298e787551b2d7e9adcc726d6e7e7c146a8bf0ef754d4352b96609c3f5a4390b ]]
bash -n "$H/run-once.sh" "$H/arm-once.sh" "$H/retire-after-golden.sh"
python3 -m py_compile "$H/validate-cam-output.py"
tail -n +3 "$H/99zzzzzz_sp11_camera_e004lx" | grub-script-check
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
sudo -n cp -a "/var/lib/sp11-e004lx-build/build" "$D/bundle/build"
sudo -n cp -a "/var/lib/sp11-e004lx-build/source" "$D/bundle/source"
sudo -n chown -R root:root "$D/bundle"
sudo -n chmod -R go-rwx "$D/bundle"
sudo -n test -x "$D/bundle/build/src/apps/cam/cam"
sudo -n install -m 0700 /tmp/sp11-e004lx-neutral-probe "$D/bundle/neutral-probe"
sudo -n install -m 0600 "$H/validate-cam-output.py" "$D/bundle/validate-cam-output.py"
sudo -n test -f "$D/bundle/build/src/ipa/simple/ipa_soft_simple.so.sign"
sudo -n install -m 0600 "$H/run-once.sh" "$D/run-once.sh"
sudo -n install -m 0600 "$H/sp11-camera-e004lx-one-shot.service" "$D/service.txt"
sudo -n install -m 0600 "$H/99zzzzzz_sp11_camera_e004lx" "$D/entry.txt"
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
sudo -n sh -c 'cd /var/lib/sp11-camera-e004lx && sha256sum modules/*.ko candidate/*.ko bundle/neutral-probe bundle/validate-cam-output.py bundle/build/src/apps/cam/cam bundle/build/src/libcamera/libcamera.so.0.7.0 bundle/build/src/libcamera/base/libcamera-base.so.0.7.0 bundle/build/src/ipa/simple/ipa_soft_simple.so bundle/build/src/ipa/simple/ipa_soft_simple.so.sign bundle/source/src/libcamera/pipeline/simple/simple.cpp bundle/source/src/libcamera/pipeline/simple/sp11-libcamera-e004lx-lease.h bundle/source/src/ipa/simple/soft_simple.cpp bundle/source/src/ipa/simple/sp11-imx681-fixed-frame-agc.h run-once.sh service.txt entry.txt > SESSION-ASSETS.sha256'
sudo -n sh -c 'cd /var/lib/sp11-camera-e004lx && sha256sum -c SESSION-ASSETS.sha256 >/dev/null'
sudo -n install -d -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004lx-xrgb8888"
sudo -n install -m 0644 "$SRC/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
[[ "$(sudo -n sha256sum "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" | awk '{print $1}')" == bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a ]]
[[ "$(sudo -n sha256sum "$BOOT/initrd.img-7.1.5-sp11-camera-e004lx-xrgb8888" | awk '{print $1}')" == ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d ]]
sudo -n install -m 0755 "$H/99zzzzzz_sp11_camera_e004lx" "$ENTRY"
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-camera-e004lx-one-shot.service" "$SERVICE"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-camera-e004lx-one-shot.service
sudo -n update-grub >/dev/null
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
echo E004LX_INSTALLED_UNARMED=PASS_GOLDEN_SAVED_UNCHANGED
