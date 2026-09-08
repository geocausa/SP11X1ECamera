#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, random, struct, subprocess, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
CF=BASE/'cf-native-aec-final-exposure-si'
CE=BASE/'ce-native-aec-final-target-producer'
CC=BASE/'cc-native-aec-adrc-darkboost-tail'
BY=BASE/'by-native-aec-method11-point-aggregation'
CG=BASE/'cg-native-aec-qword-convergence-input'
CH=BASE/'ch-native-aec-t681-preview-arbitration'
AX=BASE/'ax-windows-aec-convergence-history-loop'
CK=BASE/'ck-windows-aec-preview-history-delay'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA

def fresh(d,script,marker,extra=()):
    p=d/script
    cp=subprocess.run([str(p)],cwd=d,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert cp.returncode==0,(p,cp.stdout,cp.stderr)
    assert marker in cp.stdout,(p,marker,cp.stdout)
    for x in extra: assert x in cp.stdout,(p,x,cp.stdout)
    return cp.stdout

# Exact temporal selector, seven-lane Windows persistence, and T681 primitive.
fresh(CK,'verify-ck.py','CK_VERIFY=PASS',('ANALYZER_HISTORY_OFFSET=3',))
fresh(AX,'verify-ax.py','AX_VERIFY=PASS',('LANES=7','TYPE5_TABLE_CONSUMES_SELECTED_RECORD=PASS','HISTORY_RETAINED_EXPOSURE=richRecord+0x20'))
fresh(CH,'verify-ch.py','CH_VERIFY=PASS',('NATIVE_T681_PREVIEW_MATCH=bit-exact gain/time/retained',))
assert subprocess.run(['git','merge-base','--is-ancestor','23abd8a','HEAD'],cwd=REPO).returncode==0

# Public seam reduction: caller no longer supplies source S1.
h=(HERE/'native-aec-request-loop.h').read_text()
c=(HERE/'native-aec-request-loop.c').read_text()
ib=h.split('struct e003i_request_loop_input {',1)[1].split('};',1)[0]
assert 'source_exposure_s1' not in ib
assert 'uint64_t frame_id;' in ib and 'struct e003i_final_target_input target_input;' in ib
assert 'uint64_t s1_exposure;' in h
assert 'fi.source_exposure_s1 = h3->s1_exposure;' in c
assert 'out->convergence.linear[E003I_LANE_S1]' in c
assert 'cur->s1_exposure = out->s1_arbitration.retained_exposure;' in c

# Compile complete CL native composition under strict FP policy.
td=Path(tempfile.mkdtemp(prefix='e003i-cl-')); so=td/'cl.so'
cmd=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off',
     str(HERE/'native-aec-request-loop.c'),str(CF/'native-final-exposure.c'),str(CE/'native-final-target.c'),
     str(CC/'native-aec-tail.c'),str(BY/'native-target-aggregate.c'),str(CG/'native-convergence.c'),str(CH/'native-t681.c'),
     '-I',str(HERE),'-I',str(CF),'-I',str(CE),'-I',str(CC),'-I',str(BY),'-I',str(CG),'-I',str(CH),'-lm','-o',str(so)]
subprocess.run(cmd,check=True)
lib=ctypes.CDLL(str(so))

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def bytesof(x): return ctypes.string_at(ctypes.byref(x),ctypes.sizeof(x))

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
class State(ctypes.Structure): _fields_=[('history',HE*16)]
class RIn(ctypes.Structure): _fields_=[('frame_id',ctypes.c_uint64),('target_input',TIn)]
class ROut(ctypes.Structure):
    _fields_=[('target_publication',FOut),('convergence',COut),('short_arbitration',AOut),('long_arbitration',AOut),('safe_arbitration',AOut),('s1_arbitration',AOut)]

lib.e003i_request_loop_init.argtypes=[ctypes.POINTER(State)]
lib.e003i_request_loop_seed_history.argtypes=[ctypes.POINTER(State),ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_float]
lib.e003i_request_loop_seed_history.restype=ctypes.c_int
lib.e003i_request_loop_process.argtypes=[ctypes.POINTER(State),ctypes.POINTER(RIn),ctypes.POINTER(ROut)]
lib.e003i_request_loop_process.restype=ctypes.c_int
lib.e003i_aec_default_final_exposures.argtypes=[ctypes.POINTER(FIn),ctypes.POINTER(FOut)]; lib.e003i_aec_default_final_exposures.restype=ctypes.c_int
lib.e003i_converge_front_preview_unlocked_qword_history.argtypes=[ctypes.POINTER(CIn),ctypes.POINTER(COut)]; lib.e003i_converge_front_preview_unlocked_qword_history.restype=ctypes.c_int
lib.e003i_t681_preview_arbitrate.argtypes=[ctypes.c_uint64,ctypes.POINTER(AOut)]; lib.e003i_t681_preview_arbitrate.restype=ctypes.c_int

# Fail closed when temporal state is incomplete or S1 seed is invalid.
s=State(); lib.e003i_request_loop_init(ctypes.byref(s)); ri=RIn(); ri.frame_id=3; ro=ROut()
assert lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(ri),ctypes.byref(ro))==-2
assert lib.e003i_request_loop_seed_history(ctypes.byref(s),0,1,1,1,0,1.0)==-1

rng=random.Random(0xC1A5F003)
def target_input():
    x=TIn(); x.lux_index=f32(rng.uniform(20,800))
    for n in ('frame','sat_prev','dark_prev','brighten','extreme_color','illuminance','short_sat_prev','long_dark_prev'):
        setattr(x,n,Cand(f32(rng.uniform(0.72,1.45)),f32(rng.choice([0.001,0.01,0.05,0.1,0.25,0.5,1.0]))))
    return x

def standalone(source,ti,h1,h2,h3):
    fi=FIn(source,ti); fo=FOut(); assert lib.e003i_aec_default_final_exposures(ctypes.byref(fi),ctypes.byref(fo))==0
    ci=CIn(); ci.target_exposure[:]=(fo.short_exposure,fo.long_exposure,fo.safe_exposure)
    ci.history1=H1(h1[0],h1[1],h1[2],h1[4]); ci.history2=H2(h2[0],h2[1],h2[2],h2[4]); ci.delayed_history=H3(h3[2])
    co=COut(); rc=lib.e003i_converge_front_preview_unlocked_qword_history(ctypes.byref(ci),ctypes.byref(co)); assert rc==0,rc
    ar=[]
    for lane in (0,1,2,3):
        a=AOut(); rc=lib.e003i_t681_preview_arbitrate(co.linear[lane],ctypes.byref(a)); assert rc==0,(lane,co.linear[lane],rc); ar.append(a)
    return fo,co,ar

# Deterministic temporal trap: make F-3 S1 and F-1 Short deliberately distinct,
# prove the two possible analyzer-source references produce different output, then
# require CL to match only the Windows-proven F-3 S1 reference.
trap=State(); lib.e003i_request_loop_init(ctypes.byref(trap))
trap_hist={
    0:(11_111_111,12_222_222,13_333_333,17_654_321,f32(1.0)),
    1:(14_444_444,15_555_555,16_666_666,18_765_432,f32(1.2)),
    2:(29_876_543,19_999_999,20_111_111,21_222_222,f32(1.5)),
}
for f,v in trap_hist.items():
    assert lib.e003i_request_loop_seed_history(ctypes.byref(trap),f,*v)==0
trap_ti=TIn(); trap_ti.lux_index=f32(240.0)
for n,v,cw in (
    ('frame',1.03,1.0),('sat_prev',0.97,0.25),('dark_prev',1.08,0.1),
    ('brighten',1.01,0.05),('extreme_color',0.99,0.01),('illuminance',1.02,0.5),
    ('short_sat_prev',1.04,0.1),('long_dark_prev',0.96,0.1)):
    setattr(trap_ti,n,Cand(f32(v),f32(cw)))
correct=standalone(trap_hist[0][3],trap_ti,trap_hist[2],trap_hist[1],trap_hist[0])
wrong=standalone(trap_hist[2][0],trap_ti,trap_hist[2],trap_hist[1],trap_hist[0])
assert bytesof(correct[0]) != bytesof(wrong[0])
trap_in=RIn(3,trap_ti); trap_out=ROut()
assert lib.e003i_request_loop_process(ctypes.byref(trap),ctypes.byref(trap_in),ctypes.byref(trap_out))==0
assert bytesof(trap_out.target_publication)==bytesof(correct[0])
assert bytesof(trap_out.target_publication)!=bytesof(wrong[0])

# Differential state-machine proof. S1 seeds are independent from Short and every
# request reference uses mirror[F-3].S1. Equality after T681 is allowed: retained
# quantities may legitimately converge even when their producer identities differ.
seq_cases=request_cases=s1_distinct_cases=0
for seq in range(256):
    s=State(); lib.e003i_request_loop_init(ctypes.byref(s)); mirror={}
    base=rng.randrange(8_000_000,30_000_000)
    for f in range(3):
        short=rng.randrange(base//2,base*2)
        long=rng.randrange(base//2,base*2)
        safe=rng.randrange(base//2,base*2)
        s1=rng.randrange(base//3,base*3)
        if s1==short: s1+=137
        pred=f32(rng.choice([1.0,1.0,1.2,1.5,2.0]))
        mirror[f]=(short,long,safe,s1,pred)
        assert lib.e003i_request_loop_seed_history(ctypes.byref(s),f,short,long,safe,s1,pred)==0
    for f in range(3,11):
        source=mirror[f-3][3]
        if source != mirror[f-1][0]: s1_distinct_cases+=1
        ti=target_input(); fo,co,ar=standalone(source,ti,mirror[f-1],mirror[f-2],mirror[f-3])
        ri=RIn(f,ti); ro=ROut(); rc=lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(ri),ctypes.byref(ro)); assert rc==0,(seq,f,rc)
        assert bytesof(ro.target_publication)==bytesof(fo)
        assert bytesof(ro.convergence)==bytesof(co)
        assert bytesof(ro.short_arbitration)==bytesof(ar[0])
        assert bytesof(ro.long_arbitration)==bytesof(ar[1])
        assert bytesof(ro.safe_arbitration)==bytesof(ar[2])
        assert bytesof(ro.s1_arbitration)==bytesof(ar[3])
        new=(ar[0].retained_exposure,ar[1].retained_exposure,ar[2].retained_exposure,ar[3].retained_exposure,f32(co.pred_gain))
        mirror[f]=new
        he=s.history[f%16]
        assert he.valid and he.frame_id==f
        assert (he.short_exposure,he.long_exposure,he.safe_exposure,he.s1_exposure)==new[:4]
        assert struct.pack('<f',he.pred_gain)==struct.pack('<f',new[4])
        # Strong temporal trap: current source remains the independent F-3 S1 mirror.
        assert source > 0 and mirror[f][3] > 0
        request_cases+=1
    seq_cases+=1

assert s1_distinct_cases > 0
print('DLL_SHA256='+SHA)
print('TEMPORAL_TRAP=F-3.S1 reference differs from F-1.Short and CL selects F-3.S1')
print('SOURCE_S1_PUBLIC_INPUT=removed')
print('SOURCE_S1_RECURRENCE=history[F-3].S1')
print('S1_PERSISTENCE=convergence lane3 -> T681 retained qword -> history.S1')
print('S1_EQUALS_SHORT=not assumed')
print('SEQUENCES='+str(seq_cases))
print('REQUEST_CASES='+str(request_cases))
print('S1_DISTINCT_FROM_F1_SHORT_CASES='+str(s1_distinct_cases))
print('COMPOSED_OUTPUT_MATCH=byte-exact vs independent CF+CG+CH(Short/Long/Safe/S1) calls')
print('CL_VERIFY=PASS')
