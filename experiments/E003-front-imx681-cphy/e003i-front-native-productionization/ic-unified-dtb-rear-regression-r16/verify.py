#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent; BASE=D.parent
IB=BASE/'ib-unified-current-golden-rear-front-dtb'
def need(v,m):
 if not v: raise AssertionError(m)
ib=json.load(open(IB/'RESULT.json')); r=json.load(open(D/'RESULT.json')); need(ib['status']=='PASS_OFFLINE_UNIFIED_CURRENT_GOLDEN_REAR_FRONT_DTB','IB parent')
menu=(D/'99zzzzzz_sp11_camera_ic_unified_rear_r16').read_text(); gold=subprocess.check_output(['sudo','-n','cat','/etc/grub.d/76_sp11_audio_fullio_v19c'],text=True)
def args(t):
 l=next(x.strip() for x in t.splitlines() if x.strip().startswith('linux ')); p=l.split(); return p[1],p[2:]
_,ga=args(gold); cp,ca=args(menu); need(cp=='/boot/sp11-7.1.5-camera-ic-unified-rear-r16/vmlinuz-7.1.5-sp11-render-parity-v4+','linux path')
n=[]
for x in ca:
 if x in ('modprobe.blacklist=qcom_camss,imx681,ov13858','sp11_camera_ic_unified_rear_r16=1'): continue
 if x=='sp11_entry=7.1.5-sp11-camera-ic-unified-rear-r16': x='sp11_entry=7.1.5-sp11-fullio-v19c'
 n.append(x)
need(n==ga,'Golden cmdline drift'); need('firmware_class.path=' not in menu,'firmware path')
for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-rear-once.sh','archive.sh','finalize-archive.sh','golden-return-check.sh','retire-candidate.sh'):
 cp2=subprocess.run(['bash','-n',str(D/f)],text=True,capture_output=True); need(cp2.returncode==0,f+' syntax '+cp2.stderr)
cp2=subprocess.run(['shellcheck','-x','-S','warning',*[str(p) for p in sorted(D.glob('*.sh'))]],text=True,capture_output=True); need(cp2.returncode==0,'shellcheck '+cp2.stdout+cp2.stderr)
for f in ('verify.py','verify-installed.py','verify-live.py','discover-unified.py'):
 cp2=subprocess.run(['python3','-m','py_compile',str(D/f)],text=True,capture_output=True); need(cp2.returncode==0,f+' compile '+cp2.stderr)
t=(D/'invoke-rear-once.sh').read_text(); need(len(re.findall(r'--stream-count=1(?:\s|$)',t))==1 and len(re.findall(r'--stream-count=16(?:\s|$)',t))==1,'stream sites'); need('front_video_forbidden' in t,'front prohibition'); need('ATTEMPT1-CONSUMED.marker' in t,'consume marker'); need('on_fail()' in t and 'ATTEMPT1-FAILURE.json' in t,'failure archive guard')
need(r.get('status') in ('PREPARED_NOT_INSTALLED_UNIFIED_REAR_REGRESSION_R16','INSTALLED_UNARMED_UNIFIED_REAR_REGRESSION_R16','FAIL_HARNESS_PRE_STREAM_NO_CAMERA_STREAM_GOLDEN_RESTORED_RETIRED'),'RESULT status')
for k,v in {'candidate_armed':False,'camera_runtime_performed':False,'front_stream_authorized':False,'same_stream_retry_authorized':False,'same_boot_retry_authorized':False,'unified_dtb_sha256':'5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321'}.items(): need(r.get(k)==v,'RESULT '+k)
if r['status']=='PREPARED_NOT_INSTALLED_UNIFIED_REAR_REGRESSION_R16': need(r.get('candidate_installed') is False,'prepared installed')
elif r['status']=='INSTALLED_UNARMED_UNIFIED_REAR_REGRESSION_R16': need(r.get('candidate_installed') is True,'installed flag'); need(r.get('install_source_head') is not None,'install source head')
else: need(r.get('candidate_retired') is True and r.get('camera_stream_started') is False and r.get('golden_return')=='PASS','final prestream failure closure')
print('IC_STATIC_VERIFY=PASS STATUS='+r['status']+' REAR=COLORBAR+R16 FRONT_STREAM=NO RETRY=NO')
