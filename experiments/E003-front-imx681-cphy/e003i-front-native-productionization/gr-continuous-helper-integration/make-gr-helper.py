#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='32ecff0848a3f47fe149ead36ccf63eec26a8c78180075129253a65792dedf1e'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    n=s.count(a); need(n==1,f'{label}: count={n}'); return s.replace(a,b,1)
def transform(s):
    s=once(s,'#include "native-db-schedule.h"','#include "continuous-db-schedule.h"','schedule include')
    s=once(s,'\tstruct e003i_db_schedule_state schedule;','\tstruct e003i_cont_schedule_state schedule;','state type')
    s=once(s,'\tstruct e003i_db_apply_event apply_event[FRAME_COUNT];','\tstruct e003i_cont_apply_event apply_event[FRAME_COUNT];','event array type')
    s=once(s,'\tstruct e003i_db_apply_event *ev = &ctx->apply_event[after_generation - 1U];','\tstruct e003i_cont_apply_event *ev = &ctx->apply_event[after_generation - 1U];','release event type')
    s=s.replace('e003i_db_schedule_fail','e003i_cont_schedule_fail')
    s=s.replace('e003i_db_schedule_queue','e003i_cont_schedule_queue')
    s=s.replace('e003i_db_schedule_release','e003i_cont_schedule_release')
    s=s.replace('e003i_db_schedule_init','e003i_cont_schedule_init')
    s=once(s,'if (target >= 2U && target <= 4U) {','if (target >= 2U) {','continuous release range')
    s=s.replace('DZ_BOUNDARY_RELEASE_FAIL','GR_BOUNDARY_RELEASE_FAIL')
    old='''\tif (audit.schedule.failed || audit.schedule.queued_generation != FRAME_COUNT ||
\t    audit.schedule.released_writes != E003I_DB_WRITTEN_SOURCE_GENERATIONS)
\t\tpin_until_reboot("native-AEC delayed sensor schedule did not release exactly G1..G3");
\tprintf("DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..27 WRITES=%u RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6\\n",
\t       audit.schedule.released_writes);
\tfflush(stdout);'''
    new='''\tif (audit.schedule.failed || audit.schedule.queued_generation != FRAME_COUNT ||
\t    audit.schedule.released_source_generation != FRAME_COUNT - 1U ||
\t    !audit.schedule.pending_valid[(FRAME_COUNT - 1U) % E003I_CONT_PENDING_SLOTS] ||
\t    audit.schedule.pending_generation[(FRAME_COUNT - 1U) % E003I_CONT_PENDING_SLOTS] != FRAME_COUNT ||
\t    audit.schedule.pending_valid[FRAME_COUNT % E003I_CONT_PENDING_SLOTS])
\t\tpin_until_reboot("continuous delayed sensor schedule did not close bounded G1..G26 releases with G27 pending");
\tprintf("GR_CONT_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PENDING=G27 EFFECT_RANGE=G4..G29\\n");
\tfflush(stdout);'''
    s=once(s,old,new,'final schedule acceptance')
    # Remaining audit-loop API/type and delay constant references.
    s=s.replace('struct e003i_db_apply_event','struct e003i_cont_apply_event')
    s=s.replace('E003I_DB_STATS_TO_REQUEST_DELAY','E003I_CONT_STATS_TO_REQUEST_DELAY')
    s=s.replace('E003I_DB_WRITE_TO_EFFECT_DELAY','E003I_CONT_WRITE_TO_EFFECT_DELAY')
    s=s.replace('ctx->schedule.released_writes','ctx->schedule.released_source_generation')
    return s
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'GO helper SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('GR_HELPER_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
