#!/usr/bin/env bash
# E004me: separate root-only non-default non-armed software RGB trial.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004me-morning-full10-rgb-channel-profile-one-shot
SOURCE=$(cat /tmp/sp11-e004me-stage-location)
D=/var/lib/sp11-camera-e004me
BOOT=/boot/sp11-7.1.5-camera-e004me-rgb-session
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004me
SERVICE=/etc/systemd/system/sp11-camera-e004me-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004me-run-once
ID=sp11-camera-e004me-morning-full10-rgb-channel-profile-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" && ! -e "$H/evidence/CONSUMED.json" && ! -e "$H/RESULT.json" ]] || { echo E004ME_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$D" && ! -e "$BOOT" && ! -e /usr/local/lib/sp11-camera-e004me && ! -e /etc/systemd/system/sp11-camera-e004me-session@.service ]]
for f in "$ENTRY" "$SERVICE" "$RUNNER"; do sudo -n test ! -e "$f"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
! grep -Fq 'sp11_camera_e004me_rgb_session=1' /proc/cmdline
[[ "$(sha256sum "$SOURCE/stage/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
( cd "$SOURCE/stage"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null )
python3 "$R/src/sp11-camera-stack/verify-package.py" "$SOURCE/stage" --require-r4
# Stage standalone temporary standard front V4L2 loopback module only in this disposable candidate.
[[ ! -e /dev/video90 && ! -e /dev/video91 && ! -d /sys/module/v4l2loopback ]]
R4SRC=$R/src/front-imx681/userspace/iq/authority/r4-bootstrap.bin
R4REL=usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin
R4SHA=1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa
[[ -f "$R4SRC" && ! -L "$R4SRC" && "$(stat -c%s "$R4SRC")" == 41088 ]]
[[ "$(sha256sum "$R4SRC" | awk '{print $1}')" == "$R4SHA" ]]
[[ "$(sha256sum "$SOURCE/stage/$R4REL" | awk '{print $1}')" == "$R4SHA" ]]
FRONT_SOURCE=$H/front-rggb10p-to-nv12-1080.c
FRONT_SOURCE_SHA=6563134ef6c11d130a6134050b7b49577f9bf912a69d79fa82fb707cf641a028
FRONT_BRIDGE_SHA=820a6871f78e9ecaecfd4b1a16fc1e0bad9600aeeb6a1505133e467c1354dc82
FRONT_AUDIT_SHA=377a9c2e8704bd57687c5449608c632e1e06cc39067b87cc28aa3ac8a060d186
FRONT_APP_SHA=e165491ea22bcc4c452ea03073525662293c30ff3c274c67c4c6d4872e1c6b0a
FRONT_ROUTE_SHA=53c2230114512b954c67fa4572df569394d3bd259fb3ae036691f72002009861
FRONT_VALIDATOR_SHA=934fb0aea58c8996ec9edd1e9581c3ce83d7c48cff0ba8ae10923c4877ec95f4
FRONT_NV12_AUDIT_SOURCE=$H/front-nv12-1080p-pipe-audit.c
FRONT_NV12_AUDIT_SOURCE_SHA=2d194cac3301c8189a37eb08768c4962919cfd83f293902e77ebfb1ed0369b62
FRONT_NV12_AUDIT_SHA=23e5152cea7dab8b437eae309f16a8f33e7c01b50f9ab61fa26f952d90b3600e
[[ "$(sha256sum "$FRONT_NV12_AUDIT_SOURCE" | awk '{print $1}')" == "$FRONT_NV12_AUDIT_SOURCE_SHA" ]]
[[ "$(sha256sum "$SOURCE/front-nv12-1080p-pipe-audit" | awk '{print $1}')" == "$FRONT_NV12_AUDIT_SHA" ]]
LOOP_SOURCE=$SOURCE/loopback-clean/modules/v4l2loopback/v4l2loopback.ko
LOOP_SOURCE_DEB=$SOURCE/loopback-package/v4l2loopback-source_0.15.3-1ubuntu2_all.deb
LOOP_SHA=4ac4c557c7d9ae67829808ee46bfa0b86f73eb491856d1e9ce0de1db0daa8cda
[[ "$(sha256sum "$LOOP_SOURCE_DEB" | awk '{print $1}')" == 007a2aa9a723976318407c871b2f1ecdbcd3dc065bf482b0b86f03b026ef40e0 ]]
[[ -f "$LOOP_SOURCE" && ! -L "$LOOP_SOURCE" && "$(sha256sum "$LOOP_SOURCE" | awk '{print $1}')" == "$LOOP_SHA" ]]
[[ "$(modinfo -F vermagic "$LOOP_SOURCE")" == '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ]]
DIAG_SOURCE=$R/experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic/camera-media-graph-diagnostic.py
DIAG_SHA=4435c52d364e4030285c3e74372446eb452fa5722c355301201812a6d2341348
[[ "$(sha256sum "$FRONT_SOURCE" | awk '{print $1}')" == "$FRONT_SOURCE_SHA" ]]
[[ "$(sha256sum "$SOURCE/front-rggb10p-to-nv12-1080" | awk '{print $1}')" == "$FRONT_BRIDGE_SHA" ]]
[[ "$(sha256sum "$SOURCE/front-rdi-raw10-pipe-audit" | awk '{print $1}')" == "$FRONT_AUDIT_SHA" ]]
[[ "$(sha256sum "$H/front-1080p-app.py" | awk '{print $1}')" == "$FRONT_APP_SHA" ]]
[[ "$(sha256sum "$H/route-state.py" | awk '{print $1}')" == "$FRONT_ROUTE_SHA" ]]
[[ "$(sha256sum "$H/validate-front-rdi.py" | awk '{print $1}')" == "$FRONT_VALIDATOR_SHA" ]]
[[ "$(sha256sum "$DIAG_SOURCE" | awk '{print $1}')" == "$DIAG_SHA" ]]
[[ "$(sha256sum "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(modinfo -F vermagic "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
[[ "$(sha256sum "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" | awk '{print $1}')" == 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ]]
bash -n "$H/run-once.sh" "$H/arm-once.sh" "$H/retire-after-golden.sh"
python3 "$H/test_scene_probe.py"
python3 "$H/test_paired_source_validator.py"
python3 "$H/test_sensor_gain_trial.py"
gcc -O3 -std=c11 -Wall -Wextra -Werror -pedantic "$H/test_raw_nv12_probe.c" -o "$SOURCE/pair-scalar-probe-offline-test"
"$SOURCE/pair-scalar-probe-offline-test"
tail -n +3 "$H/99zzzzzz_sp11_camera_e004me" | grub-script-check
# Source-only graph and converted pixel integrity checks, never camera activation.
python3 -m unittest discover -s "$R/experiments/E004-front-ir-vd55g0/e004ke-front-rdi-rggb-raw-bypass" -p 'test_*.py' -q
python3 -m unittest discover -s "$R/experiments/E004-front-ir-vd55g0/e004ki-front-rear-session-switch-offline" -p 'test_*.py' -q
# Stage exclusively root-private; no experimental binary is installed into Golden.
sudo -n mkdir -m 0700 "$D"
sudo -n cp -a "$SOURCE/stage" "$D/stack"
sudo -n install -m 0644 "$LOOP_SOURCE" "$D/v4l2loopback.ko"
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == "$LOOP_SHA" ]]
sudo -n install -d -m 0700 "$D/bridge"
sudo -n install -m 0700 "$SOURCE/front-rggb10p-to-nv12-1080" "$D/bridge/front-rggb10p-to-nv12-1080"
sudo -n install -m 0700 "$SOURCE/front-rdi-raw10-pipe-audit" "$D/bridge/front-rdi-raw10-pipe-audit"
sudo -n install -m 0700 "$SOURCE/front-nv12-1080p-pipe-audit" "$D/bridge/front-nv12-1080p-pipe-audit"
[[ "$(sudo -n sha256sum "$D/bridge/front-nv12-1080p-pipe-audit" | awk '{print $1}')" == "$FRONT_NV12_AUDIT_SHA" ]]
sudo -n install -m 0600 "$H/front-1080p-app.py" "$D/bridge/front-1080p-app.py"
sudo -n install -m 0600 "$H/route-state.py" "$D/route-state.py"
sudo -n install -m 0600 "$H/validate-front-rdi.py" "$D/validate-front-rdi.py"
sudo -n install -m 0600 "$DIAG_SOURCE" "$D/camera-media-graph-diagnostic.py"
[[ "$(sudo -n sha256sum "$D/bridge/front-rggb10p-to-nv12-1080" | awk '{print $1}')" == "$FRONT_BRIDGE_SHA" ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-rdi-raw10-pipe-audit" | awk '{print $1}')" == "$FRONT_AUDIT_SHA" ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-1080p-app.py" | awk '{print $1}')" == "$FRONT_APP_SHA" ]]
# Root-copied session/rear components are manifest-locked before camera activation.
for file in camera-session-contract.py discover-unified.py publish-front.sh publish-rear.sh validate-partial.py direct-camera-app.py thermal-monitor.py validate-session.py record-stop.py validate-stop.py; do
 sudo -n install -m 0600 "$H/$file" "$D/$file"
done
for camera in front rear; do
 sudo -n install -m 0700 "$SOURCE/$camera-direct-publisher" "$D/bridge/$camera-direct-publisher"
done
[[ "$(sudo -n sha256sum "$D/bridge/front-direct-publisher" | awk '{print $1}')" == a25885a18a127dc5ba513cd2b47a9085c7bc50e67c0ff96a22c4767d33513c87 ]]
[[ "$(sudo -n sha256sum "$D/bridge/rear-direct-publisher" | awk '{print $1}')" == 5d9f27d2b140c629be0e221ef45efd491169c17bd7d6ac2ffd4b86a2f0fcab3e ]]
sudo -n install -m 0700 "$SOURCE/rear-bayer-4k-240" "$D/bridge/rear-bayer-to-nv12-4k"
sudo -n install -m 0700 "$SOURCE/nv12-4k-pipe-audit" "$D/bridge/nv12-4k-pipe-audit"
sudo -n install -m 0600 "$R/experiments/E004-front-ir-vd55g0/e004jx-rear-4k-partial-telemetry/nv12-4k-partial-telemetry-app.py" "$D/bridge/nv12-4k-partial-telemetry-app.py"
[[ "$(sudo -n sha256sum "$D/bridge/rear-bayer-to-nv12-4k" | awk '{print $1}')" == 2d2678fa2edccf8d1d63699d5575a5b3a949a479aff9fcab07604a72ef234c12 ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-4k-pipe-audit" | awk '{print $1}')" == b59cacf149021bcaee39ac9c54ce7f6fd2f4e4fead7dbeacb24ca8dfe51b4bff ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-4k-partial-telemetry-app.py" | awk '{print $1}')" == 1e129b385d9d849808eadd1e8b43224e721c19c3bb364513975604d05ce7e0b8 ]]
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
sudo -n chown -R root:root "$D"
sudo -n chmod 0700 "$D"
# Generate one synthetic RGGB RAW10 frame INTO A PIPE; only text metadata persisted.
sudo -n timeout 25s bash -o pipefail -c '
  /usr/bin/python3 -c '"'"'import sys
r=bytes([220,95,220,95,0])*(3840//4)
b=bytes([95,50,95,50,0])*(3840//4)
frame=(r+b)*1080
assert len(frame)==10368000
sys.stdout.buffer.write(frame)'"'"' |
    "$1" --frames 1 --idle-ms 2500 |
    "$2" --frames 1 |
    /usr/bin/python3 "$3" --frames 1 --idle-seconds 3
' bash "$D/bridge/front-rdi-raw10-pipe-audit" "$D/bridge/front-rggb10p-to-nv12-1080" \
  "$D/bridge/front-1080p-app.py" > "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt" 2>&1
grep -Fq 'E004KH_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt"
grep -Fq 'E004KH_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=1' "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt"
grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt" "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
# A second camera-free dry run verifies exact 1920x1080 NV12 meter + actual
# GStreamer consumer, with one transient synthetic frame and zero pixel files.
sudo -n timeout 20s bash -o pipefail -c '
 /usr/bin/python3 -c "import sys;sys.stdout.buffer.write(bytes([100])*(1920*1080*3//2))" |
   "$1" --frames 1 --idle-ms 2500 |
   /usr/bin/python3 "$2" --frames 1 --idle-seconds 3
' bash "$D/bridge/front-nv12-1080p-pipe-audit" "$D/bridge/front-1080p-app.py" > "$SOURCE/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt" 2>&1
grep -Fq 'E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$SOURCE/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$SOURCE/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt" "$D/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
sudo -n sh -c 'cd /var/lib/sp11-camera-e004me/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
REAR_FIXTURE=$R/experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw
[[ -f "$REAR_FIXTURE" && "$(stat -c%s "$REAR_FIXTURE")" == 14321824 ]]
[[ "$(sha256sum "$REAR_FIXTURE" | awk '{print $1}')" == 6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346 ]]
sudo -n timeout 20s bash -o pipefail -c '
  cat "$1" | "$2" --frames 1 | /usr/bin/python3 "$3" --frames 1
' bash "$REAR_FIXTURE" "$D/bridge/rear-bayer-to-nv12-4k" \
  "$D/bridge/nv12-4k-partial-telemetry-app.py" > "$SOURCE/REAR-APP-DRYRUN.txt" 2>&1
grep -Fq 'E004KK_PIPE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$SOURCE/REAR-APP-DRYRUN.txt"
grep -Fq 'E004JX_NV12_APPSRC_CONSUMER=PASS FRAMES=1' "$SOURCE/REAR-APP-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/REAR-APP-DRYRUN.txt" "$D/REAR-APP-DRYRUN.txt"
sudo -n timeout 25s bash -o pipefail -c '
  cat "$1" | "$2" --frames 1 |
    "$3" --frames 1 --idle-ms 3000 |
    /usr/bin/python3 "$4" --frames 1 --idle-seconds 4
' bash "$REAR_FIXTURE" "$D/bridge/rear-bayer-to-nv12-4k" \
  "$D/bridge/nv12-4k-pipe-audit" "$D/bridge/nv12-4k-partial-telemetry-app.py" \
  > "$SOURCE/REAR-PIPE-AUDIT-DRYRUN.txt" 2>&1
grep -Fq 'E004JZ_4K_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$SOURCE/REAR-PIPE-AUDIT-DRYRUN.txt"
grep -Fq 'E004JX_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$SOURCE/REAR-PIPE-AUDIT-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/REAR-PIPE-AUDIT-DRYRUN.txt" "$D/REAR-PIPE-AUDIT-DRYRUN.txt"
sudo -n install -d -m 0755 /usr/local/lib/sp11-camera-e004me
sudo -n install -m 0644 "$H/direct-camera-app.py" /usr/local/lib/sp11-camera-e004me/client.py
sudo -n install -m 0600 "$H/start-session.sh" "$D/start-session.sh"
sudo -n install -m 0600 "$H/client_lifecycle.py" "$D/client_lifecycle.py"
sudo -n install -m 0600 "$H/paired_source_validator.py" "$D/paired_source_validator.py"
sudo -n install -m 0600 "$H/validate_raw10_profile.py" "$D/validate_raw10_profile.py"
# Root-sealed maintained service backend; no source tree imports at runtime.
# Exact files are committed and then pinned by the candidate asset manifest.
sudo -n install -d -m 0700 "$D/rgb" "$D/rgb/service" "$D/routing"
for module in session.py media_backend.py rgb_device_backend.py candidate_owner.py candidate_driver.py selector.py rgbctl.py; do
 sudo -n install -m 0600 "$R/src/sp11-camera-stack/rgb/service/$module" "$D/rgb/service/$module"
done
# Fresh E004me in-memory scene diagnostic; do not alter maintained daily
# service controller or the previously CONSUMED E004ma runner.
sudo -n install -m 0600 "$H/selector_acceptance.py" "$D/rgb/service/selector_acceptance.py"
sudo -n install -m 0600 "$H/sensor_gain_trial.py" "$D/rgb/service/sensor_gain_trial.py"
sudo -n install -m 0644 "$H/scene_probe.py" /usr/local/lib/sp11-camera-e004me/scene_probe.py
for module in route_policy.py graph_contract.py; do
 sudo -n install -m 0600 "$R/src/sp11-camera-stack/routing/$module" "$D/routing/$module"
done
sudo -n install -m 0644 "$H/sp11-camera-e004me-session@.service" /etc/systemd/system/sp11-camera-e004me-session@.service
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-camera-e004me-one-shot.service" "$SERVICE"
sudo -n systemd-analyze verify "$SERVICE" /etc/systemd/system/sp11-camera-e004me-session@.service
sudo -n mkdir -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004me-rgb-session"
sudo -n install -m 0644 "$D/stack/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$BOOT/"
sudo -n install -m 0755 "$H/99zzzzzz_sp11_camera_e004me" "$ENTRY"
# Absolute-path SHA manifest pins all root-copied execution inputs and private boot assets.
sudo -n bash -c 'find "$1" -type f ! -name SESSION-ASSETS.sha256 ! -name EXPECTED-HEAD -print0 | sort -z | xargs -0 sha256sum; sha256sum "$2" "$3" "$4"; find "$5" -type f -print0 | sort -z | xargs -0 sha256sum' bash "$D" "$RUNNER" "$SERVICE" "$ENTRY" "$BOOT" | sudo -n tee "$D/SESSION-ASSETS.sha256" >/dev/null
sudo -n sha256sum /usr/local/lib/sp11-camera-e004me/client.py /usr/local/lib/sp11-camera-e004me/scene_probe.py /etc/systemd/system/sp11-camera-e004me-session@.service | sudo -n tee -a "$D/SESSION-ASSETS.sha256" >/dev/null
sudo -n sha256sum -c "$D/SESSION-ASSETS.sha256" >/dev/null
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-camera-e004me-one-shot.service
sudo -n update-grub > "$SOURCE/UPDATE-GRUB.log"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n systemctl is-enabled sp11-camera-e004me-one-shot.service
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemctl is-active --quiet sp11-camera-e004me-one-shot.service && exit 1 || :
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004ME_INSTALLED=PASS ARMED=NO FRONT_RDI_RAW10_SOURCE_LOCKED=YES ACTIVE_CAMERA=NO AUTO_GOLDEN_RETURN=ENABLED
