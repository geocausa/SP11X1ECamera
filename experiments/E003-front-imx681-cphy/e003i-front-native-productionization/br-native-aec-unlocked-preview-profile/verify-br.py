#!/usr/bin/env python3
from pathlib import Path
import ctypes, json, math, random, subprocess, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
BP=BASE/'bp-native-aec-fixed-preview-profile'
BQ=BASE/'bq-windows-aec-normal-streaming-runtime-state'
N=7

# Re-establish both immediate prerequisites.
for tag,path,script,needle in [
    ('BQ',BQ,'verify-bq.py','BQ_VERIFY=PASS'),
    ('BP',BP,'verify-bp.py','BP_VERIFY=PASS'),
]:
    cp=subprocess.run([str(path/script)],cwd=path,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{tag} failed\n{cp.stdout}\n{cp.stderr}')
    assert needle in cp.stdout,(tag,cp.stdout)

hdr=(HERE/'native-convergence.h').read_text()
src=(HERE/'native-convergence.c').read_text()

# BR public input contains request data only. BQ-closed runtime controls and all
# earlier tuning selectors must not be caller-selectable fields.
for name in (
    'intolerance_gate','small_delta_exemption','state_flag_short','state_flag_long',
    'pipeline_delay','base_speed','base_capping','drc_speed','capping_type',
    'tolerance_steps','minimum_step','drc_policy','stretch_capacity',
    'stretch_active_count','stretch_agg_type','stretch_direction_mode',
    'stretch_target_negative'):
    assert not any(line.strip().startswith(('uint32_t '+name,'float '+name,'int32_t '+name))
                   for line in hdr.splitlines()),name
assert 'struct e003i_front_preview_unlocked_input' in hdr
assert 'e003i_converge_front_preview_unlocked' in hdr
assert 'struct e003i_stretch_record' not in hdr
assert 'struct e003i_conv_input' not in hdr

# Source must bind the BQ normal-unlocked projection, while retaining BP's
# mechanically closed Windows tuning/profile constants.
for token in (
    'rt.intolerance_gate = 0','rt.small_delta_exemption = 0',
    'rt.state_flag_short = 0','rt.state_flag_long = 0',
    'rt.pipeline_delay = 3','0x3f4ccccdU','0x3ea8f5c3U','0x3e19999aU',
    'rt.capping_type = 2','rt.tolerance_steps = 2','0x3f000000U',
    'rt.drc_policy = 0','rt.stretch[0].offset = 0.0f',
    'rt.stretch[0].temp_weight = 1.0f'):
    assert token in src,token

cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math']
tmp=Path(tempfile.mkdtemp(prefix='e003i-br-'))
bpso=tmp/'bp.so'; brso=tmp/'br.so'
subprocess.run(cc+[str(BP/'native-convergence.c'),'-I',str(BP),'-lm','-o',str(bpso)],check=True)
subprocess.run(cc+[str(HERE/'native-convergence.c'),'-I',str(HERE),'-lm','-o',str(brso)],check=True)
bp=ctypes.CDLL(str(bpso)); br=ctypes.CDLL(str(brso))

class Hist(ctypes.Structure):
    _fields_=[('lanes',ctypes.c_uint64*N),('drc_gain',ctypes.c_float),('previous_delta',ctypes.c_float)]
class BPIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*N),('history1',Hist),('history2',Hist),('delayed_history',Hist),
              ('intolerance_gate',ctypes.c_uint32),('small_delta_exemption',ctypes.c_uint32),
              ('state_flag_short',ctypes.c_int32),('state_flag_long',ctypes.c_int32)]
class BRIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*N),('history1',Hist),('history2',Hist),('delayed_history',Hist)]
class Out(ctypes.Structure):
    _fields_=[('basic_safe_log',ctypes.c_double),('post_stretch_log',ctypes.c_double*N),('final_log',ctypes.c_double*N),
              ('linear',ctypes.c_uint64*N),('pred_gain',ctypes.c_float),('short_stretch',ctypes.c_float),('safe_stretch',ctypes.c_float),
              ('stretch_ratio',ctypes.c_float),('drc_ratio',ctypes.c_float),('basic_direction_ok',ctypes.c_uint32),('drc_branch',ctypes.c_uint32)]

bp.e003i_converge_front_preview.argtypes=[ctypes.POINTER(BPIn),ctypes.POINTER(Out)]
bp.e003i_converge_front_preview.restype=ctypes.c_int
br.e003i_converge_front_preview_unlocked.argtypes=[ctypes.POINTER(BRIn),ctypes.POINTER(Out)]
br.e003i_converge_front_preview_unlocked.restype=ctypes.c_int

POW_BASE=1.0299999713897705078125
def lin(logv): return max(1,int(math.pow(POW_BASE,float(logv))))
def fill_hist(h,logs,drc,delta):
    h.lanes[:]=[lin(x) for x in logs]
    h.drc_gain=drc; h.previous_delta=delta

def copy_to_bp(dst,src):
    dst.target_log[:]=src.target_log[:]
    dst.history1=src.history1; dst.history2=src.history2; dst.delayed_history=src.delayed_history
    dst.intolerance_gate=0; dst.small_delta_exemption=0
    dst.state_flag_short=0; dst.state_flag_long=0

# Fail-closed boundary is preserved.
o=Out(); assert br.e003i_converge_front_preview_unlocked(None,ctypes.byref(o))==-1
bad=BRIn(); bad.target_log[:]=(1.0,)*N
assert br.e003i_converge_front_preview_unlocked(ctypes.byref(bad),ctypes.byref(o))==-2

rng=random.Random(0xE0031C); cases=0; branch_counts={}
for k in range(1536):
    x=BRIn()
    h1s=rng.uniform(65.0,220.0)
    h2s=h1s+rng.uniform(-3.0,3.0)
    hds=h1s+rng.uniform(-5.0,5.0)
    h1=(h1s+rng.uniform(-8,2),h1s+rng.uniform(-3,4),h1s,
        h1s+rng.uniform(-6,3),h1s+rng.uniform(-6,3),h1s+rng.uniform(-6,3),h1s+rng.uniform(-6,3))
    h2=(h2s+rng.uniform(-8,2),h2s+rng.uniform(-3,4),h2s,
        h2s+rng.uniform(-6,3),h2s+rng.uniform(-6,3),h2s+rng.uniform(-6,3),h2s+rng.uniform(-6,3))
    hd=(hds+rng.uniform(-8,2),hds+rng.uniform(-3,4),hds,
        hds+rng.uniform(-6,3),hds+rng.uniform(-6,3),hds+rng.uniform(-6,3),hds+rng.uniform(-6,3))
    fill_hist(x.history1,h1,rng.choice([1.0,1.0,1.25,1.5,2.0]),rng.choice([-4.0,-2.0,-1.0,0.0,1.0,2.0,4.0]))
    fill_hist(x.history2,h2,rng.choice([1.0,1.25,1.5]),rng.choice([-2.0,0.0,2.0]))
    fill_hist(x.delayed_history,hd,1.0,0.0)
    ts=h1s+rng.uniform(-10.0,10.0)
    x.target_log[:]=(ts+rng.uniform(-9,0),ts+rng.uniform(-2,5),ts,
                     ts+rng.uniform(-5,2),ts+rng.uniform(-5,2),ts+rng.uniform(-5,2),ts+rng.uniform(-5,2))

    old=BPIn(); copy_to_bp(old,x)
    ob=Out(); orn=Out()
    rbp=bp.e003i_converge_front_preview(ctypes.byref(old),ctypes.byref(ob))
    rbr=br.e003i_converge_front_preview_unlocked(ctypes.byref(x),ctypes.byref(orn))
    assert rbp==0 and rbr==0,(k,rbp,rbr)
    assert ctypes.string_at(ctypes.byref(ob),ctypes.sizeof(ob)) == ctypes.string_at(ctypes.byref(orn),ctypes.sizeof(orn)),k
    assert orn.short_stretch==0.0 and orn.safe_stretch==0.0 and orn.pred_gain==1.0,k
    branch_counts[int(orn.drc_branch)]=branch_counts.get(int(orn.drc_branch),0)+1
    cases+=1

print('PROFILE=normal-streaming AEC-unlocked metering-lock-context-inactive')
print('PUBLIC_TUNING_INPUTS=0')
print('PUBLIC_RUNTIME_SCALAR_CONTROLS=0')
print('PUBLIC_REQUEST_STATE=target_log[7],history1,history2,delayed_history')
print(f'DIFFERENTIAL_CASES={cases}')
print('DRC_BRANCH_COUNTS='+json.dumps(branch_counts,sort_keys=True))
print('BP_ZERO_PROJECTION_MATCH=bit-exact')
print('BR_VERIFY=PASS')
