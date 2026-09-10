#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, importlib.util, math, random, struct, subprocess, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
AQ=BASE/'aq-windows-aec-arbitration-table'
AX=BASE/'ax-windows-aec-convergence-history-loop'
DLL=REPO.parent.parent/'00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd9de785509c1fbebc975facc5286f12865cf675f1d'
# Replace the hash from a committed checkpoint rather than trust hand transcription.
SHA=[x.split('=',1)[1] for x in (BASE/'cg-native-aec-qword-convergence-input'/'VERIFY-RESULT.txt').read_text().splitlines() if x.startswith('DLL_SHA256=')][0]
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA

def dis(a,b): return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)
def need(t,*xs):
    for x in xs: assert x in t,x

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def fbits(x): return struct.unpack('<I',struct.pack('<f',f32(x)))[0]

def frinta_pos(x):
    assert math.isfinite(x) and x>=0
    return int(math.floor(float(x)+0.5))

# Require committed topology/replay ancestry and rerun the small static AX proof.
for commit in ('97f2236','b17365c'):
    cp=subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=REPO)
    assert cp.returncode==0,(commit,'missing')
cp=subprocess.run(['python3',str(AX/'verify-ax.py')],cwd=AX,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert cp.returncode==0,(cp.stdout,cp.stderr)
assert 'AX_VERIFY=PASS' in cp.stdout

# AQ is the independent clean replay of the pinned table/range-fit arithmetic.
spec=importlib.util.spec_from_file_location('aqreplay',AQ/'E003I-AQ-aec-arbitration-replay.py')
aq=importlib.util.module_from_spec(spec); spec.loader.exec_module(aq)
assert aq.KNEES==[(1,1.0,37516),(1,67.0,33333333),(1,67.0,66666666),(0,92.0,66666666)]
prods=[aq.exposure_product(g,t) for _,g,t in aq.KNEES]
assert prods==[37516,2233333311,4466666622,6133333272]

# AQ's later same-machine read-only range recapture is the active controller
# source for preview limits; do not regress to the old nearby 33.333 ms value.
rr=AQ/'windows-evidence/range-recapture-20260910'
assert hashlib.sha256((rr/'E003I-CH-RANGE-RECAPTURE.zip').read_bytes()).hexdigest()=='809e7d58ba5605cbd5f98bcc2e2b41c12843dcc79e91cf2fd86e43647a9e8c67'
ctrl=(rr/'controller-plus-0100.bin').read_bytes(); assert len(ctrl)==0xe0
assert struct.unpack_from('<f',ctrl,0x28)[0]==1.0 and struct.unpack_from('<Q',ctrl,0x30)[0]==37516
assert struct.unpack_from('<f',ctrl,0x50)[0]==92.0 and struct.unpack_from('<Q',ctrl,0x58)[0]==66666664
assert struct.unpack_from('<Q',ctrl,0xa0)[0]==0

# Final post-fit retained exposure path mechanically uses the fit gain/time,
# correction, FRINTA, then stores qword at table result +0x18.
t=dis(0x1803c3bd0,0x1803c4210)
need(t,
 '1803c3c20:', 'ldr\ts8, [x8, #0x10]',
 '1803c3c24:', 'ldr\tx25, [x8, #0x18]',
 '1803c4184:', 'fmul\td13, d16, d14',
 '1803c41c0:', 'str\ts8, [x20]',
 '1803c41c4:', 'str\tx25, [x20, #0x8]',
 '1803c41d4:', 'ldr\ts16, [x8, #0x24]',
 '1803c41e0:', 'fmul\td0, d16, d13',
 '1803c41e4:', 'bl\t0x1800014b0',
 '1803c41f0:', 'str\tx8, [x20, #0x18]')
fr=dis(0x1800014b0,0x1800014c0)
need(fr,'1800014b0:','frinta\td0, d0','1800014b4:','ret')

# Compile native CH.
td=Path(tempfile.mkdtemp(prefix='e003i-ch-')); so=td/'ch.so'
cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
subprocess.run(cc+[str(HERE/'native-t681.c'),'-I',str(HERE),'-lm','-o',str(so)],check=True)
lib=ctypes.CDLL(str(so))
class R(ctypes.Structure):
    _fields_=[('gain',ctypes.c_float),('exposure_time_ns',ctypes.c_uint64),('correction',ctypes.c_float),('retained_exposure',ctypes.c_uint64),('upper_knee',ctypes.c_uint32)]
lib.e003i_t681_preview_arbitrate.argtypes=[ctypes.c_uint64,ctypes.POINTER(R)]
lib.e003i_t681_preview_arbitrate.restype=ctypes.c_int
assert lib.e003i_t681_preview_arbitrate(1000,None)==-1
r=R(); assert lib.e003i_t681_preview_arbitrate(prods[0]-1,ctypes.byref(r))==-2
assert lib.e003i_t681_preview_arbitrate(prods[-1]+1,ctypes.byref(r))==-2

# Independent expected result = AQ table + AQ preview fit + AX final retained FRINTA.
def reference(target):
    tab=aq.apply_core_table(int(target))
    fit=aq.make_table_exposure_fit(tab,1.0,37516,92.0,66666664)
    assert fit['ok']
    product=(float(fit['gain'])*float(fit['time']))*float(fit['corr'])
    return fbits(fit['gain']),int(fit['time']),fbits(fit['corr']),frinta_pos(product),int(tab['upper']),int(fit['desired'])

def native(target):
    o=R(); rc=lib.e003i_t681_preview_arbitrate(int(target),ctypes.byref(o)); assert rc==0,(target,rc)
    return fbits(o.gain),int(o.exposure_time_ns),fbits(o.correction),int(o.retained_exposure),int(o.upper_knee)

# Knee boundaries, preview cap transitions, observed neighborhood and random corpus.
tests=set()
for p in prods:
    for d in range(-4,5):
        if prods[0] <= p+d <= prods[-1]: tests.add(p+d)
for p in (33333332,33333333,66666664,66666665,241379190,241379203,241379204,241379210,2233333311,4466666622):
    if prods[0]<=p<=prods[-1]: tests.add(p)
rng=random.Random(0x681C8)
for _ in range(65536): tests.add(rng.randrange(prods[0],prods[-1]+1))

retained_diff=0; seg={1:0,2:0,3:0}
for target in sorted(tests):
    ref=reference(target); got=native(target)
    assert got==ref[:5],(target,got,ref)
    seg[got[4]]+=1
    # Prove retained qword is a separate post-fit quantity; count cases where
    # it differs from AQ's preserved pre-fit desired value.
    if got[3] != ref[5]: retained_diff+=1
assert retained_diff>0

# Fixed known values useful for later integration guards.
for target in (37516,241379204,2233333311,4466666622,6133333272):
    print('FIX',target,native(target),'desired',reference(target)[5])

print('DLL_SHA256='+SHA)
print('TABLE681=1@37516;67@33333333;67@66666666;92@66666666')
print('PREVIEW_LIMITS=minGain1,minTime37516,maxGain92,maxTime66666664')
print('RETAINED_EXPOSURE=FRINTA(double(f32 gain)*double(time)*double(f32 correction))')
print('DIFFERENTIAL_CASES='+str(len(tests)))
print('SEGMENT_COUNTS='+str(seg))
print('RETAINED_DIFFERS_FROM_PRESERVED_DESIRED_CASES='+str(retained_diff))
print('NATIVE_T681_PREVIEW_MATCH=bit-exact gain/time/retained')
print('CH_VERIFY=PASS')
