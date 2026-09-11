#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib
BASE_SHA='335e15f48cac9835d9ddfa0f1dc96f559346f167f2e8cce1c384635b872d13aa'
def need(x,m):
 if not x: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
 need(s.count(a)==1,f'{label}: count={s.count(a)}');return s.replace(a,b,1)
def transform(s):
 s=once(s,'\tstruct camss_buffer *video_done_eleventh;\n','\tstruct camss_buffer *video_done_eleventh;\n\tstruct camss_buffer *video_done_twelfth;\n','done field')
 s=once(s,'\tbool epoch0_steady_eighth_seen;\n','\tbool epoch0_steady_eighth_seen;\n\tbool epoch0_steady_ninth_seen;\n','epoch flag')
 s=once(s,'\tbool video_eleventh_seen;\n','\tbool video_eleventh_seen;\n\tbool video_twelfth_seen;\n','video flag')
 s=once(s,'\tbool slot0_reusable_sixth;\n','\tbool slot0_reusable_sixth;\n\tbool slot1_reused_fifth;\n\tbool slot1_reusable_sixth;\n','slot flags')
 s=once(s,'\tstruct camss_buffer *video_requeued_seventh;\n','\tstruct camss_buffer *video_requeued_seventh;\n\tstruct camss_buffer *video_requeued_eighth;\n','requeue field')
 s=once(s,'\tbool live_requeue_seventh_acquired;\n','\tbool live_requeue_seventh_acquired;\n\tbool live_requeue_eighth_acquired;\n','requeue acquired')
 s=once(s,'frame_number < 7 || frame_number > 11 || request_id != frame_number ||','frame_number < 7 || frame_number > 12 || request_id != frame_number ||','steady bound')
 s=once(s,'\tstruct camss_x1e_pix_capsule_materialized *materialized_r11 = NULL;\n','\tstruct camss_x1e_pix_capsule_materialized *materialized_r11 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r12 = NULL;\n','materialized')
 s=once(s,'\tstruct camss_buffer *tenth = NULL, *eleventh = NULL;\n','\tstruct camss_buffer *tenth = NULL, *eleventh = NULL, *twelfth = NULL;\n','buffer local')
 s=once(s,'if (!result || frame_limit < 1 || frame_limit > 11)','if (!result || frame_limit < 1 || frame_limit > 12)','frame limit')
 s=once(s,'\tif (frame_limit >= 11)\n\t\tmaterialized_r11 = kzalloc_obj(*materialized_r11, GFP_KERNEL);\n','\tif (frame_limit >= 11)\n\t\tmaterialized_r11 = kzalloc_obj(*materialized_r11, GFP_KERNEL);\n\tif (frame_limit >= 12)\n\t\tmaterialized_r12 = kzalloc_obj(*materialized_r12, GFP_KERNEL);\n','alloc')
 s=once(s,'\t    (frame_limit >= 11 && !materialized_r11)) {\n','\t    (frame_limit >= 11 && !materialized_r11) ||\n\t    (frame_limit >= 12 && !materialized_r12)) {\n','alloc check')
 anchor='''\tif (frame_limit >= 11) {
\t\tret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
\t\t\tcsid, vfe, 11, 11, 0, req->video[2], materialized_r11,
\t\t\t&epoch0_seq, video_seq, &eleventh, &result->video_done_eleventh);
\t\tif (eleventh) {
\t\t\tresult->video_requeued_seventh = eleventh;
\t\t\tresult->live_requeue_seventh_acquired = true;
\t\t}
\t\tif (ret)
\t\t\tgoto out_unwind;
\t\tresult->epoch0_steady_eighth_seen = true;
\t\tresult->video_eleventh_seen = true;
\t\tresult->slot0_reused_fifth = true;
\t\tresult->slot0_reusable_sixth = true;
\t}

'''
 ext=anchor+'''\tif (frame_limit >= 12) {
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
 s=once(s,anchor,ext,'frame12 block')
 s=once(s,'\t\tresult->video_done_eleventh = NULL;\n','\t\tresult->video_done_eleventh = NULL;\n\t\tresult->video_done_twelfth = NULL;\n','unsafe null')
 s=once(s,'out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r11);\n','out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r12);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r11);\n','release')
 s=once(s,'out_free_inputs:\n\tkfree(materialized_r11);\n','out_free_inputs:\n\tkfree(materialized_r12);\n\tkfree(materialized_r11);\n','free')
 s=once(s,'camss_x1e_pix_runner_frames(camss, &req, &result, 11)','camss_x1e_pix_runner_frames(camss, &req, &result, 12)','worker count')
 s=once(s,'\t    result.video_done_eleventh != video2 ||\n','\t    result.video_done_eleventh != video2 || result.video_done_twelfth != video3 ||\n','worker done')
 s=once(s,'\t    result.video_requeued_seventh != video2 || result.live_completed != 11 ||\n','\t    result.video_requeued_seventh != video2 || result.video_requeued_eighth != video3 ||\n\t    result.live_completed != 12 ||\n','worker requeue')
 s=once(s,'\t    !result.live_requeue_seventh_acquired || !result.epoch0_seen ||\n','\t    !result.live_requeue_seventh_acquired || !result.live_requeue_eighth_acquired || !result.epoch0_seen ||\n','worker acquire')
 s=once(s,'\t    !result.epoch0_steady_eighth_seen || !result.video_seen ||\n','\t    !result.epoch0_steady_eighth_seen || !result.epoch0_steady_ninth_seen || !result.video_seen ||\n','worker epoch')
 s=once(s,'\t    !result.video_eleventh_seen || !result.slot0_reusable ||\n','\t    !result.video_eleventh_seen || !result.video_twelfth_seen || !result.slot0_reusable ||\n','worker video')
 s=once(s,'\t    !result.slot0_reused_fifth || !result.slot0_reusable_sixth) {\n','\t    !result.slot0_reused_fifth || !result.slot0_reusable_sixth ||\n\t    !result.slot1_reused_fifth || !result.slot1_reusable_sixth) {\n','worker slots')
 s=once(s,'bounded eleven-frame live requeue','bounded twelve-frame live requeue','log')
 s=once(s,'\t\tif (result.live_requeue_seventh_acquired && result.live_completed < 11)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_seventh);\n','\t\tif (result.live_requeue_seventh_acquired && result.live_completed < 11)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_seventh);\n\t\tif (result.live_requeue_eighth_acquired && result.live_completed < 12)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_eighth);\n','error buffer')
 return s
def main():
 ap=argparse.ArgumentParser();ap.add_argument('src',type=Path);ap.add_argument('dst',type=Path);a=ap.parse_args()
 b=a.src.read_bytes();need(hashlib.sha256(b).hexdigest()==BASE_SHA,'EY11 source SHA drift');out=transform(b.decode());a.dst.write_text(out)
 print('BASE_SHA='+BASE_SHA);print('PATCHED_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__':main()
