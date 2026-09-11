#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='1dc9d1b2e31ca74c983e6bdf48dc66f3780da1ffbfd369e4c455d88d9266d5b1'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    n=s.count(a); need(n==1,f'{label}: count={n}'); return s.replace(a,b,1)
def transform(s):
    s=once(s,'#include "gain-feed.h"','#include "gain-feed.h"\n#include "minimal-dgain-sentinel.h"','sentinel include')
    s=once(s,'\tstruct e003i_cont_schedule_state schedule;\n',
           '\tstruct e003i_cont_schedule_state schedule;\n\tstruct e003i_imx681_controls last_applied_controls;\n\tunsigned int last_applied_valid;\n\tunsigned int control_ioctl_count;\n\tunsigned int sentinel_write_count;\n\tunsigned int sentinel_suppressed_count;\n\tunsigned int bounded_shadow_count;\n','sentinel state')
    s=once(s,'\tuint64_t start_ns, end_ns;\n\tunsigned int completed;\n\tint rc;',
           '\tuint64_t start_ns, end_ns;\n\tunsigned int completed;\n\tconst struct e003i_imx681_controls *write_controls = &ev->controls;\n\tstruct e003i_imx681_controls sentinel_controls;\n\tint rc;','release locals')
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

\tstart_ns = mono_ns();
\trc = apply_sensor_controls(ctx->sensor_fd, &ev->controls);'''
    new='''\tif (ev->source_generation == 4U) {
\t\tenum e003i_gw_decision decision = e003i_gw_make_sentinel(
\t\t\tev->source_generation,
\t\t\tctx->last_applied_valid ? &ctx->last_applied_controls : NULL,
\t\t\t&ev->controls, &sentinel_controls);

\t\tif (decision == E003I_GW_APPLY_SENTINEL) {
\t\t\twrite_controls = &sentinel_controls;
\t\t\tprintf("GX_SENTINEL_WRITE_ALLOW SOURCE=4 AFTER_G=%u REQUEST=%llu EFFECT_G=%u NATIVE_DGAIN=%u SENTINEL_DGAIN=%u\\n",
\t\t\t       after_generation, (unsigned long long)ev->logical_request_frame,
\t\t\t       ev->expected_effect_generation, ev->controls.digital_gain_code,
\t\t\t       sentinel_controls.digital_gain_code);
\t\t\tfflush(stdout);
\t\t} else {
\t\t\tctx->sentinel_suppressed_count++;
\t\t\tcompleted = atomic_load_explicit(&ctx->video_completed_generation,
\t\t\t\t\t\t memory_order_acquire);
\t\t\tif (completed != after_generation)
\t\t\t\treturn -ETIME;
\t\t\tprintf("GX_SENTINEL_SUPPRESSED SOURCE=4 AFTER_G=%u DECISION=%u NATIVE_DGAIN=%u MONO_NS=%llu COMPLETED_G=%u\\n",
\t\t\t       after_generation, (unsigned int)decision,
\t\t\t       ev->controls.digital_gain_code,
\t\t\t       (unsigned long long)mono_ns(), completed);
\t\t\tfflush(stdout);
\t\t\treturn 0;
\t\t}
\t} else if (ev->source_generation > 4U) {
\t\tctx->bounded_shadow_count++;
\t\tcompleted = atomic_load_explicit(&ctx->video_completed_generation,
\t\t\t\t\t\t memory_order_acquire);
\t\tif (completed != after_generation)
\t\t\treturn -ETIME;
\t\tprintf("GX_SENSOR_WRITE_SHADOW SOURCE=%u AFTER_G=%u REQUEST=%llu EFFECT_G=%u FLL=%u EXP=%u AGAIN=%u DGAIN=%u MONO_NS=%llu COMPLETED_G=%u\\n",
\t\t       ev->source_generation, after_generation,
\t\t       (unsigned long long)ev->logical_request_frame,
\t\t       ev->expected_effect_generation, ev->controls.frame_length_lines,
\t\t       ev->controls.exposure_lines, ev->controls.analogue_gain_code,
\t\t       ev->controls.digital_gain_code,
\t\t       (unsigned long long)mono_ns(), completed);
\t\tfflush(stdout);
\t\treturn 0;
\t}

\tstart_ns = mono_ns();
\trc = apply_sensor_controls(ctx->sensor_fd, write_controls);'''
    s=once(s,old,new,'sentinel write block')
    s=s.replace('ev->expected_effect_generation, ev->controls.frame_length_lines,\n\t       ev->controls.exposure_lines, ev->controls.analogue_gain_code,\n\t       ev->controls.digital_gain_code,',
                'ev->expected_effect_generation, write_controls->frame_length_lines,\n\t       write_controls->exposure_lines, write_controls->analogue_gain_code,\n\t       write_controls->digital_gain_code,',1)
    old='''\tif (completed != after_generation)
\t\treturn -ETIME;
\treturn 0;
}

static void *pair_audit_thread'''
    new='''\tif (completed != after_generation)
\t\treturn -ETIME;
\tctx->last_applied_controls = *write_controls;
\tctx->last_applied_valid = 1U;
\tctx->control_ioctl_count++;
\tif (ev->source_generation == 4U)
\t\tctx->sentinel_write_count++;
\treturn 0;
}

static void *pair_audit_thread'''
    s=once(s,old,new,'write accounting')
    old='''\tprintf("GS_SHADOW_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PHYSICAL_WRITES=G1..G3 SHADOW=G4..G26 PENDING=G27 EFFECT_RANGE=G4..G29\\n");
\tfflush(stdout);'''
    new='''\tif (audit.control_ioctl_count != 3U + audit.sentinel_write_count ||
\t    audit.sentinel_write_count > 1U ||
\t    audit.sentinel_write_count + audit.sentinel_suppressed_count != 1U ||
\t    audit.bounded_shadow_count != 22U)
\t\tpin_until_reboot("minimal sentinel accounting invariant failed");
\tprintf("GX_SENTINEL_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 CONTROL_IOCTLS=%u SENTINEL_WRITES=%u SENTINEL_SUPPRESSED=%u BOUND_SHADOW=%u PENDING=G27 EFFECT_RANGE=G4..G29\\n",
\t       audit.control_ioctl_count, audit.sentinel_write_count,
\t       audit.sentinel_suppressed_count, audit.bounded_shadow_count);
\tfflush(stdout);'''
    s=once(s,old,new,'final sentinel accounting')
    s=s.replace('GS_BOUNDARY_RELEASE_FAIL','GX_BOUNDARY_RELEASE_FAIL')
    return s
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'GS helper SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('GX_HELPER_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
