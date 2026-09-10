#!/usr/bin/env python3
from pathlib import Path
import argparse,ctypes,hashlib,json,struct,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
AD=BASE/'ad-native-live-trigger-core'
AC=BASE/'ac-clean-cct-reconstruction'
W=BASE/'w-request-stats-selection-trigger-oracle/ANALYSIS.json'
DEFAULT_DP=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-dp/attempt1-iq-awb-zero-weight-20260910T2020/runtime-output/producer/STATS3A-G1.bin')

class Result(ctypes.Structure):
    _fields_=[('measured_luma',ctypes.c_float),('lux',ctypes.c_float),('agw_x',ctypes.c_float),('agw_y',ctypes.c_float),('fresh_cct',ctypes.c_float),('sum_weight',ctypes.c_float),('p01',ctypes.c_uint32),('valid',ctypes.c_uint32)]

def bits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def fb(u): return struct.unpack('<f',struct.pack('<I',u))[0]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def tables():
    def fa(v): return (ctypes.c_float*len(v))(*[float(x) for x in v])
    p04n=[];p04r=[];p05r=[]
    for ci in range(3):
        b=(AC/'fixtures'/f'E003I-AC36-P04-C{ci}.bin').read_bytes()
        for j in range(6): p04n+=list(struct.unpack_from('<ff',b,j*0x18))
        for ri in range(6):
            d=(AC/'fixtures'/f'E003I-AC36-P04-C{ci}-R{ri}.bin').read_bytes()
            for j in range(5): p04r+=list(struct.unpack_from('<fff',d,j*12))
    for ci in range(10):
        b=(AC/'fixtures'/f'E003I-AC36-P05-C{ci}.bin').read_bytes()
        for j in range(10): p05r+=list(struct.unpack_from('<fff',b,j*12))
    return fa(p04n),fa(p04r),fa(p05r)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot-dir',type=Path,required=True)
    ap.add_argument('--dp-g1',type=Path,default=DEFAULT_DP)
    ap.add_argument('--manifest',type=Path,default=HERE/'RESULT.json')
    a=ap.parse_args()
    w=json.loads(W.read_text()); baseline_bits=int(w['request4_6_trigger_oracle'][0]['raw']['aec_lux_index'],16); baseline=fb(baseline_bits)
    eng=(AC/'fixtures/E003I-AC31-CCTENGINE.bin').read_bytes(); anc=(AC/'fixtures/E003I-AC31-CCTANCHORS.bin').read_bytes()
    ENG=(ctypes.c_ubyte*len(eng)).from_buffer_copy(eng); ANC=(ctypes.c_ubyte*len(anc)).from_buffer_copy(anc); P04N,P04R,P05R=tables()
    with tempfile.TemporaryDirectory(prefix='e003i-dr-') as td:
        td=Path(td); libs={}
        for name,src in [('ad',AD/'native-trigger-core.c'),('dr',HERE/'native-trigger-core.c')]:
            so=td/f'{name}.so'
            subprocess.run(['gcc','-O3','-shared','-fPIC','-std=c11','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror',str(src),'-lm','-o',str(so)],check=True)
            lib=ctypes.CDLL(str(so)); fn=lib.e003i_trigger_native
            fn.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_float,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float),ctypes.POINTER(Result)]
            fn.restype=ctypes.c_int; libs[name]=(so,fn)
        def run(fn,aec,awb):
            aa=(ctypes.c_ubyte*len(aec)).from_buffer_copy(aec); ww=(ctypes.c_ubyte*len(awb)).from_buffer_copy(awb); o=Result()
            rc=fn(aa,len(aec),ww,len(awb),ctypes.c_float(baseline),ENG,len(eng),ANC,len(anc),P04N,P04R,P05R,ctypes.byref(o))
            return rc,o
        normal=[]
        for i in range(6):
            b=(a.snapshot_dir/f'STATS3A-{i}.bin').read_bytes(); assert len(b)==0x51040
            aec=b[0x40:0x14040]; awb=b[0x15040:0x51040]
            ra,oa=run(libs['ad'][1],aec,awb); rr,orr=run(libs['dr'][1],aec,awb)
            assert ra==rr==0
            for q in ('measured_luma','lux','agw_x','agw_y','fresh_cct','sum_weight'):
                assert bits(getattr(oa,q))==bits(getattr(orr,q)),(i,q)
            assert oa.p01==orr.p01 and oa.valid==orr.valid
            normal.append({'generation':i+1,'bit_exact_ad':True,'p01':orr.p01,'valid':orr.valid})
        # Deterministic zero-weight hostile case: valid AEC with no AWB candidates.
        b=(a.snapshot_dir/'STATS3A-0.bin').read_bytes(); aec=b[0x40:0x14040]; zero_awb=bytes(0x3c000)
        rr,o=run(libs['dr'][1],aec,zero_awb)
        assert rr==1 and o.p01==0 and o.valid==0 and bits(o.sum_weight)==0 and bits(o.agw_x)==0 and bits(o.agw_y)==0 and bits(o.fresh_cct)==0
        exact_dp=None
        if a.dp_g1.exists():
            b=a.dp_g1.read_bytes(); assert sha(a.dp_g1)=='1344836e819a28d4a9aef5f9d91908ca6806d59b08bec0f2c185fb56149087ea'
            aec=b[0x40:0x14040]; awb=b[0x15040:0x51040]; rr,o=run(libs['dr'][1],aec,awb)
            assert rr==1 and o.p01==8 and o.valid==0 and bits(o.sum_weight)==0 and bits(o.agw_x)==0 and bits(o.agw_y)==0 and bits(o.fresh_cct)==0
            exact_dp={'sha256':sha(a.dp_g1),'rc':rr,'measured_luma_bits':f'0x{bits(o.measured_luma):08x}','lux_bits':f'0x{bits(o.lux):08x}','p01':o.p01,'valid':o.valid}
        result={'schema':'sp11-e003i-dr-native-awb-zero-weight-hold-v1','status':'PASS','runtime_performed':False,'hold_code':1,'normal_ad_regression':normal,'all_normal_bit_exact_ad':True,'zero_weight_synthetic':{'rc':1,'p01':0,'valid':0,'fresh_target_xy':[0.0,0.0]},'dp_attempt1_g1':exact_dp,'source_sha256':sha(HERE/'native-trigger-core.c'),'windows_authority':'DQ zero aggregate weight -> target (0,0) -> higher CAWB retains previous AWB state','continuous_aec_claimed':False}
        a.manifest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('DR_NORMAL_AD_BIT_EXACT=6/6')
        print('DR_ZERO_WEIGHT_HOLD=PASS')
        if exact_dp: print('DR_DP_G1_HOLD=PASS',exact_dp)
        print('DR_VERIFY=PASS')
if __name__=='__main__': main()
