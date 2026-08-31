#!/usr/bin/env python3
import argparse, mmap, os, struct, time
from pathlib import Path
BASE=0x0ADE0000
SIZE=0x20000
OFFS=[0x138f8,0x138fc,0x13900,0x13904,0x13908,0x1390c,0x13910,0x13914,0x13918,0x1391c,0x13920,0x13924,0x13928,0x1392c,0x13930,0x13934,0x13938,0x1393c]
RATE_BY_CFG={0x00000204:240_000_000,0x00000203:300_000_000,0x00000301:400_000_000}
p=argparse.ArgumentParser(); p.add_argument('log'); p.add_argument('--ready',required=True); p.add_argument('--stop',required=True); p.add_argument('--max-seconds',type=float,default=15.0); a=p.parse_args()
log=Path(a.log); ready=Path(a.ready); stop=Path(a.stop)
for x in (log,ready,stop):
    if x.exists(): raise SystemExit(f'FAIL: preexisting {x}')
fd=os.open('/dev/mem',os.O_RDONLY|os.O_SYNC)
m=mmap.mmap(fd,SIZE,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ,offset=BASE)
def snap(): return tuple(struct.unpack_from('<I',m,o)[0] for o in OFFS)
def fmt(vals):
    cmd,cfg,branch=vals[0],vals[1],vals[6]
    rate=RATE_BY_CFG.get(cfg,0)
    return f'cmd=0x{cmd:08x} cfg=0x{cfg:08x} branch=0x{branch:08x} rate_hz={rate} vals=' + ','.join(f'{o:05x}:0x{v:08x}' for o,v in zip(OFFS,vals))
start=time.monotonic_ns(); prev=None; samples=0; changes=0; seen300=False; seen_any_live=False
with log.open('w',buffering=1) as f:
    f.write(f'BASE=0x{BASE:08x} OFF_CFG=0x138fc OFF_BRANCH=0x13910 POLL_NS_TARGET=500000\n')
    v=snap(); prev=v; changes+=1
    f.write(f'CHANGE t_ns=0 {fmt(v)}\n')
    ready.write_text('READY\n')
    while not stop.exists() and (time.monotonic_ns()-start) < int(a.max_seconds*1e9):
        v=snap(); samples+=1
        if (v[6]&1) and v[0] != 0x80000000: seen_any_live=True
        if (v[6]&1) and v[1] == 0x00000203: seen300=True
        if v != prev:
            changes+=1
            f.write(f'CHANGE t_ns={time.monotonic_ns()-start} {fmt(v)}\n')
            prev=v
        time.sleep(0.0005)
    v=snap(); samples+=1
    if (v[6]&1) and v[0] != 0x80000000: seen_any_live=True
    if (v[6]&1) and v[1] == 0x00000203: seen300=True
    if v != prev:
        changes+=1; f.write(f'CHANGE t_ns={time.monotonic_ns()-start} {fmt(v)}\n')
    f.write(f'SUMMARY samples={samples} changes={changes} seen_any_live={int(seen_any_live)} seen_live_300={int(seen300)} elapsed_ns={time.monotonic_ns()-start}\n')
m.close(); os.close(fd)
