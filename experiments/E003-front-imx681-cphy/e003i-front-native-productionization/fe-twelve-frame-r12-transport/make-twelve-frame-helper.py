#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_HELPER_SHA='b5ecb959b95c63eb38c1e7da98e1f37e9c71d9cc4abe4ee6fbc5456e9bd67993'
BASE_SCHED_SHA='6d6cfc6833c035d545d5d626a4af479717227732cf94ef301422e6c74f3dd113'
def need(x,m):
 if not x: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
 need(s.count(a)==1,f'{label}: count={s.count(a)}');return s.replace(a,b,1)
ap=argparse.ArgumentParser();ap.add_argument('helper_in',type=Path);ap.add_argument('schedule_in',type=Path);ap.add_argument('helper_out',type=Path);ap.add_argument('schedule_out',type=Path);a=ap.parse_args()
s=a.helper_in.read_text();need(hashlib.sha256(s.encode()).hexdigest()==BASE_HELPER_SHA,'EY11 helper SHA drift')
s=once(s,'#define FRAME_COUNT 11U','#define FRAME_COUNT 12U','frame count')
s=once(s,'{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2 }','{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3 }','buffer cycle')
s=once(s,'if (argc != 19) {','if (argc != 20) {','argc')
s=once(s,'out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10\\n','out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10 out11\\n','usage')
s=once(s,'TARGETS=1..11','TARGETS=1..12','audit targets')
s=once(s,'if (target <= 8U) {','if (target <= 9U) {','gain publish')
s=once(s,'EY_DQBUF_MISMATCH','FE_DQBUF_MISMATCH','diag label')
s=once(s,'if (i < 7U) {','if (i < 8U) {','requeue')
s=once(s,'ACCEPTED_G=1..11','ACCEPTED_G=1..12','accepted')
s=once(s,'PASS: eleven-frame transport plus producer-derived R5..R11 and paired TL_BG/3A generations 1..11 (AO collector)','PASS: twelve-frame transport plus producer-derived R5..R12 and paired TL_BG/3A generations 1..12 (AO collector)','pass')
a.helper_out.write_text(s)
h=a.schedule_in.read_text();need(hashlib.sha256(h.encode()).hexdigest()==BASE_SCHED_SHA,'EY11 schedule SHA drift')
h=once(h,'#define E003I_DB_FRAME_COUNT 11U','#define E003I_DB_FRAME_COUNT 12U','schedule count');a.schedule_out.write_text(h)
print('HELPER_SHA='+hashlib.sha256(s.encode()).hexdigest());print('SCHEDULE_H_SHA='+hashlib.sha256(h.encode()).hexdigest())
