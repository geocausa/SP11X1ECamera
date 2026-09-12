#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent; BASE=D.parent
HY=BASE/'hy-production-one-stream-r27'; ID=BASE/'id-unified-dtb-rear-regression-r16'; IB=BASE/'ib-unified-current-golden-rear-front-dtb'
def need(v,m):
    if not v: raise AssertionError(m)
hy=json.load(open(HY/'RESULT.json')); rid=json.load(open(ID/'RESULT.json')); ib=json.load(open(IB/'RESULT.json')); r=json.load(open(D/'RESULT.json'))
need(hy['status']=='PASS_CAPTURE_HY_PRODUCTION_ONE_STREAM_R27_GOLDEN_RESTORED_RETIRED','HY parent')
need(rid['status']=='PASS_CAPTURE_ID_UNIFIED_REAR_R16_GOLDEN_RESTORED_RETIRED' and rid['golden_return']=='PASS','ID parent')
need(ib['status']=='PASS_OFFLINE_UNIFIED_CURRENT_GOLDEN_REAR_FRONT_DTB','IB parent')
menu=(D/'99zzzzzz_sp11_camera_ie_unified_front_r27').read_text()
gold=subprocess.check_output(['sudo','-n','cat','/etc/grub.d/76_sp11_audio_fullio_v19c'],text=True)
def args(t):
    l=next(x.strip() for x in t.splitlines() if x.strip().startswith('linux ')); p=l.split(); return p[1],p[2:]
_,ga=args(gold); cp,ca=args(menu)
need(cp=='/boot/sp11-7.1.5-camera-ie-unified-front-r27/vmlinuz-7.1.5-sp11-render-parity-v4+','linux path')
n=[]
for x in ca:
    if x in ('modprobe.blacklist=qcom_camss,imx681,ov13858','sp11_camera_ie_unified_front_r27=1'): continue
    if x=='sp11_entry=7.1.5-sp11-camera-ie-unified-front-r27': x='sp11_entry=7.1.5-sp11-fullio-v19c'
    n.append(x)
need(n==ga,'Golden cmdline drift')
need('x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb' in menu,'unified dtb path')
need('firmware_class.path=' not in menu,'legacy firmware path')
for f in ('prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-one.sh','archive.sh','finalize-archive.sh','golden-return-check.sh','retire-candidate.sh'):
    cp2=subprocess.run(['bash','-n',str(D/f)],capture_output=True,text=True); need(cp2.returncode==0,f+' syntax '+cp2.stderr)
cp2=subprocess.run(['shellcheck','-x','-S','warning',*[str(p) for p in sorted(D.glob('*.sh'))]],capture_output=True,text=True); need(cp2.returncode==0,'shellcheck '+cp2.stdout+cp2.stderr)
for f in ('verify.py','verify-installed.py','verify-live.py','discover-unified.py','verify-rear-route.py','verify-rear-disabled.py'):
    cp2=subprocess.run(['python3','-m','py_compile',str(D/f)],capture_output=True,text=True); need(cp2.returncode==0,f+' compile '+cp2.stderr)
fixture=ID/'fixtures/ic-real-media-graph.normalized.txt'
cp2=subprocess.run([str(Path('src/front-imx681/bin/front-imx681-discover.py')),'--topology-file',str(fixture),'--json'],capture_output=True,text=True)
need(cp2.returncode==0,'offline front discovery '+cp2.stderr)
p=json.loads(cp2.stdout); need(p['sensor_entity']=='imx681 1-0010' and p['video_entity']=='msm_vfe1_video3','offline front route')
t=(D/'invoke-one.sh').read_text()
need(t.count('front-imx681-launcher.py')==1,'single launcher site')
need('--post-g3-write-policy shadow' in t and 'cap-release-one-shot' not in t,'shadow policy')
need('ATTEMPT1-CONSUMED.marker' in t and 'on_fail()' in t,'consume/fail guard')
need('verify-rear-disabled.py' in t,'rear disabled gates')
need('msm_csiphy1' not in t and 'msm_csid0' not in t and 'msm_vfe0_rdi0' not in t,'rear route mutation leaked')
load=(D/'load.sh').read_text()
need('ov13858-production.ko' in load and 'discover-unified.py' in load and 'front-imx681-discover.py' in load,'unified load')
need('--stream-' not in load and 'v4l2-ctl' not in load,'load must not stream')
static={'candidate_id':'sp11-camera-ie-unified-front-r27-one-shot','candidate_marker':'sp11_camera_ie_unified_front_r27=1','stream_count':1,'frames':27,'post_g3_policy':'shadow','post_g3_native_writes_authorized':0,'same_stream_retry_authorized':False,'same_boot_retry_authorized':False,'rear_stream_authorized':False,'unified_dtb_sha256':'5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321','production_package_manifest_sha256':'57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757'}
for k,v in static.items(): need(r.get(k)==v,'RESULT '+k)
need(r.get('status') in ('PREPARED_NOT_INSTALLED_UNIFIED_FRONT_PRODUCTION_R27','INSTALLED_UNARMED_UNIFIED_FRONT_PRODUCTION_R27','PASS_CAPTURE_IE_UNIFIED_FRONT_R27_GOLDEN_RESTORED_RETIRED','FAIL_IE_GOLDEN_RESTORED_RETIRED'),'status')
if r['status']=='PREPARED_NOT_INSTALLED_UNIFIED_FRONT_PRODUCTION_R27':
    need(r.get('candidate_installed') is False and r.get('candidate_armed') is False and r.get('camera_runtime_performed') is False,'prep lifecycle')
if r['status']=='INSTALLED_UNARMED_UNIFIED_FRONT_PRODUCTION_R27':
    need(r.get('candidate_installed') is True and r.get('candidate_armed') is False and r.get('camera_runtime_performed') is False,'installed lifecycle')
if r['status']=='PASS_CAPTURE_IE_UNIFIED_FRONT_R27_GOLDEN_RESTORED_RETIRED':
    need(r.get('candidate_installed') is False and r.get('candidate_retired') is True and r.get('candidate_boot_consumed') is True,'pass lifecycle')
    need(r.get('camera_runtime_performed') is True and r.get('streams_completed')==1 and r.get('frames')==27,'pass stream')
    need(r.get('first_snapshot_generation')==1 and r.get('producer_generations')==24 and r.get('producer_requests')==23,'pass producer')
    need(r.get('startup_native_writes')==3 and r.get('post_g3_native_writes')==0 and r.get('hardware_control_transactions_including_bootstrap')==4,'pass writes')
    need(r.get('streamoff_count')==1 and r.get('kernel_health')=='PASS' and r.get('golden_return')=='PASS','pass health')
    need(r.get('rear_stream_executed') is False and r.get('rear_route_post_stream')=='disabled','rear isolation')
    need(r.get('same_stream_retry_performed') is False and r.get('same_boot_retry_performed') is False,'pass retry')
    need(r.get('archive_manifest_sha256')=='9ad7fa2649d688a23105d99dc1782d7b3b8eeb14cfe894c2fc435e5c21c9496e','pass archive')
print('IE_STATIC_VERIFY=PASS STATUS='+r['status']+' STREAMS=1 POLICY=shadow REAR_STREAM=NO RETRY=NO')
