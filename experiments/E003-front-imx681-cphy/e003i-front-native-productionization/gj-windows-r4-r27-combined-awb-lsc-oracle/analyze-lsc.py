#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse,ctypes,hashlib,importlib.util,json,math,struct,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
DXFILE=BASE/'dx-parent-cq-gain-feed/live-iq-producer.py'
XFILE=BASE/'x-native-live-lsc-deadline/prove-native-live-lsc-deadline.py'
PACK=HERE.parents[1]/'e003h-iq-producer-0073-static/prove-lsc-live-staging-pack.py'

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
def bitsf(b,o):return struct.unpack_from('<f',b,o)[0]
def fbits(v):return struct.unpack('<I',struct.pack('<f',float(v)))[0]
def bitsu(b,o):return struct.unpack_from('<I',b,o)[0]
def need(v,m):
    if not v:raise RuntimeError(m)

def run_parsed(lsc,parsed:bytes,lux:float,cct:float):
    need(len(parsed)==0x12bec,'parsed Tintless size')
    need(bitsu(parsed,0)&2 and bitsu(parsed,4)==0x300,'parsed Tintless layout')
    x22,csel,asel=lsc._select_x22(lux,cct)
    x23=lsc.CL.calibrate(x22,lsc.gold,lsc.otp)
    pre=lsc.X.resample(lsc.res,x23)
    m=lsc.mem
    dirty=lsc.C.update_wrapper_config_front(m,lsc.X.WRAP,lsc.X.X1)
    ca=struct.unpack('<Q',m.mem_read(lsc.X.WRAP+0x128,8))[0]
    if ca==0:
        ca=lsc.X.CORE;m.mem_write(lsc.X.WRAP+0x128,struct.pack('<Q',ca));dirty=True
    if dirty:
        lsc.C.initialize_core_front_mode2(m,lsc.X.CORE,lsc.X.WRAP)
        lsc.state=bytearray(m.mem_read(lsc.X.CORE,lsc.C.CORE_BYTES))
    seed=lsc.K.output_seed('zero')
    outb=bytearray(seed[:0xdd0])
    SA=(ctypes.c_ubyte*len(lsc.state)).from_buffer(lsc.state)
    # Windows x2 oracle is bounded at the highest byte consumed by the core;
    # native standalone ABI still requires the full allocation length.
    parsed_full=parsed+bytes(0x12c20-len(parsed))
    PA=(ctypes.c_ubyte*len(parsed_full)).from_buffer_copy(parsed_full)
    FA=(ctypes.c_float*884).from_buffer_copy(pre)
    OA=(ctypes.c_float*884).from_buffer(outb)
    need(lsc.core(SA,len(lsc.state),PA,len(parsed_full),FA,OA)==0,'native Tintless rc')
    m.mem_write(lsc.X.IN,pre+bytes(0x20))
    m.mem_write(lsc.X.OUT,outb+seed[0xdd0:])
    lsc.C._wrapper_temporal_blend(m,lsc.X.WRAP,lsc.X.D3,lsc.X.D4)
    got=m.mem_read(lsc.X.OUT,0xdf0)
    wire=lsc.K.wire_from_output(got)
    cr,ar=csel['ratio'],asel['ratio']
    return wire,{
      'lux':float(lux),'cct':float(cct),
      'cct_selector_mode':csel['mode'],
      'cct_ratio_bits':None if cr is None else f'0x{fbits(cr):08x}',
      'cct_ratio':None if cr is None else float(cr),
      'aec_selector_mode':asel['mode'],
      'aec_ratio_bits':None if ar is None else f'0x{fbits(ar):08x}',
      'aec_ratio':None if ar is None else float(ar),
      'x22_sha256':sha(x22),'pretintless_sha256':sha(pre),
      'tintless_output_sha256':sha(got[:0xdd0]),
      'lsc0_sha256':sha(wire[0]),'lsc1_sha256':sha(wire[1]),
      'lsc2_sha256':sha(wire[2]),'gic_sha256':sha(wire[3])
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('capture_dir',type=Path)
    ap.add_argument('--end-request',type=int,default=27)
    ap.add_argument('--result',type=Path,default=HERE/'LSC-RESULT.json')
    a=ap.parse_args()
    need(4<=a.end_request<=27,'end request range')
    DX=load(DXFILE,'ed_dx')
    X=load(XFILE,'ed_x')
    P=load(PACK,'ed_pack')
    with tempfile.TemporaryDirectory(prefix='e003i-ed-') as td:
        so=Path(td)/'libe003i_tintless.so'
        X.compile_native(so)
        lsc=DX.DynamicLsc(so)
        rows=[]
        for r in range(4,a.end_request+1):
            stats=(a.capture_dir/f'R{r:02d}_TINTLESS_STATS.bin').read_bytes()
            trig=(a.capture_dir/f'R{r:02d}_TRIGGER.bin').read_bytes()
            staging=(a.capture_dir/f'R{r:02d}_LSC_STAGING.bin').read_bytes()
            need(len(stats)==0x12bec and len(trig)==0x100 and len(staging)==P.STAGING_BYTES,f'R{r} file size')
            need(bitsu(stats,0)==3 and bitsu(stats,4)==0x300,f'R{r} stats header')
            lux=bitsf(trig,0x38);cct=bitsf(trig,0x48)
            need(math.isfinite(lux) and math.isfinite(cct) and lux>0 and cct>0,f'R{r} trigger finite')
            # Pin front Sensor2 geometry from the same request trigger.
            need(bitsu(trig,0xb8)==0,f'R{r} Bayer')
            need((bitsu(trig,0xbc),bitsu(trig,0xc0),bitsu(trig,0xc4),bitsu(trig,0xc8))==(3840,2160,3840,2160),f'R{r} geometry')
            need((bitsu(trig,0xe8),bitsu(trig,0xec),bitsu(trig,0xf0))==(104,496,6528),f'R{r} crop/black')
            wire,meta=run_parsed(lsc,stats,lux,cct)
            geo,w0,w1,w2=P.pack_live_staging(staging)
            wgic=(w0+w1)[0x22e:0x42e]
            need(not any(w2),f'R{r} captured LSC2 nonzero')
            eq={'lsc0':wire[0]==w0,'lsc1':wire[1]==w1,'lsc2':wire[2]==w2,'gic':wire[3]==wgic}
            need(all(eq.values()),f'R{r} clean wire mismatch {eq}')
            rows.append({
              'request':r,'bank':geo['bank'],
              'stats_sha256':sha(stats),'trigger_sha256':sha(trig),'staging_sha256':sha(staging),
              **meta,
              'captured_lsc0_sha256':sha(w0),'captured_lsc1_sha256':sha(w1),
              'captured_lsc2_sha256':sha(w2),'captured_gic_sha256':sha(wgic),
              'wire_byte_exact':eq
            })
    banks=[x['bank'] for x in rows]
    need(banks==[1 if i%2==0 else 0 for i in range(len(rows))],f'bank parity {banks}')
    result={
      'schema':f'sp11-e003i-gj-r4-r{a.end_request}-clean-lsc-replay-v1',
      'status':f'PASS_WINDOWS_LSC_R4_R{a.end_request}_CLEANROOM_REPLAY',
      'requests':list(range(4,a.end_request+1)),
      'decimal_fixed_capture':True,
      'rejected_attempt1':None,
      'accepted_capture':str(a.capture_dir),
      'stats_layout':{'word0':3,'records':768,'bytes':0x12bec},
      'trigger_bytes':0x100,'staging_bytes':0x18a0,
      'bank_values':banks,
      'clean_lsc_replay':f'{len(rows)}/{len(rows)} byte-exact LSC0/LSC1/LSC2/GIC',
      'native_tintless_core':True,
      'production_selector_reused_from':'DX DynamicLsc',
      'rows':rows,
      'linux_camera_runtime':False,
      'continuous_aec_claimed':False,
      'next_gate':'join GJ combined Windows AWB + LSC authority through R27 before any R25+ Linux live candidate'
    }
    a.result.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(f'GJ_LSC_CLEAN_REPLAY={len(rows)}/{len(rows)} PASS')
    print('GJ_LSC_BANK_PARITY='+','.join(map(str,banks))+' PASS')
    for x in rows:
        print(f"R{x['request']} LUX={x['lux']:.6f} CCT={x['cct']:.1f} CCTSEL={x['cct_selector_mode']} AECSEL={x['aec_selector_mode']} LSC0={x['lsc0_sha256'][:16]}")
    print('GJ_LSC_ANALYZE=PASS')
if __name__=='__main__':main()
