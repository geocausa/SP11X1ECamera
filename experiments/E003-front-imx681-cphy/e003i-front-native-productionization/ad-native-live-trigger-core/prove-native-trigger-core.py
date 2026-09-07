#!/usr/bin/env python3
import argparse, ctypes, hashlib, importlib.util, json, pathlib, statistics, struct, subprocess, sys, tempfile, time

HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent
AB=BASE/'ab-clean-lux-reconstruction'
AC=BASE/'ac-clean-cct-reconstruction'
W=BASE/'w-request-stats-selection-trigger-oracle/ANALYSIS.json'

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def bits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def frombits(x): return struct.unpack('<f',struct.pack('<I',x))[0]
def need(c,m):
    if not c: raise RuntimeError(m)
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def pack_tables():
    def fa(v): return (ctypes.c_float*len(v))(*[float(x) for x in v])
    p04n=[];p04r=[];p05r=[]
    for ci in range(3):
        b=(AC/'fixtures'/f'E003I-AC36-P04-C{ci}.bin').read_bytes()
        for j in range(6): p04n += list(struct.unpack_from('<ff',b,j*0x18))
        for ri in range(6):
            d=(AC/'fixtures'/f'E003I-AC36-P04-C{ci}-R{ri}.bin').read_bytes()
            for j in range(5): p04r += list(struct.unpack_from('<fff',d,j*12))
    for ci in range(10):
        b=(AC/'fixtures'/f'E003I-AC36-P05-C{ci}.bin').read_bytes()
        for j in range(10): p05r += list(struct.unpack_from('<fff',b,j*12))
    return fa(p04n),fa(p04r),fa(p05r)

class Result(ctypes.Structure):
    _fields_=[('measured_luma',ctypes.c_float),('lux',ctypes.c_float),('agw_x',ctypes.c_float),('agw_y',ctypes.c_float),('fresh_cct',ctypes.c_float),('sum_weight',ctypes.c_float),('p01',ctypes.c_uint32),('valid',ctypes.c_uint32)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot-dir',type=pathlib.Path,required=True,help='directory containing STATS3A-0.bin ... STATS3A-5.bin')
    ap.add_argument('--baseline-bits',type=lambda x:int(x,0),required=True,help='bounded fixed-exposure history baseline seed')
    ap.add_argument('--iterations',type=int,default=500)
    ap.add_argument('--manifest',type=pathlib.Path,default=HERE/'RESULT.json')
    a=ap.parse_args()
    need(a.iterations>=20,'iterations too small')
    L=load('e003i_ad_luma',AB/'replay-measured-luma.py'); A=load('e003i_ad_lux',AB/'replay-lux-adjustment.py')
    sys.path.insert(0,str(AC)); C=load('e003i_ad_cct',AC/'cct_model.py')
    w=json.loads(W.read_text()); r4=w['request4_6_trigger_oracle'][0]
    need(int(r4['request_frame'])==4 and int(r4['source_generation'])==1,'W R4/G1 drift')
    need(int(r4['raw']['aec_lux_index'],16)==a.baseline_bits,'baseline seed does not match W R4 authority')
    engine=(AC/'fixtures/E003I-AC31-CCTENGINE.bin').read_bytes();anchors=(AC/'fixtures/E003I-AC31-CCTANCHORS.bin').read_bytes()
    ENG=(ctypes.c_ubyte*len(engine)).from_buffer_copy(engine);ANC=(ctypes.c_ubyte*len(anchors)).from_buffer_copy(anchors)
    P04N,P04R,P05R=pack_tables();baseline=f32(frombits(a.baseline_bits));target=0x42480000;k=0x429bcc0c
    with tempfile.TemporaryDirectory(prefix='e003i-ad-') as td:
        so=pathlib.Path(td)/'libe003i_trigger.so'
        cmd=['gcc','-O3','-shared','-fPIC','-std=c11','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror',str(HERE/'native-trigger-core.c'),'-lm','-o',str(so)]
        subprocess.run(cmd,check=True)
        lib=ctypes.CDLL(str(so));fn=lib.e003i_trigger_native
        fn.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_float,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float),ctypes.POINTER(Result)];fn.restype=ctypes.c_int
        def native(aec,awb):
            aa=(ctypes.c_ubyte*len(aec)).from_buffer_copy(aec);ww=(ctypes.c_ubyte*len(awb)).from_buffer_copy(awb);o=Result()
            rc=fn(aa,len(aec),ww,len(awb),ctypes.c_float(baseline),ENG,len(engine),ANC,len(anchors),P04N,P04R,P05R,ctypes.byref(o));return rc,o
        rows=[]; payloads=[]
        for i in range(6):
            p=a.snapshot_dir/f'STATS3A-{i}.bin';b=p.read_bytes();need(len(b)==0x51040,f'{p.name} size')
            magic,ver,hb=struct.unpack_from('<IHH',b,0);gen=struct.unpack_from('<Q',b,8)[0];seq,slot=struct.unpack_from('<II',b,16)
            need((magic,ver,hb)==(0x54534133,1,64),f'{p.name} header');need((gen,seq,slot)==(i+1,i+1,i&1),f'{p.name} identity')
            aec=b[0x40:0x14040];awb=b[0x15040:0x51040];payloads.append((aec,awb))
            meas=L.replay(aec);lux=A.algorithm001(L.bits(meas),target,L.bits(baseline),k)
            tmp=pathlib.Path(td)/f'awb-{i}.raw';tmp.write_bytes(awb);g=C.agw(tmp,lux)
            py={'measured_luma':meas,'lux':lux,'agw_x':float(g['x']),'agw_y':float(g['y']),'fresh_cct':float(g['cct']),'sum_weight':float(g['sumW']),'p01':g['p01'],'valid':g['valid']}
            rc,o=native(aec,awb); mism=[]
            for q in ('measured_luma','lux','agw_x','agw_y','fresh_cct','sum_weight'):
                if bits(getattr(o,q))!=bits(py[q]):mism.append(q)
            if o.p01!=py['p01']:mism.append('p01')
            if o.valid!=py['valid']:mism.append('valid')
            need(rc==0 and not mism,f'G{i+1} native differential mismatch rc={rc} fields={mism}')
            rows.append({'generation':i+1,'source_seq':i+1,'slot':i&1,'snapshot_sha256':hashlib.sha256(b).hexdigest(),'measured_luma_bits':f'0x{bits(o.measured_luma):08x}','lux_bits':f'0x{bits(o.lux):08x}','lux':float(o.lux),'agw_xy_bits':[f'0x{bits(o.agw_x):08x}',f'0x{bits(o.agw_y):08x}'],'fresh_cct_bits':f'0x{bits(o.fresh_cct):08x}','fresh_cct':float(o.fresh_cct),'sum_weight_bits':f'0x{bits(o.sum_weight):08x}','p01':o.p01,'valid':o.valid,'bit_exact_python':True})
        timing={}
        for idx in (1,2):
            aec,awb=payloads[idx];times=[]
            for _ in range(a.iterations):
                t=time.perf_counter_ns();rc,o=native(aec,awb);dt=(time.perf_counter_ns()-t)/1e6;need(rc==0,'native timing rc');times.append(dt)
            s=sorted(times);timing[f'G{idx+1}']={'iterations':a.iterations,'mean_ms':statistics.mean(times),'p95_ms':s[int(len(s)*.95)-1],'p99_ms':s[int(len(s)*.99)-1],'max_ms':max(times)}
        result={'schema':'sp11-e003i-ad-native-live-trigger-core-v1','status':'PASS','offline_only':True,'runtime_performed':False,'bounded_baseline':{'bits':f'0x{a.baseline_bits:08x}','value':baseline,'authority':'W request4 AEC lux seed; valid for bounded fixed-exposure Linux six-frame proof only','continuous_aec_claimed':False},'differential':{'generations':rows,'all_six_bit_exact':True},'native_build':{'command':' '.join(cmd),'source_sha256':sha(HERE/'native-trigger-core.c'),'library_sha256':sha(so),'fno_fast_math':True,'fp_contract_off':True},'timing_ms':timing,'deadline_classification':'Native trigger cost is negligible relative to 33.333 ms frame budget; combine with Stage X arbitrary-trigger native LSC path before live FIFO proof.','safety':{'source_generation_is_request_id':False,'request_mapping':'R5<-G2, R6<-G3','dynamic_continuous_aec_authorized':False,'bounded_r5_r6_integration_next':True},'next_gate':'compose live G2/G3 trigger -> front LSC -> template-free steady capsule and queue through existing deferred V4L2 IQ FIFO before R5/R6 provider gates'}
        a.manifest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        for r in rows: print(f"G{r['generation']} lux={r['lux']:.9f} cct={r['fresh_cct']:.9f} p01={r['p01']} valid={r['valid']} BIT_EXACT")
        print('G2_P95_MS',timing['G2']['p95_ms']);print('G3_P95_MS',timing['G3']['p95_ms']);print('E003I_AD_NATIVE_TRIGGER=PASS')
if __name__=='__main__': main()
