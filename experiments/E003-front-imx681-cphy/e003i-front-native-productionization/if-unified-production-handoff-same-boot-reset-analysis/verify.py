#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
D=Path(__file__).resolve().parent; BASE=D.parent; REPO=D.parents[3]
def need(v,m):
    if not v: raise AssertionError(m)
def load(name): return json.load(open(BASE/name/'RESULT.json'))
idp=load('id-unified-dtb-rear-regression-r16')
iep=load('ie-unified-front-production-r27')
hqp=load('hq-four-stream-shadow-r27')
hrp=load('hr-production-repeated-open-handoff')
r=json.load(open(D/'RESULT.json'))
need(idp['status']=='PASS_CAPTURE_ID_UNIFIED_REAR_R16_GOLDEN_RESTORED_RETIRED','ID parent')
need(iep['status']=='PASS_CAPTURE_IE_UNIFIED_FRONT_R27_GOLDEN_RESTORED_RETIRED','IE parent')
need(hqp['status']=='PASS_CAPTURE_HQ_FOUR_STREAM_SHADOW_R27_GOLDEN_RESTORED_RETIRED' and hqp['streams_completed']==4 and hqp['first_snapshot_generation_each_stream']==1,'HQ parent')
need(hrp['status']=='PASS_OFFLINE_PRODUCTION_REPEATED_OPEN_HANDOFF' and hrp['production_contract']['bounded_repeated_open_close_proven'] is True,'HR parent')
# Source-level front reset closure.
v=(REPO/'src/front-imx681/kernel/camss/camss-video.c').read_text()
for fn,field in [('camss_x1e_tlbg_reset','x1e_tlbg_generation'),('camss_x1e_3a_reset','x1e_3a_generation')]:
    m=re.search(rf'void {fn}\(.*?\n\}}',v,re.S); need(m,fn); need(field+' = 0;' in m.group(0),fn+' generation reset')
c=(REPO/'src/front-imx681/kernel/camss/camss-csid-680.c').read_text()
m=re.search(r'static int csid_reset\(.*?\n\}',c,re.S); need(m,'csid_reset')
for field in ('x1e_ipp_epoch0_count = 0;','x1e_buf_done_video_count = 0;','x1e_buf_done_aec_bhist_count = 0;','x1e_buf_done_tintless_count = 0;','x1e_buf_done_awb_count = 0;'):
    need(field in m.group(0),'csid reset '+field)
# Accepted helpers enable but do not disable their mutable route.
rear=(BASE/'id-unified-dtb-rear-regression-r16/invoke-rear-once.sh').read_text()
front=(REPO/'src/front-imx681/bin/front-imx681-launcher.py').read_text()
need(rear.count('media-ctl -d "$MEDIA" -l')==2 and '[0]' not in '\n'.join(x for x in rear.splitlines() if 'media-ctl -d "$MEDIA" -l' in x),'rear route disable absent')
need(front.count("['media-ctl','-d',m,'-l'")==2 and '[0]' not in '\n'.join(x for x in front.splitlines() if "['media-ctl','-d',m,'-l'" in x),'front route disable absent')
# Real unified topology starts neutral.
fix=D/'ic-real-media-graph.normalized.txt'
cp=subprocess.run([str(D/'route-state.py'),str(fix),'--expect','neutral'],text=True,capture_output=True)
need(cp.returncode==0,'neutral fixture '+cp.stdout+cp.stderr)
# Synthetic exact rear-only and front-only states prove classifier/contract.
s=fix.read_text()
def setlink(text,entity,target,pad,on):
    pat=rf'(^- entity \d+: {re.escape(entity)} \([^\n]*\)\n.*?)(?=^- entity |\Z)'
    mm=re.search(pat,text,re.M|re.S); need(mm,'entity '+entity)
    b=mm.group(1)
    old=rf'(-> "{re.escape(target)}":{pad} )\[([^\]]*)\]'
    def sub(m): return m.group(1)+('[ENABLED]' if on else '[]')
    nb,n=re.subn(old,sub,b,count=1); need(n==1,'link '+entity+'->'+target)
    return text[:mm.start(1)]+nb+text[mm.end(1):]
rear_state=setlink(setlink(s,'msm_csiphy1','msm_csid0',0,True),'msm_csid0','msm_vfe0_rdi0',0,True)
front_state=setlink(setlink(s,'msm_csiphy2','msm_csid1',0,True),'msm_csid1','msm_vfe1_pix',0,True)
with tempfile.TemporaryDirectory(prefix='if-route-') as td:
    for name,data,expect in [('rear',rear_state,'rear-only'),('front',front_state,'front-only')]:
        p=Path(td)/(name+'.txt'); p.write_text(data)
        cp=subprocess.run([str(D/'route-state.py'),str(p),'--expect',expect],text=True,capture_output=True)
        need(cp.returncode==0,name+' state '+cp.stdout+cp.stderr)
for k,vv in {
 'status':'PASS_OFFLINE_UNIFIED_HANDOFF_RESET_ANALYSIS',
 'camera_runtime_performed':False,
 'front_repeated_open_proven':True,
 'front_repeated_streams_proven':4,
 'front_repeated_frames_proven':108,
 'rear_repeated_open_live_proven':False,
 'rear_route_auto_disable_proven':False,
 'front_route_auto_disable_proven':False,
 'same_boot_cross_camera_switch_proven':False,
 'production_default_promotion_authorized':False,
 'first_live_direction':'rear-to-front',
 'first_live_gate':'IG-unified-rear-to-front-same-boot-r16-r27',
 'second_live_direction':'front-to-rear',
 'second_live_gate':'IH-unified-front-to-rear-same-boot-r27-r16'
}.items(): need(r.get(k)==vv,'RESULT '+k)
need(all(r['route_handoff_contract'].values()),'handoff contract')
print('IF_VERIFY=PASS FRONT_RESET=SOURCE+4STREAM REAR_REPEAT=UNPROVEN ROUTE_AUTO_DISABLE=NO')
print('IF_HANDOFF=NEUTRAL_REQUIRED NEXT=IG_REAR_TO_FRONT THEN_IH_FRONT_TO_REAR')
