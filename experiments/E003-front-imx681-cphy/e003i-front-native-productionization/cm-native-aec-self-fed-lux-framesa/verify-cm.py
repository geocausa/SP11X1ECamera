#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, importlib.util, math, random, struct, subprocess, sys, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
CF=BASE/'cf-native-aec-final-exposure-si'
CE=BASE/'ce-native-aec-final-target-producer'
CC=BASE/'cc-native-aec-adrc-darkboost-tail'
BY=BASE/'by-native-aec-method11-point-aggregation'
CG=BASE/'cg-native-aec-qword-convergence-input'
CH=BASE/'ch-native-aec-t681-preview-arbitration'
BK=BASE/'bk-native-aec-history-state'
BJ=BASE/'bj-native-aec-log103-coordinate'
CL=BASE/'cl-native-aec-self-fed-s1-history'
BG=BASE/'bg-windows-aec-framesa-target-lux'
BZ=BASE/'bz-windows-aec-final-adjratio-publication'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert TUNING.is_file() and hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA

def fresh(d,script,marker,extra=()):
    p=d/script
    cp=subprocess.run([str(p)],cwd=d,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert cp.returncode==0,(p,cp.stdout,cp.stderr)
    assert marker in cp.stdout,(p,marker,cp.stdout)
    for x in extra: assert x in cp.stdout,(p,x,cp.stdout)
    return cp.stdout

fresh(CL,'verify-cl.py','CL_VERIFY=PASS',('SOURCE_S1_RECURRENCE=history[F-3].S1',))
fresh(BK,'verify-bk.py','BK_VERIFY=PASS',('F3_HISTORY_INPUT=S1 linear exposure -> BJ log103 coordinate',))
fresh(BG,'verify-bg.py','BG_VERIFY=PASS',('CONFIDENCE_0P001_IS_NOT_TARGET=PASS',))
fresh(BZ,'verify-bz.py','BZ_VERIFY=PASS',('FRAME_ADJRATIO=3:7=(3:5)/(3:4)',))
assert subprocess.run(['git','merge-base','--is-ancestor','e012082','HEAD'],cwd=REPO).returncode==0

# Public seam reduction: no request Lux and no request Frame candidate.
h=(HERE/'native-aec-request-loop.h').read_text()
c=(HERE/'native-aec-request-loop.c').read_text()
ib=h.split('struct e003i_request_loop_input {',1)[1].split('};',1)[0]
rb=h.split('struct e003i_remaining_analyzer_input {',1)[1].split('};',1)[0]
assert 'lux_index' not in ib and 'frame_candidate' not in ib
assert 'float measured_luma;' in ib
assert rb.count('struct e003i_aec_candidate')==7
for n in ('sat_prev','dark_prev','brighten','extreme_color','illuminance','short_sat_prev','long_dark_prev'):
    assert n in rb
assert 'fi.target_input.lux_index = lux_in;' in c
assert 'fi.target_input.frame.value = frame_adj;' in c
assert 'fi.target_input.frame.confidence = frame_conf;' in c
assert 'f32bits(0x3a83126fU)' in c
assert 'state->lux_trigger = next_lux;' in c

# Independently parse the exact FrameSA confidence terminal from pinned tuning.
sys.path.insert(0,str(REPO/'tools'))
import qti_parameter_bin as qti
obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
calc=struct.unpack('<18I',bytes.fromhex(ids[3607]['raw_hex']))
assert calc==(1,19,0,9,8,9,8,1,3608, 1,19,0,9,8,9,8,1,3610)
conf=struct.unpack('<fff',bytes.fromhex(ids[3609]['raw_hex']))
weight=struct.unpack('<fff',bytes.fromhex(ids[3611]['raw_hex']))
assert conf[:2]==(0.0,1000.0)
assert struct.unpack('<I',struct.pack('<f',conf[2]))[0]==0x3a83126f
assert weight==(0.0,1000.0,1.0)

# Load BH's separately verified float32 reference model for FrameSA/Algorithm001.
bh_path=BASE/'bh-native-aec-request-state'/'windows-aec-request-state.py'
spec=importlib.util.spec_from_file_location('e003i_bh_ref',bh_path)
bh=importlib.util.module_from_spec(spec); sys.modules[spec.name]=bh; spec.loader.exec_module(bh)

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def fbits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def bytesof(x): return ctypes.string_at(ctypes.byref(x),ctypes.sizeof(x))
CONF=f32(struct.unpack('<f',struct.pack('<I',0x3a83126f))[0])

# Compile complete CM composition under the same strict FP policy.
td=Path(tempfile.mkdtemp(prefix='e003i-cm-')); so=td/'cm.so'
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
class State(ctypes.Structure): _fields_=[('lux_trigger',ctypes.c_float),('algorithm001_alpha',ctypes.c_float),('history',HE*16)]
class Rem(ctypes.Structure):
    _fields_=[('sat_prev',Cand),('dark_prev',Cand),('brighten',Cand),('extreme_color',Cand),('illuminance',Cand),('short_sat_prev',Cand),('long_dark_prev',Cand)]
class RIn(ctypes.Structure): _fields_=[('frame_id',ctypes.c_uint64),('measured_luma',ctypes.c_float),('analyzers',Rem)]
class ROut(ctypes.Structure):
    _fields_=[('lux_trigger_in',ctypes.c_float),('frame_target',ctypes.c_float),('frame_candidate',Cand),('history_reference_log103',ctypes.c_float),('next_lux_trigger',ctypes.c_float),('target_publication',FOut),('convergence',COut),('short_arbitration',AOut),('long_arbitration',AOut),('safe_arbitration',AOut),('s1_arbitration',AOut)]

lib.e003i_request_loop_init.argtypes=[ctypes.POINTER(State),ctypes.c_float,ctypes.c_float]; lib.e003i_request_loop_init.restype=ctypes.c_int
lib.e003i_request_loop_seed_history.argtypes=[ctypes.POINTER(State),ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_float]; lib.e003i_request_loop_seed_history.restype=ctypes.c_int
lib.e003i_request_loop_process.argtypes=[ctypes.POINTER(State),ctypes.POINTER(RIn),ctypes.POINTER(ROut)]; lib.e003i_request_loop_process.restype=ctypes.c_int
lib.e003i_aec_default_final_exposures.argtypes=[ctypes.POINTER(FIn),ctypes.POINTER(FOut)]; lib.e003i_aec_default_final_exposures.restype=ctypes.c_int
lib.e003i_converge_front_preview_unlocked_qword_history.argtypes=[ctypes.POINTER(CIn),ctypes.POINTER(COut)]; lib.e003i_converge_front_preview_unlocked_qword_history.restype=ctypes.c_int
lib.e003i_t681_preview_arbitrate.argtypes=[ctypes.c_uint64,ctypes.POINTER(AOut)]; lib.e003i_t681_preview_arbitrate.restype=ctypes.c_int
lib.e003i_log103_coordinate.argtypes=[ctypes.c_uint64]; lib.e003i_log103_coordinate.restype=ctypes.c_float

# Fail closed and preserve state on a rejected request.
s=State(); assert lib.e003i_request_loop_init(ctypes.byref(s),ctypes.c_float(150.0),ctypes.c_float(0.0))==0
assert lib.e003i_request_loop_init(None,ctypes.c_float(0.0),ctypes.c_float(0.0))==-1
assert lib.e003i_request_loop_seed_history(ctypes.byref(s),0,1,1,1,0,1.0)==-1
bad=RIn(); bad.frame_id=3; bad.measured_luma=1.0; bo=ROut()
assert lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(bad),ctypes.byref(bo))==-3
for f in range(3): assert lib.e003i_request_loop_seed_history(ctypes.byref(s),f,1_000_000+f,1_100_000+f,1_200_000+f,1_300_000+f,1.0)==0
bad.analyzers.sat_prev=Cand(float('nan'),1.0)
before=bytesof(s); assert lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(bad),ctypes.byref(bo))!=0; assert bytesof(s)==before

fields=('sat_prev','dark_prev','brighten','extreme_color','illuminance','short_sat_prev','long_dark_prev')
def make_ti(lux,measured,rem):
    ti=TIn(); ti.lux_index=f32(lux)
    target=bh.framesa_target_low(f32(lux))
    adj=f32(f32(target)/f32(measured))
    ti.frame=Cand(adj,CONF)
    for n in fields: setattr(ti,n,getattr(rem,n))
    return ti,target,adj

def standalone(source,ti,h1,h2,h3):
    fi=FIn(source,ti); fo=FOut(); assert lib.e003i_aec_default_final_exposures(ctypes.byref(fi),ctypes.byref(fo))==0
    ci=CIn(); ci.target_exposure[:]=(fo.short_exposure,fo.long_exposure,fo.safe_exposure)
    ci.history1=H1(h1[0],h1[1],h1[2],h1[4]); ci.history2=H2(h2[0],h2[1],h2[2],h2[4]); ci.delayed_history=H3(h3[2])
    co=COut(); assert lib.e003i_converge_front_preview_unlocked_qword_history(ctypes.byref(ci),ctypes.byref(co))==0
    ar=[]
    for lane in (0,1,2,3):
        a=AOut(); rc=lib.e003i_t681_preview_arbitrate(co.linear[lane],ctypes.byref(a)); assert rc==0,(lane,int(co.linear[lane]),rc); ar.append(a)
    return fo,co,ar

# FrameSA fixed facts at representative Lux/gap points.
for lux,expected in ((0,55),(140,55),(150,52.5),(160,50),(285,48),(300,46),(365,43),(370,40),(480,35),(500,30),(1200,30)):
    assert fbits(bh.framesa_target_low(f32(lux)))==fbits(expected)
assert fbits(CONF)==0x3a83126f

# Multi-frame differential. The independent mirror explicitly constructs the
# FrameSA pair from entry Lux and measured luma, then separately advances Lux.
rng=random.Random(0xC1A5C002)
seq_cases=request_cases=0
for seq in range(256):
    alpha=f32(rng.choice([0.0,0.0,0.1,0.25]))
    lux=f32(rng.uniform(20.0,500.0))
    s=State(); assert lib.e003i_request_loop_init(ctypes.byref(s),lux,alpha)==0
    mirror={}
    # Keep successful recurrence cases inside CL's already-proven ordinary
    # target/arbitration domain.  FrameSA itself is intentionally allowed to
    # be numerically large: AB live luma is ~0.60..2.56 while BG target is
    # 30..55, but Frame confidence is only 0.001f.
    base=rng.randrange(8_000_000,30_000_000)
    for f in range(3):
        v=(rng.randrange(base//2,base*2),rng.randrange(base//2,base*2),rng.randrange(base//2,base*2),rng.randrange(base//3,base*3),f32(rng.choice([1.0,1.2,1.5,2.0])))
        mirror[f]=v; assert lib.e003i_request_loop_seed_history(ctypes.byref(s),f,*v)==0
    for f in range(3,11):
        measured=f32(rng.uniform(0.55,2.75))
        rem=Rem()
        for n in fields:
            setattr(rem,n,Cand(f32(rng.uniform(0.72,1.45)),f32(0.0 if rng.random()<0.12 else rng.choice([0.001,0.01,0.05,0.1,0.25,0.5,1.0]))))
        ti,target,adj=make_ti(lux,measured,rem)
        fo,co,ar=standalone(mirror[f-3][3],ti,mirror[f-1],mirror[f-2],mirror[f-3])
        href=f32(lib.e003i_log103_coordinate(mirror[f-3][3]))
        next_lux=bh.algorithm001_lux(measured,href,lux,alpha)
        ri=RIn(f,measured,rem); ro=ROut(); rc=lib.e003i_request_loop_process(ctypes.byref(s),ctypes.byref(ri),ctypes.byref(ro)); assert rc==0,(seq,f,rc)
        assert fbits(ro.lux_trigger_in)==fbits(lux)
        assert fbits(ro.frame_target)==fbits(target)
        assert fbits(ro.frame_candidate.value)==fbits(adj)
        assert fbits(ro.frame_candidate.confidence)==0x3a83126f
        assert fbits(ro.history_reference_log103)==fbits(href)
        assert fbits(ro.next_lux_trigger)==fbits(next_lux)
        assert bytesof(ro.target_publication)==bytesof(fo)
        assert bytesof(ro.convergence)==bytesof(co)
        for got,exp in ((ro.short_arbitration,ar[0]),(ro.long_arbitration,ar[1]),(ro.safe_arbitration,ar[2]),(ro.s1_arbitration,ar[3])):
            assert bytesof(got)==bytesof(exp)
        new=(ar[0].retained_exposure,ar[1].retained_exposure,ar[2].retained_exposure,ar[3].retained_exposure,f32(co.pred_gain)); mirror[f]=new
        he=s.history[f%16]
        assert he.valid and he.frame_id==f and (he.short_exposure,he.long_exposure,he.safe_exposure,he.s1_exposure)==new[:4]
        assert fbits(he.pred_gain)==fbits(new[4]) and fbits(s.lux_trigger)==fbits(next_lux)
        lux=f32(next_lux); request_cases+=1
    seq_cases+=1

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('PUBLIC_REQUEST_LUX=removed')
print('PUBLIC_REQUEST_FRAMESA=removed')
print('PUBLIC_MEASURED_LUMA=retained')
print('FRAMESA_CONFIDENCE_BITS=0x3a83126f')
print('FRAMESA_ADJRATIO=float32(target/luma)')
print('LUX_ORDER=entry Lux -> current FrameSA/CE -> Algorithm001 -> next request Lux')
print('SOURCE_S1=history[F-3].S1')
print('ALGORITHM001_ALPHA=initialization seam')
print('SEQUENCES='+str(seq_cases))
print('REQUEST_CASES='+str(request_cases))
print('COMPOSED_OUTPUT_MATCH=byte-exact explicit FrameSA+CF+CG+CH mirror')
print('CM_VERIFY=PASS')
