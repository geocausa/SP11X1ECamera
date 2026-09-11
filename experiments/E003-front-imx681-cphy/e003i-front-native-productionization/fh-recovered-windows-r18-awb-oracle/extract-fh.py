#!/usr/bin/env python3
from pathlib import Path
import argparse,re
ap=argparse.ArgumentParser()
ap.add_argument('log',type=Path)
ap.add_argument('out',type=Path)
a=ap.parse_args()
s=a.log.read_text(errors='replace').replace('\r','')
rows=[x.strip() for x in s.splitlines() if x.strip().startswith(('FA_GA ','FA_PUB '))]
pairs={}
i=0
while i+1<len(rows):
    ga,pub=rows[i:i+2]
    mg=re.search(r'\breq=(\d+)\b',ga);mp=re.search(r'\breq=(\d+)\b',pub)
    if not mg or not mp or mg.group(1)!=mp.group(1):
        raise SystemExit(f'FAIL pair mismatch raw row {i}')
    req=int(mg.group(1))
    if req in pairs: raise SystemExit(f'FAIL duplicate R{req}')
    pairs[req]=(ga,pub);i+=2
if i!=len(rows): raise SystemExit('FAIL odd row count')
need=list(range(4,19))
if sorted(pairs)!=need: raise SystemExit(f'FAIL requests {sorted(pairs)}')
m=re.search(r'FA_CAPTURE_COMPLETE R=12 PAIRS=(\d+)',s)
if not m or int(m.group(1))!=15: raise SystemExit('FAIL final pair marker')
out=[]
for req in need: out.extend(pairs[req])
a.out.write_text('\n'.join(out)+'\n')
print('FH_EXTRACT=PASS REQUESTS=4..18 PAIRS=15 SAME_FA_STREAM=1')
