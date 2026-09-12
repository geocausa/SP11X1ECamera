#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E004-front-ir-vd55g0/e004b-linux-probe-authority
D=$R/experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe
S=$R/src/front-ir-vd55g0/sp11-vd55g0-idprobe
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
BOOT=/boot/sp11-7.1.5-camera-e004c-ir-idprobe
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004c_ir_idprobe
ID=sp11-camera-e004c-ir-idprobe-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
HEAD=$(git -C "$R" rev-parse HEAD)
ORIGIN=$(git -C "$R" rev-parse '@{u}')
[ "$HEAD" = "$ORIGIN" ] || fail origin_mismatch
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process --expect-head "$HEAD" --expect-origin "$ORIGIN" || fail overlap_guard
[ -z "$(git -C "$R" status --porcelain -- experiments/E004-front-ir-vd55g0 src/front-ir-vd55g0)" ] || fail e004_tree_dirty
python3 "$B/verify-e004b-dtb.py" >/tmp/e004c-dt-verify.txt || fail dt_authority
python3 "$B/verify-probe.py" >/tmp/e004c-probe-verify.txt || fail probe_authority
[ "$(sha256sum "$B/x1e80100-microsoft-denali-sp11-e004b-ir-probe.dtb"|awk '{print $1}')" = '2b9ff2265606aa95006e3c952597c496367106e00aa1e2d1ec1e75b8f9e485e6' ] || fail dtb_hash
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail golden_kernel
[ "$(sudo -n sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail golden_initrd
rm -rf "$D/build"
mkdir -p "$D/build"
cp "$S/sp11-vd55g0-idprobe.ko" "$D/build/sp11-vd55g0-idprobe.ko"
[ "$(sha256sum "$D/build/sp11-vd55g0-idprobe.ko"|awk '{print $1}')" = 'd749fb549ff7c03e0ebcd1690b78b795d985d6d37083ab938a2a2663c397daed' ] || fail module_hash
make -C "$K" M="$S" clean >/dev/null
sudo -n test ! -e "$BOOT" || fail candidate_boot_exists
sudo -n test ! -e "$ENTRY" || fail candidate_entry_exists
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail candidate_in_grub
[ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] && [ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] || fail prior_attempt
[ ! -d /sys/module/sp11_vd55g0_idprobe ] || fail probe_module_loaded
[ ! -e /dev/media0 ] || fail media_node_present
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
python3 - <<'PY' || fail free_space
import os
v=os.statvfs('/home/geoca/Documents/SP11-PROJECT')
assert v.f_bavail*v.f_frsize>=4*1024**3
PY
{
 echo 'schema=sp11-camera-e004c-prearm-v1'
 echo 'status=PASS_READY_TO_INSTALL'
 echo "time=$(date -Ins)"
 echo "head=$HEAD"
 echo 'e004b_dtb_sha256=2b9ff2265606aa95006e3c952597c496367106e00aa1e2d1ec1e75b8f9e485e6'
 echo 'idprobe_module_sha256=d749fb549ff7c03e0ebcd1690b78b795d985d6d37083ab938a2a2663c397daed'
 echo 'linux_probe_performed=NO'
} > "$D/PREARM.txt"
echo 'E004C_PREARM=PASS RUNTIME=NO'
