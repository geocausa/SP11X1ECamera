#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004u-csiphy0-readback-runtime
K=$R/experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module
SENSOR=$D/build/sp11-vd55g0.ko
HARNESS=$D/build/e004t_csiphy_readback_test.ko
CAMSS=$K/qcom-camss.ko

"$D/runtime-preflight.sh"
CLIENT_PATH=$(sed -n 's/^i2c_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt")
CLIENT_NAME=$(sed -n 's/^i2c_client_name=//p' "$D/RUNTIME-PREFLIGHT.txt")
[ -n "$CLIENT_PATH" ] && [ -n "$CLIENT_NAME" ]
[ "$(basename "$CLIENT_PATH")" = "$CLIENT_NAME" ]
[[ "$CLIENT_NAME" =~ ^[0-9]+-0060$ ]]
[ "$(tr -d '\0' < "$CLIENT_PATH/of_node/compatible")" = 'microsoft,sp11-vd55g0' ]
SENSOR_NAME="sp11-vd55g0 $CLIENT_NAME"

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
		[ -L "$CLIENT_PATH/driver" ] && break
		sleep 0.05
	done
	[ -L "$CLIENT_PATH/driver" ] || FAIL=1
fi
if [ "$FAIL" -eq 0 ]; then
	for _ in $(seq 1 100); do
		[ "$(cat "$CLIENT_PATH/power/runtime_status" 2>/dev/null || true)" = "suspended" ] && break
		sleep 0.05
	done
	[ "$(cat "$CLIENT_PATH/power/runtime_status" 2>/dev/null || true)" = "suspended" ] || FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
	MEDIA=
	SUBDEV=
	GRAPH_READY=0
	for _ in $(seq 1 100); do
		SUBDEV=
		for n in /sys/class/video4linux/v4l-subdev*/name; do
			[ -r "$n" ] || continue
			if grep -Fxq "$SENSOR_NAME" "$n"; then
				SUBDEV="/dev/$(basename "$(dirname "$n")")"
				break
			fi
		done
		MEDIA=
		for x in /dev/media*; do
			[ -e "$x" ] || continue
			TMP=/tmp/e004u-media-probe.txt
			if media-ctl -d "$x" -p > "$TMP" 2>/dev/null &&
			   grep -Fq "$SENSOR_NAME (1 pad, 1 link, 0 routes)" "$TMP" &&
			   grep -q -- '-> "msm_csiphy0":0 \[ENABLED,IMMUTABLE\]' "$TMP"; then
				MEDIA="$x"
				cp "$TMP" "$D/MEDIA.txt"
				break
			fi
		done
		if [ -n "$MEDIA" ] && [ -n "$SUBDEV" ]; then
			GRAPH_READY=1
			break
		fi
		sleep 0.1
	done
	[ "$GRAPH_READY" -eq 1 ] || FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
	v4l2-ctl -d "$SUBDEV" --list-ctrls-menus > "$D/CONTROLS.txt" || true
fi

# Receiver-only action. The E004t harness independently requires:
# sensor runtime-suspended, CSIPHY0 D-PHY lane0, and no enabled CSIPHY0->CSID link.
if [ "$FAIL" -eq 0 ]; then
	[ "$(cat "$CLIENT_PATH/power/runtime_status" 2>/dev/null || true)" = "suspended" ] || FAIL=1
fi
if [ "$FAIL" -eq 0 ]; then
	sudo -n insmod "$HARNESS" || FAIL=1
	sleep 0.2
	sudo -n rmmod e004t_csiphy_readback_test 2>/dev/null || true
fi

sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/RUNTIME-DMESG.txt"
{
	echo "i2c_client_name=$CLIENT_NAME"
	echo "i2c_client_path=$CLIENT_PATH"
	echo "runtime_status=$(cat "$CLIENT_PATH/power/runtime_status" 2>/dev/null || echo missing)"
	echo "runtime_usage=$(cat "$CLIENT_PATH/power/runtime_usage" 2>/dev/null || echo missing)"
	echo "runtime_control=$(cat "$CLIENT_PATH/power/control" 2>/dev/null || echo missing)"
	echo "camss_e004j_param=$(sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity 2>/dev/null || echo missing)"
	grep -E 'E004J_CSIPHY0_DPHY_WINDOWS_PARITY|E004T_RECEIVER_PRECHECK|E004T_CSIPHY0_READBACK|E004T_CSIPHY0_MISMATCH|E004T_SENSOR_PM_CHANGED|E004T_RECEIVER_END|SP11_VD55G0_NATIVE_STREAM_BLOCK' "$D/RUNTIME-DMESG.txt" || true
} > "$D/RECEIVER-READBACK.txt"

python3 - "$FAIL" "$D" "$CLIENT_NAME" <<'PY'
import json,re,sys
from pathlib import Path
pre_fail=int(sys.argv[1]); d=Path(sys.argv[2]); client_name=sys.argv[3]
sensor_name=f'sp11-vd55g0 {client_name}'
log=(d/'RUNTIME-DMESG.txt').read_text() if (d/'RUNTIME-DMESG.txt').exists() else ''
media=(d/'MEDIA.txt').read_text() if (d/'MEDIA.txt').exists() else ''
ctrl=(d/'CONTROLS.txt').read_text() if (d/'CONTROLS.txt').exists() else ''
rb=(d/'RECEIVER-READBACK.txt').read_text() if (d/'RECEIVER-READBACK.txt').exists() else ''

native_required=[
 'SP11_VD55G0_NATIVE_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0',
 'SP11_VD55G0_NATIVE_STROBE_BASELINE=PASS reg=0x0468 value=0x02 write_authorized=0',
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596 patch=552 safe_config=42 extclk=19200000 mipi=840000000 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_POWER_ON=PASS xclk=19200000 initialized=1 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_POWER_OFF reset_asserted=1 stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_BIND=PASS format=Y10_1X10 size=644x604 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 stream_capable=0 illumination_capable=0',
]
missing=[x for x in native_required if x not in log]

precheck=(
 f'E004T_RECEIVER_PRECHECK: sensor={client_name} sensor_pm=suspended '
 'csiphy=msm_csiphy0 id=0 phy=DPHY lanes=1 lane0_pos=0 downstream_link=none '
 'fmt=Y10_1X10/644x604'
)
e004j=(
 'E004J_CSIPHY0_DPHY_WINDOWS_PARITY link_freq=420000000 timer=266666667 '
 'lane_mask=0x81 settle=0x10 ctrl11_21=ff,fe,e6,df,df,fc,fb,9b,7f,bf,ff'
)
readback=(
 'E004T_CSIPHY0_READBACK: expected=96 matches=96 mismatches=0 '
 'timer_clk_rate=266666667 lane_mask_reg=0x00000081 settle_lane0=0x00000010 '
 'common_ctrl7=0x0000007a'
)
end=(
 'E004T_RECEIVER_END: result=0 receiver_off=1 csiphy_power_off=1 '
 'sensor_pm_suspended=1 sensor_stream_call=0 csid_stream_call=0 '
 'vfe_stream_call=0 illumination=0'
)

sensor_entity_ok=f'{sensor_name} (1 pad, 1 link, 0 routes)' in media
link_ok='-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' in media
format_ok='Y10_1X10/644x604' in media
subdev_ok=bool(re.search(r'device node name /dev/v4l-subdev\d+',media))
controls_ok=all(x in ctrl for x in ('value=1351','value=556','420000000','value=84000000'))
precheck_ok=precheck in log
e004j_ok=e004j in log
readback_ok=readback in log
end_ok=end in log
runtime_suspended='runtime_status=suspended' in rb and 'runtime_usage=0' in rb
param_armed='camss_e004j_param=Y' in rb
no_mismatch='E004T_CSIPHY0_MISMATCH' not in log
sensor_stream_not_called='SP11_VD55G0_NATIVE_STREAM_BLOCK' not in log
sensor_pm_unchanged='E004T_SENSOR_PM_CHANGED' not in log
kernel_fault_or_warn=bool(re.search(r'(?i)(WARNING:|Call trace:|Oops:|BUG:|SError Interrupt|IOMMU.*fault)',log))
forbidden_activity=bool(re.search(r'(?i)(STREAM_START|ILLUMINATION_ON)',log))

ok=(pre_fail==0 and not missing and sensor_entity_ok and link_ok and format_ok and subdev_ok
    and controls_ok and precheck_ok and e004j_ok and readback_ok and end_ok
    and runtime_suspended and param_armed and no_mismatch and sensor_stream_not_called
    and sensor_pm_unchanged and not kernel_fault_or_warn and not forbidden_activity)

out={
 'schema':'sp11-camera-e004u-csiphy0-readback-attempt1-v1',
 'status':'PASS_CSIPHY0_WINDOWS_96_OF_96_RECEIVER_ONLY' if ok else 'FAIL_BOUNDED_NO_RETRY',
 'precheck_or_load_failure':pre_fail,
 'discovered_i2c_client':client_name,
 'missing_native_markers':missing,
 'sensor_windows_state_pass':not any('WINDOWS_STATE' in x for x in missing),
 'sensor_data_writes':596 if not missing else None,
 'sensor_runtime_suspended_before_receiver':precheck_ok,
 'media_graph_pass':sensor_entity_ok and link_ok and format_ok and subdev_ok,
 'controls_pass':controls_ok,
 'camss_e004j_parameter_armed':param_armed,
 'receiver_programming_marker_pass':e004j_ok,
 'receiver_expected_registers':96,
 'receiver_register_matches':96 if readback_ok else None,
 'receiver_register_mismatches':0 if readback_ok else None,
 'receiver_readback_pass':readback_ok,
 'receiver_powered_off':end_ok,
 'sensor_runtime_suspended_after_receiver':runtime_suspended and end_ok,
 'sensor_stream_callback_performed':not sensor_stream_not_called,
 'csid_stream_callback_performed':False,
 'vfe_stream_callback_performed':False,
 'capture_stream_performed':False,
 'illumination_performed':False,
 'kernel_fault_or_warning':kernel_fault_or_warn,
 'retry_authorized':False,
 'next':'reboot to Golden immediately' if ok else 'reboot to Golden and analyze offline',
}
(d/('ATTEMPT1-PASS.json' if ok else 'ATTEMPT1-FAILURE.json')).write_text(json.dumps(out,indent=2)+'\n')

print('E004U_ATTEMPT1='+('PASS' if ok else 'FAIL NO_RETRY'))
print('E004U_NATIVE_SENSOR_STATE='+('PASS' if not missing else 'FAIL')+' RUNTIME_SUSPENDED='+('YES' if runtime_suspended else 'NO'))
print('E004U_RECEIVER_PRECHECK='+('PASS' if precheck_ok else 'FAIL'))
print('E004U_E004J_PROGRAMMING='+('PASS' if e004j_ok else 'FAIL'))
print('E004U_CSIPHY0_READBACK='+('PASS 96/96' if readback_ok else 'FAIL'))
print('E004U_RECEIVER_OFF='+('YES' if end_ok else 'NO')+' SENSOR_STREAM_CALL='+('NO' if sensor_stream_not_called else 'YES'))
print('E004U_KERNEL_WARN_OR_FAULT='+('YES' if kernel_fault_or_warn else 'NO'))
print('E004U_CAPTURE=NO ILLUMINATION=NO')
if missing: print('MISSING_NATIVE='+repr(missing))
sys.exit(0 if ok else 1)
PY
