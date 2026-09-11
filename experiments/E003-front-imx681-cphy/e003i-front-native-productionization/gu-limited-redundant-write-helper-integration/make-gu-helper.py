#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='1dc9d1b2e31ca74c983e6bdf48dc66f3780da1ffbfd369e4c455d88d9266d5b1'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    n=s.count(a); need(n==1,f'{label}: count={n}'); return s.replace(a,b,1)
def transform(s):
    s=once(s,'#include "gain-feed.h"','#include "gain-feed.h"\n#include "redundant-write-policy.h"','policy include')
    s=once(s,'\tstruct e003i_cont_schedule_state schedule;\n',
           '\tstruct e003i_cont_schedule_state schedule;\n\tstruct e003i_imx681_controls last_applied_controls;\n\tunsigned int last_applied_valid;\n\tunsigned int physical_write_count;\n\tunsigned int redundant_write_count;\n\tunsigned int changed_shadow_count;\n\tunsigned int bounded_shadow_count;\n','policy state')
    old='''\tif (ev->source_generation > 3U) {
\t\tcompleted = atomic_load_explicit(&ctx->video_completed_generation,
\t\t\t\t\t\t memory_order_acquire);
\t\tif (completed != after_generation)
\t\t\treturn -ETIME;
\t\tprintf("GS_SENSOR_WRITE_SHADOW SOURCE=%u AFTER_G=%u REQUEST=%llu EFFECT_G=%u FLL=%u EXP=%u AGAIN=%u DGAIN=%u MONO_NS=%llu COMPLETED_G=%u\\n",
\t\t       ev->source_generation, after_generation,
\t\t       (unsigned long long)ev->logical_request_frame,
\t\t       ev->expected_effect_generation, ev->controls.frame_length_lines,
\t\t       ev->controls.exposure_lines, ev->controls.analogue_gain_code,
\t\t       ev->controls.digital_gain_code,
\t\t       (unsigned long long)mono_ns(), completed);
\t\tfflush(stdout);
\t\treturn 0;
\t}

\tstart_ns = mono_ns();'''
    new='''\t{
\t\tenum e003i_redundant_write_decision decision =
\t\t\te003i_redundant_write_decide(ev->source_generation,
\t\t\t\tctx->last_applied_valid ? &ctx->last_applied_controls : NULL,
\t\t\t\t&ev->controls);

\t\tif (ev->source_generation <= 3U) {
\t\t\tif (decision != E003I_WRITE_PROVEN_STARTUP)
\t\t\t\treturn -EPROTO;
\t\t} else if (decision == E003I_WRITE_REDUNDANT_ALLOWED) {
\t\t\tprintf("GU_REDUNDANT_WRITE_ALLOW SOURCE=%u AFTER_G=%u REQUEST=%llu EFFECT_G=%u\\n",
\t\t\t       ev->source_generation, after_generation,
\t\t\t       (unsigned long long)ev->logical_request_frame,
\t\t\t       ev->expected_effect_generation);
\t\t\tfflush(stdout);
\t\t} else {
\t\t\tconst char *kind;

\t\t\tif (decision == E003I_WRITE_SHADOW_CHANGED) {
\t\t\t\tkind = "CHANGED";
\t\t\t\tctx->changed_shadow_count++;
\t\t\t} else if (decision == E003I_WRITE_SHADOW_BOUND) {
\t\t\t\tkind = "BOUND";
\t\t\t\tctx->bounded_shadow_count++;
\t\t\t} else {
\t\t\t\treturn -EPROTO;
\t\t\t}
\t\t\tcompleted = atomic_load_explicit(&ctx->video_completed_generation,
\t\t\t\t\t\t memory_order_acquire);
\t\t\tif (completed != after_generation)
\t\t\t\treturn -ETIME;
\t\t\tprintf("GU_SENSOR_WRITE_SHADOW_%s SOURCE=%u AFTER_G=%u REQUEST=%llu EFFECT_G=%u FLL=%u EXP=%u AGAIN=%u DGAIN=%u MONO_NS=%llu COMPLETED_G=%u\\n",
\t\t\t       kind, ev->source_generation, after_generation,
\t\t\t       (unsigned long long)ev->logical_request_frame,
\t\t\t       ev->expected_effect_generation, ev->controls.frame_length_lines,
\t\t\t       ev->controls.exposure_lines, ev->controls.analogue_gain_code,
\t\t\t       ev->controls.digital_gain_code,
\t\t\t       (unsigned long long)mono_ns(), completed);
\t\t\tfflush(stdout);
\t\t\treturn 0;
\t\t}
\t}

\tstart_ns = mono_ns();'''
    s=once(s,old,new,'policy decision block')
    old='''\tif (completed != after_generation)
\t\treturn -ETIME;
\treturn 0;
}

static void *pair_audit_thread'''
    new='''\tif (completed != after_generation)
\t\treturn -ETIME;
\tctx->last_applied_controls = ev->controls;
\tctx->last_applied_valid = 1U;
\tctx->physical_write_count++;
\tif (ev->source_generation > 3U)
\t\tctx->redundant_write_count++;
\treturn 0;
}

static void *pair_audit_thread'''
    s=once(s,old,new,'write accounting')
    old='''\tprintf("GS_SHADOW_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PHYSICAL_WRITES=G1..G3 SHADOW=G4..G26 PENDING=G27 EFFECT_RANGE=G4..G29\\n");
\tfflush(stdout);'''
    new='''\tif (audit.physical_write_count != 3U + audit.redundant_write_count ||
\t    audit.redundant_write_count > 3U ||
\t    audit.redundant_write_count + audit.changed_shadow_count != 3U ||
\t    audit.bounded_shadow_count != 20U)
\t\tpin_until_reboot("limited redundant-write accounting invariant failed");
\tprintf("GU_LIMITED_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PHYSICAL_WRITES=%u REDUNDANT=%u CHANGED_SHADOW=%u BOUND_SHADOW=%u PENDING=G27 EFFECT_RANGE=G4..G29\\n",
\t       audit.physical_write_count, audit.redundant_write_count,
\t       audit.changed_shadow_count, audit.bounded_shadow_count);
\tfflush(stdout);'''
    s=once(s,old,new,'final accounting')
    s=s.replace('GS_BOUNDARY_RELEASE_FAIL','GU_BOUNDARY_RELEASE_FAIL')
    return s
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'GS helper SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('GU_HELPER_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
