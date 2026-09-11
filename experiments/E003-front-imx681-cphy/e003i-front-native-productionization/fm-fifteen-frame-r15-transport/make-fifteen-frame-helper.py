#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_HELPER_SHA='e6f2a792dc070c9d6a726817f30d3a8b1da56b554debccbe2832bd0b18ae47de'
BASE_SCHED_SHA='1872289bdd280cc067034c4425234b9bfa334e27dce62841ffb540b061f86690'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}');return s.replace(a,b,1)
ap=argparse.ArgumentParser();ap.add_argument('helper_in',type=Path);ap.add_argument('schedule_in',type=Path);ap.add_argument('helper_out',type=Path);ap.add_argument('schedule_out',type=Path);a=ap.parse_args()
s=a.helper_in.read_text();need(hashlib.sha256(s.encode()).hexdigest()==BASE_HELPER_SHA,'FE12 helper SHA drift')
s=once(s,'#define FRAME_COUNT 12U','#define FRAME_COUNT 15U','frame count')
s=once(s,'{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3 }','{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2 }','buffer cycle')
s=once(s,'if (argc != 20) {','if (argc != 23) {','argc')
s=once(s,'out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10 out11\\n','out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10 out11 out12 out13 out14\\n','usage')
s=once(s,'TARGETS=1..12','TARGETS=1..15','audit targets')
s=once(s,'if (target <= 9U) {','if (target <= 12U) {','gain publish')
s=once(s,'FE_DQBUF_MISMATCH','FM_DQBUF_MISMATCH','diag label')
s=once(s,'if (i < 8U) {','if (i < 11U) {','requeue')
s=once(s,'ACCEPTED_G=1..12','ACCEPTED_G=1..15','accepted')
s=once(s,'PASS: twelve-frame transport plus producer-derived R5..R12 and paired TL_BG/3A generations 1..12 (AO collector)','PASS: fifteen-frame transport plus producer-derived R5..R15 and paired TL_BG/3A generations 1..15 (AO collector)','pass')
a.helper_out.write_text(s)
h=a.schedule_in.read_text();need(hashlib.sha256(h.encode()).hexdigest()==BASE_SCHED_SHA,'FE12 schedule SHA drift')
h=once(h,'#define E003I_DB_FRAME_COUNT 12U','#define E003I_DB_FRAME_COUNT 15U','schedule count')
a.schedule_out.write_text(h)
print('HELPER_SHA='+hashlib.sha256(s.encode()).hexdigest())
print('SCHEDULE_H_SHA='+hashlib.sha256(h.encode()).hexdigest())
