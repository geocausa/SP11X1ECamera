#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib

BASE_HELPER_SHA='f68413ae23cdfbfb84ee39129582e40ecee2fd4b3a37ee242a5bceb4997fb4b4'
BASE_SCHED_SHA='b080113d1a07a2600eb8a06b3e5b045422debe0858577d84ab7d61fae03ff54d'

def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}')
    return s.replace(a,b,1)

ap=argparse.ArgumentParser()
ap.add_argument('helper_in',type=Path); ap.add_argument('schedule_in',type=Path)
ap.add_argument('helper_out',type=Path); ap.add_argument('schedule_out',type=Path)
a=ap.parse_args()

s=a.helper_in.read_text()
need(hashlib.sha256(s.encode()).hexdigest()==BASE_HELPER_SHA,'FM15 helper SHA drift')
s=once(s,'#define FRAME_COUNT 15U','#define FRAME_COUNT 18U','frame count')
s=once(s,'{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2 }',
       '{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1 }','buffer cycle')
s=once(s,'if (argc != 23) {','if (argc != 26) {','argc')
s=once(s,'out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10 out11 out12 out13 out14\\n',
       'out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10 out11 out12 out13 out14 out15 out16 out17\\n','usage')
s=once(s,'TARGETS=1..15','TARGETS=1..18','audit targets')
s=once(s,'if (target <= 12U) {','if (target <= 15U) {','gain publish')
s=once(s,'FM_DQBUF_MISMATCH','FT_DQBUF_MISMATCH','diag label')
s=once(s,'if (i < 11U) {','if (i < 14U) {','requeue')
s=once(s,'ACCEPTED_G=1..15','ACCEPTED_G=1..18','accepted')
s=once(s,'PASS: fifteen-frame transport plus producer-derived R5..R15 and paired TL_BG/3A generations 1..15 (AO collector)',
       'PASS: eighteen-frame transport plus producer-derived R5..R18 and paired TL_BG/3A generations 1..18 (AO collector)','pass')
a.helper_out.write_text(s)

h=a.schedule_in.read_text()
need(hashlib.sha256(h.encode()).hexdigest()==BASE_SCHED_SHA,'FM15 schedule SHA drift')
h=once(h,'#define E003I_DB_FRAME_COUNT 15U','#define E003I_DB_FRAME_COUNT 18U','schedule count')
a.schedule_out.write_text(h)
print('HELPER_SHA='+hashlib.sha256(s.encode()).hexdigest())
print('SCHEDULE_H_SHA='+hashlib.sha256(h.encode()).hexdigest())
