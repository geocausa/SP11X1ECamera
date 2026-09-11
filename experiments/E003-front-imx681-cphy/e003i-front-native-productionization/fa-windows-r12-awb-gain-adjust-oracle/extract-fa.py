#!/usr/bin/env python3
from pathlib import Path
import argparse,re
ap=argparse.ArgumentParser();ap.add_argument('log',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
s=a.log.read_text(errors='replace').replace('\r','')
rows=[line.strip() for line in s.splitlines() if line.strip().startswith(('FA_GA ','FA_PUB '))]
if len(rows)!=18: raise SystemExit(f'FAIL: expected 18 oracle rows, got {len(rows)}')
req=[]
for i in range(0,18,2):
    ga,pub=rows[i:i+2]
    mg=re.search(r'\breq=(\d+)\b',ga);mp=re.search(r'\breq=(\d+)\b',pub)
    if not mg or not mp or mg.group(1)!=mp.group(1): raise SystemExit(f'FAIL: pair mismatch at {i//2}')
    req.append(int(mg.group(1)))
if req!=list(range(4,13)): raise SystemExit(f'FAIL: request sequence {req}')
if 'FA_CAPTURE_COMPLETE R=12 PAIRS=9' not in s: raise SystemExit('FAIL: terminal capture marker')
a.out.write_text('\n'.join(rows)+'\n')
print('FA_EXTRACT=PASS REQUESTS=4..12 PAIRS=9')
