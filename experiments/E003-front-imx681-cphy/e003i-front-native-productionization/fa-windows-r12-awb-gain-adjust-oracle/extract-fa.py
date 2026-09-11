#!/usr/bin/env python3
from pathlib import Path
import argparse,re
ap=argparse.ArgumentParser();ap.add_argument('log',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
s=a.log.read_text(errors='replace').replace('\r','')
rows=[line.strip() for line in s.splitlines() if line.strip().startswith(('FA_GA ','FA_PUB '))]
pairs={}
i=0
while i+1<len(rows):
    ga,pub=rows[i:i+2]
    mg=re.search(r'\breq=(\d+)\b',ga); mp=re.search(r'\breq=(\d+)\b',pub)
    if not mg or not mp or mg.group(1)!=mp.group(1):
        raise SystemExit(f'FAIL: pair mismatch at raw row {i}')
    req=int(mg.group(1))
    if req in pairs:
        raise SystemExit(f'FAIL: duplicate request {req}')
    pairs[req]=(ga,pub)
    i+=2
if i!=len(rows): raise SystemExit('FAIL: odd oracle row count')
need=list(range(4,13))
missing=[r for r in need if r not in pairs]
if missing: raise SystemExit(f'FAIL: missing requests {missing}')
extra=sorted(r for r in pairs if r not in need)
if extra and extra!=list(range(13,max(extra)+1)):
    raise SystemExit(f'FAIL: unexpected non-contiguous extra requests {extra}')
m=re.search(r'FA_CAPTURE_COMPLETE R=12 PAIRS=(\d+)',s)
if not m or int(m.group(1))<9: raise SystemExit('FAIL: terminal capture marker')
selected=[]
for req in need: selected.extend(pairs[req])
a.out.write_text('\n'.join(selected)+'\n')
print(f'FA_EXTRACT=PASS REQUESTS=4..12 PAIRS=9 TRAILING_SAME_STREAM={len(extra)}')
