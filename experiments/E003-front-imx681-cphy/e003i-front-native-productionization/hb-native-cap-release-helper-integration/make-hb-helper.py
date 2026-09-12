#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='1dc9d1b2e31ca74c983e6bdf48dc66f3780da1ffbfd369e4c455d88d9266d5b1'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    n=s.count(a); need(n==1,f'{label}: count={n}'); return s.replace(a,b,1)
def transform(s):
    s=once(s,'#include "gain-feed.h"','#include "gain-feed.h"\n#include "native-cap-release-policy.h"','HA include')
    s=once(s,'\tstruct e003i_cont_schedule_state schedule;\n',
           '\tstruct e003i_cont_schedule_state schedule;\n'
           '\tstruct e003i_imx681_controls last_applied_controls;\n'
           '\tunsigned int last_applied_valid;\n'
           '\tunsigned int later_native_write_applied;\n'
           '\tunsigned int later_native_write_count;\n'
           '\tunsigned int control_ioctl_count;\n'
           '\tunsigned int later_shadow_count;\n'
           '\tunsigned int cap_active_shadow_count;\n'
           '\tunsigned int unchanged_shadow_count;\n'
           '\tunsigned int already_applied_shadow_count;\n','HA state')
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
    new='''\tif (ev->source_generation > 3U) {
\t\tconst struct e003i_raw_control_output *native =
\t\t\t&ctx->aec_output[ev->source_generation - 1U];
\t\tenum e003i_ha_decision decision = e003i_ha_decide(
\t\t\tev->source_generation, ctx->later_native_write_applied,
\t\t\tctx->last_applied_valid ? &ctx->last_applied_controls : NULL,
\t\t\tnative);
\t\tuint64_t conv = native->raw.request.convergence.linear[E003I_LANE_SHORT];
\t\tuint64_t cap = native->raw.request.capped.linear[E003I_LANE_SHORT];

\t\tif (decision == E003I_HA_APPLY_ONE_NATIVE) {
\t\t\tprintf("HB_NATIVE_CAP_RELEASE_ALLOW SOURCE=%u AFTER_G=%u REQUEST=%llu EFFECT_G=%u CONV=%llu CAP=%llu FLL=%u EXP=%u AGAIN=%u DGAIN=%u\\n",
\t\t\t       ev->source_generation, after_generation,
\t\t\t       (unsigned long long)ev->logical_request_frame,
\t\t\t       ev->expected_effect_generation,
\t\t\t       (unsigned long long)conv, (unsigned long long)cap,
\t\t\t       ev->controls.frame_length_lines, ev->controls.exposure_lines,
\t\t\t       ev->controls.analogue_gain_code, ev->controls.digital_gain_code);
\t\t\tfflush(stdout);
\t\t} else if (decision == E003I_HA_SHADOW_CAP_ACTIVE ||
\t\t\t   decision == E003I_HA_SHADOW_UNCHANGED ||
\t\t\t   decision == E003I_HA_SHADOW_ALREADY_APPLIED) {
\t\t\tctx->later_shadow_count++;
\t\t\tif (decision == E003I_HA_SHADOW_CAP_ACTIVE)
\t\t\t\tctx->cap_active_shadow_count++;
\t\t\telse if (decision == E003I_HA_SHADOW_UNCHANGED)
\t\t\t\tctx->unchanged_shadow_count++;
\t\t\telse
\t\t\t\tctx->already_applied_shadow_count++;
\t\t\tcompleted = atomic_load_explicit(&ctx->video_completed_generation,
\t\t\t\t\t\t memory_order_acquire);
\t\t\tif (completed != after_generation)
\t\t\t\treturn -ETIME;
\t\t\tprintf("HB_NATIVE_CAP_RELEASE_SHADOW SOURCE=%u AFTER_G=%u DECISION=%u CONV=%llu CAP=%llu FLL=%u EXP=%u AGAIN=%u DGAIN=%u MONO_NS=%llu COMPLETED_G=%u\\n",
\t\t\t       ev->source_generation, after_generation, (unsigned int)decision,
\t\t\t       (unsigned long long)conv, (unsigned long long)cap,
\t\t\t       ev->controls.frame_length_lines, ev->controls.exposure_lines,
\t\t\t       ev->controls.analogue_gain_code, ev->controls.digital_gain_code,
\t\t\t       (unsigned long long)mono_ns(), completed);
\t\t\tfflush(stdout);
\t\t\treturn 0;
\t\t} else {
\t\t\treturn -EPROTO;
\t\t}
\t}

\tstart_ns = mono_ns();'''
    s=once(s,old,new,'HA release policy block')
    old='''\tif (completed != after_generation)
\t\treturn -ETIME;
\treturn 0;
}

static void *pair_audit_thread'''
    new='''\tif (completed != after_generation)
\t\treturn -ETIME;
\tctx->last_applied_controls = ev->controls;
\tctx->last_applied_valid = 1U;
\tctx->control_ioctl_count++;
\tif (ev->source_generation > 3U) {
\t\tctx->later_native_write_applied = 1U;
\t\tctx->later_native_write_count++;
\t}
\treturn 0;
}

static void *pair_audit_thread'''
    s=once(s,old,new,'HA write accounting')
    old='''\tprintf("GS_SHADOW_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PHYSICAL_WRITES=G1..G3 SHADOW=G4..G26 PENDING=G27 EFFECT_RANGE=G4..G29\\n");
\tfflush(stdout);'''
    new='''\tif (audit.control_ioctl_count != 3U + audit.later_native_write_count ||
\t    audit.later_native_write_count > 1U ||
\t    audit.later_shadow_count + audit.later_native_write_count != 23U ||
\t    audit.cap_active_shadow_count + audit.unchanged_shadow_count +
\t    audit.already_applied_shadow_count != audit.later_shadow_count)
\t\tpin_until_reboot("native cap-release accounting invariant failed");
\tprintf("HB_NATIVE_CAP_RELEASE_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 CONTROL_IOCTLS=%u LATER_NATIVE_WRITES=%u LATER_SHADOW=%u CAP_ACTIVE_SHADOW=%u UNCHANGED_SHADOW=%u ALREADY_APPLIED_SHADOW=%u PENDING=G27 EFFECT_RANGE=G4..G29\\n",
\t       audit.control_ioctl_count, audit.later_native_write_count,
\t       audit.later_shadow_count, audit.cap_active_shadow_count,
\t       audit.unchanged_shadow_count, audit.already_applied_shadow_count);
\tfflush(stdout);'''
    s=once(s,old,new,'HA final accounting')
    s=s.replace('GS_BOUNDARY_RELEASE_FAIL','HB_BOUNDARY_RELEASE_FAIL')
    return s
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'GS helper SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('HB_HELPER_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
