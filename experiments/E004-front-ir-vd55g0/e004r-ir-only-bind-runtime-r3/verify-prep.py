#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, shutil, subprocess, tempfile

D=Path(__file__).resolve().parent
R=D.parents[2]
Q=D.parent/'e004q-ir-only-bind-runtime-r2'
O=D.parent/'e004o-ir-only-graph-authority'
L=D.parent/'e004l-native-bind-only-authority'
K=D.parent/'e004k-csiphy0-dphy-parity-module'
BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
API=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/v4l2-core/v4l2-ctrls-api.c')
BOOT=Path('/boot/sp11-7.1.5-camera-e004r-ir-only-bind-r3')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004r_ir_only_bind_r3')

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
need(o['only_behavioral_delta']=='typed V4L2 control accessors in verification harness','delta declaration')
need(o['dtb_sha256']=='fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742','dtb')
need(o['sensor_module_sha256']=='4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','sensor')
need(o['camss_module_sha256']=='bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba','camss')
need(o['harness_module_sha256']=='2cacc5e1336ac77b32c7e67e8c6f05cfdbaf6d54e9424cede1168f69c25f3303','harness module')

q=json.load(open(Q/'RESULT.json'))
need(q['status']=='FAIL_HARNESS_ACCESSOR_WARN_GRAPH_AND_STREAM_BLOCK_PASS_GOLDEN_RETURN_RETIRED','E004q class')
need(q['media_graph_pass'] is True and q['direct_sensor_stream_result']=='-EOPNOTSUPP','E004q core pass')
need(q['kernel_warns_from_wrong_accessor'] is True,'E004q accessor diagnosis')
og=json.load(open(O/'RESULT.json'))
need(og['status']=='PASS_OFFLINE_IR_ONLY_CAMSS_GRAPH_AUTHORITY','E004o graph')
l=json.load(open(L/'RESULT.json'))
need(l['status']=='PASS_OFFLINE_NATIVE_BIND_ONLY_AUTHORITY','E004l sensor')
k=json.load(open(K/'RESULT.json'))
need(k['status']=='PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE','E004k CAMSS')

need(sha(D/'e004r_stream_block_test.c')=='47992c23009b6fa2a4894243e04c3ad34dfb7392cfb435506c3205f0e0601e84','harness source')
need(sha(D/'Makefile')=='5a4b7ccf4c237243d3ee595eaf15b99175df6776b6efe4f25014843ecbb9c73c','Makefile')
h=(D/'e004r_stream_block_test.c').read_text()
need(h.count('v4l2_ctrl_g_ctrl_int64(')==1,'int64 accessor must be used once')
need('pixel_val = v4l2_ctrl_g_ctrl_int64(pixel);' in h,'pixel int64 accessor')
need('link_idx = v4l2_ctrl_g_ctrl(link);' in h,'link menu index accessor')
need('hblank_val = v4l2_ctrl_g_ctrl(hblank);' in h,'hblank integer accessor')
need('vblank_val = v4l2_ctrl_g_ctrl(vblank);' in h,'vblank integer accessor')
need('link->type != V4L2_CTRL_TYPE_INTEGER_MENU' in h and '!link->qmenu_int' in h,'link menu type gate')
need('link_val = link->qmenu_int[link_idx];' in h,'link menu map')
for token in (
 'E004R_V4L2_CONTRACT',
 'E004R_STREAM_BLOCK_TEST',
 'cfg.type != V4L2_MBUS_CSI2_DPHY',
 'cfg.bus.mipi_csi2.num_data_lanes != 1',
 'cfg.link_freq != 420000000LL',
 'stream_ret != -EOPNOTSUPP',
):
    need(token in h,'harness token '+token)

api=API.read_text()
g64=api[api.index('s64 v4l2_ctrl_g_ctrl_int64'):api.index('EXPORT_SYMBOL(v4l2_ctrl_g_ctrl_int64)')]
g32=api[api.index('s32 v4l2_ctrl_g_ctrl('):api.index('EXPORT_SYMBOL(v4l2_ctrl_g_ctrl)')]
need('ctrl->type != V4L2_CTRL_TYPE_INTEGER64' in g64,'kernel int64 API guard')
need('WARN_ON(!ctrl->is_int)' in g32,'kernel integer API guard')

# Rebuild the harness twice against Golden and require canonical bytes.
with tempfile.TemporaryDirectory(prefix='e004r-harness-') as td:
    td=Path(td)
    copies=[]
    for n in ('a','b'):
        subprocess.run(['make','-C',str(BUILD),f'M={D}','clean'],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['make','-C',str(BUILD),f'M={D}','modules','V=0'],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        qko=D/'e004r_stream_block_test.ko'
        cp=td/f'{n}.ko'
        shutil.copyfile(qko,cp)
        copies.append(cp)
    need(sha(copies[0])==sha(copies[1])=='2cacc5e1336ac77b32c7e67e8c6f05cfdbaf6d54e9424cede1168f69c25f3303',
         'harness module reproducibility')
    need(copies[0].read_bytes()==copies[1].read_bytes(),'harness byte reproducibility')
    mi=subprocess.check_output(['modinfo',str(copies[1])],text=True)
    need('name:           e004r_stream_block_test' in mi,'module name')
    need('7.1.5-sp11-render-parity-v4+' in mi,'Golden vermagic')
    nm=subprocess.check_output(['nm','-u',str(copies[1])],text=True)
    need(' U v4l2_ctrl_g_ctrl\n' in nm,'32-bit accessor symbol')
    need(' U v4l2_ctrl_g_ctrl_int64\n' in nm,'int64 accessor symbol')
subprocess.run(['make','-C',str(BUILD),f'M={D}','clean'],check=True,stdout=subprocess.DEVNULL)

g=(D/'99zzzzzz_sp11_camera_e004r_ir_only_bind_r3').read_text()
for token in (
 'sp11-camera-e004r-ir-only-bind-r3-one-shot',
 'sp11_camera_e004r_ir_only_bind_r3=1',
 '/boot/sp11-7.1.5-camera-e004r-ir-only-bind-r3/',
 'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb',
):
    need(token in g,'GRUB token '+token)

run=(D/'run-once.sh').read_text()
need('for _ in $(seq 1 100); do' in run and 'sleep 0.1' in run,'bounded notifier wait')
need("sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)" in run,'graph wait')
need("'-> \"msm_csiphy0\":0 \\[ENABLED,IMMUTABLE\\]'" in run,'immutable link wait')
need("contract_marker='E004R_V4L2_CONTRACT: link_idx=0 link_freq=420000000 pixel_rate=84000000 hblank=556 vblank=1351 mbus_ret=0 type=5 lanes=1 mbus_link_freq=420000000'" in run,
     'typed contract acceptance')
need(run.count('insmod "$CAMSS" e004j_ir_dphy_windows_parity=1')==1,'CAMSS load')
need(run.count('insmod "$SENSOR"')==1,'sensor load')
need(run.count('insmod "$HARNESS"')==1,'harness load')
need("'E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log" in run,'receiver programming absent')
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count','media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden action '+bad)

need(not BOOT.exists(),'candidate boot absent')
need(not ENTRY.exists(),'candidate entry absent')
need('sp11_camera_e004r_ir_only_bind_r3=1' not in Path('/proc/cmdline').read_text(),'candidate active')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
for m in ('qcom_camss','sp11_vd55g0','e004r_stream_block_test'):
    need(not Path('/sys/module',m).exists(),'module already loaded '+m)

print('E004R_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO RUNTIME=NO')
print('E004R_DELTA=TYPED_V4L2_ACCESSORS_ONLY')
print('E004R_HARNESS=LINK_MENU32 PIXEL64 HBLANK32 VBLANK32 REPRODUCIBLE=YES')
print('E004R_GRAPH=IR_ONLY NOTIFIER_WAIT=10S STREAM_BLOCK=-95')
print('E004R_CAPTURE_STREAM=NO RECEIVER_PROGRAMMING=NO ILLUMINATION=NO')
