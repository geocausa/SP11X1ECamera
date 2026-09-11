#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,re,struct,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
DLL=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
ELP=BASE/'el-calibrated-awb-scalar-join/awb_scalar.py';PAIR=HERE/'ORACLE-PAIRS.txt'
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
HOOKS={0x6bf1a0:(64,'56ce25a26bb9e2a707bd5637364af4619c16631252d772b9281e173eb4cab371'),0x6bfa68:(48,'24eaf82d9f264c8e0363f1042e75b124bf5a679262191cf724bcf3a1386de5fe'),0x68f490:(64,'ca361c0cb1baec2e483f1a610e0c3bbb27577113c23bcea8db725a95800288db'),0x68fa00:(200,'12f2f1f9fe26e02eb5397325ae37c61bd4b43fe2f6560e6c1beeae12fa92c1eb')}
def need(x,m):
 if not x: raise AssertionError(m)
def sha(b): return hashlib.sha256(b).hexdigest()
need(sha(DLL.read_bytes())==DLL_SHA,'pinned DLL SHA')
import pefile
pe=pefile.PE(str(DLL))
for rva,(n,h) in HOOKS.items(): need(sha(pe.get_data(rva,n))==h,f'hook bytes {rva:x}')
oracle=(HERE/'oracle.cmd').read_text();ga_cmd=(HERE/'ga.cmd').read_text();pub_cmd=(HERE/'pub.cmd').read_text()
for t in ('QcDeviceMFT8380+0x6bfa68','QcDeviceMFT8380+0x68fa00','FA_BREAKPOINTS_ARMED'):need(t in oracle,'oracle '+t)
for t in ('dwo(@x19+0xa4)','dwo(@x19+0xa8)','dwo(@x19+0x78)','dwo(poi(@x19+0x88)+0xf49)','dwo(@x19+0x14)','dwo(@x19+0x1c)'):need(t in ga_cmd,'GA map '+t)
for t in ('qwo(@x23+0x128)','dwo(@x13+8)','dwo(@x13+0xc)','dwo(@x13+0x10)','dwo(@x13+0x14)','FA_CAPTURE_COMPLETE R=12'):need(t in pub_cmd,'PUB map '+t)
eg=json.loads((BASE/'eg-windows-awb-gain-adjust-oracle/RESULT.json').read_text()); need(eg['status']=='PASS_8_OF_8_BIT_EXACT' and eg['requests']==list(range(4,12)),'EG authority')
el=json.loads((BASE/'el-calibrated-awb-scalar-join/RESULT.json').read_text()); need(el['status']=='PASS_OFFLINE_JOIN' and el['triangle_state_differential']=='8/8','EL authority')
if not PAIR.exists():
 print('FA_STATIC_VERIFY=PASS DLL_AND_HOOKS_PINNED EG_EL_AUTHORITY=PASS');raise SystemExit(0)
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
EL=load(ELP,'fa_el')
def fb(h):return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]
def kv(line):return dict(re.findall(r'(\w+)=([0-9A-Fa-f]+)',line))
lines=[x.strip() for x in PAIR.read_text().splitlines() if x.strip()];ga=[kv(x) for x in lines if x.startswith('FA_GA ')];pub=[kv(x) for x in lines if x.startswith('FA_PUB ')]
need(len(ga)==len(pub)==9,'9 paired samples');core=EL.CalibratedAWB();rows=[]
for i,(a,p) in enumerate(zip(ga,pub),4):
 need(int(a['req'])==int(p['req'])==i,f'R{i} request identity')
 rg,bg,lux,cct=[fb(a[k]) for k in ('rg','bg','lux','cct')];o=core.run(rg,bg,lux,cct,1.0);z=o['gain_adjust']
 need(z['triangle']==int(a['tri']),f'R{i} triangle');need(z['vertices']==[int(a[k]) for k in ('v0','v1','v2')],f'R{i} vertices')
 need([EL.bits(x) for x in z['weights']]==[int(a[k],16) for k in ('w0','w1','w2')],f'R{i} weights')
 need([EL.bits(x) for x in z['cct_rgb']]==[int(a[k],16) for k in ('cctr','cctg','cctb')],f'R{i} CCT multiplier')
 need([EL.bits(x) for x in z['final_rgb']]==[int(a[k],16) for k in ('ar','ag','ab')],f'R{i} final GA')
 got=[EL.bits(o[k]) for k in ('R','G','B')];exp=[int(p[k],16) for k in ('R','G','B')];need(got==exp,f'R{i} published RGB');need(int(cct)==int(p['CCT']),f'R{i} published CCT')
 rows.append({'request':i,'triangle':z['triangle'],'gain_bits':[f'0x{x:08x}' for x in got],'cct':int(p['CCT'])})
out={'schema':'sp11-e003i-fa-windows-r12-awb-gain-adjust-oracle-v1','status':'PASS_9_OF_9_STATEFUL_BIT_EXACT','requests':list(range(4,13)),'new_request':12,'dll_sha256':DLL_SHA,'same_run_stateful_gain_adjust':'9/9','same_run_publisher_rgb':'9/9','same_run_publisher_cct':'9/9','r12':rows[-1],'windows_streams':1,'continuous_aec_claimed':False}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
