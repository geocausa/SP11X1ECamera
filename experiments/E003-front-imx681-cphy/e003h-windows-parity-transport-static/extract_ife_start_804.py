#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

EXPECTED_SHA256 = '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
EXPECTED_BUS_ORACLE_SHA256 = '126599031f6b8e611f7f9930b2239edbfccbcee2f2d988f47a78b46e5786d927'
IMAGE_BASE = 0x140000000
TEXT_RAW = 0x400
TEXT_RVA = 0x1000
TEXT_SIZE = 0x3d48c
LOG_BYTES = 3180
LOG_SHA256 = '3b72a57e9c4b4568d66118f171690df476f4b1cbf4aaad159f46fbdc581acbfd'
LOG_MARKER = 'EV IFE_START804 id=1 usecase=2 skip=0'


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('binary', type=Path)
    ap.add_argument('--log', type=Path, required=True)
    ap.add_argument('--bus-oracle', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()

    data = a.binary.read_bytes()
    binary_sha = sha256(data)
    if binary_sha != EXPECTED_SHA256 or len(data) != 376560:
        die('qccamisp identity drift')

    raw_log = a.log.read_bytes()
    if len(raw_log) != LOG_BYTES or sha256(raw_log) != LOG_SHA256:
        die('IFE start dynamic log identity drift')
    text_log = raw_log.decode('utf-16')
    markers = [line.strip() for line in text_log.splitlines()
               if line.strip().startswith('EV IFE_START804')]
    if markers != [LOG_MARKER]:
        die('IFE start dynamic marker drift: ' + repr(markers))

    bus_bytes = a.bus_oracle.read_bytes()
    bus_sha = sha256(bus_bytes)
    if bus_sha != EXPECTED_BUS_ORACLE_SHA256:
        die('VFE1 BUS oracle identity drift')
    bus = json.loads(bus_bytes)

    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    md.skipdata = True
    ins = {i.address - IMAGE_BASE: i for i in md.disasm(
        data[TEXT_RAW:TEXT_RAW + TEXT_SIZE], IMAGE_BASE + TEXT_RVA)
        if i.mnemonic != '.byte'}

    def need(rva, mnemonic=None, contains=None):
        i = ins.get(rva)
        if not i:
            die(f'missing instruction 0x{rva:x}')
        if mnemonic and i.mnemonic != mnemonic:
            die(f'0x{rva:x}: expected {mnemonic}, got {i.mnemonic}')
        if contains and contains not in i.op_str:
            die(f'0x{rva:x}: expected {contains!r}, got {i.op_str!r}')
        return i

    pe = pefile.PE(data=data)

    def cstr(rva, limit=256):
        off = pe.get_offset_from_rva(rva)
        return data[off:off + limit].split(b'\0', 1)[0].decode('ascii')

    # ISP-manager DEVICE_START dispatch into each active IFE resource.
    need(0x15fd8, 'mov', 'w1, #0x804')
    need(0x15fec, 'blr', 'x15')

    # Exact IFE command dispatcher and 0x804 branch.
    need(0x22cd0, 'pacibsp')
    need(0x23604, 'cmp', 'w1, #0x804')
    need(0x23608, 'b.eq', '#0x14002366c')
    need(0x2366c, 'cbz', 'x21')
    need(0x23670, 'ldr', 'w3, [x21, #4]')
    need(0x2367c, 'ldr', 'w2, [x19, #0x120]')
    need(0x23688, 'str', 'w3, [x19, #0x348c]')
    need(0x2368c, 'ldr', 'w4, [x21]')
    need(0x23690, 'str', 'w4, [x19, #0x3490]')
    need(0x23694, 'bl', '#0x140029ad8')

    fmt_rva = 0x39248
    fmt = cstr(fmt_rva)
    expected_fmt = 'IFE%d: Camera use case is %d, number of frames to skip is %d.'
    if fmt != expected_fmt:
        die('IFE 0x804 diagnostic string drift')

    # The branch itself has no hardware access: two state stores plus diagnostics.
    branch = []
    calls = []
    stores = []
    for rva in range(0x2366c, 0x23698, 4):
        i = ins.get(rva)
        if not i:
            die(f'0x804 branch hole at 0x{rva:x}')
        branch.append(f'0x{rva:x}: {i.mnemonic} {i.op_str}')
        if i.mnemonic in ('bl', 'blr'):
            calls.append(rva)
        if i.mnemonic in ('str', 'stur', 'stp'):
            stores.append((rva, i.op_str))
    if calls != [0x23694]:
        die('unexpected 0x804 branch call topology')
    if stores != [
        (0x23688, 'w3, [x19, #0x348c]'),
        (0x23690, 'w4, [x19, #0x3490]'),
    ]:
        die('unexpected 0x804 branch store topology')

    # Prove these are the only reads of the two object fields in the whole .text.
    xrefs = []
    for rva, i in sorted(ins.items()):
        if '#0x348c' in i.op_str or '#0x3490' in i.op_str:
            xrefs.append((rva, i.mnemonic, i.op_str))
    expected_xrefs = [
        (0x1c554, 'ldr', 'w8, [x19, #0x348c]'),
        (0x1c564, 'ldr', 'w24, [x19, #0x3490]'),
        (0x1e05c, 'ldr', 'w8, [x19, #0x348c]'),
        (0x1e068, 'ldr', 'w3, [x19, #0x3490]'),
        (0x23688, 'str', 'w3, [x19, #0x348c]'),
        (0x23690, 'str', 'w4, [x19, #0x3490]'),
    ]
    if xrefs != expected_xrefs:
        die('0x804 object-field xref set drift: ' + repr(xrefs))

    # IFELite IO configuration: only use-case 4 derives frame-drop state from
    # frames_to_skip.  Other use-cases load per-resource pattern/period fields.
    need(0x1c554, 'ldr', 'w8, [x19, #0x348c]')
    need(0x1c55c, 'cmp', 'w8, #4')
    need(0x1c560, 'b.ne', '#0x14001c598')
    need(0x1c564, 'ldr', 'w24, [x19, #0x3490]')
    need(0x1c580, 'lsl', 'w25, w13, w24')
    need(0x1c598, 'add', 'x17, x20, #0x104')
    need(0x1c59c, 'ldp', 'w25, w24, [x17]')
    need(0x1c734, 'ldr', 'w8, [x19, #0x3428]')
    need(0x1c73c, 'str', 'w24, [x12, w8, uxtw]')
    need(0x1c74c, 'ldr', 'w8, [x19, #0x342c]')
    need(0x1c754, 'str', 'w25, [x12, w8, uxtw]')

    if cstr(0x36770) != 'IFELite %d IFEPortID %d, frameDropPeriod = 0x%x':
        die('IFELite frameDropPeriod string drift')
    if cstr(0x367a0) != 'IFELite %d IFEPortID %d, frameDropPattern = 0x%x':
        die('IFELite frameDropPattern string drift')

    # Full IFE IO/BUS configuration used by VFE1.  The same use-case-4-only
    # override exists; normal use-case 2 falls through to resource +0x104/+0x108.
    need(0x1e05c, 'ldr', 'w8, [x19, #0x348c]')
    need(0x1e060, 'cmp', 'w8, #4')
    need(0x1e064, 'b.ne', '#0x14001e09c')
    need(0x1e068, 'ldr', 'w3, [x19, #0x3490]')
    need(0x1e080, 'lsl', 'w2, w10, w3')
    need(0x1e09c, 'add', 'x17, x21, #0x104')
    need(0x1e0a0, 'ldp', 'w2, w3, [x17]')
    need(0x1e0a4, 'stp', 'w3, w2, [sp, #0x14]')
    need(0x1e424, 'ldr', 'w8, [x19, #0x3428]')
    need(0x1e428, 'ldr', 'w3, [sp, #0x14]')
    need(0x1e42c, 'str', 'w3, [x10, w8, uxtw]')
    need(0x1e440, 'ldr', 'w8, [x19, #0x342c]')
    need(0x1e444, 'ldr', 'w2, [sp, #0x18]')
    need(0x1e448, 'str', 'w2, [x10, w8, uxtw]')

    if cstr(0x37128) != 'IFE %d IFEPortID %d, frameDropPeriod = 0x%x, index=%d':
        die('IFE frameDropPeriod string drift')
    if cstr(0x37160) != 'IFE %d IFEPortID %d, frameDropPattern = 0x%x,index=%d':
        die('IFE frameDropPattern string drift')

    # Cross-check the same-machine VFE1 BUS oracle: every active client in this
    # front session has the normal use-case-2 frame-drop state 0/1.
    static_sets = [
        bus['full_qc10c']['client0_full_y_static'],
        bus['full_qc10c']['client1_full_c_static'],
        bus['ds']['client2_ds4_static'],
        bus['ds']['client3_ds16_static'],
    ] + [bus['stats'][str(i)] for i in (11, 12, 13, 14, 18)]
    if len(static_sets) != 9:
        die('unexpected VFE1 BUS active-client count')
    for idx, s in enumerate(static_sets):
        if s['framedrop_period'] != '0x00000000':
            die(f'client {idx} frame-drop period drift')
        if s['framedrop_pattern'] != '0x00000001':
            die(f'client {idx} frame-drop pattern drift')

    out = {
        'schema': 'sp11-e003h-windows-ife-start-804-v2',
        'accepted': True,
        'source': {'driver': a.binary.name, 'bytes': len(data), 'sha256': binary_sha},
        'manager': {
            'device_start_ife_call_rva': '0x15fec',
            'opcode': '0x804',
        },
        'ife_dispatcher': {
            'function_rva': '0x22cd0',
            'opcode_branch_rva': '0x2366c',
            'branch_instructions': branch,
        },
        'dynamic_same_machine': {
            'raw_log': a.log.name,
            'bytes': len(raw_log),
            'sha256': sha256(raw_log),
            'ife1_marker': LOG_MARKER,
            'camera_use_case': 2,
            'frames_to_skip': 0,
        },
        'payload': {
            'word0': 'number of frames to skip',
            'word1': 'camera use case',
            'object_frames_to_skip_offset': '0x3490',
            'object_camera_use_case_offset': '0x348c',
            'diagnostic_format': fmt,
        },
        'object_field_xrefs': [
            {'rva': f'0x{rva:x}', 'mnemonic': mnemonic, 'op_str': op_str}
            for rva, mnemonic, op_str in xrefs
        ],
        'hardware_action': {
            'direct_mmio_in_0x804_branch': False,
            'hardware_start_call_in_0x804_branch': False,
            'only_call': 'diagnostic/log helper RVA 0x29ad8',
            'classification': 'logical start-state capture; not a hardware-start primitive',
        },
        'downstream_semantics': {
            'only_consumers': [
                'IFELite IO configuration RVA 0x1c554',
                'full IFE IO/BUS configuration RVA 0x1e05c',
            ],
            'override_condition': 'camera_use_case == 4 only',
            'override_rule': 'frameDropPeriod=frames_to_skip; frameDropPattern=(1 << frames_to_skip)',
            'front_use_case_2_override_taken': False,
            'front_frames_to_skip_consumed': False,
            'normal_resource_fields': {
                'resource_plus_0x108': 'frameDropPeriod',
                'resource_plus_0x104': 'frameDropPattern',
            },
            'vfe1_bus_oracle': {
                'file': a.bus_oracle.name,
                'sha256': bus_sha,
                'active_clients': 9,
                'all_framedrop_period': '0x00000000',
                'all_framedrop_pattern': '0x00000001',
            },
        },
        'linux_consequence': (
            'Do not add a synthetic IFE-start MMIO write or a new runtime stage for opcode 0x804. '
            'The normal front session is camera use-case 2, so frames_to_skip=0 is not consumed by '
            'either downstream IO/BUS path. Both paths use the ordinary per-resource frame-drop '
            'fields, and the same-machine VFE1 BUS oracle already proves 0/1 for all nine active '
            'clients; the retained Linux BUS recipe already represents that state. The missing '
            'Epoch0 must therefore be sought in another VFE1/CSID/ingress prerequisite.'
        ),
        'runtime_authorized': False,
    }
    text = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(text)
    else:
        print(text, end='')
    print('PASS: IFE start 0x804 is logical-only; front use-case 2 does not consume frames_to_skip')


if __name__ == '__main__':
    main()
