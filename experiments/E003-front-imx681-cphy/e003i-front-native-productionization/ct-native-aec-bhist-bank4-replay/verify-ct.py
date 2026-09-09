#!/usr/bin/env python3
import ctypes
import hashlib
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
ORACLE = Path('/tmp/sp11-aec-oracle')
DLL = ORACLE / 'QcDeviceMFT8380.dll'
TUNING = ORACLE / 'com.surface.tuned.ffc_imx681.bin'
DLL_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA = '2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
AXIS_SHA = 'f552e96271ad0737af14ab0272aa31c628dbf6b9d8b11d7ddcb8dd0d510e39f9'
S1_ORACLE_SHA = '21f4cd87bf24333aa717dfdbeea0e57bf49b29aa949adf7dc9dd45814decbf46'
RUNTIME_FLAGS_ORACLE_SHA = '04addcfd69a3ef2b2a37016c3cb63bf33c14d4d8fb61157a05b02fd6786a8e40'


def ensure_oracles():
    archive = REPO.parents[1] / '00-RE-archive' / 'sp11-driverdump'
    dll_src = archive / 'surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342' / 'QcDeviceMFT8380.dll'
    tune_src = archive / 'surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e' / 'com.surface.tuned.ffc_imx681.bin'
    assert dll_src.is_file(), dll_src
    assert tune_src.is_file(), tune_src
    ORACLE.mkdir(parents=True, exist_ok=True)
    if not DLL.is_file():
        shutil.copy2(dll_src, DLL)
    if not TUNING.is_file():
        shutil.copy2(tune_src, TUNING)

    # Legacy AV and descendants consume a retained full disassembly cache. /tmp
    # is reboot-volatile, so recreate it deterministically from the pinned DLL.
    full_asm = ORACLE / 'full.asm'
    if not full_asm.is_file():
        with full_asm.open('w') as f:
            subprocess.run(['llvm-objdump', '-d', str(DLL)], stdout=f,
                           stderr=subprocess.DEVNULL, check=True)


def fresh(rel, script, marker):
    p = BASE / rel / script
    cp = subprocess.run([sys.executable, str(p)], cwd=p.parent, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout, (rel, marker, cp.stdout[-4000:])


def dis(a, b):
    return subprocess.check_output([
        'llvm-objdump', '-d', f'--start-address={hex(a)}',
        f'--stop-address={hex(b)}', str(DLL)
    ], text=True, stderr=subprocess.DEVNULL)


def line_has(text, addr, *parts):
    key = f'{addr:x}:'
    lines = [x for x in text.splitlines() if key in x]
    assert len(lines) == 1, (hex(addr), lines)
    for part in parts:
        assert part in lines[0], (hex(addr), part, lines[0])


def fbits(x):
    return struct.unpack('<I', struct.pack('<f', x))[0]


def assert_f32_tuple(actual, expected):
    assert tuple(map(fbits, actual)) == tuple(map(fbits, expected)), (actual, expected)


def parse_axis_oracle(path):
    text = path.read_text(errors='replace')
    m = re.search(r'CTAXIS .*? axis=([0-9a-fA-F]+)', text)
    assert m, 'missing CTAXIS axis pointer'
    start = int(m.group(1), 16)
    vals = []
    active = False
    for line in text.splitlines():
        mm = re.match(r'^([0-9a-fA-F]+)`([0-9a-fA-F]+)\s+(.+?)\s*$', line)
        if not mm:
            continue
        addr = int(mm.group(1) + mm.group(2), 16)
        words = re.findall(r'\b[0-9a-fA-F]{8}\b', mm.group(3))
        if not active:
            if addr != start:
                continue
            active = True
        expected = start + len(vals) * 4
        if addr != expected:
            break
        vals.extend(int(x, 16) for x in words)
        if len(vals) >= 1024:
            break
    assert len(vals) == 1024, len(vals)
    return b''.join(struct.pack('<I', x) for x in vals)


ensure_oracles()
assert hashlib.sha256(DLL.read_bytes()).hexdigest() == DLL_SHA
assert hashlib.sha256(TUNING.read_bytes()).hexdigest() == TUNING_SHA

# Join CT to accepted ownership/raw authority and the accepted S1 enum/history proof.
fresh('cs-windows-aec-bhist-bright-ratio', 'verify-cs.py', 'CS_VERIFY=PASS')
fresh('cj-windows-aec-source-s1-history-provenance', 'verify-cj.py', 'CJ_VERIFY=PASS')

sys.path.insert(0, str(REPO / 'tools'))
import qti_parameter_bin as qti
obj = qti.parse(TUNING)
ids = {e['id']: e for e in obj['entries']}

def raw(eid): return bytes.fromhex(ids[eid]['raw_hex'])
def u32s(eid):
    b = raw(eid); assert len(b) % 4 == 0
    return struct.unpack('<%dI' % (len(b)//4), b)
def f32s(eid):
    b = raw(eid); assert len(b) % 4 == 0
    return struct.unpack('<%df' % (len(b)//4), b)

def text(ref): return ids[ref]['text']

# Serialized calculator descriptors are 23 u32 = 0x5c bytes. The live
# runtime oracle below proves serialized word 12 becomes expanded runtime +0x38,
# while serialized words 13/14 become runtime +0x3c/+0x40 outputStart/outputEnd.
w = u32s(162)
fixed = [w[5+i*23:5+(i+1)*23] for i in range(4)]
sc = raw(7120)
assert len(sc) == 55 * 92
configurable = [struct.unpack_from('<23I', sc, i*92) for i in range(55)]
by_id = {r[0]: r for r in fixed + configurable}
expected_calcs = {
    4:  ('BrightRatio',              5, 'BhistY', (5, 6),   7118, 1),
    11: ('SatPrevHighPCTLLuma',      6, 'BhistY', (7, 7),   7126, 1),
    12: ('DarkPrevLowPCTLLuma',      6, 'BhistY', (8, 8),   7133, 1),
    23: ('ShortSatPrevHighPCTLLuma', 6, 'BhistY', (19, 19), 7196, 0),
}
for cid, (desc, api, channel, outs, trig, flag38) in expected_calcs.items():
    r = by_id[cid]
    assert text(r[2]) == desc
    assert r[3] == api
    assert text(r[5]) == channel
    assert tuple(r[13:15]) == outs
    assert r[20] == trig
    assert r[12] == flag38

assert_f32_tuple(f32s(7118), (0.0, 1000.0, 255.0, 256.0))
assert_f32_tuple(f32s(7126), (
    0.0,160.0,0.85,1.0, 180.0,260.0,0.95,0.99,
    300.0,360.0,0.95,0.99, 440.0,480.0,0.96,0.99,
    500.0,1000.0,0.98,1.0))
assert_f32_tuple(f32s(7133), (
    0.0,270.0,0.0,0.11, 300.0,360.0,0.0,0.12,
    380.0,460.0,0.0,0.12, 480.0,1000.0,0.0,0.15))
assert_f32_tuple(f32s(7196), (
    0.0,190.0,0.99,1.0, 240.0,290.0,0.98,1.0,
    340.0,1000.0,0.98,1.0))

# Exact cap provenance. Runtime calculator +0x38 is a separate flag; runtime
# outputStart/outputEnd are +0x3c/+0x40. RunCalculator passes +0x38 as w1 and
# record+0x30 source tag as w2 to the cap-scale helper at 0x1803eac78.
run = dis(0x1803f4cf0, 0x1803f4de0)
line_has(run, 0x1803f4cf4, 'ldp', 'x8, x12, [x21, #0x80]')
line_has(run, 0x1803f4d50, 'ldr', 'w26, [x8, #0x38]')
line_has(run, 0x1803f4dc4, 'mov', 'w1, w26')
line_has(run, 0x1803f4dd0, 'ldr', 'w2, [x8, #0x30]')
line_has(run, 0x1803f4dd4, 'bl', '0x1803eac78')
pub = dis(0x1803f63c0, 0x1803f6400)
line_has(pub, 0x1803f63d8, 'ldr', 'x8, [x21, #0x80]')
line_has(pub, 0x1803f63dc, 'ldp', 'w9, w8, [x8, #0x3c]')

# API5/API6 range wrapper carries the same descriptor +0x38 value as kernel w5.
wrap = dis(0x1803f6808, 0x1803f68a4)
line_has(wrap, 0x1803f6844, 'ldp', 'x9, x8, [x23, #0x80]')
line_has(wrap, 0x1803f6860, 'ldr', 'w25, [x9, #0x38]')
line_has(wrap, 0x1803f6880, 'mov', 'w5, w25')
line_has(wrap, 0x1803f689c, 'bl', '0x1803ea478')

kernel = dis(0x1803ea478, 0x1803ea5a0)
line_has(kernel, 0x1803ea4d0, 'mov', 'w20, w5')
line_has(kernel, 0x1803ea500, 'mov', 'x9, #0x48')
line_has(kernel, 0x1803ea514, 'ldr', 'w26, [x1, #0x30]')
line_has(kernel, 0x1803ea51c, 'mov', 'w2, w26')
line_has(kernel, 0x1803ea520, 'mov', 'w1, w20')
line_has(kernel, 0x1803ea528, 'bl', '0x1803eac78')
line_has(kernel, 0x1803ea574, 'ldp', 'w10, w9, [x9, #0x14]')
line_has(kernel, 0x1803ea578, 'scvtf', 'd1, w9')
line_has(kernel, 0x1803ea584, 'bl', '0x180cee718')
line_has(kernel, 0x1803ea58c, 'fsub', 'd16, d0, d16')
line_has(kernel, 0x1803ea594, 'fmul', 's16, s16, s8')

scale = dis(0x1803eac78, 0x1803ead40)
line_has(scale, 0x1803eac90, 'ldr', 's8, 0x1803ead38')
line_has(scale, 0x1803eac94, 'mov', 'w20, w2')
line_has(scale, 0x1803eac98, 'cmp', 'w1, #0x1')
line_has(scale, 0x1803eac9c, 'b.ne', '0x1803ead1c')
line_has(scale, 0x1803eacd4, 'ldr', 'x8, [x0, #0x78]')
line_has(scale, 0x1803eacd8, 'ucvtf', 's17, x8')
line_has(scale, 0x1803eace0, 'add', 'x9, x8, #0x1')
line_has(scale, 0x1803eace4, 'mov', 'x8, #0x28')
line_has(scale, 0x1803eace8, 'mul', 'x8, x9, x8')
line_has(scale, 0x1803eacec, 'ldr', 'x8, [x8, x0]')
line_has(scale, 0x1803eacf0, 'ucvtf', 's16, x8')
line_has(scale, 0x1803eacfc, 'fdiv', 's17, s17, s16')
line_has(scale, 0x1803ead04, 'ldr', 's16, [x0, #0x178]')
line_has(scale, 0x1803ead08, 'fdiv', 's17, s17, s16')
line_has(scale, 0x1803ead10, 'fcmpe', 's17, s16')
line_has(scale, 0x1803ead14, 'b.le', '0x1803ead1c')
line_has(scale, 0x1803ead18, 'fdiv', 's8, s8, s17')
# Literal is exactly float32 0.98f.
image = DLL.read_bytes()
# .text raw offset = RVA - 0xc00 for this image.
def dll_off(va): return (va - 0x180000000) - 0xc00
assert struct.unpack_from('<I', image, dll_off(0x1803ead38))[0] == 0x3f7ae148

# The retained one-shot proves ordinary 1024-bin BhistY record+0x30 carries tag 3.
s1log = HERE/'windows-oracle'/'E003I-CT-BHIST-S1-ORACLE_20260909.txt'
assert hashlib.sha256(s1log.read_bytes()).hexdigest() == S1_ORACLE_SHA
hits = re.findall(r'^CT_BHIST .*?tag=([0-9a-fA-F]+).*?type0=([0-9a-fA-F]+).*?bins=([0-9a-fA-F]+)',
                  s1log.read_text(errors='replace'), re.M)
assert len(hits) >= 5
assert {int(tag,16) for tag,_,_ in hits} == {3}
assert {int(bins,16) for _,_,bins in hits} == {0x400}
assert len({int(fid,16) for _,fid,_ in hits}) >= 5
cj = json.loads((BASE/'cj-windows-aec-source-s1-history-provenance'/'RESULT.json').read_text())
assert cj['ordinary_analyzer_source_type'] == 'S1'
assert cj['source_vector']['lanes'][3] == 'S1'

# Read-only live process-memory oracle pins the expanded runtime +0x38 flags and
# disambiguates ordinary BhistY from BhistY_short by dereferenced channel name.
rtlog = HERE/'windows-oracle'/'E003I-CT-RUNTIME-DESCRIPTOR-FLAGS_20260909.txt'
assert hashlib.sha256(rtlog.read_bytes()).hexdigest() == RUNTIME_FLAGS_ORACLE_SHA
rtt = rtlog.read_text(errors='replace')
for snippet in (
    'id=4 api=5 name=BrightRatio channel=BhistY\n  runtime +0x38 flag = 1',
    'id=11 api=6 name=SatPrevHighPCTLLuma channel=BhistY\n  runtime +0x38 flag = 1',
    'id=12 api=6 name=DarkPrevLowPCTLLuma channel=BhistY\n  runtime +0x38 flag = 1',
    'id=23 api=6 name=ShortSatPrevHighPCTLLuma channel=BhistY\n  runtime +0x38 flag = 0',
    'BhistY_short and flag=0'):
    assert snippet in rtt, snippet

# The native request loop already retains the exact F-3 state consumed by the
# Windows flag==1 helper: Safe, S1 and predictive gain.
loop_h = (BASE/'cl-native-aec-self-fed-s1-history'/'native-aec-request-loop.h').read_text()
for field in ('uint64_t safe_exposure;', 'uint64_t s1_exposure;', 'float pred_gain;'):
    assert field in loop_h

# Exact 1024-entry producer axis: compare retained Windows bytes to native output.
axis_oracle = parse_axis_oracle(HERE/'windows-oracle'/'E003I-CT-VALUE-AXIS.log')
assert len(axis_oracle) == 4096
assert hashlib.sha256(axis_oracle).hexdigest() == AXIS_SHA

with tempfile.TemporaryDirectory(prefix='e003i-ct-') as td:
    td = Path(td)
    libp = td/'libe003i-ct.so'
    subprocess.run([
        'gcc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fPIC','-shared',
        '-I'+str(HERE), str(HERE/'native-bhist-bank4.c'), '-lm', '-o', str(libp)
    ], check=True)
    lib = ctypes.CDLL(str(libp))
    Axis = ctypes.c_float * 1024
    axis = Axis()
    lib.e003i_bhist_build_value_axis.argtypes = [ctypes.POINTER(ctypes.c_float)]
    lib.e003i_bhist_build_value_axis.restype = ctypes.c_int
    assert lib.e003i_bhist_build_value_axis(axis) == 0
    native_axis = ctypes.string_at(ctypes.addressof(axis), ctypes.sizeof(axis))
    assert native_axis == axis_oracle

    class Hist(ctypes.Structure):
        _fields_ = [
            ('safe_exposure', ctypes.c_uint64),
            ('s1_exposure', ctypes.c_uint64),
            ('pred_gain', ctypes.c_float)]
    class Out(ctypes.Structure):
        _fields_ = [
            ('b6', ctypes.c_float), ('b7', ctypes.c_float),
            ('b8', ctypes.c_float), ('b19', ctypes.c_float)]
    Raw = ctypes.c_uint32 * 1024
    lib.e003i_bhist_replay_bank4.argtypes = [
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_float,
        ctypes.POINTER(Hist), ctypes.POINTER(Out)]
    lib.e003i_bhist_replay_bank4.restype = ctypes.c_int

    neutral = Hist(1000, 1000, 1.0)   # Safe/S1/PredGain ratio = 1 -> 0.98f
    limited = Hist(200, 100, 1.0)     # ratio = 2 -> scale = 0.49f
    gain_cancel = Hist(200, 100, 2.0) # ratio = 1 after PredGain -> 0.98f
    startup_zero = Hist(33333332, 33333332, 0.0) # CN/CP synthetic start history

    def replay(k, lux, history=neutral, raw_word=1):
        a = Raw()
        if k is not None:
            a[k] = raw_word
        o = Out()
        assert lib.e003i_bhist_replay_bank4(
            a, ctypes.c_float(lux), ctypes.byref(history), ctypes.byref(o)) == 0
        return tuple(fbits(getattr(o, n)) for n in ('b6','b7','b8','b19'))

    fixtures = [
        (None, 350.0, (0x00000000,0x00000000,0x00000000,0x00000000)),
        (0,      0.0, (0x00000000,0x3a807358,0x3a807358,0x3a807358)),
        (127,  200.0, (0x00000000,0x3e000000,0x3e000000,0x3e000000)),
        (500,  350.0, (0x00000000,0x40d20405,0x40d20404,0x40d20404)),
        (1022, 500.0, (0x00000000,0x4379e667,0x4379e668,0x4379e667)),
        (1023, 500.0, (0x3f800000,0x4379e667,0x4379e668,0x4379e667)),
    ]
    for k, lux, exp in fixtures:
        got = replay(k, lux)
        assert got == exp, (k, lux, got, exp)

    # Exact history-normalized cap behavior for ordinary source tag S1=3.
    # Bank4:6 is the API5 CDF-mass lane and is invariant to the weighted-luma cap;
    # Bank4:19 has runtime flag=0 and also stays on fixed 0.98f.
    assert replay(1023, 500.0, limited) == (
        0x3f800000, 0x42f9e667, 0x42f9e668, 0x4379e667)
    assert replay(1023, 500.0, gain_cancel) == replay(1023, 500.0, neutral)
    assert replay(1023, 500.0, startup_zero) == (
        0x3f800000, 0x00000000, 0x00000000, 0x4379e667)

    # Invalid retained history cannot produce an exact Windows-equivalent 7/8.
    bad = Hist(0, 100, 1.0); a = Raw(); o = Out()
    assert lib.e003i_bhist_replay_bank4(
        a, ctypes.c_float(350.0), ctypes.byref(bad), ctypes.byref(o)) == -1

    # Parser mask is local to the replay: high seven bits cannot change results.
    assert replay(500, 350.0, raw_word=0xfe000001) == replay(500, 350.0, raw_word=1)

    # Exercise actual generation-tagged Golden-safe Linux STATS3A producer data
    # under a neutral history vector. This is an adapter fixture, not same-frame
    # Windows Bank4 oracle output.
    real = {
        1: ('ac3d527b95d36b422d314cb6921b697e7dc48f1d15700eaf27eab06de4497e4a',
            '42325c63ba6d7f05cc27523eb18684f09fed96186ed000a2f9d9eb7d399a6889',
            (0x00000000,0x41079b60,0x3f127b0e,0x4197267d)),
        2: ('fe0d8b22ab4d6a7092b2e55dd8102acd45608ada5f575e23a389df170c6e8da4',
            '638717265e0d2f288dc64df854b10e77a892c75f96aef045e8fb109f4bdf98e6',
            (0x00000000,0x41078f1e,0x3f1059a5,0x4196e518)),
        3: ('3e5bb2e3b5da20723cff2bf7f56485ce71ccebb849326ef72b5273207d0e3628',
            'ff6c6245a7822f195ee80083e60d66cb78abf9860ce2bdbe3567097566251129',
            (0x00000000,0x4107a647,0x3f108b96,0x4196ca33)),
    }
    ap = BASE/'ap-bounded-imx681-control-runtime'/'runtime-output'/'producer'
    for gen, (file_sha, bh_sha, exp) in real.items():
        b = (ap/f'STATS3A-G{gen}.bin').read_bytes()
        assert hashlib.sha256(b).hexdigest() == file_sha
        bh = b[0x14040:0x15040]
        assert len(bh) == 4096 and hashlib.sha256(bh).hexdigest() == bh_sha
        vals = struct.unpack('<1024I', bh)
        assert sum(v & 0x01ffffff for v in vals) == 2073600
        a = Raw(*vals); o = Out()
        assert lib.e003i_bhist_replay_bank4(
            a, ctypes.c_float(358.141845703125), ctypes.byref(neutral), ctypes.byref(o)) == 0
        got = tuple(fbits(getattr(o,n)) for n in ('b6','b7','b8','b19'))
        assert got == exp, (gen, got, exp)

result = {
    'schema': 'sp11-e003i-ct-native-aec-bhist-bank4-replay-v1',
    'accepted': True,
    'dll_sha256': DLL_SHA,
    'tuning_sha256': TUNING_SHA,
    'windows_axis_sha256': AXIS_SHA,
    'windows_s1_oracle_sha256': S1_ORACLE_SHA,
    'windows_runtime_flags_oracle_sha256': RUNTIME_FLAGS_ORACLE_SHA,
    'bhist': {
        'bins': 1024,
        'raw_word_mask': '0x01ffffff',
        'record_source_tag': 3,
        'record_source_lane': 'S1',
        'bit_depth': 8,
    },
    'value_axis': {
        'entries': 1024,
        'bytes': 4096,
        'native_matches_windows_bytes': True,
        'last_value': 255.5,
    },
    'runtime_flags': {
        'bank4_6_BrightRatio': 1,
        'bank4_7_SatPrevHighPCTLLuma': 1,
        'bank4_8_DarkPrevLowPCTLLuma': 1,
        'bank4_19_ShortSatPrevHighPCTLLuma': 0,
    },
    'cap_scale': {
        'literal_bits': '0x3f7ae148',
        'literal': 0.98,
        'flag1_formula_for_source_S1': 'ratio=float(Safe)/float(S1)/PredGain; scale=(ratio>1)?0.98f/ratio:0.98f; PredGain=+0 -> +inf then scale +0',
        'history_required_for_outputs': [7,8],
        'bank4_6_note': 'BrightRatio flag=1 but Bank4:6 is CDF-mass lane and does not consume weighted-luma cap',
        'bank4_19_note': 'runtime flag=0, fixed 0.98f cap',
        'bit_depth_cap': '(2^8 - 1) * selected_scale',
    },
    'history_input': {
        'temporal_source': 'ordinary retained F-3 history',
        'fields': ['safe_exposure','s1_exposure','pred_gain'],
        'already_carried_by': 'cl-native-aec-self-fed-s1-history/native-aec-request-loop.h',
    },
    'bank4': {
        '6': 'BrightRatio API5 normalized CDF mass over value range [255,256]',
        '7': 'SatPrevHighPCTLLuma API6 percentile-weighted luma with flag1 S1 history cap',
        '8': 'DarkPrevLowPCTLLuma API6 percentile-weighted luma with flag1 S1 history cap',
        '19': 'ShortSatPrevHighPCTLLuma API6 percentile-weighted luma with fixed cap',
    },
    'native': {
        'source': 'native-bhist-bank4.c',
        'axis_exact': True,
        'cdf_reciprocal': 'ARM FRECPE + two FRECPS/Newton refinements',
        'synthetic_fixture_count': 9,
        'real_stats3a_fixture_count': 3,
        'mask_equivalence_checked': True,
        'history_branch_checked': True,
        'cold_start_zero_pred_gain_checked': True,
    },
    'safety': {
        'windows_oracles': 'read-only KDNET plus read-only FrameServer process-memory scan; returned to Golden Linux',
        'linux_camera_runtime': False,
        'golden_saved_entry': 'sp11-audio-fullio-v19c',
    },
    'scope_limit': 'ordinary raw BhistY + LuxIndex + retained F-3 Safe/S1/PredGain -> Bank4 {6,7,8,19}; not full continuous AEC/convergence',
    'status': 'PASS',
}
(HERE/'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('BHIST_SOURCE_TAG=3=S1')
print('RUNTIME_FLAGS=BrightRatio:1 SatPrev:1 DarkPrev:1 ShortSatPrev:0')
print('HISTORY_CAP=Safe/S1/PredGain -> Bank4:7,8; startup PredGain=0 -> exact zero cap; Bank4:6 mass invariant; Bank4:19 fixed')
print('VALUE_AXIS_SHA256='+AXIS_SHA)
print('VALUE_AXIS_NATIVE_BYTE_EXACT=PASS')
print('REAL_STATS3A_FIXTURES=3')
print('BANK4_REPLAY={6,7,8,19}')
print('CT_VERIFY=PASS')
