#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent
L=D.parent/'e004l-native-bind-only-authority'
CAMSS=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss/camss.c')

def need(v,m):
    if not v:
        raise AssertionError(m)

a=json.load(open(D/'ATTEMPT1-FAILURE.json'))
need(a['status']=='FAIL_BOUNDED_NO_RETRY','attempt status')
need(a['sensor_windows_state_pass'] is True,'native Windows state')
need(a['runtime_suspended'] is True,'sensor runtime suspend')
need(a['camss_e004j_parameter_armed'] is True,'CAMSS parity gate')
need(a['camss_receiver_programming_invoked'] is False,'receiver programming')
need(a['direct_sensor_s_stream_result'] is None,'direct stream callback must not run')
need(a['capture_stream_performed'] is False and a['illumination_performed'] is False,'stream/illumination')
need(a['serious_fault'] is False,'serious fault')

log=(D/'RUNTIME-DMESG.txt').read_text()
for x in (
 'SP11_VD55G0_NATIVE_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0',
 'SP11_VD55G0_NATIVE_STROBE_BASELINE=PASS reg=0x0468 value=0x02 write_authorized=0',
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596 patch=552 safe_config=42 extclk=19200000 mipi=840000000 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_POWER_ON=PASS xclk=19200000 initialized=1 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_POWER_OFF reset_asserted=1 stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_BIND=PASS format=Y10_1X10 size=644x604 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 stream_capable=0 illumination_capable=0',
):
    need(x in log,'missing native PASS '+x)
for bad in ('SP11_VD55G0_NATIVE_STREAM_BLOCK','E004N_STREAM_BLOCK_TEST',
            'E004N_V4L2_CONTRACT','E004J_CSIPHY0_DPHY_WINDOWS_PARITY',
            'STREAM_START','ILLUMINATION_ON'):
    need(bad not in log,'unexpected later-stage marker '+bad)

block=(D/'STREAM-BLOCK.txt').read_text()
need('runtime_status=suspended' in block and 'runtime_usage=0' in block,'runtime PM')
need('camss_e004j_param=Y' in block,'CAMSS parameter')

media=(D/'MEDIA.txt').read_text()
need('sp11-vd55g0 2-0060 (1 pad, 0 link, 0 routes)' in media,'zero-link IR entity')
need('msm_csiphy0' in media,'CSIPHY0 entity')
need('device node name /dev/v4l-subdev' not in media,'subdev nodes unexpectedly registered')

dtb=L/'x1e80100-microsoft-denali-sp11-e004l-native-bind.dtb'
ports=subprocess.check_output(['fdtget','-l',str(dtb),'/soc@0/isp@acb7000/ports'],text=True).split()
need(set(ports)=={'port@0','port@1','port@2'},'E004l CAMSS ports are not IR+rear+front')

c=CAMSS.read_text()
bound=c[c.index('static int camss_subdev_notifier_bound'):c.index('static int camss_subdev_notifier_complete')]
complete=c[c.index('static int camss_subdev_notifier_complete'):c.index('static const struct v4l2_async_notifier_operations')]
need('subdev->host_priv = csiphy;' in bound,'bound callback behavior')
need('media_create_pad_link(sensor, i, input' in complete,'link only in complete')
need('v4l2_device_register_subdev_nodes(&camss->v4l2_dev)' in complete,'subdev nodes only in complete')

need('status=PASS' in (D/'GOLDEN-RETURN.txt').read_text(),'Golden return')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'retired')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'currently Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='FAIL_GRAPH_NOTIFIER_INCOMPLETE_NATIVE_SENSOR_PASS_GOLDEN_RETURN_RETIRED','final result')
need(r['sensor_data_writes']==596 and r['media_sensor_entity_links']==0,'result evidence')
need(r['golden_return_pass'] is True and r['candidate_retired'] is True,'cleanup')

print('E004N_RUNTIME_VERIFY=PASS NATIVE_SENSOR_WINDOWS_STATE=PASS WRITES=596')
print('E004N_GRAPH=FAIL_EXPECTED_CAUSE CAMSS_PORTS=3 SENSOR_ENTITY_LINKS=0 NOTIFIER_COMPLETE=NO')
print('E004N_STREAM_CALLBACK=NO RECEIVER_PROGRAMMING=NO CAPTURE=NO ILLUMINATION=NO')
print('E004N_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES RETRY=NO')
