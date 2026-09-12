#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

D=Path(__file__).resolve().parent
R=D.parents[2]
O=D.parent/'e004o-ir-only-graph-authority'
L=D.parent/'e004l-native-bind-only-authority'
K=D.parent/'e004k-csiphy0-dphy-parity-module'
N=D.parent/'e004n-native-bind-runtime-r1'
BOOT=Path('/boot/sp11-7.1.5-camera-e004p-ir-only-bind')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004p_ir_only_bind')

def need(v,m):
    if not v:
        raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

scripts=['prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
         'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh']
for name in scripts:
    subprocess.run(['bash','-n',str(D/name)],check=True)

o=json.load(open(D/'RESULT.json'))
need(o['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(o['attempt_limit']==1 and o['retry_authorized'] is False,'one attempt')
need(o['dtb_sha256']=='fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742','dtb')
need(o['sensor_module_sha256']=='4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','sensor')
need(o['camss_module_sha256']=='bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba','camss')
need(o['harness_module_sha256']=='674e1a79b2fb51046387643716db4d23642134ca8f30600adb30fca8c3ce0a4b','harness')

og=json.load(open(O/'RESULT.json'))
need(og['status']=='PASS_OFFLINE_IR_ONLY_CAMSS_GRAPH_AUTHORITY','E004o authority')
need(og['camss_external_ports']==['port@0'],'IR-only graph')
need(og['rgb_camera_nodes_present'] is False,'RGB nodes removed')
l=json.load(open(L/'RESULT.json'))
need(l['status']=='PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY','E004l authority')
k=json.load(open(K/'RESULT.json'))
need(k['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k authority')
n=json.load(open(N/'RESULT.json'))
need(n['status']=='FAIL_GRAPH_NOTIFIER_INCOMPLETE_NATIVE_SENSOR_PASS_GOLDEN_RETURN_RETIRED','E004n diagnosis')
need(n['sensor_data_writes']==596 and n['media_sensor_entity_links']==0,'E004n proved native sensor but incomplete graph')

need(sha(D/'e004p_stream_block_test.c')=='85ed4e2c021beb1562ce5404d1e7dc12a693aea0787ffc04db43104cb5940ed3','harness source')
need(sha(D/'Makefile')=='9c369bba7184c21b4dc8897330797de67e8531d58ca20d217165834a3813acdb','harness makefile')
h=(D/'e004p_stream_block_test.c').read_text()
for token in (
    'bus_find_device_by_name(&i2c_bus_type, NULL, "2-0060")',
    'V4L2_CID_LINK_FREQ','V4L2_CID_PIXEL_RATE','V4L2_CID_HBLANK','V4L2_CID_VBLANK',
    'v4l2_subdev_call(sd, pad, get_mbus_config, 0, &cfg)',
    'cfg.type != V4L2_MBUS_CSI2_DPHY',
    'cfg.bus.mipi_csi2.num_data_lanes != 1',
    'cfg.link_freq != 420000000LL',
    'v4l2_subdev_call(sd, video, s_stream, 1)',
    'stream_ret != -EOPNOTSUPP',
    'E004P_V4L2_CONTRACT',
    'E004P_STREAM_BLOCK_TEST',
):
    need(token in h,'harness token '+token)

g=(D/'99zzzzzz_sp11_camera_e004p_ir_only_bind').read_text()
for token in (
    'sp11-camera-e004p-ir-only-bind-one-shot',
    'sp11_camera_e004p_ir_only_bind=1',
    '/boot/sp11-7.1.5-camera-e004p-ir-only-bind/',
    'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb',
    'modprobe.blacklist=qcom_camss,sp11_vd55g0,vd55g0,imx681,ov13858',
):
    need(token in g,'GRUB token '+token)

run=(D/'run-once.sh').read_text()
need(run.count('insmod "$CAMSS" e004j_ir_dphy_windows_parity=1')==1,'single CAMSS insertion')
need(run.count('insmod "$SENSOR"')==1,'single sensor insertion')
need(run.count('insmod "$HARNESS"')==1,'single harness insertion')
need(run.count('sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity')==2,
     'privileged CAMSS param reads')
need('sp11-vd55g0 2-0060 \\(1 pad, 1 link, 0 routes\\)' in run,'one-link entity acceptance')
need("'-> \"msm_csiphy0\":0 [ENABLED,IMMUTABLE]' in media" in run,'immutable link acceptance')
need("subdev_node_ok=bool(re.search(r'device node name /dev/v4l-subdev\\d+',media))" in run,'subdev acceptance')
need("type=5 lanes=1 mbus_link_freq=420000000" in run,'actual kernel DPHY enum acceptance')
need("'E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log" in run,'receiver programming must remain absent')
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count',
            'media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden streaming/link action '+bad)
need("'capture_stream_performed':False" in run and "'illumination_performed':False" in run,
     'no capture/illumination result')

need(not BOOT.exists(),'candidate boot absent')
need(not ENTRY.exists(),'candidate entry absent')
need('sp11_camera_e004p_ir_only_bind=1' not in Path('/proc/cmdline').read_text(),'candidate not active')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
for m in ('qcom_camss','sp11_vd55g0','e004p_stream_block_test'):
    need(not Path('/sys/module',m).exists(),'module already loaded '+m)

print('E004P_PREP_VERIFY=PASS FRESH_ONE_SHOT=YES INSTALLED=NO ARMED=NO RUNTIME=NO')
print('E004P_GRAPH_CONTRACT=IR_ONLY ENTITY_LINKS=1 TARGET=CSIPHY0 FLAGS=ENABLED+IMMUTABLE SUBDEV=REQUIRED')
print('E004P_V4L2=LINK420M PIX84M HBLANK556 VBLANK1351 DPHY1 STREAM_BLOCK=-95')
print('E004P_CAPTURE_STREAM=NO RECEIVER_PROGRAMMING=NO ILLUMINATION=NO')
