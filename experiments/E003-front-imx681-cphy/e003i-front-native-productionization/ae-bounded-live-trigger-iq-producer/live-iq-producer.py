#!/usr/bin/env python3
from __future__ import annotations
import argparse, ctypes, errno, hashlib, importlib.util, json, os, pathlib, struct, subprocess, sys, tempfile, time

HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
AB=BASE/'ab-clean-lux-reconstruction'; AC=BASE/'ac-clean-cct-reconstruction'; AD=BASE/'ad-native-live-trigger-core'
EFILE=BASE/'e-template-free-capsule/build-template-free-0076-capsules.py'
XFILE=BASE/'x-native-live-lsc-deadline/prove-native-live-lsc-deadline.py'
NFILE=BASE/'n-titan680-tlbg-parser/titan680-tlbg-parser.py'
MFILE=BASE/'m-stats-only-lsc-request-state/generate-stats-only-front-lsc.py'
KFILE=BASE/'k-cleanroom-lsc-backend/generate-cleanroom-front-lsc-wire.py'
IFILE=BASE/'i-cleanroom-tintless/cleanroom-tintless-helpers.py'
GFILE=BASE/'g-cleanroom-lsc-upstream/cleanroom-front-lsc.py'
WFILE=BASE/'w-request-stats-selection-trigger-oracle/ANALYSIS.json'

STATS3A_BYTES=0x51040; TLBG_BYTES=0xf020; IQ_BYTES=41088
STATS3A_MAGIC=0x54534133; TLBG_MAGIC=0x47424c54
BASELINE_BITS=0x43b302c7
INITIAL_PREV_X_BITS=0x3f1129ca; INITIAL_PREV_Y_BITS=0x3f00e486
UPPER_LEAF_SHA='f0c84bd42df54e3b18abb41d787e922d98f82f0aa72230c90aaea48f94994ee8'

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def bits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def frombits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
def f32(x): return frombits(bits(x))
def need(v,m):
    if not v: raise RuntimeError(m)
def compile_so(src,out,extra=()):
    cmd=['gcc','-O3','-shared','-fPIC','-std=c11','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror',str(src),*extra,'-o',str(out)]
    subprocess.run(cmd,check=True);return cmd

def parse_3a(b:bytes):
    need(len(b)==STATS3A_BYTES,'3A size')
    magic,ver,hb=struct.unpack_from('<IHH',b,0);gen=struct.unpack_from('<Q',b,8)[0];seq,slot=struct.unpack_from('<II',b,16)
    need((magic,ver,hb)==(STATS3A_MAGIC,1,64),'3A header')
    need(struct.unpack_from('<6I',b,24)==(0,0x14000,0x14000,0x1000,0x15000,0x3c000),'3A layout')
    need(struct.unpack_from('<I',b,48)[0]&1 and gen and seq and slot<2,'3A identity')
    return (gen,seq,slot),b[0x40:0x14040],b[0x15040:0x51040]
def parse_tlbg(b:bytes):
    need(len(b)==TLBG_BYTES,'TLBG size')
    magic,ver,hb=struct.unpack_from('<IHH',b,0);gen=struct.unpack_from('<Q',b,8)[0];seq,slot,rb,flags=struct.unpack_from('<IIII',b,16)
    need((magic,ver,hb,rb)==(TLBG_MAGIC,1,32,0xf000) and flags&1 and gen and seq and slot<2,'TLBG header')
    return (gen,seq,slot),b[32:]

class TriggerResult(ctypes.Structure):
    _fields_=[('measured_luma',ctypes.c_float),('lux',ctypes.c_float),('agw_x',ctypes.c_float),('agw_y',ctypes.c_float),('fresh_cct',ctypes.c_float),('sum_weight',ctypes.c_float),('p01',ctypes.c_uint32),('valid',ctypes.c_uint32)]

class NativeTrigger:
    def __init__(self,so:pathlib.Path):
        self.CCT=load(AC/'cct_model.py','ae_cct'); self.prev_x=frombits(INITIAL_PREV_X_BITS);self.prev_y=frombits(INITIAL_PREV_Y_BITS)
        def fa(v):return (ctypes.c_float*len(v))(*[float(x) for x in v])
        p04n=[];p04r=[];p05r=[]
        for ci in range(3):
            b=(AC/'fixtures'/f'E003I-AC36-P04-C{ci}.bin').read_bytes()
            for j in range(6):p04n+=list(struct.unpack_from('<ff',b,j*0x18))
            for ri in range(6):
                d=(AC/'fixtures'/f'E003I-AC36-P04-C{ci}-R{ri}.bin').read_bytes()
                for j in range(5):p04r+=list(struct.unpack_from('<fff',d,j*12))
        for ci in range(10):
            b=(AC/'fixtures'/f'E003I-AC36-P05-C{ci}.bin').read_bytes()
            for j in range(10):p05r+=list(struct.unpack_from('<fff',b,j*12))
        self.p04n,self.p04r,self.p05r=fa(p04n),fa(p04r),fa(p05r)
        eng=(AC/'fixtures/E003I-AC31-CCTENGINE.bin').read_bytes();anc=(AC/'fixtures/E003I-AC31-CCTANCHORS.bin').read_bytes();self.engb,self.ancb=eng,anc
        self.eng=(ctypes.c_ubyte*len(eng)).from_buffer_copy(eng);self.anc=(ctypes.c_ubyte*len(anc)).from_buffer_copy(anc)
        lib=ctypes.CDLL(str(so));self.fn=lib.e003i_trigger_native
        self.fn.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_float,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float),ctypes.POINTER(TriggerResult)];self.fn.restype=ctypes.c_int
        w=json.loads(WFILE.read_text());r4=w['request4_6_trigger_oracle'][0];need(int(r4['raw']['aec_lux_index'],16)==BASELINE_BITS,'W R4 baseline authority drift')
    def run(self,aec:bytes,awb:bytes):
        aa=(ctypes.c_ubyte*len(aec)).from_buffer_copy(aec);ww=(ctypes.c_ubyte*len(awb)).from_buffer_copy(awb);o=TriggerResult();t=time.perf_counter_ns()
        rc=self.fn(aa,len(aec),ww,len(awb),ctypes.c_float(frombits(BASELINE_BITS)),self.eng,len(self.engb),self.anc,len(self.ancb),self.p04n,self.p04r,self.p05r,ctypes.byref(o));need(rc==0,f'native trigger rc={rc}')
        t1=time.perf_counter_ns();fx,fy,fc=self.CCT.temporal(o.agw_x,o.agw_y,self.prev_x,self.prev_y);self.prev_x,self.prev_y=fx,fy
        return o,fx,fy,fc,(t1-t)/1e6

class DynamicLsc:
    def __init__(self,so:pathlib.Path):
        self.X=load(XFILE,'ae_x');self.N=load(NFILE,'ae_n');self.M=load(MFILE,'ae_m');self.K=load(KFILE,'ae_k');self.C=load(IFILE,'ae_i');self.CL=load(GFILE,'ae_g');self.DEC=load(self.X.DECFILE,'ae_dec');self.GOLD=load(self.X.GOLDFILE,'ae_gold')
        leaf_4bd,leaf_4bf,gold,otp=self.X.front_authority(self.DEC,self.CL,self.GOLD)
        blob=self.X.TUNING.read_bytes();h=self.DEC.parse_header(blob);recs,_=self.DEC.parse_symbol_table(blob,h['sections'][0],h['sections'][1]);obj=h['sections'][1]
        leaf_4b9=self.DEC.data_bytes(blob,obj,recs[0x4b9]);leaf_4bb=self.DEC.data_bytes(blob,obj,recs[0x4bb]);upper=self.DEC.data_bytes(blob,obj,recs[0x4c3]);need(sha(upper)==UPPER_LEAF_SHA,'upper front LSC leaf drift')
        self.lower_cct_leaves=(leaf_4b9,leaf_4bb,leaf_4bd,leaf_4bf);self.upper=upper;self.gold,self.otp=gold,otp
        self.core,self.res=self.X.api(so);self.x1,_=self.M.build_front_x1();self.reset()
    def reset(self):
        self.mem=self.X.mem0(self.K,self.C,self.M,self.x1);self.state=None
    def _lower_cct(self,cct:float):
        c=f32(cct);a,b,cold,warm=self.lower_cct_leaves
        if c < f32(2500.0): return a,{'mode':'leaf_0x4b9','ratio':None}
        if c < f32(2700.0):
            r=f32((c-f32(2500.0))/f32(200.0));return self.CL.interpolate_leaf(a,b,r),{'mode':'gap_2500_2700','ratio':r}
        if c < f32(3200.0): return b,{'mode':'leaf_0x4bb','ratio':None}
        if c < f32(3400.0):
            r=f32((c-f32(3200.0))/f32(200.0));return self.CL.interpolate_leaf(b,cold,r),{'mode':'gap_3200_3400','ratio':r}
        if c < f32(4500.0): return cold,{'mode':'leaf_0x4bd','ratio':None}
        if c < f32(5000.0):
            r=f32((c-f32(4500.0))/f32(500.0));return self.CL.interpolate_leaf(cold,warm,r),{'mode':'gap_4500_5000','ratio':r}
        return warm,{'mode':'leaf_0x4bf','ratio':None}
    def _select_x22(self,lux:float,cct:float):
        lower,cd=self._lower_cct(cct);L=f32(lux)
        if L < f32(390.0): return lower,cd,{'mode':'lower_aec','ratio':None}
        if L < f32(490.0):
            r=f32((L-f32(390.0))/f32(100.0));return self.CL.interpolate_leaf(lower,self.upper,r),cd,{'mode':'gap_390_490','ratio':r}
        return self.upper,cd,{'mode':'upper_aec','ratio':None}
    def run(self,tlbg_raw:bytes,lux:float,cct:float):
        t0=time.perf_counter_ns();x22,csel,asel=self._select_x22(lux,cct);x23=self.CL.calibrate(x22,self.gold,self.otp);pre=self.X.resample(self.res,x23);parsed=self.N.parse_titan680_tlbg(tlbg_raw);t1=time.perf_counter_ns()
        m=self.mem;dirty=self.C.update_wrapper_config_front(m,self.X.WRAP,self.X.X1);ca=struct.unpack('<Q',m.mem_read(self.X.WRAP+0x128,8))[0]
        if ca==0:ca=self.X.CORE;m.mem_write(self.X.WRAP+0x128,struct.pack('<Q',ca));dirty=True
        if dirty:self.C.initialize_core_front_mode2(m,self.X.CORE,self.X.WRAP);self.state=bytearray(m.mem_read(self.X.CORE,self.C.CORE_BYTES))
        seed=self.K.output_seed('zero');outb=bytearray(seed[:0xdd0]);SA=(ctypes.c_ubyte*len(self.state)).from_buffer(self.state);PA=(ctypes.c_ubyte*len(parsed)).from_buffer_copy(parsed);FA=(ctypes.c_float*884).from_buffer_copy(pre);OA=(ctypes.c_float*884).from_buffer(outb);need(self.core(SA,len(self.state),PA,len(parsed),FA,OA)==0,'native Tintless rc')
        m.mem_write(self.X.IN,pre+bytes(0x20));m.mem_write(self.X.OUT,outb+seed[0xdd0:]);self.C._wrapper_temporal_blend(m,self.X.WRAP,self.X.D3,self.X.D4);got=m.mem_read(self.X.OUT,0xdf0);wire=self.K.wire_from_output(got);t2=time.perf_counter_ns()
        cr,ar=csel['ratio'],asel['ratio']
        return wire,{'cct_selector_mode':csel['mode'],'cct_ratio_bits':None if cr is None else f'0x{bits(cr):08x}','cct_ratio':None if cr is None else float(cr),'aec_selector_mode':asel['mode'],'aec_ratio_bits':None if ar is None else f'0x{bits(ar):08x}','aec_ratio':None if ar is None else float(ar),'x22_sha256':sha(x22),'pretintless_sha256':sha(pre),'tintless_output_sha256':sha(got[:0xdd0]),'lsc0_sha256':sha(wire[0]),'lsc1_sha256':sha(wire[1]),'lsc2_sha256':sha(wire[2]),'gic_sha256':sha(wire[3]),'pre_parse_ms':(t1-t0)/1e6,'tintless_wire_ms':(t2-t1)/1e6}

class Composer:
    def __init__(self):
        self.E=load(EFILE,'ae_e');E=self.E
        _e,self.variant,self.main,self.raw4,self.slot4,self.startup,self.payloads,self.sp,self.pp=E.static_recipe(REPO)
        self.base={req:self._base_state(req) for req in (5,6)}
    def _base_state(self,req):
        E=self.E;raw,slot,source=E.raw_request(REPO,req,self.raw4,self.slot4);values=[[0]*6 for _ in E.MODULES];vmask=[0]*len(E.MODULES)
        for r in self.variant['dynamic_register_fields']:
            off=int(r['field'],16);ro=int(r['register_offset'],16);mi,si=E.REG_SLOT[ro];values[mi][si]=struct.unpack_from('<I',raw,off)[0];vmask[mi]|=1<<si
        pay=[slot[o:o+n] for _,o,n in E.DMI_SOURCE];pmask=[0]*len(E.MODULES)
        for mi,indices in {1:[0],2:[1,2,3],4:[4],5:[5],6:[6],7:[7,8,9],8:[10,11,12,13]}.items():
            for j,_ in enumerate(indices):pmask[mi]|=1<<j
        module=bytearray()
        for i in range(len(E.MODULES)):module+=struct.pack('<BBH6I4x',vmask[i],pmask[i],0,*values[i])
        need(len(module)==0x120,'module bytes');return {'module':bytes(module),'payload':pay,'source':source}
    def compose(self,req,wire):
        b=self.base[req];pay=list(b['payload']);pay[1],pay[2],pay[3],pay[4]=wire;state={'module':b['module'],'payload':pay,'source':b['source']};t=time.perf_counter_ns();cap,desc=self.E.compose(req,self.main,self.startup,self.payloads,self.sp,self.pp,state);dt=(time.perf_counter_ns()-t)/1e6
        need(len(cap)==IQ_BYTES,'capsule size');return cap,desc,dt

class Producer:
    def __init__(self,work:pathlib.Path):
        work.mkdir(parents=True,exist_ok=True);self.work=work
        self.trigger_so=work/'libtrigger.so';self.tintless_so=work/'libtintless.so'
        compile_so(AD/'native-trigger-core.c',self.trigger_so,('-lm',));X=load(XFILE,'ae_x_compile');X.compile_native(self.tintless_so)
        self.trigger=NativeTrigger(self.trigger_so);self.lsc=DynamicLsc(self.tintless_so);self.composer=Composer();self.rows=[]
    def process(self,stats3a:bytes,tlbg:bytes):
        id3,aec,awb=parse_3a(stats3a);idt,tlraw=parse_tlbg(tlbg);need(id3==idt,'3A/TLBG identity mismatch');gen,seq,slot=id3;t0=time.perf_counter_ns();tr,fx,fy,fc,tr_ms=self.trigger.run(aec,awb);wire,ls=self.lsc.run(tlraw,tr.lux,fc);cap=desc=comp_ms=None;req=None
        if gen in (2,3):req=gen+3;cap,desc,comp_ms=self.composer.compose(req,wire)
        row={'generation':gen,'source_seq':seq,'slot':slot,'request_target':req,'measured_luma_bits':f'0x{bits(tr.measured_luma):08x}','lux_bits':f'0x{bits(tr.lux):08x}','lux':float(tr.lux),'fresh_cct_bits':f'0x{bits(tr.fresh_cct):08x}','fresh_cct':float(tr.fresh_cct),'final_xy_bits':[f'0x{bits(fx):08x}',f'0x{bits(fy):08x}'],'final_cct_bits':f'0x{bits(fc):08x}','final_cct':float(fc),'published_cct':int(fc),'p01':tr.p01,'valid':tr.valid,'trigger_ms':tr_ms,'lsc':ls,'compose_ms':comp_ms,'capsule_sha256':None if cap is None else sha(cap),'total_process_ms':(time.perf_counter_ns()-t0)/1e6}
        self.rows.append(row);return row,cap,desc

class LiveControl:
    def __init__(self,fd:int,so:pathlib.Path):
        self.fd=fd;lib=ctypes.CDLL(str(so));self.g3=lib.e003i_get_3a;self.gt=lib.e003i_get_tlbg;self.si=lib.e003i_submit_iq
        for f in (self.g3,self.gt,self.si):f.argtypes=[ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t];f.restype=ctypes.c_int
    def get_pair(self,target:int,timeout_s:float=5.0):
        a=(ctypes.c_ubyte*STATS3A_BYTES)();t=(ctypes.c_ubyte*TLBG_BYTES)();end=time.monotonic()+timeout_s
        while time.monotonic()<end:
            r=self.g3(self.fd,a,STATS3A_BYTES)
            if r<0:time.sleep(0.0002);continue
            ab=bytes(a)
            try:i3,_,_=parse_3a(ab)
            except Exception:time.sleep(0.0002);continue
            if i3[0]<target:time.sleep(0.0002);continue
            need(i3[0]==target,f'missed 3A generation {target}, now {i3[0]}')
            r=self.gt(self.fd,t,TLBG_BYTES)
            if r<0:time.sleep(0.0002);continue
            tb=bytes(t)
            try:it,_=parse_tlbg(tb)
            except Exception:time.sleep(0.0002);continue
            if it==i3:return ab,tb
            if it[0]>target:raise RuntimeError(f'missed paired TLBG generation {target}, now {it[0]}')
            time.sleep(0.0001)
        raise TimeoutError(f'timed out waiting generation {target}')
    def submit(self,cap:bytes):
        b=(ctypes.c_ubyte*len(cap)).from_buffer_copy(cap);r=self.si(self.fd,b,len(cap));need(r==0,f'IQ submit rc={r}')

def write_manifest(path,mode,rows,extra=None):
    d={'schema':'sp11-e003i-ae-bounded-live-trigger-iq-producer-v1','mode':mode,'status':'PASS','source_generation_is_request_id':False,'selection_law':'R5<-G2, R6<-G3','bounded_baseline_bits':f'0x{BASELINE_BITS:08x}','continuous_aec_claimed':False,'rows':rows};
    if extra:d.update(extra)
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');tmp.replace(path)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('offline','live'),required=True);ap.add_argument('--snapshot-dir',type=pathlib.Path);ap.add_argument('--output-dir',type=pathlib.Path,required=True);ap.add_argument('--manifest',type=pathlib.Path,required=True);ap.add_argument('--fd',type=int);ap.add_argument('--ready-fd',type=int);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='e003i-ae-') as td:
        p=Producer(pathlib.Path(td));control=None
        if a.mode=='live':
            need(a.fd is not None and a.ready_fd is not None,'live fd args');shim=pathlib.Path(td)/'libctrl.so';compile_so(HERE/'v4l2-control-shim.c',shim);control=LiveControl(a.fd,shim);os.write(a.ready_fd,b'R');os.close(a.ready_fd);print('AE_PRODUCER_READY',flush=True)
        for gen in (1,2,3):
            if a.mode=='offline':
                need(a.snapshot_dir is not None,'snapshot dir');s=(a.snapshot_dir/f'STATS3A-{gen-1}.bin').read_bytes();t=(a.snapshot_dir/f'TLBG-{gen-1}.bin').read_bytes()
            else:s,t=control.get_pair(gen)
            (a.output_dir/f'STATS3A-G{gen}.bin').write_bytes(s);(a.output_dir/f'TLBG-G{gen}.bin').write_bytes(t)
            row,cap,desc=p.process(s,t);print(f"AE_G{gen} lux={row['lux']:.9f} cct={row['published_cct']} total_ms={row['total_process_ms']:.4f}",flush=True)
            if cap is not None:
                req=gen+3;(a.output_dir/f'R{req}-dynamic.bin').write_bytes(cap)
                if control is not None:
                    ts=time.perf_counter_ns();control.submit(cap);row['submit_ms']=(time.perf_counter_ns()-ts)/1e6;row['submitted_live']=True;print(f"AE_R{req}_SUBMITTED_FROM_G{gen} sha={row['capsule_sha256']}",flush=True)
                else:row['submitted_live']=False
            write_manifest(a.manifest,a.mode,p.rows,{'runtime_performed':a.mode=='live'})
        print('E003I_AE_PRODUCER=PASS',flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:
        print(f'E003I_AE_PRODUCER=FAIL {type(e).__name__}: {e}',file=sys.stderr,flush=True);raise
