#!/usr/bin/env python3
from __future__ import annotations
import ctypes
import hashlib
import importlib.util
import json
import math
import random
import re
import struct
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PROJ = REPO.parent.parent
BASE = REPO / 'experiments/E003-front-imx681-cphy/e003i-front-native-productionization'
CP = BASE / 'cp-native-aec-self-contained-cold-init'
AJ = BASE / 'aj-imx681-exposure-controls'
AP = BASE / 'ap-bounded-imx681-control-runtime'
CH = BASE / 'ch-native-aec-t681-preview-arbitration'
DLL = PROJ / '00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'
BLOB = PROJ / '00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin'

DLL_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
BLOB_SHA = 'f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c'
ORACLE_HASHES = {
 'E003I-CQ2-cdb.cmd':'4ca20484db282cef8177ffbe3c54692844defd038980850a1c4b12b3f545e5cc',
 'E003I-CQ2-cdb.log':'a07fe8641d2cb5e6914002eac5f5a1dea5b96df6054cc44a2db03136574737b1',
 'E003I-CQ2-holder.log':'36375720c66ca94295675922e604db510d56006286b7f5633ac767efa8f8a624',
 'E003I-CQ2-Holder.ps1':'0f0f02f65461f626cbc30966bd9dada4b11837094373abc3bef956d2108a6f06',
 'E003I-CQ3-cdb.cmd':'0ad8c63e6377ffb1e471aa718ac2fb23d97b394279fb68159ab31d1066b407a9',
 'E003I-CQ3-cdb.log':'56bb327a7369b9620840d967b831d32f40a10abb363f8368cb03b7924138a261',
 'E003I-CQ3-holder.log':'4d988eb58f16332c9bf4d9956f9b83766bff99d170f7b92fcd603655a25cc651',
 'E003I-CQ3-Holder.ps1':'60f82d75f339ae30a7c7c0a923311ece53cbc98e62913d90ee0d4f0566076166',
 'E003I-CQ4-cdb.cmd':'6aeaababd936b019689be753945cafb7f322e487f9739f4c3ea804504568ce9a',
 'E003I-CQ4-cdb.log':'c80dadb3afb50cb034fb80727afb6840c754fada40bd121c77eaa00aa30ff43a',
 'E003I-CQ4-holder.log':'b81d9a7916bcb0111bdf17c81595abc638af20706010a2fff0946db4575a30bb',
 'E003I-CQ4-Holder.ps1':'dde6fa26416287c22fb0004dac2a8f06b5e1029e4af9c539fc18b2fe0b8f5a6f',
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run_parent(path: Path, script: str, marker: str) -> str:
    cp = subprocess.run(['python3', str(path/script)], cwd=path, text=True,
                        capture_output=True)
    if cp.returncode != 0:
        raise AssertionError(f'{path.name}/{script} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout, (path, marker, cp.stdout[-2000:])
    return cp.stdout

def dis(a: int, b: int) -> str:
    cp = subprocess.run(['llvm-objdump','-d',f'--start-address={a:#x}',
                         f'--stop-address={b:#x}',str(DLL)], text=True,
                        capture_output=True, check=True)
    return cp.stdout

def f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]

def fbits(x: float) -> int:
    return struct.unpack('<I', struct.pack('<f', f32(x)))[0]

def half_away_positive(x: float) -> int:
    assert x >= 0.0 and math.isfinite(x)
    return math.floor(x + 0.5)

# Immutable artifact pins.
assert DLL.is_file() and sha(DLL) == DLL_SHA
assert BLOB.is_file() and sha(BLOB) == BLOB_SHA
assert subprocess.run(['git','merge-base','--is-ancestor','84a8ed7','HEAD'], cwd=REPO).returncode == 0

# Preserve the actual bounded Windows oracle runs byte-for-byte.
for name, expected in ORACLE_HASHES.items():
    p = HERE/'windows-oracle'/name
    assert p.is_file(), p
    assert sha(p) == expected, (name, sha(p), expected)
for tag in ('CQ2','CQ3','CQ4'):
    holder = (HERE/'windows-oracle'/f'E003I-{tag}-holder.log').read_bytes().decode('utf-16')
    assert 'START_STATUS=Success' in holder and 'STOP_PASS' in holder and 'CP_HOLDER_END' in holder

cq2 = (HERE/'windows-oracle/E003I-CQ2-cdb.log').read_text(errors='replace')
cq3 = (HERE/'windows-oracle/E003I-CQ3-cdb.log').read_text(errors='replace')
cq4 = (HERE/'windows-oracle/E003I-CQ4-cdb.log').read_text(errors='replace')
assert re.search(r'CQ2_HIT.*?w27=00000008.*?00000008.*?Detached', cq2, re.S)
assert re.search(r'CQ3_HIT.*?w24=00000de2.*?w27=00000008.*?PAIR.*?00000de0 00000de2.*?POLICY.*?00000008.*?EXTRA.*?00000000.*?Detached', cq3, re.S)
assert re.search(r'CQ4_HIT.*?FINAL_PAIR.*?00000de0 00000de8.*?GAIN_TIME_RAW.*?3f800000 00000000 01fc4ec4 00000000.*?Detached', cq4, re.S)

# Parent closures: self-contained AEC and exact IMX681 gain/register callback.
cp_out = run_parent(CP, 'verify-cp.py', 'CP_VERIFY=PASS')
ch_out = run_parent(CH, 'verify-ch.py', 'CH_VERIFY=PASS')
aj_out = run_parent(AJ, 'prove-aj.py', 'AJ_PROOF=PASS')
assert 'PUBLIC_STARTUP_ARGS=none' in cp_out and 'REQUEST_CASES=2304' in cp_out
assert 'PREVIEW_LIMITS=minGain1,minTime37516,maxGain92,maxTime66666664' in ch_out
assert 'AJ_WINDOWS_DYNAMIC_BYTES=20000/20000' in aj_out

# AP retained live hardware evidence, without touching root-owned capture binaries.
ap_result = json.loads((AP/'RESULT.json').read_text())
needle = 'AM request controls: FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0'
assert ap_result['status'] == 'PASS_LIVE_CONTROLS_AND_PAIRED_AUDIT'
assert ap_result['control_transaction'] == needle and ap_result['golden_return'] == 'PASS'
assert needle in (AP/'DMESG.txt').read_text(errors='replace')
assert needle in (AP/'runtime-output/CONTROL-TRANSACTION.txt').read_text(errors='replace')

# Static anchors: exact rounding, timing, SensorNode policy and count-1 lane collapse.
round_asm = dis(0x1800014b0, 0x1800014d0)
assert 'frinta\td0, d0' in round_asm
line_asm = dis(0x18071a208, 0x18071a310)
for s in ('mul\tw8, w9, w8','fcvtzu\tx8, d16','fdiv\td8, d16, d18'):
    assert s in line_asm, s
sensor_asm = dis(0x1803591f8, 0x1803592a0)
for s in ('ucvtf\td9, x8','fdiv\td8, d9, d0','str\tw0, [x20, #0x10]'):
    assert s in sensor_asm, s
policy_asm = dis(0x180359830, 0x1803598bc)
for s in ('ldr\tw8, [x19, x22]','cmp\tw8, #0x8','add\tw24, w9, w8','str\tw24, [x20, #0x14]'):
    assert s in policy_asm, s
bc_asm = dis(0x1803d1410, 0x1803d17e8)
for s in ('ldr\td20, [x19, #0xa0]','str\td20, [x19, #0x100]','str\td1, [x19, #0xb8]'):
    assert s in bc_asm, s

# Load AJ's already-proven reference implementation.
spec = importlib.util.spec_from_file_location('aj_oracle', AJ/'windows-oracle/oracle.py')
aj = importlib.util.module_from_spec(spec); spec.loader.exec_module(aj)

class T681(ctypes.Structure):
    _fields_ = [('gain',ctypes.c_float),('exposure_time_ns',ctypes.c_uint64),
                ('correction',ctypes.c_float),('retained_exposure',ctypes.c_uint64),
                ('upper_knee',ctypes.c_uint32)]
class Controls(ctypes.Structure):
    _fields_ = [('line_count_before_even',ctypes.c_uint32),
                ('frame_length_lines',ctypes.c_uint32),('vertical_blanking',ctypes.c_uint32),
                ('exposure_lines',ctypes.c_uint32),('analogue_gain_code',ctypes.c_uint32),
                ('digital_gain_code',ctypes.c_uint32),('isp_gain',ctypes.c_float)]

with tempfile.TemporaryDirectory(prefix='e003i-cq-') as td:
    so = Path(td)/'libcq.so'
    cmd = ['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fno-fast-math',
           '-ffp-contract=off','-shared','-fPIC',f'-I{CH}',str(HERE/'native-imx681-control.c'),str(CH/'native-t681.c'),
           '-lm','-o',str(so)]
    subprocess.run(cmd, check=True)
    lib = ctypes.CDLL(str(so))
    lib.e003i_imx681_controls_from_t681.argtypes = [ctypes.POINTER(T681),ctypes.POINTER(Controls)]
    lib.e003i_imx681_controls_from_t681.restype = ctypes.c_int
    lib.e003i_t681_preview_arbitrate.argtypes = [ctypes.c_uint64,ctypes.POINTER(T681)]
    lib.e003i_t681_preview_arbitrate.restype = ctypes.c_int

    # Fail-closed API boundaries.
    o=Controls(); assert lib.e003i_imx681_controls_from_t681(None,ctypes.byref(o)) == -1
    good=T681(1.0,37516,1.0,0,0)
    assert lib.e003i_imx681_controls_from_t681(ctypes.byref(good),None) == -1
    for g,t,rc in [(0.5,37516,-2),(93.0,37516,-2),(1.0,37515,-3),(1.0,66666665,-3)]:
        x=T681(f32(g),t,1.0,0,0); assert lib.e003i_imx681_controls_from_t681(ctypes.byref(x),ctypes.byref(o)) == rc

    line_len=6752; default_fll=3554; fps=30.0; height=2160
    pixels=(line_len*default_fll)&0xffffffff
    vt=int(float(pixels)*fps)
    line_ns=float(line_len)*1000000000.0/float(vt)
    assert vt == 719898240
    assert struct.unpack('<Q',struct.pack('<d',line_ns))[0] == 0x40c2518d3ad36374

    def reference(gain: float, time_ns: int):
        raw=max(4,half_away_positive(float(time_ns)/line_ns))
        fll=default_fll if raw <= 3546 else raw+8
        exposure=raw & ~1
        exp=aj.calculate_exposure(f32(gain), raw, False)
        return raw,fll,fll-height,exposure,exp['analog_reg'],exp['digital_reg'],exp['isp_gain_bits']
    def native(gain: float, time_ns: int):
        x=T681(f32(gain),time_ns,1.0,0,0); y=Controls()
        rc=lib.e003i_imx681_controls_from_t681(ctypes.byref(x),ctypes.byref(y)); assert rc==0,(gain,time_ns,rc)
        return (int(y.line_count_before_even),int(y.frame_length_lines),int(y.vertical_blanking),
                int(y.exposure_lines),int(y.analogue_gain_code),int(y.digital_gain_code),fbits(y.isp_gain))

    # Deterministic boundaries plus live/oracle-correlated values.
    fixed=[(1.0,37516),(1.0,33312452),(1.0,33333332),(16.0,33333332),
           (32.0,33333332),(92.0,33333332),(1.0,66666664),(67.0,66666664),
           (92.0,66666664),(300.0/4.0,1000000)]
    # Exact integer-ns neighborhoods around every line transition in a useful range.
    for k in (4,5,6,100,1000,3545,3546,3547,3551,3552,3553,3554,7106,7107,7108):
        center=(k+0.5)*line_ns
        n=int(math.floor(center))
        for dt in (-2,-1,0,1,2):
            t=n+dt
            if 37516 <= t <= 66666664: fixed.append((1.0,t))
    aq_gain=struct.unpack('<f',struct.pack('<I',0x40e7b95b))[0]
    fixed.append((aq_gain,33333332))
    for g,t in fixed:
        a=native(g,t); b=reference(g,t); assert a==b,(g,t,a,b)

    # Live CQ4 sample must reproduce the finalized SensorNode pair exactly.
    live=native(1.0,33312452)
    assert live[0] == 3552 and live[1] == 3560 and live[2] == 1400 and live[3] == 3552, live
    maxv=native(1.0,33333332)
    assert maxv[0] == 3554 and maxv[1] == 3562 and maxv[2] == 1402 and maxv[3] == 3554, maxv
    max_time=native(1.0,66666664)
    assert max_time[0] == 7108 and max_time[1] == 7116 and max_time[2] == 4956 and max_time[3] == 7108, max_time

    rng=random.Random(0xE0031C0)
    random_cases=65536
    for i in range(random_cases):
        # Generate an actual float32 gain, including dense neighborhoods of 16x.
        if i % 16 == 0:
            g=f32(16.0 + rng.uniform(-0.02,0.02))
        else:
            g=f32(rng.uniform(1.0,92.0))
        t=rng.randrange(37516,66666665)
        a=native(g,t); b=reference(g,t)
        assert a==b,(i,g,t,a,b)

    # Exercise the real CH->CQ ABI seam with actual T681 results.
    rng2=random.Random(0x681C0DE)
    seam_cases=16384
    for i in range(seam_cases):
        target=rng2.randrange(37516,6133333273)
        tr=T681(); rc=lib.e003i_t681_preview_arbitrate(target,ctypes.byref(tr))
        assert rc==0,(i,target,rc)
        got=Controls(); rc=lib.e003i_imx681_controls_from_t681(ctypes.byref(tr),ctypes.byref(got))
        assert rc==0,(i,target,rc)
        a=(int(got.line_count_before_even),int(got.frame_length_lines),int(got.vertical_blanking),
           int(got.exposure_lines),int(got.analogue_gain_code),int(got.digital_gain_code),fbits(got.isp_gain))
        b=reference(float(tr.gain),int(tr.exposure_time_ns))
        assert a==b,(i,target,float(tr.gain),int(tr.exposure_time_ns),a,b)

print(f'DLL_SHA256={DLL_SHA}')
print(f'SENSOR_BLOB_SHA256={BLOB_SHA}')
print('WINDOWS_ORACLE_RUNS=CQ2,CQ3,CQ4 hashes+clean-holder-exit PASS')
print('WINDOWS_VERT_OFFSET=8')
print('WINDOWS_POLICY=8 extraOffset=0')
print('WINDOWS_LIVE_FINAL_PAIR=linecount3552 FLL3560 gain1.0 time33312452ns')
print('VT_CLOCK_HZ=719898240')
print('LINE_READOUT_NS_BITS=0x40c2518d3ad36374')
print('LINECOUNT_ROUNDING=FRINTA nearest ties-away')
print('FLL_RULE=3554 when linecount<=3546 else linecount+8')
print('SINGLE_EXPOSURE_SENSOR_LANE=Short (BC count1 Short->S1..S4)')
print('T681_ACTIVE_PREVIEW_DOMAIN=gain1..92,time37516..66666664')
print('AP_LIVE_CONTROL_EVIDENCE=retained PASS')
print('FIXED_CASES=%d' % len(fixed))
print('RANDOM_CASES=65536')
print('ACTUAL_CH_TO_CQ_SEAM_CASES=16384')
print('NATIVE_VS_AJ_TIMING_GAIN=bit-exact PASS')
print('CQ_VERIFY=PASS')
