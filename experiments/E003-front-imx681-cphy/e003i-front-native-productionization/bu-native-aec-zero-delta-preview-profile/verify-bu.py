#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, json, math, random, re, subprocess, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
BT=BASE/'bt-native-aec-minimal-history-preview-profile'
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
N=7; T=3

def fresh(path, script, marker):
    cp=subprocess.run([str(path/script)],cwd=path,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{script} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,cp.stdout

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)

def req(text,*needles):
    for n in needles: assert n in text,n

def addrs_matching(text, pattern):
    out=[]
    rx=re.compile(pattern)
    for line in text.splitlines():
        if rx.search(line):
            m=re.match(r'\s*([0-9a-f]+):',line)
            if m: out.append(int(m.group(1),16))
    return out

fresh(BT,'verify-bt.py','BT_VERIFY=PASS')
assert DLL.is_file()
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA

# Windows recurrence: +0xdc is initialized to +0.0f or reloaded unchanged from F-1.
init=dis(0x1803b46f0,0x1803b47c0)
req(init,
    '1803b471c:', 'str\twzr, [x22, #0xdc]',
    '1803b47a4:', 'ldr\ts16, [x24, #0x17c]',
    '1803b47a8:', 'str\ts16, [x22, #0xdc]')
run=dis(0x1803b38c0,0x1803b6400)
dc_lines=[l for l in run.splitlines() if '[x22, #0xdc]' in l]
assert len(dc_lines)==2,dc_lines
assert addrs_matching(run,r'\[x22, #0xdc\]')==[0x1803b471c,0x1803b47a8]
assert not any(re.search(r'\bldr\w*\b',l) for l in dc_lines),dc_lines
# No helper receives the convergence base before final PopulateOutput.
base_x0=addrs_matching(run,r'\bmov\s+x0, x22\b')
assert base_x0==[0x1803b63ec],base_x0
tail=dis(0x1803b63e8,0x1803b63f8)
req(tail,'1803b63ec:', 'mov\tx0, x22', '1803b63f0:', 'bl\t0x1803cdf50')

pop=dis(0x1803cdf50,0x1803ce070)
req(pop,
    '1803ce048:', 'ldr\ts16, [x19, #0xdc]',
    '1803ce04c:', 'str\ts16, [x20, #0x80]')
eof=dis(0x1803bd3e0,0x1803bd460)
req(eof,
    '1803bd3ec:', 'mov\tx9, #0x10a8',
    '1803bd3f0:', 'add\tx21, x19, x9',
    '1803bd44c:', 'ldr\ts16, [x23, #0x80]',
    '1803bd454:', 'str\ts16, [x19, #0x1224]')
assert 0x10a8+0x17c==0x1224

hdr=(HERE/'native-convergence.h').read_text(); src=(HERE/'native-convergence.c').read_text()
assert 'float previous_delta;' not in hdr
assert 'e003i_front_preview_unlocked_zero_delta_history_input' in hdr
assert 'e003i_converge_front_preview_unlocked_zero_delta_history' in hdr
assert 'rt.history1.previous_delta = 0.0f;' in src
assert 'rt.history1.previous_delta = in->history1.previous_delta;' not in src

cc=['cc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-fno-fast-math']
tmp=Path(tempfile.mkdtemp(prefix='e003i-bu-')); btso=tmp/'bt.so'; buso=tmp/'bu.so'
subprocess.run(cc+[str(BT/'native-convergence.c'),'-I',str(BT),'-lm','-o',str(btso)],check=True)
subprocess.run(cc+[str(HERE/'native-convergence.c'),'-I',str(HERE),'-lm','-o',str(buso)],check=True)
bt=ctypes.CDLL(str(btso)); bu=ctypes.CDLL(str(buso))

class BTH1(ctypes.Structure):
    _fields_=[('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('drc_gain',ctypes.c_float),('previous_delta',ctypes.c_float)]
class BUH1(ctypes.Structure):
    _fields_=[('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('drc_gain',ctypes.c_float)]
class H2(ctypes.Structure):
    _fields_=[('short_exposure',ctypes.c_uint64),('long_exposure',ctypes.c_uint64),('safe_exposure',ctypes.c_uint64),('drc_gain',ctypes.c_float)]
class H3(ctypes.Structure): _fields_=[('safe_exposure',ctypes.c_uint64)]
class BTIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*T),('history1',BTH1),('history2',H2),('delayed_history',H3)]
class BUIn(ctypes.Structure):
    _fields_=[('target_log',ctypes.c_double*T),('history1',BUH1),('history2',H2),('delayed_history',H3)]
class Out(ctypes.Structure):
    _fields_=[('basic_safe_log',ctypes.c_double),('post_stretch_log',ctypes.c_double*N),('final_log',ctypes.c_double*N),
              ('linear',ctypes.c_uint64*N),('pred_gain',ctypes.c_float),('short_stretch',ctypes.c_float),('safe_stretch',ctypes.c_float),
              ('stretch_ratio',ctypes.c_float),('drc_ratio',ctypes.c_float),('basic_direction_ok',ctypes.c_uint32),('drc_branch',ctypes.c_uint32)]
bt.e003i_converge_front_preview_unlocked_minimal_history.argtypes=[ctypes.POINTER(BTIn),ctypes.POINTER(Out)]
bt.e003i_converge_front_preview_unlocked_minimal_history.restype=ctypes.c_int
bu.e003i_converge_front_preview_unlocked_zero_delta_history.argtypes=[ctypes.POINTER(BUIn),ctypes.POINTER(Out)]
bu.e003i_converge_front_preview_unlocked_zero_delta_history.restype=ctypes.c_int

POW_BASE=1.0299999713897705078125
def lin(x): return max(1,int(math.pow(POW_BASE,float(x))))
def obytes(o): return ctypes.string_at(ctypes.byref(o),ctypes.sizeof(o))

o=Out(); assert bu.e003i_converge_front_preview_unlocked_zero_delta_history(None,ctypes.byref(o))==-1
bad=BUIn(); bad.target_log[:]=(1.0,2.0,3.0)
assert bu.e003i_converge_front_preview_unlocked_zero_delta_history(ctypes.byref(bad),ctypes.byref(o))==-2

rng=random.Random(0xE0031F); cases=0; branches={}
for k in range(2048):
    h1s=rng.uniform(65,220); h2s=h1s+rng.uniform(-3,3); h3s=h1s+rng.uniform(-5,5)
    h1=(lin(h1s+rng.uniform(-8,2)),lin(h1s+rng.uniform(-3,4)),lin(h1s),rng.choice([1.0,1.0,1.25,1.5,2.0]))
    h2=(lin(h2s+rng.uniform(-8,2)),lin(h2s+rng.uniform(-3,4)),lin(h2s),rng.choice([1.0,1.25,1.5]))
    h3=lin(h3s)
    ts=h1s+rng.uniform(-10,10); targets=(ts+rng.uniform(-9,0),ts+rng.uniform(-2,5),ts)

    a=BTIn(); b=BUIn(); a.target_log[:]=targets; b.target_log[:]=targets
    a.history1.short_exposure,b.history1.short_exposure=h1[0],h1[0]
    a.history1.long_exposure,b.history1.long_exposure=h1[1],h1[1]
    a.history1.safe_exposure,b.history1.safe_exposure=h1[2],h1[2]
    a.history1.drc_gain,b.history1.drc_gain=h1[3],h1[3]
    a.history1.previous_delta=0.0
    a.history2.short_exposure=b.history2.short_exposure=h2[0]
    a.history2.long_exposure=b.history2.long_exposure=h2[1]
    a.history2.safe_exposure=b.history2.safe_exposure=h2[2]
    a.history2.drc_gain=b.history2.drc_gain=h2[3]
    a.delayed_history.safe_exposure=b.delayed_history.safe_exposure=h3

    oa=Out(); ob=Out()
    ra=bt.e003i_converge_front_preview_unlocked_minimal_history(ctypes.byref(a),ctypes.byref(oa))
    rb=bu.e003i_converge_front_preview_unlocked_zero_delta_history(ctypes.byref(b),ctypes.byref(ob))
    assert ra==rb==0,(k,ra,rb)
    assert obytes(oa)==obytes(ob),('bu-zero-delta-projection',k)
    branches[int(ob.drc_branch)]=branches.get(int(ob.drc_branch),0)+1; cases+=1

print('DLL_SHA256='+DLL_SHA)
print('PROFILE=normal-streaming AEC-unlocked single-exposure')
print('WINDOWS_PREVIOUS_DELTA_BASE=+0.0f')
print('WINDOWS_PREVIOUS_DELTA_RECURRENCE=F<-F-1 unchanged')
print('PUBLIC_HISTORY_F1=Short,Long,Safe,drc_gain')
print('PUBLIC_HISTORY_F2=Short,Long,Safe,drc_gain')
print('PUBLIC_HISTORY_F3=Safe')
print(f'ZERO_DELTA_PROJECTION_CASES={cases}')
print('DRC_BRANCH_COUNTS='+json.dumps(branches,sort_keys=True))
print('BT_ZERO_DELTA_PROJECTION_MATCH=bit-exact')
print('BU_VERIFY=PASS')
