#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004r-ir-only-bind-runtime-r3
L=$R/experiments/E004-front-ir-vd55g0/e004l-native-bind-only-authority
O=$R/experiments/E004-front-ir-vd55g0/e004o-ir-only-graph-authority
K=$R/experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module
N=$R/src/front-ir-vd55g0/sp11-vd55g0-native
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
BOOT=/boot/sp11-7.1.5-camera-e004r-ir-only-bind-r3
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004r_ir_only_bind_r3
ID=sp11-camera-e004r-ir-only-bind-r3-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }

HEAD=$(git -C "$R" rev-parse HEAD); ORIGIN=$(git -C "$R" rev-parse '@{u}')
[ "$HEAD" = "$ORIGIN" ] || fail origin_mismatch
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process --expect-head "$HEAD" --expect-origin "$ORIGIN" || fail overlap_guard
[ -z "$(git -C "$R" status --porcelain -- experiments/E004-front-ir-vd55g0 src/front-ir-vd55g0)" ] || fail e004_tree_dirty
python3 "$L/verify_e004l.py" >/tmp/e004r-e004l.txt || fail e004l_authority
python3 "$O/verify_e004o.py" >/tmp/e004r-e004o.txt || fail e004o_graph_authority
python3 "$K/verify_e004k.py" >/tmp/e004r-e004k.txt || fail e004k_authority

python3 "$N/generate_windows_header.py" >/dev/null
make -C "$B" M="$N" clean >/dev/null
make -C "$B" M="$N" modules V=0 >/tmp/e004r-native-build.txt
cp "$N/sp11-vd55g0.ko" /tmp/e004r-sp11-vd55g0.ko
[ "$(sha256sum /tmp/e004r-sp11-vd55g0.ko|awk '{print $1}')" = '4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72' ] || fail sensor_hash
make -C "$B" M="$N" clean >/dev/null
rm -f "$N/surface-windows.generated.h"

make -C "$B" M="$D" clean >/dev/null
make -C "$B" M="$D" modules V=0 >/tmp/e004r-harness-build.txt
cp "$D/e004r_stream_block_test.ko" /tmp/e004r-stream-block-test.ko
[ "$(sha256sum /tmp/e004r-stream-block-test.ko|awk '{print $1}')" = '2cacc5e1336ac77b32c7e67e8c6f05cfdbaf6d54e9424cede1168f69c25f3303' ] || fail harness_hash
make -C "$B" M="$D" clean >/dev/null

rm -rf "$D/build"; mkdir -p "$D/build"
cp /tmp/e004r-sp11-vd55g0.ko "$D/build/sp11-vd55g0.ko"
cp /tmp/e004r-stream-block-test.ko "$D/build/e004r_stream_block_test.ko"
[ "$(sha256sum "$D/build/sp11-vd55g0.ko"|awk '{print $1}')" = '4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72' ] || fail packaged_sensor_hash
[ "$(sha256sum "$D/build/e004r_stream_block_test.ko"|awk '{print $1}')" = '2cacc5e1336ac77b32c7e67e8c6f05cfdbaf6d54e9424cede1168f69c25f3303' ] || fail packaged_harness_hash

[ "$(sha256sum "$K/qcom-camss.ko"|awk '{print $1}')" = 'bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba' ] || fail camss_hash
[ "$(sha256sum "$O/x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb"|awk '{print $1}')" = 'fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742' ] || fail dtb_hash
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail golden_kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail golden_initrd

sudo -n test ! -e "$BOOT" || fail candidate_boot_exists
sudo -n test ! -e "$ENTRY" || fail candidate_entry_exists
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail candidate_in_grub
for x in RUNTIME-PREFLIGHT.txt RUNTIME-DMESG.txt MEDIA.txt CONTROLS.txt STREAM-BLOCK.txt ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json; do
 [ ! -e "$D/$x" ] || fail "prior_$x"
done
for m in qcom_camss sp11_vd55g0 e004r_stream_block_test; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ ! -e /dev/media0 ] || fail media_node_present
command -v media-ctl >/dev/null || fail media_ctl
command -v v4l2-ctl >/dev/null || fail v4l2_ctl
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
{
 echo 'schema=sp11-camera-e004r-prearm-v1'; echo 'status=PASS_READY_TO_INSTALL'; echo "time=$(date -Ins)"
 echo "head=$HEAD"
 echo 'dtb_sha256=fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742'
 echo 'sensor_module_sha256=4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72'
 echo 'camss_module_sha256=bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba'
 echo 'harness_sha256=2cacc5e1336ac77b32c7e67e8c6f05cfdbaf6d54e9424cede1168f69c25f3303'
 echo 'stream_request=direct_sensor_callback_only'; echo 'capture_stream=NO'; echo 'illumination=NO'
} > "$D/PREARM.txt"
echo 'E004R_PREARM=PASS RUNTIME=NO'
