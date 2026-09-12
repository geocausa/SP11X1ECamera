#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent
K=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source')
API=K/'drivers/media/v4l2-core/v4l2-ctrls-api.c'

def need(v,m):
    if not v: raise AssertionError(m)

a=json.load(open(D/'ATTEMPT1-FAILURE.json'))
need(a['status']=='FAIL_BOUNDED_NO_RETRY','attempt status')
need(a['sensor_windows_state_pass'] is True,'sensor state')
need(a['media_graph_pass'] is True,'graph')
need(a['sensor_entity_one_link'] is True and a['immutable_enabled_link_to_csiphy0'] is True,'link')
need(a['sensor_format_visible'] is True and a['subdev_node_registered'] is True,'format/subdev')
need(a['runtime_suspended'] is True,'runtime PM')
need(a['camss_e004j_parameter_armed'] is True,'CAMSS parameter')
need(a['camss_receiver_programming_invoked'] is False,'receiver programming')
need(a['direct_sensor_s_stream_result']=='-EOPNOTSUPP','direct stream refusal')
need(a['capture_stream_performed'] is False and a['illumination_performed'] is False,'stream/illumination')

log=(D/'RUNTIME-DMESG.txt').read_text()
need('E004Q_V4L2_CONTRACT: link_freq=0 pixel_rate=84000000 hblank=0 vblank=0 mbus_ret=0 type=5 lanes=1 mbus_link_freq=420000000' in log,
     'harness observed contract')
need('SP11_VD55G0_NATIVE_STREAM_BLOCK=PASS requested=1 reason=E004l_bind_only stream=0 illumination=0' in log,
     'sensor stream block')
need('E004Q_STREAM_BLOCK_TEST: s_stream(1) ret=-95 expected=-95' in log,'harness stream result')
need(log.count('WARNING: drivers/media/v4l2-core/v4l2-ctrls-api.c:901 at v4l2_ctrl_g_ctrl_int64')==3,
     'expected three wrong-accessor WARNs')
need('E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log,'receiver programming marker')
need('STREAM_START' not in log and 'ILLUMINATION_ON' not in log,'stream/illumination markers')

media=(D/'MEDIA.txt').read_text()
need('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)' in media,'one-link entity')
need('-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' in media,'immutable link')
need('device node name /dev/v4l-subdev' in media,'subdev')
need('fmt:Y10_1X10/644x604' in media,'format')

ctrl=(D/'CONTROLS.txt').read_text()
for x in ('vertical_blanking','value=1351','horizontal_blanking','value=556',
          '420000000','pixel_rate','value=84000000'):
    need(x in ctrl,'control '+x)

src=(D/'e004q_stream_block_test.c').read_text()
need(src.count('v4l2_ctrl_g_ctrl_int64(')==4,'consumed harness accessor pattern')
api=API.read_text()
g64=api[api.index('s64 v4l2_ctrl_g_ctrl_int64'):api.index('EXPORT_SYMBOL(v4l2_ctrl_g_ctrl_int64)')]
need('ctrl->type != V4L2_CTRL_TYPE_INTEGER64' in g64,'kernel int64 guard')
g32=api[api.index('s32 v4l2_ctrl_g_ctrl('):api.index('EXPORT_SYMBOL(v4l2_ctrl_g_ctrl)')]
need('WARN_ON(!ctrl->is_int)' in g32,'kernel integer accessor')

need('status=PASS' in (D/'GOLDEN-RETURN.txt').read_text(),'Golden return')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'retired')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'currently Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='FAIL_HARNESS_ACCESSOR_WARN_GRAPH_AND_STREAM_BLOCK_PASS_GOLDEN_RETURN_RETIRED','result')
need(r['media_graph_pass'] is True and r['direct_sensor_stream_result']=='-EOPNOTSUPP','core pass')
need(r['golden_return_pass'] is True and r['candidate_retired'] is True,'cleanup')

print('E004Q_RUNTIME_VERIFY=PASS GRAPH=PASS DIRECT_STREAM_BLOCK=-95')
print('E004Q_CONTROLS_USERSPACE=420M/84M/H556/V1351 MBUS=DPHY1@420M')
print('E004Q_FAILURE_CLASS=HARNESS_WRONG_V4L2_ACCESSOR WARNS=3 CAMERA_STACK_FAULT=NO')
print('E004Q_RECEIVER_PROGRAMMING=NO CAPTURE=NO ILLUMINATION=NO')
print('E004Q_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES RETRY=NO')
