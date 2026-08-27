#!/bin/sh
set -eu
BASE="$1"; NATIVE_DTBO="$2"; OUT="$3"; WORK="${4:-${OUT}.work}"
rm -f "$WORK"; fdtoverlay -i "$BASE" -o "$WORK" "$NATIVE_DTBO"
SENSOR=/soc@0/cci@ac15000/i2c-bus@1/rear-probe@10
RSC=/soc@0/rsc@17500000
L6=$RSC/regulators-8/ldo6
L5=$RSC/regulators-8/ldo5
L1=$RSC/regulators-8/ldo1
ph() { fdtget -t x "$WORK" "$1" phandle; }
P6=$(ph "$L6"); P5=$(ph "$L5"); P1=$(ph "$L1")
fdtput -t x "$WORK" "$SENSOR" dovdd-supply "0x$P6"
fdtput -t x "$WORK" "$SENSOR" dvdd-supply "0x$P1"
fdtput -t x "$WORK" "$SENSOR" avdd-supply "0x$P5"
fdtput -r "$WORK" "$RSC/camera-rpmh-regulators"
for p in camera_rpmh_r3d vreg_l16b_camera_r3d vreg_l5m_camera_r3d vreg_l1m_camera_r3d vreg_l6m_camera_r3d; do
  fdtput -d "$WORK" /__symbols__ "$p" 2>/dev/null || true
done
mv "$WORK" "$OUT"
# Assertions
[ "$(fdtget -t x "$OUT" "$SENSOR" dovdd-supply)" = "$P6" ]
[ "$(fdtget -t x "$OUT" "$SENSOR" dvdd-supply)" = "$P1" ]
[ "$(fdtget -t x "$OUT" "$SENSOR" avdd-supply)" = "$P5" ]
! fdtget -p "$OUT" "$RSC/camera-rpmh-regulators" >/dev/null 2>&1
[ "$(fdtget -t s "$OUT" "$RSC/regulators-8" compatible)" = "qcom,pm8010-rpmh-regulators" ]
