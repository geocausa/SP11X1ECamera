#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Install (not arm) the one-shot rear pattern calibration boot entry.
# Arm with:  grub-reboot sp11-camera-rear-pattern-61 && systemctl reboot
set -Eeuo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PROJECT=/home/geoca/Documents/SP11-PROJECT
B=$PROJECT/02-kernel/libcamera-rear-pattern61-19
S60=/var/lib/sp11-camera-native-rear-generation-20261007-60
BOOT60=/boot/sp11-7.1.5-camera-native-rear-generation-20261007-60
D=/var/lib/sp11-camera-rear-pattern-63
ID=sp11-camera-rear-pattern-63
MARK=sp11_camera_rear_pattern_63
test "$(id -u)" = 0
test ! -e "$D/CONSUMED" || { echo "already consumed; pick a new identity" >&2; exit 1; }
rm -rf "$D"; install -d -m 700 "$D" "$D/lib" "$D/lib/ipa" "$D/lib/proxy" "$D/modules"
install -m 600 $S60/modules/*.ko "$D/modules/"; install -m 600 $PROJECT/02-kernel/native-rgb-rear-tone-63/camss/qcom-camss.ko "$D/modules/qcom-camss.ko"
install -m 600 $S60/route-contract.py $S60/discover-unified.py "$D/"
install -m 600 $S60/run-once.py "$D/helpers60.py"
install -m 700 "$HERE/run-pattern63.py" "$D/run-pattern63.py"
install -m 700 "$B/capture-pattern" "$D/capture-pattern"
install -m 600 "$B/src/libcamera/libcamera.so.0.7.0" "$D/lib/libcamera.so.0.7"
install -m 600 "$B/src/libcamera/base/libcamera-base.so.0.7.0" "$D/lib/libcamera-base.so.0.7"
install -m 600 "$B/src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so" "$B/src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so.sign" "$D/lib/ipa/"
install -m 700 "$B/src/libcamera/proxy/worker/camss_x1e_rear_ipa_proxy" "$D/lib/proxy/"
cat > "$D/return-golden.sh" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
if grep -qw '$MARK=1' /proc/cmdline; then
  grub-reboot sp11-audio-fullio-v19c
  if test "\${PATTERN_WATCHDOG:-0}" = 1; then
    echo WATCHDOG > $D/WATCHDOG-FIRED; dmesg > $D/PRIVATE-WATCHDOG-DMESG.txt; sync
    systemctl reboot --force --force
  else
    printf 'service_result=%s exit_status=%s\n' "\${SERVICE_RESULT:-?}" "\${EXIT_STATUS:-?}" > $D/SERVICE-RESULT.txt; sync
    systemctl reboot --no-block
  fi
fi
EOF
chmod 700 "$D/return-golden.sh"
cat > /etc/systemd/system/$ID.service <<EOF
[Unit]
Description=SP11 rear pattern calibration capture, one candidate use
ConditionKernelCommandLine=$MARK=1
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 $D/run-pattern63.py
ExecStopPost=$D/return-golden.sh
TimeoutStartSec=600
TimeoutStopSec=15
KillMode=control-group
[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/$ID-watchdog.service <<EOF
[Unit]
Description=SP11 rear pattern independent Golden-return watchdog
ConditionKernelCommandLine=$MARK=1
[Service]
Type=oneshot
Environment=PATTERN_WATCHDOG=1
ExecStart=$D/return-golden.sh
EOF
cat > /etc/systemd/system/$ID-watchdog.timer <<EOF
[Unit]
Description=SP11 rear pattern 720-second return deadline
ConditionKernelCommandLine=$MARK=1
[Timer]
OnBootSec=720
Unit=$ID-watchdog.service
AccuracySec=1
[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable $ID.service $ID-watchdog.timer
SRC=/etc/grub.d/99zzzzzz_sp11_camera_native_rear_generation_20261007_60
DST=/etc/grub.d/99zzzzzz_sp11_camera_rear_pattern_63
sed -e "s/--id 'sp11-camera-native-rear-generation-20261007-60'/--id '$ID'/" \
    -e "s/menuentry 'SP11 rear generation proof - one use'/menuentry 'SP11 rear tone63 verification - one use'/" \
    -e "s/sp11_camera_native_rear_generation_20261007_60=1/$MARK=1/" \
    -e "s/sp11_entry=7.1.5-sp11-camera-native-rear-generation-20261007-60/sp11_entry=7.1.5-$ID/" "$SRC" > "$DST"
chmod 755 "$DST"
grep -q "$MARK=1" "$DST"; grep -q "$BOOT60/vmlinuz" "$DST"
update-grub >/dev/null 2>&1
grep -q -- "--id '$ID'" /boot/grub/grub.cfg
grub-editenv list
echo INSTALLED_NOT_ARMED
