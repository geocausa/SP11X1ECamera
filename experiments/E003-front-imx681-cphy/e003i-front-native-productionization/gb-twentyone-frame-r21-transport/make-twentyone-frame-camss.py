#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib

BASE_SHA='a096493ae74fc3a22945f71f670f8777f0ea375bd3ad667c7451c96116d2ef6c'

def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: count={s.count(a)}')
    return s.replace(a,b,1)

def transform(s):
    s=once(s,'\tstruct camss_buffer *video_done_eighteenth;\n',
           '\tstruct camss_buffer *video_done_eighteenth;\n\tstruct camss_buffer *video_done_nineteenth;\n\tstruct camss_buffer *video_done_twentieth;\n\tstruct camss_buffer *video_done_twentyfirst;\n','done fields')
    s=once(s,'\tbool epoch0_steady_fifteenth_seen;\n',
           '\tbool epoch0_steady_fifteenth_seen;\n\tbool epoch0_steady_sixteenth_seen;\n\tbool epoch0_steady_seventeenth_seen;\n\tbool epoch0_steady_eighteenth_seen;\n','epoch flags')
    s=once(s,'\tbool video_eighteenth_seen;\n',
           '\tbool video_eighteenth_seen;\n\tbool video_nineteenth_seen;\n\tbool video_twentieth_seen;\n\tbool video_twentyfirst_seen;\n','video flags')
    s=once(s,'\tbool slot1_reusable_ninth;\n',
           '\tbool slot1_reusable_ninth;\n\tbool slot0_reused_ninth;\n\tbool slot0_reusable_tenth;\n\tbool slot1_reused_ninth;\n\tbool slot1_reusable_tenth;\n\tbool slot0_reused_tenth;\n\tbool slot0_reusable_eleventh;\n','slot flags')
    s=once(s,'\tstruct camss_buffer *video_requeued_fourteenth;\n',
           '\tstruct camss_buffer *video_requeued_fourteenth;\n\tstruct camss_buffer *video_requeued_fifteenth;\n\tstruct camss_buffer *video_requeued_sixteenth;\n\tstruct camss_buffer *video_requeued_seventeenth;\n','requeue fields')
    s=once(s,'\tbool live_requeue_fourteenth_acquired;\n',
           '\tbool live_requeue_fourteenth_acquired;\n\tbool live_requeue_fifteenth_acquired;\n\tbool live_requeue_sixteenth_acquired;\n\tbool live_requeue_seventeenth_acquired;\n','requeue acquired')
    s=once(s,'frame_number < 7 || frame_number > 18 || request_id != frame_number ||',
           'frame_number < 7 || frame_number > 21 || request_id != frame_number ||','steady bound')
    s=once(s,'\tstruct camss_x1e_pix_capsule_materialized *materialized_r18 = NULL;\n',
           '\tstruct camss_x1e_pix_capsule_materialized *materialized_r18 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r19 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r20 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r21 = NULL;\n','materialized locals')
    s=once(s,'\tstruct camss_buffer *sixteenth = NULL, *seventeenth = NULL, *eighteenth = NULL;\n',
           '\tstruct camss_buffer *sixteenth = NULL, *seventeenth = NULL, *eighteenth = NULL;\n\tstruct camss_buffer *nineteenth = NULL, *twentieth = NULL, *twentyfirst = NULL;\n','buffer locals')
    s=once(s,'if (!result || frame_limit < 1 || frame_limit > 18)',
           'if (!result || frame_limit < 1 || frame_limit > 21)','frame limit')
    s=once(s,'\tif (frame_limit >= 18)\n\t\tmaterialized_r18 = kzalloc_obj(*materialized_r18, GFP_KERNEL);\n',
           '\tif (frame_limit >= 18)\n\t\tmaterialized_r18 = kzalloc_obj(*materialized_r18, GFP_KERNEL);\n\tif (frame_limit >= 19)\n\t\tmaterialized_r19 = kzalloc_obj(*materialized_r19, GFP_KERNEL);\n\tif (frame_limit >= 20)\n\t\tmaterialized_r20 = kzalloc_obj(*materialized_r20, GFP_KERNEL);\n\tif (frame_limit >= 21)\n\t\tmaterialized_r21 = kzalloc_obj(*materialized_r21, GFP_KERNEL);\n','alloc')
    s=once(s,'\t    (frame_limit >= 18 && !materialized_r18)) {\n',
           '\t    (frame_limit >= 18 && !materialized_r18) ||\n\t    (frame_limit >= 19 && !materialized_r19) ||\n\t    (frame_limit >= 20 && !materialized_r20) ||\n\t    (frame_limit >= 21 && !materialized_r21)) {\n','alloc check')

    frame18='''\tif (frame_limit >= 18) {
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
    ext=frame18+'''\tif (frame_limit >= 19) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 19, 19, 0, req->video[2], materialized_r19,
\t\t\t&epoch0_seq, video_seq, &nineteenth, &result->video_done_nineteenth);
\t\tif (nineteenth) {
\t\t\tresult->video_requeued_fifteenth = nineteenth;
\t\t\tresult->live_requeue_fifteenth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_sixteenth_seen = true;
\t\tresult->video_nineteenth_seen = true;
\t\tresult->slot0_reused_ninth = true;
\t\tresult->slot0_reusable_tenth = true;
\t}

\tif (frame_limit >= 20) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 20, 20, 1, req->video[3], materialized_r20,
\t\t\t&epoch0_seq, video_seq, &twentieth, &result->video_done_twentieth);
\t\tif (twentieth) {
\t\t\tresult->video_requeued_sixteenth = twentieth;
\t\t\tresult->live_requeue_sixteenth_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_seventeenth_seen = true;
\t\tresult->video_twentieth_seen = true;
\t\tresult->slot1_reused_ninth = true;
\t\tresult->slot1_reusable_tenth = true;
\t}

\tif (frame_limit >= 21) {
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
    s=once(s,frame18,ext,'frames19-21')
    s=once(s,'\t\tresult->video_done_eighteenth = NULL;\n',
           '\t\tresult->video_done_eighteenth = NULL;\n\t\tresult->video_done_nineteenth = NULL;\n\t\tresult->video_done_twentieth = NULL;\n\t\tresult->video_done_twentyfirst = NULL;\n','unsafe nulls')
    s=once(s,'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r18);\n',
           'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r21);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r20);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r19);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r18);\n','release')
    s=once(s,'out_free_inputs:\n\tkfree(materialized_r18);\n',
           'out_free_inputs:\n\tkfree(materialized_r21);\n\tkfree(materialized_r20);\n\tkfree(materialized_r19);\n\tkfree(materialized_r18);\n','free')
    s=once(s,'camss_x1e_pix_runner_frames(camss, &req, &result, 18)',
           'camss_x1e_pix_runner_frames(camss, &req, &result, 21)','worker count')
    s=once(s,'\t    result.video_done_seventeenth != video0 || result.video_done_eighteenth != video1 ||\n',
           '\t    result.video_done_seventeenth != video0 || result.video_done_eighteenth != video1 ||\n\t    result.video_done_nineteenth != video2 || result.video_done_twentieth != video3 ||\n\t    result.video_done_twentyfirst != video0 ||\n','worker done')
    s=once(s,'\t    result.video_requeued_thirteenth != video0 || result.video_requeued_fourteenth != video1 ||\n\t    result.live_completed != 18 ||\n',
           '\t    result.video_requeued_thirteenth != video0 || result.video_requeued_fourteenth != video1 ||\n\t    result.video_requeued_fifteenth != video2 || result.video_requeued_sixteenth != video3 ||\n\t    result.video_requeued_seventeenth != video0 || result.live_completed != 21 ||\n','worker requeue')
    s=once(s,'\t    !result.live_requeue_thirteenth_acquired || !result.live_requeue_fourteenth_acquired ||\n\t    !result.epoch0_seen ||\n',
           '\t    !result.live_requeue_thirteenth_acquired || !result.live_requeue_fourteenth_acquired ||\n\t    !result.live_requeue_fifteenth_acquired || !result.live_requeue_sixteenth_acquired ||\n\t    !result.live_requeue_seventeenth_acquired || !result.epoch0_seen ||\n','worker acquired')
    s=once(s,'\t    !result.epoch0_steady_fourteenth_seen || !result.epoch0_steady_fifteenth_seen ||\n\t    !result.video_seen ||\n',
           '\t    !result.epoch0_steady_fourteenth_seen || !result.epoch0_steady_fifteenth_seen ||\n\t    !result.epoch0_steady_sixteenth_seen || !result.epoch0_steady_seventeenth_seen ||\n\t    !result.epoch0_steady_eighteenth_seen || !result.video_seen ||\n','worker epoch')
    s=once(s,'\t    !result.video_seventeenth_seen || !result.video_eighteenth_seen || !result.slot0_reusable ||\n',
           '\t    !result.video_seventeenth_seen || !result.video_eighteenth_seen ||\n\t    !result.video_nineteenth_seen || !result.video_twentieth_seen ||\n\t    !result.video_twentyfirst_seen || !result.slot0_reusable ||\n','worker video')
    s=once(s,'\t    !result.slot1_reused_eighth || !result.slot1_reusable_ninth) {\n',
           '\t    !result.slot1_reused_eighth || !result.slot1_reusable_ninth ||\n\t    !result.slot0_reused_ninth || !result.slot0_reusable_tenth ||\n\t    !result.slot1_reused_ninth || !result.slot1_reusable_tenth ||\n\t    !result.slot0_reused_tenth || !result.slot0_reusable_eleventh) {\n','worker slots')
    s=once(s,'bounded eighteen-frame live requeue','bounded twenty-one-frame live requeue','log')
    s=once(s,'\t\tif (result.live_requeue_fourteenth_acquired && result.live_completed < 18)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_fourteenth);\n',
           '\t\tif (result.live_requeue_fourteenth_acquired && result.live_completed < 18)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_fourteenth);\n\t\tif (result.live_requeue_fifteenth_acquired && result.live_completed < 19)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_fifteenth);\n\t\tif (result.live_requeue_sixteenth_acquired && result.live_completed < 20)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_sixteenth);\n\t\tif (result.live_requeue_seventeenth_acquired && result.live_completed < 21)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_seventeenth);\n','error buffers')
    return s

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('src',type=Path); ap.add_argument('dst',type=Path); a=ap.parse_args()
    b=a.src.read_bytes(); need(hashlib.sha256(b).hexdigest()==BASE_SHA,'FT18 source SHA drift')
    out=transform(b.decode()); a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA); print('PATCHED_SHA='+hashlib.sha256(out.encode()).hexdigest())

if __name__=='__main__': main()
