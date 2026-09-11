#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib

BASE_HELPER_SHA='24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce'
BASE_SCHED_SHA='092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf'

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
need(hashlib.sha256(s.encode()).hexdigest()==BASE_HELPER_SHA,'FT18 helper SHA drift')
s=once(s,'#define FRAME_COUNT 18U','#define FRAME_COUNT 21U','frame count')
s=once(s,'{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1 }',
       '{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0 }','buffer cycle')
s=once(s,'if (argc != 26) {','if (argc != 29) {','argc')
s=once(s,'out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10 out11 out12 out13 out14 out15 out16 out17\\n',
       'out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10 out11 out12 out13 out14 out15 out16 out17 out18 out19 out20\\n','usage')
s=once(s,'TARGETS=1..18','TARGETS=1..21','audit targets')
s=once(s,'if (target <= 15U) {','if (target <= 18U) {','gain publish')
s=once(s,'FT_DQBUF_MISMATCH','GB_DQBUF_MISMATCH','diag label')
s=once(s,'if (i < 14U) {','if (i < 17U) {','requeue')
s=once(s,'ACCEPTED_G=1..18','ACCEPTED_G=1..21','accepted')
s=once(s,'PASS: eighteen-frame transport plus producer-derived R5..R18 and paired TL_BG/3A generations 1..18 (AO collector)',
       'PASS: twenty-one-frame transport plus producer-derived R5..R21 and paired TL_BG/3A generations 1..21 (AO collector)','pass')
a.helper_out.write_text(s)

h=a.schedule_in.read_text()
need(hashlib.sha256(h.encode()).hexdigest()==BASE_SCHED_SHA,'FT18 schedule SHA drift')
h=once(h,'#define E003I_DB_FRAME_COUNT 18U','#define E003I_DB_FRAME_COUNT 21U','schedule count')
a.schedule_out.write_text(h)
print('HELPER_SHA='+hashlib.sha256(s.encode()).hexdigest())
print('SCHEDULE_H_SHA='+hashlib.sha256(h.encode()).hexdigest())
