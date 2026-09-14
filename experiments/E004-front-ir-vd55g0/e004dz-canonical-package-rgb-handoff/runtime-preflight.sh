#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff
fail(){ echo "FAIL: $*" >&2; exit 1; }
CMD=$(cat /proc/cmdline)
for t in sp11_camera_e004dz_canonical_package_rgb_handoff=1 sp11_entry=7.1.5-sp11-camera-e004dz-canonical-package-rgb-handoff modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0; do grep -Fq "$t"<<<"$CMD" || fail cmdline_$t; done
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next_not_consumed
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ] || fail origin
(cd "$R" && sha256sum -c "$D/KNOWN-DIRTY.sha256" >/dev/null) || fail dirty_hash
mapfile -t dirty < <(git -C "$R" diff --name-only | sort); expected=(CONTINUE.md HANDOFF.md PROJECT_STATE.md README.md state/project.yaml); [ "${dirty[*]}" = "${expected[*]}" ] || fail dirty_set
for x in UNIFIED-DISCOVERY.json LOAD-MEDIA.txt DMESG.txt ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json ATTEMPT1-CONSUMED.marker; do [ ! -e "$D/$x" ] || fail prior_$x; done
for m in qcom_camss imx681 ov13858 sp11_vd55g0 e004t_csiphy_readback_test; do [ ! -d "/sys/module/$m" ] || fail module_$m; done
[ ! -e /dev/media0 ] || fail media_present
[ "$(sha256sum /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256|awk '{print $1}')" = d1d0eb4c504378643630f6975a08d9c15d2b8ac0bedca2f1205bbfb51f885373 ] || fail package_manifest
sudo -n sh -c 'cd / && sha256sum -c /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256 >/dev/null' || fail package_files
grep -qx 'activated=NO' /var/lib/sp11-camera-stack/INSTALL-STATE.txt || fail package_activation_state
for spec in \
 '/proc/device-tree/soc@0/cci@ac15000/i2c-bus@0/camera@60/compatible:microsoft,sp11-vd55g0' \
 '/proc/device-tree/soc@0/cci@ac15000/i2c-bus@1/camera@10/compatible:ovti,ov13858' \
 '/proc/device-tree/soc@0/cci@ac16000/i2c-bus@1/camera@10/compatible:sony,imx681'; do p=${spec%%:*}; v=${spec#*:}; [ -r "$p" ] || fail dt_$v; [ "$(tr -d '\0' < "$p")" = "$v" ] || fail compat_$v; done
sudo -n modprobe i2c_qcom_cci
find_compat(){ local addr=$1 compat=$2 p; for p in /sys/bus/i2c/devices/*-$addr; do [ -e "$p" ] || continue; [ -r "$p/of_node/compatible" ] || continue; [ "$(tr -d '\0' < "$p/of_node/compatible")" = "$compat" ] && { echo "$p"; return 0; }; done; return 1; }
IR=; REAR=; FRONT=
for _ in $(seq 1 60); do IR=$(find_compat 0060 microsoft,sp11-vd55g0 2>/dev/null||true); REAR=$(find_compat 0010 ovti,ov13858 2>/dev/null||true); FRONT=$(find_compat 0010 sony,imx681 2>/dev/null||true); [ -n "$IR" ] && [ -n "$REAR" ] && [ -n "$FRONT" ] && break; sleep 0.1; done
[ -n "$IR" ] && [ -n "$REAR" ] && [ -n "$FRONT" ] || fail i2c_clients
for p in "$IR" "$REAR" "$FRONT"; do [ ! -e "$p/driver" ] || fail unexpected_bound_$(basename "$p"); done
{
 echo schema=sp11-camera-e004dz-runtime-preflight-v1; echo status=PASS_READY_FOR_PACKAGE_REAR_FRONT_HANDOFF; echo time=$(date -Ins); echo boot_id=$(cat /proc/sys/kernel/random/boot_id)
 echo ir_client_path=$IR; echo rear_client_path=$REAR; echo front_client_path=$FRONT; echo package_manifest_sha256=d1d0eb4c504378643630f6975a08d9c15d2b8ac0bedca2f1205bbfb51f885373
 echo qcom_camss=absent; echo media_node=absent; echo ir_stream=NO; echo illumination=NO; echo secureisp=NO; echo retry=NO
} > "$D/RUNTIME-PREFLIGHT.txt"
echo "E004DZ_RUNTIME_PREFLIGHT=PASS IR=$(basename "$IR") REAR=$(basename "$REAR") FRONT=$(basename "$FRONT") PACKAGE=EXACT"
