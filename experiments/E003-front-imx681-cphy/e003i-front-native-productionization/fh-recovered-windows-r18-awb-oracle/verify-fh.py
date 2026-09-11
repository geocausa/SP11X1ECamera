#!/usr/bin/env python3
from pathlib import Path
import hashlib,importlib.util,json,re,struct,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fa/windows-r12-20260911/extracted')
ZIP=A.parent/'E003I-FA-EVIDENCE.zip'
LOG=A/'E003I-FA-oracle.log'
HOLDER=A/'E003I-FA-holder-output.txt'
SUMMARY=A/'CAPTURE-SUMMARY.txt'
PAIR=HERE/'ORACLE-PAIRS.txt'
FBP=BASE/'fb-dynamic-awb-cal-slot-replay/dynamic_awb.py'
HASHES={
 'log':'0e457e62fc614ea019da73babd2499a58cf46eff8350e9c8b012d20804059c02',
 'holder':'7ed06235a38bbcb733005e40bdd2bdf3084ab3f540db9e70fb1db7f58d77afe9',
 'summary':'4be6be2b2e13f73372e661482fb440548fa5238a52c8834714a2e64a6c41a97d',
 'zip':'7719f046515b3b6f5f71dc06f99bfe00b1858c80dee18a6dd13e33a6b94c78fa',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
for k,p in [('log',LOG),('holder',HOLDER),('summary',SUMMARY),('zip',ZIP)]:
    need(sha(p)==HASHES[k],f'{k} hash drift')
hs=HOLDER.read_text(errors='replace').replace('\r','')
need(hs.count('START_BEGIN')==1 and hs.count('START_STATUS=Success')==1,'one holder start')
need(hs.count('STOP_PASS')==1 and hs.count('FA_HOLDER_END')==1,'normal holder stop')
need('job_exit_code=0' in hs,'holder exit')
ss=SUMMARY.read_text(errors='replace').replace('\r','')
for t in ('requests_seen=4,5,6,7,8,9,10,11,12,13,14,15,16,17,18','raw_rows=30','stream_count=1','holder_stop=PASS','cdb_control_artifact=post_R12_rows_present_same_stream'):
    need(t in ss,'summary '+t)
with tempfile.TemporaryDirectory(prefix='e003i-fh-') as td:
    t=Path(td)/'pairs.txt'
    subprocess.run([str(HERE/'extract-fh.py'),str(LOG),str(t)],check=True,stdout=subprocess.DEVNULL)
    if PAIR.exists(): need(t.read_bytes()==PAIR.read_bytes(),'tracked pair drift')
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
FB=load(FBP,'fh_fb')
def fbits(h): return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]
def kv(line): return dict(re.findall(r'(\w+)=([0-9A-Fa-f]+)',line))
lines=[x.strip() for x in PAIR.read_text().splitlines() if x.strip()]
ga=[kv(x) for x in lines if x.startswith('FA_GA ')]
pub=[kv(x) for x in lines if x.startswith('FA_PUB ')]
need(len(ga)==len(pub)==15,'15 pairs')
core=FB.DynamicCalibratedAWB();rows=[]
for req,(a,p) in enumerate(zip(ga,pub),4):
    need(int(a['req'])==int(p['req'])==req,f'R{req} identity')
    rg,bg,lux,cct=[fbits(a[k]) for k in ('rg','bg','lux','cct')]
    o=core.run(rg,bg,lux,cct,1.0);z=o['gain_adjust']
    need(z['triangle']==int(a['tri']),f'R{req} triangle')
    need(z['vertices']==[int(a[k]) for k in ('v0','v1','v2')],f'R{req} vertices')
    need([FB.bits(x) for x in z['weights']]==[int(a[k],16) for k in ('w0','w1','w2')],f'R{req} weights')
    need([FB.bits(x) for x in z['cct_rgb']]==[int(a[k],16) for k in ('cctr','cctg','cctb')],f'R{req} nested CCT multiplier')
    need([FB.bits(x) for x in z['final_rgb']]==[int(a[k],16) for k in ('ar','ag','ab')],f'R{req} final GA')
    got=[FB.bits(o[k]) for k in ('R','G','B')]
    need(got==[int(p[k],16) for k in ('R','G','B')],f'R{req} published RGB')
    rows.append({'request':req,'slot':o['calibration_slot'],'region':o['calibration_region'],'triangle':z['triangle'],'published_gain_bits':[f'0x{x:08x}' for x in got],'published_cct':int(p['CCT'])})
out={
 'schema':'sp11-e003i-fh-recovered-windows-r18-awb-oracle-v1',
 'status':'PASS_RECOVERED_WINDOWS_R4_R18_AWB_15_OF_15_BIT_EXACT',
 'source_stream':'FA single Windows holder stream',
 'new_windows_streams':0,
 'requests':list(range(4,19)),
 'recovered_requests':list(range(13,19)),
 'fb_bit_exact':'15/15',
 'dynamic_slots':[r['slot'] for r in rows],
 'rows':rows,
 'archive_hashes':HASHES,
 'windows_stream_count':1,
 'holder_stop':'PASS',
 'continuous_aec_claimed':False,
}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
