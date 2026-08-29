#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

DRIVER_SHA = '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
DRIVER_BYTES = 376560
RAW_SHA = '81aa7b23e2434dd89ddea21868917e23a2ce3abc1220a19b53805324c37825b5'
RAW_BYTES = 8616
DYNAMIC_SHA = '925028750e8be60c65a69f24349bb540b0ba0776726f40d59273b0be7f464282'
COMPLETION_SHA = '696f476a18bbfe4d6a30e06198c744d6495048b85399d22ff1bfe6c6176763f9'
IMAGE = 0x140000000

ADDR_ORDER = [
    ('3000', 0), ('3000', 1), ('3001', 0), ('3002', 0), ('301c', 0),
    ('3010', 0), ('300f', 0), ('300e', 0), ('300c', 0),
]
EVENT_ORDER = [0x3, 0xd, 0xe, 0x10, 0x12]
SEQ_RE = re.compile(r'^SEQ=(\d+) (?:ADDR rid=([0-9a-f]{4}) sel=([0-9a-f]+)|START_DONE|EV id=([0-9a-f]+))$')


def die(msg):
    raise SystemExit('FAIL: ' + msg)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_path(path):
    return sha_bytes(Path(path).read_bytes())


def pe_sections(data):
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    count = struct.unpack_from('<H', data, pe + 6)[0]
    opt_size = struct.unpack_from('<H', data, pe + 20)[0]
    table = pe + 24 + opt_size
    out = []
    for i in range(count):
        off = table + i * 40
        name = data[off:off + 8].rstrip(b'\0').decode('ascii')
        virtual_size, virtual_address, raw_size, raw_off = struct.unpack_from('<IIII', data, off + 8)
        out.append((name, virtual_address, virtual_size, raw_off, raw_size))
    return out


def rva_off(sections, rva):
    for _, va, vs, raw, rs in sections:
        if va <= rva < va + max(vs, rs):
            return raw + (rva - va)
    die(f'unmapped RVA 0x{rva:x}')


def verify_driver(path):
    data = path.read_bytes()
    if len(data) != DRIVER_BYTES or sha_bytes(data) != DRIVER_SHA:
        die('driver identity drift')
    sections = pe_sections(data)
    text = next((s for s in sections if s[0] == '.text'), None)
    if not text:
        die('.text missing')
    _, va, _, raw, rs = text
    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    md.skipdata = True
    ins = {
        x.address - IMAGE: x
        for x in md.disasm(data[raw:raw + rs], IMAGE + va)
        if x.mnemonic != '.byte'
    }

    anchors = {
        # IFE ISR: Epoch0 path is invoked before the event/completion dispatch loop.
        0x1f3f4: ('ldr', 'w2, [x19, #0x120]'),
        0x1f3fc: ('add', 'x1, x8, #0xa60'),
        0x1f408: ('ldr', 'w1, [x23, #0x2c]'),
        0x1f410: ('bl', '#0x140025268'),
        0x1f438: ('cmp', 'w8, #3'),
        # Epoch0 handler: update resources first, then ask CDM to consume/program a batch.
        0x25a34: ('mov', 'x0, x21'),
        0x25a38: ('bl', '#0x140028380'),
        0x25eac: ('ldr', 'x0, [x21, #0x98]'),
        0x25ec0: ('mov', 'x2, #0'),
        0x25ec4: ('mov', 'w1, #2'),
        0x25ec8: ('bl', '#0x140028480'),
        0x25ef8: ('add', 'x1, x8, #0x728'),
        # X1E writer callback registration and resource-update callback invocation.
        0x1a048: ('adrp', 'x8, #0x14001d000'),
        0x1a04c: ('add', 'x8, x8, #0xd20'),
        0x1a058: ('str', 'x9, [x8, #0x6a8]'),
        0x283c8: ('ldr', 'x8, [x24, #0x6a8]'),
        # CDM dispatcher selector: op1 accumulates BL descriptors; op0 queues the batch;
        # op2 dequeues/programs it. Epoch0 uses op2 above.
        0x2222c: ('ldr', 'x8, [x0]'),
        0x22254: ('mov', 'w1, #1'),
        0x22268: ('blr', 'x15'),
        0x28524: ('cmp', 'w1, #2'),
        0x28528: ('b.eq', '#0x140028664'),
        0x28998: ('add', 'x11, x19, #0x890'),
        0x28a14: ('cbnz', 'x2, #0x140028a58'),
        0x28a5c: ('add', 'x1, x19, #0x890'),
        0x28a60: ('ldr', 'x0, [x19, #0x50]'),
        0x28a70: ('bl', '#0x14002bef8'),
        # op2 eventually commits each dequeued BL to FIFO0 base/len/store.
        0x28884: ('str', 'w22, [x8, #0x50]'),
        0x2888c: ('str', 'w20, [x8, #0x54]'),
        0x28894: ('str', 'w9, [x8, #0x58]'),
    }
    rendered = {}
    for rva, (mnemonic, operands) in anchors.items():
        x = ins.get(rva)
        if not x or x.mnemonic != mnemonic or x.op_str != operands:
            die(f'driver anchor drift at 0x{rva:x}: {x}')
        rendered[f'0x{rva:x}'] = f'{x.mnemonic} {x.op_str}'

    strings = {
        0x37a60: b'IFE%d IFE Epoch0 Irq occured.\0',
        0x3a728: b' IFE%d sending the IFE CDM BL_ENQUEUE in epoch irq for request id %d, subRequest:%d \0',
        0x3c6e0: b'cdmBlQueue does not have any packet to dequeue with result %d\0',
        0x3c720: b'cdmBlQueue dequeue failed with result %d\0',
        0x3d100: b'Entered HAL_cdm_commit_bl function\0',
        0x3d170: b'Exiting HAL_cdm_commit_bl function\0',
    }
    for rva, expected in strings.items():
        off = rva_off(sections, rva)
        if data[off:off + len(expected)] != expected:
            die(f'diagnostic string drift at 0x{rva:x}')

    return rendered


def parse_timeline(path):
    data = path.read_bytes()
    if len(data) != RAW_BYTES or sha_bytes(data) != RAW_SHA:
        die('post-start raw log identity drift')
    text = data.decode('utf-16')
    events = []
    for line in text.splitlines():
        m = SEQ_RE.fullmatch(line)
        if not m:
            continue
        seq = int(m.group(1))
        if m.group(2):
            events.append({'seq': seq, 'kind': 'addr', 'rid': m.group(2), 'sel': int(m.group(3), 16)})
        elif 'START_DONE' in line:
            events.append({'seq': seq, 'kind': 'start_done'})
        else:
            events.append({'seq': seq, 'kind': 'completion', 'event_id': int(m.group(4), 16)})

    if not events or any(a['seq'] >= b['seq'] for a, b in zip(events, events[1:])):
        die('timeline sequence is missing or non-monotonic')
    starts = [i for i, e in enumerate(events) if e['kind'] == 'start_done']
    if len(starts) != 2:
        die(f'expected two START_DONE windows, got {len(starts)}')

    def expect_addr_bundle(chunk, label):
        got = [(e.get('rid'), e.get('sel')) for e in chunk]
        if len(chunk) != len(ADDR_ORDER) or any(e['kind'] != 'addr' for e in chunk) or got != ADDR_ORDER:
            die(f'{label} address bundle drift: {got!r}')
        return {'first_seq': chunk[0]['seq'], 'last_seq': chunk[-1]['seq']}

    sessions = []
    for number, idx in enumerate(starts, 1):
        if idx < 9 or idx + 23 >= len(events):
            die(f'session {number} local window truncated')
        pre = events[idx - 9:idx]
        post = events[idx + 1:idx + 10]
        done = events[idx + 10:idx + 15]
        refill = events[idx + 15:idx + 24]
        p = expect_addr_bundle(pre, f'session {number} pre-start')
        q = expect_addr_bundle(post, f'session {number} first post-start')
        r = expect_addr_bundle(refill, f'session {number} post-completion refill')
        got_events = [e.get('event_id') for e in done]
        if len(done) != 5 or any(e['kind'] != 'completion' for e in done) or got_events != EVENT_ORDER:
            die(f'session {number} completion observation drift: {got_events!r}')
        sessions.append({
            'session': number,
            'pre_start_bundle': p,
            'isp_start_done_seq': events[idx]['seq'],
            'first_post_start_bundle': q,
            'first_completion_cycle': {
                'first_seq': done[0]['seq'], 'last_seq': done[-1]['seq'],
                'observed_event_ids': [f'0x{x:x}' for x in got_events],
            },
            'post_completion_refill_bundle': r,
            'observed_initial_prime_depth_bundles': 2,
        })
    return sessions


def verify_oracles(dynamic_path, completion_path):
    if sha_path(dynamic_path) != DYNAMIC_SHA:
        die('dynamic-address oracle identity drift')
    if sha_path(completion_path) != COMPLETION_SHA:
        die('completion oracle identity drift')
    dynamic = json.loads(dynamic_path.read_text())
    completion = json.loads(completion_path.read_text())
    if not dynamic.get('accepted') or not completion.get('accepted'):
        die('upstream oracle not accepted')
    expected_dynamic_order = [
        'FULL_Y/0x3000:0', 'FULL_C/0x3000:1', 'DS4/0x3001', 'DS16/0x3002',
        'AEC_BE/0x301c', 'RS/0x3010', 'BHIST/0x300f', 'AWB_BG/0x300e', 'TL_BG/0x300c',
    ]
    if dynamic['client_address_order'] != expected_dynamic_order:
        die('upstream dynamic address order drift')
    groups = [g['event_id'] for g in completion['groups']]
    if groups != EVENT_ORDER:
        die('upstream completion group IDs drift')
    if completion['group_queue_model'].get('cross_group_order_enforced') is not False:
        die('completion oracle no longer proves independent group FIFOs')
    return dynamic, completion


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--driver', type=Path, required=True)
    ap.add_argument('--log', type=Path, required=True)
    ap.add_argument('--dynamic-oracle', type=Path, required=True)
    ap.add_argument('--completion-oracle', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path)
    a = ap.parse_args()

    anchors = verify_driver(a.driver)
    sessions = parse_timeline(a.log)
    dynamic, completion = verify_oracles(a.dynamic_oracle, a.completion_oracle)

    out = {
        'schema': 'sp11-e003h-windows-vfe1-post-start-ownership-v1',
        'accepted': True,
        'source_evidence': {
            'driver': {'bytes': DRIVER_BYTES, 'sha256': DRIVER_SHA},
            'raw_log': {'bytes': RAW_BYTES, 'sha256': RAW_SHA, 'encoding': 'UTF-16LE KD text'},
            'dynamic_address_oracle_sha256': DYNAMIC_SHA,
            'completion_groups_oracle_sha256': COMPLETION_SHA,
        },
        'driver_call_graph': {
            'epoch0_isr_diagnostic_rva': '0x37a60',
            'epoch0_handler_rva': '0x25268',
            'isr_epoch0_call_rva': '0x1f410',
            'completion_dispatch_first_compare_rva': '0x1f438',
            'epoch0_bus_update_wrapper_rva': '0x28380',
            'epoch0_bus_update_call_rva': '0x25a38',
            'x1e_bus_address_writer_rva': '0x1dd20',
            'x1e_bus_writer_callback_slot': 'IFE context +0x6a8',
            'cdm_dispatcher_rva': '0x28480',
            'cdm_add_bl_wrapper_rva': '0x22200',
            'cdm_add_bl_selector': 1,
            'cdm_queue_selector': 0,
            'cdm_epoch_consume_selector': 2,
            'cdm_epoch_consume_call_rva': '0x25ec8',
            'cdm_fifo0_commit_register_offsets': ['+0x50', '+0x54', '+0x58'],
            'instruction_anchors': anchors,
        },
        'runtime_timeline': {
            'complete_windows_sessions': 2,
            'address_bundle_order': [f'0x{rid}:{sel}' for rid, sel in ADDR_ORDER],
            'address_bundle_clients': 9,
            'sessions': sessions,
            'observed_startup_prime': 'one complete bundle before ISP_START_DONE plus one complete bundle after ISP_START_DONE before the first completion cycle',
            'observed_refill': 'a new complete address bundle is written after the first five-group completion cycle',
        },
        'ownership': {
            'software_owned_post_start': [
                'IFE Epoch0 request-consumption scheduling',
                'complete nine-client VFE1 BUS IOVA update through the existing writer callback',
                'RT-CDM queued-BL consume/program operation',
                'completion-group FIFO retirement',
            ],
            'startup_template_not_post_start_rewrite': ['VFE1 +0x3b70', 'VFE1 +0x3d78', 'VFE1 +0x3d7c', 'VFE1 +0x3d80', 'VFE1 +0x3d84', 'VFE1 period_cfg +0x8c'],
            'hardware_live_mutable_observation_only': ['VFE1 +0x3d78', 'VFE1 +0x3d7c', 'VFE1 +0x3d80', 'VFE1 +0x3d84'],
            'bounded_live_stable_no_post_start_write_proven': ['VFE1 +0x3b70'],
            'period_cfg_live_readback': 'zero in the prior bounded same-machine stream samples; startup command value is not a post-start MMIO target',
        },
        'completion_policy': {
            'observed_first_cycle': [f'0x{x:x}' for x in EVENT_ORDER],
            'cross_group_order_required': False,
            'reason': completion['linux_consequence']['completion_order'],
            'slot_reuse': completion['linux_consequence']['slot_reuse'],
        },
        'linux_consequence': {
            'pipeline': 'model two initially primed frame bundles: program a second Linux-owned IOVA bundle before the first completion, retire the oldest bundle through five independent completion-group FIFOs, then replenish a reusable slot on a later Epoch0 update',
            'bus_addresses': 'use queued Linux DMA IOVAs only; never freeze Windows addresses or Windows allocator strides',
            'rtcdm': 'Epoch0 requires a queued command batch in the Windows behavior, but this oracle does not authorize Linux FIFO0 submission',
            'live_registers': 'do not create periodic Linux rewrites for +0x3b70/+0x3d78..+0x3d84 or period_cfg +0x8c; preserve their already-closed startup-template ownership and treat live mutation as observation',
            'runtime_gate': 'remain fail-closed: no caller may arm RT-CDM, enable VFE1 PIX, start CSID1 IPP/MIPI, transmit IMX681, or attempt a frame',
        },
    }
    text = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if a.output:
        a.output.write_text(text)
    else:
        print(text, end='')
    print('PASS: post-start ownership is Epoch0 software scheduling -> BUS IOVA update -> RT-CDM batch consume, with independent completion retirement and hardware-live counters observation-only')


if __name__ == '__main__':
    main()
