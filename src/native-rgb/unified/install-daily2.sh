#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Install the SP11 daily camera boot entry (both cameras). Golden stays the GRUB
# default. Entry = Golden kernel/initrd/command line + camera device tree (a pure
# superset of the Golden tree) + unified camera stack + two webcam bridges.
# Try once:  grub-reboot sp11-camera-daily2 && systemctl reboot
set -Eeuo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
P=/home/geoca/Documents/SP11-PROJECT
K=$P/02-kernel/native-rgb-unified-48
B=$P/02-kernel/libcamera-unified-21
OLD=/var/lib/sp11-camera-daily
PRIV=$P/02-kernel/front-open-01
D=/var/lib/sp11-camera-daily2
BOOT=/boot/sp11-7.1.5-camera-daily2
GOLD=/boot/sp11-7.1.5-audio-fullio-v19c
ID=sp11-camera-daily2
MARK=sp11_camera_daily2
test "$(id -u)" = 0
for s in sp11-webcam-front sp11-webcam-rear sp11-camera-daily2; do systemctl stop $s.service 2>/dev/null || true; done
rm -rf "$D"
install -d -m 755 "$D" "$D/lib" "$D/lib/ipa" "$D/lib/proxy" "$D/modules" "$D/tuning"
install -d -m 700 "$D/firmware" "$D/firmware/qcom" "$D/firmware/qcom/sp11"
install -m 644 "$K/camss/qcom-camss.ko" "$K/imx681/imx681.ko" "$K/ov13858/ov13858.ko" "$D/modules/"
install -m 644 "$OLD/modules/sp11-vd55g0.ko" "$OLD/modules/v4l2loopback.ko" "$D/modules/"
# Private startup profile (stays on this machine) and our own measured LSC/ABF tables.
PROFILE=$P/02-kernel/native-front-profile-20261007-01/imx681-2560x1440-nv12-v1.bin
test "$(sha256sum "$PROFILE" | cut -d' ' -f1)" = c59a54b760a8662af650fa8961aab2224c7c0d2a0cdcdea3c9581370ac5ddd03
install -m 600 "$PROFILE" "$D/firmware/qcom/sp11/"
install -m 600 "$P/02-kernel/front-lsc-v1/imx681-front-lsc-v1.bin" "$PRIV/imx681-front-abf-v1.bin" "$D/firmware/qcom/sp11/"
install -m 644 "$HERE/../front-ae/tuning/imx681-front-v15.yaml" "$D/tuning/imx681-front.yaml"
python3 -c "import json;j=json.load(open('$P/02-kernel/front-ae-93/run-93.json'));print(' '.join(j['camss_params']+['native_rear_generation_trial=1']))" > "$D/camss-params.txt"
install -m 755 "$HERE/setup-daily2.py" "$D/setup.py"
install -m 755 "$B/sp11-webcam" "$D/sp11-webcam"
install -m 644 "$B/src/libcamera/libcamera.so.0.7.0" "$D/lib/libcamera.so.0.7"
install -m 644 "$B/src/libcamera/base/libcamera-base.so.0.7.0" "$D/lib/libcamera-base.so.0.7"
install -m 644 "$B/src/ipa/camss-x1e/ipa_camss_x1e.so" "$B/src/ipa/camss-x1e/ipa_camss_x1e.so.sign" \
  "$B/src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so" "$B/src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so.sign" "$D/lib/ipa/"
install -m 755 "$B/src/libcamera/proxy/worker/camss_x1e_ipa_proxy" "$B/src/libcamera/proxy/worker/camss_x1e_rear_ipa_proxy" "$D/lib/proxy/"
install -d -m 755 "$BOOT"
# camera device tree (superset of Golden) + rear lens actuator supply (make-daily-dtb.py)
CAMDTB=/boot/sp11-7.1.5-camera-daily/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb
test "$(md5sum < $CAMDTB | cut -d' ' -f1)" = 22ca17bf6c265d356bb841ede864a9c0
# Rear lens supply (make-daily-dtb.py v2: separate camera-only RPMh provider,
# loaded by setup.py). On by default; SP11_REAR_VAF=0 installs the plain camera tree.
if [ "${SP11_REAR_VAF:-1}" = 1 ]; then
  python3 "$HERE/make-daily-dtb.py" "$CAMDTB" "$BOOT/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
  T=$(mktemp -d); cp "$HERE/vaf/Kbuild" "$HERE/vaf/sp11_camera_rpmh_regulator.c" "$T/"
  make -s -C /lib/modules/$(uname -r)/build M="$T" W=1 modules
  install -m 644 "$T/sp11_camera_rpmh_regulator.ko" "$D/modules/"; rm -rf "$T"
else
  install -m 644 "$CAMDTB" "$BOOT/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
fi

cat > /etc/systemd/system/$ID.service <<EOF
[Unit]
Description=SP11 cameras (daily boot entry): load the camera stack and webcam devices
ConditionKernelCommandLine=$MARK=1
After=systemd-modules-load.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/python3 $D/setup.py
TimeoutStartSec=90
[Install]
WantedBy=multi-user.target
EOF
for cam in front:sp11-front-imx681:camss-x1e:/dev/video50 rear:sp11-rear-ov13858-qualification:camss-x1e-rear:/dev/video51; do
  IFS=: read -r name cid handler dev <<<"$cam"
  extra=""
  [ "$name" = front ] && extra="Environment=LIBCAMERA_CAMSS_X1E_TUNING_FILE=$D/tuning/imx681-front.yaml"
  # both bridges enumerate the same media device: let the front one go first
  [ "$name" = rear ] && extra="Environment=SP11_WEBCAM_LOOKUP_DELAY=4"
  # rendering measured against Windows (fit-look.py); identity when absent
  lookarg=""
  if [ -f "$HERE/looks/look-$name.look" ]; then
    install -m 644 "$HERE/looks/look-$name.look" "$D/look-$name.look"; lookarg="$D/look-$name.look"
  fi
  cat > /etc/systemd/system/sp11-webcam-$name.service <<EOF
[Unit]
Description=SP11 $name camera webcam bridge ($dev)
ConditionKernelCommandLine=$MARK=1
Requires=$ID.service
StartLimitIntervalSec=0
After=$ID.service
# applications (PipeWire) must find the loopback already configured as a webcam
Before=display-manager.service systemd-user-sessions.service
[Service]
Type=notify
NotifyAccess=main
# re-announce the device so a running PipeWire picks up a restarted bridge
ExecStartPost=/bin/sh -c 'udevadm trigger --action=remove --settle $dev; udevadm trigger --action=add --settle $dev; true'
Environment=LD_LIBRARY_PATH=$D/lib
Environment=LIBCAMERA_IPA_MODULE_PATH=$D/lib/ipa
Environment=LIBCAMERA_IPA_PROXY_PATH=$D/lib/proxy
Environment=LIBCAMERA_PIPELINES_MATCH_LIST=$handler
Environment=LIBCAMERA_LOG_LEVELS=*:WARN
$extra
ExecStart=$D/sp11-webcam $cid $dev $lookarg
Restart=on-failure
RestartSec=2
Nice=-5
[Install]
WantedBy=multi-user.target
EOF
done
systemctl daemon-reload
systemctl enable $ID.service sp11-webcam-front.service sp11-webcam-rear.service

# GRUB entry derived from the Golden entry: same kernel, initrd and command line.
SRC=/etc/grub.d/76_sp11_audio_fullio_v19c
DST=/etc/grub.d/42_sp11_camera_daily2
{
  printf '#!/bin/sh\nexec tail -n +3 $0\n'
  tail -n +3 "$SRC" | sed \
    -e "s|^menuentry '[^']*' --id 'sp11-audio-fullio-v19c'|menuentry 'SP11 Golden + Cameras' --id '$ID'|" \
    -e "s|devicetree $GOLD/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb|devicetree $BOOT/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb|" \
    -e "/^ linux /s|\$| $MARK=1 sp11_entry=7.1.5-$ID modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0 firmware_class.path=$D/firmware|"
} > "$DST"
chmod 755 "$DST"
grep -q -- "--id '$ID'" "$DST"; grep -q "devicetree $BOOT/" "$DST"; grep -q "$MARK=1" "$DST"
update-grub >/dev/null 2>&1
grep -q -- "--id '$ID'" /boot/grub/grub.cfg
grub-editenv list
# already in the camera boot: bring the (re)installed stack back up
if grep -qw "$MARK=1" /proc/cmdline; then systemctl start $ID.service sp11-webcam-front.service sp11-webcam-rear.service; fi
echo DAILY2_INSTALLED_NOT_DEFAULT
