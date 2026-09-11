#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_HELPER_SHA='6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d'
BASE_SCHED_SHA='47890d6b37bc6a484310d983a8a303798b56d06eea6f2287dc4df254eaf5eb14'
def need(x,m):
    if not x: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}');return s.replace(a,b,1)
ap=argparse.ArgumentParser();ap.add_argument('helper_in',type=Path);ap.add_argument('schedule_in',type=Path);ap.add_argument('helper_out',type=Path);ap.add_argument('schedule_out',type=Path);a=ap.parse_args()
s=a.helper_in.read_text();need(hashlib.sha256(s.encode()).hexdigest()==BASE_HELPER_SHA,'ES9 helper SHA drift')
s=once(s,'#define FRAME_COUNT 9U','#define FRAME_COUNT 11U','frame count')
s=once(s,'{ 0, 1, 2, 3, 0, 1, 2, 3, 0 }','{ 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2 }','buffer cycle')
s=once(s,'if (argc != 17) {','if (argc != 19) {','argc')
s=once(s,'out0 out1 out2 out3 out4 out5 out6 out7 out8\\n','out0 out1 out2 out3 out4 out5 out6 out7 out8 out9 out10\\n','usage')
s=once(s,'TARGETS=1..9','TARGETS=1..11','audit targets')
s=once(s,'if (target <= 6U) {','if (target <= 8U) {','gain publish bound')
s=once(s,'if (b.index != expect_index[i] || plane.bytesused != QC10C_BYTES || b.sequence != i)\n\t\t\tpin_until_reboot("unexpected completed buffer ordering");',
'''if (b.index != expect_index[i] || plane.bytesused != QC10C_BYTES || b.sequence != i) {\n\t\t\tfprintf(stderr, "EY_DQBUF_MISMATCH LOOP=%u EXPECT_INDEX=%u EXPECT_BYTES=%u EXPECT_SEQUENCE=%u ACTUAL_INDEX=%u ACTUAL_BYTES=%u ACTUAL_SEQUENCE=%u\\n",\n\t\t\t\ti, expect_index[i], QC10C_BYTES, i, b.index, plane.bytesused, b.sequence);\n\t\t\tfflush(stderr);\n\t\t\tpin_until_reboot("unexpected completed buffer ordering");\n\t\t}''','DQBUF diagnostic')
s=once(s,'if (i < 5U) {','if (i < 7U) {','requeue window')
s=once(s,'ACCEPTED_G=1..9','ACCEPTED_G=1..11','AEC accepted')
s=once(s,'PASS: nine-frame transport plus producer-derived R5..R9 and paired TL_BG/3A generations 1..9 (AO collector)','PASS: eleven-frame transport plus producer-derived R5..R11 and paired TL_BG/3A generations 1..11 (AO collector)','pass marker')
a.helper_out.write_text(s)
h=a.schedule_in.read_text();need(hashlib.sha256(h.encode()).hexdigest()==BASE_SCHED_SHA,'ES9 schedule SHA drift')
h=once(h,'#define E003I_DB_FRAME_COUNT 9U','#define E003I_DB_FRAME_COUNT 11U','schedule frame count');a.schedule_out.write_text(h)
print('HELPER_SHA='+hashlib.sha256(s.encode()).hexdigest());print('SCHEDULE_H_SHA='+hashlib.sha256(h.encode()).hexdigest())
