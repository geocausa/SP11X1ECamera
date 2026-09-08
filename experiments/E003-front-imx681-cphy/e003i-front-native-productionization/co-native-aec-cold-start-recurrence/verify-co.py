#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, importlib.util, random, struct, subprocess, sys, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
CN=BASE/'cn-windows-aec-cold-start-history-bootstrap'
CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'
CC=BASE/'cc-native-aec-adrc-darkboost-tail'; BY=BASE/'by-native-aec-method11-point-aggregation'
CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'
BK=BASE/'bk-native-aec-history-state'; BJ=BASE/'bj-native-aec-log103-coordinate'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
cp=subprocess.run([str(CN/'verify-cn.py')],cwd=CN,text=True,capture_output=True)
assert cp.returncode==0,(cp.stdout,cp.stderr)
assert 'CN_VERIFY=PASS' in cp.stdout and 'START_RECORD=frame0 marker1 seven_lanes_33333332' in cp.stdout
assert subprocess.run(['git','merge-base','--is-ancestor','8720706','HEAD'],cwd=REPO).returncode==0

h=(HERE/'native-aec-request-loop.h').read_text(); c=(HERE/'native-aec-request-loop.c').read_text()
assert 'e003i_request_loop_seed_history' not in h+c
assert '#define E003I_WINDOWS_START_EXPOSURE UINT64_C(33333332)' in h
assert 'struct e003i_request_history_entry start_history;' in h
for x in ('start->short_exposure = E003I_WINDOWS_START_EXPOSURE;',
          'start->long_exposure = E003I_WINDOWS_START_EXPOSURE;',
          'start->safe_exposure = E003I_WINDOWS_START_EXPOSURE;',
          'start->s1_exposure = E003I_WINDOWS_START_EXPOSURE;',
          'h1 = history_get_offset(state, in->frame_id, 1);',
          'h2 = history_get_offset(state, in->frame_id, 2);',
          'h3 = history_get_offset(state, in->frame_id, 3);',
          'if (in->frame_id != state->next_frame_id)',
          'state->next_frame_id++;'):
    assert x in c,x

# Load the separately-established float32 FrameSA + Algorithm001 reference.
bh_path=BASE/'bh-native-aec-request-state'/'windows-aec-request-state.py'
spec=importlib.util.spec_from_file_location('e003i_bh_ref_co',bh_path)
bh=importlib.util.module_from_spec(spec);sys.modules[spec.name]=bh;spec.loader.exec_module(bh)
def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def fbits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def bytesof(x): return ctypes.string_at(ctypes.byref(x),ctypes.sizeof(x))
CONF=f32(struct.unpack('<f',struct.pack('<I',0x3a83126f))[0])

# Compile CO plus already-committed native primitives using the strict FP policy.
td=Path(tempfile.mkdtemp(prefix='e003i-co-')); so=td/'co.so'
cmd=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off',
 str(HERE/'native-aec-request-loop.c'),str(CF/'native-final-exposure.c'),str(CE/'native-final-target.c'),
 str(CC/'native-aec-tail.c'),str(BY/'native-target-aggregate.c'),str(CG/'native-convergence.c'),str(CH/'native-t681.c'),
 str(BK/'native-aec-state.c'),str(BJ/'native-log103.c'),
 '-I',str(HERE),'-I',str(CF),'-I',str(CE),'-I',str(CC),'-I',str(BY),'-I',str(CG),'-I',str(CH),'-I',str(BK),'-I',str(BJ),
 '-lm','-o',str(so)]
subprocess.run(cmd,check=True)
lib=ctypes.CDLL(str(so))

class Cand(ctypes.Structure): _fields_=[('value',ctypes.c_float),('confidence',ctypes.c_float)]
class TIn(ctypes.Structure):
    _fields_=[('lux_index',ctypes.c_float),('frame',Cand),('sat_prev',Cand),('dark_prev',Cand),('brighten',Cand),('extreme_color',Cand),('illuminance',Cand),('short_sat_prev',Cand),('long_dark_prev',Cand)]
class Tail(ctypes.Structure):
    _fields_=[('adrc_lux_face_cap',ctypes.c_float),('adj_ratio_short',ctypes.c_float),('adrc_gain',ctypes.c_float),('short_adj_ratio',ctypes.c_float),('drc_gain_remainder',ctypes.c_float),('adj_ratio_long',ctypes.c_float),('dark_boost_gain',ctypes.c_float),('long_adj_ratio',ctypes.c_float)]
class TOut(ctypes.Structure):
    _fields_=[('safe_target',ctypes.c_float),('safe_adj_ratio',ctypes.c_float),('short_target',ctypes.c_float),('long_target',ctypes.c_float),('tail',Tail)]
class FIn(ctypes.Structure): _fields_=[('source_exposure_s1',ctypes.c_uint64),('target_input',TIn)]
class FOut(ctypes.Structure): _fields_=[('targets',TOut),('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64)]
class H1(ctypes.Structure): _fields_=[('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('drc_gain',ctypes.c_float)]
class H2(ctypes.Structure): _fields_=H1._fields_
class H3(ctypes.Structure): _fields_=[('safe_exposure',ctypes.c_uint64)]
class CIn(ctypes.Structure): _fields_=[('target_exposure',ctypes.c_uint64*3),('history1',H1),('history2',H2),('delayed_history',H3)]
class COut(ctypes.Structure):
    _fields_=[('basic_safe_log',ctypes.c_double),('post_stretch_log',ctypes.c_double*7),('final_log',ctypes.c_double*7),('linear',ctypes.c_uint64*7),('pred_gain',ctypes.c_float),('short_stretch',ctypes.c_float),('safe_stretch',ctypes.c_float),('stretch_ratio',ctypes.c_float),('drc_ratio',ctypes.c_float),('basic_direction_ok',ctypes.c_uint32),('drc_branch',ctypes.c_uint32)]
class AOut(ctypes.Structure): _fields_=[('gain',ctypes.c_float),('exposure_time_ns',ctypes.c_uint64),('correction',ctypes.c_float),('retained_exposure',ctypes.c_uint64),('upper_knee',ctypes.c_uint32)]
class HE(ctypes.Structure):
    _fields_=[('frame_id',ctypes.c_uint64),('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('s1_exposure',ctypes.c_uint64),('pred_gain',ctypes.c_float),('valid',ctypes.c_uint8)]
class State(ctypes.Structure):
    _fields_=[('lux_trigger',ctypes.c_float),('algorithm001_alpha',ctypes.c_float),('next_frame_id',ctypes.c_uint64),('start_history',HE),('history',HE*16)]
class Rem(ctypes.Structure):
    _fields_=[('sat_prev',Cand),('dark_prev',Cand),('brighten',Cand),('extreme_color',Cand),('illuminance',Cand),('short_sat_prev',Cand),('long_dark_prev',Cand)]
class RIn(ctypes.Structure): _fields_=[('frame_id',ctypes.c_uint64),('measured_luma',ctypes.c_float),('analyzers',Rem)]
class ROut(ctypes.Structure):
    _fields_=[('lux_trigger_in',ctypes.c_float),('frame_target',ctypes.c_float),('frame_candidate',Cand),('history_reference_log103',ctypes.c_float),('next_lux_trigger',ctypes.c_float),('target_publication',FOut),('convergence',COut),('short_arbitration',AOut),('long_arbitration',AOut),('safe_arbitration',AOut),('s1_arbitration',AOut)]

lib.e003i_request_loop_init.argtypes=[ctypes.POINTER(State),ctypes.c_float,ctypes.c_float];lib.e003i_request_loop_init.restype=ctypes.c_int
lib.e003i_request_loop_process.argtypes=[ctypes.POINTER(State),ctypes.POINTER(RIn),ctypes.POINTER(ROut)];lib.e003i_request_loop_process.restype=ctypes.c_int
lib.e003i_aec_default_final_exposures.argtypes=[ctypes.POINTER(FIn),ctypes.POINTER(FOut)];lib.e003i_aec_default_final_exposures.restype=ctypes.c_int
lib.e003i_converge_front_preview_unlocked_qword_history.argtypes=[ctypes.POINTER(CIn),ctypes.POINTER(COut)];lib.e003i_converge_front_preview_unlocked_qword_history.restype=ctypes.c_int
lib.e003i_t681_preview_arbitrate.argtypes=[ctypes.c_uint64,ctypes.POINTER(AOut)];lib.e003i_t681_preview_arbitrate.restype=ctypes.c_int
lib.e003i_log103_coordinate.argtypes=[ctypes.c_uint64];lib.e003i_log103_coordinate.restype=ctypes.c_float

START=(33333332,33333332,33333332,33333332,f32(0.0))
fields=('sat_prev','dark_prev','brighten','extreme_color','illuminance','short_sat_prev','long_dark_prev')

def lookup(real,current,offset):
    selected=START; selected_id='START'
    for depth in range(1,min(current,10)+1):
        fid=current-depth
        assert fid in real,(current,offset,fid)
        selected=real[fid];selected_id=fid
        if fid+offset<=current:break
    return selected,selected_id

def make_ti(lux,measured,rem):
    ti=TIn();ti.lux_index=f32(lux);target=bh.framesa_target_low(f32(lux));adj=f32(f32(target)/f32(measured));ti.frame=Cand(adj,CONF)
    for n in fields:setattr(ti,n,getattr(rem,n))
    return ti,target,adj

def standalone(source,ti,h1,h2,h3):
    fi=FIn(source,ti);fo=FOut();assert lib.e003i_aec_default_final_exposures(ctypes.byref(fi),ctypes.byref(fo))==0
    ci=CIn();ci.target_exposure[:]=(fo.short_exposure,fo.long_exposure,fo.safe_exposure)
    ci.history1=H1(h1[0],h1[1],h1[2],h1[4]);ci.history2=H2(h2[0],h2[1],h2[2],h2[4]);ci.delayed_history=H3(h3[2])
    co=COut();assert lib.e003i_converge_front_preview_unlocked_qword_history(ctypes.byref(ci),ctypes.byref(co))==0
    ar=[]
    for lane in (0,1,2,3):
        a=AOut();rc=lib.e003i_t681_preview_arbitrate(co.linear[lane],ctypes.byref(a));assert rc==0,(lane,int(co.linear[lane]),rc);ar.append(a)
    return fo,co,ar

# Initialization exactly owns the synthetic Windows seed.
s=State();assert lib.e003i_request_loop_init(ctypes.byref(s),150.0,0.0)==0
assert s.next_frame_id==0 and s.start_history.valid==1 and s.start_history.frame_id==0
assert (s.start_history.short_exposure,s.start_history.long_exposure,s.start_history.safe_exposure,s.start_history.s1_exposure)==START[:4]
assert fbits(s.start_history.pred_gain)==0
assert all(not x.valid for x in s.history)

# Rejected non-sequential requests are side-effect free.
r=RIn();r.frame_id=1;r.measured_luma=1.0
for n in fields:setattr(r.analyzers,n,Cand(1.0,0.25))
o=ROut();before=bytesof(s);assert lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(r),ctypes.byref(o))==-2;assert bytesof(s)==before
r.frame_id=0;r.measured_luma=float('nan');before=bytesof(s);assert lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(r),ctypes.byref(o))==-3;assert bytesof(s)==before

# Explicit temporal warm-up identities from CN.
assert lookup({},0,1)[1]=='START' and lookup({},0,2)[1]=='START' and lookup({},0,3)[1]=='START'
dummy={0:(1,2,3,4,1.0)}
assert [lookup(dummy,1,k)[1] for k in (1,2,3)]==[0,0,0]
dummy[1]=(5,6,7,8,1.0)
assert [lookup(dummy,2,k)[1] for k in (1,2,3)]==[1,0,0]
dummy[2]=(9,10,11,12,1.0)
assert [lookup(dummy,3,k)[1] for k in (1,2,3)]==[2,1,0]

# Full cold-start-to-steady-state differential.
rng=random.Random(0xC01D57A2);seq_cases=request_cases=0;warm_ids=[]
for seq in range(192):
    alpha=f32(rng.choice([0.0,0.0,0.1,0.25]));lux=f32(rng.uniform(30.0,480.0))
    s=State();assert lib.e003i_request_loop_init(ctypes.byref(s),lux,alpha)==0
    real={}
    for f in range(12):
        h1,id1=lookup(real,f,1);h2,id2=lookup(real,f,2);h3,id3=lookup(real,f,3)
        if seq==0 and f<5:warm_ids.append((f,id1,id2,id3))
        measured=f32(rng.uniform(0.60,2.50));rem=Rem()
        # Keep the seven still-external analyzers in the proven ordinary range,
        # with at least one strong SafeAgg peer so low-confidence FrameSA cannot
        # alone drive the synthetic test outside the T681 table.
        for j,n in enumerate(fields):
            conf=f32(rng.choice([0.05,0.1,0.25,0.5,1.0]))
            if j==1:conf=f32(0.5)
            setattr(rem,n,Cand(f32(rng.uniform(0.88,1.12)),conf))
        ti,target,adj=make_ti(lux,measured,rem)
        fo,co,ar=standalone(h3[3],ti,h1,h2,h3)
        href=f32(lib.e003i_log103_coordinate(h3[3]));next_lux=bh.algorithm001_lux(measured,href,lux,alpha)
        ri=RIn(f,measured,rem);ro=ROut();rc=lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(ri),ctypes.byref(ro));assert rc==0,(seq,f,rc)
        assert fbits(ro.lux_trigger_in)==fbits(lux) and fbits(ro.frame_target)==fbits(target)
        assert fbits(ro.frame_candidate.value)==fbits(adj) and fbits(ro.frame_candidate.confidence)==0x3a83126f
        assert fbits(ro.history_reference_log103)==fbits(href) and fbits(ro.next_lux_trigger)==fbits(next_lux)
        assert bytesof(ro.target_publication)==bytesof(fo) and bytesof(ro.convergence)==bytesof(co)
        for got,exp in ((ro.short_arbitration,ar[0]),(ro.long_arbitration,ar[1]),(ro.safe_arbitration,ar[2]),(ro.s1_arbitration,ar[3])):assert bytesof(got)==bytesof(exp)
        new=(ar[0].retained_exposure,ar[1].retained_exposure,ar[2].retained_exposure,ar[3].retained_exposure,f32(co.pred_gain));real[f]=new
        he=s.history[f%16];assert he.valid and he.frame_id==f and (he.short_exposure,he.long_exposure,he.safe_exposure,he.s1_exposure)==new[:4] and fbits(he.pred_gain)==fbits(new[4])
        assert s.next_frame_id==f+1 and fbits(s.lux_trigger)==fbits(next_lux)
        lux=f32(next_lux);request_cases+=1
    seq_cases+=1

assert warm_ids==[(0,'START','START','START'),(1,0,0,0),(2,1,0,0),(3,2,1,0),(4,3,2,1)]
print('DLL_SHA256='+DLL_SHA)
print('PUBLIC_SEED_HISTORY=removed')
print('START_EXPOSURE=33333332 all retained lanes')
print('WARMUP_IDS='+repr(warm_ids))
print('FRAME0_PROCESS=PASS')
print('SEQUENTIAL_GUARD=PASS')
print('SEQUENCES='+str(seq_cases))
print('REQUEST_CASES='+str(request_cases))
print('COMPOSED_OUTPUT_MATCH=byte-exact CN lookup + FrameSA+CF+CG+CH mirror')
print('CO_VERIFY=PASS')
