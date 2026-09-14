#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dk-rgb-alternating-soak
BOOT=/boot/sp11-7.1.5-camera-e004dk-rgb-alternating-soak
fail(){ echo "FAIL: $*" >&2; exit 1; }
CMD=$(cat /proc/cmdline)
for t in sp11_camera_e004dk_rgb_alternating_soak=1 sp11_entry=7.1.5-sp11-camera-e004dk-rgb-alternating-soak modprobe.blacklist=qcom_camss,imx681,ov13858 clk_ignore_unused pd_ignore_unused; do grep -Fq "$t"<<<"$CMD" || fail cmdline_$t; done
grep -Fq 'BOOT_IMAGE=/boot/sp11-7.1.5-camera-e004dk-rgb-alternating-soak/vmlinuz-7.1.5-sp11-render-parity-v4+'<<<"$CMD" || fail boot_image
K=$(mktemp); trap 'rm -f "$K"' EXIT; journalctl -b -k --no-pager >"$K"
for n in 'TLB sync timed out -- SMMU may be deadlocked' 'vblank wait timed out' 'Internal error: Oops' 'soft lockup' 'Kernel panic' 'Unhandled fault'; do ! grep -Fiq "$n" "$K" || fail boot_$n; done
sudo -n true || fail sudo
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next_consumed
[ "$(git -C "$R" branch --show-current)" = experiment/e004-front-ir-vd55g0 ] || fail branch
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ] || fail origin
(cd "$R" && sha256sum -c "$D/KNOWN-DIRTY.sha256" >/dev/null) || fail dirty_hash
mapfile -t dirty < <(git -C "$R" diff --name-only | sort); expected=(CONTINUE.md HANDOFF.md PROJECT_STATE.md README.md state/project.yaml); [ "${dirty[*]}" = "${expected[*]}" ] || fail dirty_set
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail module_$m; done
[ ! -e "$D/runtime-output" ] && [ ! -e "$D/ATTEMPT1-CONSUMED.marker" ] && [ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] || fail prior_attempt
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb"|awk '{print $1}')" = 5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321 ] || fail dtb
(cd "$D/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail package
echo 'E004DK_RUNTIME_PREFLIGHT=PASS LEGS=6 TRANSITIONS=5 NEUTRAL_REQUIRED=YES RETRY=NO'
