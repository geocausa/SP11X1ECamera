#!/usr/bin/env python3
from pathlib import Path
import ctypes, json, math, random, subprocess, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
BS=BASE/'bs-native-aec-three-target-preview-profile'
N=7; T=3

cp=subprocess.run([str(BS/'verify-bs.py')],cwd=BS,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if cp.returncode: raise AssertionError(f'BS failed\n{cp.stdout}\n{cp.stderr}')
assert 'BS_VERIFY=PASS' in cp.stdout,cp.stdout

hdr=(HERE/'native-convergence.h').read_text(); src=(HERE/'native-convergence.c').read_text()
for token in ('struct e003i_history_f1','struct e003i_history_f2','struct e003i_history_f3',
              'short_exposure','long_exposure','safe_exposure','float drc_gain','float previous_delta',
              'e003i_converge_front_preview_unlocked_minimal_history'):
    assert token in hdr,token
assert 'uint64_t lanes[E003I_CONV_LANES];' not in hdr
for token in (
 'in->history1.lanes[E003I_LANE_SAFE]','in->history2.lanes[E003I_LANE_SAFE]',
 'in->delayed_history.lanes[E003I_LANE_SAFE]','in->history1.previous_delta',
 'adjusted_history_lane(&in->history1,t)','adjusted_history_lane(&in->history2,t)',
 'get_exposure_info(in,0,normal[E003I_LANE_SAFE])','get_exposure_info(in,1,normal[E003I_LANE_SAFE])',
 'rt.history1.lanes[E003I_LANE_SHORT] = in->history1.short_exposure',
 'rt.history2.drc_gain = in->history2.drc_gain',
 'rt.delayed_history.lanes[E003I_LANE_SAFE] = in->delayed_history.safe_exposure'):
    assert token in src,token

cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math']
tmp=Path(tempfile.mkdtemp(prefix='e003i-bt-')); bsso=tmp/'bs.so'; btso=tmp/'bt.so'
subprocess.run(cc+[str(BS/'native-convergence.c'),'-I',str(BS),'-lm','-o',str(bsso)],check=True)
subprocess.run(cc+[str(HERE/'native-convergence.c'),'-I',str(HERE),'-lm','-o',str(btso)],check=True)
bs=ctypes.CDLL(str(bsso)); bt=ctypes.CDLL(str(btso))

class Hist(ctypes.Structure):
    _fields_=[('lanes',ctypes.c_uint64*N),('drc_gain',ctypes.c_float),('previous_delta',ctypes.c_float)]
class BSIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*T),('history1',Hist),('history2',Hist),('delayed_history',Hist)]
class H1(ctypes.Structure):
    _fields_=[('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('drc_gain',ctypes.c_float),('previous_delta',ctypes.c_float)]
class H2(ctypes.Structure):
    _fields_=[('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('drc_gain',ctypes.c_float)]
class H3(ctypes.Structure): _fields_=[('safe_exposure',ctypes.c_uint64)]
class BTIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*T),('history1',H1),('history2',H2),('delayed_history',H3)]
class Out(ctypes.Structure):
    _fields_=[('basic_safe_log',ctypes.c_double),('post_stretch_log',ctypes.c_double*N),('final_log',ctypes.c_double*N),
              ('linear',ctypes.c_uint64*N),('pred_gain',ctypes.c_float),('short_stretch',ctypes.c_float),('safe_stretch',ctypes.c_float),
              ('stretch_ratio',ctypes.c_float),('drc_ratio',ctypes.c_float),('basic_direction_ok',ctypes.c_uint32),('drc_branch',ctypes.c_uint32)]
bs.e003i_converge_front_preview_unlocked_three_target.argtypes=[ctypes.POINTER(BSIn),ctypes.POINTER(Out)]
bs.e003i_converge_front_preview_unlocked_three_target.restype=ctypes.c_int
bt.e003i_converge_front_preview_unlocked_minimal_history.argtypes=[ctypes.POINTER(BTIn),ctypes.POINTER(Out)]
bt.e003i_converge_front_preview_unlocked_minimal_history.restype=ctypes.c_int

POW_BASE=1.0299999713897705078125
def lin(x): return max(1,int(math.pow(POW_BASE,float(x))))
def obytes(o): return ctypes.string_at(ctypes.byref(o),ctypes.sizeof(o))
def set_retained(full,short,long,safe,drc,delta=0.0):
    full.lanes[0]=short; full.lanes[1]=long; full.lanes[2]=safe; full.drc_gain=drc; full.previous_delta=delta

def random_dropped(full,rng,keep=(0,1,2)):
    for i in range(N):
        if i not in keep: full.lanes[i]=rng.randrange(1,1<<40)

def copy_full_retained(dst,src):
    dst.lanes[0]=src.lanes[0]; dst.lanes[1]=src.lanes[1]; dst.lanes[2]=src.lanes[2]
    dst.drc_gain=src.drc_gain; dst.previous_delta=src.previous_delta

# Fail closed on missing required history.
o=Out(); assert bt.e003i_converge_front_preview_unlocked_minimal_history(None,ctypes.byref(o))==-1
bad=BTIn(); bad.target_log[:]=(1.0,2.0,3.0)
assert bt.e003i_converge_front_preview_unlocked_minimal_history(ctypes.byref(bad),ctypes.byref(o))==-2

rng=random.Random(0xE0031E); cases=0; branches={}
for k in range(2048):
    h1s=rng.uniform(65,220); h2s=h1s+rng.uniform(-3,3); h3s=h1s+rng.uniform(-5,5)
    h1vals=(lin(h1s+rng.uniform(-8,2)),lin(h1s+rng.uniform(-3,4)),lin(h1s))
    h2vals=(lin(h2s+rng.uniform(-8,2)),lin(h2s+rng.uniform(-3,4)),lin(h2s))
    h3safe=lin(h3s)
    h1d=rng.choice([1.0,1.0,1.25,1.5,2.0]); h2d=rng.choice([1.0,1.25,1.5])
    h1delta=rng.choice([-4.0,-2.0,-1.0,0.0,1.0,2.0,4.0])
    ts=h1s+rng.uniform(-10,10); targets=(ts+rng.uniform(-9,0),ts+rng.uniform(-2,5),ts)

    a=BSIn(); b=BSIn(); a.target_log[:]=targets; b.target_log[:]=targets
    set_retained(a.history1,*h1vals,h1d,h1delta); set_retained(a.history2,*h2vals,h2d,rng.uniform(-100,100))
    set_retained(b.history1,*h1vals,h1d,h1delta); set_retained(b.history2,*h2vals,h2d,rng.uniform(100,300))
    a.delayed_history.lanes[2]=h3safe; b.delayed_history.lanes[2]=h3safe
    # Dropped metadata varies independently.
    a.delayed_history.drc_gain=rng.uniform(0.2,8.0); b.delayed_history.drc_gain=rng.uniform(9.0,20.0)
    a.delayed_history.previous_delta=rng.uniform(-50,50); b.delayed_history.previous_delta=rng.uniform(60,160)
    random_dropped(a.history1,rng); random_dropped(b.history1,rng)
    random_dropped(a.history2,rng); random_dropped(b.history2,rng)
    # F3 drops Short/Long and S1..S4, retaining only Safe.
    random_dropped(a.delayed_history,rng,keep=(2,)); random_dropped(b.delayed_history,rng,keep=(2,))

    x=BTIn(); x.target_log[:]=targets
    x.history1.short_exposure=h1vals[0]; x.history1.long_exposure=h1vals[1]; x.history1.safe_exposure=h1vals[2]
    x.history1.drc_gain=h1d; x.history1.previous_delta=h1delta
    x.history2.short_exposure=h2vals[0]; x.history2.long_exposure=h2vals[1]; x.history2.safe_exposure=h2vals[2]; x.history2.drc_gain=h2d
    x.delayed_history.safe_exposure=h3safe

    oa=Out(); ob=Out(); ox=Out()
    ra=bs.e003i_converge_front_preview_unlocked_three_target(ctypes.byref(a),ctypes.byref(oa))
    rb=bs.e003i_converge_front_preview_unlocked_three_target(ctypes.byref(b),ctypes.byref(ob))
    rx=bt.e003i_converge_front_preview_unlocked_minimal_history(ctypes.byref(x),ctypes.byref(ox))
    assert ra==rb==rx==0,(k,ra,rb,rx)
    assert obytes(oa)==obytes(ob),('removed-history-invariance',k)
    assert obytes(oa)==obytes(ox),('bt-projection',k)
    branches[int(ox.drc_branch)]=branches.get(int(ox.drc_branch),0)+1; cases+=1

print('PROFILE=normal-streaming AEC-unlocked single-exposure')
print('PUBLIC_HISTORY_F1=Short,Long,Safe,drc_gain,previous_delta')
print('PUBLIC_HISTORY_F2=Short,Long,Safe,drc_gain')
print('PUBLIC_HISTORY_F3=Safe')
print(f'REMOVED_HISTORY_INVARIANCE_CASES={cases}')
print('DRC_BRANCH_COUNTS='+json.dumps(branches,sort_keys=True))
print('BS_MINIMAL_HISTORY_PROJECTION_MATCH=bit-exact')
print('BT_VERIFY=PASS')
