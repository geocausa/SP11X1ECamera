#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E=$R/experiments/E004-front-ir-vd55g0/e004h-safe42-config-authority
D=$R/experiments/E004-front-ir-vd55g0/e004i-bounded-safe42-runtime
S=$R/src/front-ir-vd55g0/sp11-vd55g0-config42probe
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
BOOT=/boot/sp11-7.1.5-camera-e004i-config42
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004i_config42
ID=sp11-camera-e004i-config42-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
HEAD=$(git -C "$R" rev-parse HEAD); ORIGIN=$(git -C "$R" rev-parse '@{u}')
[ "$HEAD" = "$ORIGIN" ] || fail origin_mismatch
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process --expect-head "$HEAD" --expect-origin "$ORIGIN" || fail overlap_guard
[ -z "$(git -C "$R" status --porcelain -- experiments/E004-front-ir-vd55g0 src/front-ir-vd55g0)" ] || fail e004_tree_dirty
python3 "$E/verify_e004h.py" >/tmp/e004i-e004h-verify.txt || fail e004h_authority
rm -rf "$D/build"; mkdir -p "$D/build"
cp "$S/sp11-vd55g0-config42probe.ko" "$D/build/sp11-vd55g0-config42probe.ko"
[ "$(sha256sum "$D/build/sp11-vd55g0-config42probe.ko"|awk '{print $1}')" = '75eccb1ac7a8a5f247ec03a9f56339527d2dcd7cfab77450b3ba1f8efe563c5c' ] || fail module_hash
make -C "$K" M="$S" clean >/dev/null
rm -f "$S/surface-windows.generated.h"
[ "$(sha256sum "$E/x1e80100-microsoft-denali-sp11-e004h-config42.dtb"|awk '{print $1}')" = 'e29c787acf9e2f1330a4e73fd8014aba118a2f0a59be51c86859a9ab7fed4ef2' ] || fail dtb_hash
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail golden_kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail golden_initrd
sudo -n test ! -e "$BOOT" || fail candidate_boot_exists
sudo -n test ! -e "$ENTRY" || fail candidate_entry_exists
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail candidate_in_grub
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] && [ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] || fail prior_attempt
[ ! -d /sys/module/sp11_vd55g0_config42probe ] || fail config42_module_loaded
[ ! -e /dev/media0 ] || fail media_node_present
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
{
 echo 'schema=sp11-camera-e004i-prearm-v1'; echo 'status=PASS_READY_TO_INSTALL'; echo "time=$(date -Ins)"
 echo "head=$HEAD"; echo 'dtb_sha256=e29c787acf9e2f1330a4e73fd8014aba118a2f0a59be51c86859a9ab7fed4ef2'
 echo 'module_sha256=75eccb1ac7a8a5f247ec03a9f56339527d2dcd7cfab77450b3ba1f8efe563c5c'
 echo 'safe42_sha256=159647774f45331210044d0680e50bf16e8aaeeb8c3e98449d2cef7adeffacb2'
 echo 'attempt_limit=1'; echo 'linux_safe42_runtime_performed=NO'
} > "$D/PREARM.txt"
echo 'E004I_PREARM=PASS RUNTIME=NO'
