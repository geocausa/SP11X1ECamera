#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,tempfile
D=Path(__file__).resolve().parent
BASE=D.parent
REPO=D.parents[3]
IF=BASE/'if-unified-production-handoff-same-boot-reset-analysis'

def need(v,m):
    if not v:
        raise AssertionError(m)

def load(stage):
    return json.load(open(BASE/stage/'RESULT.json'))

r=json.load(open(D/'RESULT.json'))
ifp=load('if-unified-production-handoff-same-boot-reset-analysis')
igp=load('ig-unified-rear-to-front-r16-r27')
idp=load('id-unified-dtb-rear-regression-r16')
iep=load('ie-unified-front-production-r27')
ib=load('ib-unified-current-golden-rear-front-dtb')
need(ifp['status']=='PASS_OFFLINE_UNIFIED_HANDOFF_RESET_ANALYSIS','IF parent')
need(ifp['second_live_direction']=='front-to-rear','IF direction')
need(igp['status']=='PASS_CAPTURE_IG_REAR_TO_FRONT_R16_R27_GOLDEN_RESTORED_RETIRED','IG parent')
need(idp['status']=='PASS_CAPTURE_ID_UNIFIED_REAR_R16_GOLDEN_RESTORED_RETIRED','ID parent')
need(iep['status']=='PASS_CAPTURE_IE_UNIFIED_FRONT_R27_GOLDEN_RESTORED_RETIRED','IE parent')
need(ib['status']=='PASS_OFFLINE_UNIFIED_CURRENT_GOLDEN_REAR_FRONT_DTB','IB parent')

menu=(D/'99zzzzzz_sp11_camera_ih_front_to_rear_r27_r16').read_text()
gold=subprocess.check_output(['sudo','-n','cat','/etc/grub.d/76_sp11_audio_fullio_v19c'],text=True)
def args(t):
    l=next(x.strip() for x in t.splitlines() if x.strip().startswith('linux '))
    p=l.split()
    return p[1],p[2:]
_,ga=args(gold)
cp,ca=args(menu)
need(cp=='/boot/sp11-7.1.5-camera-ih-front-to-rear-r27-r16/vmlinuz-7.1.5-sp11-render-parity-v4+','linux path')
n=[]
for x in ca:
    if x in ('modprobe.blacklist=qcom_camss,imx681,ov13858','sp11_camera_ih_front_to_rear_r27_r16=1'):
        continue
    if x=='sp11_entry=7.1.5-sp11-camera-ih-front-to-rear-r27-r16':
        x='sp11_entry=7.1.5-sp11-fullio-v19c'
    n.append(x)
need(n==ga,'Golden cmdline drift')
need('x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb' in menu,'unified dtb')
need('firmware_class.path=' not in menu,'legacy firmware path')

for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-once.sh','archive.sh','finalize-archive.sh','golden-return-check.sh','retire-candidate.sh'):
    cp2=subprocess.run(['bash','-n',str(D/f)],capture_output=True,text=True)
    need(cp2.returncode==0,f+' syntax '+cp2.stderr)
cp2=subprocess.run(['shellcheck','-x','-S','warning',*[str(p) for p in sorted(D.glob('*.sh'))]],capture_output=True,text=True)
need(cp2.returncode==0,'shellcheck '+cp2.stdout+cp2.stderr)
for f in ('verify.py','verify-installed.py','verify-live.py','discover-unified.py','route-state.py'):
    cp2=subprocess.run(['python3','-m','py_compile',str(D/f)],capture_output=True,text=True)
    need(cp2.returncode==0,f+' compile '+cp2.stderr)

fix=IF/'ic-real-media-graph.normalized.txt'
s=fix.read_text()
def setlink(text,entity,target,pad,on):
    pat=rf'(^- entity \d+: {re.escape(entity)} \([^\n]*\)\n.*?)(?=^- entity |\Z)'
    mm=re.search(pat,text,re.M|re.S); need(mm,'entity '+entity)
    b=mm.group(1)
    old=rf'(-> "{re.escape(target)}":{pad} )\[([^\]]*)\]'
    def sub(m): return m.group(1)+('[ENABLED]' if on else '[]')
    nb,count=re.subn(old,sub,b,count=1); need(count==1,'link '+entity+'->'+target)
    return text[:mm.start(1)]+nb+text[mm.end(1):]
front=setlink(setlink(s,'msm_csiphy2','msm_csid1',0,True),'msm_csid1','msm_vfe1_pix',0,True)
neutral=setlink(setlink(front,'msm_csiphy2','msm_csid1',0,False),'msm_csid1','msm_vfe1_pix',0,False)
rear=setlink(setlink(neutral,'msm_csiphy1','msm_csid0',0,True),'msm_csid0','msm_vfe0_rdi0',0,True)
with tempfile.TemporaryDirectory(prefix='ih-route-') as td:
    for name,data,expect in [('pre',s,'neutral'),('front',front,'front-only'),('neutral',neutral,'neutral'),('rear',rear,'rear-only')]:
        p=Path(td)/(name+'.txt'); p.write_text(data)
        z=subprocess.run([str(D/'route-state.py'),str(p),'--expect',expect],capture_output=True,text=True)
        need(z.returncode==0,name+' '+z.stdout+z.stderr)

t=(D/'invoke-once.sh').read_text()
consume=t.index('CONSUMED_BEFORE_FIRST_ROUTE_MUTATION')
front_call=t.index('front-imx681-launcher.py')
front_off1=t.index('msm_csiphy2":1 -> "msm_csid1":0 [0]')
front_off2=t.index('msm_csid1":4 -> "msm_vfe1_pix":0 [0]')
neutral_gate=t.index('ROUTE-NEUTRAL-HANDOFF.txt')
rear_on1=t.index('msm_csiphy1":1 -> "msm_csid0":0 [1]')
rear_on2=t.index('msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]')
need(consume<front_call<front_off1<neutral_gate<rear_on1,'mutation order 1')
need(front_call<front_off2<neutral_gate<rear_on2,'mutation order 2')
need(t.count('front-imx681-launcher.py')==1,'single front launcher')
need(len(re.findall(r'--stream-count=1(?:\s|$)',t))==1 and len(re.findall(r'--stream-count=16(?:\s|$)',t))==1,'rear stream count sites')
need('--post-g3-write-policy shadow' in t and 'cap-release-one-shot' not in t,'front shadow only')
need('ATTEMPT1-CONSUMED.marker' in t and 'on_fail()' in t,'consume/fail guard')
need('ROUTE-FRONT-ONLY.txt' in t and 'ROUTE-NEUTRAL-HANDOFF.txt' in t and 'ROUTE-REAR-ONLY.txt' in t,'route evidence')

static={
 'candidate_id':'sp11-camera-ih-front-to-rear-r27-r16-one-shot',
 'candidate_marker':'sp11_camera_ih_front_to_rear_r27_r16=1',
 'direction':'front-to-rear',
 'front_frames':27,
 'front_post_g3_policy':'shadow',
 'front_post_g3_native_writes_authorized':0,
 'rear_colorbar_frames':1,
 'rear_normal_frames':16,
 'handoff_neutral_required':True,
 'consume_before_first_route_mutation':True,
 'same_stream_retry_authorized':False,
 'same_boot_retry_authorized':False,
 'unified_dtb_sha256':'5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321',
 'rear_colorbar_sha256':'6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346',
 'production_package_manifest_sha256':'57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757',
}
for k,v in static.items():
    need(r.get(k)==v,'RESULT '+k)
need(r.get('status') in ('PREPARED_NOT_INSTALLED_FRONT_TO_REAR_R27_R16','INSTALLED_UNARMED_FRONT_TO_REAR_R27_R16','PASS_CAPTURE_IH_FRONT_TO_REAR_R27_R16_GOLDEN_RESTORED_RETIRED','FAIL_IH_GOLDEN_RESTORED_RETIRED'),'status')
if r['status']=='PREPARED_NOT_INSTALLED_FRONT_TO_REAR_R27_R16':
    need(r.get('candidate_installed') is False and r.get('candidate_armed') is False and r.get('camera_runtime_performed') is False,'prep lifecycle')
if r['status']=='INSTALLED_UNARMED_FRONT_TO_REAR_R27_R16':
    need(r.get('candidate_installed') is True and r.get('candidate_armed') is False and r.get('camera_runtime_performed') is False,'installed lifecycle')

print('IH_STATIC_VERIFY=PASS DIRECTION=front-to-neutral-to-rear FRONT=R27 REAR=R16 POLICY=shadow RETRY=NO')
