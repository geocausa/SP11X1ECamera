#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004m-native-bind-runtime
L=$R/experiments/E004-front-ir-vd55g0/e004l-native-bind-only-authority
K=$R/experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module
N=$R/src/front-ir-vd55g0/sp11-vd55g0-native
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
BOOT=/boot/sp11-7.1.5-camera-e004m-native-bind
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004m_native_bind
ID=sp11-camera-e004m-native-bind-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }

HEAD=$(git -C "$R" rev-parse HEAD); ORIGIN=$(git -C "$R" rev-parse '@{u}')
[ "$HEAD" = "$ORIGIN" ] || fail origin_mismatch
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process --expect-head "$HEAD" --expect-origin "$ORIGIN" || fail overlap_guard
[ -z "$(git -C "$R" status --porcelain -- experiments/E004-front-ir-vd55g0 src/front-ir-vd55g0)" ] || fail e004_tree_dirty
python3 "$L/verify_e004l.py" >/tmp/e004m-e004l.txt || fail e004l_authority
python3 "$K/verify_e004k.py" >/tmp/e004m-e004k.txt || fail e004k_authority

rm -rf "$D/build"; mkdir -p "$D/build"
python3 "$N/generate_windows_header.py" >/dev/null
make -C "$B" M="$N" clean >/dev/null
make -C "$B" M="$N" modules V=0 >/tmp/e004m-native-build.txt
cp "$N/sp11-vd55g0.ko" "$D/build/sp11-vd55g0.ko"
[ "$(sha256sum "$D/build/sp11-vd55g0.ko"|awk '{print $1}')" = '4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72' ] || fail sensor_hash
make -C "$B" M="$N" clean >/dev/null
rm -f "$N/surface-windows.generated.h"

make -C "$B" M="$D" clean >/dev/null
make -C "$B" M="$D" modules V=0 >/tmp/e004m-harness-build.txt
cp "$D/e004m_stream_block_test.ko" "$D/build/e004m_stream_block_test.ko"
[ "$(sha256sum "$D/build/e004m_stream_block_test.ko"|awk '{print $1}')" = '93f947e9737c1472cf11df15b62223d07cae8adb330ebb359d27952172e5a926' ] || fail harness_hash
make -C "$B" M="$D" clean >/dev/null

[ "$(sha256sum "$K/qcom-camss.ko"|awk '{print $1}')" = 'bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba' ] || fail camss_hash
[ "$(sha256sum "$L/x1e80100-microsoft-denali-sp11-e004l-native-bind.dtb"|awk '{print $1}')" = 'dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b' ] || fail dtb_hash
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail golden_kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail golden_initrd

sudo -n test ! -e "$BOOT" || fail candidate_boot_exists
sudo -n test ! -e "$ENTRY" || fail candidate_entry_exists
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail candidate_in_grub
for x in RUNTIME-PREFLIGHT.txt RUNTIME-DMESG.txt MEDIA.txt CONTROLS.txt STREAM-BLOCK.txt ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json; do
 [ ! -e "$D/$x" ] || fail "prior_$x"
done
for m in qcom_camss sp11_vd55g0 e004m_stream_block_test; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ ! -e /dev/media0 ] || fail media_node_present
command -v media-ctl >/dev/null || fail media_ctl
command -v v4l2-ctl >/dev/null || fail v4l2_ctl
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
{
 echo 'schema=sp11-camera-e004m-prearm-v1'; echo 'status=PASS_READY_TO_INSTALL'; echo "time=$(date -Ins)"
 echo "head=$HEAD"
 echo 'dtb_sha256=dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b'
 echo 'sensor_module_sha256=4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72'
 echo 'camss_module_sha256=bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba'
 echo 'harness_sha256=93f947e9737c1472cf11df15b62223d07cae8adb330ebb359d27952172e5a926'
 echo 'stream_request=direct_sensor_callback_only'; echo 'capture_stream=NO'; echo 'illumination=NO'
} > "$D/PREARM.txt"
echo 'E004M_PREARM=PASS RUNTIME=NO'
