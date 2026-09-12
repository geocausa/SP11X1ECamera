#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, shutil, subprocess, tempfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
E004J=REPO/'experiments/E004-front-ir-vd55g0/e004j-csiphy0-dphy-authority'
BASE_CAMSS=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
BASE_SRC=BASE_CAMSS/'camss-csiphy-3ph-1-0.c'
BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
PATCH=HERE/'0001-sp11-e004j-csiphy0-dphy-windows-parity.patch'
KO=HERE/'qcom-camss.ko'

BASE_SHA='418fe18845e1d57e2de5f2c9ece4bdd78d817d59ca71b25b00eb4259581464a8'
PATCH_SHA='1fc0f918a2f00e79918cf8bf7164f49cb8df395b8b05c949dc424a7b3824a869'
MODULE_SHA='bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba'
BUILD_LOG_SHA='1bc1fbb5e8a3feb94b69b00dab3cf4c755074a458e9cd478ca4cd6752ba2ea52'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

def need(v,m):
    if not v: raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

need(sha(BASE_SRC)==BASE_SHA,'shared source baseline restored')
need(sha(PATCH)==PATCH_SHA,'patch identity')
need(sha(KO)==MODULE_SHA,'module identity')
need(sha(HERE/'CAMSS-BUILD-A.txt')==BUILD_LOG_SHA and sha(HERE/'CAMSS-BUILD-B.txt')==BUILD_LOG_SHA,'build logs')
need((HERE/'CAMSS-BUILD-A.txt').read_bytes()==(HERE/'CAMSS-BUILD-B.txt').read_bytes(),'build logs byte identical')

j=json.load(open(E004J/'RESULT.json'))
need(j['status']=='PASS_OFFLINE_WINDOWS_LINUX_CSIPHY0_DPHY_DIFF_AUTHORITY','E004j authority')
need(j['scoped_correction']['modeled_windows_matches']==96 and j['scoped_correction']['modeled_windows_mismatches']==0,'96/96 model')
need(j['scoped_correction']['rear_csiphy1_affected'] is False and j['scoped_correction']['front_rgb_cphy_affected'] is False,'scope')

pt=PATCH.read_text()
for token in (
 'e004j_ir_dphy_windows_parity',
 'csiphy->id == 0',
 'c->phy_cfg == V4L2_MBUS_CSI2_DPHY',
 'settle_cnt = 0x10',
 'writel_relaxed(lane_mask',
 '0xff, 0xfe, 0xe6, 0xdf, 0xdf, 0xfc, 0xfb, 0x9b, 0x7f, 0xbf, 0xff',
 'E004J_CSIPHY0_DPHY_WINDOWS_PARITY',
 'else if (!x1e_cphy)',
):
    need(token in pt,'patch token '+token)
need(pt.count('+++ b/')==1,'single source file patch')
need('camss.c' not in pt,'core camss.c unchanged')

mi=subprocess.check_output(['modinfo',str(KO)],text=True)
need('name:           qcom_camss' in mi,'module name')
verm=next(x for x in mi.splitlines() if x.startswith('vermagic:')).split(':',1)[1].strip()
need(verm==VERMAGIC,'Golden vermagic')
need('e004j_ir_dphy_windows_parity:Arm SP11 E004j CSIPHY0 D-PHY same-machine Windows receiver parity (bool)' in mi,'module param')
st=subprocess.check_output(['strings',str(KO)],text=True,errors='replace')
need('E004J_CSIPHY0_DPHY_WINDOWS_PARITY link_freq=%lld timer=%u lane_mask=0x%02x settle=0x%02x ctrl11_21=ff,fe,e6,df,df,fc,fb,9b,7f,bf,ff' in st,'runtime proof marker')

# Mechanical replay in a private copy. This must not modify the shared source tree.
with tempfile.TemporaryDirectory(prefix='e004k-camss-replay-') as td:
    root=Path(td)
    target=root/'drivers/media/platform/qcom/camss'
    target.parent.mkdir(parents=True)
    shutil.copytree(BASE_CAMSS,target,ignore=shutil.ignore_patterns('*.o','*.ko','*.mod','*.mod.c','*.cmd','Module.symvers','modules.order','.module-common.o'))
    subprocess.run(['patch','-p1','-i',str(PATCH)],cwd=root,check=True,stdout=subprocess.DEVNULL)
    patched=target/'camss-csiphy-3ph-1-0.c'
    need(sha(patched)=='2ea354304cad721967279a8a0211e97ec2731a71bd945a6ddba6dccdb191a362','patched source identity')
    hashes=[]
    text_hashes=[]
    frozen_text=root/'frozen.text'
    subprocess.run(['llvm-objcopy','--dump-section',f'.text={frozen_text}',str(KO),str(root/'frozen-copy.ko')],check=True)
    frozen_text_sha=sha(frozen_text)
    frozen_srcversion=subprocess.check_output(['modinfo','-F','srcversion',str(KO)],text=True).strip()
    for n in ('a','b'):
        subprocess.run(['make','-C',str(BUILD),f'M={target}','clean'],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['make','-C',str(BUILD),f'M={target}','modules','V=0'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        q=target/'qcom-camss.ko'
        hashes.append(sha(q))
        sec=root/f'{n}.text'
        subprocess.run(['llvm-objcopy','--dump-section',f'.text={sec}',str(q),str(root/f'{n}-copy.ko')],check=True)
        text_hashes.append(sha(sec))
        rmi=subprocess.check_output(['modinfo',str(q)],text=True)
        need(VERMAGIC in rmi,'replay vermagic')
        need('e004j_ir_dphy_windows_parity:' in rmi,'replay module param')
        need(subprocess.check_output(['modinfo','-F','srcversion',str(q)],text=True).strip()==frozen_srcversion,'replay srcversion')
        rst=subprocess.check_output(['strings',str(q)],text=True,errors='replace')
        need('E004J_CSIPHY0_DPHY_WINDOWS_PARITY' in rst,'replay proof marker')
    need(hashes[0]==hashes[1],'relocated replay builds not byte-identical to each other')
    need(text_hashes==[frozen_text_sha,frozen_text_sha],'replayed executable text differs from frozen module')

need(sha(BASE_SRC)==BASE_SHA,'shared source changed during replay')
need(not Path('/sys/module/qcom_camss').exists(),'CAMSS must remain unloaded on Golden')
need('sp11_camera_e004' not in Path('/proc/cmdline').read_text(),'no disposable E004 candidate boot active')

result={
 'schema':'sp11-camera-e004k-csiphy0-dphy-parity-module-v1',
 'status':'PASS_OFFLINE_REPRODUCIBLE_SCOPED_CAMSS_MODULE',
 'parent_e004j_commit':'2334f46',
 'base_csiphy_source_sha256':BASE_SHA,
 'patched_csiphy_source_sha256':'2ea354304cad721967279a8a0211e97ec2731a71bd945a6ddba6dccdb191a362',
 'patch_sha256':PATCH_SHA,
 'module_sha256':MODULE_SHA,
 'module_vermagic':VERMAGIC,
 'two_builds_byte_reproducible':True,
 'replay_builds_match_frozen_executable_text':True,
 'relocated_full_ko_hash_note':'temporary build path changes debug metadata; executable .text and srcversion are required to match',
 'parameter':'e004j_ir_dphy_windows_parity',
 'parameter_default':False,
 'scope':'CAMSS_X1E80100 && CSIPHY0 && DPHY only',
 'programming_when_armed':{
   'settle_count':'0x10',
   'dynamic_lane_mask':'preserved/restored; expected IR value 0x81',
   'common_ctrl11_21':['0xff','0xfe','0xe6','0xdf','0xdf','0xfc','0xfb','0x9b','0x7f','0xbf','0xff'],
 },
 'modeled_windows_receiver_match':'96/96',
 'shared_kernel_source_restored':True,
 'runtime_performed':False,
 'runtime_authorized':False,
 'next_gate':'Integrate a fixed-mode native VD55G0 subdevice using the proven Surface patch/config while keeping sensor stream disabled; use the E004k CAMSS module only in a disposable candidate before first real IR stream.'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('E004K_VERIFY=PASS MODULE_SHA256='+MODULE_SHA+' REPLAY_BUILDS=2/2')
print('E004K_SCOPE=DEFAULT_OFF X1E_CSIPHY0_DPHY_ONLY MODELED_WINDOWS=96/96')
print('E004K_KERNEL_SOURCE=RESTORED BASE_SHA256='+BASE_SHA)
print('E004K_RUNTIME=NO')

