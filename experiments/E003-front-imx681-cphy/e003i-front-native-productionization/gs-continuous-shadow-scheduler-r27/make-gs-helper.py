#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='7f597f69cb4b5c7230521996db8a5574091c997c76e1b0b322f7dacbd3402e55'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    n=s.count(a); need(n==1,f'{label}: count={n}'); return s.replace(a,b,1)
def transform(s):
    anchor='''\tstart_ns = mono_ns();
\trc = apply_sensor_controls(ctx->sensor_fd, &ev->controls);
\tend_ns = mono_ns();'''
    repl='''\tif (ev->source_generation > 3U) {
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
\trc = apply_sensor_controls(ctx->sensor_fd, &ev->controls);
\tend_ns = mono_ns();'''
    s=once(s,anchor,repl,'shadow suppression')
    s=s.replace('GR_BOUNDARY_RELEASE_FAIL','GS_BOUNDARY_RELEASE_FAIL')
    s=once(s,'GR_CONT_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PENDING=G27 EFFECT_RANGE=G4..G29','GS_SHADOW_SCHEDULE_PASS ACCEPTED_G=1..27 RELEASED_SOURCES=G1..G26 PHYSICAL_WRITES=G1..G3 SHADOW=G4..G26 PENDING=G27 EFFECT_RANGE=G4..G29','pass marker')
    return s
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'GR helper SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('GS_HELPER_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
