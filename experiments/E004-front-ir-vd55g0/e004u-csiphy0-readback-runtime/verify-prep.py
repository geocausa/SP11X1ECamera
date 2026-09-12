#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent
P=D.parent
T=P/'e004t-csiphy0-readback-authority'
S=P/'e004s-dynamic-ir-bind-runtime-r4'
K=P/'e004k-csiphy0-dphy-parity-module'
O=P/'e004o-ir-only-graph-authority'
L=P/'e004l-native-bind-only-authority'
BOOT=Path('/boot/sp11-7.1.5-camera-e004u-csiphy0-readback')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004u_csiphy0_readback')

def need(v,m):
    if not v: raise AssertionError(m)

for name in ('prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
             'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh'):
    subprocess.run(['bash','-n',str(D/name)],check=True)

o=json.load(open(D/'RESULT.json'))
need(o['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(o['attempt_limit']==1 and o['retry_authorized'] is False,'one attempt')
need(o['receiver_harness_sha256']=='6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e','harness hash')
need(o['receiver_expected_table_sha256']=='95007de362b9e10d1369dd255c06e0950fced412169de5e83930bb0afec1e770','expected table hash')

tr=json.load(open(T/'RESULT.json'))
need(tr['status']=='PASS_OFFLINE_RECEIVER_ONLY_READBACK_HARNESS_AUTHORITY','E004t authority')
need(tr['expected_register_count']==96 and tr['modeled_windows_matches']==96,'E004t model')
need(tr['sensor_stream_call'] is False and tr['csid_stream_call'] is False and
     tr['vfe_stream_call'] is False and tr['illumination'] is False,'E004t safety')
sr=json.load(open(S/'RESULT.json'))
need(sr['status']=='PASS_DYNAMIC_ID_NATIVE_BIND_GRAPH_CONTROLS_STREAM_BLOCK_GOLDEN_RETURN_RETIRED','E004s authority')
kr=json.load(open(K/'RESULT.json'))
need(kr['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k authority')
need(kr['modeled_windows_receiver_match']=='96/96','E004k 96/96 model')
need(json.load(open(O/'RESULT.json'))['status']=='PASS_OFFLINE_IR_ONLY_CAMSS_GRAPH_AUTHORITY','E004o')
need(json.load(open(L/'RESULT.json'))['status']=='PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY','E004l')

pre=(D/'prearm-check.sh').read_text()
for token in (
    'T=$R/experiments/E004-front-ir-vd55g0/e004t-csiphy0-readback-authority',
    'python3 "$T/verify_e004t.py"',
    'make -C "$B" M="$T" modules',
    'e004t_csiphy_readback_test.ko',
    '6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e',
):
    need(token in pre,'prearm token '+token)

rp=(D/'runtime-preflight.sh').read_text()
need('for p in /sys/bus/i2c/devices/*-0060' in rp,'dynamic client scan')
need('microsoft,sp11-vd55g0' in rp,'compatible identity')
need('e004t_csiphy_readback_test.ko' in rp,'receiver harness hash check')
need('PASS_READY_FOR_RECEIVER_READBACK' in rp,'preflight status')

run=(D/'run-once.sh').read_text()
for token in (
    'HARNESS=$D/build/e004t_csiphy_readback_test.ko',
    'insmod "$CAMSS" e004j_ir_dphy_windows_parity=1',
    'insmod "$SENSOR"',
    'insmod "$HARNESS"',
    'rmmod e004t_csiphy_readback_test',
    'E004J_CSIPHY0_DPHY_WINDOWS_PARITY link_freq=420000000 timer=266666667',
    'E004T_RECEIVER_PRECHECK:',
    'E004T_CSIPHY0_READBACK: expected=96 matches=96 mismatches=0',
    'E004T_RECEIVER_END: result=0 receiver_off=1 csiphy_power_off=1',
    "sensor_stream_not_called='SP11_VD55G0_NATIVE_STREAM_BLOCK' not in log",
    "'E004T_CSIPHY0_MISMATCH' not in log",
    "'E004T_SENSOR_PM_CHANGED' not in log",
    'kernel_fault_or_warn',
):
    need(token in run,'runtime token '+token)

# The wrapper itself may search for forbidden markers, but it must not contain capture/stream commands.
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count',
            'media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden command '+bad)
need('v4l2_subdev_call(sensor_sd' not in run,'wrapper unexpectedly contains kernel sensor call')

g=(D/'99zzzzzz_sp11_camera_e004u_csiphy0_readback').read_text()
for token in (
    'sp11-camera-e004u-csiphy0-readback-one-shot',
    'sp11_camera_e004u_csiphy0_readback=1',
    '/boot/sp11-7.1.5-camera-e004u-csiphy0-readback/',
    'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb',
):
    need(token in g,'GRUB token '+token)

# No fixed adapter identity in operational package.
for name in ('runtime-preflight.sh','run-once.sh','prearm-check.sh','verify-installed.sh',
             'install-candidate.sh','arm-once.sh','golden-return-check.sh','retire-candidate.sh'):
    s=(D/name).read_text()
    need('2-0060' not in s and '3-0060' not in s,'fixed adapter in '+name)

need(not BOOT.exists(),'candidate boot absent')
need(not ENTRY.exists(),'candidate entry absent')
need('sp11_camera_e004u_csiphy0_readback=1' not in Path('/proc/cmdline').read_text(),'candidate active')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
for m in ('qcom_camss','sp11_vd55g0','e004t_csiphy_readback_test','i2c_qcom_cci'):
    need(not Path('/sys/module',m).exists(),'module already loaded '+m)

print('E004U_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO RUNTIME=NO')
print('E004U_NEW_ACTION=CSIPHY0_ONLY POWER+PROGRAM+96_READBACK+OFF')
print('E004U_EXPECT=WINDOWS_96/96 LANE_MASK=0x81 SETTLE=0x10 CTRL7=0x7a')
print('E004U_SENSOR_STREAM=NO CSID_STREAM=NO VFE_STREAM=NO CAPTURE=NO ILLUMINATION=NO')
