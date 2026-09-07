#!/usr/bin/env python3
"""Minimal standard-library parser for the accepted E003h Epoch0 KD log.

This intentionally contains only the raw batch/record parser needed by the
E003i template-free capsule composer.  It does not import Capstone or perform
any driver disassembly.  The source log identity and structural counts remain
pinned to the accepted oracle.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

RAW_SHA = '1e8dc9671296e35a0704315588669fc8ed97612fd4b72c1d71b11bb7244d9a7f'
RAW_BYTES = 3994804
EXPECTED_TOTAL_BATCHES = 179
EXPECTED_TOTAL_RECORDS = 894

BATCH_RE = re.compile(r'^BATCH_BEGIN n=(\d+) count=(\d+)$')
END_RE = re.compile(r'^BATCH_END n=(\d+)$')
REC_RE = re.compile(
    r'^REC batch=(\d+) idx=(\d+) count=(\d+) iova=([0-9a-f]{8}) '
    r'cpu=([0-9a-f]{16}) lenenc=([0-9a-f]+) bytes=([0-9a-f]+) extra=([0-9a-f]{16})$', re.I)
MEM_RE = re.compile(r'^([0-9a-f]{8})`([0-9a-f]{8})\s+(.*)$', re.I)
HEXBYTE_RE = re.compile(r'^[0-9a-f]{2}$', re.I)


def die(msg: str) -> None:
    raise RuntimeError('Epoch0 log parse: ' + msg)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_mem_line(line: str):
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


def parse_log(path: Path):
    path = Path(path)
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
            die(
                f"batch {current_rec['batch']} record {current_rec['idx']} "
                f"byte capture {len(current_rec['data'])} != {current_rec['bytes']}")
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
                'batch': batch,
                'idx': idx,
                'count': count,
                'iova': iova,
                'cpu': cpu,
                'lenenc': lenenc,
                'bytes': nbytes,
                'extra': extra,
                'data': bytearray(),
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
                    die(
                        f"batch {current_rec['batch']} record {current_rec['idx']} "
                        f"memory address 0x{addr:x} != 0x{want:x}")
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
