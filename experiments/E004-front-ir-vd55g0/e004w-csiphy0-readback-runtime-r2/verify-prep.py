#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent
P=D.parent
U=P/'e004u-csiphy0-readback-runtime'
V=P/'e004v-csiphy0-aperture-authority'
T=P/'e004t-csiphy0-readback-authority'
K=P/'e004k-csiphy0-dphy-parity-module'
L=P/'e004l-native-bind-only-authority'
O=P/'e004o-ir-only-graph-authority'
BOOT=Path('/boot/sp11-7.1.5-camera-e004w-csiphy0-readback-r2')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004w_csiphy0_readback_r2')

def need(v,m):
    if not v:
        raise AssertionError(m)

for name in ('prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
             'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh'):
    subprocess.run(['bash','-n',str(D/name)],check=True)

r=json.load(open(D/'RESULT.json'))
need(r['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(r['attempt_limit']==1 and r['retry_authorized'] is False,'one attempt')
need(r['only_behavioral_input_delta']=='DTB CSIPHY0 resource size 0x1000 -> 0x2000','delta')
need(r['dtb_sha256']=='5547a43f06062053c7acdacbf8d6e103233f3d5e3ea7ebc8761bc32fbdcc0009','DTB')
need(r['sensor_module_sha256']=='4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','sensor')
need(r['camss_module_sha256']=='bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba','CAMSS')
need(r['receiver_harness_sha256']=='6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e','harness')

ur=json.load(open(U/'RESULT.json'))
need(ur['status']=='FAIL_CSIPHY0_DT_APERTURE_4K_VS_REQUIRED_8K_GOLDEN_RETURN_RETIRED','E004u diagnosis')
need(ur['attempt_count']==1 and ur['retry_performed'] is False,'E004u bounded')
need(ur['sensor_stream_callback_performed'] is False and ur['illumination_performed'] is False,'E004u safety')
vr=json.load(open(V/'RESULT.json'))
need(vr['status']=='PASS_OFFLINE_CSIPHY0_8K_APERTURE_AUTHORITY','E004v')
need(vr['binary_diff_count']==1 and vr['graph_or_other_dt_change'] is False,'E004v isolation')
need(json.load(open(T/'RESULT.json'))['status']=='PASS_OFFLINE_RECEIVER_ONLY_READBACK_HARNESS_AUTHORITY','E004t')
need(json.load(open(K/'RESULT.json'))['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k')
need(json.load(open(L/'RESULT.json'))['status']=='PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY','E004l')
need(json.load(open(O/'RESULT.json'))['status']=='PASS_OFFLINE_IR_ONLY_CAMSS_GRAPH_AUTHORITY','E004o')

pre=(D/'prearm-check.sh').read_text()
for token in (
    'V=$R/experiments/E004-front-ir-vd55g0/e004v-csiphy0-aperture-authority',
    'python3 "$V/verify_e004v.py"',
    'x1e80100-microsoft-denali-sp11-e004v-ir-csiphy0-8k.dtb',
    '5547a43f06062053c7acdacbf8d6e103233f3d5e3ea7ebc8761bc32fbdcc0009',
    '4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72',
    'bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba',
    '6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e',
):
    need(token in pre,'prearm '+token)

inst=(D/'install-candidate.sh').read_text()
need('V=$R/experiments/E004-front-ir-vd55g0/e004v-csiphy0-aperture-authority' in inst,'install V')
need('x1e80100-microsoft-denali-sp11-e004v-ir-csiphy0-8k.dtb' in inst,'install DT')

vi=(D/'verify-installed.sh').read_text()
need('5547a43f06062053c7acdacbf8d6e103233f3d5e3ea7ebc8761bc32fbdcc0009' in vi,'installed DT hash')

rp=(D/'runtime-preflight.sh').read_text()
need('for p in /sys/bus/i2c/devices/*-0060' in rp,'dynamic I2C scan')
need('microsoft,sp11-vd55g0' in rp,'compatible')
need('PASS_READY_FOR_RECEIVER_READBACK' in rp,'runtime gate')

run=(D/'run-once.sh').read_text()
for token in (
    'insmod "$CAMSS" e004j_ir_dphy_windows_parity=1',
    'insmod "$SENSOR"',
    'insmod "$HARNESS"',
    'E004T_RECEIVER_PRECHECK:',
    'E004J_CSIPHY0_DPHY_WINDOWS_PARITY link_freq=420000000 timer=266666667',
    'E004T_CSIPHY0_READBACK: expected=96 matches=96 mismatches=0',
    'E004T_RECEIVER_END: result=0 receiver_off=1 csiphy_power_off=1',
    "sensor_stream_not_called='SP11_VD55G0_NATIVE_STREAM_BLOCK' not in log",
    "'E004T_CSIPHY0_MISMATCH' not in log",
    "'E004T_SENSOR_PM_CHANGED' not in log",
):
    need(token in run,'runtime '+token)
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count','media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden command '+bad)

g=(D/'99zzzzzz_sp11_camera_e004w_csiphy0_readback_r2').read_text()
for token in (
    'sp11-camera-e004w-csiphy0-readback-r2-one-shot',
    'sp11_camera_e004w_csiphy0_readback_r2=1',
    'x1e80100-microsoft-denali-sp11-e004v-ir-csiphy0-8k.dtb',
):
    need(token in g,'GRUB '+token)

for name in ('runtime-preflight.sh','run-once.sh','prearm-check.sh','verify-installed.sh',
             'install-candidate.sh','arm-once.sh','golden-return-check.sh','retire-candidate.sh'):
    s=(D/name).read_text()
    need('2-0060' not in s and '3-0060' not in s,'fixed adapter '+name)

need(not BOOT.exists(),'candidate boot already exists')
need(not ENTRY.exists(),'candidate entry already exists')
need('sp11_camera_e004w_csiphy0_readback_r2=1' not in Path('/proc/cmdline').read_text(),'candidate active')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
for m in ('qcom_camss','sp11_vd55g0','e004t_csiphy_readback_test','i2c_qcom_cci'):
    need(not Path('/sys/module',m).exists(),'module already active '+m)

print('E004W_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO RUNTIME=NO')
print('E004W_ONLY_DELTA=CSIPHY0_DTB_APERTURE_0x1000_TO_0x2000')
print('E004W_BINARIES=SENSOR_SAME CAMSS_SAME HARNESS_SAME')
print('E004W_EXPECT=RECEIVER_PROGRAMMING+WINDOWS_96/96')
print('E004W_SENSOR_STREAM=NO CSID_STREAM=NO VFE_STREAM=NO CAPTURE=NO ILLUMINATION=NO')
