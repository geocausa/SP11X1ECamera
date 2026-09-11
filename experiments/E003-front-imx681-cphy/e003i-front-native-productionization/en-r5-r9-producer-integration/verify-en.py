#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import ctypes,hashlib,importlib.util,json,math,os,shutil,statistics,struct,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DZ=BASE/'dz-current-first-cq-publish-sensor-release'
EM=BASE/'em-r7-r9-template-free-composer'
EXPECTED={
 5:'818b65e439b3df9723ce2447e7f5d39f39a44c24cea35aa410bcef279393e4de',
 6:'7e6f2503165706b1f0f81069a33aae09244ccc5a1c5bc3ae6a8c3626d766199a',
 7:'681f17d83d289fba57548241bbb7db4219afbfde48495d680de969274720ea2e',
 8:'79804d678235f53429e4690c0d5e4a905873edde6652f002c878e2fad8634d2e',
 9:'1bd2e7cd98eb6ebc6c4161a34b3b8c72343d6e69232b11346f65496f79e33fda'}
GAIN_BITS=[0x3f802d08,0x3f800544,0x3f801646,0x3f801646,0x3f801646,0x3f801646]
GAIN_REC=struct.Struct('<IHHIIII')

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fbits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;assert s.loader;s.loader.exec_module(m);return m

# Parent/schedule provenance: only broaden IQ gain publication, never sensor writes.
dz=(DZ/'e003i-dz-six-frame-native-aec.c').read_text();en=(HERE/'e003i-en-six-frame-native-aec.c').read_text()
want=dz.replace('if (target <= 3U) {','if (target <= 6U) {',1).replace('producer-derived R5/R6','producer-derived R5-R9',1)
need(en==want,'parent source changed outside CQ feed range/success text')
need('if (target >= 2U && target <= 4U) {' in en,'sensor release gate changed')
need((HERE/'native-db-schedule.c').read_bytes()==(DZ/'native-db-schedule.c').read_bytes(),'sensor schedule source drift')
need((HERE/'native-db-schedule.h').read_bytes()==(DZ/'native-db-schedule.h').read_bytes(),'sensor schedule header drift')
gz=(DZ/'gain-feed.c').read_text();eg=(HERE/'gain-feed.c').read_text()
need(eg==gz.replace('generation > 3U','generation > 6U',1),'gain-feed source unexpected delta')

# Build the real AArch64 helper under -Werror.
with tempfile.TemporaryDirectory(prefix='en-verify-') as td:
    td=Path(td);helper=td/'helper';subprocess.run([str(HERE/'build-helper.sh'),str(helper)],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    need(helper.is_file() and helper.stat().st_size>0,'helper build')

    # Independent C IPC test through an actual pipe.
    so=td/'libgain.so';subprocess.run(['cc','-O2','-shared','-fPIC','-std=c11','-Wall','-Wextra','-Werror',str(HERE/'gain-feed.c'),'-lm','-o',str(so)],check=True)
    lib=ctypes.CDLL(str(so));fn=lib.e003i_gain_feed_publish;fn.argtypes=[ctypes.c_int,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_float];fn.restype=ctypes.c_int
    rd,wr=os.pipe()
    try:
        for gen,u in enumerate(GAIN_BITS,1):
            gain=fbits(u);need(fn(wr,gen,gen+3,ctypes.c_float(gain))==0,f'IPC publish G{gen}')
            raw=b''
            while len(raw)<GAIN_REC.size: raw+=os.read(rd,GAIN_REC.size-len(raw))
            magic,ver,n,g,r,bitsv,res=GAIN_REC.unpack(raw)
            need((magic,ver,n,g,r,bitsv,res)==(0x31464749,1,24,gen,gen+3,u,0),f'IPC decode G{gen}')
        need(fn(wr,7,10,ctypes.c_float(1.0))==-22,'IPC must reject G7')
        need(fn(wr,6,8,ctypes.c_float(1.0))==-22,'IPC must reject wrong request')
    finally:
        os.close(rd);os.close(wr)

    # Assemble one snapshot directory for the actual EN CLI, using only tracked fixtures.
    snap=td/'snap';snap.mkdir()
    for g in range(1,7):
        shutil.copy2(HERE/'fixtures'/f'STATS3A-G{g}.bin',snap/f'STATS3A-G{g}.bin')
        shutil.copy2(EM/'fixtures'/f'TLBG-G{g}.bin',snap/f'TLBG-G{g}.bin')
    out=td/'cli-out';manifest=td/'cli-result.json'
    subprocess.run([sys.executable,str(HERE/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(snap),'--gain-manifest',str(HERE/'FIXTURE-MANIFEST.json'),'--output-dir',str(out),'--manifest',str(manifest)],check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    cli=json.loads(manifest.read_text());need(cli['schema']=='sp11-e003i-en-r5-r9-producer-v1' and cli['status']=='PASS','CLI manifest')
    rows=cli['rows'];need([(r['generation'],r['request_target']) for r in rows]==[(1,None),(2,5),(3,6),(4,7),(5,8),(6,9)],'CLI mapping')
    need(all(r['awb_hold_previous'] is True and r['awb_triangle']==5 for r in rows),'EA AWB hold/triangle')
    for req,h in EXPECTED.items():
        p=out/f'R{req}-dynamic.bin';need(p.is_file() and p.stat().st_size==41088,f'CLI R{req} capsule');need(sha(p)==h,f'CLI R{req} hash')
    for g,r in enumerate(rows,1):
        need(r['gain_feed']['generation']==g and r['gain_feed']['request']==g+3,f'gain identity G{g}')
        need(r['gain_feed']['isp_gain_bits']==f'0x{GAIN_BITS[g-1]:08x}'==r['cq_isp_gain_bits'],f'gain bits G{g}')

    # Repeated in-process sequence after live-style prewarm. This exercises state reset and gives a conservative normal-user timing gate.
    P=load(HERE/'live-iq-producer.py','en_verify_producer');prod=P.Producer(td/'work');prod.prewarm()
    timing=[]
    for rep in range(8):
        prod.reset_sequence();seen=[]
        for g in range(1,7):
            st=(HERE/'fixtures'/f'STATS3A-G{g}.bin').read_bytes();tl=(EM/'fixtures'/f'TLBG-G{g}.bin').read_bytes()
            r,cap,_=prod.process(st,tl,fbits(GAIN_BITS[g-1]));seen.append((g,r['request_target']))
            if g>=2:
                timing.append(float(r['total_process_ms']));need(hashlib.sha256(cap).hexdigest()==EXPECTED[g+3],f'repeat {rep} R{g+3}')
        need(seen==[(1,None),(2,5),(3,6),(4,7),(5,8),(6,9)],f'repeat mapping {rep}')
    st=sorted(timing);p95=st[max(0,math.ceil(.95*len(st))-1)];mx=max(st);med=statistics.median(st)
    # Live runs CPU11/nice -20. Keep offline normal-user gate substantially below one 33.33ms frame.
    need(p95<20.0 and mx<25.0,f'timing margin p95={p95:.3f} max={mx:.3f}')
    result={'schema':'sp11-e003i-en-r5-r9-offline-integration-v1','status':'PASS_OFFLINE_R5_R9_INTEGRATION',
      'parent_diff':'CQ gain feed G1..G6 only; sensor release unchanged G2..G4','gain_feed_ipc':'G1..G6 PASS; G7/wrong-request rejected',
      'mapping':'R5<-G2,R6<-G3,R7<-G4,R8<-G5,R9<-G6','capsule_sha256':{str(k):v for k,v in EXPECTED.items()},
      'r5_r6_ea_byte_regression':'2/2','r7_r9_em_byte_regression':'3/3','awb_hold':'6/6','awb_triangle':5,
      'timing_samples':len(timing),'timing_gate':'PASS_MEASURED_EACH_RUN','timing_p95_budget_ms':20.0,'timing_max_budget_ms':25.0,'frame_interval_ms':33.333333,
      'linux_camera_runtime':False,'continuous_unrestricted_aec_proven':False}
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(f'EN_TIMING_OBSERVED median_ms={med:.6f} p95_ms={p95:.6f} max_ms={mx:.6f}')
    print(json.dumps(result,indent=2,sort_keys=True))
