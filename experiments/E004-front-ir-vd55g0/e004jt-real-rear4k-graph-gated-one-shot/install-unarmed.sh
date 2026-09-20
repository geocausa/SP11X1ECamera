#!/usr/bin/env bash
# E004jt: install root-owned NON-DEFAULT, NON-ARMED one-shot test assets.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004jt-real-rear4k-graph-gated-one-shot
SOURCE=$(cat /tmp/sp11-e004jt-stage-location)
D=/var/lib/sp11-camera-e004jt
BOOT=/boot/sp11-7.1.5-camera-e004jt-graph-rear4k
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004jt
SERVICE=/etc/systemd/system/sp11-camera-e004jt-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004jt-run-once
ID=sp11-camera-e004jt-graph-gated-rear4k-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]] || { echo E004JT_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$D" && ! -e "$BOOT" ]]
for f in "$ENTRY" "$SERVICE" "$RUNNER"; do sudo -n test ! -e "$f"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
! grep -Fq 'sp11_camera_e004jt_rear4k_graph=1' /proc/cmdline
[[ "$(sha256sum "$SOURCE/stage/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
( cd "$SOURCE/stage"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null )
python3 "$R/src/sp11-camera-stack/verify-package.py" "$SOURCE/stage" --require-r4
# E004jg previously proved the exact standalone virtual device with the same
# Golden-v4 ABI. Keep it OUT of the release package, stage root privately.
LOOP_SOURCE=$SOURCE/loopback-build/modules/v4l2loopback/v4l2loopback.ko
LOOP_SOURCE_DEB=$SOURCE/loopback-package/v4l2loopback-source_0.15.3-1ubuntu2_all.deb
LOOP_SHA=52ca41e7a6dd510f1034458969255dfd1f55c244c50830ab12ea1f18795f0379
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
BRIDGE_SOURCE=$R/experiments/E004-front-ir-vd55g0/e004jt-real-rear4k-graph-gated-one-shot
BRIDGE_APP_SOURCE=$R/experiments/E004-front-ir-vd55g0/e004jn-rear-4k-appsrc-offline/nv12-4k-appsrc-consumer.py
BRIDGE_BIN_SHA=adb7925376f61ebf81e30b07f05cabcccde41b400676a9a5b24e7c24903af3c4
BRIDGE_PY_SHA=813d6ad77f5b936955df178c4b426c3c3844d6d640f4377dd7196b5f1fba96a5
[[ "$(sha256sum "$BRIDGE_APP_SOURCE" | awk '{print $1}')" == "$BRIDGE_PY_SHA" ]]
[[ "$(sha256sum "$SOURCE/rear-bayer-4k-27" | awk '{print $1}')" == "$BRIDGE_BIN_SHA" ]]
python3 "$R/src/sp11-camera-stack/verify-package.py" "$SOURCE/stage" --require-r4
[[ "$(sha256sum "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(modinfo -F vermagic "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
[[ "$(sha256sum "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" | awk '{print $1}')" == 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ]]
[[ "$(modinfo -F vermagic "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
find "$SOURCE/stage/usr" -type l | grep . && exit 1 || :
bash -n "$H/run-once.sh"
tail -n +3 "$H/99zzzzzz_sp11_camera_e004jt" | grub-script-check
systemd-analyze verify "$H/sp11-camera-e004jt-one-shot.service" 2>&1 |
  grep -v 'not executable: No such file or directory' || :
# Stage only the candidate assets in a newly created, root-owned directory.
sudo -n mkdir -m 0700 "$D"
sudo -n cp -a "$SOURCE/stage" "$D/stack"
sudo -n install -m 0644 "$LOOP_SOURCE" "$D/v4l2loopback.ko"
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == "$LOOP_SHA" ]]
sudo -n install -d -m 0700 "$D/bridge"
sudo -n install -m 0700 "$SOURCE/rear-bayer-4k-27" "$D/bridge/rear-bayer-to-nv12-4k"
sudo -n install -m 0600 "$BRIDGE_APP_SOURCE" "$D/bridge/nv12-4k-appsrc-consumer.py"
DIAG_SOURCE=$R/experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic/camera-media-graph-diagnostic.py
DIAG_SHA=4435c52d364e4030285c3e74372446eb452fa5722c355301201812a6d2341348
[[ "$(sha256sum "$DIAG_SOURCE" | awk '{print $1}')" == "$DIAG_SHA" ]]
sudo -n install -m 0600 "$DIAG_SOURCE" "$D/camera-media-graph-diagnostic.py"
[[ "$(sudo -n sha256sum "$D/camera-media-graph-diagnostic.py" | awk '{print $1}')" == "$DIAG_SHA" ]]
[[ "$(sudo -n sha256sum "$D/bridge/rear-bayer-to-nv12-4k" | awk '{print $1}')" == "$BRIDGE_BIN_SHA" ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-4k-appsrc-consumer.py" | awk '{print $1}')" == "$BRIDGE_PY_SHA" ]]
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
' bash "$REAR_FIXTURE" "$D/bridge/rear-bayer-to-nv12-4k" \
  "$D/bridge/nv12-4k-appsrc-consumer.py" > "$SOURCE/REAR-APP-DRYRUN.txt" 2>&1
grep -Fq 'E004JT_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$SOURCE/REAR-APP-DRYRUN.txt"
grep -Fq 'E004JN_NV12_APPSRC_CONSUMER=PASS FRAMES=1' "$SOURCE/REAR-APP-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/REAR-APP-DRYRUN.txt" "$D/REAR-APP-DRYRUN.txt"
echo E004JT_ROOT_COPIED_REAL_REAR_4K_BRIDGE_AND_GSTREAMER_OFFLINE_PLAN=PASS
# Prove the exactly staged real Bayer->NV12->GStreamer fdsrc publisher
# grammar without opening a V4L2 device, BEFORE the one-shot may be armed.
sudo -n timeout 22s bash -o pipefail -c '
  cat "$1" | "$2" --frames 1 |
    gst-launch-1.0 -q fdsrc fd=0 blocksize=12441600 \
      ! rawvideoparse format=nv12 width=3840 height=2160 framerate=30/1 \
      ! "video/x-raw,format=NV12,width=3840,height=2160,framerate=30/1" \
      ! fakesink sync=false
' bash "$REAR_FIXTURE" "$D/bridge/rear-bayer-to-nv12-4k" \
  > "$SOURCE/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt" 2>&1
grep -Fq 'E004JT_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$SOURCE/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt" "$D/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
echo E004JT_ROOT_COPIED_REAR_4K_TO_GSTREAMER_FDSRC_PUBLISHER_DRYRUN=PASS
sudo -n sh -c 'cd /var/lib/sp11-camera-e004jt/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
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
print('E004JT_OFFLINE_PACKAGED_FRONT_LAUNCH_PLAN_R4_SIDECAR=PASS')
PY
sudo -n install -m 0600 "$SOURCE/FRONT-LAUNCH-DRYRUN.json" "$D/FRONT-LAUNCH-DRYRUN.json"
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-camera-e004jt-one-shot.service" "$SERVICE"
sudo -n systemd-analyze verify "$SERVICE"
sudo -n mkdir -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004jt-graph-rear4k"
sudo -n install -m 0644 "$D/stack/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$BOOT/"
sudo -n install -m 0755 "$H/99zzzzzz_sp11_camera_e004jt" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-camera-e004jt-one-shot.service
sudo -n update-grub > "$SOURCE/UPDATE-GRUB.log"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n systemctl is-enabled sp11-camera-e004jt-one-shot.service
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemctl is-active --quiet sp11-camera-e004jt-one-shot.service && exit 1 || :
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004JT_INSTALLED=PASS ARMED=NO REAL_REAR_4K_SOURCE_LOCKED=YES ACTIVE_CAMERA=NO AUTO_GOLDEN_RETURN=ENABLED
