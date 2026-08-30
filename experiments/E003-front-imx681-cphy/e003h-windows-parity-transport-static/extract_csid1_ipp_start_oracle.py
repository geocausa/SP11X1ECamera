#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

EXPECTED_DRIVER_SHA256 = '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
EXPECTED_DRIVER_BYTES = 376560
EXPECTED_COMPANION_SHA256 = '3d9d1beb74641c8e699f045abcc79384c52d5365780dd3134a99ab0dbd42e194'
EXPECTED_COMPANION_BYTES = 136290
EXPECTED_ROUTE_SHA256 = 'fd8edcee46e794dffa0e2305331f19d4e9d2cd5b9ba5197484aa1cc7fa6c6fca'
EXPECTED_ROUTE_BYTES = 2457712
IMAGE_BASE = 0x140000000
TEXT_RAW = 0x400
TEXT_RVA = 0x1000
TEXT_SIZE = 0x3d48c
CSID1_BASE = 0x0acb9000
WRAPPER_BASE = 0x0acb6000

DD = re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+((?:[0-9a-f]{8}\s+){3}[0-9a-f]{8})$', re.I)
DB = re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+((?:[0-9a-f]{2}\s+){7}[0-9a-f]{2})-((?:[0-9a-f]{2}\s+){7}[0-9a-f]{2})', re.I)
EVAL = re.compile(r'^Evaluate expression: .* = ([0-9a-f]{8})`([0-9a-f]{8})$', re.I)
ROUTE_LINE = re.compile(
    r'^([0-9a-f]{8})`([0-9a-f]{8})\s+'
    r'([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s*$',
    re.I | re.M,
)


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def dwords(lines):
    out = {}
    for line in lines:
        m = DD.match(line)
        if not m:
            continue
        addr = int(m.group(1) + m.group(2), 16)
        for i, value in enumerate(m.group(3).split()):
            out[addr + 4 * i] = int(value, 16)
    return out


def dump_window(lines, base, size):
    data = bytearray(size)
    seen = bytearray(size)
    for line in lines:
        m = DB.match(line)
        if not m:
            continue
        addr = int(m.group(1) + m.group(2), 16)
        if not base <= addr < base + size:
            continue
        chunk = bytes(int(x, 16) for x in (m.group(3) + ' ' + m.group(4)).split())
        off = addr - base
        take = min(len(chunk), size - off)
        data[off:off + take] = chunk[:take]
        seen[off:off + take] = b'\1' * take
    if not all(seen):
        die(f'incomplete KD byte window at 0x{base:x}, size 0x{size:x}')
    return bytes(data)


def decode_reg_cont(stream):
    pos = 0
    writes = []
    commands = []
    while pos < len(stream):
        if pos + 8 > len(stream):
            die('truncated CSID companion command header')
        word0, reg = struct.unpack_from('<II', stream, pos)
        opcode = word0 >> 24
        count = word0 & 0xffff
        if opcode != 3 or count == 0:
            die(f'unexpected CSID companion opcode/count at 0x{pos:x}: 0x{word0:08x}')
        need = 8 + 4 * count
        if pos + need > len(stream):
            die('truncated CSID REG_CONT command')
        reg &= 0xffffff
        vals = list(struct.unpack_from('<' + 'I' * count, stream, pos + 8))
        commands.append({
            'stream_offset': f'0x{pos:x}',
            'opcode': opcode,
            'count': count,
            'register_offset': f'0x{reg:03x}',
            'values': [f'0x{v:08x}' for v in vals],
        })
        for i, val in enumerate(vals):
            writes.append((reg + 4 * i, val))
        pos += need
    if pos != len(stream):
        die('CSID companion decode length mismatch')
    return commands, writes


def parse_companion(raw):
    text = raw.decode('utf-16')
    lines = text.splitlines()
    marker = '===E003H_COMPANION_803==='
    marks = [i for i, line in enumerate(lines) if line == marker]
    if len(marks) != 4:
        die(f'expected four CSID companion 0x803 captures, got {len(marks)}')

    packets = []
    expected_used = [0x3c, 0x10, 0x10, 0x10]
    expected_writes = [
        [(0x330, 0), (0x37c, 1), (0x380, 0),
         (0x35c, 0x0eff0000), (0x360, 0x086f0000),
         (0x384, 0x0000001f), (0x388, 0x08700f00)],
        [(0x35c, 0x0eff0000), (0x360, 0x086f0000)],
        [(0x35c, 0x0eff0000), (0x360, 0x086f0000)],
        [(0x35c, 0x0eff0000), (0x360, 0x086f0000)],
    ]

    for pi, mark in enumerate(marks):
        block = lines[mark:marks[pi + 1] if pi + 1 < len(marks) else len(lines)]
        xline = next((line for line in block if line.startswith('x2=')), None)
        if not xline:
            die(f'packet {pi}: missing x2 marker')
        xm = re.search(r'x2=([0-9a-f]+)\s+x8=([0-9a-f]+)', xline, re.I)
        if not xm:
            die(f'packet {pi}: malformed x2/x8 marker')
        x2 = int(xm.group(1), 16)
        dw = dwords(block)
        if dw.get(x2 + 8) != pi or dw.get(x2 + 0x1c) != 3:
            die(f'packet {pi}: outer packet identity drift')

        b = x2 + 0x94  # descriptor 1
        handle = dw.get(b, 0) | (dw.get(b + 4, 0) << 32)
        desc = {
            'index': 1,
            'handle': f'0x{handle:016x}',
            'offset': dw.get(b + 8),
            'capacity': dw.get(b + 0xc),
            'used_length': dw.get(b + 0x10),
            'flags': dw.get(b + 0x14),
            'type': dw.get(b + 0x18),
        }
        if desc['used_length'] != expected_used[pi] or desc['type'] != 0x12:
            die(f'packet {pi}: descriptor-1 identity drift: {desc!r}')

        evals = []
        for line in block:
            m = EVAL.match(line)
            if m:
                evals.append(int(m.group(1) + m.group(2), 16))
        if len(evals) != 2:
            die(f'packet {pi}: expected descriptor1/2 evaluate addresses, got {len(evals)}')
        cpu = evals[0]
        window = dump_window(block, cpu, 0x40)
        stream = window[:desc['used_length']]
        commands, writes = decode_reg_cont(stream)
        if writes != expected_writes[pi]:
            die(f'packet {pi}: CSID1 IPP companion writes drift: {writes!r}')
        packets.append({
            'packet': pi,
            'descriptor': desc,
            'mapped_cpu_va': f'0x{cpu:016x}',
            'used_sha256': sha256(stream),
            'commands': commands,
            'writes': [
                {'register_offset': f'0x{off:03x}', 'value': f'0x{val:08x}'}
                for off, val in writes
            ],
        })
    return packets


def parse_route_dump(text, phase, region, base, size):
    begin = f'===E003G3_{phase}_{region.upper()}_BEGIN==='
    end = f'===E003G3_{phase}_{region.upper()}_END==='
    if begin not in text or end not in text:
        die(f'missing route marker pair {begin}/{end}')
    body = text.rsplit(begin, 1)[1].split(end, 1)[0]
    out = {}
    for m in ROUTE_LINE.finditer(body):
        addr = int(m.group(1) + m.group(2), 16)
        for i in range(4):
            out[addr + 4 * i] = int(m.group(3 + i), 16)
    if len(out) != size // 4:
        die(f'{phase}/{region}: expected {size // 4} route dwords, got {len(out)}')
    if min(out) != base or max(out) != base + size - 4:
        die(f'{phase}/{region}: route address window drift')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('binary', type=Path)
    ap.add_argument('--companion-log', type=Path, required=True)
    ap.add_argument('--route-log', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    args = ap.parse_args()

    data = args.binary.read_bytes()
    if len(data) != EXPECTED_DRIVER_BYTES or sha256(data) != EXPECTED_DRIVER_SHA256:
        die('qccamisp8380 identity drift')
    companion = args.companion_log.read_bytes()
    if len(companion) != EXPECTED_COMPANION_BYTES or sha256(companion) != EXPECTED_COMPANION_SHA256:
        die('CSID companion KD log identity drift')
    route_raw = args.route_log.read_bytes()
    if len(route_raw) != EXPECTED_ROUTE_BYTES or sha256(route_raw) != EXPECTED_ROUTE_SHA256:
        die('same-machine route oracle identity drift')

    pe = pefile.PE(data=data)
    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    md.skipdata = True
    ins = {
        i.address - IMAGE_BASE: i
        for i in md.disasm(data[TEXT_RAW:TEXT_RAW + TEXT_SIZE], IMAGE_BASE + TEXT_RVA)
        if i.mnemonic != '.byte'
    }

    def need(rva, mnemonic=None, contains=None):
        i = ins.get(rva)
        if not i:
            die(f'missing instruction at 0x{rva:x}')
        if mnemonic and i.mnemonic != mnemonic:
            die(f'0x{rva:x}: expected {mnemonic}, got {i.mnemonic}')
        if contains and contains not in i.op_str:
            die(f'0x{rva:x}: expected {contains!r}, got {i.op_str!r}')
        return i

    def u32_rva(rva):
        off = pe.get_offset_from_rva(rva)
        return struct.unpack_from('<I', data, off)[0]

    # Full-CSID initial configuration builder. These are direct MMIO writes.
    need(0x1a870, 'pacibsp')
    need(0x1a9a0, 'ldr', 'w8, #0x14001b3c0')
    need(0x1a9a4, 'str', 'w8, [x9, #0xa0]')
    need(0x1a9ac, 'mov', 'w8, #0x1ffff')
    need(0x1a9b0, 'str', 'w8, [x9, #0x90]')
    need(0x1aa38, 'ldr', 'w8, #0x14001b3c4')
    need(0x1aa3c, 'str', 'w8, [x9, #0x334]')
    need(0x1ab1c, 'str', 'w9, [x8, #0x310]')
    need(0x1ab24, 'str', 'wzr, [x8, #0x324]')
    if u32_rva(0x1b3c0) != 0x019fb800:
        die('Windows CSID RX IRQ mask literal drift')
    if u32_rva(0x1b3c4) != 0x00130013:
        die('Windows IPP epoch IRQ literal drift')

    # CSID path-enable HAL. Path 5 is IPP.
    need(0x1b3d0, 'pacibsp')
    need(0x1b410, 'cmp', 'w3, #5')
    need(0x1b414, 'b.eq', '#0x14001b48c')
    need(0x1b4b8, 'str', 'w11, [x8, #0x304]')
    need(0x1b4c0, 'ldr', 'w8, #0x14001b5e0')
    need(0x1b4c4, 'str', 'w8, [x9, #0xb0]')
    need(0x1b4cc, 'str', 'w11, [x8, #0x80]')
    if u32_rva(0x1b5e0) != 0x3cbc601c:
        die('Windows CSID IPP IRQ mask literal drift')

    # CSID command dispatcher. Unlike IFE 0x804, zero skip calls DAL_csid_start.
    need(0x218d8, 'cmp', 'w1, #0x804')
    need(0x218dc, 'b.eq', '#0x140021b4c')
    need(0x21b50, 'ldr', 'w8, [x21, #4]')
    need(0x21b54, 'str', 'w8, [x19, #0x190]')
    need(0x21b58, 'ldr', 'w8, [x21]')
    need(0x21b5c, 'str', 'w8, [x19, #0x114]')
    need(0x21b60, 'cbnz', 'w8, #0x140021b70')
    need(0x21b68, 'bl', '#0x140024260')

    # DAL_csid_start iterates every active path and calls the path-enable callback.
    need(0x24260, 'pacibsp')
    need(0x2427c, 'ldrb', 'w8, [x19, #0x1e4]')
    need(0x2429c, 'add', 'x8, x21, #0x72')
    need(0x242a0, 'ldr', 'w3, [x19, x8, lsl #2]')
    need(0x242d4, 'mov', 'w1, #5')
    need(0x242e0, 'ldr', 'x8, [x19, #0x218]')
    need(0x242f8, 'blr', 'x15')

    packets = parse_companion(companion)

    route_text = route_raw.decode('utf-16', errors='replace')
    w1 = parse_route_dump(route_text, 'LIVE1', 'wrapper', WRAPPER_BASE, 0x1000)
    w2 = parse_route_dump(route_text, 'LIVE2', 'wrapper', WRAPPER_BASE, 0x1000)
    c1 = parse_route_dump(route_text, 'LIVE1', 'csid1', CSID1_BASE, 0x2000)
    c2 = parse_route_dump(route_text, 'LIVE2', 'csid1', CSID1_BASE, 0x2000)

    expected_stable = {
        0x080: 0x00000001,
        0x090: 0x0001ffff,
        0x0a0: 0x019fb800,
        0x0b0: 0x3cbc601c,
        0x200: 0x11300000,
        0x204: 0x00000001,
        0x300: 0x802b2000,
        0x304: 0x00000001,
        0x310: 0x00007241,
        0x324: 0x00000000,
        0x328: 0xffff0000,
        0x32c: 0xffff0000,
        0x330: 0x00000000,
        0x334: 0x00130013,
        0x338: 0xffffffff,
        0x33c: 0xffffffff,
        0x35c: 0x0eff0000,
        0x360: 0x086f0000,
        0x364: 0x00000000,
        0x368: 0x00000001,
        0x36c: 0x00000000,
        0x370: 0x00000001,
        0x374: 0x00000000,
        0x378: 0x00000001,
        0x37c: 0x00000001,
        0x380: 0x00000000,
        0x384: 0x0000001f,
        0x388: 0x08700f00,
    }
    for off, val in expected_stable.items():
        got1 = c1[CSID1_BASE + off]
        got2 = c2[CSID1_BASE + off]
        if got1 != val or got2 != val:
            die(f'Windows live CSID1 +0x{off:x} drift: 0x{got1:08x}/0x{got2:08x}')

    if w1[WRAPPER_BASE + 4] != 0x00000101 or w2[WRAPPER_BASE + 4] != 0x00000101:
        die('Windows CSID1 wrapper route drift')

    # Classify values that must remain telemetry/readback, not replay inputs.
    if c1[CSID1_BASE + 0x340] != c2[CSID1_BASE + 0x340]:
        # This capture happened to be stable, but static ISR proves +0x340 is status.
        pass
    need(0x1b6d4, 'ldr', 'w8, [x8, #0x340]')
    need(0x1b7fc, 'ldr', 'w9, [x8, #0x398]')
    need(0x1b804, 'ldr', 'w8, [x8, #0x39c]')

    oracle = {
        'schema': 'sp11-e003h-windows-csid1-ipp-start-v1',
        'accepted': True,
        'source': {
            'driver': args.binary.name,
            'bytes': len(data),
            'sha256': sha256(data),
            'companion_log': args.companion_log.name,
            'companion_bytes': len(companion),
            'companion_sha256': sha256(companion),
            'route_log': args.route_log.name,
            'route_bytes': len(route_raw),
            'route_sha256': sha256(route_raw),
        },
        'windows_csid_0x804': {
            'dispatcher_opcode_compare_rva': '0x218d8',
            'branch_rva': '0x21b4c',
            'payload_word0': 'number of frames to skip',
            'payload_word1': 'camera use case',
            'zero_skip_calls_dal_csid_start_rva': '0x24260',
            'classification': 'real CSID hardware/path start when frames_to_skip == 0',
        },
        'dal_csid_start': {
            'function_rva': '0x24260',
            'active_path_count_offset': '0x1e4',
            'active_path_array_base_word_index': '0x72',
            'path_enable_callback_offset': '0x218',
            'ipp_path_id': 5,
        },
        'ipp_path_enable': {
            'function_rva': '0x1b3d0',
            'path5_branch_rva': '0x1b48c',
            'writes_in_order': [
                {'register_offset': '0x304', 'value': '0x00000001', 'role': 'IPP control enable'},
                {'register_offset': '0x0b0', 'value': '0x3cbc601c', 'role': 'IPP IRQ mask'},
                {'register_offset': '0x080', 'value': '0x00000001', 'role': 'TOP IRQ mask'},
            ],
        },
        'initial_full_csid_builder': {
            'function_rva': '0x1a870',
            'proven_direct_writes': [
                {'register_offset': '0x0a0', 'value': '0x019fb800', 'role': 'RX IRQ mask'},
                {'register_offset': '0x090', 'value': '0x0001ffff', 'role': 'BUF_DONE IRQ mask'},
                {'register_offset': '0x334', 'value': '0x00130013', 'role': 'IPP epoch IRQ config'},
                {'register_offset': '0x324', 'value': '0x00000000', 'role': 'exact zero; semantic name intentionally not promoted here'},
            ],
        },
        'captured_csid1_companion_0x803': {
            'descriptor_index': 1,
            'descriptor_type': '0x12',
            'packets': packets,
            'packet0_exact_zero_at_0x330': True,
            'note': 'The +0x330 zero is proven from exact same-machine command bytes; semantic register naming remains intentionally unresolved.',
        },
        'same_machine_live_state': {
            'wrapper_csid1_io_path_cfg0': '0x00000101',
            'csid1_stable_values': {
                f'0x{off:03x}': f'0x{val:08x}' for off, val in expected_stable.items()
            },
            'volatile_or_readback_do_not_freeze': {
                '0x340': 'static ISR reads this as BUF_DONE/status state',
                '0x398': 'read by timestamp/readback path and differs between live passes',
                '0x39c': 'paired timestamp/readback field; do not promote merely because this capture is stable',
            },
        },
        'linux_consequence': {
            'front_mode0_only': True,
            'required_parity_deltas': [
                'write exact zero to CSID1 +0x324 during front IPP configuration',
                'write exact zero to CSID1 +0x330 from captured companion packet',
                'use Windows front-session IRQ masks: BUF_DONE +0x90=0x0001ffff, RX +0xa0=0x019fb800, IPP +0xb0=0x3cbc601c, TOP +0x80=0x00000001',
            ],
            'do_not_add': [
                'a speculative CSID REG_UPDATE_CMD write: no such write is proven in the captured Windows CSID initial/start boundary',
                'replay of +0x340/+0x398/+0x39c status/timestamp values',
            ],
            'timeout_telemetry_before_next_runtime': [
                'wrapper CSID1 IO_PATH_CFG0',
                'CSID1 RX packet/ECC/CRC counters',
                'TOP/RX/IPP/BUF_DONE IRQ status and masks',
                'CSID1 RX_CFG0/RX_CFG1',
                'CSID1 IPP CFG/control/crop/drop/format-measure state',
            ],
        },
        'runtime_authorized': False,
    }

    text = json.dumps(oracle, indent=2) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
