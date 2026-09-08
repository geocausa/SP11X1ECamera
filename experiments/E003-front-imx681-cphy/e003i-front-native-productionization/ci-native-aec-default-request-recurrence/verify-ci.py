#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, random, struct, subprocess, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'
CC=BASE/'cc-native-aec-adrc-darkboost-tail'; BY=BASE/'by-native-aec-method11-point-aggregation'
CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'
BA=BASE/'ba-windows-aec-drc-stretch-aggregator'; AX=BASE/'ax-windows-aec-convergence-history-loop'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA=[x.split('=',1)[1] for x in (CH/'VERIFY-RESULT.txt').read_text().splitlines() if x.startswith('DLL_SHA256=')][0]
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA

def dis(a,b): return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)
def need(t,*xs):
    for x in xs: assert x in t,x

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def bytesof(x): return ctypes.string_at(ctypes.byref(x),ctypes.sizeof(x))

# Require native ancestry and the independent Windows topology/policy proofs.
for commit in ('3ff2346','b17365c','6aca7ee'):
    assert subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=REPO).returncode==0
for d,s,m in ((BA,'verify-ba.py','BA_VERIFY=PASS'),(AX,'verify-ax.py','AX_VERIFY=PASS')):
    cp=subprocess.run(['python3',str(d/s)],cwd=d,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert cp.returncode==0,(s,cp.stdout,cp.stderr); assert m in cp.stdout

# PredGain recurrence is mechanically the same scalar:
# history+178 -> convergence+d8 -> PopulateOutput+70 -> EOF history+178.
r=dis(0x1803b46f0,0x1803b47ac)
need(r,
 '1803b4718:', 'fmov\ts16, #1.00000000',
 '1803b4720:', 'str\ts16, [x22, #0xd8]',
 '1803b479c:', 'ldr\ts16, [x24, #0x178]',
 '1803b47a0:', 'str\ts16, [x22, #0xd8]')
p=dis(0x1803cdf50,0x1803ce058)
need(p,'1803ce040:','ldr\ts16, [x19, #0xd8]','1803ce044:','str\ts16, [x20, #0x70]')
e=dis(0x1803bd430,0x1803bd460)
need(e,'1803bd440:','ldr\ts16, [x23, #0x70]','1803bd448:','str\ts16, [x19, #0x1220]')
assert 0x10a8+0x178==0x1220

# Compile complete native composition.
td=Path(tempfile.mkdtemp(prefix='e003i-ci-')); so=td/'ci.so'
cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
subprocess.run(cc+[
 str(HERE/'native-aec-request-loop.c'),str(CF/'native-final-exposure.c'),str(CE/'native-final-target.c'),
 str(CC/'native-aec-tail.c'),str(BY/'native-target-aggregate.c'),str(CG/'native-convergence.c'),str(CH/'native-t681.c'),
 '-I',str(HERE),'-I',str(CF),'-I',str(CE),'-I',str(CC),'-I',str(BY),'-I',str(CG),'-I',str(CH),'-lm','-o',str(so)],check=True)
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
class HE(ctypes.Structure): _fields_=[('frame_id',ctypes.c_uint64),('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('pred_gain',ctypes.c_float),('valid',ctypes.c_uint8)]
class State(ctypes.Structure): _fields_=[('history',HE*16)]
class RIn(ctypes.Structure): _fields_=[('frame_id',ctypes.c_uint64),('source_exposure_s1',ctypes.c_uint64),('target_input',TIn)]
class ROut(ctypes.Structure): _fields_=[('target_publication',FOut),('convergence',COut),('short_arbitration',AOut),('long_arbitration',AOut),('safe_arbitration',AOut)]

lib.e003i_request_loop_init.argtypes=[ctypes.POINTER(State)]
lib.e003i_request_loop_seed_history.argtypes=[ctypes.POINTER(State),ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_float]; lib.e003i_request_loop_seed_history.restype=ctypes.c_int
lib.e003i_request_loop_process.argtypes=[ctypes.POINTER(State),ctypes.POINTER(RIn),ctypes.POINTER(ROut)]; lib.e003i_request_loop_process.restype=ctypes.c_int
lib.e003i_aec_default_final_exposures.argtypes=[ctypes.POINTER(FIn),ctypes.POINTER(FOut)]; lib.e003i_aec_default_final_exposures.restype=ctypes.c_int
lib.e003i_converge_front_preview_unlocked_qword_history.argtypes=[ctypes.POINTER(CIn),ctypes.POINTER(COut)]; lib.e003i_converge_front_preview_unlocked_qword_history.restype=ctypes.c_int
lib.e003i_t681_preview_arbitrate.argtypes=[ctypes.c_uint64,ctypes.POINTER(AOut)]; lib.e003i_t681_preview_arbitrate.restype=ctypes.c_int

# Fail closed on missing state/history.
s=State(); lib.e003i_request_loop_init(ctypes.byref(s)); o=ROut(); x=RIn(); x.frame_id=3
assert lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(x),ctypes.byref(o))==-2
assert lib.e003i_request_loop_seed_history(ctypes.byref(s),0,0,1,1,1.0)==-1

rng=random.Random(0xC10031)
def target_input():
    x=TIn(); x.lux_index=f32(rng.uniform(20,800))
    names=['frame','sat_prev','dark_prev','brighten','extreme_color','illuminance','short_sat_prev','long_dark_prev']
    # AdjRatio-like ordinary magnitudes, all confidence paths positive so method11 is defined.
    for n in names:
        setattr(x,n,Cand(f32(rng.uniform(0.72,1.45)),f32(rng.choice([0.001,0.01,0.05,0.1,0.25,0.5,1.0]))))
    return x

def standalone(source,ti,h1,h2,h3):
    fi=FIn(source,ti); fo=FOut(); assert lib.e003i_aec_default_final_exposures(ctypes.byref(fi),ctypes.byref(fo))==0
    ci=CIn(); ci.target_exposure[:]=(fo.short_exposure,fo.long_exposure,fo.safe_exposure)
    ci.history1=H1(h1[0],h1[1],h1[2],h1[3]); ci.history2=H2(h2[0],h2[1],h2[2],h2[3]); ci.delayed_history=H3(h3[2])
    co=COut(); rc=lib.e003i_converge_front_preview_unlocked_qword_history(ctypes.byref(ci),ctypes.byref(co)); assert rc==0,rc
    ar=[]
    for q in co.linear[:3]:
        a=AOut(); rc=lib.e003i_t681_preview_arbitrate(q,ctypes.byref(a)); assert rc==0,(q,rc); ar.append(a)
    return fo,co,ar

# Multi-frame state-machine differential: independent Python mirror chooses
# exact F-1/F-2/F-3 values and compares complete composed outputs byte-for-byte.
seq_cases=0; request_cases=0
for seq in range(256):
    s=State(); lib.e003i_request_loop_init(ctypes.byref(s)); mirror={}
    base=rng.randrange(8_000_000,30_000_000)
    for f in range(3):
        h=(rng.randrange(base//2,base*2),rng.randrange(base//2,base*2),rng.randrange(base//2,base*2),f32(rng.choice([1.0,1.0,1.2,1.5,2.0])))
        mirror[f]=h; assert lib.e003i_request_loop_seed_history(ctypes.byref(s),f,*h)==0
    for f in range(3,11):
        source=mirror[f-1][0]  # realistic caller choice; identity itself is not claimed by CI.
        ti=target_input(); exp=standalone(source,ti,mirror[f-1],mirror[f-2],mirror[f-3])
        ri=RIn(f,source,ti); ro=ROut(); rc=lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(ri),ctypes.byref(ro)); assert rc==0,(seq,f,rc)
        fo,co,ar=exp
        assert bytesof(ro.target_publication)==bytesof(fo)
        assert bytesof(ro.convergence)==bytesof(co)
        assert bytesof(ro.short_arbitration)==bytesof(ar[0]); assert bytesof(ro.long_arbitration)==bytesof(ar[1]); assert bytesof(ro.safe_arbitration)==bytesof(ar[2])
        new=(ar[0].retained_exposure,ar[1].retained_exposure,ar[2].retained_exposure,f32(co.pred_gain)); mirror[f]=new
        he=s.history[f%16]
        assert he.valid and he.frame_id==f
        assert (he.short_exposure,he.long_exposure,he.safe_exposure)==new[:3]
        assert struct.pack('<f',he.pred_gain)==struct.pack('<f',new[3])
        request_cases+=1
    seq_cases+=1

print('DLL_SHA256='+SHA)
print('PRED_GAIN_RECURRENCE=history+0x178 -> conv+0xd8 -> output+0x70 -> history+0x178')
print('EXPOSURE_RECURRENCE=post-T681 retained Short/Long/Safe qwords')
print('SOURCE_S1=explicit request input; producer identity deferred')
print('WARM_HISTORY_REQUIRED=F-1,F-2,F-3')
print('SEQUENCES='+str(seq_cases))
print('REQUEST_CASES='+str(request_cases))
print('COMPOSED_OUTPUT_MATCH=byte-exact vs independent CF+CG+CH calls')
print('CI_VERIFY=PASS')
