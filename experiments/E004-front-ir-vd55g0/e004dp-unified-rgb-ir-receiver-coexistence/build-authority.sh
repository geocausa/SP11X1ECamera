#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dp-unified-rgb-ir-receiver-coexistence
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
OLD=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src
NEW=/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src
PATCH=$R/experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module/0001-sp11-e004j-csiphy0-dphy-windows-parity.patch
SENSOR=$R/src/front-ir-vd55g0/sp11-vd55g0-native
HARNESS=$R/experiments/E004-front-ir-vd55g0/e004t-csiphy0-readback-authority
IG=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ig-unified-rear-to-front-r16-r27
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(sha256sum "$PATCH"|awk '{print $1}')" = 1fc0f918a2f00e79918cf8bf7164f49cb8df395b8b05c949dc424a7b3824a869 ] || fail patch
[ "$(sha256sum "$SENSOR/sp11-vd55g0.c"|awk '{print $1}')" = 20bca88eb4333f386e76e17d800268511dcf30fbc0b642d39e425e00703d6745 ] || fail sensor_source
[ "$(sha256sum "$IG/build/imx681.ko"|awk '{print $1}')" = ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ] || fail imx681_authority
[ "$(sha256sum "$IG/build/ov13858-production.ko"|awk '{print $1}')" = 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309 ] || fail ov13858_authority
# The current generated wrapper must be restored after this function exactly.
grep -Fq "$NEW/Makefile" "$K/Makefile" || fail current_wrapper
[ "$(readlink "$K/source")" = "$NEW" ] || fail current_source_link
BK=$(mktemp -d /tmp/e004dp-kbuild-backup.XXXXXX)
cp -a "$K/Makefile" "$BK/Makefile"; readlink "$K/source" > "$BK/source.target"
restore(){
  make -C "$K" M="$SENSOR" clean >/dev/null 2>&1 || true
  make -C "$K" M="$HARNESS" clean >/dev/null 2>&1 || true
  rm -f "$SENSOR/surface-windows.generated.h"
  cp -a "$BK/Makefile" "$K/Makefile"
  rm -f "$K/source"; ln -s "$(cat "$BK/source.target")" "$K/source"
  rm -rf "$BK"
}
trap restore EXIT INT TERM
sed "s#${NEW//\#/\\#}#${OLD//\#/\\#}#g" "$BK/Makefile" > "$K/Makefile"
rm -f "$K/source"; ln -s "$OLD" "$K/source"
ROOTB=/tmp/e004dp-accepted-base; ROOTP=/tmp/e004dp-accepted-ir
rm -rf "$ROOTB" "$ROOTP"; mkdir -p "$ROOTB" "$ROOTP"
cp -a "$R/src/front-imx681/kernel/camss" "$ROOTB/camss"
cp -a "$R/src/front-imx681/kernel/camss" "$ROOTP/camss"
patch -p6 -d "$ROOTP/camss" < "$PATCH" >/dev/null
for spec in "base:$ROOTB" "ir:$ROOTP"; do
  kind=${spec%%:*}; root=${spec#*:}; w=$root/camss
  MAP="-ffile-prefix-map=$root=/usr/src/sp11-front-imx681 -fdebug-prefix-map=$root=/usr/src/sp11-front-imx681 -fmacro-prefix-map=$root=/usr/src/sp11-front-imx681"
  make -C "$K" M="$w" clean >/dev/null
  make -C "$K" M="$w" W=1 KCFLAGS="$MAP" KCPPFLAGS="$MAP" -j4 >"/tmp/e004dp-camss-$kind.log"
done
BASESHA=$(sha256sum "$ROOTB/camss/qcom-camss.ko"|awk '{print $1}')
IRSHA=$(sha256sum "$ROOTP/camss/qcom-camss.ko"|awk '{print $1}')
[ "$BASESHA" = 7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95 ] || fail baseline_not_accepted
[ "$IRSHA" = 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ] || fail ir_camss_hash
modinfo "$ROOTP/camss/qcom-camss.ko" | grep -Fq 'e004j_ir_dphy_windows_parity' || fail ir_param
# Reproduce exact accepted bind-only sensor module in its historical source pathname.
make -C "$K" M="$SENSOR" clean >/dev/null
python3 "$SENSOR/generate_windows_header.py" >/tmp/e004dp-sensor-gen.log
make -C "$K" M="$SENSOR" modules V=0 >/tmp/e004dp-sensor-build.log
SENSORSHA=$(sha256sum "$SENSOR/sp11-vd55g0.ko"|awk '{print $1}')
[ "$SENSORSHA" = 4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72 ] || fail sensor_module_hash
# Reproduce exact accepted receiver-only harness.
make -C "$K" M="$HARNESS" clean >/dev/null
make -C "$K" M="$HARNESS" modules V=0 >/tmp/e004dp-harness-build.log
HARNESSHA=$(sha256sum "$HARNESS/e004t_csiphy_readback_test.ko"|awk '{print $1}')
[ "$HARNESSHA" = 6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e ] || fail harness_hash
rm -rf "$D/build"; mkdir -p "$D/build"
cp "$ROOTP/camss/qcom-camss.ko" "$D/build/qcom-camss-ir-gated.ko"
cp "$SENSOR/sp11-vd55g0.ko" "$D/build/sp11-vd55g0.ko"
cp "$HARNESS/e004t_csiphy_readback_test.ko" "$D/build/e004t_csiphy_readback_test.ko"
cp "$IG/build/imx681.ko" "$D/build/imx681.ko"
cp "$IG/build/ov13858-production.ko" "$D/build/ov13858-production.ko"
cat > "$D/build/AUTHORITY.sha256" <<HASHES
862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7  qcom-camss-ir-gated.ko
4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72  sp11-vd55g0.ko
6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e  e004t_csiphy_readback_test.ko
ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6  imx681.ko
13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309  ov13858-production.ko
HASHES
(cd "$D/build" && sha256sum -c AUTHORITY.sha256 >/dev/null) || fail packaged_hashes
# Restore now, then prove exact restoration before success.
restore; trap - EXIT INT TERM
grep -Fq "$NEW/Makefile" "$K/Makefile" || fail wrapper_restore
[ "$(readlink "$K/source")" = "$NEW" ] || fail source_link_restore
[ -z "$(git -C "$R" status --porcelain -- src/front-ir-vd55g0/sp11-vd55g0-native experiments/E004-front-ir-vd55g0/e004t-csiphy0-readback-authority)" ] || fail build_tree_cleanup
printf 'E004DP_BUILD=PASS BASELINE=7afe6ed0 IR_CAMSS=862732b7 SENSOR=4839415e HARNESS=6475d453 RGB_MODULES=ACCEPTED\n'
