#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, importlib.util, math, random, struct, subprocess, sys, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA

def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

for rel,script,marker in [
 ('ay-windows-aec-basic-safe-convergence','verify-ay.py','AY_VERIFY=PASS'),
 ('az-windows-aec-convstretch-aggregation','verify-az.py','AZ_VERIFY=PASS'),
 ('bb-windows-aec-get-exposure-info','verify-bb.py','BB_VERIFY=PASS'),
 ('ba-windows-aec-drc-stretch-aggregator','verify-ba.py','BA_VERIFY=PASS'),
 ('bc-windows-aec-single-exposure-output','verify-bc.py','BC_VERIFY=PASS'),
 ('bj-native-aec-log103-coordinate','verify-bj.py','BJ_VERIFY=PASS')]: fresh(rel,script,marker)

def load(name,rel):
    p=BASE/rel
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ay=load('bl_ay','ay-windows-aec-basic-safe-convergence/windows-basic-safe.py')
az=load('bl_az','az-windows-aec-convstretch-aggregation/windows-convstretch.py')
bb=load('bl_bb','bb-windows-aec-get-exposure-info/windows-get-exposure-info.py')
ba=load('bl_ba','ba-windows-aec-drc-stretch-aggregator/windows-drc-stretch.py')
bc=load('bl_bc','bc-windows-aec-single-exposure-output/windows-single-exposure-output.py')

# Compile the actual target-native implementation warning-free.
td=tempfile.TemporaryDirectory(prefix='e003i-bl-'); so=Path(td.name)/'libconv.so'
subprocess.run(['gcc','-shared','-fPIC','-O2','-fno-fast-math','-Wall','-Wextra','-Werror',
                str(HERE/'native-convergence.c'),'-I',str(HERE),'-lm','-o',str(so)],check=True)
lib=ctypes.CDLL(str(so))

N=7; MAX=16
class Hist(ctypes.Structure):
    _fields_=[('lanes',ctypes.c_uint64*N),('drc_gain',ctypes.c_float),('previous_delta',ctypes.c_float)]
class Rec(ctypes.Structure):
    _fields_=[('weight',ctypes.c_float),('offset',ctypes.c_float),('comp',ctypes.c_float),('temp_weight',ctypes.c_float),('negative',ctypes.c_uint32)]
class In(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*N),('history1',Hist),('history2',Hist),('delayed_history',Hist),
              ('pipeline_delay',ctypes.c_uint32),('base_speed',ctypes.c_float),('base_capping',ctypes.c_float),('drc_speed',ctypes.c_float),
              ('capping_type',ctypes.c_int32),('tolerance_steps',ctypes.c_int32),('minimum_step',ctypes.c_float),
              ('intolerance_gate',ctypes.c_uint32),('small_delta_exemption',ctypes.c_uint32),('stretch',Rec*MAX),
              ('stretch_capacity',ctypes.c_uint32),('stretch_active_count',ctypes.c_uint32),('stretch_agg_type',ctypes.c_uint32),
              ('stretch_direction_mode',ctypes.c_uint32),('stretch_target_negative',ctypes.c_uint32),
              ('state_flag_short',ctypes.c_int32),('state_flag_long',ctypes.c_int32),('drc_policy',ctypes.c_int32)]
class Out(ctypes.Structure):
    _fields_=[('basic_safe_log',ctypes.c_double),('post_stretch_log',ctypes.c_double*N),('final_log',ctypes.c_double*N),
              ('linear',ctypes.c_uint64*N),('pred_gain',ctypes.c_float),('short_stretch',ctypes.c_float),('safe_stretch',ctypes.c_float),
              ('stretch_ratio',ctypes.c_float),('drc_ratio',ctypes.c_float),('basic_direction_ok',ctypes.c_uint32),('drc_branch',ctypes.c_uint32)]
lib.e003i_converge_single_request.argtypes=[ctypes.POINTER(In),ctypes.POINTER(Out)];lib.e003i_converge_single_request.restype=ctypes.c_int
lib.e003i_stretch_materialize.argtypes=[ctypes.c_int,ctypes.c_float,ctypes.c_float,ctypes.c_float,ctypes.c_float,ctypes.POINTER(Rec)];lib.e003i_stretch_materialize.restype=ctypes.c_int

POW_BASE=1.0299999713897705
def lin(logv): return max(1,int(math.pow(POW_BASE,float(logv))))
def fbits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]

def oracle(i,records):
    h1=list(i.history1.lanes);h2=list(i.history2.lanes);hd=list(i.delayed_history.lanes)
    prev=bb.log103_linear(float(h1[2]));prev2=bb.log103_linear(float(h2[2]));delay=bb.log103_linear(float(hd[2]))
    ar=ay.compute_basic_safe(ay.BasicSafeInputs(i.target_log[2],prev,prev2,delay,i.history1.previous_delta,
        i.pipeline_delay,i.base_speed,i.base_capping,i.drc_speed,i.capping_type,i.tolerance_steps,i.minimum_step,
        bool(i.intolerance_gate),bool(i.small_delta_exemption)))
    rr=[az.StretchRecord(r.weight,r.offset,r.comp,r.temp_weight,r.negative) for r in records]
    ag=az.aggregate_stretch_output(rr,i.stretch_active_count,i.stretch_agg_type,i.stretch_direction_mode,bool(i.stretch_target_negative))
    sr=az.apply_aggregated_stretch(ar.output_log,i.history1.previous_delta,ag,i.minimum_step)
    rs=bb.compute(bb.GetExposureInfoInputs(0,i.target_log[0],i.target_log[2],sr.safe_log,
        bb.HistoryLane(h1[2],h1[0],i.history1.drc_gain),bb.HistoryLane(h2[2],h2[0],i.history2.drc_gain),
        i.drc_speed,i.minimum_step,i.tolerance_steps,i.state_flag_short))
    rl=bb.compute(bb.GetExposureInfoInputs(1,i.target_log[1],i.target_log[2],sr.safe_log,
        bb.HistoryLane(h1[2],h1[1],i.history1.drc_gain),bb.HistoryLane(h2[2],h2[1],i.history2.drc_gain),
        i.drc_speed,i.minimum_step,i.tolerance_steps,i.state_flag_long))
    normal=ba.Lanes(sr.short_log,sr.long_log,sr.safe_log,ar.output_log,ar.output_log,ar.output_log,ar.output_log)
    drc=ba.Lanes(rs.output_log,rl.output_log,sr.safe_log,ar.output_log,ar.output_log,ar.output_log,ar.output_log)
    br=ba.aggregate(normal,drc,sr.pred_gain,i.drc_policy)
    y=bc.converge_single_exposure(bc.SevenLogLanes(br.lanes.short,br.lanes.long,br.lanes.safe,br.lanes.s1,br.lanes.s2,br.lanes.s3,br.lanes.s4))
    return ar,sr,br,y,bc.populate_output(y)

def fill_hist(h,logs,drc=1.0,delta=0.0):
    h.lanes[:]=[lin(x) for x in logs];h.drc_gain=drc;h.previous_delta=delta

def run(i):
    o=Out(); rc=lib.e003i_converge_single_request(ctypes.byref(i),ctypes.byref(o)); assert rc==0,rc; return o

# Materialization boundary against AZ, including exact one-step factor.
for typ,raw in [(0,1.03),(0,1.0),(1,-2.0),(1,3.5)]:
    c=Rec(); assert lib.e003i_stretch_materialize(typ,1.0,raw,.5,.25,ctypes.byref(c))==0
    p=az.materialize_record(typ,1.0,raw,.5,.25)
    assert abs(c.offset-p.offset)<2e-5 and c.negative==p.negative

# One fully composed deterministic case is exact at every externally important boundary.
i=In(); i.target_log[:]=(98,101,105,105,105,105,105)
fill_hist(i.history1,(96,100,100,100,100,100,100),1.0,0.0)
fill_hist(i.history2,(95,99,99,99,99,99,99),1.0,0.0)
fill_hist(i.delayed_history,(94,98,98,98,98,98,98),1.0,0.0)
i.pipeline_delay=3;i.base_speed=.5;i.base_capping=.4;i.drc_speed=.3;i.capping_type=0;i.tolerance_steps=1;i.minimum_step=.5
i.stretch_capacity=1;i.stretch_active_count=1;i.stretch_agg_type=0;i.stretch_direction_mode=0;i.stretch_target_negative=0
i.stretch[0]=Rec(1,0,1,.5,0);i.drc_policy=2
ar,sr,br,y,z=oracle(i,[i.stretch[0]]);o=run(i)
assert o.basic_safe_log==ar.output_log
assert list(o.linear)==list(z)==[18,19,20,18,18,18,18]
assert all(a==b for a,b in zip(o.final_log,y.tuple()))

# Deterministic differential corpus across all capping/aggregation modes and valid DRC policies.
rng=random.Random(0xE0031); cases=0; exact_linear=0; max_log_error=0.0
for k in range(768):
    i=In(); hs=rng.uniform(85.0,210.0); h2s=hs+rng.uniform(-1.2,1.2); hds=hs+rng.uniform(-2.5,2.5)
    h1logs=(hs-rng.uniform(0,5),hs+rng.uniform(-2,2),hs,hs,hs,hs,hs)
    h2logs=(h2s-rng.uniform(0,5),h2s+rng.uniform(-2,2),h2s,h2s,h2s,h2s,h2s)
    hdlogs=(hds-2,hds-1,hds,hds,hds,hds,hds)
    delta=rng.choice([-2.0,-1.0,0.0,1.0,2.0])
    fill_hist(i.history1,h1logs,rng.choice([1.0,1.0,1.25,2.0]),delta)
    fill_hist(i.history2,h2logs,rng.choice([1.0,1.5]),0.0);fill_hist(i.delayed_history,hdlogs,1.0,0.0)
    ts=hs+rng.uniform(-6,6); i.target_log[:]=(ts-rng.uniform(0,7),ts+rng.uniform(-2,2),ts,ts,ts,ts,ts)
    i.pipeline_delay=3;i.base_speed=rng.choice([.1,.25,.5,.8]);i.base_capping=rng.choice([.2,.33,.5,1.0]);i.drc_speed=rng.choice([.1,.3,.6,.9])
    i.capping_type=k%3;i.tolerance_steps=rng.choice([0,1,2]);i.minimum_step=rng.choice([.25,.5,1.0]);i.intolerance_gate=0;i.small_delta_exemption=0
    offs=[-4.0,-1.0,2.0,5.0]; ws=[1.0,2.0,3.0,4.0]
    i.stretch_capacity=4;i.stretch_active_count=4;i.stretch_agg_type=k%5;i.stretch_direction_mode=0;i.stretch_target_negative=(k//5)&1
    recs=[]
    for j in range(4):
        r=Rec(ws[j],offs[(j+k)%4],rng.choice([.25,.5,1.0,1.5]),rng.choice([0.0,.25,.5,.75,1.0]),1 if offs[(j+k)%4]<0 else 0)
        i.stretch[j]=r; recs.append(r)
    i.state_flag_short=(k>>2)&1;i.state_flag_long=(k>>3)&1;i.drc_policy=k%3
    ar,sr,br,y,z=oracle(i,recs);o=run(i);cases+=1
    errs=[abs(o.basic_safe_log-ar.output_log)]+[abs(a-b) for a,b in zip(o.final_log,y.tuple())]
    max_log_error=max(max_log_error,max(errs))
    assert max(errs)<1e-4,(k,max(errs),list(o.final_log),y.tuple())
    if list(o.linear)==list(z): exact_linear+=1
    else:
        # Tiny helper-rounding differences are allowed only if they cannot exceed one output quantum.
        assert all(abs(int(a)-int(b))<=1 for a,b in zip(o.linear,z)),(k,list(o.linear),z)

# Fail closed for missing/zero linear history.
bad=In();bad.target_log[:]=(1,1,1,1,1,1,1);bad.pipeline_delay=3;bad.stretch_capacity=1;bad.stretch_active_count=1
bo=Out();assert lib.e003i_converge_single_request(ctypes.byref(bad),ctypes.byref(bo))==-2

print('DLL_SHA256='+DLL_SHA)
print('NATIVE_CHAIN=AY->AZ->BB->BA->BC')
print('HISTORY_DOMAIN=absolute log1.03(linear exposure); distinct from BJ T681-relative coordinate')
print(f'DIFFERENTIAL_CASES={cases}')
print(f'EXACT_LINEAR_CASES={exact_linear}/{cases}')
print(f'MAX_LOG_ERROR={max_log_error:.9g}')
print('UNRESOLVED_UPSTREAM_SEAM=request-local ConvBase/ConvStretch/profile materialization and policy selection')
print('BL_VERIFY=PASS')
