#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
DLL = Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING = Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA = '2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'

assert DLL.is_file(), DLL
assert TUNING.is_file(), TUNING
assert hashlib.sha256(DLL.read_bytes()).hexdigest() == DLL_SHA
assert hashlib.sha256(TUNING.read_bytes()).hexdigest() == TUNING_SHA

sys.path.insert(0, str(REPO / 'tools'))
import qti_parameter_bin as qti  # noqa: E402


def dis(start: int, stop: int) -> str:
    return subprocess.check_output([
        'llvm-objdump', '-d', f'--start-address={hex(start)}',
        f'--stop-address={hex(stop)}', str(DLL)
    ], text=True)


def req(text: str, *needles: str) -> None:
    for needle in needles:
        assert needle in text, needle


def pe_sections(data: bytes):
    e = struct.unpack_from('<I', data, 0x3c)[0]
    coff = e + 4
    nsec = struct.unpack_from('<H', data, coff + 2)[0]
    opt_size = struct.unpack_from('<H', data, coff + 16)[0]
    opt = coff + 20
    image = struct.unpack_from('<Q', data, opt + 24)[0]
    secbase = opt + opt_size
    out = []
    for i in range(nsec):
        o = secbase + i * 40
        name = data[o:o+8].split(b'\0', 1)[0].decode('ascii', 'replace')
        vsize, rva, rsize, rptr = struct.unpack_from('<IIII', data, o + 8)
        out.append((name, image + rva, vsize, rsize, rptr))
    return out


DLL_BYTES = DLL.read_bytes()
SECTIONS = pe_sections(DLL_BYTES)


def va_off(va: int) -> int:
    for _name, start, vsize, rsize, rptr in SECTIONS:
        if start <= va < start + max(vsize, rsize):
            return rptr + (va - start)
    raise AssertionError(f'VA outside image: {va:#x}')


def cstr(va: int) -> str:
    o = va_off(va)
    z = DLL_BYTES.find(b'\0', o)
    assert z >= 0
    return DLL_BYTES[o:z].decode('ascii', 'replace')


# ---- Exact exposure-type conversion and names ----
# UtilExposureTypeTuning2Enum jump table. Each signed byte is a word-offset
# from table base 0x180388764 to one of the return stubs.
raw = DLL_BYTES[va_off(0x180388764):va_off(0x180388764)+8]
offs = struct.unpack('8b', raw)
dests = tuple(0x180388764 + v * 4 for v in offs)
return_value = {
    0x180388658: 0,
    0x18038866c: 2,
    0x180388680: 1,
    0x180388750: 3,
    0x180388694: 4,
    0x1803886a8: 5,
    0x1803886bc: 6,
}
conversion = tuple(return_value[d] for d in dests)
assert conversion == (0, 2, 1, 3, 4, 5, 6, 3), (offs, dests, conversion)

# Internal enum-to-string helper @ 0x1803885b0 has a seven-entry table.
raw_names = DLL_BYTES[va_off(0x180388628):va_off(0x180388628)+7]
name_dests = tuple(0x180388628 + v * 4 for v in struct.unpack('7b', raw_names))
name_va_for_stub = {
    0x1803885c8: 0x1813ad620,
    0x1803885d4: 0x1813ad638,
    0x1803885e0: 0x1813ad630,
    0x1803885ec: 0x1813ad62c,
    0x1803885f8: 0x1813ad628,
    0x180388604: 0x1813ad650,
    0x180388610: 0x1813ad64c,
}
internal_names = tuple(cstr(name_va_for_stub[d]) for d in name_dests)
assert internal_names == ('Short', 'Long', 'Safe', 'S1', 'S2', 'S3', 'S4')
tuning_names = tuple(internal_names[i] for i in conversion)
assert tuning_names == ('Short', 'Safe', 'Long', 'S1', 'S2', 'S3', 'S4', 'S1')

# ---- Compact IMX681 analyzer tuning ----
obj = qti.parse(TUNING)
entries = obj['entries']
ids = {e['id']: e for e in entries}
analyzers = ids[3592]
assert analyzers['name'] == 'analyzers'
assert analyzers['payload_size'] == 7280 == 52 * 0x8c
payload = bytes.fromhex(analyzers['raw_hex'])
name_text = {e['id']: e['text'] for e in entries if e['name'] == 'analyzerName' and e['text']}
records = {}
for n in range(52):
    rec = payload[n*0x8c:(n+1)*0x8c]
    assert len(rec) == 0x8c
    words = struct.unpack('<35I', rec)
    analyzer_id = words[0]
    name_len, name_ref = words[3], words[4]
    name = name_text.get(name_ref)
    assert name is not None, (n, analyzer_id, name_ref)
    assert name_len == len(name) + 1, (name, name_len)
    records[analyzer_id] = {
        'name': name,
        # Compact Parameter Bin uses 32-bit string length/ref pairs. After
        # parser expansion those become native pointers, so these are the
        # two scalar fields that follow analyzerName in compact order.
        'exposure_type': words[5],
        'source_type': words[6],
    }
assert len(records) == 52

expected = {
    2: ('FrameSA', 1, 3),
    3: ('SafeAggSA', 1, 3),
    4: ('ShortAggSA', 0, 3),
    5: ('LongAggSA', 2, 3),
    0x34: ('HDRSafeAggSA', 1, 1),
    0x35: ('HDRShortAggSA', 0, 0),
    0x36: ('HDRLongAggSA', 2, 2),
}
for aid, (name, et, st) in expected.items():
    r = records[aid]
    assert (r['name'], r['exposure_type'], r['source_type']) == (name, et, st), (aid, r)

# DefaultSequence is separately named in the active-analyzer tuning.
assert ids[2568]['name'] == 'description' and ids[2568]['text'] == 'DefaultSequence'
seq = list(struct.unpack('<14I', bytes.fromhex(ids[2569]['raw_hex'])))
assert ids[2569]['name'] == 'analyzerID'
assert seq == [2, 30, 31, 32, 45, 35, 36, 47, 58, 81, 60, 3, 4, 5]
assert [records[i]['name'] for i in seq] == [
    'FrameSA', 'SatPrevSA', 'DarkPrevSA', 'BrightenImgSA', 'ExtremeColorSA',
    'ShortSatPrevSA', 'LongDarkPrevSA', 'YHistSA', 'IlluminanceSA',
    'AFBrktFlagSA', 'ADRCCapSA', 'SafeAggSA', 'ShortAggSA', 'LongAggSA'
]

# ---- Native expanded tuning -> CAnalyzer fields ----
set_tuning = dis(0x1803f18d8, 0x1803f1940)
req(set_tuning,
    '1803f192c:', 'ldr\tw8, [x23, #0x18]',
    '1803f1930:', 'str\tw8, [x19, #0x28]',
    '1803f1934:', 'ldr\tw8, [x23, #0x1c]',
    '1803f1938:', 'str\tw8, [x19, #0x2c]')

# ---- CAnalyzer target-SI producer ----
run = dis(0x1803f0ef8, 0x1803f18d0)
# First aggregate -> measured luma.
req(run,
    '1803f100c:', 'add\tx0, x19, #0x38',
    '1803f1010:', 'bl\t0x1803ef500',
    '1803f1014:', 'ldr\ts16, [x0]',
    '1803f1018:', 'str\ts16, [x19, #0x10]')
# Target pair and confidence are committed into the returned result object.
req(run,
    '1803f15c4:', 'str\tx8, [x19, #0x18]',
    '1803f15d8:', 'str\ts16, [x19, #0x14]')
# sourceType selects the seven-lane source exposure.
req(run,
    '1803f15e0:', 'ldr\tw0, [x19, #0x2c]',
    '1803f15f0:', 'bl\t0x180388630',
    '1803f15f4:', 'add\tx20, x20, w0, sxtw #3',
    '1803f15fc:', 'ldr\td8, [x20]')
# Exact scalar arithmetic and SI storage.
req(run,
    '1803f1694:', 'ldr\ts17, [x19, #0x10]',
    '1803f1698:', 'ldr\ts16, 0x1803f18d0',
    '1803f169c:', 'fcmp\ts17, s16',
    '1803f16a0:', 'fcsel\ts17, s17, s16, gt',
    '1803f16a4:', 'ldr\ts16, [x19, #0x18]',
    '1803f16a8:', 'fdiv\ts16, s16, s17',
    '1803f16ac:', 'fcvt\td16, s16',
    '1803f16b4:', 'fmul\td16, d16, d8',
    '1803f16b8:', 'fcvtzu\tx8, d16',
    '1803f16bc:', 'str\tx8, [x19, #0x20]',
    '1803f18a8:', 'add\tx0, x19, #0x8')
assert struct.unpack('<I', DLL_BYTES[va_off(0x1803f18d0):va_off(0x1803f18d0)+4])[0] == 0x33d6bf95

# Returned result +0x20 is consumed as tuning exposureType by AnalyzerManager.
mgr = dis(0x1803b21f0, 0x1803b2864)
req(mgr,
    '1803b2660:', 'add\tx1, x19, #0x20',
    '1803b2668:', 'bl\t0x1803f0ef8',
    '1803b2684:', 'ldr\tw8, [x21, #0x20]',
    '1803b26b0:', 'ldr\tw0, [x21, #0x20]',
    '1803b26b4:', 'bl\t0x180388630')

# ---- Reuse the already-closed live FrameSA measured-luma evidence ----
ab = json.loads((BASE / 'ab-clean-lux-reconstruction' / 'RESULT.json').read_text())
ml = ab['measured_luma']
assert ml['status'] == 'PASS_LIVE_BIT_EXACT'
assert 'FrameSA analyzer ID 2' in ml['normal_path']
assert ml['ab23_live_bits'] == ml['ab23_replay_bits'] == '0x3f5d179f'
assert ml['ab26_live_bits'] == ml['ab26_replay_bits'] == '0x3f26a3f7'
assert len(ml['ab8_live_cases']) == 8 and all(x['pass'] for x in ml['ab8_live_cases'])

# ---- Offline arithmetic model ----
spec = importlib.util.spec_from_file_location('bdmodel', HERE / 'windows-target-si.py')
model = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = model
spec.loader.exec_module(model)
assert model.EPS_BITS == 0x33d6bf95
assert model.TUNING_TO_INTERNAL == conversion
assert model.TUNING_NAMES == tuning_names
assert model.source_lane(3) == 3 and model.TUNING_NAMES[3] == 'S1'
# Distinguish float32 division from all-double arithmetic with a chosen case.
a = model.target_si(33_312_451.0, model.from_bits(0x3f5d179f), 50.0)
measured = model.from_bits(0x3f5d179f)
double_only = int(33_312_451.0 * (50.0 / measured))
assert a != double_only, (a, double_only)
# Clamp and truncation sanity checks.
assert model.target_si(100.0, 1.0, 1.0) == 100
assert model.target_si(100.0, 0.0, model.EPS) == 100

# Fresh static/evidence downstream joins. Do not require proprietary live fixtures.
def run_verify(rel: str, script: str, marker: str) -> None:
    p = BASE / rel / script
    cp = subprocess.run([sys.executable, str(p)], cwd=p.parent, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout, (rel, marker, cp.stdout)

run_verify('bc-windows-aec-single-exposure-output', 'verify-bc.py', 'BC_VERIFY=PASS')

print('DLL_SHA256=' + DLL_SHA)
print('TUNING_SHA256=' + TUNING_SHA)
print('ANALYZER_RECORDS=52x0x8c')
print('TUNING_TO_INTERNAL=0,2,1,3,4,5,6,3')
print('INTERNAL_NAMES=Short,Long,Safe,S1,S2,S3,S4')
print('NORMAL_ANALYZERS=FrameSA:Safe<-S1,SafeAggSA:Safe<-S1,ShortAggSA:Short<-S1,LongAggSA:Long<-S1')
print('HDR_CROSSCHECK=Safe<-Safe,Short<-Short,Long<-Long')
print('RESULT_EXPOSURE_TYPE=CAnalyzer+0x28 -> result+0x20 -> UtilExposureTypeTuning2Enum')
print('SOURCE_TYPE=CAnalyzer+0x2c -> UtilExposureTypeTuning2Enum -> source exposure lane')
print('SI=FCVTZU(double(sourceExposure)*double(f32(targetLow/max(measured,eps))))')
print('EPS_BITS=0x33d6bf95')
print('AB_FRAMESA_LUMA_JOIN=PASS_LIVE_BIT_EXACT')
print('DOWNSTREAM_JOIN=BC PASS')
print('BD_VERIFY=PASS')
