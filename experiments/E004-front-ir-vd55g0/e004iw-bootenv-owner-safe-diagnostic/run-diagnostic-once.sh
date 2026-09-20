#!/usr/bin/env bash
# E004iw: read-only, single-use candidate boot GRUB environment diagnostic.
# NO camera/module/IR activation; read-only /boot/grub/grubenv observation.
set -Eeuo pipefail
umask 077
D=/var/lib/sp11-camera-e004iw
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
OUT=$D/out
mkdir -p "$OUT"
[[ "$EUID" == 0 ]]
[[ "$(uname -r)" == "7.1.5-sp11-render-parity-v4+" ]]
grep -Fqx 'sp11_camera_e004iw_bootenv_diagnostic=1' <(tr ' ' '\n' </proc/cmdline)
grep -Fqx 'sp11_entry=7.1.5-sp11-camera-e004iw-bootenv-diagnostic' <(tr ' ' '\n' </proc/cmdline)
[[ -f "$D/EXPECTED-HEAD" ]]
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" ]]
record_result() {
  local rc=$?
  trap - EXIT
  if [[ "$rc" == 0 ]]; then
    echo 'PASS_READ_ONLY_GRUBENV_AFTER_WRITERS' > "$D/ATTEMPT-RESULT.txt"
  else
    printf 'FAIL_DIAGNOSTIC_RC=%s NO_CAMERA_ACCESS NO_SAME_BOOT_RETRY\n' "$rc" > "$D/ATTEMPT-RESULT.txt"
  fi
  printf 'boot_id=%s\n' "$(cat /proc/sys/kernel/random/boot_id)" >> "$D/ATTEMPT-RESULT.txt"
  sync
  exit "$rc"
}
trap record_result EXIT
[[ ! -e "$D/ATTEMPT-CONSUMED" ]]
( set -C; printf 'boot_id=%s\n' "$(cat /proc/sys/kernel/random/boot_id)" > "$D/ATTEMPT-CONSUMED" )
if ls /dev/video* /dev/media* >/dev/null 2>&1; then
  echo 'E004IW_CAMERA_NODES_UNEXPECTED' >&2
  exit 1
fi
for mod in qcom_camss imx681 ov13858 sp11_vd55g0; do
  [[ ! -d "/sys/module/$mod" ]] || { echo "E004IW_MODULE_UNEXPECTED=$mod" >&2; exit 1; }
done
# Immutable, private candidate-boot snapshot, even if the parsed environment
# is invalid. Keep bytes PRIVATE, never commit them to the repository.
cp -- /boot/grub/grubenv "$OUT/grubenv-observed.bin"
chmod 0600 "$OUT/grubenv-observed.bin"
sha256sum "$OUT/grubenv-observed.bin" > "$OUT/grubenv-observed.sha256"
stat -c 'bytes=%s mode=%a' "$OUT/grubenv-observed.bin" > "$OUT/grubenv-observed-size.txt"
grub-editenv /boot/grub/grubenv list > "$OUT/grubenv-list.txt" 2>"$OUT/grubenv-stderr.txt" || {
  echo E004IW_INVALID_GRUB_ENV_AFTER_WRITERS >&2
  exit 1
}
grep -qx 'saved_entry=sp11-audio-fullio-v19c' "$OUT/grubenv-list.txt"
grep -qx 'next_entry=' "$OUT/grubenv-list.txt"
test "$(grep -c '^saved_entry=' "$OUT/grubenv-list.txt")" -eq 1
test "$(grep -c '^next_entry=' "$OUT/grubenv-list.txt")" -eq 1
[[ "$(cat "$D/EXPECTED-HEAD")" == "$(runuser -u geoca -- git -C "$R" rev-parse HEAD)" ]]
[[ ! -d /sys/module/qcom_camss && ! -e /dev/media0 ]]
echo E004IW_READ_ONLY_CANDIDATE_GRUB_ENV_AFTER_WRITERS=PASS
