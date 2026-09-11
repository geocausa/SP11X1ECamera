#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_HELPER_SHA='df20afacd4f839250b0338de22600b8d89a09b6320f4c685fdfcfa76e7fa6b79'
BASE_SCHED_SHA='71a88a4ebacb453a84e9eeaebd6f21354b73b3363f18a47d719336a3500c993b'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}'); return s.replace(a,b,1)
ap=argparse.ArgumentParser(); ap.add_argument('helper_in',type=Path); ap.add_argument('schedule_in',type=Path); ap.add_argument('helper_out',type=Path); ap.add_argument('schedule_out',type=Path); a=ap.parse_args()
s=a.helper_in.read_text(); need(hashlib.sha256(s.encode()).hexdigest()==BASE_HELPER_SHA,'GH24 helper SHA drift')
s=once(s,'#define FRAME_COUNT 24U','#define FRAME_COUNT 27U','frame count')
s=once(s,'{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3 }','{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2 }','buffer cycle')
s=once(s,'if (argc != 32) {','if (argc != 35) {','argc')
s=once(s,'out21 out22 out23\\n','out21 out22 out23 out24 out25 out26\\n','usage')
s=once(s,'TARGETS=1..24','TARGETS=1..27','audit targets')
s=once(s,'if (target <= 21U) {','if (target <= 24U) {','gain publish')
s=once(s,'GH_DQBUF_MISMATCH','GN_DQBUF_MISMATCH','diag label')
s=once(s,'if (i < 20U) {','if (i < 23U) {','requeue')
s=once(s,'ACCEPTED_G=1..24','ACCEPTED_G=1..27','accepted')
s=once(s,'PASS: twenty-four-frame transport plus producer-derived R5..R24 and paired TL_BG/3A generations 1..24 (AO collector)','PASS: twenty-seven-frame transport plus producer-derived R5..R27 and paired TL_BG/3A generations 1..27 (AO collector)','pass')
a.helper_out.write_text(s)
h=a.schedule_in.read_text(); need(hashlib.sha256(h.encode()).hexdigest()==BASE_SCHED_SHA,'GH24 schedule SHA drift')
h=once(h,'#define E003I_DB_FRAME_COUNT 24U','#define E003I_DB_FRAME_COUNT 27U','schedule count'); a.schedule_out.write_text(h)
print('HELPER_SHA='+hashlib.sha256(s.encode()).hexdigest()); print('SCHEDULE_H_SHA='+hashlib.sha256(h.encode()).hexdigest())
