#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004p-ir-only-native-bind-runtime
K=$R/experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module
SENSOR=$D/build/sp11-vd55g0.ko
HARNESS=$D/build/e004p_stream_block_test.ko
CAMSS=$K/qcom-camss.ko
"$D/runtime-preflight.sh"
date -Ins > "$D/ATTEMPT1-CONSUMED.marker"
BEFORE=$(sudo -n dmesg | wc -l)
FAIL=0

for m in mc videodev v4l2_fwnode v4l2_async videobuf2_common videobuf2_v4l2 videobuf2_dma_sg; do
	sudo -n modprobe "$m" || FAIL=1
done

if [ "$FAIL" -eq 0 ]; then
	sudo -n insmod "$CAMSS" e004j_ir_dphy_windows_parity=1 || FAIL=1
fi
if [ "$FAIL" -eq 0 ]; then
	for _ in $(seq 1 50); do [ -d /sys/module/qcom_camss ] && break; sleep 0.1; done
	[ -d /sys/module/qcom_camss ] || FAIL=1
fi
if [ "$FAIL" -eq 0 ]; then
	P=$(sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity 2>/dev/null || true)
	[ "$P" = "Y" ] || FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
	sudo -n insmod "$SENSOR" || FAIL=1
fi
if [ "$FAIL" -eq 0 ]; then
	for _ in $(seq 1 100); do
		[ -L /sys/bus/i2c/devices/2-0060/driver ] && break
		sleep 0.05
	done
	[ -L /sys/bus/i2c/devices/2-0060/driver ] || FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
	for _ in $(seq 1 100); do
		[ "$(cat /sys/bus/i2c/devices/2-0060/power/runtime_status 2>/dev/null || true)" = "suspended" ] && break
		sleep 0.05
	done
	[ "$(cat /sys/bus/i2c/devices/2-0060/power/runtime_status 2>/dev/null || true)" = "suspended" ] || FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
	MEDIA=
	for x in /dev/media*; do
		[ -e "$x" ] || continue
		if media-ctl -d "$x" -p 2>/dev/null | grep -q 'sp11-vd55g0 2-0060'; then MEDIA="$x"; break; fi
	done
	[ -n "$MEDIA" ] || FAIL=1
fi
if [ "$FAIL" -eq 0 ]; then
	media-ctl -d "$MEDIA" -p > "$D/MEDIA.txt" || FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
	SUBDEV=
	for n in /sys/class/video4linux/v4l-subdev*/name; do
		[ -r "$n" ] || continue
		if grep -q 'sp11-vd55g0 2-0060' "$n"; then SUBDEV="/dev/$(basename "$(dirname "$n")")"; break; fi
	done
	[ -n "$SUBDEV" ] || FAIL=1
fi
if [ "$FAIL" -eq 0 ]; then
	v4l2-ctl -d "$SUBDEV" --list-ctrls-menus > "$D/CONTROLS.txt" || true
fi

if [ "$FAIL" -eq 0 ]; then
	sudo -n insmod "$HARNESS" || FAIL=1
	sleep 0.2
	sudo -n rmmod e004p_stream_block_test 2>/dev/null || true
fi

sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/RUNTIME-DMESG.txt"
{
	echo "runtime_status=$(cat /sys/bus/i2c/devices/2-0060/power/runtime_status 2>/dev/null || echo missing)"
	echo "runtime_usage=$(cat /sys/bus/i2c/devices/2-0060/power/runtime_usage 2>/dev/null || echo missing)"
	echo "runtime_control=$(cat /sys/bus/i2c/devices/2-0060/power/control 2>/dev/null || echo missing)"
	echo "camss_e004j_param=$(sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity 2>/dev/null || echo missing)"
	grep -E 'SP11_VD55G0_NATIVE_STREAM_BLOCK|E004P_STREAM_BLOCK_TEST|E004J_CSIPHY0_DPHY_WINDOWS_PARITY' "$D/RUNTIME-DMESG.txt" || true
} > "$D/STREAM-BLOCK.txt"

python3 - "$FAIL" "$D" <<'PY'
import json,re,sys
from pathlib import Path
pre_fail=int(sys.argv[1]); d=Path(sys.argv[2])
log=(d/'RUNTIME-DMESG.txt').read_text() if (d/'RUNTIME-DMESG.txt').exists() else ''
media=(d/'MEDIA.txt').read_text() if (d/'MEDIA.txt').exists() else ''
ctrl=(d/'CONTROLS.txt').read_text() if (d/'CONTROLS.txt').exists() else ''
block=(d/'STREAM-BLOCK.txt').read_text() if (d/'STREAM-BLOCK.txt').exists() else ''

required_log=[
 'SP11_VD55G0_NATIVE_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0',
 'SP11_VD55G0_NATIVE_STROBE_BASELINE=PASS reg=0x0468 value=0x02 write_authorized=0',
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596 patch=552 safe_config=42 extclk=19200000 mipi=840000000 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_POWER_ON=PASS xclk=19200000 initialized=1 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_BIND=PASS format=Y10_1X10 size=644x604 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 stream_capable=0 illumination_capable=0',
 'SP11_VD55G0_NATIVE_POWER_OFF reset_asserted=1 stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_STREAM_BLOCK=PASS requested=1 reason=E004l_bind_only stream=0 illumination=0',
 'E004P_STREAM_BLOCK_TEST: s_stream(1) ret=-95 expected=-95',
]
missing=[x for x in required_log if x not in log]
sensor_entity_ok=bool(re.search(r'sp11-vd55g0 2-0060 \(1 pad, 1 link, 0 routes\)',media))
link_ok='-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' in media
format_ok='Y10_1X10/644x604' in media
subdev_node_ok=bool(re.search(r'device node name /dev/v4l-subdev\d+',media))
media_ok=sensor_entity_ok and link_ok and format_ok and subdev_node_ok
contract_marker='E004P_V4L2_CONTRACT: link_freq=420000000 pixel_rate=84000000 hblank=556 vblank=1351 mbus_ret=0 type=5 lanes=1 mbus_link_freq=420000000'
controls_ok=contract_marker in log
runtime_suspended='runtime_status=suspended' in block
param_armed='camss_e004j_param=Y' in block
receiver_programming_absent='E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log
serious_fault=bool(re.search(r'(?i)(kernel panic|Call trace:|Oops:|BUG:|SError Interrupt|IOMMU.*fault)',log))
stream_activity=bool(re.search(r'(?i)(STREAM_START|ILLUMINATION_ON)',log))
ok=(pre_fail==0 and not missing and media_ok and controls_ok and runtime_suspended
    and param_armed and receiver_programming_absent and not serious_fault and not stream_activity)
out={
 'schema':'sp11-camera-e004p-native-bind-attempt1-v1',
 'status':'PASS_NATIVE_BIND_GRAPH_CONTROLS_STREAM_BLOCKED' if ok else 'FAIL_BOUNDED_NO_RETRY',
 'precheck_or_load_failure':pre_fail,
 'missing_log_markers':missing,
 'sensor_windows_state_pass':not any('WINDOWS_STATE' in x for x in missing),
 'media_graph_pass':media_ok,
 'sensor_entity_one_link':sensor_entity_ok,
 'immutable_enabled_link_to_csiphy0':link_ok,
 'sensor_format_visible':format_ok,
 'subdev_node_registered':subdev_node_ok,
 'controls_pass':controls_ok,
 'runtime_suspended':runtime_suspended,
 'camss_e004j_parameter_armed':param_armed,
 'camss_receiver_programming_invoked':not receiver_programming_absent,
 'direct_sensor_s_stream_result':'-EOPNOTSUPP' if 'ret=-95 expected=-95' in log else None,
 'capture_stream_performed':False,
 'sensor_stream_register_write_performed':False,
 'illumination_performed':False,
 'serious_fault':serious_fault,
 'retry_authorized':False,
 'next':'reboot to Golden immediately' if ok else 'reboot to Golden and analyze offline',
}
(d/('ATTEMPT1-PASS.json' if ok else 'ATTEMPT1-FAILURE.json')).write_text(json.dumps(out,indent=2)+'\n')
print('E004P_ATTEMPT1='+('PASS' if ok else 'FAIL NO_RETRY'))
print('E004P_GRAPH='+('PASS' if media_ok else 'FAIL')+' ENTITY1LINK='+('YES' if sensor_entity_ok else 'NO')+' LINK='+('YES' if link_ok else 'NO')+' SUBDEV='+('YES' if subdev_node_ok else 'NO')+' FORMAT='+('YES' if format_ok else 'NO')+' CONTROLS='+('PASS' if controls_ok else 'FAIL'))
print('E004P_SENSOR_RUNTIME_SUSPENDED='+('YES' if runtime_suspended else 'NO'))
print('E004P_DIRECT_STREAM_BLOCK='+('PASS' if 'ret=-95 expected=-95' in log else 'FAIL'))
print('E004P_CAMSS_PARITY_PARAM='+('ARMED' if param_armed else 'BAD')+' RECEIVER_PROGRAMMING_INVOKED='+('NO' if receiver_programming_absent else 'YES'))
print('E004P_CAPTURE_STREAM=NO ILLUMINATION=NO')
if missing: print('MISSING='+repr(missing))
sys.exit(0 if ok else 1)
PY
