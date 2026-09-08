#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, math, random, struct, subprocess, sys, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
CE=BASE/'ce-native-aec-final-target-producer'
CC=BASE/'cc-native-aec-adrc-darkboost-tail'
BY=BASE/'by-native-aec-method11-point-aggregation'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
# Canonical DLL SHA from every prior checkpoint; keep a separately literal value
# so this verifier fails rather than silently accepting a typo above.
CANONICAL_DLL='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL_SHA==CANONICAL_DLL
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert TUNING.is_file() and hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA
sys.path.insert(0,str(REPO/'tools'))
import qti_parameter_bin as qti

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)
def need(t,*xs):
    for x in xs: assert x in t,x

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def fbits(x): return struct.unpack('<I',struct.pack('<f',f32(x)))[0]

# CE is the immediately preceding native producer contract; require its committed
# ancestry and rerun its compact verifier fresh.
cp=subprocess.run(['git','merge-base','--is-ancestor','db49d42','HEAD'],cwd=REPO)
assert cp.returncode==0,'CE ancestry missing'
cp=subprocess.run([sys.executable,str(CE/'verify-ce.py')],cwd=CE,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert cp.returncode==0,(cp.stdout,cp.stderr)
assert 'CE_VERIFY=PASS' in cp.stdout,cp.stdout

# Final aggregators 3/4/5 all source from tuning sourceType 3 = S1.
obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
raw=bytes.fromhex(ids[3592]['raw_hex']); assert len(raw)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',raw[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w
for aid,etype in ((3,1),(4,0),(5,2)):
    r=recs[aid]
    assert r[5]==etype and r[6]==3,(aid,r[5],r[6])

# Windows positive phase-2 publication path: read positive AdjRatio, promote
# f32->d64, multiply selected S1 d64, FCVTZU, store qword.
run=dis(0x1803f15e0,0x1803f16c4)
need(run,
 '1803f15e0:', 'ldr\tw0, [x19, #0x2c]',
 '1803f15f0:', 'bl\t0x180388630',
 '1803f15f4:', 'add\tx20, x20, w0, sxtw #3',
 '1803f15fc:', 'ldr\td8, [x20]',
 '1803f1668:', 'ldp\tw9, w8, [x8, #0xf0]',
 '1803f1678:', 'bl\t0x1803d5d30',
 '1803f1680:', 'fcmpe\ts9, #0.0',
 '1803f1688:', 'fmov\ts16, s9',
 '1803f16ac:', 'fcvt\td16, s16',
 '1803f16b4:', 'fmul\td16, d16, d8',
 '1803f16b8:', 'fcvtzu\tx8, d16',
 '1803f16bc:', 'str\tx8, [x19, #0x20]')

# Compile the exact native composition: CF + CE + CC + BY.
tmp=Path(tempfile.mkdtemp(prefix='e003i-cf-')); so=tmp/'cf.so'
cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
subprocess.run(cc+[
 str(HERE/'native-final-exposure.c'),
 str(CE/'native-final-target.c'),
 str(CC/'native-aec-tail.c'),
 str(BY/'native-target-aggregate.c'),
 '-I',str(HERE),'-I',str(CE),'-I',str(CC),'-I',str(BY),'-lm','-o',str(so)],check=True)
lib=ctypes.CDLL(str(so))

class Cand(ctypes.Structure): _fields_=[('value',ctypes.c_float),('confidence',ctypes.c_float)]
class TIn(ctypes.Structure):
    _fields_=[('lux_index',ctypes.c_float),('frame',Cand),('sat_prev',Cand),('dark_prev',Cand),
              ('brighten',Cand),('extreme_color',Cand),('illuminance',Cand),
              ('short_sat_prev',Cand),('long_dark_prev',Cand)]
class TailOut(ctypes.Structure):
    _fields_=[('adrc_lux_face_cap',ctypes.c_float),('adj_ratio_short',ctypes.c_float),
              ('adrc_gain',ctypes.c_float),('short_adj_ratio',ctypes.c_float),
              ('drc_gain_remainder',ctypes.c_float),('adj_ratio_long',ctypes.c_float),
              ('dark_boost_gain',ctypes.c_float),('long_adj_ratio',ctypes.c_float)]
class TOut(ctypes.Structure):
    _fields_=[('safe_target',ctypes.c_float),('safe_adj_ratio',ctypes.c_float),
              ('short_target',ctypes.c_float),('long_target',ctypes.c_float),('tail',TailOut)]
class FIn(ctypes.Structure): _fields_=[('source_exposure_s1',ctypes.c_uint64),('target_input',TIn)]
class FOut(ctypes.Structure):
    _fields_=[('targets',TOut),('short_exposure',ctypes.c_uint64),
              ('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64)]
lib.e003i_aec_default_final_targets.argtypes=[ctypes.POINTER(TIn),ctypes.POINTER(TOut)]
lib.e003i_aec_default_final_targets.restype=ctypes.c_int
lib.e003i_aec_default_final_exposures.argtypes=[ctypes.POINTER(FIn),ctypes.POINTER(FOut)]
lib.e003i_aec_default_final_exposures.restype=ctypes.c_int

# API failure behavior.
o=FOut(); assert lib.e003i_aec_default_final_exposures(None,ctypes.byref(o))==-1

# Reference the exact positive/in-range FCVTZU semantics. Python float is IEEE
# binary64 and int() truncates toward zero for positive finite values.
def qword(source,ratio):
    product=float(int(source))*float(f32(ratio))
    assert math.isfinite(product) and 0.0 <= product < 2.0**64
    return int(product)

def make_input(rng):
    x=TIn(); x.lux_index=f32(rng.uniform(0.0,1000.0))
    # Keep values/weights in the valid positive ordinary producer domain.
    vals=[rng.uniform(1.0,220.0) for _ in range(8)]
    ws=[rng.choice([0.0,0.001,0.01,0.1,0.25,0.5,1.0,2.0]) for _ in range(8)]
    if not any(w>0 for w in ws[:6]): ws[0]=1.0
    fields=['frame','sat_prev','dark_prev','brighten','extreme_color','illuminance','short_sat_prev','long_dark_prev']
    for n,v,w in zip(fields,vals,ws): setattr(x,n,Cand(f32(v),f32(w)))
    return x

# Exercise integer->double rounding boundaries explicitly as well as ordinary S1 values.
sources=[0,1,2,999,10_000_000,2**24-1,2**24+1,2**32-1,2**32+1,
         2**53-1,2**53,2**53+1,2**53+3]
rng=random.Random(0xE0031F); cases=0; boundary_cases=0
for source in sources:
    for _ in range(64):
        ti=make_input(rng); ce=TOut(); rc=lib.e003i_aec_default_final_targets(ctypes.byref(ti),ctypes.byref(ce))
        if rc!=0: continue
        ratios=[ce.tail.short_adj_ratio,ce.tail.long_adj_ratio,ce.safe_adj_ratio]
        if any(float(source)*float(f32(r)) >= 2.0**64 for r in ratios): continue
        fi=FIn(source,ti); fo=FOut(); assert lib.e003i_aec_default_final_exposures(ctypes.byref(fi),ctypes.byref(fo))==0
        assert ctypes.string_at(ctypes.byref(fo.targets),ctypes.sizeof(TOut)) == ctypes.string_at(ctypes.byref(ce),ctypes.sizeof(TOut))
        exp=(qword(source,ratios[0]),qword(source,ratios[1]),qword(source,ratios[2]))
        got=(fo.short_exposure,fo.long_exposure,fo.safe_exposure)
        assert got==exp,(source,[fbits(r) for r in ratios],got,exp)
        cases+=1; boundary_cases+=source>=2**53-1

for _ in range(16384):
    ti=make_input(rng); ce=TOut(); rc=lib.e003i_aec_default_final_targets(ctypes.byref(ti),ctypes.byref(ce))
    if rc!=0: continue
    source=rng.randrange(0,2_000_000_000)
    ratios=[ce.tail.short_adj_ratio,ce.tail.long_adj_ratio,ce.safe_adj_ratio]
    fi=FIn(source,ti); fo=FOut(); assert lib.e003i_aec_default_final_exposures(ctypes.byref(fi),ctypes.byref(fo))==0
    exp=(qword(source,ratios[0]),qword(source,ratios[1]),qword(source,ratios[2]))
    assert (fo.short_exposure,fo.long_exposure,fo.safe_exposure)==exp
    cases+=1

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('FINAL_SOURCE_TYPES=SafeAgg:S1,ShortAgg:S1,LongAgg:S1')
print('WINDOWS_PUBLICATION=f32 AdjRatio -> d64; d64*S1; FCVTZU qword')
print('SOURCE_API=uint64_t S1 converted to double at publication')
print('DOUBLE_INTEGER_BOUNDARY_CASES='+str(boundary_cases))
print('DIFFERENTIAL_CASES='+str(cases))
print('NATIVE_FINAL_EXPOSURE_PUBLICATION_MATCH=bit-exact-qword')
print('CF_VERIFY=PASS')
