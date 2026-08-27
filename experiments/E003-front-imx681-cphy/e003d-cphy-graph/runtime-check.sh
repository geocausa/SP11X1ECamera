#!/bin/bash
set -u
say(){ printf '\n=== %s ===\n' "$1"; }
say boot
uname -r
cat /proc/cmdline
sudo grub-editenv /boot/grub/grubenv list || true
say modules
for m in qcom_camss imx681; do echo "$m srcversion=$(cat /sys/module/$m/srcversion 2>/dev/null || echo absent)"; done
say imx681-driver-pm
readlink -f /sys/bus/i2c/devices/3-0010/driver 2>/dev/null || true
for f in runtime_status runtime_usage runtime_active_time runtime_suspended_time control; do printf '%s=' "$f"; cat "/sys/bus/i2c/devices/3-0010/power/$f" 2>/dev/null || true; done
say media-front
for m in /dev/media*; do [ -e "$m" ] || continue; out=$(media-ctl -d "$m" -p 2>/dev/null || true); if grep -q 'imx681\|msm_csiphy2' <<<"$out"; then echo "MEDIA=$m"; grep -A10 -B4 -E 'imx681|msm_csiphy2' <<<"$out"; fi; done
say clocks
sudo grep -E 'cam_cc_mclk4_clk |cam_cc_csiphy2_clk |cam_cc_csi2phytimer_clk ' /sys/kernel/debug/clk/clk_summary 2>/dev/null || true
say rails
sudo grep -A2 -E 'vreg_l3m_camera|vreg_l7b_2p8' /sys/kernel/debug/regulator/regulator_summary 2>/dev/null || true
say reset
sudo grep -E '^ gpio237 ' /sys/kernel/debug/gpio 2>/dev/null || true
say rear
readlink -f /sys/bus/i2c/devices/1-0010/driver 2>/dev/null || true
say wifi
ip -br link | grep -E 'wl|wlan|^lo' || true
iw dev 2>/dev/null | grep -E 'Interface|ssid|channel|type' || true
say audio
aplay -l 2>/dev/null || true
arecord -l 2>/dev/null || true
say touch
awk 'BEGIN{RS=""}/Microsoft Surface G6 Touch/{print}' /proc/bus/input/devices || true
say serious-faults
journalctl -k -b --no-pager 2>/dev/null | grep -Ei 'BUG:|Oops:|kernel panic|Unable to handle|Internal error|SError|watchdog: BUG|Call trace:|Missing lane_regs definition' || true
