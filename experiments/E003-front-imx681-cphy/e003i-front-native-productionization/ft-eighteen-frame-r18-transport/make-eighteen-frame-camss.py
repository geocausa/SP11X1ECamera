#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib

BASE_SHA='592f31d591ff9542f8f67d8228e5f45808afb63088368107ce56422b4d8e34d6'

def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}')
    return s.replace(a,b,1)

def transform(s):
    s=once(s,'\tstruct camss_buffer *video_done_fifteenth;\n',
           '\tstruct camss_buffer *video_done_fifteenth;\n\tstruct camss_buffer *video_done_sixteenth;\n\tstruct camss_buffer *video_done_seventeenth;\n\tstruct camss_buffer *video_done_eighteenth;\n','done fields')
    s=once(s,'\tbool epoch0_steady_twelfth_seen;\n',
           '\tbool epoch0_steady_twelfth_seen;\n\tbool epoch0_steady_thirteenth_seen;\n\tbool epoch0_steady_fourteenth_seen;\n\tbool epoch0_steady_fifteenth_seen;\n','epoch flags')
    s=once(s,'\tbool video_fifteenth_seen;\n',
           '\tbool video_fifteenth_seen;\n\tbool video_sixteenth_seen;\n\tbool video_seventeenth_seen;\n\tbool video_eighteenth_seen;\n','video flags')
    s=once(s,'\tbool slot0_reusable_eighth;\n',
           '\tbool slot0_reusable_eighth;\n\tbool slot1_reused_seventh;\n\tbool slot1_reusable_eighth;\n\tbool slot0_reused_eighth;\n\tbool slot0_reusable_ninth;\n\tbool slot1_reused_eighth;\n\tbool slot1_reusable_ninth;\n','slot flags')
    s=once(s,'\tstruct camss_buffer *video_requeued_eleventh;\n',
           '\tstruct camss_buffer *video_requeued_eleventh;\n\tstruct camss_buffer *video_requeued_twelfth;\n\tstruct camss_buffer *video_requeued_thirteenth;\n\tstruct camss_buffer *video_requeued_fourteenth;\n','requeue fields')
    s=once(s,'\tbool live_requeue_eleventh_acquired;\n',
           '\tbool live_requeue_eleventh_acquired;\n\tbool live_requeue_twelfth_acquired;\n\tbool live_requeue_thirteenth_acquired;\n\tbool live_requeue_fourteenth_acquired;\n','requeue acquired')
    s=once(s,'frame_number < 7 || frame_number > 15 || request_id != frame_number ||',
           'frame_number < 7 || frame_number > 18 || request_id != frame_number ||','steady bound')
    s=once(s,'\tstruct camss_x1e_pix_capsule_materialized *materialized_r15 = NULL;\n',
           '\tstruct camss_x1e_pix_capsule_materialized *materialized_r15 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r16 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r17 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r18 = NULL;\n','materialized locals')
    s=once(s,'\tstruct camss_buffer *thirteenth = NULL, *fourteenth = NULL, *fifteenth = NULL;\n',
           '\tstruct camss_buffer *thirteenth = NULL, *fourteenth = NULL, *fifteenth = NULL;\n\tstruct camss_buffer *sixteenth = NULL, *seventeenth = NULL, *eighteenth = NULL;\n','buffer locals')
    s=once(s,'if (!result || frame_limit < 1 || frame_limit > 15)',
           'if (!result || frame_limit < 1 || frame_limit > 18)','frame limit')
    s=once(s,'\tif (frame_limit >= 15)\n\t\tmaterialized_r15 = kzalloc_obj(*materialized_r15, GFP_KERNEL);\n',
           '\tif (frame_limit >= 15)\n\t\tmaterialized_r15 = kzalloc_obj(*materialized_r15, GFP_KERNEL);\n\tif (frame_limit >= 16)\n\t\tmaterialized_r16 = kzalloc_obj(*materialized_r16, GFP_KERNEL);\n\tif (frame_limit >= 17)\n\t\tmaterialized_r17 = kzalloc_obj(*materialized_r17, GFP_KERNEL);\n\tif (frame_limit >= 18)\n\t\tmaterialized_r18 = kzalloc_obj(*materialized_r18, GFP_KERNEL);\n','alloc')
    s=once(s,'\t    (frame_limit >= 15 && !materialized_r15)) {\n',
           '\t    (frame_limit >= 15 && !materialized_r15) ||\n\t    (frame_limit >= 16 && !materialized_r16) ||\n\t    (frame_limit >= 17 && !materialized_r17) ||\n\t    (frame_limit >= 18 && !materialized_r18)) {\n','alloc check')

    frame15='''\tif (frame_limit >= 15) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 15, 15, 0, req->video[2], materialized_r15,
\t\t\t&epoch0_seq, video_seq, &fifteenth, &result->video_done_fifteenth);
\t\tif (fifteenth) {
\t\t\tresult->video_requeued_eleventh = fifteenth;
\t\t\tresult->live_requeue_eleventh_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_twelfth_seen = true;
\t\tresult->video_fifteenth_seen = true;
\t\tresult->slot0_reused_seventh = true;
\t\tresult->slot0_reusable_eighth = true;
\t}

'''
    ext=frame15+'''\tif (frame_limit >= 16) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 16, 16, 1, req->video[3], materialized_r16,
\t\t\t&epoch0_seq, video_seq, &sixteenth, &result->video_done_sixteenth);
\t\tif (sixteenth) {
\t\t\tresult->video_requeued_twelfth = sixteenth;
\t\t\tresult->live_requeue_twelfth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_thirteenth_seen = true;
\t\tresult->video_sixteenth_seen = true;
\t\tresult->slot1_reused_seventh = true;
\t\tresult->slot1_reusable_eighth = true;
\t}

\tif (frame_limit >= 17) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 17, 17, 0, req->video[0], materialized_r17,
\t\t\t&epoch0_seq, video_seq, &seventeenth, &result->video_done_seventeenth);
\t\tif (seventeenth) {
\t\t\tresult->video_requeued_thirteenth = seventeenth;
\t\t\tresult->live_requeue_thirteenth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_fourteenth_seen = true;
\t\tresult->video_seventeenth_seen = true;
\t\tresult->slot0_reused_eighth = true;
\t\tresult->slot0_reusable_ninth = true;
\t}

\tif (frame_limit >= 18) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 18, 18, 1, req->video[1], materialized_r18,
\t\t\t&epoch0_seq, video_seq, &eighteenth, &result->video_done_eighteenth);
\t\tif (eighteenth) {
\t\t\tresult->video_requeued_fourteenth = eighteenth;
\t\t\tresult->live_requeue_fourteenth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_fifteenth_seen = true;
\t\tresult->video_eighteenth_seen = true;
\t\tresult->slot1_reused_eighth = true;
\t\tresult->slot1_reusable_ninth = true;
\t}

'''
    s=once(s,frame15,ext,'frames16-18')

    s=once(s,'\t\tresult->video_done_fifteenth = NULL;\n',
           '\t\tresult->video_done_fifteenth = NULL;\n\t\tresult->video_done_sixteenth = NULL;\n\t\tresult->video_done_seventeenth = NULL;\n\t\tresult->video_done_eighteenth = NULL;\n','unsafe nulls')
    s=once(s,'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r15);\n',
           'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r18);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r17);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r16);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r15);\n','release')
    s=once(s,'out_free_inputs:\n\tkfree(materialized_r15);\n',
           'out_free_inputs:\n\tkfree(materialized_r18);\n\tkfree(materialized_r17);\n\tkfree(materialized_r16);\n\tkfree(materialized_r15);\n','free')
    s=once(s,'camss_x1e_pix_runner_frames(camss, &req, &result, 15)',
           'camss_x1e_pix_runner_frames(camss, &req, &result, 18)','worker count')
    s=once(s,'\t    result.video_done_fifteenth != video2 ||\n',
           '\t    result.video_done_fifteenth != video2 || result.video_done_sixteenth != video3 ||\n\t    result.video_done_seventeenth != video0 || result.video_done_eighteenth != video1 ||\n','worker done')
    s=once(s,'\t    result.video_requeued_eleventh != video2 || result.live_completed != 15 ||\n',
           '\t    result.video_requeued_eleventh != video2 || result.video_requeued_twelfth != video3 ||\n\t    result.video_requeued_thirteenth != video0 || result.video_requeued_fourteenth != video1 ||\n\t    result.live_completed != 18 ||\n','worker requeue')
    s=once(s,'\t    !result.live_requeue_eleventh_acquired || !result.epoch0_seen ||\n',
           '\t    !result.live_requeue_eleventh_acquired || !result.live_requeue_twelfth_acquired ||\n\t    !result.live_requeue_thirteenth_acquired || !result.live_requeue_fourteenth_acquired ||\n\t    !result.epoch0_seen ||\n','worker acquired')
    s=once(s,'\t    !result.epoch0_steady_tenth_seen || !result.epoch0_steady_eleventh_seen ||\n\t    !result.epoch0_steady_twelfth_seen || !result.video_seen ||\n',
           '\t    !result.epoch0_steady_tenth_seen || !result.epoch0_steady_eleventh_seen ||\n\t    !result.epoch0_steady_twelfth_seen || !result.epoch0_steady_thirteenth_seen ||\n\t    !result.epoch0_steady_fourteenth_seen || !result.epoch0_steady_fifteenth_seen ||\n\t    !result.video_seen ||\n','worker epoch')
    s=once(s,'\t    !result.video_thirteenth_seen || !result.video_fourteenth_seen ||\n\t    !result.video_fifteenth_seen || !result.slot0_reusable ||\n',
           '\t    !result.video_thirteenth_seen || !result.video_fourteenth_seen ||\n\t    !result.video_fifteenth_seen || !result.video_sixteenth_seen ||\n\t    !result.video_seventeenth_seen || !result.video_eighteenth_seen || !result.slot0_reusable ||\n','worker video')
    s=once(s,'\t    !result.slot0_reused_seventh || !result.slot0_reusable_eighth) {\n',
           '\t    !result.slot0_reused_seventh || !result.slot0_reusable_eighth ||\n\t    !result.slot1_reused_seventh || !result.slot1_reusable_eighth ||\n\t    !result.slot0_reused_eighth || !result.slot0_reusable_ninth ||\n\t    !result.slot1_reused_eighth || !result.slot1_reusable_ninth) {\n','worker slots')
    s=once(s,'bounded fifteen-frame live requeue','bounded eighteen-frame live requeue','log')
    s=once(s,'\t\tif (result.live_requeue_eleventh_acquired && result.live_completed < 15)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_eleventh);\n',
           '\t\tif (result.live_requeue_eleventh_acquired && result.live_completed < 15)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_eleventh);\n\t\tif (result.live_requeue_twelfth_acquired && result.live_completed < 16)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_twelfth);\n\t\tif (result.live_requeue_thirteenth_acquired && result.live_completed < 17)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_thirteenth);\n\t\tif (result.live_requeue_fourteenth_acquired && result.live_completed < 18)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_fourteenth);\n','error buffers')
    return s

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'FM15 source SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('PATCHED_SHA='+hashlib.sha256(out.encode()).hexdigest())

if __name__=='__main__': main()
