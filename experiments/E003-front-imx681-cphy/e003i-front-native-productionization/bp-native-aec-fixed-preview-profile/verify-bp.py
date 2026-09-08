#!/usr/bin/env python3
from pathlib import Path
import ctypes, json, math, random, struct, subprocess, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
BL=BASE/'bl-native-aec-convergence-kernel'
BM=BASE/'bm-windows-aec-tuning-selection'
BN=BASE/'bn-windows-aec-convbase-default-controls'
BO=BASE/'bo-windows-aec-convergence-global-controls'
N=7; MAX=16

# Re-establish the three proofs that define the fixed profile.
for tag,path,needle in [
    ('BM',BM,'BM_VERIFY=PASS'),
    ('BN',BN,'BN_VERIFY=PASS'),
    ('BO',BO,'BO_VERIFY=PASS'),
]:
    out=subprocess.check_output([str(path/('verify-'+tag.lower()+'.py'))],cwd=path,text=True)
    assert needle in out,(tag,out)

hdr=(HERE/'native-convergence.h').read_text()
src=(HERE/'native-convergence.c').read_text()
# Removed knobs must not be public fields or public types.
for name in ('pipeline_delay','base_speed','base_capping','drc_speed','capping_type',
             'tolerance_steps','minimum_step','drc_policy','stretch_capacity',
             'stretch_active_count','stretch_agg_type','stretch_direction_mode',
             'stretch_target_negative'):
    assert not any(line.strip().startswith(('uint32_t '+name,'float '+name,'int32_t '+name))
                   for line in hdr.splitlines()), name
assert 'struct e003i_stretch_record' not in hdr
assert 'struct e003i_conv_input' not in hdr
assert 'e003i_converge_single_request' not in hdr
assert 'e003i_converge_front_preview' in hdr

# Source binds exact proven float32/control constants and BM identity leaf.
for token in ('0x3f4ccccdU','0x3ea8f5c3U','0x3e19999aU','0x3f000000U',
              'rt.pipeline_delay = 3','rt.capping_type = 2','rt.tolerance_steps = 2',
              'rt.drc_policy = 0','rt.stretch[0].weight = 1.0f',
              'rt.stretch[0].offset = 0.0f','rt.stretch[0].comp = 1.0f',
              'rt.stretch[0].temp_weight = 1.0f'):
    assert token in src,token

cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math']
tmp=Path(tempfile.mkdtemp(prefix='e003i-bp-'))
blso=tmp/'bl.so'; bpso=tmp/'bp.so'
subprocess.run(cc+[str(BL/'native-convergence.c'),'-I',str(BL),'-lm','-o',str(blso)],check=True)
subprocess.run(cc+[str(HERE/'native-convergence.c'),'-I',str(HERE),'-lm','-o',str(bpso)],check=True)
bl=ctypes.CDLL(str(blso)); bp=ctypes.CDLL(str(bpso))

class Hist(ctypes.Structure):
    _fields_=[('lanes',ctypes.c_uint64*N),('drc_gain',ctypes.c_float),('previous_delta',ctypes.c_float)]
class Rec(ctypes.Structure):
    _fields_=[('weight',ctypes.c_float),('offset',ctypes.c_float),('comp',ctypes.c_float),('temp_weight',ctypes.c_float),('negative',ctypes.c_uint32)]
class BLIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*N),('history1',Hist),('history2',Hist),('delayed_history',Hist),
              ('pipeline_delay',ctypes.c_uint32),('base_speed',ctypes.c_float),('base_capping',ctypes.c_float),('drc_speed',ctypes.c_float),
              ('capping_type',ctypes.c_int32),('tolerance_steps',ctypes.c_int32),('minimum_step',ctypes.c_float),
              ('intolerance_gate',ctypes.c_uint32),('small_delta_exemption',ctypes.c_uint32),('stretch',Rec*MAX),
              ('stretch_capacity',ctypes.c_uint32),('stretch_active_count',ctypes.c_uint32),('stretch_agg_type',ctypes.c_uint32),
              ('stretch_direction_mode',ctypes.c_uint32),('stretch_target_negative',ctypes.c_uint32),
              ('state_flag_short',ctypes.c_int32),('state_flag_long',ctypes.c_int32),('drc_policy',ctypes.c_int32)]
class BPIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*N),('history1',Hist),('history2',Hist),('delayed_history',Hist),
              ('intolerance_gate',ctypes.c_uint32),('small_delta_exemption',ctypes.c_uint32),
              ('state_flag_short',ctypes.c_int32),('state_flag_long',ctypes.c_int32)]
class Out(ctypes.Structure):
    _fields_=[('basic_safe_log',ctypes.c_double),('post_stretch_log',ctypes.c_double*N),('final_log',ctypes.c_double*N),
              ('linear',ctypes.c_uint64*N),('pred_gain',ctypes.c_float),('short_stretch',ctypes.c_float),('safe_stretch',ctypes.c_float),
              ('stretch_ratio',ctypes.c_float),('drc_ratio',ctypes.c_float),('basic_direction_ok',ctypes.c_uint32),('drc_branch',ctypes.c_uint32)]

bl.e003i_converge_single_request.argtypes=[ctypes.POINTER(BLIn),ctypes.POINTER(Out)]
bl.e003i_converge_single_request.restype=ctypes.c_int
bp.e003i_converge_front_preview.argtypes=[ctypes.POINTER(BPIn),ctypes.POINTER(Out)]
bp.e003i_converge_front_preview.restype=ctypes.c_int

POW_BASE=1.0299999713897705078125
def f32bits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
def lin(logv): return max(1,int(math.pow(POW_BASE,float(logv))))
def fill_hist(h,logs,drc,delta):
    h.lanes[:]=[lin(x) for x in logs]
    h.drc_gain=drc; h.previous_delta=delta

def bind_fixed(dst,src):
    dst.target_log[:]=src.target_log[:]
    dst.history1=src.history1; dst.history2=src.history2; dst.delayed_history=src.delayed_history
    dst.pipeline_delay=3
    dst.base_speed=f32bits(0x3f4ccccd); dst.base_capping=f32bits(0x3ea8f5c3); dst.drc_speed=f32bits(0x3e19999a)
    dst.capping_type=2; dst.tolerance_steps=2; dst.minimum_step=f32bits(0x3f000000)
    dst.intolerance_gate=src.intolerance_gate; dst.small_delta_exemption=src.small_delta_exemption
    dst.stretch_capacity=1; dst.stretch_active_count=1; dst.stretch_agg_type=0; dst.stretch_direction_mode=0; dst.stretch_target_negative=0
    dst.stretch[0]=Rec(1.0,0.0,1.0,1.0,0)
    dst.state_flag_short=src.state_flag_short; dst.state_flag_long=src.state_flag_long; dst.drc_policy=0

# Null/fail-closed boundary.
o=Out(); assert bp.e003i_converge_front_preview(None,ctypes.byref(o))==-1
bad=BPIn(); bad.target_log[:]=(1,)*N
assert bp.e003i_converge_front_preview(ctypes.byref(bad),ctypes.byref(o))==-2

rng=random.Random(0xE0031B); cases=0; branch_counts={}
for k in range(1024):
    x=BPIn()
    h1s=rng.uniform(65.0,220.0)
    h2s=h1s+rng.uniform(-3.0,3.0)
    hds=h1s+rng.uniform(-5.0,5.0)
    # Preserve realistic lane ordering freedom without forcing equality.
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
    x.intolerance_gate=(k>>0)&1
    x.small_delta_exemption=(k>>1)&1
    x.state_flag_short=(k>>2)&1
    x.state_flag_long=(k>>3)&1

    g=BLIn(); bind_fixed(g,x)
    ob=Out(); op=Out()
    rb=bl.e003i_converge_single_request(ctypes.byref(g),ctypes.byref(ob))
    rp=bp.e003i_converge_front_preview(ctypes.byref(x),ctypes.byref(op))
    assert rb==0 and rp==0,(k,rb,rp)
    # BP is the same native kernel with only profile materialization moved inside.
    assert ctypes.string_at(ctypes.byref(ob),ctypes.sizeof(ob)) == ctypes.string_at(ctypes.byref(op),ctypes.sizeof(op)),k
    # BM identity must survive arbitrary previous_delta.
    assert op.short_stretch==0.0 and op.safe_stretch==0.0 and op.pred_gain==1.0 and op.stretch_ratio==1.0,k
    branch_counts[int(op.drc_branch)]=branch_counts.get(int(op.drc_branch),0)+1
    cases+=1

print('PROFILE=PipelineDelay3 FastConv(0.8,0.33,0.15) capping2 tolerance2 minStep0.5 DisableStretch DRCpolicy0')
print('PUBLIC_TUNING_INPUTS=0')
print('UNRESOLVED_RUNTIME_CONTROLS=intolerance_gate,small_delta_exemption,state_flag_short,state_flag_long')
print(f'DIFFERENTIAL_CASES={cases}')
print('DRC_BRANCH_COUNTS='+json.dumps(branch_counts,sort_keys=True))
print('DISABLE_STRETCH_IDENTITY=bit-exact across arbitrary retained delta')
print('BP_VERIFY=PASS')
