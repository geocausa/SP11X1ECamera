#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent

def need(v,m):
    if not v: raise AssertionError(m)

a=json.load(open(D/'ATTEMPT1-FAILURE.json'))
need(a['status']=='FAIL_BOUNDED_NO_RETRY','attempt status')
need(a['sensor_windows_state_pass'] is True,'sensor Windows state')
need(a['runtime_suspended'] is True,'runtime suspend')
need(a['camss_e004j_parameter_armed'] is True,'CAMSS parameter')
need(a['camss_receiver_programming_invoked'] is False,'receiver programming')
need(a['direct_sensor_s_stream_result'] is None,'direct stream callback')
need(a['capture_stream_performed'] is False and a['illumination_performed'] is False,'stream/illumination')

late=(D/'LATE-MEDIA.txt').read_text()
need('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)' in late,'late one-link sensor entity')
need('-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' in late,'late immutable CSIPHY0 link')
need('device node name /dev/v4l-subdev25' in late,'late sensor subdev')
need('fmt:Y10_1X10/644x604' in late,'late sensor format')

diag=(D/'LATE-DIAG.txt').read_text()
need('subdev=/dev/v4l-subdev25' in diag,'late subdev diag')
need('runtime_status=suspended' in diag and 'runtime_usage=0' in diag,'late runtime PM')
need('camss_e004j_param=Y' in diag,'late CAMSS param')

ctrl=(D/'LATE-CONTROLS.txt').read_text()
for x in ('vertical_blanking','value=1351','horizontal_blanking','value=556',
          '420000000','pixel_rate','value=84000000'):
    need(x in ctrl,'late control '+x)

log=(D/'RUNTIME-DMESG.txt').read_text()
for x in (
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596',
 'SP11_VD55G0_NATIVE_BIND=PASS format=Y10_1X10 size=644x604',
):
    need(x in log,'native pass '+x)
for bad in ('SP11_VD55G0_NATIVE_STREAM_BLOCK','E004P_STREAM_BLOCK_TEST',
            'E004J_CSIPHY0_DPHY_WINDOWS_PARITY','STREAM_START','ILLUMINATION_ON'):
    need(bad not in log,'unexpected runtime marker '+bad)

need('status=PASS' in (D/'GOLDEN-RETURN.txt').read_text(),'Golden return')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'retired')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'currently Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='FAIL_ACCEPTANCE_RACE_LATE_GRAPH_PASS_GOLDEN_RETURN_RETIRED','result status')
need(r['late_graph_pass'] is True and r['late_sensor_entity_links']==1,'late graph result')
need(r['golden_return_pass'] is True and r['candidate_retired'] is True,'cleanup')

print('E004P_RUNTIME_VERIFY=PASS CLASS=ACCEPTANCE_RACE LATE_GRAPH=PASS')
print('E004P_LATE_GRAPH=SENSOR1LINK->CSIPHY0 ENABLED+IMMUTABLE SUBDEV25 Y10_644x604')
print('E004P_CONTROLS=LINK420M PIX84M HBLANK556 VBLANK1351 RUNTIME_SUSPENDED=YES')
print('E004P_STREAM_CALLBACK=NO RECEIVER_PROGRAMMING=NO CAPTURE=NO ILLUMINATION=NO')
print('E004P_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES RETRY=NO')
