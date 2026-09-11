#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='deee56e61090bba938f602a7baeae054435762e6312e47d2cac9dbf9a210f15d'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}')
    return s.replace(a,b,1)
def transform(s):
    s=once(s,'\tstruct camss_buffer *video_done_twelfth;\n',
           '\tstruct camss_buffer *video_done_twelfth;\n\tstruct camss_buffer *video_done_thirteenth;\n\tstruct camss_buffer *video_done_fourteenth;\n\tstruct camss_buffer *video_done_fifteenth;\n','done fields')
    s=once(s,'\tbool epoch0_steady_ninth_seen;\n',
           '\tbool epoch0_steady_ninth_seen;\n\tbool epoch0_steady_tenth_seen;\n\tbool epoch0_steady_eleventh_seen;\n\tbool epoch0_steady_twelfth_seen;\n','epoch flags')
    s=once(s,'\tbool video_twelfth_seen;\n',
           '\tbool video_twelfth_seen;\n\tbool video_thirteenth_seen;\n\tbool video_fourteenth_seen;\n\tbool video_fifteenth_seen;\n','video flags')
    s=once(s,'\tbool slot1_reusable_sixth;\n',
           '\tbool slot1_reusable_sixth;\n\tbool slot0_reused_sixth;\n\tbool slot0_reusable_seventh;\n\tbool slot1_reused_sixth;\n\tbool slot1_reusable_seventh;\n\tbool slot0_reused_seventh;\n\tbool slot0_reusable_eighth;\n','slot flags')
    s=once(s,'\tstruct camss_buffer *video_requeued_eighth;\n',
           '\tstruct camss_buffer *video_requeued_eighth;\n\tstruct camss_buffer *video_requeued_ninth;\n\tstruct camss_buffer *video_requeued_tenth;\n\tstruct camss_buffer *video_requeued_eleventh;\n','requeue fields')
    s=once(s,'\tbool live_requeue_eighth_acquired;\n',
           '\tbool live_requeue_eighth_acquired;\n\tbool live_requeue_ninth_acquired;\n\tbool live_requeue_tenth_acquired;\n\tbool live_requeue_eleventh_acquired;\n','requeue acquired')
    s=once(s,'frame_number < 7 || frame_number > 12 || request_id != frame_number ||',
           'frame_number < 7 || frame_number > 15 || request_id != frame_number ||','steady bound')
    s=once(s,'\tstruct camss_x1e_pix_capsule_materialized *materialized_r12 = NULL;\n',
           '\tstruct camss_x1e_pix_capsule_materialized *materialized_r12 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r13 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r14 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r15 = NULL;\n','materialized locals')
    s=once(s,'\tstruct camss_buffer *tenth = NULL, *eleventh = NULL, *twelfth = NULL;\n',
           '\tstruct camss_buffer *tenth = NULL, *eleventh = NULL, *twelfth = NULL;\n\tstruct camss_buffer *thirteenth = NULL, *fourteenth = NULL, *fifteenth = NULL;\n','buffer locals')
    s=once(s,'if (!result || frame_limit < 1 || frame_limit > 12)',
           'if (!result || frame_limit < 1 || frame_limit > 15)','frame limit')
    s=once(s,'\tif (frame_limit >= 12)\n\t\tmaterialized_r12 = kzalloc_obj(*materialized_r12, GFP_KERNEL);\n',
           '\tif (frame_limit >= 12)\n\t\tmaterialized_r12 = kzalloc_obj(*materialized_r12, GFP_KERNEL);\n\tif (frame_limit >= 13)\n\t\tmaterialized_r13 = kzalloc_obj(*materialized_r13, GFP_KERNEL);\n\tif (frame_limit >= 14)\n\t\tmaterialized_r14 = kzalloc_obj(*materialized_r14, GFP_KERNEL);\n\tif (frame_limit >= 15)\n\t\tmaterialized_r15 = kzalloc_obj(*materialized_r15, GFP_KERNEL);\n','alloc')
    s=once(s,'\t    (frame_limit >= 12 && !materialized_r12)) {\n',
           '\t    (frame_limit >= 12 && !materialized_r12) ||\n\t    (frame_limit >= 13 && !materialized_r13) ||\n\t    (frame_limit >= 14 && !materialized_r14) ||\n\t    (frame_limit >= 15 && !materialized_r15)) {\n','alloc check')

    frame12='''\tif (frame_limit >= 12) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 12, 12, 1, req->video[3], materialized_r12,
\t\t\t&epoch0_seq, video_seq, &twelfth, &result->video_done_twelfth);
\t\tif (twelfth) {
\t\t\tresult->video_requeued_eighth = twelfth;
\t\t\tresult->live_requeue_eighth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_ninth_seen = true;
\t\tresult->video_twelfth_seen = true;
\t\tresult->slot1_reused_fifth = true;
\t\tresult->slot1_reusable_sixth = true;
\t}

'''
    ext=frame12+'''\tif (frame_limit >= 13) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 13, 13, 0, req->video[0], materialized_r13,
\t\t\t&epoch0_seq, video_seq, &thirteenth, &result->video_done_thirteenth);
\t\tif (thirteenth) {
\t\t\tresult->video_requeued_ninth = thirteenth;
\t\t\tresult->live_requeue_ninth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_tenth_seen = true;
\t\tresult->video_thirteenth_seen = true;
\t\tresult->slot0_reused_sixth = true;
\t\tresult->slot0_reusable_seventh = true;
\t}

\tif (frame_limit >= 14) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 14, 14, 1, req->video[1], materialized_r14,
\t\t\t&epoch0_seq, video_seq, &fourteenth, &result->video_done_fourteenth);
\t\tif (fourteenth) {
\t\t\tresult->video_requeued_tenth = fourteenth;
\t\t\tresult->live_requeue_tenth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_eleventh_seen = true;
\t\tresult->video_fourteenth_seen = true;
\t\tresult->slot1_reused_sixth = true;
\t\tresult->slot1_reusable_seventh = true;
\t}

\tif (frame_limit >= 15) {
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
    s=once(s,frame12,ext,'frames13-15')

    s=once(s,'\t\tresult->video_done_twelfth = NULL;\n',
           '\t\tresult->video_done_twelfth = NULL;\n\t\tresult->video_done_thirteenth = NULL;\n\t\tresult->video_done_fourteenth = NULL;\n\t\tresult->video_done_fifteenth = NULL;\n','unsafe nulls')
    s=once(s,'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r12);\n',
           'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r15);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r14);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r13);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r12);\n','release')
    s=once(s,'out_free_inputs:\n\tkfree(materialized_r12);\n',
           'out_free_inputs:\n\tkfree(materialized_r15);\n\tkfree(materialized_r14);\n\tkfree(materialized_r13);\n\tkfree(materialized_r12);\n','free')

    s=once(s,'camss_x1e_pix_runner_frames(camss, &req, &result, 12)',
           'camss_x1e_pix_runner_frames(camss, &req, &result, 15)','worker count')
    s=once(s,'\t    result.video_done_eleventh != video2 || result.video_done_twelfth != video3 ||\n',
           '\t    result.video_done_eleventh != video2 || result.video_done_twelfth != video3 ||\n\t    result.video_done_thirteenth != video0 || result.video_done_fourteenth != video1 ||\n\t    result.video_done_fifteenth != video2 ||\n','worker done')
    s=once(s,'\t    result.video_requeued_seventh != video2 || result.video_requeued_eighth != video3 ||\n\t    result.live_completed != 12 ||\n',
           '\t    result.video_requeued_seventh != video2 || result.video_requeued_eighth != video3 ||\n\t    result.video_requeued_ninth != video0 || result.video_requeued_tenth != video1 ||\n\t    result.video_requeued_eleventh != video2 || result.live_completed != 15 ||\n','worker requeue')
    s=once(s,'\t    !result.live_requeue_seventh_acquired || !result.live_requeue_eighth_acquired || !result.epoch0_seen ||\n',
           '\t    !result.live_requeue_seventh_acquired || !result.live_requeue_eighth_acquired ||\n\t    !result.live_requeue_ninth_acquired || !result.live_requeue_tenth_acquired ||\n\t    !result.live_requeue_eleventh_acquired || !result.epoch0_seen ||\n','worker acquired')
    s=once(s,'\t    !result.epoch0_steady_eighth_seen || !result.epoch0_steady_ninth_seen || !result.video_seen ||\n',
           '\t    !result.epoch0_steady_eighth_seen || !result.epoch0_steady_ninth_seen ||\n\t    !result.epoch0_steady_tenth_seen || !result.epoch0_steady_eleventh_seen ||\n\t    !result.epoch0_steady_twelfth_seen || !result.video_seen ||\n','worker epoch')
    s=once(s,'\t    !result.video_eleventh_seen || !result.video_twelfth_seen || !result.slot0_reusable ||\n',
           '\t    !result.video_eleventh_seen || !result.video_twelfth_seen ||\n\t    !result.video_thirteenth_seen || !result.video_fourteenth_seen ||\n\t    !result.video_fifteenth_seen || !result.slot0_reusable ||\n','worker video')
    s=once(s,'\t    !result.slot1_reused_fifth || !result.slot1_reusable_sixth) {\n',
           '\t    !result.slot1_reused_fifth || !result.slot1_reusable_sixth ||\n\t    !result.slot0_reused_sixth || !result.slot0_reusable_seventh ||\n\t    !result.slot1_reused_sixth || !result.slot1_reusable_seventh ||\n\t    !result.slot0_reused_seventh || !result.slot0_reusable_eighth) {\n','worker slots')
    s=once(s,'bounded twelve-frame live requeue','bounded fifteen-frame live requeue','log')
    s=once(s,'\t\tif (result.live_requeue_eighth_acquired && result.live_completed < 12)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_eighth);\n',
           '\t\tif (result.live_requeue_eighth_acquired && result.live_completed < 12)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_eighth);\n\t\tif (result.live_requeue_ninth_acquired && result.live_completed < 13)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_ninth);\n\t\tif (result.live_requeue_tenth_acquired && result.live_completed < 14)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_tenth);\n\t\tif (result.live_requeue_eleventh_acquired && result.live_completed < 15)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_eleventh);\n','error buffers')
    return s
def main():
    ap=argparse.ArgumentParser();ap.add_argument('src',type=Path);ap.add_argument('dst',type=Path);a=ap.parse_args()
    b=a.src.read_bytes();need(hashlib.sha256(b).hexdigest()==BASE_SHA,'FE12 source SHA drift')
    out=transform(b.decode());a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA);print('PATCHED_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__': main()
