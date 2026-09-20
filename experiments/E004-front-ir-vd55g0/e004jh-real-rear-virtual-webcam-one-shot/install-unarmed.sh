#!/usr/bin/env bash
# E004jh: install root-owned NON-DEFAULT, NON-ARMED one-shot test assets.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004jh-real-rear-virtual-webcam-one-shot
SOURCE=/tmp/sp11-e004jh-rear-virtual-source-20260920
D=/var/lib/sp11-camera-e004jh
BOOT=/boot/sp11-7.1.5-camera-e004jh-two-rgb-dma-guard
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004jh
SERVICE=/etc/systemd/system/sp11-camera-e004jh-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004jh-run-once
ID=sp11-camera-e004jh-two-rgb-dma-guard-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]] || { echo E004JH_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$D" && ! -e "$BOOT" ]]
for f in "$ENTRY" "$SERVICE" "$RUNNER"; do sudo -n test ! -e "$f"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
! grep -Fq 'sp11_camera_e004jh_two_rgb_dma_guard=1' /proc/cmdline
[[ "$(sha256sum "$SOURCE/stage/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
( cd "$SOURCE/stage"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null )
python3 "$R/src/sp11-camera-stack/verify-package.py" "$SOURCE/stage" --require-r4
# E004jg previously proved the exact standalone virtual device with the same
# Golden-v4 ABI. Keep it OUT of the release package, stage root privately.
LOOP_SOURCE=/tmp/sp11-e004jg-loopback-source-20260920/source/v4l2loopback/v4l2loopback.ko
LOOP_SOURCE_DEB=/tmp/sp11-e004jg-loopback-source-20260920/v4l2loopback-source_0.15.3-1ubuntu2_all.deb
LOOP_SHA=2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1
[[ "$(sha256sum "$LOOP_SOURCE_DEB" | awk '{print $1}')" == 007a2aa9a723976318407c871b2f1ecdbcd3dc065bf482b0b86f03b026ef40e0 ]]
[[ -f "$LOOP_SOURCE" && ! -L "$LOOP_SOURCE" &&
   "$(sha256sum "$LOOP_SOURCE" | awk '{print $1}')" == "$LOOP_SHA" ]]
[[ "$(modinfo -F vermagic "$LOOP_SOURCE")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
[[ ! -e /dev/video90 && ! -d /sys/module/v4l2loopback ]]
# The E004jd release package now includes the SHA-pinned derived R4
# in BOTH manifests. Never append it a second time or tamper with the release.
R4SRC=$R/src/front-imx681/userspace/iq/authority/r4-bootstrap.bin
R4REL=usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin
R4SHA=1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa
[[ -f "$R4SRC" && ! -L "$R4SRC" && "$(stat -c%s "$R4SRC")" == 41088 ]]
[[ "$(sha256sum "$R4SRC" | awk '{print $1}')" == "$R4SHA" ]]
[[ -f "$SOURCE/stage/$R4REL" && ! -L "$SOURCE/stage/$R4REL" && -f "$SOURCE/stage/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.json" ]]
[[ "$(stat -c%s "$SOURCE/stage/$R4REL")" == 41088 && "$(sha256sum "$SOURCE/stage/$R4REL" | awk '{print $1}')" == "$R4SHA" ]]
# Production package (51 files) is immutable and includes the R4.
# E004je bridge is a separate source-locked private helper, never added
# to that accepted production package or installed into Golden.
BRIDGE_SOURCE=$R/experiments/E004-front-ir-vd55g0/e004je-rear-live-appsrc-bridge
BRIDGE_BIN_SHA=a5b949303fbb40adbdcc62fe494823fec1524feca4d3cd7d5aa273eebdb73c15
BRIDGE_PY_SHA=9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613
[[ "$(sha256sum "$BRIDGE_SOURCE/nv12-appsrc-consumer.py" | awk '{print $1}')" == "$BRIDGE_PY_SHA" ]]
[[ "$(sha256sum "$SOURCE/bridge/rear-bayer-stdin-to-nv12" | awk '{print $1}')" == "$BRIDGE_BIN_SHA" ]]
python3 "$R/src/sp11-camera-stack/verify-package.py" "$SOURCE/stage" --require-r4
[[ "$(sha256sum "$SOURCE/candidate/camss/qcom-camss.ko" | awk '{print $1}')" == 4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d ]]
[[ "$(sha256sum "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sha256sum "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" | awk '{print $1}')" == 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ]]
[[ "$(modinfo -F vermagic "$SOURCE/candidate/camss/qcom-camss.ko")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
find "$SOURCE/stage/usr" -type l | grep . && exit 1 || :
bash -n "$H/run-once.sh"
tail -n +3 "$H/99zzzzzz_sp11_camera_e004jh" | grub-script-check
systemd-analyze verify "$H/sp11-camera-e004jh-one-shot.service" 2>&1 |
  grep -v 'not executable: No such file or directory' || :
# Stage only the candidate assets in a newly created, root-owned directory.
sudo -n mkdir -m 0700 "$D"
sudo -n cp -a "$SOURCE/stage" "$D/stack"
sudo -n mkdir -m 0700 "$D/candidate"
sudo -n install -m 0644 "$SOURCE/candidate/camss/qcom-camss.ko" "$D/candidate/qcom-camss.ko"
sudo -n install -m 0644 "$LOOP_SOURCE" "$D/v4l2loopback.ko"
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == "$LOOP_SHA" ]]
sudo -n install -d -m 0700 "$D/bridge"
sudo -n install -m 0700 "$SOURCE/bridge/rear-bayer-stdin-to-nv12" "$D/bridge/rear-bayer-stdin-to-nv12"
sudo -n install -m 0600 "$BRIDGE_SOURCE/nv12-appsrc-consumer.py" "$D/bridge/nv12-appsrc-consumer.py"
[[ "$(sudo -n sha256sum "$D/bridge/rear-bayer-stdin-to-nv12" | awk '{print $1}')" == "$BRIDGE_BIN_SHA" ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-appsrc-consumer.py" | awk '{print $1}')" == "$BRIDGE_PY_SHA" ]]
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
sudo -n chown -R root:root "$D"
sudo -n chmod 0700 "$D"
# Hardware-free acceptance of the ROOT-COPIED bridge and exact archived
# rear colourbar. Checks a genuine Gst appsrc/application consumer before
# this boot ever loads a camera module; only text metadata is persisted.
REAR_FIXTURE=$R/experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw
[[ -f "$REAR_FIXTURE" && "$(stat -c%s "$REAR_FIXTURE")" == 14321824 ]]
[[ "$(sha256sum "$REAR_FIXTURE" | awk '{print $1}')" == 6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346 ]]
sudo -n timeout 20s bash -o pipefail -c '
  cat "$1" | "$2" --frames 1 | /usr/bin/python3 "$3" --frames 1
' bash "$REAR_FIXTURE" "$D/bridge/rear-bayer-stdin-to-nv12" \
  "$D/bridge/nv12-appsrc-consumer.py" > "$SOURCE/REAR-APP-DRYRUN.txt" 2>&1
grep -Fq 'E004JE_BAYER10_STREAM_NV12=PASS FRAMES=1' "$SOURCE/REAR-APP-DRYRUN.txt"
grep -Fq 'E004JE_NV12_APPSRC_CONSUMER=PASS FRAMES=1' "$SOURCE/REAR-APP-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/REAR-APP-DRYRUN.txt" "$D/REAR-APP-DRYRUN.txt"
echo E004JH_ROOT_COPIED_REAR_BRIDGE_AND_GSTREAMER_OFFLINE_PLAN=PASS
# Prove the exactly staged real Bayer->NV12->GStreamer fdsrc publisher
# grammar without opening a V4L2 device, BEFORE the one-shot may be armed.
sudo -n timeout 22s bash -o pipefail -c '
  cat "$1" | "$2" --frames 1 |
    gst-launch-1.0 -q fdsrc fd=0 blocksize=3110400 \
      ! rawvideoparse format=nv12 width=1920 height=1080 framerate=30/1 \
      ! "video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1" \
      ! fakesink sync=false
' bash "$REAR_FIXTURE" "$D/bridge/rear-bayer-stdin-to-nv12" \
  > "$SOURCE/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt" 2>&1
grep -Fq 'E004JE_BAYER10_STREAM_NV12=PASS FRAMES=1' "$SOURCE/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt" "$D/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
echo E004JH_ROOT_COPIED_BAYER_TO_GSTREAMER_FDSRC_PUBLISHER_DRYRUN=PASS
sudo -n sh -c 'cd /var/lib/sp11-camera-e004jh/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
# The 51-file canonical package itself contains the required R4.
# Do NOT alter its digest after staging; prove the installed launcher OFFLINE.
[[ "$(sudo -n sha256sum "$D/stack/$R4REL" | awk '{print $1}')" == "$R4SHA" ]]
sudo -n test "$(sudo -n stat -c%s "$D/stack/$R4REL")" -eq 41088
sudo -n python3 "$D/stack/usr/lib/sp11-front-imx681/bin/front-imx681-launcher.py" \
  --topology-file "$R/experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/LOAD-MEDIA.txt" \
  --media /dev/media0 --build-dir "$D/stack/usr/lib/sp11-front-imx681/build" \
  --output-dir "$D/offline-plan-do-not-create" \
  --post-g3-write-policy shadow > "$SOURCE/FRONT-LAUNCH-DRYRUN.json"
python3 - "$SOURCE/FRONT-LAUNCH-DRYRUN.json" "$D" "$R4SHA" <<'PY'
import json,sys
from pathlib import Path
p=json.loads(Path(sys.argv[1]).read_text())
d=Path(sys.argv[2]); sha=sys.argv[3]
assert p['r4_sha256']==sha and p['execute'] is False
assert p['post_g3_write_policy']=='shadow'
assert p['discovery']['proven_capture_fourcc']=='QC10C'
assert p['capture_command'][2]==str(d/'stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin')
assert p['output_dir']==str(d/'offline-plan-do-not-create')
assert not (d/'offline-plan-do-not-create').exists()
print('E004JH_OFFLINE_PACKAGED_FRONT_LAUNCH_PLAN_R4_SIDECAR=PASS')
PY
sudo -n install -m 0600 "$SOURCE/FRONT-LAUNCH-DRYRUN.json" "$D/FRONT-LAUNCH-DRYRUN.json"
[[ "$(sudo -n sha256sum "$D/candidate/qcom-camss.ko" | awk '{print $1}')" == 4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d ]]
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-camera-e004jh-one-shot.service" "$SERVICE"
sudo -n systemd-analyze verify "$SERVICE"
sudo -n mkdir -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004jh-two-rgb-dma-guard"
sudo -n install -m 0644 "$D/stack/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$BOOT/"
sudo -n install -m 0755 "$H/99zzzzzz_sp11_camera_e004jh" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-camera-e004jh-one-shot.service
sudo -n update-grub > "$SOURCE/UPDATE-GRUB.log"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n systemctl is-enabled sp11-camera-e004jh-one-shot.service
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemctl is-active --quiet sp11-camera-e004jh-one-shot.service && exit 1 || :
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004JH_INSTALLED=PASS ARMED=NO ACTIVE_CAMERA=NO AUTOMATIC_GOLDEN_RETURN_UNIT=ENABLED
