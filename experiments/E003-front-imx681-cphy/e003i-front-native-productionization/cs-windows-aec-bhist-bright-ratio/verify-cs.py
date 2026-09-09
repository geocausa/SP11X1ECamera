#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, subprocess, sys
import pefile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
DLL = Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING = Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA = '2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest() == DLL_SHA
assert TUNING.is_file() and hashlib.sha256(TUNING.read_bytes()).hexdigest() == TUNING_SHA
sys.path.insert(0, str(REPO / 'tools'))
import qti_parameter_bin as qti


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


# Keep CS joined to the accepted ordinary AEC chain and the already accepted
# raw front 3A transport/parser authority.
fresh('cr-native-aec-effective-analyzer-producer', 'verify-cr.py', 'CR_VERIFY=PASS')
fresh('y-generation-tagged-3a-stats', 'prove-3a-raw-authority.py', '"accepted": true')

obj = qti.parse(TUNING)
ids = {e['id']: e for e in obj['entries']}

def raw(eid): return bytes.fromhex(ids[eid]['raw_hex'])
def u32s(eid):
    b = raw(eid); assert len(b) % 4 == 0
    return struct.unpack('<%dI' % (len(b)//4), b)
def f32s(eid):
    b = raw(eid); assert len(b) % 4 == 0
    return struct.unpack('<%df' % (len(b)//4), b)

# aecxmeteringstatscalculator is a five-word header, four fixed 23-u32
# calculator descriptors, then (count=55, ref=7120) for tunable calculators.
w = u32s(162)
assert len(w) == 99 and w[:5] == (10, 0, 0, 2, 7091)
assert w[97:] == (55, 7120)
fixed = [w[5+i*23:5+(i+1)*23] for i in range(4)]
assert [r[0] for r in fixed] == [1, 2, 3, 4]
expected = [
    ('AvgLumaBE16x16', 1, 'LumaBE16x16', (1,1), 7097),
    ('FrameLuma',       1, 'LumaBE16x16', (2,2), 7104),
    ('DarkRatio',       5, 'BhistY',       (3,4), 7111),
    ('BrightRatio',     5, 'BhistY',       (5,6), 7118),
]
for r, (desc, api, channel, out_range, trigref) in zip(fixed, expected):
    assert ids[r[2]]['text'] == desc, (r[0], ids[r[2]]['text'])
    assert r[3] == api, (r[0], r[3])
    assert ids[r[5]]['text'] == channel, (r[0], ids[r[5]]['text'])
    assert tuple(r[13:15]) == out_range, (r[0], r[13:15])
    assert r[20] == trigref, (r[0], r[20])
assert f32s(7111) == (0.0, 1000.0, 0.0, 1.0)
assert f32s(7118) == (0.0, 1000.0, 255.0, 256.0)
# The configurable array starts at calculator 11; fixed IDs 1..4 are separate.
sc = raw(7120)
assert len(sc) == 55 * 92
assert struct.unpack_from('<I', sc, 0)[0] == 11

# Bank4 dictionary mechanically names IDs 5/6 as the two saturate outputs.
d = raw(3334); assert len(d) == 69 * 16
dict4 = {}
for i in range(69):
    data_id, zero, n, ref = struct.unpack_from('<4I', d, i*16)
    assert zero == 0
    dict4[data_id] = ids[ref]['text']
assert dict4[5] == 'SaturateStatsAvg'
assert dict4[6] == 'SaturateStatsRatio'

# Fixed calculator runtime binder: four successive 0x78 descriptors are bound
# to manager slots +18/+20/+28/+30.
bind = dis(0x1803f46d0, 0x1803f4a40)
for addr, cfg_off, slot in [
    (0x1803f46e8, '#0x28', '#0x18'),
    (0x1803f4804, '#0xa0', '#0x20'),
    (0x1803f4904, '#0x118', '#0x28'),
    (0x1803f4a20, '#0x190', '#0x30'),
]:
    line_has(bind, addr, 'add', 'x9, x22', cfg_off)
for addr, slot in [(0x1803f46f8,'#0x18'),(0x1803f4814,'#0x20'),
                   (0x1803f4914,'#0x28'),(0x1803f4a30,'#0x30')]:
    line_has(bind, addr, 'str', 'x0, [x19', slot)

# Bank4 storage is 16-byte records. Getter scalar = base+0x3e80+id*16+0x0c;
# setter/materializer copy the complete 16-byte {id,value,metadata...} record.
b4 = dis(0x1803d5ef8, 0x1803d5f28)
line_has(b4, 0x1803d5f04, 'add', 'x8, x0, w8, sxtw #4')
line_has(b4, 0x1803d5f0c, 'ldr', 's16, [x8, #0x3e8c]')
setter = dis(0x1803d6610, 0x1803d6654)
line_has(setter, 0x1803d6634, 'ldr', 'w9, [x19]')
line_has(setter, 0x1803d6640, 'ldr', 'q16, [x19]')
line_has(setter, 0x1803d6644, 'add', 'x9, x8, w9, sxtw #4')
line_has(setter, 0x1803d6648, 'mov', 'x8, #0x3e88')
line_has(setter, 0x1803d664c, 'str', 'q16, [x9, x8]')
mat = dis(0x1803f63d8, 0x1803f64c8)
line_has(mat, 0x1803f63dc, 'ldp', 'w9, w8, [x8, #0x3c]')
line_has(mat, 0x1803f63e0, 'add', 'w20, w9, w19')
line_has(mat, 0x1803f6484, 'add', 'x8, x8, #0x24')
line_has(mat, 0x1803f6488, 'ldr', 's16, [x21, x8, lsl #2]')
line_has(mat, 0x1803f64b8, 'add', 'x9, x8, w20, sxtw #4')
line_has(mat, 0x1803f64bc, 'mov', 'x8, #0x3e88')
line_has(mat, 0x1803f64c0, 'str', 'q16, [x9, x8]')

# API5 is the two-output range calculator; API6 is the one-output percentile
# mode. Both call the same histogram wrapper, but API5 passes mode w3=0.
api = dis(0x1803f5380, 0x1803f53c8)
line_has(api, 0x1803f5380, 'mov', 'w4, #0x0')
line_has(api, 0x1803f5384, 'mov', 'w3, #0x0')
line_has(api, 0x1803f5388, 'add', 'x2, x21, #0x90')
line_has(api, 0x1803f5394, 'bl', '0x1803f6808')
line_has(api, 0x1803f5398, 'mov', 'w20, #0x2')
line_has(api, 0x1803f53a8, 'mov', 'w3, #0x1')
line_has(api, 0x1803f53b8, 'bl', '0x1803f6808')
line_has(api, 0x1803f53bc, 'mov', 'w20, #0x1')

# API5 range kernel: raw uint32 counts at record+0x38, float value/luma axis
# at +0x40, bin count clamped to 1024. Mode zero takes the 0..256 coordinate
# branch, searches that supplied axis, accumulates uint32 counts, and stores two
# floats: interval weighted-average value and normalized interval mass.
rng = dis(0x1803ea548, 0x1803eaa00)
line_has(rng, 0x1803ea56c, 'mov', 'w8, #0x400')
line_has(rng, 0x1803ea570, 'ldp', 'x22, x23, [x9, #0x38]')
line_has(rng, 0x1803ea574, 'ldp', 'w10, w9, [x9, #0x14]')
line_has(rng, 0x1803ea580, 'csel', 'w21, w10, w8, lo')
line_has(rng, 0x1803ea598, 'cbz', 'w25, 0x1803ea72c')
line_has(rng, 0x1803ea72c, 'ldp', 's20, s18, [x24]')
line_has(rng, 0x1803ea738, 'ldr', 's19, 0x1803ea9fc')
line_has(rng, 0x1803ea76c, 'ldr', 's19, [x23, w8, uxtw #2]')
line_has(rng, 0x1803ea840, 'add', 'x7, x22, w10, uxtw #2')
line_has(rng, 0x1803ea85c, 'ldr', 'w8, [x7]')
line_has(rng, 0x1803ea864, 'ucvtf', 's17, w8')
line_has(rng, 0x1803ea99c, 'fdiv', 's18, s18, s16')
line_has(rng, 0x1803ea9c8, 'fsub', 's16, s17, s16')
line_has(rng, 0x1803ea9cc, 'stp', 's18, s16, [x19]')
# Literal at 0x1803ea9fc is exact float32 256.0f.
pe = pefile.PE(str(DLL), fast_load=True)
image = DLL.read_bytes()
def off_va(va): return pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)
assert struct.unpack_from('<I', image, off_va(0x1803ea9fc))[0] == 0x43800000

# PreprocessCoreStats builds the normalized CDF from the raw uint32 count array.
cdf = dis(0x1803f97e4, 0x1803f99d0)
line_has(cdf, 0x1803f97e4, 'ldr', 'x12, [x20, #0x38]')
line_has(cdf, 0x1803f97ec, 'ldr', 'x8, [x20, #0x40]')
line_has(cdf, 0x1803f9800, 'add', 'x10, x8, #0x148')
line_has(cdf, 0x1803f9804, 'ldr', 'w8, [x12]')
line_has(cdf, 0x1803f980c, 'ucvtf', 's16, w8')
line_has(cdf, 0x1803f9818, 'str', 's16, [x10]')
line_has(cdf, 0x1803f9898, 'ldr', 'w11, [x10, x8]')
line_has(cdf, 0x1803f98a0, 'ucvtf', 's17, w11')
line_has(cdf, 0x1803f98a4, 'fadd', 's16, s17, s16')
line_has(cdf, 0x1803f98bc, 'fmov', 's17, #1.00000000')
line_has(cdf, 0x1803f98d4, 'ldr', 's16, [x19, x10, lsl #2]')
line_has(cdf, 0x1803f98e8, 'fcmp', 's17, s16')
line_has(cdf, 0x1803f98ec, 'fcsel', 's16, s17, s16, gt')
# Vector body uses reciprocal estimate/Newton refinement; scalar tail uses FDIV.
line_has(cdf, 0x1803f9908, 'frecpe', 'v18.4s, v19.4s')
line_has(cdf, 0x1803f9910, 'frecps', 'v17.4s, v19.4s, v18.4s')
line_has(cdf, 0x1803f9984, 'fdiv', 's17, s17, s16')
line_has(cdf, 0x1803f99bc, 'fdiv', 's17, s17, s16')

# Existing Y authority pins the raw front BHist as 1024 x uint32 = 0x1000.
y = json.loads((BASE/'y-generation-tagged-3a-stats'/'RAW-AUTHORITY.json').read_text())
assert y['accepted'] is True
assert y['bhist'] == {
    'bins': 1024, 'bus_allocation_ceiling': 6144,
    'raw_bytes': 4096, 'raw_hex': '0x1000', 'raw_word_bytes': 4
}
# Pinned raw parser copies counts to a 0x1018 object, masking each raw word to
# 25 bits. Dual-source path masks both words then adds the two counts.
parser = dis(0x1805f4044, 0x1805f4110)
line_has(parser, 0x1805f4044, 'mov', 'x2, #0x1018')
line_has(parser, 0x1805f4094, 'ldr', 'w10, [x9, x6, lsl #2]')
line_has(parser, 0x1805f409c, 'and', 'w5, w10, #0x1ffffff')
line_has(parser, 0x1805f40a4, 'str', 'w5, [x19, x10, lsl #2]')
line_has(parser, 0x1805f40e4, 'ldr', 'w11, [x10, x4, lsl #2]')
line_has(parser, 0x1805f40ec, 'and', 'w5, w11, #0x1ffffff')
line_has(parser, 0x1805f40f0, 'ldr', 'w11, [x9, x4, lsl #2]')
line_has(parser, 0x1805f40f4, 'and', 'w11, w11, #0x1ffffff')
line_has(parser, 0x1805f40f8, 'add', 'w5, w5, w11')
# Parser object constructor explicitly configures 0x400 bins.
create = dis(0x180a06d30, 0x180a06d58)
line_has(create, 0x180a06d44, 'mov', 'w8, #0x400')
line_has(create, 0x180a06d48, 'str', 'w8, [x19, #0xe8]')

result = {
    'schema': 'sp11-e003i-cs-windows-aec-bhist-bright-ratio-v1',
    'accepted': True,
    'dll_sha256': DLL_SHA,
    'tuning_sha256': TUNING_SHA,
    'fixed_calculators': [
        {'id':1,'description':'AvgLumaBE16x16','api':1,'channel':'LumaBE16x16','bank4':[1,1]},
        {'id':2,'description':'FrameLuma','api':1,'channel':'LumaBE16x16','bank4':[2,2]},
        {'id':3,'description':'DarkRatio','api':5,'channel':'BhistY','bank4':[3,4],'range':[0.0,1.0]},
        {'id':4,'description':'BrightRatio','api':5,'channel':'BhistY','bank4':[5,6],'range':[255.0,256.0]},
    ],
    'bank4_6': {
        'name': 'SaturateStatsRatio',
        'producer': 'fixed calculator 4 BrightRatio API5 output lane 1',
        'range': [255.0, 256.0],
    },
    'bhist_raw': {'bins':1024,'word_bytes':4,'raw_bytes':4096,'parser_mask':'0x01ffffff'},
    'cdf': {
        'input': 'record+0x38 uint32 counts',
        'storage': 'per-source +0x148 float32 cumulative array',
        'denominator': 'max(1.0f, final cumulative count)',
        'normalization': 'SIMD reciprocal-estimate/Newton body plus scalar FDIV tail',
    },
    'value_axis': {
        'input': 'record+0x40 float32 per-bin value/luma coordinate array',
        'consumer_proven': True,
        'producer_proven': False,
        'status': 'DEFERRED_TO_CT',
    },
    'safety': {'offline_only':True,'linux_camera_runtime':False,'windows_oracle_new':False},
    'status': 'PASS',
}
(HERE/'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print('DLL_SHA256=' + DLL_SHA)
print('TUNING_SHA256=' + TUNING_SHA)
print('FIXED_CALC_4=BrightRatio API5 BhistY -> Bank4:5..6')
print('BANK4_6=SaturateStatsRatio = BrightRatio[255,256].ratio')
print('BHIST_RAW=1024xuint32 parser-mask=0x01ffffff')
print('CDF=uint32 cumulative-f32 / max(1,final)')
print('VALUE_AXIS=record+0x40 float32 consumer-proven producer=DEFERRED_TO_CT')
print('CS_VERIFY=PASS')
