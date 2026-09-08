#!/usr/bin/env python3
from pathlib import Path
import ctypes, hashlib, importlib.util, json, struct, subprocess, sys, tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA

def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

def fbits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def fval(b): return struct.unpack('<f',struct.pack('<I',int(b)&0xffffffff))[0]

# Fresh semantic/arithmetic prerequisites.
fresh('bi-windows-aec-lux-history-coordinate','verify-bi.py','BI_VERIFY=PASS')
fresh('bj-native-aec-log103-coordinate','verify-bj.py','BJ_VERIFY=PASS')
fresh('bh-native-aec-request-state','verify-bh.py','BH_VERIFY=PASS')

# Build target-native state plus separately verified BJ primitive.
td=tempfile.TemporaryDirectory(prefix='e003i-bk-')
so=Path(td.name)/'libaecstate.so'
subprocess.run(['gcc','-shared','-fPIC','-O2','-fno-fast-math',
                str(HERE/'native-aec-state.c'),
                str(BASE/'bj-native-aec-log103-coordinate'/'native-log103.c'),
                '-I',str(HERE),'-I',str(BASE/'bj-native-aec-log103-coordinate'),
                '-lm','-o',str(so)],check=True)
lib=ctypes.CDLL(str(so))

LANES=7; HS=32; PS=8
class Hist(ctypes.Structure):
    _fields_=[('frame_id',ctypes.c_uint64),('lanes',ctypes.c_uint64*LANES),('valid',ctypes.c_uint8)]
class Pub(ctypes.Structure):
    _fields_=[('frame_id',ctypes.c_uint64),('lux',ctypes.c_float),('valid',ctypes.c_uint8)]
class State(ctypes.Structure):
    _fields_=[('lux_trigger',ctypes.c_float),('algorithm001_alpha',ctypes.c_float),('history',Hist*HS),('publication',Pub*PS)]
class Result(ctypes.Structure):
    _fields_=[('frame_id',ctypes.c_uint64),('lux_trigger_in',ctypes.c_float),('target_low',ctypes.c_float),
              ('measured_luma',ctypes.c_float),('frame_sa_safe_si',ctypes.c_uint64),
              ('history_reference_frame',ctypes.c_uint64),('history_reference_s1_exposure',ctypes.c_uint64),
              ('history_reference_log103',ctypes.c_float),('next_lux_trigger',ctypes.c_float),
              ('external_lux_valid',ctypes.c_uint8),('external_lux',ctypes.c_float),
              ('previous_exposure_valid',ctypes.c_uint8),('previous_exposure_frame',ctypes.c_uint64),
              ('previous_exposure_lanes',ctypes.c_uint64*LANES)]
lib.e003i_aec_state_init.argtypes=[ctypes.POINTER(State),ctypes.c_float,ctypes.c_float]
lib.e003i_aec_state_commit_exposure.argtypes=[ctypes.POINTER(State),ctypes.c_uint64,ctypes.POINTER(ctypes.c_uint64)]
lib.e003i_aec_state_process.argtypes=[ctypes.POINTER(State),ctypes.c_uint64,ctypes.c_float,ctypes.c_uint64,ctypes.POINTER(Result)]
lib.e003i_aec_state_process.restype=ctypes.c_int
lib.e003i_framesa_target_low.argtypes=[ctypes.c_float]; lib.e003i_framesa_target_low.restype=ctypes.c_float
lib.e003i_algorithm001_lux.argtypes=[ctypes.c_float,ctypes.c_float,ctypes.c_float,ctypes.c_float]; lib.e003i_algorithm001_lux.restype=ctypes.c_float

# Exact BG target curve including gap interpolation.
for x,y in [(0,55),(140,55),(150,52.5),(160,50),(285,48),(300,46),(365,43),(370,40),(440,40),(480,35),(500,30),(1200,30)]:
    got=lib.e003i_framesa_target_low(ctypes.c_float(x)); assert fbits(got)==fbits(y),(x,got,y)

# AB eight live Algorithm001 cases remain bit exact when called with their
# captured F-3 coordinate; alpha is pinned zero on those captures.
ab=json.loads((BASE/'ab-clean-lux-reconstruction'/'RESULT.json').read_text())['lux_algorithm001']['ab8_cases']
for row in ab:
    got=lib.e003i_algorithm001_lux(fval(int(row['measured_bits'],16)),
                                   fval(int(row['baseline_bits'],16)),0.0,0.0)
    assert fbits(got)==int(row['live_output_bits'],16),(row['raw'],hex(fbits(got)),row['live_output_bits'])

# State-level AB2/BI closure: F=10 consumes F-3=7 S1 exposure 33,312,451,
# derives exact coord 0x4365acdd internally, then reproduces AB R1 Lux.
s=State(); lib.e003i_aec_state_init(ctypes.byref(s),ctypes.c_float(150.0),ctypes.c_float(0.0))
def commit(f,vals):
    a=(ctypes.c_uint64*LANES)(*vals); assert lib.e003i_aec_state_commit_exposure(ctypes.byref(s),f,a)==0
commit(7,[100,200,300,33312451,500,600,700])
commit(9,[101,102,103,104,105,106,107])
r10=Result(); rc=lib.e003i_aec_state_process(ctypes.byref(s),10,fval(0x3f1e9ed8),1000000,ctypes.byref(r10)); assert rc==0
assert r10.history_reference_frame==7 and r10.history_reference_s1_exposure==33312451
assert fbits(r10.history_reference_log103)==0x4365acdd
assert fbits(r10.next_lux_trigger)==0x43bd1baa
assert fbits(r10.lux_trigger_in)==fbits(150.0) and fbits(r10.target_low)==fbits(52.5)
assert r10.previous_exposure_valid and r10.previous_exposure_frame==9 and list(r10.previous_exposure_lanes)==[101,102,103,104,105,106,107]
assert not r10.external_lux_valid

# Subsequent requests use the newly written internal Lux; external publication
# of F10's Algorithm001 result appears exactly at F12.
commit(8,[1,1,1,33312451,1,1,1]); commit(10,[1]*7)
r11=Result(); assert lib.e003i_aec_state_process(ctypes.byref(s),11,fval(0x3f1fc97f),1000000,ctypes.byref(r11))==0
assert fbits(r11.lux_trigger_in)==0x43bd1baa and not r11.external_lux_valid
commit(11,[1]*7)
r12=Result(); assert lib.e003i_aec_state_process(ctypes.byref(s),12,fval(0x3f1fbfcb),1000000,ctypes.byref(r12))==0
assert r12.external_lux_valid and fbits(r12.external_lux)==0x43bd1baa

# Missing F-3 history must fail closed.
z=State(); lib.e003i_aec_state_init(ctypes.byref(z),50.0,0.0); rz=Result()
assert lib.e003i_aec_state_process(ctypes.byref(z),100,1.0,1000,ctypes.byref(rz))==-2

print('DLL_SHA256='+DLL_SHA)
print('F3_HISTORY_INPUT=S1 linear exposure -> BJ log103 coordinate (no scalar seam)')
print('AB2_STATE_COORD=0x4365acdd')
print('AB2_STATE_LUX=0x43bd1baa')
print('ENTRY_LUX_TARGET_ORDER=PASS')
print('EXTERNAL_LUX_PLUS2=PASS')
print('F1_EXPOSURE_HISTORY_SEPARATE=PASS')
print('MISSING_F3_FAIL_CLOSED=PASS')
print('BK_VERIFY=PASS')
