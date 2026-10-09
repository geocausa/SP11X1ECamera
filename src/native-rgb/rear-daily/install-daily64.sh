#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Install the daily rear-camera boot entry (NOT default; Golden stays default).
# Entry = Golden kernel/initrd + camera device tree + camera stack loaded at boot.
# Try once with: grub-reboot sp11-camera-daily && systemctl reboot
set -Eeuo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
P=/home/geoca/Documents/SP11-PROJECT
S60=/var/lib/sp11-camera-native-rear-generation-20261007-60
B=$P/02-kernel/libcamera-rear-daily-20
K=$P/02-kernel/native-rgb-rear-daily-64
D=/var/lib/sp11-camera-daily
BOOT=/boot/sp11-7.1.5-camera-daily
GOLD=/boot/sp11-7.1.5-audio-fullio-v19c
ID=sp11-camera-daily
MARK=sp11_camera_daily
test "$(id -u)" = 0
rm -rf "$D"; install -d -m 755 "$D" "$D/lib" "$D/lib/ipa" "$D/lib/proxy" "$D/modules"
install -m 644 $S60/modules/ov13858.ko $S60/modules/imx681.ko $S60/modules/sp11-vd55g0.ko "$D/modules/"
install -m 644 "$K/camss/qcom-camss.ko" "$D/modules/qcom-camss.ko"
install -m 644 $S60/route-contract.py $S60/discover-unified.py "$D/"
install -m 644 $S60/run-once.py "$D/helpers60.py"
install -m 755 "$HERE/setup-camera.py" "$D/setup-camera.py"
install -m 755 "$B/capture-pattern" "$D/capture-pattern"
install -m 644 "$B/src/libcamera/libcamera.so.0.7.0" "$D/lib/libcamera.so.0.7"
install -m 644 "$B/src/libcamera/base/libcamera-base.so.0.7.0" "$D/lib/libcamera-base.so.0.7"
install -m 644 "$B/src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so" "$B/src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so.sign" "$D/lib/ipa/"
install -m 755 "$B/src/libcamera/proxy/worker/camss_x1e_rear_ipa_proxy" "$D/lib/proxy/"
install -d -m 755 "$BOOT"
install -m 644 /boot/sp11-7.1.5-camera-native-rear-generation-20261007-60/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb "$BOOT/"
cat > /etc/systemd/system/$ID.service <<EOF
[Unit]
Description=SP11 rear camera (daily boot entry): load and route camera stack
ConditionKernelCommandLine=$MARK=1
After=systemd-modules-load.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/python3 $D/setup-camera.py
TimeoutStartSec=90
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable $ID.service
SRC=/etc/grub.d/99zzzzzz_sp11_camera_native_rear_generation_20261007_60
DST=/etc/grub.d/99zzzzzz_sp11_camera_daily
sed -e "s/--id 'sp11-camera-native-rear-generation-20261007-60'/--id '$ID'/" \
    -e "s/menuentry 'SP11 rear generation proof - one use'/menuentry 'SP11 Daily + Rear Camera'/" \
    -e "s/sp11_camera_native_rear_generation_20261007_60=1/$MARK=1/" \
    -e "s/sp11_entry=7.1.5-sp11-camera-native-rear-generation-20261007-60/sp11_entry=7.1.5-$ID/" \
    -e "s|devicetree /boot/sp11-7.1.5-camera-native-rear-generation-20261007-60/|devicetree $BOOT/|" \
    -e "s|linux /boot/sp11-7.1.5-camera-native-rear-generation-20261007-60/|linux $GOLD/|" \
    -e "s|initrd /boot/sp11-7.1.5-camera-native-rear-generation-20261007-60/|initrd $GOLD/|" "$SRC" > "$DST"
chmod 755 "$DST"
grep -q "$MARK=1" "$DST"; grep -q "devicetree $BOOT/" "$DST"; grep -q "linux $GOLD/vmlinuz" "$DST"
update-grub >/dev/null 2>&1
grep -q -- "--id '$ID'" /boot/grub/grub.cfg
grub-editenv list
echo DAILY_INSTALLED_NOT_DEFAULT
