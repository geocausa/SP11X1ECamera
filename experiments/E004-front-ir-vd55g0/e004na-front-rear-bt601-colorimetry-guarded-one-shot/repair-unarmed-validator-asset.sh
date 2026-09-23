#!/usr/bin/env bash
# Pre-ARM source-locked E004na exact missing-validator staging repair ONLY.
# Discovered during independent pre-arm inspection: the newly added original
# run-once.sh referred to validate_bt601_live.py but the pre-arm installer
# inadvertently did not copy it into root stage. No E004na boot/camera trial
# has yet run. NEVER attempt this after arm/consume or on a non-Golden host.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004na-front-rear-bt601-colorimetry-guarded-one-shot
D=/var/lib/sp11-camera-e004na
BOOT=/boot/sp11-7.1.5-camera-e004na-rgb-session
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004na
SERVICE=/etc/systemd/system/sp11-camera-e004na-one-shot.service
SESSION=/etc/systemd/system/sp11-camera-e004na-session@.service
RUNNER=/usr/local/sbin/sp11-camera-e004na-run-once
OLD_HEAD=98ad08bb49a74f23d4ab849dccee4cdb0b9031d6
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$OLD_HEAD" ]]
[[ -d "$D" && ! -L "$D" && -d "$BOOT" && -f "$RUNNER" && -f "$SERVICE" && -f "$ENTRY" && -f "$SESSION" ]]
sudo -n test ! -e "$D/ATTEMPT-ARMED"
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n test ! -e "$D/UNARMED-REPAIR.txt"
sudo -n test ! -e "$D/validate_bt601_live.py"
[[ "$(sudo -n grep -Fc 'python3 "$D/validate_bt601_live.py"' "$RUNNER")" == 1 ]]
sudo -n cmp "$H/run-once.sh" "$RUNNER"
cmp "$H/scene_probe.py" /usr/local/lib/sp11-camera-e004na/scene_probe.py
sudo -n cmp "$H/selector_acceptance.py" "$D/rgb/service/selector_acceptance.py"
cmp "$H/iq/nv12_colorimetry.h" "$R/src/sp11-camera-stack/rgb/iq/nv12_colorimetry.h"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n sha256sum -c "$D/SESSION-ASSETS.sha256" >/dev/null
python3 "$H/test_validate_bt601_live.py"
python3 "$R/src/sp11-camera-stack/rgb/tests/test_nv12_gst_colorimetry.py" >/dev/null
python3 -m unittest discover -s "$H" -p 'test_*.py' -q
sudo -n install -m 0600 "$H/validate_bt601_live.py" "$D/validate_bt601_live.py"
[[ "$(sudo -n sha256sum "$D/validate_bt601_live.py" | awk '{print $1}')" == "$(sha256sum "$H/validate_bt601_live.py" | awk '{print $1}')" ]]
printf 'Unarmed source-asset installation omission caught before E004na physical boot. Fresh colour validator copied from source-locked Git HEAD and root all-asset manifest regenerated. No camera, IR, GRUB next_entry, reboot or sensor access during this prearm repair. The original HEAD 98ad08b staged binary/content of camera publishers and runner is unchanged. Repair is single-use; NEVER run after E004na armed or consumed.\n' | sudo -n tee "$D/UNARMED-REPAIR.txt" >/dev/null
sudo -n bash -c 'find "$1" -type f ! -name SESSION-ASSETS.sha256 ! -name EXPECTED-HEAD -print0 | sort -z | xargs -0 sha256sum; sha256sum "$2" "$3" "$4"; find "$5" -type f -print0 | sort -z | xargs -0 sha256sum' bash "$D" "$RUNNER" "$SERVICE" "$ENTRY" "$BOOT" | sudo -n tee "$D/SESSION-ASSETS.sha256" >/dev/null
sudo -n sha256sum /usr/local/lib/sp11-camera-e004na/client.py /usr/local/lib/sp11-camera-e004na/scene_probe.py "$SESSION" | sudo -n tee -a "$D/SESSION-ASSETS.sha256" >/dev/null
sudo -n sha256sum -c "$D/SESSION-ASSETS.sha256" >/dev/null
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-ARMED"
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004NA_UNARMED_COLOUR_VALIDATOR_ASSET_REPAIRED_MANIFEST_LOCKED_NO_BOOT_OR_CAMERA=PASS
