#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

D=Path(__file__).resolve().parent
R=D.parents[2]
L=R/'experiments/E004-front-ir-vd55g0/e004l-native-bind-only-authority'
K=R/'experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module'
BOOT=Path('/boot/sp11-7.1.5-camera-e004m-native-bind')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004m_native_bind')

def need(v,m):
    if not v: raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

scripts=['prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
         'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh']
for name in scripts:
    subprocess.run(['bash','-n',str(D/name)],check=True)

o=json.load(open(D/'RESULT.json'))
need(o['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(o['attempt_limit']==1 and o['retry_authorized'] is False,'one attempt')
need(o['sensor_module_sha256']=='4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','sensor')
need(o['camss_module_sha256']=='bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba','camss')
need(o['harness_sha256']=='93f947e9737c1472cf11df15b62223d07cae8adb330ebb359d27952172e5a926','harness')
need(o['dtb_sha256']=='dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b','dtb')

l=json.load(open(L/'RESULT.json'))
need(l['status']=='PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY','E004l parent')
need(l['v4l2_contract']['stream_on']=='-EOPNOTSUPP','native stream block')
k=json.load(open(K/'RESULT.json'))
need(k['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k parent')
need(k['parameter_default'] is False,'CAMSS gate default off')

need(sha(D/'e004m_stream_block_test.c')=='7ca3673881ec4e44a67f6198ad484d726cbecf052037750c26883b91651a822f','harness source')
need(sha(D/'Makefile')=='da57916c3a372a599da61421a26588c85e5151d1b45dd4e868f780b9febab014','harness Makefile')
h=(D/'e004m_stream_block_test.c').read_text()
need('bus_find_device_by_name(&i2c_bus_type, NULL, "2-0060")' in h,'exact IR client')
need('v4l2_subdev_call(sd, video, s_stream, 1)' in h,'direct callback')
need('ret == -EOPNOTSUPP' in h,'expected block')

g=(D/'99zzzzzz_sp11_camera_e004m_native_bind').read_text()
for token in ('sp11-camera-e004m-native-bind-one-shot','sp11_camera_e004m_native_bind=1',
              'modprobe.blacklist=qcom_camss,sp11_vd55g0,vd55g0,imx681,ov13858',
              'x1e80100-microsoft-denali-sp11-e004l-native-bind.dtb'):
    need(token in g,'grub token '+token)

run=(D/'run-once.sh').read_text()
need(run.count('insmod "$CAMSS" e004j_ir_dphy_windows_parity=1')==1,'single CAMSS load')
need(run.count('insmod "$SENSOR"')==1,'single sensor load')
need(run.count('insmod "$HARNESS"')==1,'single direct callback harness load')
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count',
            'media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden runtime action '+bad)
need("'E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log" in run,'receiver programming must remain absent')
need("'capture_stream_performed':False" in run and "'illumination_performed':False" in run,'no stream/illumination result')

need(not BOOT.exists(),'candidate boot absent')
need(not ENTRY.exists(),'candidate entry absent')
need('sp11_camera_e004m_native_bind=1' not in Path('/proc/cmdline').read_text(),'not candidate now')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
for m in ('qcom_camss','sp11_vd55g0','e004m_stream_block_test'):
    need(not Path('/sys/module',m).exists(),'module loaded '+m)

print('E004M_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO RUNTIME=NO')
print('E004M_CONTRACT=NATIVE_BIND+GRAPH+CONTROLS+DIRECT_SENSOR_STREAM_BLOCK_ONLY')
print('E004M_CAPTURE_STREAM=NO CAMSS_RECEIVER_PROGRAMMING=NO ILLUMINATION=NO')
