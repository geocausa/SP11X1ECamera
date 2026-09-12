#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

D=Path(__file__).resolve().parent
R=D.parents[2]
M=D.parent/'e004m-native-bind-runtime'
L=D.parent/'e004l-native-bind-only-authority'
K=D.parent/'e004k-csiphy0-dphy-parity-module'
BOOT=Path('/boot/sp11-7.1.5-camera-e004n-native-bind-r1')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004n_native_bind_r1')

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
need(o['e004m_permission_bug_fixed'] is True,'permission fix declared')
need(o['sensor_module_sha256']=='4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','sensor hash')
need(o['camss_module_sha256']=='bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba','camss hash')
need(o['harness_module_sha256']=='57c2dea17bf0a6f1efed628eb13e53b9b7e12d2f89493e68c14edeaa6f0a8fcb','harness hash')
need(o['dtb_sha256']=='dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b','dtb hash')

m=json.load(open(M/'RESULT.json'))
need(m['status']=='FAIL_SAFE_PRE_SENSOR_CAMSS_PARAM_PERMISSION_GOLDEN_RETURN_RETIRED','E004m failure class')
need(m['sensor_data_writes']==0 and m['candidate_retired'] is True,'E004m safely retired')
l=json.load(open(L/'RESULT.json'))
need(l['status']=='PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY','E004l authority')
k=json.load(open(K/'RESULT.json'))
need(k['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k authority')

need(sha(D/'e004n_stream_block_test.c')=='29dbab0637fed647230047e750c5f3a5b916cfb73a2c5e70d6303a2ae64bf440','harness source')
need(sha(D/'Makefile')=='c98903763482bed97d8583fdf62b2b9ca1fd9b514bffa2bff79fae436bfa3b0f','harness makefile')
h=(D/'e004n_stream_block_test.c').read_text()
for token in (
 'bus_find_device_by_name(&i2c_bus_type, NULL, "2-0060")',
 'V4L2_CID_LINK_FREQ','V4L2_CID_PIXEL_RATE','V4L2_CID_HBLANK','V4L2_CID_VBLANK',
 'v4l2_subdev_call(sd, pad, get_mbus_config, 0, &cfg)',
 'cfg.type != V4L2_MBUS_CSI2_DPHY',
 'cfg.bus.mipi_csi2.num_data_lanes != 1',
 'cfg.link_freq != 420000000LL',
 'v4l2_subdev_call(sd, video, s_stream, 1)',
 'stream_ret != -EOPNOTSUPP',
 'E004N_V4L2_CONTRACT',
 'E004N_STREAM_BLOCK_TEST',
):
    need(token in h,'harness token '+token)

g=(D/'99zzzzzz_sp11_camera_e004n_native_bind_r1').read_text()
for token in (
 'sp11-camera-e004n-native-bind-r1-one-shot',
 'sp11_camera_e004n_native_bind_r1=1',
 '/boot/sp11-7.1.5-camera-e004n-native-bind-r1/',
 'modprobe.blacklist=qcom_camss,sp11_vd55g0,vd55g0,imx681,ov13858',
):
    need(token in g,'GRUB token '+token)

run=(D/'run-once.sh').read_text()
need(run.count('insmod "$CAMSS" e004j_ir_dphy_windows_parity=1')==1,'single CAMSS insertion')
need(run.count('insmod "$SENSOR"')==1,'single sensor insertion')
need(run.count('insmod "$HARNESS"')==1,'single harness insertion')
priv='sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity'
need(run.count(priv)==2,'both CAMSS parameter reads must be privileged')
plain='$(cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity'
need(plain not in run,'unprivileged E004m parameter read regression')
need("type=5 lanes=1 mbus_link_freq=420000000" in run,'actual kernel DPHY enum acceptance')
need("'E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log" in run,'receiver programming absent gate')
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count',
            'media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden streaming/link action '+bad)
need("'capture_stream_performed':False" in run and "'illumination_performed':False" in run,'no stream/illumination result')

for p in D.glob('*.sh'):
    need('e004n-native-bind-runtime-r1' in p.read_text(),'r1 directory missing from '+p.name)
need(not BOOT.exists(),'candidate boot must be absent')
need(not ENTRY.exists(),'candidate entry must be absent')
need('sp11_camera_e004n_native_bind_r1=1' not in Path('/proc/cmdline').read_text(),'candidate must not be active')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
for mname in ('qcom_camss','sp11_vd55g0','e004n_stream_block_test'):
    need(not Path('/sys/module',mname).exists(),'module already loaded '+mname)

print('E004N_PREP_VERIFY=PASS FRESH_ONE_SHOT=YES INSTALLED=NO ARMED=NO RUNTIME=NO')
print('E004N_PERMISSION_FIX=PASS CAMSS_PARAM_READS=SUDO_2/2')
print('E004N_HARNESS=LINK420M PIX84M HBLANK556 VBLANK1351 DPHY1 STREAM_BLOCK=-95')
print('E004N_CAPTURE_STREAM=NO RECEIVER_PROGRAMMING=NO ILLUMINATION=NO')
