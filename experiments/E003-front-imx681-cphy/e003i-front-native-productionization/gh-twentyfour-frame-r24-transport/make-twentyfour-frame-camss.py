#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib

BASE_SHA='d09cd0bf6d91ed7c51c981455d9643d1f486cb0374fec23a375376b83e837fb4'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}')
    return s.replace(a,b,1)

def transform(s):
    s=once(s,'\tstruct camss_buffer *video_done_twentyfirst;\n',
           '\tstruct camss_buffer *video_done_twentyfirst;\n\tstruct camss_buffer *video_done_twentysecond;\n\tstruct camss_buffer *video_done_twentythird;\n\tstruct camss_buffer *video_done_twentyfourth;\n','done fields')
    s=once(s,'\tbool epoch0_steady_eighteenth_seen;\n',
           '\tbool epoch0_steady_eighteenth_seen;\n\tbool epoch0_steady_nineteenth_seen;\n\tbool epoch0_steady_twentieth_seen;\n\tbool epoch0_steady_twentyfirst_seen;\n','epoch flags')
    s=once(s,'\tbool video_twentyfirst_seen;\n',
           '\tbool video_twentyfirst_seen;\n\tbool video_twentysecond_seen;\n\tbool video_twentythird_seen;\n\tbool video_twentyfourth_seen;\n','video flags')
    s=once(s,'\tbool slot0_reusable_eleventh;\n',
           '\tbool slot0_reusable_eleventh;\n\tbool slot1_reused_tenth;\n\tbool slot1_reusable_eleventh;\n\tbool slot0_reused_eleventh;\n\tbool slot0_reusable_twelfth;\n\tbool slot1_reused_eleventh;\n\tbool slot1_reusable_twelfth;\n','slot flags')
    s=once(s,'\tstruct camss_buffer *video_requeued_seventeenth;\n',
           '\tstruct camss_buffer *video_requeued_seventeenth;\n\tstruct camss_buffer *video_requeued_eighteenth;\n\tstruct camss_buffer *video_requeued_nineteenth;\n\tstruct camss_buffer *video_requeued_twentieth;\n','requeue fields')
    s=once(s,'\tbool live_requeue_seventeenth_acquired;\n',
           '\tbool live_requeue_seventeenth_acquired;\n\tbool live_requeue_eighteenth_acquired;\n\tbool live_requeue_nineteenth_acquired;\n\tbool live_requeue_twentieth_acquired;\n','requeue acquired')
    s=once(s,'frame_number < 7 || frame_number > 21 || request_id != frame_number ||',
           'frame_number < 7 || frame_number > 24 || request_id != frame_number ||','steady bound')
    s=once(s,'\tstruct camss_x1e_pix_capsule_materialized *materialized_r21 = NULL;\n',
           '\tstruct camss_x1e_pix_capsule_materialized *materialized_r21 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r22 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r23 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r24 = NULL;\n','materialized locals')
    s=once(s,'\tstruct camss_buffer *nineteenth = NULL, *twentieth = NULL, *twentyfirst = NULL;\n',
           '\tstruct camss_buffer *nineteenth = NULL, *twentieth = NULL, *twentyfirst = NULL;\n\tstruct camss_buffer *twentysecond = NULL, *twentythird = NULL, *twentyfourth = NULL;\n','buffer locals')
    s=once(s,'if (!result || frame_limit < 1 || frame_limit > 21)',
           'if (!result || frame_limit < 1 || frame_limit > 24)','frame limit')
    s=once(s,'\tif (frame_limit >= 21)\n\t\tmaterialized_r21 = kzalloc_obj(*materialized_r21, GFP_KERNEL);\n',
           '\tif (frame_limit >= 21)\n\t\tmaterialized_r21 = kzalloc_obj(*materialized_r21, GFP_KERNEL);\n\tif (frame_limit >= 22)\n\t\tmaterialized_r22 = kzalloc_obj(*materialized_r22, GFP_KERNEL);\n\tif (frame_limit >= 23)\n\t\tmaterialized_r23 = kzalloc_obj(*materialized_r23, GFP_KERNEL);\n\tif (frame_limit >= 24)\n\t\tmaterialized_r24 = kzalloc_obj(*materialized_r24, GFP_KERNEL);\n','alloc')
    s=once(s,'\t    (frame_limit >= 21 && !materialized_r21)) {\n',
           '\t    (frame_limit >= 21 && !materialized_r21) ||\n\t    (frame_limit >= 22 && !materialized_r22) ||\n\t    (frame_limit >= 23 && !materialized_r23) ||\n\t    (frame_limit >= 24 && !materialized_r24)) {\n','alloc check')
    frame21='''\tif (frame_limit >= 21) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 21, 21, 0, req->video[0], materialized_r21,
\t\t\t&epoch0_seq, video_seq, &twentyfirst, &result->video_done_twentyfirst);
\t\tif (twentyfirst) {
\t\t\tresult->video_requeued_seventeenth = twentyfirst;
\t\t\tresult->live_requeue_seventeenth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_eighteenth_seen = true;
\t\tresult->video_twentyfirst_seen = true;
\t\tresult->slot0_reused_tenth = true;
\t\tresult->slot0_reusable_eleventh = true;
\t}

'''
    ext=frame21+'''\tif (frame_limit >= 22) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 22, 22, 1, req->video[1], materialized_r22,
\t\t\t&epoch0_seq, video_seq, &twentysecond, &result->video_done_twentysecond);
\t\tif (twentysecond) {
\t\t\tresult->video_requeued_eighteenth = twentysecond;
\t\t\tresult->live_requeue_eighteenth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_nineteenth_seen = true;
\t\tresult->video_twentysecond_seen = true;
\t\tresult->slot1_reused_tenth = true;
\t\tresult->slot1_reusable_eleventh = true;
\t}

\tif (frame_limit >= 23) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 23, 23, 0, req->video[2], materialized_r23,
\t\t\t&epoch0_seq, video_seq, &twentythird, &result->video_done_twentythird);
\t\tif (twentythird) {
\t\t\tresult->video_requeued_nineteenth = twentythird;
\t\t\tresult->live_requeue_nineteenth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_twentieth_seen = true;
\t\tresult->video_twentythird_seen = true;
\t\tresult->slot0_reused_eleventh = true;
\t\tresult->slot0_reusable_twelfth = true;
\t}

\tif (frame_limit >= 24) {
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
    s=once(s,frame21,ext,'frames22-24')
    s=once(s,'\t\tresult->video_done_twentyfirst = NULL;\n',
           '\t\tresult->video_done_twentyfirst = NULL;\n\t\tresult->video_done_twentysecond = NULL;\n\t\tresult->video_done_twentythird = NULL;\n\t\tresult->video_done_twentyfourth = NULL;\n','unsafe nulls')
    s=once(s,'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r21);\n',
           'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r24);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r23);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r22);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r21);\n','release')
    s=once(s,'out_free_inputs:\n\tkfree(materialized_r21);\n',
           'out_free_inputs:\n\tkfree(materialized_r24);\n\tkfree(materialized_r23);\n\tkfree(materialized_r22);\n\tkfree(materialized_r21);\n','free')
    s=once(s,'camss_x1e_pix_runner_frames(camss, &req, &result, 21)',
           'camss_x1e_pix_runner_frames(camss, &req, &result, 24)','worker count')
    s=once(s,'\t    result.video_done_twentyfirst != video0 ||\n',
           '\t    result.video_done_twentyfirst != video0 || result.video_done_twentysecond != video1 ||\n\t    result.video_done_twentythird != video2 || result.video_done_twentyfourth != video3 ||\n','worker done')
    s=once(s,'\t    result.video_requeued_seventeenth != video0 || result.live_completed != 21 ||\n',
           '\t    result.video_requeued_seventeenth != video0 || result.video_requeued_eighteenth != video1 ||\n\t    result.video_requeued_nineteenth != video2 || result.video_requeued_twentieth != video3 ||\n\t    result.live_completed != 24 ||\n','worker requeue')
    s=once(s,'\t    !result.live_requeue_fifteenth_acquired || !result.live_requeue_sixteenth_acquired ||\n\t    !result.live_requeue_seventeenth_acquired || !result.epoch0_seen ||\n',
           '\t    !result.live_requeue_fifteenth_acquired || !result.live_requeue_sixteenth_acquired ||\n\t    !result.live_requeue_seventeenth_acquired || !result.live_requeue_eighteenth_acquired ||\n\t    !result.live_requeue_nineteenth_acquired || !result.live_requeue_twentieth_acquired ||\n\t    !result.epoch0_seen ||\n','worker acquired')
    s=once(s,'\t    !result.epoch0_steady_sixteenth_seen || !result.epoch0_steady_seventeenth_seen ||\n\t    !result.epoch0_steady_eighteenth_seen || !result.video_seen ||\n',
           '\t    !result.epoch0_steady_sixteenth_seen || !result.epoch0_steady_seventeenth_seen ||\n\t    !result.epoch0_steady_eighteenth_seen || !result.epoch0_steady_nineteenth_seen ||\n\t    !result.epoch0_steady_twentieth_seen || !result.epoch0_steady_twentyfirst_seen || !result.video_seen ||\n','worker epoch')
    s=once(s,'\t    !result.video_nineteenth_seen || !result.video_twentieth_seen ||\n\t    !result.video_twentyfirst_seen || !result.slot0_reusable ||\n',
           '\t    !result.video_nineteenth_seen || !result.video_twentieth_seen ||\n\t    !result.video_twentyfirst_seen || !result.video_twentysecond_seen ||\n\t    !result.video_twentythird_seen || !result.video_twentyfourth_seen || !result.slot0_reusable ||\n','worker video')
    s=once(s,'\t    !result.slot1_reused_ninth || !result.slot1_reusable_tenth ||\n\t    !result.slot0_reused_tenth || !result.slot0_reusable_eleventh) {\n',
           '\t    !result.slot1_reused_ninth || !result.slot1_reusable_tenth ||\n\t    !result.slot0_reused_tenth || !result.slot0_reusable_eleventh ||\n\t    !result.slot1_reused_tenth || !result.slot1_reusable_eleventh ||\n\t    !result.slot0_reused_eleventh || !result.slot0_reusable_twelfth ||\n\t    !result.slot1_reused_eleventh || !result.slot1_reusable_twelfth) {\n','worker slots')
    s=once(s,'bounded twenty-one-frame live requeue','bounded twenty-four-frame live requeue','log')
    s=once(s,'\t\tif (result.live_requeue_seventeenth_acquired && result.live_completed < 21)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_seventeenth);\n',
           '\t\tif (result.live_requeue_seventeenth_acquired && result.live_completed < 21)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_seventeenth);\n\t\tif (result.live_requeue_eighteenth_acquired && result.live_completed < 22)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_eighteenth);\n\t\tif (result.live_requeue_nineteenth_acquired && result.live_completed < 23)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_nineteenth);\n\t\tif (result.live_requeue_twentieth_acquired && result.live_completed < 24)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_twentieth);\n','error buffers')
    return s

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'GB21 source SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('PATCHED_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
