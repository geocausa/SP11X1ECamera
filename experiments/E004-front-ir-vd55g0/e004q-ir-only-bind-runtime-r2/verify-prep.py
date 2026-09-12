#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

D=Path(__file__).resolve().parent
P=D.parent/'e004p-ir-only-native-bind-runtime'
O=D.parent/'e004o-ir-only-graph-authority'
L=D.parent/'e004l-native-bind-only-authority'
K=D.parent/'e004k-csiphy0-dphy-parity-module'
BOOT=Path('/boot/sp11-7.1.5-camera-e004q-ir-only-bind-r2')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004q_ir_only_bind_r2')

def need(v,m):
    if not v: raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

for name in ('prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
             'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh'):
    subprocess.run(['bash','-n',str(D/name)],check=True)

o=json.load(open(D/'RESULT.json'))
need(o['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(o['attempt_limit']==1 and o['retry_authorized'] is False,'one attempt')
need(o['dtb_sha256']=='fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742','dtb')
need(o['sensor_module_sha256']=='4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','sensor')
need(o['camss_module_sha256']=='bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba','camss')
need(o['harness_module_sha256']=='a7eeb50a78e50f758d716d875cd01af46ca2e2da6e6cf1c7b38384d49a7b7869','harness')
need(o['notifier_wait']['max_wait_seconds']==10.0 and o['notifier_wait']['read_only'] is True,'wait contract')

p=json.load(open(P/'RESULT.json'))
need(p['status']=='FAIL_ACCEPTANCE_RACE_LATE_GRAPH_PASS_GOLDEN_RETURN_RETIRED','E004p race class')
need(p['late_graph_pass'] is True and p['late_sensor_entity_links']==1,'E004p late graph')
og=json.load(open(O/'RESULT.json'))
need(og['status']=='PASS_OFFLINE_IR_ONLY_CAMSS_GRAPH_AUTHORITY','E004o graph authority')
l=json.load(open(L/'RESULT.json'))
need(l['status']=='PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY','E004l native authority')
k=json.load(open(K/'RESULT.json'))
need(k['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k CAMSS authority')

need(sha(D/'e004q_stream_block_test.c')=='632d783dde3b5d24c4a1941264a7879637d66b3e13701ee74483ccd0740ecd99','harness source')
need(sha(D/'Makefile')=='41928743fcc17e9eca5035752006c58a5e71d234018fd8ae4251e28357a55456','Makefile')
h=(D/'e004q_stream_block_test.c').read_text()
for token in (
 'E004Q_V4L2_CONTRACT',
 'E004Q_STREAM_BLOCK_TEST',
 'V4L2_CID_LINK_FREQ','V4L2_CID_PIXEL_RATE','V4L2_CID_HBLANK','V4L2_CID_VBLANK',
 'cfg.type != V4L2_MBUS_CSI2_DPHY',
 'cfg.bus.mipi_csi2.num_data_lanes != 1',
 'cfg.link_freq != 420000000LL',
 'stream_ret != -EOPNOTSUPP',
):
    need(token in h,'harness token '+token)

g=(D/'99zzzzzz_sp11_camera_e004q_ir_only_bind_r2').read_text()
for token in (
 'sp11-camera-e004q-ir-only-bind-r2-one-shot',
 'sp11_camera_e004q_ir_only_bind_r2=1',
 '/boot/sp11-7.1.5-camera-e004q-ir-only-bind-r2/',
 'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb',
):
    need(token in g,'GRUB token '+token)

run=(D/'run-once.sh').read_text()
need('for _ in $(seq 1 100); do' in run,'bounded wait loop')
need("sleep 0.1" in run,'wait cadence')
need("sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)" in run,'wait entity contract')
need("'-> \"msm_csiphy0\":0 \\[ENABLED,IMMUTABLE\\]'" in run,'wait link contract')
need('GRAPH_READY=1' in run and '[ "$GRAPH_READY" -eq 1 ] || FAIL=1' in run,'wait gate')
need(run.count('insmod "$CAMSS" e004j_ir_dphy_windows_parity=1')==1,'CAMSS load')
need(run.count('insmod "$SENSOR"')==1,'sensor load')
need(run.count('insmod "$HARNESS"')==1,'harness load')
need(run.count('sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity')==2,'CAMSS param privileged')
need("'E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log" in run,'receiver programming absent')
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count','media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden action '+bad)

need(not BOOT.exists(),'candidate boot absent')
need(not ENTRY.exists(),'candidate entry absent')
need('sp11_camera_e004q_ir_only_bind_r2=1' not in Path('/proc/cmdline').read_text(),'candidate active')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
for m in ('qcom_camss','sp11_vd55g0','e004q_stream_block_test'):
    need(not Path('/sys/module',m).exists(),'module already loaded '+m)

print('E004Q_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO RUNTIME=NO')
print('E004Q_DELTA=BOUNDED_READONLY_NOTIFIER_WAIT_ONLY MAX=10S')
print('E004Q_GRAPH=IR_ONLY ONE_IMMUTABLE_LINK_TO_CSIPHY0 SUBDEV_REQUIRED')
print('E004Q_V4L2=LINK420M PIX84M HBLANK556 VBLANK1351 DPHY1 STREAM_BLOCK=-95')
print('E004Q_CAPTURE_STREAM=NO RECEIVER_PROGRAMMING=NO ILLUMINATION=NO')
