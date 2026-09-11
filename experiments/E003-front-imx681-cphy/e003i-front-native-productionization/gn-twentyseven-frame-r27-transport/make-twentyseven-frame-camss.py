#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='b47e9ca26d4591b55d5208eaf40edcef1794d4d6d7fb2e3c33e72edf5f527386'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}'); return s.replace(a,b,1)
def transform(s):
    s=once(s,'\tstruct camss_buffer *video_done_twentyfourth;\n','\tstruct camss_buffer *video_done_twentyfourth;\n\tstruct camss_buffer *video_done_twentyfifth;\n\tstruct camss_buffer *video_done_twentysixth;\n\tstruct camss_buffer *video_done_twentyseventh;\n','done fields')
    s=once(s,'\tbool epoch0_steady_twentyfirst_seen;\n','\tbool epoch0_steady_twentyfirst_seen;\n\tbool epoch0_steady_twentysecond_seen;\n\tbool epoch0_steady_twentythird_seen;\n\tbool epoch0_steady_twentyfourth_seen;\n','epoch flags')
    s=once(s,'\tbool video_twentyfourth_seen;\n','\tbool video_twentyfourth_seen;\n\tbool video_twentyfifth_seen;\n\tbool video_twentysixth_seen;\n\tbool video_twentyseventh_seen;\n','video flags')
    s=once(s,'\tbool slot1_reusable_twelfth;\n','\tbool slot1_reusable_twelfth;\n\tbool slot0_reused_twelfth;\n\tbool slot0_reusable_thirteenth;\n\tbool slot1_reused_twelfth;\n\tbool slot1_reusable_thirteenth;\n\tbool slot0_reused_thirteenth;\n\tbool slot0_reusable_fourteenth;\n','slot flags')
    s=once(s,'\tstruct camss_buffer *video_requeued_twentieth;\n','\tstruct camss_buffer *video_requeued_twentieth;\n\tstruct camss_buffer *video_requeued_twentyfirst;\n\tstruct camss_buffer *video_requeued_twentysecond;\n\tstruct camss_buffer *video_requeued_twentythird;\n','requeue fields')
    s=once(s,'\tbool live_requeue_twentieth_acquired;\n','\tbool live_requeue_twentieth_acquired;\n\tbool live_requeue_twentyfirst_acquired;\n\tbool live_requeue_twentysecond_acquired;\n\tbool live_requeue_twentythird_acquired;\n','requeue acquired')
    s=once(s,'frame_number < 7 || frame_number > 24 || request_id != frame_number ||','frame_number < 7 || frame_number > 27 || request_id != frame_number ||','steady bound')
    s=once(s,'\tstruct camss_x1e_pix_capsule_materialized *materialized_r24 = NULL;\n','\tstruct camss_x1e_pix_capsule_materialized *materialized_r24 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r25 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r26 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r27 = NULL;\n','materialized locals')
    s=once(s,'\tstruct camss_buffer *twentysecond = NULL, *twentythird = NULL, *twentyfourth = NULL;\n','\tstruct camss_buffer *twentysecond = NULL, *twentythird = NULL, *twentyfourth = NULL;\n\tstruct camss_buffer *twentyfifth = NULL, *twentysixth = NULL, *twentyseventh = NULL;\n','buffer locals')
    s=once(s,'if (!result || frame_limit < 1 || frame_limit > 24)','if (!result || frame_limit < 1 || frame_limit > 27)','frame limit')
    s=once(s,'\tif (frame_limit >= 24)\n\t\tmaterialized_r24 = kzalloc_obj(*materialized_r24, GFP_KERNEL);\n','\tif (frame_limit >= 24)\n\t\tmaterialized_r24 = kzalloc_obj(*materialized_r24, GFP_KERNEL);\n\tif (frame_limit >= 25)\n\t\tmaterialized_r25 = kzalloc_obj(*materialized_r25, GFP_KERNEL);\n\tif (frame_limit >= 26)\n\t\tmaterialized_r26 = kzalloc_obj(*materialized_r26, GFP_KERNEL);\n\tif (frame_limit >= 27)\n\t\tmaterialized_r27 = kzalloc_obj(*materialized_r27, GFP_KERNEL);\n','alloc')
    s=once(s,'\t    (frame_limit >= 24 && !materialized_r24)) {\n','\t    (frame_limit >= 24 && !materialized_r24) ||\n\t    (frame_limit >= 25 && !materialized_r25) ||\n\t    (frame_limit >= 26 && !materialized_r26) ||\n\t    (frame_limit >= 27 && !materialized_r27)) {\n','alloc check')
    frame24='''\tif (frame_limit >= 24) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 24, 24, 1, req->video[3], materialized_r24,
\t\t\t&epoch0_seq, video_seq, &twentyfourth, &result->video_done_twentyfourth);
\t\tif (twentyfourth) {
\t\t\tresult->video_requeued_twentieth = twentyfourth;
\t\t\tresult->live_requeue_twentieth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_twentyfirst_seen = true;
\t\tresult->video_twentyfourth_seen = true;
\t\tresult->slot1_reused_eleventh = true;
\t\tresult->slot1_reusable_twelfth = true;
\t}

'''
    ext=frame24+'''\tif (frame_limit >= 25) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 25, 25, 0, req->video[0], materialized_r25,
\t\t\t&epoch0_seq, video_seq, &twentyfifth, &result->video_done_twentyfifth);
\t\tif (twentyfifth) {
\t\t\tresult->video_requeued_twentyfirst = twentyfifth;
\t\t\tresult->live_requeue_twentyfirst_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_twentysecond_seen = true;
\t\tresult->video_twentyfifth_seen = true;
\t\tresult->slot0_reused_twelfth = true;
\t\tresult->slot0_reusable_thirteenth = true;
\t}

\tif (frame_limit >= 26) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 26, 26, 1, req->video[1], materialized_r26,
\t\t\t&epoch0_seq, video_seq, &twentysixth, &result->video_done_twentysixth);
\t\tif (twentysixth) {
\t\t\tresult->video_requeued_twentysecond = twentysixth;
\t\t\tresult->live_requeue_twentysecond_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_twentythird_seen = true;
\t\tresult->video_twentysixth_seen = true;
\t\tresult->slot1_reused_twelfth = true;
\t\tresult->slot1_reusable_thirteenth = true;
\t}

\tif (frame_limit >= 27) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 27, 27, 0, req->video[2], materialized_r27,
\t\t\t&epoch0_seq, video_seq, &twentyseventh, &result->video_done_twentyseventh);
\t\tif (twentyseventh) {
\t\t\tresult->video_requeued_twentythird = twentyseventh;
\t\t\tresult->live_requeue_twentythird_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_twentyfourth_seen = true;
\t\tresult->video_twentyseventh_seen = true;
\t\tresult->slot0_reused_thirteenth = true;
\t\tresult->slot0_reusable_fourteenth = true;
\t}

'''
    s=once(s,frame24,ext,'frames25-27')
    s=once(s,'\t\tresult->video_done_twentyfourth = NULL;\n','\t\tresult->video_done_twentyfourth = NULL;\n\t\tresult->video_done_twentyfifth = NULL;\n\t\tresult->video_done_twentysixth = NULL;\n\t\tresult->video_done_twentyseventh = NULL;\n','unsafe nulls')
    s=once(s,'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r24);\n','out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r27);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r26);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r25);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r24);\n','release')
    s=once(s,'out_free_inputs:\n\tkfree(materialized_r24);\n','out_free_inputs:\n\tkfree(materialized_r27);\n\tkfree(materialized_r26);\n\tkfree(materialized_r25);\n\tkfree(materialized_r24);\n','free')
    s=once(s,'camss_x1e_pix_runner_frames(camss, &req, &result, 24)','camss_x1e_pix_runner_frames(camss, &req, &result, 27)','worker count')
    s=once(s,'\t    result.video_done_twentythird != video2 || result.video_done_twentyfourth != video3 ||\n','\t    result.video_done_twentythird != video2 || result.video_done_twentyfourth != video3 ||\n\t    result.video_done_twentyfifth != video0 || result.video_done_twentysixth != video1 ||\n\t    result.video_done_twentyseventh != video2 ||\n','worker done')
    s=once(s,'\t    result.video_requeued_nineteenth != video2 || result.video_requeued_twentieth != video3 ||\n\t    result.live_completed != 24 ||\n','\t    result.video_requeued_nineteenth != video2 || result.video_requeued_twentieth != video3 ||\n\t    result.video_requeued_twentyfirst != video0 || result.video_requeued_twentysecond != video1 ||\n\t    result.video_requeued_twentythird != video2 || result.live_completed != 27 ||\n','worker requeue')
    s=once(s,'\t    !result.live_requeue_nineteenth_acquired || !result.live_requeue_twentieth_acquired ||\n\t    !result.epoch0_seen ||\n','\t    !result.live_requeue_nineteenth_acquired || !result.live_requeue_twentieth_acquired ||\n\t    !result.live_requeue_twentyfirst_acquired || !result.live_requeue_twentysecond_acquired ||\n\t    !result.live_requeue_twentythird_acquired || !result.epoch0_seen ||\n','worker acquired')
    s=once(s,'\t    !result.epoch0_steady_twentieth_seen || !result.epoch0_steady_twentyfirst_seen || !result.video_seen ||\n','\t    !result.epoch0_steady_twentieth_seen || !result.epoch0_steady_twentyfirst_seen ||\n\t    !result.epoch0_steady_twentysecond_seen || !result.epoch0_steady_twentythird_seen ||\n\t    !result.epoch0_steady_twentyfourth_seen || !result.video_seen ||\n','worker epoch')
    s=once(s,'\t    !result.video_twentythird_seen || !result.video_twentyfourth_seen || !result.slot0_reusable ||\n','\t    !result.video_twentythird_seen || !result.video_twentyfourth_seen ||\n\t    !result.video_twentyfifth_seen || !result.video_twentysixth_seen ||\n\t    !result.video_twentyseventh_seen || !result.slot0_reusable ||\n','worker video')
    s=once(s,'\t    !result.slot1_reused_eleventh || !result.slot1_reusable_twelfth) {\n','\t    !result.slot1_reused_eleventh || !result.slot1_reusable_twelfth ||\n\t    !result.slot0_reused_twelfth || !result.slot0_reusable_thirteenth ||\n\t    !result.slot1_reused_twelfth || !result.slot1_reusable_thirteenth ||\n\t    !result.slot0_reused_thirteenth || !result.slot0_reusable_fourteenth) {\n','worker slots')
    s=once(s,'bounded twenty-four-frame live requeue','bounded twenty-seven-frame live requeue','log')
    s=once(s,'\t\tif (result.live_requeue_twentieth_acquired && result.live_completed < 24)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_twentieth);\n','\t\tif (result.live_requeue_twentieth_acquired && result.live_completed < 24)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_twentieth);\n\t\tif (result.live_requeue_twentyfirst_acquired && result.live_completed < 25)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_twentyfirst);\n\t\tif (result.live_requeue_twentysecond_acquired && result.live_completed < 26)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_twentysecond);\n\t\tif (result.live_requeue_twentythird_acquired && result.live_completed < 27)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_twentythird);\n','error buffers')
    return s
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'GH24 source SHA drift')
    out=transform(b.decode()); a.dst.write_text(out); print('BASE_SHA='+BASE_SHA); print('PATCHED_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
