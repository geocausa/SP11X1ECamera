#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent
R=D.parents[2]
E=R/'experiments/E004-front-ir-vd55g0/e004h-safe42-config-authority'
BOOT=Path('/boot/sp11-7.1.5-camera-e004i-config42')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004i_config42')

def need(v,m):
    if not v: raise AssertionError(m)

scripts=['prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
         'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh']
for name in scripts:
    subprocess.run(['bash','-n',str(D/name)],check=True)

o=json.load(open(D/'RESULT.json'))
need(o['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(o['attempt_limit']==1 and o['retry_authorized'] is False,'one attempt')
need(o['dtb_sha256']=='e29c787acf9e2f1330a4e73fd8014aba118a2f0a59be51c86859a9ab7fed4ef2','DT hash')
need(o['module_sha256']=='75eccb1ac7a8a5f247ec03a9f56339527d2dcd7cfab77450b3ba1f8efe563c5c','module hash')
need(o['safe42_sha256']=='159647774f45331210044d0680e50bf16e8aaeeb8c3e98449d2cef7adeffacb2','safe42 hash')

e=json.load(open(E/'RESULT.json'))
need(e['status']=='PASS_OFFLINE_SAFE42_WINDOWS_CONFIG_AUTHORITY','E004h parent')
need(e['expected_total_sensor_data_writes']==596,'write count authority')
need(e['safe_final_config_writes']==42,'safe42 count')
need(e['isolated_strobe']['register']=='0x0468' and e['isolated_strobe']['writes_authorized'] is False,'strobe isolated')

g=(D/'99zzzzzz_sp11_camera_e004i_config42').read_text()
for token in ('sp11-camera-e004i-config42-one-shot','sp11_camera_e004i_config42=1',
              'modprobe.blacklist=qcom_camss,imx681,ov13858,vd55g0,sp11_vd55g0_config42probe',
              '/boot/sp11-7.1.5-camera-e004i-config42/'):
    need(token in g,'grub token '+token)

run=(D/'run-once.sh').read_text()
need(run.count('insmod "$KO"')==1,'single insmod')
need(run.index('ATTEMPT1-CONSUMED.marker') < run.index('insmod "$KO"'),'consume before insmod')
for token in ('writes=596','safe_config_writes=42','isolated_strobe_writes=0',
              'STROBE_ISOLATION_BEFORE','STROBE_ISOLATION_AFTER','READBACK=PASS',
              'stream=0 illumination=0'):
    need(token in run,'acceptance token '+token)
for bad in ('v4l2-ctl','media-ctl','gst-launch','ffmpeg','request_firmware'):
    need(bad not in run,'forbidden runtime tool '+bad)

need(not BOOT.exists(),'candidate boot absent')
need(not ENTRY.exists(),'candidate entry absent')
need('sp11_camera_e004i_config42=1' not in Path('/proc/cmdline').read_text(),'not candidate now')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden default/no next')
print('E004I_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO ATTEMPT=NO')
print('E004I_CONTRACT=ONE_SHOT WRITES=596 SAFE42=42 STROBE_WRITES=0 READBACK=REQUIRED STREAM=NO ILLUMINATION=NO')
