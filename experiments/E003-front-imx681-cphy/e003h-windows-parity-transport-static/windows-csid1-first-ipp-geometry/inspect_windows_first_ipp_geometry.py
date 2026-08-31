#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

RAW_SHA = '0f69735727efd5fb37fb04fe561d1948279d343624f3305259e23e5f400e4932'
SENSOR_SHA = 'f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c'
EPOCH_STATUS = 0x00600228
PRE_EPOCH_STATUS = 0x00811dd0
BIT14 = 1 << 14

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def die(s: str) -> None:
    raise SystemExit('FAIL: ' + s)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw-log', type=Path, required=True)
    ap.add_argument('--sensor-summary', type=Path, required=True)
    a = ap.parse_args()
    if not a.raw_log.is_file():
        die(f'raw KD log missing: {a.raw_log}')
    if sha(a.raw_log) != RAW_SHA:
        die(f'raw KD log SHA mismatch: {sha(a.raw_log)}')
    s = json.loads(a.sensor_summary.read_text())
    if s.get('oracle_sha256') != SENSOR_SHA:
        die('sensor oracle SHA drift')
    m = s.get('mode0', {})
    expect = dict(width=3840, height=2640, line_length=6752, frame_length=3554, pixel_rate_hz=548570000)
    for k,v in expect.items():
        if m.get(k) != v: die(f'sensor mode0 {k} drift: {m.get(k)!r}')
    regs = s.get('key_final_registers', {})
    required = {
        '0x0342':0x1a, '0x0343':0x60,
        '0x034c':0x0f, '0x034d':0x00, '0x034e':0x0a, '0x034f':0x50,
    }
    for k,v in required.items():
        if regs.get(k) != v: die(f'sensor register {k} drift')
    text = a.raw_log.read_text(errors='replace')
    low = text.lower()
    required_literals = ['00811dd0','00600228','08700f00','00007241','0eff0000','086f0000']
    for lit in required_literals:
        if lit not in low: die(f'raw KD log missing expected literal {lit}')
    if low.find('00811dd0') > low.find('00600228'):
        die('first pre-Epoch IRQ does not precede first Epoch IRQ')
    # Parse status-like values only from lines that mention IRQ/status, then reject bit14.
    status_values=[]
    for line in text.splitlines():
        ll=line.lower()
        if 'irq' not in ll and 'status' not in ll: continue
        for h in re.findall(r'0x([0-9a-fA-F]{8})', line):
            v=int(h,16)
            if v in (PRE_EPOCH_STATUS,EPOCH_STATUS) or (v & 0xff000000)==0:
                status_values.append(v)
    if PRE_EPOCH_STATUS not in status_values or EPOCH_STATUS not in status_values:
        die('expected bounded IRQ statuses not parsed')
    if any(v & BIT14 for v in status_values):
        die('bit14 observed in bounded Windows IRQ statuses')
    print(json.dumps({
        'result':'PASS',
        'raw_log_sha256':RAW_SHA,
        'sensor_blob_sha256':SENSOR_SHA,
        'first_complete_epoch_actual':'0x08700f00',
        'first_complete_epoch_geometry':'3840x2160',
        'bounded_windows_bit14_seen':False,
        'sensor_mode0':'3840x2640@30',
        'sensor_line_length':6752,
        'sensor_frame_length':3554,
        'sensor_pixel_rate_hz':548570000,
    }, indent=2))

if __name__ == '__main__': main()
