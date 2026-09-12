#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, shutil, subprocess, tempfile

D=Path(__file__).resolve().parent
R=D.parents[2]
RR=D.parent/'e004r-ir-only-bind-runtime-r3'
Q=D.parent/'e004q-ir-only-bind-runtime-r2'
O=D.parent/'e004o-ir-only-graph-authority'
L=D.parent/'e004l-native-bind-only-authority'
K=D.parent/'e004k-csiphy0-dphy-parity-module'
BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
BOOT=Path('/boot/sp11-7.1.5-camera-e004s-dynamic-ir-bind-r4')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004s_dynamic_ir_bind_r4')

def need(v,m):
    if not v:
        raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

for name in ('prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
             'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh'):
    subprocess.run(['bash','-n',str(D/name)],check=True)

o=json.load(open(D/'RESULT.json'))
need(o['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(o['attempt_limit']==1 and o['retry_authorized'] is False,'one attempt')
need(o['only_behavioral_delta']=='adapter-independent physical IR device discovery','delta')
need(o['dtb_sha256']=='fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742','dtb')
need(o['sensor_module_sha256']=='4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','sensor')
need(o['camss_module_sha256']=='bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba','camss')
need(o['harness_module_sha256']=='f1cd5f44504251224253939f509c95c1ef86c603ba19002c0dce1f3314cfab57','harness')

rr=json.load(open(RR/'RESULT.json'))
need(rr['status']=='ABORT_PRE_ATTEMPT_I2C_ADAPTER_NUMBER_DRIFT_GOLDEN_RETURN_RETIRED','E004r class')
need(rr['camera_attempt_started'] is False and rr['sensor_data_writes']==0,'E004r safe abort')
q=json.load(open(Q/'RESULT.json'))
need(q['status']=='FAIL_HARNESS_ACCESSOR_WARN_GRAPH_AND_STREAM_BLOCK_PASS_GOLDEN_RETURN_RETIRED','E004q graph/stream proof')
need(q['media_graph_pass'] is True and q['direct_sensor_stream_result']=='-EOPNOTSUPP','E004q core proof')
og=json.load(open(O/'RESULT.json'))
need(og['status']=='PASS_OFFLINE_IR_ONLY_CAMSS_GRAPH_AUTHORITY','E004o graph')
l=json.load(open(L/'RESULT.json'))
need(l['status']=='PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY','E004l sensor')
k=json.load(open(K/'RESULT.json'))
need(k['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k CAMSS')

need(sha(D/'e004s_stream_block_test.c')=='a2a9fd22285cffeb8bb31c71319debc76a6128d8dccc5c7b1b0ead02b9ff26b3','harness source')
need(sha(D/'Makefile')=='79feb96cf22395cfaa95e23d26086d91d250ae4a6e669b094a08ec073781cd35','Makefile')
h=(D/'e004s_stream_block_test.c').read_text()
for token in (
    'of_find_compatible_node(NULL, NULL, E004S_COMPAT)',
    'bus_find_device_by_of_node(&i2c_bus_type, np)',
    'client->addr != E004S_ADDR',
    '#define E004S_COMPAT "microsoft,sp11-vd55g0"',
    '#define E004S_ADDR 0x60',
    'E004S_DEVICE_IDENTITY',
    'link_idx = v4l2_ctrl_g_ctrl(link);',
    'pixel_val = v4l2_ctrl_g_ctrl_int64(pixel);',
    'hblank_val = v4l2_ctrl_g_ctrl(hblank);',
    'vblank_val = v4l2_ctrl_g_ctrl(vblank);',
    'E004S_V4L2_CONTRACT',
    'E004S_STREAM_BLOCK_TEST',
    'stream_ret != -EOPNOTSUPP',
):
    need(token in h,'harness token '+token)
need('bus_find_device_by_name' not in h,'name-based kernel lookup regression')
need('2-0060' not in h and '3-0060' not in h,'literal bus number in harness')

rp=(D/'runtime-preflight.sh').read_text()
for token in (
    'for p in /sys/bus/i2c/devices/*-0060',
    'tr -d',
    'microsoft,sp11-vd55g0',
    'i2c_client_path=$DEV',
    'i2c_client_name=$CLIENT',
    'i2c_address=0x60',
    'dynamic_i2c_client_not_unique',
):
    need(token in rp,'preflight token '+token)

run=(D/'run-once.sh').read_text()
for token in (
    "CLIENT_PATH=$(sed -n 's/^i2c_client_path=//p'",
    "CLIENT_NAME=$(sed -n 's/^i2c_client_name=//p'",
    'SENSOR_NAME="sp11-vd55g0 $CLIENT_NAME"',
    '[ -L "$CLIENT_PATH/driver" ]',
    '"$CLIENT_PATH/power/runtime_status"',
    'grep -Fxq "$SENSOR_NAME"',
    'grep -Fq "$SENSOR_NAME (1 pad, 1 link, 0 routes)"',
    'python3 - "$FAIL" "$D" "$CLIENT_NAME"',
    'E004S_DEVICE_IDENTITY: dev=([0-9]+-0060)',
    'identity.group(1)==client_name',
    'kernel_fault_or_warn',
    'WARNING:',
):
    need(token in run,'runtime token '+token)
need('for _ in $(seq 1 100); do' in run and 'sleep 0.1' in run,'notifier wait')
need(run.count('insmod "$CAMSS" e004j_ir_dphy_windows_parity=1')==1,'CAMSS load')
need(run.count('insmod "$SENSOR"')==1,'sensor load')
need(run.count('insmod "$HARNESS"')==1,'harness load')
need("'E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log" in run,'receiver programming absent')
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count','media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden action '+bad)

# Every executable/runtime artifact must be free of fixed adapter identities.
operational=[D/'runtime-preflight.sh',D/'run-once.sh',D/'prearm-check.sh',
             D/'verify-installed.sh',D/'install-candidate.sh',D/'arm-once.sh',
             D/'golden-return-check.sh',D/'retire-candidate.sh',
             D/'e004s_stream_block_test.c',
             D/'99zzzzzz_sp11_camera_e004s_dynamic_ir_bind_r4']
for op in operational:
    s=op.read_text()
    need('2-0060' not in s and '3-0060' not in s,'fixed adapter identity in '+op.name)
    need('bus_find_device_by_name' not in s,'name-based device lookup in '+op.name)

# Rebuild the dynamic harness twice against Golden.
with tempfile.TemporaryDirectory(prefix='e004s-harness-') as td:
    td=Path(td); copies=[]
    for n in ('a','b'):
        subprocess.run(['make','-C',str(BUILD),f'M={D}','clean'],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['make','-C',str(BUILD),f'M={D}','modules','V=0'],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        qko=D/'e004s_stream_block_test.ko'; cp=td/f'{n}.ko'
        shutil.copyfile(qko,cp); copies.append(cp)
    need(sha(copies[0])==sha(copies[1])=='f1cd5f44504251224253939f509c95c1ef86c603ba19002c0dce1f3314cfab57',
         'harness module reproducibility')
    need(copies[0].read_bytes()==copies[1].read_bytes(),'harness byte reproducibility')
    mi=subprocess.check_output(['modinfo',str(copies[1])],text=True)
    need('name:           e004s_stream_block_test' in mi,'module name')
    need('7.1.5-sp11-render-parity-v4+' in mi,'Golden vermagic')
    nm=subprocess.check_output(['nm','-u',str(copies[1])],text=True)
    for sym in ('bus_find_device','of_find_compatible_node','of_node_put',
                'v4l2_ctrl_g_ctrl','v4l2_ctrl_g_ctrl_int64'):
        need((' U '+sym+'\n') in nm,'missing module symbol '+sym)
subprocess.run(['make','-C',str(BUILD),f'M={D}','clean'],check=True,stdout=subprocess.DEVNULL)

g=(D/'99zzzzzz_sp11_camera_e004s_dynamic_ir_bind_r4').read_text()
for token in (
    'sp11-camera-e004s-dynamic-ir-bind-r4-one-shot',
    'sp11_camera_e004s_dynamic_ir_bind_r4=1',
    '/boot/sp11-7.1.5-camera-e004s-dynamic-ir-bind-r4/',
    'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb',
):
    need(token in g,'GRUB token '+token)

need(not BOOT.exists(),'candidate boot absent')
need(not ENTRY.exists(),'candidate entry absent')
need('sp11_camera_e004s_dynamic_ir_bind_r4=1' not in Path('/proc/cmdline').read_text(),'candidate active')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
for m in ('qcom_camss','sp11_vd55g0','e004s_stream_block_test'):
    need(not Path('/sys/module',m).exists(),'module already loaded '+m)

print('E004S_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO RUNTIME=NO')
print('E004S_IDENTITY=OF_COMPAT+microsoft,sp11-vd55g0 ADDR=0x60 ADAPTER_NUMBER=UNPINNED')
print('E004S_FIXED_BUS_NAMES=NONE SAME_DISCOVERED_CLIENT_REQUIRED_END_TO_END=YES')
print('E004S_HARNESS=REPRODUCIBLE TYPED_CONTROLS=YES STREAM_BLOCK=-95')
print('E004S_CAPTURE_STREAM=NO RECEIVER_PROGRAMMING=NO ILLUMINATION=NO')
