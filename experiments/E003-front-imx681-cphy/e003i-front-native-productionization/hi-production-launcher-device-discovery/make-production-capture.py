#!/usr/bin/env python3
from pathlib import Path
import argparse
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
SRC=REPO/'src/front-imx681/userspace/runtime/e003i-hc-caprelease-native-aec.c'
DEFAULT_OUT=REPO/'src/front-imx681/userspace/runtime/front-imx681-production-capture.c'

def one(s,old,new,label):
    if s.count(old)!=1: raise RuntimeError(f'{label}: anchor count {s.count(old)}')
    return s.replace(old,new,1)
def transform(s):
    s=one(s,'#include "native-cap-release-policy.h"\n','#include "native-cap-release-policy.h"\n#include "production-write-policy.h"\n','include')
    s=one(s,'\tunsigned int later_native_write_count;\n\tunsigned int control_ioctl_count;\n',
          '\tunsigned int later_native_write_count;\n\tunsigned int policy_disabled_shadow_count;\n\tenum sp11_front_post_g3_policy post_g3_policy;\n\tunsigned int control_ioctl_count;\n','ctx')
    old='''\t\tif (decision == E003I_HA_APPLY_ONE_NATIVE) {\n\t\t\tprintf("HB_NATIVE_CAP_RELEASE_ALLOW SOURCE=%u AFTER_G=%u REQUEST=%llu EFFECT_G=%u CONV=%llu CAP=%llu FLL=%u EXP=%u AGAIN=%u DGAIN=%u\\n",'''
    new='''\t\tif (decision == E003I_HA_APPLY_ONE_NATIVE &&\n\t\t    !sp11_front_post_g3_apply_allowed(ctx->post_g3_policy, decision)) {\n\t\t\tctx->later_shadow_count++;\n\t\t\tctx->policy_disabled_shadow_count++;\n\t\t\tcompleted = atomic_load_explicit(&ctx->video_completed_generation, memory_order_acquire);\n\t\t\tif (completed != after_generation)\n\t\t\t\treturn -ETIME;\n\t\t\tprintf("PROD_POST_G3_POLICY_SHADOW SOURCE=%u AFTER_G=%u POLICY=%s CONV=%llu CAP=%llu FLL=%u EXP=%u AGAIN=%u DGAIN=%u MONO_NS=%llu COMPLETED_G=%u\\n",\n\t\t\t       ev->source_generation, after_generation,\n\t\t\t       sp11_front_post_g3_policy_name(ctx->post_g3_policy),\n\t\t\t       (unsigned long long)conv, (unsigned long long)cap,\n\t\t\t       ev->controls.frame_length_lines, ev->controls.exposure_lines,\n\t\t\t       ev->controls.analogue_gain_code, ev->controls.digital_gain_code,\n\t\t\t       (unsigned long long)mono_ns(), completed);\n\t\t\tfflush(stdout);\n\t\t\treturn 0;\n\t\t}\n\n\t\tif (decision == E003I_HA_APPLY_ONE_NATIVE) {\n\t\t\tprintf("HB_NATIVE_CAP_RELEASE_ALLOW SOURCE=%u AFTER_G=%u REQUEST=%llu EFFECT_G=%u CONV=%llu CAP=%llu FLL=%u EXP=%u AGAIN=%u DGAIN=%u\\n",'''
    s=one(s,old,new,'policy branch')
    old='''\tsensor = getenv("DB_SUBDEV");\n\tif (sensor == NULL || sensor[0] != '/') {\n\t\tfprintf(stderr, "DB_SUBDEV missing or not absolute\\n");\n\t\treturn 3;\n\t}\n\tvfd = open(video, O_RDWR | O_CLOEXEC);'''
    new='''\tsensor = getenv("DB_SUBDEV");\n\tif (sensor == NULL || sensor[0] != '/') {\n\t\tfprintf(stderr, "DB_SUBDEV missing or not absolute\\n");\n\t\treturn 3;\n\t}\n\tif (sp11_front_parse_post_g3_policy(getenv("SP11_FRONT_POST_G3_WRITE_POLICY"),\n\t\t\t\t\t&post_g3_policy)) {\n\t\tfprintf(stderr, "SP11_FRONT_POST_G3_WRITE_POLICY must be shadow or cap-release-one-shot\\n");\n\t\treturn 4;\n\t}\n\tprintf("PROD_POST_G3_POLICY=%s\\n", sp11_front_post_g3_policy_name(post_g3_policy));\n\tfflush(stdout);\n\tvfd = open(video, O_RDWR | O_CLOEXEC);'''
    # declare local first
    s=one(s,'\tunsigned int i;\n\n\tif (argc != 35) {','\tunsigned int i;\n\tenum sp11_front_post_g3_policy post_g3_policy;\n\n\tif (argc != 35) {','main declaration')
    s=one(s,old,new,'main parse')
    s=one(s,'\taudit.tlbg_prefix = tlbg_prefix; audit.stats3a_prefix = stats3a_prefix;\n',
          '\taudit.tlbg_prefix = tlbg_prefix; audit.stats3a_prefix = stats3a_prefix; audit.post_g3_policy = post_g3_policy;\n','ctx policy set')
    old='''\t    audit.cap_active_shadow_count + audit.unchanged_shadow_count +\n\t    audit.already_applied_shadow_count + audit.horizon_shadow_count !=\n\t    audit.later_shadow_count)'''
    new='''\t    audit.cap_active_shadow_count + audit.unchanged_shadow_count +\n\t    audit.already_applied_shadow_count + audit.horizon_shadow_count +\n\t    audit.policy_disabled_shadow_count != audit.later_shadow_count)'''
    s=one(s,old,new,'accounting')
    old='''\tprintf("HC_NATIVE_CAP_RELEASE_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 CONTROL_IOCTLS=%u LATER_NATIVE_WRITES=%u LATER_SHADOW=%u CAP_ACTIVE_SHADOW=%u UNCHANGED_SHADOW=%u ALREADY_APPLIED_SHADOW=%u HORIZON_SHADOW=%u PENDING=G27 APPLY_EFFECT_MAX=G27\\n",\n\t       audit.control_ioctl_count, audit.later_native_write_count,\n\t       audit.later_shadow_count, audit.cap_active_shadow_count,\n\t       audit.unchanged_shadow_count, audit.already_applied_shadow_count,\n\t       audit.horizon_shadow_count);'''
    new='''\tprintf("PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 POLICY=%s CONTROL_IOCTLS=%u LATER_NATIVE_WRITES=%u LATER_SHADOW=%u POLICY_DISABLED_SHADOW=%u CAP_ACTIVE_SHADOW=%u UNCHANGED_SHADOW=%u ALREADY_APPLIED_SHADOW=%u HORIZON_SHADOW=%u PENDING=G27 APPLY_EFFECT_MAX=G27\\n",\n\t       sp11_front_post_g3_policy_name(audit.post_g3_policy),\n\t       audit.control_ioctl_count, audit.later_native_write_count,\n\t       audit.later_shadow_count, audit.policy_disabled_shadow_count,\n\t       audit.cap_active_shadow_count, audit.unchanged_shadow_count,\n\t       audit.already_applied_shadow_count, audit.horizon_shadow_count);'''
    s=one(s,old,new,'summary')
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=DEFAULT_OUT);a=ap.parse_args()
    out=transform(SRC.read_text());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(out)
    print(f'HI_PRODUCTION_CAPTURE_SOURCE={a.output}')
if __name__=='__main__':main()
