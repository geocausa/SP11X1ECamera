#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent
R=D.parents[2]
E=R/'experiments/E004-front-ir-vd55g0/e004e-linux-prefixprobe-authority'
BOOT=Path('/boot/sp11-7.1.5-camera-e004f-prefixprobe')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004f_prefixprobe')

def need(v,m):
    if not v: raise AssertionError(m)

scripts=['prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
         'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh']
for name in scripts:
    subprocess.run(['bash','-n',str(D/name)],check=True)

o=json.load(open(D/'RESULT.json'))
need(o['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(o['attempt_limit']==1 and o['retry_authorized'] is False,'one attempt')
need(o['dtb_sha256']=='d05c4d50a4e2aaaff2216aa765802578c78551d97217cd3e422c9eda6a9c95e9','DT hash')
need(o['module_sha256']=='b257ca820cface72f4d2d28836f3621d8620c2284e23405ce519c26dd3160b1b','module hash')

e=json.load(open(E/'RESULT.json'))
need(e['status']=='PASS_OFFLINE_E004E_SURFACE_PATCH_BOOT_PREFIX_AUTHORITY','E004e parent')
need(e['sensor_data_write_count_if_successful']==554,'write count authority')
need(e['final_43_windows_config_writes'] is False and e['sensor_gpio1_strobe_configured'] is False,'no final/strobe')

g=(D/'99zzzzzz_sp11_camera_e004f_prefixprobe').read_text()
for token in ('sp11-camera-e004f-prefixprobe-one-shot','sp11_camera_e004f_prefixprobe=1',
              'modprobe.blacklist=qcom_camss,imx681,ov13858,vd55g0,sp11_vd55g0_prefixprobe',
              '/boot/sp11-7.1.5-camera-e004f-prefixprobe/'):
    need(token in g,'grub token '+token)

run=(D/'run-once.sh').read_text()
need(run.count('insmod "$KO"')==1,'single insmod')
need(run.index('ATTEMPT1-CONSUMED.marker') < run.index('insmod "$KO"'),'consume before insmod')
for token in ('writes=554','patch_writes=552','final_config_writes=0','final_state=SW_STBY','stream=0 illumination=0'):
    need(token in run,'acceptance token '+token)
for bad in ('v4l2-ctl','media-ctl','gst-launch','ffmpeg','request_firmware'):
    need(bad not in run,'forbidden runtime tool '+bad)

need(not BOOT.exists(),'candidate boot absent')
need(not ENTRY.exists(),'candidate entry absent')
need('sp11_camera_e004f_prefixprobe=1' not in Path('/proc/cmdline').read_text(),'not candidate now')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden default/no next')
print('E004F_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO ATTEMPT=NO')
print('E004F_CONTRACT=ONE_SHOT WRITES=554 FINAL_CONFIG=NO STROBE_CONFIG=NO STREAM=NO ILLUMINATION=NO')
