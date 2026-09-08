#!/usr/bin/env python3
from pathlib import Path
import ctypes, json, math, random, subprocess, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
BR=BASE/'br-native-aec-unlocked-preview-profile'
N=7
T=3

# Re-establish the immediate native prerequisite (BR itself re-runs BQ and BP).
cp=subprocess.run([str(BR/'verify-br.py')],cwd=BR,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if cp.returncode:
    raise AssertionError(f'BR failed\n{cp.stdout}\n{cp.stderr}')
assert 'BR_VERIFY=PASS' in cp.stdout,cp.stdout

hdr=(HERE/'native-convergence.h').read_text()
src=(HERE/'native-convergence.c').read_text()
assert '#define E003I_TARGET_LANES 3' in hdr
assert 'double target_log[E003I_TARGET_LANES];' in hdr
assert 'struct e003i_front_preview_unlocked_three_target_input' in hdr
assert 'e003i_converge_front_preview_unlocked_three_target' in hdr
# The public request must not expose a seven-target array; private carrier may.
pub=hdr.split('struct e003i_front_preview_unlocked_three_target_input',1)[1].split('};',1)[0]
assert 'target_log[E003I_CONV_LANES]' not in pub
# Retain full histories for this checkpoint.
assert 'uint64_t lanes[E003I_CONV_LANES];' in hdr

# Mechanical consumption/overwrite anchors.
for token in (
    'target=in->target_log[E003I_LANE_SAFE]',
    'targetlane=in->target_log[t]',
    'get_exposure_info(in,0,normal[E003I_LANE_SAFE])',
    'get_exposure_info(in,1,normal[E003I_LANE_SAFE])',
    'for(i=3;i<7;i++) final[i]=final[E003I_LANE_SHORT]',
    'memcpy(rt.target_log, in->target_log, sizeof(in->target_log))'):
    assert token in src,token

cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math']
tmp=Path(tempfile.mkdtemp(prefix='e003i-bs-'))
brso=tmp/'br.so'; bsso=tmp/'bs.so'
subprocess.run(cc+[str(BR/'native-convergence.c'),'-I',str(BR),'-lm','-o',str(brso)],check=True)
subprocess.run(cc+[str(HERE/'native-convergence.c'),'-I',str(HERE),'-lm','-o',str(bsso)],check=True)
br=ctypes.CDLL(str(brso)); bs=ctypes.CDLL(str(bsso))

class Hist(ctypes.Structure):
    _fields_=[('lanes',ctypes.c_uint64*N),('drc_gain',ctypes.c_float),('previous_delta',ctypes.c_float)]
class BRIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*N),('history1',Hist),('history2',Hist),('delayed_history',Hist)]
class BSIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*T),('history1',Hist),('history2',Hist),('delayed_history',Hist)]
class Out(ctypes.Structure):
    _fields_=[('basic_safe_log',ctypes.c_double),('post_stretch_log',ctypes.c_double*N),('final_log',ctypes.c_double*N),
              ('linear',ctypes.c_uint64*N),('pred_gain',ctypes.c_float),('short_stretch',ctypes.c_float),('safe_stretch',ctypes.c_float),
              ('stretch_ratio',ctypes.c_float),('drc_ratio',ctypes.c_float),('basic_direction_ok',ctypes.c_uint32),('drc_branch',ctypes.c_uint32)]

br.e003i_converge_front_preview_unlocked.argtypes=[ctypes.POINTER(BRIn),ctypes.POINTER(Out)]
br.e003i_converge_front_preview_unlocked.restype=ctypes.c_int
bs.e003i_converge_front_preview_unlocked_three_target.argtypes=[ctypes.POINTER(BSIn),ctypes.POINTER(Out)]
bs.e003i_converge_front_preview_unlocked_three_target.restype=ctypes.c_int

POW_BASE=1.0299999713897705078125
def lin(logv): return max(1,int(math.pow(POW_BASE,float(logv))))
def fill_hist(h,logs,drc,delta):
    h.lanes[:]=[lin(x) for x in logs]
    h.drc_gain=drc; h.previous_delta=delta

def copy_hist(dst,src):
    dst.history1=src.history1; dst.history2=src.history2; dst.delayed_history=src.delayed_history

def outbytes(x): return ctypes.string_at(ctypes.byref(x),ctypes.sizeof(x))

# Preserve fail-closed behavior.
o=Out(); assert bs.e003i_converge_front_preview_unlocked_three_target(None,ctypes.byref(o))==-1
bad=BSIn(); bad.target_log[:]=(1.0,2.0,3.0)
assert bs.e003i_converge_front_preview_unlocked_three_target(ctypes.byref(bad),ctypes.byref(o))==-2

rng=random.Random(0xE0031D); cases=0; branch_counts={}
for k in range(2048):
    x=BSIn()
    h1s=rng.uniform(65.0,220.0); h2s=h1s+rng.uniform(-3.0,3.0); hds=h1s+rng.uniform(-5.0,5.0)
    def logs(s):
        return (s+rng.uniform(-8,2),s+rng.uniform(-3,4),s,
                s+rng.uniform(-6,3),s+rng.uniform(-6,3),s+rng.uniform(-6,3),s+rng.uniform(-6,3))
    fill_hist(x.history1,logs(h1s),rng.choice([1.0,1.0,1.25,1.5,2.0]),rng.choice([-4.0,-2.0,-1.0,0.0,1.0,2.0,4.0]))
    fill_hist(x.history2,logs(h2s),rng.choice([1.0,1.25,1.5]),rng.choice([-2.0,0.0,2.0]))
    fill_hist(x.delayed_history,logs(hds),1.0,0.0)
    ts=h1s+rng.uniform(-10.0,10.0)
    current=(ts+rng.uniform(-9,0),ts+rng.uniform(-2,5),ts)
    x.target_log[:]=current

    a=BRIn(); b=BRIn(); copy_hist(a,x); copy_hist(b,x)
    a.target_log[:]=current+tuple(ts+rng.uniform(-80,80) for _ in range(4))
    b.target_log[:]=current+tuple(ts+rng.uniform(100,220) for _ in range(4))
    oa=Out(); ob=Out(); ox=Out()
    ra=br.e003i_converge_front_preview_unlocked(ctypes.byref(a),ctypes.byref(oa))
    rb=br.e003i_converge_front_preview_unlocked(ctypes.byref(b),ctypes.byref(ob))
    rx=bs.e003i_converge_front_preview_unlocked_three_target(ctypes.byref(x),ctypes.byref(ox))
    assert ra==rb==rx==0,(k,ra,rb,rx)
    assert outbytes(oa)==outbytes(ob),('hidden-target-invariance',k)
    assert outbytes(oa)==outbytes(ox),('bs-projection',k)
    branch_counts[int(ox.drc_branch)]=branch_counts.get(int(ox.drc_branch),0)+1
    cases+=1

print('PROFILE=normal-streaming AEC-unlocked single-exposure')
print('PUBLIC_CURRENT_TARGET_LANES=Short,Long,Safe')
print('DROPPED_CURRENT_TARGET_LANES=S1,S2,S3,S4')
print(f'HIDDEN_TARGET_INVARIANCE_CASES={cases}')
print('DRC_BRANCH_COUNTS='+json.dumps(branch_counts,sort_keys=True))
print('BR_THREE_TARGET_PROJECTION_MATCH=bit-exact')
print('BS_VERIFY=PASS')
