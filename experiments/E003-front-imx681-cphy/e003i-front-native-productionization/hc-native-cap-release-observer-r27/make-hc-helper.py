#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='5582c49f577b5639859b9326eb2affa70046b7c4bcb8328061fac0f998c5d6bd'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    n=s.count(a); need(n==1,f'{label}: count={n}'); return s.replace(a,b,1)
def transform(s):
    s=once(s,'\tunsigned int already_applied_shadow_count;\n',
           '\tunsigned int already_applied_shadow_count;\n\tunsigned int horizon_shadow_count;\n','horizon counter')
    anchor='''\t\tuint64_t conv = native->raw.request.convergence.linear[E003I_LANE_SHORT];
\t\tuint64_t cap = native->raw.request.capped.linear[E003I_LANE_SHORT];

\t\tif (decision == E003I_HA_APPLY_ONE_NATIVE) {'''
    repl='''\t\tuint64_t conv = native->raw.request.convergence.linear[E003I_LANE_SHORT];
\t\tuint64_t cap = native->raw.request.capped.linear[E003I_LANE_SHORT];

\t\t/* HC must keep the N+2 optical effect inside the 27-frame evidence window. */
\t\tif (ev->source_generation > 24U) {
\t\t\tctx->later_shadow_count++;
\t\t\tctx->horizon_shadow_count++;
\t\t\tcompleted = atomic_load_explicit(&ctx->video_completed_generation,
\t\t\t\t\t\t memory_order_acquire);
\t\t\tif (completed != after_generation)
\t\t\t\treturn -ETIME;
\t\t\tprintf("HC_CAP_RELEASE_HORIZON_SHADOW SOURCE=%u AFTER_G=%u CONV=%llu CAP=%llu EFFECT_G=%u MONO_NS=%llu COMPLETED_G=%u\\n",
\t\t\t       ev->source_generation, after_generation,
\t\t\t       (unsigned long long)conv, (unsigned long long)cap,
\t\t\t       ev->expected_effect_generation,
\t\t\t       (unsigned long long)mono_ns(), completed);
\t\t\tfflush(stdout);
\t\t\treturn 0;
\t\t}

\t\tif (decision == E003I_HA_APPLY_ONE_NATIVE) {'''
    s=once(s,anchor,repl,'effect horizon guard')
    old='''\t    audit.cap_active_shadow_count + audit.unchanged_shadow_count +
\t    audit.already_applied_shadow_count != audit.later_shadow_count)
\t\tpin_until_reboot("native cap-release accounting invariant failed");
\tprintf("HB_NATIVE_CAP_RELEASE_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 CONTROL_IOCTLS=%u LATER_NATIVE_WRITES=%u LATER_SHADOW=%u CAP_ACTIVE_SHADOW=%u UNCHANGED_SHADOW=%u ALREADY_APPLIED_SHADOW=%u PENDING=G27 EFFECT_RANGE=G4..G29\\n",
\t       audit.control_ioctl_count, audit.later_native_write_count,
\t       audit.later_shadow_count, audit.cap_active_shadow_count,
\t       audit.unchanged_shadow_count, audit.already_applied_shadow_count);'''
    new='''\t    audit.cap_active_shadow_count + audit.unchanged_shadow_count +
\t    audit.already_applied_shadow_count + audit.horizon_shadow_count !=
\t    audit.later_shadow_count)
\t\tpin_until_reboot("native cap-release accounting invariant failed");
\tprintf("HC_NATIVE_CAP_RELEASE_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 CONTROL_IOCTLS=%u LATER_NATIVE_WRITES=%u LATER_SHADOW=%u CAP_ACTIVE_SHADOW=%u UNCHANGED_SHADOW=%u ALREADY_APPLIED_SHADOW=%u HORIZON_SHADOW=%u PENDING=G27 APPLY_EFFECT_MAX=G27\\n",
\t       audit.control_ioctl_count, audit.later_native_write_count,
\t       audit.later_shadow_count, audit.cap_active_shadow_count,
\t       audit.unchanged_shadow_count, audit.already_applied_shadow_count,
\t       audit.horizon_shadow_count);'''
    s=once(s,old,new,'HC final accounting')
    return s
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'HB helper SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('HC_HELPER_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
