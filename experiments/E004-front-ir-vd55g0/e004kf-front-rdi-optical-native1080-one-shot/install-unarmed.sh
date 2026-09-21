#!/usr/bin/env bash
# E004kf: install root-owned NON-DEFAULT, NON-ARMED one-shot test assets.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004kf-front-rdi-optical-native1080-one-shot
SOURCE=$(cat /tmp/sp11-e004kf-stage-location)
D=/var/lib/sp11-camera-e004kf
BOOT=/boot/sp11-7.1.5-camera-e004kf-front-rdi
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004kf
SERVICE=/etc/systemd/system/sp11-camera-e004kf-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004kf-run-once
ID=sp11-camera-e004kf-front-rdi-optical-native1080-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" && ! -e "$H/evidence/CONSUMED.json" && ! -e "$H/RESULT.json" ]] || { echo E004KF_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$D" && ! -e "$BOOT" ]]
for f in "$ENTRY" "$SERVICE" "$RUNNER"; do sudo -n test ! -e "$f"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
! grep -Fq 'sp11_camera_e004kf_front_rdi=1' /proc/cmdline
[[ "$(sha256sum "$SOURCE/stage/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
( cd "$SOURCE/stage"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null )
python3 "$R/src/sp11-camera-stack/verify-package.py" "$SOURCE/stage" --require-r4
# Front RDI proof does NOT load a virtual video module or publish virtual video.
[[ ! -e /dev/video90 && ! -e /dev/video91 && ! -d /sys/module/v4l2loopback ]]
R4SRC=$R/src/front-imx681/userspace/iq/authority/r4-bootstrap.bin
R4REL=usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin
R4SHA=1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa
[[ -f "$R4SRC" && ! -L "$R4SRC" && "$(stat -c%s "$R4SRC")" == 41088 ]]
[[ "$(sha256sum "$R4SRC" | awk '{print $1}')" == "$R4SHA" ]]
[[ "$(sha256sum "$SOURCE/stage/$R4REL" | awk '{print $1}')" == "$R4SHA" ]]
FRONT_SOURCE=$R/experiments/E004-front-ir-vd55g0/e004ke-front-rdi-rggb-raw-bypass/front-rggb10p-to-nv12-1080.c
FRONT_SOURCE_SHA=42c94f32aad21d20592a8d0bcd6b47e40b905120d65d9a27599f2a55f754f1a7
FRONT_BRIDGE_SHA=3b4120431e0bc00429967dc476a24fc1edf5b2d082e12e814c1065bdf17724db
FRONT_AUDIT_SHA=9ef2bcc93b85ba8e1af3337f77d6e8dbe0d8a2bd23ea70793f84c293e7be14df
FRONT_APP_SHA=38fe90ca920b31edb1dced7bb36874d29a7ebc129754220546410130a20c068e
FRONT_ROUTE_SHA=91dbfe9b1ae299c69792e62efcc8cf2e2e0da665dc46d90743c64b83d5cec035
FRONT_VALIDATOR_SHA=ad5592776eb77cb941b96763cb4cb3419cff95a3f2b62cca50cd526dbc643c8b
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
tail -n +3 "$H/99zzzzzz_sp11_camera_e004kf" | grub-script-check
# Source-only graph and converted pixel integrity checks, never camera activation.
python3 -m unittest discover -s "$R/experiments/E004-front-ir-vd55g0/e004ke-front-rdi-rggb-raw-bypass" -p 'test_*.py' -q
python3 -m unittest discover -s "$H" -p 'test_*.py' -q
# Stage exclusively root-private; no experimental binary is installed into Golden.
sudo -n mkdir -m 0700 "$D"
sudo -n cp -a "$SOURCE/stage" "$D/stack"
sudo -n install -d -m 0700 "$D/bridge"
sudo -n install -m 0700 "$SOURCE/front-rggb10p-to-nv12-1080" "$D/bridge/front-rggb10p-to-nv12-1080"
sudo -n install -m 0700 "$SOURCE/front-rdi-raw10-pipe-audit" "$D/bridge/front-rdi-raw10-pipe-audit"
sudo -n install -m 0600 "$H/front-1080p-app.py" "$D/bridge/front-1080p-app.py"
sudo -n install -m 0600 "$H/route-state.py" "$D/route-state.py"
sudo -n install -m 0600 "$H/validate-front-rdi.py" "$D/validate-front-rdi.py"
sudo -n install -m 0600 "$DIAG_SOURCE" "$D/camera-media-graph-diagnostic.py"
[[ "$(sudo -n sha256sum "$D/bridge/front-rggb10p-to-nv12-1080" | awk '{print $1}')" == "$FRONT_BRIDGE_SHA" ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-rdi-raw10-pipe-audit" | awk '{print $1}')" == "$FRONT_AUDIT_SHA" ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-1080p-app.py" | awk '{print $1}')" == "$FRONT_APP_SHA" ]]
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
grep -Fq 'E004KF_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt"
grep -Fq 'E004KE_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=1' "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt"
grep -Fq 'E004KF_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n install -m 0600 "$SOURCE/FRONT-OFFLINE-PIPE-DRYRUN.txt" "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n sh -c 'cd /var/lib/sp11-camera-e004kf/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-camera-e004kf-one-shot.service" "$SERVICE"
sudo -n systemd-analyze verify "$SERVICE"
sudo -n mkdir -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004kf-front-rdi"
sudo -n install -m 0644 "$D/stack/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$BOOT/"
sudo -n install -m 0755 "$H/99zzzzzz_sp11_camera_e004kf" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-camera-e004kf-one-shot.service
sudo -n update-grub > "$SOURCE/UPDATE-GRUB.log"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n systemctl is-enabled sp11-camera-e004kf-one-shot.service
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemctl is-active --quiet sp11-camera-e004kf-one-shot.service && exit 1 || :
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004KF_INSTALLED=PASS ARMED=NO FRONT_RDI_RAW10_SOURCE_LOCKED=YES ACTIVE_CAMERA=NO AUTO_GOLDEN_RETURN=ENABLED
