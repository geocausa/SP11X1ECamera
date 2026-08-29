#!/usr/bin/env python3
import argparse
import collections
import hashlib
import json
import re
import struct
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

DRIVER_SHA = '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
DRIVER_BYTES = 376560
RAW_SHA = '1e8dc9671296e35a0704315588669fc8ed97612fd4b72c1d71b11bb7244d9a7f'
RAW_BYTES = 3994804
POST_START_SHA = 'd426c7cf4525f36c80623cab628061005c880abd5df02d17d8a76683fea4e66e'
IMAGE = 0x140000000

BATCH_RE = re.compile(r'^BATCH_BEGIN n=(\d+) count=(\d+)$')
END_RE = re.compile(r'^BATCH_END n=(\d+)$')
REC_RE = re.compile(
    r'^REC batch=(\d+) idx=(\d+) count=(\d+) iova=([0-9a-f]{8}) '
    r'cpu=([0-9a-f]{16}) lenenc=([0-9a-f]+) bytes=([0-9a-f]+) extra=([0-9a-f]{16})$', re.I)
MEM_RE = re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+(.*)$', re.I)
HEXBYTE_RE = re.compile(r'^[0-9a-f]{2}$', re.I)

STARTUP_MAIN_LENGTHS = [0xe94, 0xe34, 0x904, 0x4e8]
STEADY_VECTOR_COUNTS = {
    (0x4, 0x958, 0x4, 0x10, 0x14): 8,
    (0x4, 0x868, 0x4, 0x10, 0x14): 42,
    (0x4, 0x6b8, 0x4, 0x10, 0x14): 24,
    (0x4, 0x5a4, 0x4, 0x10, 0x14): 55,
    (0x4, 0x83c, 0x4, 0x10, 0x14): 46,
}
EXPECTED_STEADY_BATCHES = 175
EXPECTED_TOTAL_BATCHES = 179
EXPECTED_TOTAL_RECORDS = 894
EXPECTED_VARIANTS = {
    0x958: (8, 56, 472, 14, 24, '6c979a87c9a550ba1dfbfe740e714f8538238e7537251f855ba997c1fadc42a2'),
    0x868: (42, 45, 436, 12, 20, '001b086bcc594a37a3a8b846a038f8e534a3b7974eb87a03a2961f1247deb856'),
    0x83c: (46, 43, 429, 12, 14, '3bcc4def6731cd107ad70ffa7d0c5c52e7a712ef6436814e50a7b9725aaf9c61'),
    0x6b8: (24, 35, 352, 8, 10, 'ed90abec133e939674d19bfcbcc2250fee9e23cb539306fbeb574054b43df6d8'),
    0x5a4: (55, 22, 315, 2, 6, '3dd3c9d87f07db98df529ff522a9541cf0c9c38f0d5862c425431660b467f0e9'),
}

OP_NAMES = {
    1: 'DMI', 3: 'REG_CONT', 4: 'REG_RANDOM', 5: 'BUFF_INDIRECT',
    6: 'GEN_IRQ', 7: 'WAIT_EVENT', 8: 'CHANGE_BASE', 9: 'PERF_CTRL',
    10: 'DMI_32', 11: 'DMI_64', 12: 'COMP_WAIT', 13: 'CLEAR_COMP_WAIT',
    14: 'WAIT_PREFETCH_DISABLE',
}


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_path(path):
    return sha_bytes(Path(path).read_bytes())


def hx(v):
    return f'0x{v:x}'


def pe_sections(data):
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    n = struct.unpack_from('<H', data, pe + 6)[0]
    opt = struct.unpack_from('<H', data, pe + 20)[0]
    table = pe + 24 + opt
    out = []
    for i in range(n):
        off = table + i * 40
        name = data[off:off + 8].rstrip(b'\0').decode('ascii')
        vs, va, rs, raw = struct.unpack_from('<IIII', data, off + 8)
        out.append((name, va, vs, raw, rs))
    return out


def verify_driver(path):
    data = path.read_bytes()
    if len(data) != DRIVER_BYTES or sha_bytes(data) != DRIVER_SHA:
        die('driver identity drift')
    text = next((s for s in pe_sections(data) if s[0] == '.text'), None)
    if not text:
        die('.text missing')
    _, va, _, raw, rs = text
    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    md.skipdata = True
    ins = {
        x.address - IMAGE: x for x in md.disasm(data[raw:raw + rs], IMAGE + va)
        if x.mnemonic != '.byte'
    }
    anchors = {
        # Epoch0 asks the CDM dispatcher to consume a queued batch with selector 2.
        0x25eac: ('ldr', 'x0, [x21, #0x98]'),
        0x25ec0: ('mov', 'x2, #0'),
        0x25ec4: ('mov', 'w1, #2'),
        0x25ec8: ('bl', '#0x140028480'),
        # Selector-2 copies one exact 0x28-byte queue record to the stack.
        0x287cc: ('mov', 'x9, #0x28'),
        0x287d0: ('add', 'x8, sp, #0x68'),
        0x287d4: ('umaddl', 'x8, w24, w9, x8'),
        0x287d8: ('ldp', 'q17, q16, [x8]'),
        0x287dc: ('ldr', 'x8, [x8, #0x20]'),
        0x287e0: ('stp', 'q17, q16, [sp, #0x20]'),
        # Queue record fields used for hardware commit: IOVA and byte-length-minus-one.
        0x287e4: ('ldr', 'w22, [sp, #0x20]'),
        0x287e8: ('ldr', 'w20, [sp, #0x30]'),
        # FIFO0 base/encoded length/store ordering.
        0x28884: ('str', 'w22, [x8, #0x50]'),
        0x2888c: ('str', 'w20, [x8, #0x54]'),
        0x28894: ('str', 'w9, [x8, #0x58]'),
    }
    rendered = {}
    for rva, (mn, ops) in anchors.items():
        x = ins.get(rva)
        if not x or x.mnemonic != mn or x.op_str != ops:
            die(f'driver anchor drift at 0x{rva:x}: {x}')
        rendered[hx(rva)] = f'{x.mnemonic} {x.op_str}'
    return rendered


def verify_post_start(path):
    if sha_path(path) != POST_START_SHA:
        die('0023 post-start oracle identity drift')
    j = json.loads(path.read_text())
    if not j.get('accepted'):
        die('0023 post-start oracle not accepted')
    cg = j['driver_call_graph']
    if cg.get('epoch0_handler_rva') != '0x25268' or cg.get('cdm_dispatcher_rva') != '0x28480':
        die('0023 call graph drift')
    if cg.get('cdm_epoch_consume_selector') != 2:
        die('0023 selector drift')
    return j


def parse_mem_line(line):
    m = MEM_RE.match(line)
    if not m:
        return None
    addr = int(m.group(1) + m.group(2), 16)
    toks = m.group(3).replace('-', ' ').split()
    out = []
    for tok in toks:
        if not HEXBYTE_RE.fullmatch(tok):
            break
        out.append(int(tok, 16))
    return addr, bytes(out)


def parse_log(path):
    raw = path.read_bytes()
    if len(raw) != RAW_BYTES or sha_bytes(raw) != RAW_SHA:
        die('clean Epoch0 raw identity drift')
    lines = raw.decode('utf-16').splitlines()
    batches = []
    current_batch = None
    current_rec = None

    def finish_rec():
        nonlocal current_rec
        if current_rec is None:
            return
        if len(current_rec['data']) != current_rec['bytes']:
            die(f"batch {current_rec['batch']} record {current_rec['idx']} byte capture {len(current_rec['data'])} != {current_rec['bytes']}")
        current_rec['data'] = bytes(current_rec['data'])
        current_batch['records'].append(current_rec)
        current_rec = None

    for line in lines:
        m = BATCH_RE.fullmatch(line)
        if m:
            finish_rec()
            if current_batch is not None:
                die('nested BATCH_BEGIN')
            n, count = map(int, m.groups())
            current_batch = {'batch': n, 'count': count, 'records': []}
            continue
        m = REC_RE.fullmatch(line)
        if m:
            if current_batch is None:
                die('REC outside batch')
            finish_rec()
            batch, idx, count = map(int, m.group(1, 2, 3))
            if batch != current_batch['batch'] or count != current_batch['count']:
                die('REC batch/count mismatch')
            iova = int(m.group(4), 16)
            cpu = int(m.group(5), 16)
            lenenc = int(m.group(6), 16)
            nbytes = int(m.group(7), 16)
            extra = int(m.group(8), 16)
            if nbytes != lenenc + 1:
                die(f'batch {batch} record {idx}: bytes != lenenc + 1')
            current_rec = {
                'batch': batch, 'idx': idx, 'count': count,
                'iova': iova, 'cpu': cpu, 'lenenc': lenenc, 'bytes': nbytes,
                'extra': extra, 'data': bytearray(),
            }
            continue
        m = END_RE.fullmatch(line)
        if m:
            finish_rec()
            if current_batch is None or int(m.group(1)) != current_batch['batch']:
                die('BATCH_END mismatch')
            if len(current_batch['records']) != current_batch['count']:
                die(f"batch {current_batch['batch']} record count drift")
            if [r['idx'] for r in current_batch['records']] != list(range(current_batch['count'])):
                die(f"batch {current_batch['batch']} record index drift")
            batches.append(current_batch)
            current_batch = None
            continue
        if current_rec is not None:
            parsed = parse_mem_line(line)
            if parsed:
                addr, chunk = parsed
                want = current_rec['cpu'] + len(current_rec['data'])
                if addr != want:
                    die(f"batch {current_rec['batch']} record {current_rec['idx']} memory address 0x{addr:x} != 0x{want:x}")
                remain = current_rec['bytes'] - len(current_rec['data'])
                current_rec['data'].extend(chunk[:remain])

    finish_rec()
    if current_batch is not None:
        die('unterminated final batch')
    if len(batches) != EXPECTED_TOTAL_BATCHES:
        die(f'batch count drift: {len(batches)}')
    if sum(len(b['records']) for b in batches) != EXPECTED_TOTAL_RECORDS:
        die('record count drift')
    if [b['batch'] for b in batches] != list(range(EXPECTED_TOTAL_BATCHES)):
        die('batch numbering drift')
    return raw, batches


def decode(data):
    pos = 0
    cmds = []
    writes = []
    dmis = []
    reg_value_fields = {}
    dmi_addr_fields = {}
    while pos < len(data):
        if pos + 4 > len(data):
            die('truncated command word')
        w0 = struct.unpack_from('<I', data, pos)[0]
        op = w0 >> 24
        name = OP_NAMES.get(op)
        if not name:
            die(f'unknown opcode 0x{op:02x} at 0x{pos:x}')
        rec = {'offset': pos, 'opcode': op, 'command': name}
        if op == 3:
            n = w0 & 0xffff
            need = 8 + 4 * n
            if pos + need > len(data): die('truncated REG_CONT')
            base = struct.unpack_from('<I', data, pos + 4)[0] & 0xffffff
            vals = []
            for i in range(n):
                field = pos + 8 + 4 * i
                ro = base + 4 * i
                val = struct.unpack_from('<I', data, field)[0]
                writes.append((ro, val, field, 'REG_CONT'))
                reg_value_fields[field] = ro
                vals.append(val)
            rec.update(register_offset=base, count=n, bytes=need)
            pos += need
        elif op == 4:
            n = w0 & 0xffff
            need = 4 + 8 * n
            if pos + need > len(data): die('truncated REG_RANDOM')
            ros = []
            for i in range(n):
                ro = struct.unpack_from('<I', data, pos + 4 + 8 * i)[0] & 0xffffff
                field = pos + 8 + 8 * i
                val = struct.unpack_from('<I', data, field)[0]
                writes.append((ro, val, field, 'REG_RANDOM'))
                reg_value_fields[field] = ro
                ros.append(ro)
            rec.update(register_offsets=ros, count=n, bytes=need)
            pos += need
        elif op in (1, 10, 11):
            if pos + 12 > len(data): die('truncated DMI')
            addr = struct.unpack_from('<I', data, pos + 4)[0]
            w2 = struct.unpack_from('<I', data, pos + 8)[0]
            payload_bytes = (w0 & 0xffff) + 1
            field = pos + 4
            d = {
                'offset': pos, 'command': name, 'address': addr,
                'address_field': field, 'payload_bytes': payload_bytes,
                'dmi_register_offset': w2 & 0xffffff, 'dmi_sel': w2 >> 24,
            }
            dmis.append(d)
            dmi_addr_fields[field] = d
            rec.update(payload_bytes=payload_bytes, dmi_register_offset=w2 & 0xffffff,
                       dmi_sel=w2 >> 24, bytes=12)
            pos += 12
        elif op == 5:
            if pos + 8 > len(data): die('truncated BUFF_INDIRECT')
            rec.update(length_minus_one=w0 & 0xffff,
                       data_iova=struct.unpack_from('<I', data, pos + 4)[0], bytes=8)
            pos += 8
        elif op == 6:
            if pos + 8 > len(data): die('truncated GEN_IRQ')
            rec.update(userdata=struct.unpack_from('<I', data, pos + 4)[0], bytes=8)
            pos += 8
        elif op in (7, 12, 13, 14):
            if pos + 12 > len(data): die('truncated fixed 12-byte command')
            rec.update(bytes=12)
            pos += 12
        elif op == 8:
            rec.update(new_base=w0 & 0xffffff, bytes=4)
            pos += 4
        elif op == 9:
            rec.update(bytes=4)
            pos += 4
        cmds.append(rec)
    if pos != len(data):
        die('decode length mismatch')
    return {
        'commands': cmds, 'writes': writes, 'dmis': dmis,
        'reg_value_fields': reg_value_fields, 'dmi_addr_fields': dmi_addr_fields,
    }


def structure_signature(decoded):
    sig = []
    for c in decoded['commands']:
        name = c['command']
        if name == 'REG_CONT':
            sig.append((name, c['register_offset'], c['count']))
        elif name == 'REG_RANDOM':
            sig.append((name, tuple(c['register_offsets'])))
        elif name in ('DMI', 'DMI_32', 'DMI_64'):
            sig.append((name, c['dmi_register_offset'], c['dmi_sel'], c['payload_bytes']))
        elif name == 'CHANGE_BASE':
            sig.append((name, c['new_base']))
        elif name == 'BUFF_INDIRECT':
            sig.append((name, c['length_minus_one']))
        else:
            sig.append((name, c.get('bytes')))
    return tuple(sig)


def count_writes(decoded):
    return len(decoded['writes'])


def normalize_variant(records):
    decoded = [decode(r['data']) for r in records]
    sig0 = structure_signature(decoded[0])
    if any(structure_signature(x) != sig0 for x in decoded[1:]):
        die(f"main BL structure drift for length 0x{records[0]['bytes']:x}")
    n = records[0]['bytes']
    varying = []
    for off in range(0, n, 4):
        vals = {r['data'][off:off + 4] for r in records}
        if len(vals) > 1:
            varying.append(off)
    dmi_fields = set(decoded[0]['dmi_addr_fields'])
    reg_fields = decoded[0]['reg_value_fields']
    dynamic_regs = [o for o in varying if o in reg_fields]
    unexpected = [o for o in varying if o not in dmi_fields and o not in reg_fields]
    if unexpected:
        die(f"unclassified varying dwords in 0x{n:x}: {[hx(x) for x in unexpected]}")
    # Never preserve captured DMI IOVAs, even if any happen to repeat.
    holes = sorted(dmi_fields | set(dynamic_regs))
    normalized = []
    for r in records:
        b = bytearray(r['data'])
        for off in holes:
            b[off:off + 4] = b'\0' * 4
        normalized.append(bytes(b))
    if len({sha_bytes(x) for x in normalized}) != 1:
        die(f'normalized main BL mismatch for 0x{n:x}')
    ops = collections.Counter(c['command'] for c in decoded[0]['commands'])
    dmi_shape = [{
        'field': hx(d['address_field']),
        'dmi_register_offset': hx(d['dmi_register_offset']),
        'selector': d['dmi_sel'],
        'payload_bytes': d['payload_bytes'],
    } for d in decoded[0]['dmis']]
    dyn = [{'field': hx(off), 'register_offset': hx(reg_fields[off])} for off in dynamic_regs]
    invariant_tail = {}
    for ro in (0x24, 0x8c, 0x90):
        fields = [f for f, r in reg_fields.items() if r == ro]
        if len(fields) == 1:
            f = fields[0]
            vals = {struct.unpack_from('<I', r['data'], f)[0] for r in records}
            invariant_tail[hx(ro)] = {
                'field': hx(f), 'values': [f'0x{x:08x}' for x in sorted(vals)],
                'invariant_within_variant': len(vals) == 1,
            }
    return {
        'main_bytes': n,
        'sample_count': len(records),
        'command_count': len(decoded[0]['commands']),
        'register_write_count': count_writes(decoded[0]),
        'dmi_count': len(decoded[0]['dmis']),
        'opcode_counts': dict(sorted(ops.items())),
        'dmi_shape': dmi_shape,
        'dynamic_register_fields': dyn,
        'dmi_address_fields': [hx(x) for x in sorted(dmi_fields)],
        'normalized_holes': [hx(x) for x in holes],
        'normalized_sha256': sha_bytes(normalized[0]),
        'tail_registers': invariant_tail,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--driver', type=Path, required=True)
    ap.add_argument('--log', type=Path, required=True)
    ap.add_argument('--post-start-oracle', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    anchors = verify_driver(a.driver)
    prior = verify_post_start(a.post_start_oracle)
    raw, batches = parse_log(a.log)

    # The clean capture begins with the four previously-proven startup IFE batches.
    startup = []
    for i, expected in enumerate(STARTUP_MAIN_LENGTHS):
        b = batches[i]
        main = b['records'][1]
        if main['bytes'] != expected:
            die(f'startup packet {i} length 0x{main["bytes"]:x} != 0x{expected:x}')
        startup.append({'batch': i, 'record_count': b['count'], 'main_bytes': main['bytes']})

    steady = batches[4:]
    if len(steady) != EXPECTED_STEADY_BATCHES:
        die('steady-state batch count drift')
    vectors = collections.Counter(tuple(r['bytes'] for r in b['records']) for b in steady)
    if dict(vectors) != STEADY_VECTOR_COUNTS:
        die(f'steady vector census drift: {dict(vectors)!r}')

    # Every steady batch has the same four companion BL roles around a variable main BL.
    fixed_hashes = {0: set(), 2: set(), 3: set()}
    irq_normalized_hashes = set()
    irq_values = []
    main_by_len = collections.defaultdict(list)
    for b in steady:
        if b['count'] != 5:
            die(f'batch {b["batch"]} is not five-BL steady state')
        for idx in fixed_hashes:
            fixed_hashes[idx].add(sha_bytes(b['records'][idx]['data']))
        r0, r2, r3, r4 = (b['records'][i] for i in (0, 2, 3, 4))
        d0, d2, d3, d4 = map(lambda r: decode(r['data']), (r0, r2, r3, r4))
        if structure_signature(d0) != (('CHANGE_BASE', 0xf000),):
            die('steady BL0 is not CHANGE_BASE 0xf000')
        if structure_signature(d2) != (('CHANGE_BASE', 0x57000),):
            die('steady BL2 is not CHANGE_BASE 0x57000')
        if len(d3['commands']) != 1 or d3['commands'][0]['command'] != 'REG_CONT' or len(d3['writes']) != 2:
            die('steady BL3 structure drift')
        if [c['command'] for c in d4['commands']] != ['REG_RANDOM', 'GEN_IRQ'] or len(d4['writes']) != 1:
            die('steady BL4 structure drift')
        userdata = d4['commands'][1]['userdata']
        if userdata != b['batch']:
            die(f'batch {b["batch"]} GEN_IRQ userdata {userdata} != batch index')
        irq_values.append(userdata)
        z = bytearray(r4['data']); z[0x10:0x14] = b'\0' * 4
        irq_normalized_hashes.add(sha_bytes(z))
        main_by_len[b['records'][1]['bytes']].append(b['records'][1])

    if any(len(v) != 1 for v in fixed_hashes.values()):
        die('steady companion BL identity drift')
    if len(irq_normalized_hashes) != 1:
        die('steady BL4 normalized identity drift')

    variants = []
    for main_len in sorted(main_by_len, reverse=True):
        v = normalize_variant(main_by_len[main_len])
        v['batch_numbers'] = [r['batch'] for r in main_by_len[main_len]]
        expected = EXPECTED_VARIANTS.get(main_len)
        got = (v['sample_count'], v['command_count'], v['register_write_count'],
               v['dmi_count'], len(v['dynamic_register_fields']), v['normalized_sha256'])
        if expected != got:
            die(f'variant 0x{main_len:x} semantic drift: {got!r} != {expected!r}')
        for ro, value in (('0x24', '0x00006000'), ('0x8c', '0x37213000'), ('0x90', '0x00000001')):
            tail = v['tail_registers'].get(ro)
            if not tail or tail['values'] != [value] or not tail['invariant_within_variant']:
                die(f'variant 0x{main_len:x} tail {ro} drift: {tail!r}')
        variants.append(v)

    # 0023's direct-MMIO "no rewrite" wording is superseded: the registers are
    # present in the queued per-frame CDM lists. This does not authorize a
    # separate Linux MMIO polling/rewrite loop.
    touched = set()
    for v in variants:
        touched |= {int(x['register_offset'], 16) for x in v['dynamic_register_fields']}
        for ro in v['tail_registers']:
            touched.add(int(ro, 16))
    superseded_regs = [x for x in (0x8c, 0x3b70, 0x3d78, 0x3d7c, 0x3d80, 0x3d84) if x in touched]
    if superseded_regs != [0x8c, 0x3b70, 0x3d78, 0x3d7c, 0x3d80, 0x3d84]:
        die(f'expected 0023-superseding register set not all present: {superseded_regs}')

    out = {
        'schema': 'sp11-e003h-windows-vfe1-epoch0-cdm-batches-v1',
        'accepted': True,
        'source_evidence': {
            'driver': {'bytes': DRIVER_BYTES, 'sha256': DRIVER_SHA},
            'raw_log': {'bytes': RAW_BYTES, 'sha256': RAW_SHA, 'encoding': 'UTF-16LE KD text'},
            'post_start_0023_oracle_sha256': POST_START_SHA,
        },
        'queue_record_contract': {
            'record_bytes': 0x28,
            'selector': 2,
            'record_stack_copy_rva': '0x287d8',
            'iova_field_stack_offset': '+0x20',
            'cpu_alias_field_stack_offset': '+0x28',
            'encoded_length_field_stack_offset': '+0x30',
            'encoded_length_semantics': 'byte_count_minus_one',
            'fifo0_commit_rvas': ['0x28884', '0x2888c', '0x28894'],
            'instruction_anchors': anchors,
        },
        'capture': {
            'total_batches': len(batches),
            'total_records': sum(len(b['records']) for b in batches),
            'startup_batches': startup,
            'steady_state_batches': len(steady),
            'steady_vector_counts': [
                {'lengths': [hx(x) for x in vec], 'count': count}
                for vec, count in sorted(vectors.items(), key=lambda kv: (-kv[1], kv[0]))
            ],
        },
        'steady_companion_bls': {
            'bl0_change_base_sha256': next(iter(fixed_hashes[0])),
            'bl2_change_base_sha256': next(iter(fixed_hashes[2])),
            'bl3_register_sha256': next(iter(fixed_hashes[3])),
            'bl4_genirq_normalized_sha256': next(iter(irq_normalized_hashes)),
            'bl4_genirq_userdata_rule': 'exact batch index for all 175 steady-state batches',
        },
        'main_bl_variants': variants,
        'supersedes_0023_wording': {
            'registers': [hx(x) for x in superseded_regs],
            'correction': 'Windows steady-state queued RT-CDM BLs do contain writes to these registers. Do not model them as a separate direct-MMIO/polling rewrite loop; they belong to the per-frame CDM command program.',
            'prior_post_start_stage_order_retained': 'IFE Epoch0 -> complete VFE1 BUS IOVA update -> RT-CDM queued-BL consume/program -> completion dispatch/retirement',
        },
        'linux_consequence': {
            'steady_state_model': 'five-BL Epoch0 batch: CHANGE_BASE(VFE1), one variant main IFE BL, CHANGE_BASE(companion), fixed two-register BL, fixed register+GEN_IRQ BL with caller batch tag',
            'main_variant_count': len(variants),
            'main_variant_lengths': [hx(v['main_bytes']) for v in variants],
            'dmi_policy': 'DMI address dwords are per-batch DMA state and must be repatched to Linux-owned payload IOVAs; payload bytes are not captured by this oracle and remain a separate closure gate',
            'runtime_gate': 'remain fail-closed; no Linux RT-CDM FIFO0 submission, CSID1/VFE1 PIX/MIPI start, IMX681 transmission or front frame is authorized',
        },
    }
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print('PASS: 179 Windows Epoch0 CDM batches decode exactly; five steady main-BL variants and per-frame hole sets are closed')
    for v in variants:
        print(f"0x{v['main_bytes']:x}: samples={v['sample_count']} cmds={v['command_count']} writes={v['register_write_count']} dmi={v['dmi_count']} dyn_regs={len(v['dynamic_register_fields'])} norm={v['normalized_sha256']}")


if __name__ == '__main__':
    main()
