#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TRANSPORT = ROOT / 'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
CDM = TRANSPORT / 'windows-ife-cdm'
PRIME = TRANSPORT / 'vfe1-epoch0-priming-replay-oracle.json'
ORDER = TRANSPORT / 'windows-startup-priming-interleave/startup-priming-interleave-oracle.json'
DLL = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
DLL_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
DLL_BYTES = 23998368

# Ghidra read-only analysis facts for the SHA-pinned Surface binary.  The 0x100-byte
# hashes pin the exact code bodies from which the record strides/packing were read.
FUNCS = {
    'awb_parser':       (0x5efa00, '3a62c50ea66f1a085b41a686c133e7c2029f643c8c0bce137a74f5282d3b5440'),
    'awb_raw_single':   (0x5f1d70, '7ec7615ed4972621588b67427699f5b7b2ecaeaa6f486349522d16822d981755'),
    'aec_parser':       (0x5f6158, '7a97ec360984992ea30f343e88d85fe0b057245a234b3b13fe61634182130f52'),
    'aec_raw_single':   (0x5f6600, '310e3907a37a417b14d940e36eb6c6e4cad070797d3dc3dc772eebd1739c99ac'),
    'bhist_parser':     (0x5f3c60, '90f4e84561fd8928aca9e5b2257496340d620f5b3d3914289fd35b04d3594bc1'),
    'bhist_create':     (0xa06cc0, '903ddf2b7d4592a2dc629991561114ac72d226ab6129383db0de4acbff9762f4'),
    'awb_pack':         (0xb39950, '9d8ff730fb88c5a979d102b6e84ae8c214855539ace331fd0968dd51db3c68d8'),
    'aec_pack':         (0xb3f860, '8047bfce4327cd176a6b1bc6f21ef714bb23505c69bdefbd90c5ef00c0ccc6d9'),
}

def need(v, msg):
    if not v: raise RuntimeError(msg)

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

def pe_rva_offset(data: bytes, rva: int) -> int:
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    need(data[pe:pe+4] == b'PE\0\0', 'PE signature drift')
    nsec = struct.unpack_from('<H', data, pe + 6)[0]
    opt = struct.unpack_from('<H', data, pe + 20)[0]
    sec = pe + 24 + opt
    for i in range(nsec):
        o = sec + i * 40
        vsize, va, rsize, roff = struct.unpack_from('<IIII', data, o + 8)
        if va <= rva < va + max(vsize, rsize):
            return roff + rva - va
    raise RuntimeError(f'RVA not mapped: {rva:#x}')

def writes(packet: int) -> dict[int, list[int]]:
    p = CDM / f'packet{packet}-register-writes.csv'
    out: dict[int, list[int]] = {}
    with p.open(newline='') as f:
        for r in csv.DictReader(f):
            off = int(r['register_offset'], 16)
            out.setdefault(off, []).append(int(r['value'], 16))
    return out

def one(m, off):
    v = m.get(off, [])
    need(len(v) == 1, f'expected one write to {off:#x}, got {v}')
    return v[0]

data = DLL.read_bytes()
need(len(data) == DLL_BYTES and sha(data) == DLL_SHA, 'DeviceMFT identity drift')
for name, (rva, expected) in FUNCS.items():
    o = pe_rva_offset(data, rva)
    need(sha(data[o:o+0x100]) == expected, f'{name} code slice drift')

p = [writes(i) for i in range(4)]
# Titan680 AWB/AEC packers encode (num-1) in bits 16..21 of H/V config words.
awb_h = ((one(p[1], 0xb86c) >> 16) & 0x3f) + 1
awb_v = ((one(p[1], 0xb874) >> 16) & 0x3f) + 1
aec_h = ((one(p[1], 0xb06c) >> 16) & 0x3f) + 1
aec_v = ((one(p[1], 0xb074) >> 16) & 0x3f) + 1
need((awb_h, awb_v) == (64, 48), f'AWB geometry drift {(awb_h, awb_v)}')
need((aec_h, aec_v) == (32, 32), f'AEC geometry drift {(aec_h, aec_v)}')
# Packet1 is the last startup write to these blocks; packet2/3 do not rewrite them.
for i in (2, 3):
    need(not any(0xb060 <= x <= 0xb080 for x in p[i]), f'packet{i} rewrites AEC block')
    need(not any(0xb860 <= x <= 0xb8a4 for x in p[i]), f'packet{i} rewrites AWB block')

prime = json.loads(PRIME.read_text())
order = json.loads(ORDER.read_text())
need(prime['accepted'] is True, 'priming oracle not accepted')
need(prime['replay']['only_difference_vs_startup_each_packet'] == 'one period_cfg +0x8c dword',
     'priming replay equivalence drift')
need(order['exact_pre_csid_order'] == [
    'startup packet0','priming replay0','startup packet1','BUS config','BUS enable',
    'initial BUS addresses','priming replay1','startup packet2','startup packet3','CSID1 start'],
    'startup/priming order drift')

# Static parser facts from the pinned function bodies above.
aec_record = 0x50
awb_record = 0x50
bhist_bins = 0x400
bhist_word = 4
aec_bytes = aec_h * aec_v * aec_record
awb_bytes = awb_h * awb_v * awb_record
bhist_bytes = bhist_bins * bhist_word
need(aec_bytes == 0x14000, 'AEC size math drift')
need(awb_bytes == 0x3c000, 'AWB size math drift')
need(bhist_bytes == 0x1000, 'BHist size math drift')
need(aec_bytes + bhist_bytes + awb_bytes == 0x51000, 'bundle size math drift')

result = {
  'schema':'sp11-e003i-y-3a-raw-authority-v1', 'accepted':True,
  'device_mft':{'bytes':DLL_BYTES,'sha256':DLL_SHA,'function_slices_0x100':{k:{'rva':hex(v[0]),'sha256':v[1]} for k,v in FUNCS.items()}},
  'route':{'front':'single IFE1/VFE1 PIX path','dual_ife_raw_layout_not_used':True},
  'aec_be':{'horizontal_regions':aec_h,'vertical_regions':aec_v,'regions':aec_h*aec_v,'raw_record_bytes':aec_record,'raw_bytes':aec_bytes,'raw_hex':hex(aec_bytes),'bus_allocation_ceiling':0xa0000},
  'bhist':{'bins':bhist_bins,'raw_word_bytes':bhist_word,'raw_bytes':bhist_bytes,'raw_hex':hex(bhist_bytes),'bus_allocation_ceiling':0x1800},
  'awb_bg':{'horizontal_regions':awb_h,'vertical_regions':awb_v,'regions':awb_h*awb_v,'raw_record_bytes':awb_record,'raw_bytes':awb_bytes,'raw_hex':hex(awb_bytes),'bus_allocation_ceiling':0x151800},
  'bundle':{'raw_bytes':aec_bytes+bhist_bytes+awb_bytes,'raw_hex':hex(aec_bytes+bhist_bytes+awb_bytes),'order':['AEC_BE','BHIST','AWB_BG']},
  'startup':{'packet1_aec_h':hex(one(p[1],0xb06c)),'packet1_aec_v':hex(one(p[1],0xb074)),'packet1_awb_h':hex(one(p[1],0xb86c)),'packet1_awb_v':hex(one(p[1],0xb874)),'packet2_3_no_aec_awb_rewrite':True,'priming_replays_equal_startup_except_period_cfg':True},
  'safety':{'offline_only':True,'linux_camera_runtime':False,'new_hardware_assumption':False}
}
(HERE/'RAW-AUTHORITY.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
