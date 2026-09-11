#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_HELPER_SHA='8cb43bb96c629ce25c08014192898cc30e21abe226d101d06600f25dba829af5'
BASE_SCHED_SHA='fca5d49b12524a9f24bfca673072cf3bbb85d33645045d3a2cb4b155b58c6aae'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}')
    return s.replace(a,b,1)
ap=argparse.ArgumentParser()
ap.add_argument('helper_in',type=Path); ap.add_argument('schedule_in',type=Path)
ap.add_argument('helper_out',type=Path); ap.add_argument('schedule_out',type=Path)
a=ap.parse_args()
s=a.helper_in.read_text(); need(hashlib.sha256(s.encode()).hexdigest()==BASE_HELPER_SHA,'GB21 helper SHA drift')
s=once(s,'#define FRAME_COUNT 21U','#define FRAME_COUNT 24U','frame count')
s=once(s,'{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0 }',
       '{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3 }','buffer cycle')
s=once(s,'if (argc != 29) {','if (argc != 32) {','argc')
s=once(s,'out18 out19 out20\\n','out18 out19 out20 out21 out22 out23\\n','usage')
s=once(s,'TARGETS=1..21','TARGETS=1..24','audit targets')
s=once(s,'if (target <= 18U) {','if (target <= 21U) {','gain publish')
s=once(s,'GB_DQBUF_MISMATCH','GH_DQBUF_MISMATCH','diag label')
s=once(s,'if (i < 17U) {','if (i < 20U) {','requeue')
s=once(s,'ACCEPTED_G=1..21','ACCEPTED_G=1..24','accepted')
s=once(s,'PASS: twenty-one-frame transport plus producer-derived R5..R21 and paired TL_BG/3A generations 1..21 (AO collector)',
       'PASS: twenty-four-frame transport plus producer-derived R5..R24 and paired TL_BG/3A generations 1..24 (AO collector)','pass')
a.helper_out.write_text(s)
h=a.schedule_in.read_text(); need(hashlib.sha256(h.encode()).hexdigest()==BASE_SCHED_SHA,'GB21 schedule SHA drift')
h=once(h,'#define E003I_DB_FRAME_COUNT 21U','#define E003I_DB_FRAME_COUNT 24U','schedule count')
a.schedule_out.write_text(h)
print('HELPER_SHA='+hashlib.sha256(s.encode()).hexdigest())
print('SCHEDULE_H_SHA='+hashlib.sha256(h.encode()).hexdigest())
