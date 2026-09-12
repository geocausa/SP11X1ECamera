#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
D=Path(__file__).resolve().parent; BASE=D.parent; REPO=D.parents[3]
IB=BASE/'ib-unified-current-golden-rear-front-dtb'; FIX=D/'fixtures/ic-real-media-graph.normalized.txt'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ib=json.load(open(IB/'RESULT.json')); r=json.load(open(D/'RESULT.json'))
need(ib['status']=='PASS_OFFLINE_UNIFIED_CURRENT_GOLDEN_REAR_FRONT_DTB','IB parent')
need(sha(FIX)=='24309fb97c68bbfc5c4874864a2f100e148f7cfc152fb88ee8abcda021ee7814','real graph fixture drift')
menu=(D/'99zzzzzz_sp11_camera_id_unified_rear_r16').read_text(); gold=subprocess.check_output(['sudo','-n','cat','/etc/grub.d/76_sp11_audio_fullio_v19c'],text=True)
def args(t):
    l=next(x.strip() for x in t.splitlines() if x.strip().startswith('linux ')); p=l.split(); return p[1],p[2:]
_,ga=args(gold); cp,ca=args(menu)
need(cp=='/boot/sp11-7.1.5-camera-id-unified-rear-r16/vmlinuz-7.1.5-sp11-render-parity-v4+','linux path')
n=[]
for x in ca:
    if x in ('modprobe.blacklist=qcom_camss,imx681,ov13858','sp11_camera_id_unified_rear_r16=1'): continue
    if x=='sp11_entry=7.1.5-sp11-camera-id-unified-rear-r16': x='sp11_entry=7.1.5-sp11-fullio-v19c'
    n.append(x)
need(n==ga,'Golden cmdline drift')
need('firmware_class.path=' not in menu,'firmware path')
need('sp11-camera-ic-unified-rear-r16-one-shot' not in menu and 'sp11_camera_ic_unified_rear_r16' not in menu,'IC identity reuse')
sh=sorted(D.glob('*.sh'))
for f in sh:
    cp2=subprocess.run(['bash','-n',str(f)],text=True,capture_output=True); need(cp2.returncode==0,f.name+' syntax '+cp2.stderr)
cp2=subprocess.run(['shellcheck','-x','-S','warning',*[str(p) for p in sh]],text=True,capture_output=True); need(cp2.returncode==0,'shellcheck '+cp2.stdout+cp2.stderr)
for f in ('verify.py','verify-installed.py','verify-live.py','discover-unified.py','verify-rear-route.py'):
    cp2=subprocess.run(['python3','-m','py_compile',str(D/f)],text=True,capture_output=True); need(cp2.returncode==0,f+' compile '+cp2.stderr)
cp2=subprocess.run([str(D/'discover-unified.py'),'--from-file',str(FIX)],text=True,capture_output=True); need(cp2.returncode==0,'fixture discovery '+cp2.stderr)
disc=json.loads(cp2.stdout)
need(disc['rear_sensor_entity']=='ov13858 4-0010' and disc['rear_sensor_device']=='/dev/v4l-subdev25','fixture rear discovery')
need(disc['front_sensor_entity']=='imx681 1-0010' and disc['front_sensor_device']=='/dev/v4l-subdev26','fixture front discovery')
need(disc['rear_video_device']=='/dev/video0' and disc['front_video_device']=='/dev/video7','fixture videos')
need(disc['rear_route']==['msm_csiphy1','msm_csid0','msm_vfe0_rdi0','msm_vfe0_video0'],'fixture rear route')
need(disc['front_route']==['msm_csiphy2','msm_csid1','msm_vfe1_pix','msm_vfe1_video3'],'fixture front route')
cp2=subprocess.run([str(D/'verify-rear-route.py'),'--mode','pre','--from-file',str(FIX)],text=True,capture_output=True); need(cp2.returncode==0,'fixture pre route '+cp2.stdout+cp2.stderr)
s=FIX.read_text(); old1='\t\t-> "msm_csid0":0 []'; old2='\t\t-> "msm_vfe0_rdi0":0 []'
start=s.index('- entity 4: msm_csiphy1'); end=s.index('- entity 7: msm_csiphy2'); a=s[:start]; b=s[start:end]; c=s[end:]
need(b.count(old1)==1,'fixture csiphy1 target count'); b=b.replace(old1,'\t\t-> "msm_csid0":0 [ENABLED]',1)
cs=c.index('- entity 13: msm_csid0'); ce=c.index('- entity 19: msm_csid1'); c1=c[:cs]; c2=c[cs:ce]; c3=c[ce:]
need(c2.count(old2)==1,'fixture csid0 target count'); c2=c2.replace(old2,'\t\t-> "msm_vfe0_rdi0":0 [ENABLED]',1)
with tempfile.TemporaryDirectory(prefix='id-route-') as td:
    q=Path(td)/'enabled.txt'; q.write_text(a+b+c1+c2+c3)
    cp2=subprocess.run([str(D/'verify-rear-route.py'),'--mode','enabled','--from-file',str(q)],text=True,capture_output=True); need(cp2.returncode==0,'fixture enabled route '+cp2.stdout+cp2.stderr)
t=(D/'invoke-rear-once.sh').read_text()
mark=t.index('CONSUMED_BEFORE_REAR_ROUTE_MUTATION'); l1=t.index('media-ctl -d "$MEDIA" -l')
need(mark<l1,'consumed marker must precede first route mutation')
need(t.count('media-ctl -d "$MEDIA" -l')==2,'route enable command count')
need('\"msm_csiphy1\":1 -> \"msm_csid0\":0 [1]' in t,'rear link1 missing')
need('\"msm_csid0\":1 -> \"msm_vfe0_rdi0\":0 [1]' in t,'rear link2 missing')
need('\"msm_csiphy2\":1 -> \"msm_csid1\":0 [1]' not in t,'front link enable forbidden')
need('verify-rear-route.py" --mode pre' in t and 'verify-rear-route.py" --mode enabled' in t,'route verification gates')
need(len(re.findall(r'--stream-count=1(?:\s|$)',t))==1 and len(re.findall(r'--stream-count=16(?:\s|$)',t))==1,'stream sites')
need('front_video_forbidden' in t and 'on_fail()' in t and 'ATTEMPT1-FAILURE.json' in t,'safety guards')
load=(D/'load.sh').read_text(); need('--stream-' not in load and 'v4l2-ctl' not in load,'load must not stream')
for k,v in {'status':'PREPARED_NOT_INSTALLED_UNIFIED_REAR_REGRESSION_R16','candidate_installed':False,'candidate_armed':False,'camera_runtime_performed':False,'front_stream_authorized':False,'same_stream_retry_authorized':False,'same_boot_retry_authorized':False,'attempt_consumed_before_route_mutation':True,'unified_dtb_sha256':'5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321'}.items(): need(r.get(k)==v,'RESULT '+k)
need(all(r['ic_harness_fixes'].values()),'IC fixes not all true')
print('ID_STATIC_VERIFY=PASS FRESH_IDENTITY=YES REAL_GRAPH_DISCOVERY=PASS ROUTE_PRE=PASS ROUTE_ENABLE_SYNTH=PASS')
print('ID_ATTEMPT_CONSUME=BEFORE_ROUTE_MUTATION REAR_LINKS=2 FRONT_LINKS=0 STREAMS=1+16 RETRY=NO')
