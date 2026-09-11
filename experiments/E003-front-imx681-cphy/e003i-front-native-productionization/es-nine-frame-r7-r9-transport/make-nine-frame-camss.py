#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib
BASE_SHA='b9de92306b4d386274968dcab3f1a96ec13359f1eb22c27fda43bb15b0af7abb'

def need(c,m):
    if not c: raise SystemExit('FAIL: '+m)
def once(s,a,b,label):
    need(s.count(a)==1,f'{label}: expected one match, got {s.count(a)}')
    return s.replace(a,b,1)

def transform(src:str)->str:
    s=src
    s=once(s,
'''\tstruct camss_buffer *video_done_fifth;\n\tstruct camss_buffer *video_done_sixth;\n''',
'''\tstruct camss_buffer *video_done_fifth;\n\tstruct camss_buffer *video_done_sixth;\n\tstruct camss_buffer *video_done_seventh;\n\tstruct camss_buffer *video_done_eighth;\n\tstruct camss_buffer *video_done_ninth;\n''','done pointers')
    s=once(s,
'''\tbool epoch0_steady_next_seen;\n\tbool epoch0_steady_third_seen;\n''',
'''\tbool epoch0_steady_next_seen;\n\tbool epoch0_steady_third_seen;\n\tbool epoch0_steady_fourth_seen;\n\tbool epoch0_steady_fifth_seen;\n\tbool epoch0_steady_sixth_seen;\n''','epoch flags')
    s=once(s,
'''\tbool video_fifth_seen;\n\tbool video_sixth_seen;\n''',
'''\tbool video_fifth_seen;\n\tbool video_sixth_seen;\n\tbool video_seventh_seen;\n\tbool video_eighth_seen;\n\tbool video_ninth_seen;\n''','video flags')
    s=once(s,
'''\tbool slot0_reusable_third;\n\tbool slot1_reusable_third;\n\tstruct camss_buffer *video_requeued;\n\tstruct camss_buffer *video_requeued_next;\n\tunsigned int live_completed;\n\tbool live_requeue_acquired;\n\tbool live_requeue_next_acquired;\n''',
'''\tbool slot0_reusable_third;\n\tbool slot1_reusable_third;\n\tbool slot0_reused_third;\n\tbool slot1_reused_third;\n\tbool slot0_reused_fourth;\n\tbool slot0_reusable_fourth;\n\tbool slot1_reusable_fourth;\n\tbool slot0_reusable_fifth;\n\tstruct camss_buffer *video_requeued;\n\tstruct camss_buffer *video_requeued_next;\n\tstruct camss_buffer *video_requeued_third;\n\tstruct camss_buffer *video_requeued_fourth;\n\tstruct camss_buffer *video_requeued_fifth;\n\tunsigned int live_completed;\n\tbool live_requeue_acquired;\n\tbool live_requeue_next_acquired;\n\tbool live_requeue_third_acquired;\n\tbool live_requeue_fourth_acquired;\n\tbool live_requeue_fifth_acquired;\n''','reuse/result flags')

    decl='''static int camss_x1e_pix_iq_provider_next_steady(\n\tstruct camss *camss, struct camss_video *video, u64 expected_request_id,\n\tstruct camss_x1e_epoch0_materialized *steady);\n\n'''
    helper=decl+r'''/*
 * ES bounded post-R6 steady-frame extension.  Frames 7..9 repeat only the
 * already-proven steady Epoch0/rebind/retire sequence.  No startup, sensor,
 * CSID format, VFE format, or direct-MMIO ownership rule is added here.
 */
static int camss_x1e_pix_runner_live_steady_frame(
	struct camss *camss, const struct camss_x1e_pix_runner_request *req,
	struct camss_x1e_pix_runner_result *result,
	struct vfe680_x1e_pix_runtime *pix, struct csid_device *csid,
	struct vfe_device *vfe, unsigned int frame_number, u64 request_id,
	unsigned int slot, struct camss_buffer *expected,
	struct camss_x1e_pix_capsule_materialized *materialized,
	u32 *epoch0_seq, u32 video_seq, struct camss_buffer **buffer_out,
	struct camss_buffer **done_out)
{
	struct camss_buffer *buffer;
	u32 seq, delta;
	int ret;

	if (!camss || !req || !result || !pix || !csid || !vfe || !expected ||
	    !materialized || !epoch0_seq || !buffer_out || !done_out ||
	    frame_number < 7 || frame_number > 9 || request_id != frame_number ||
	    slot >= 2 || !req->live_requeue || !req->live_video)
		return -EINVAL;
	*buffer_out = NULL;
	*done_out = NULL;

	buffer = camss_x1e_pix_v4l2_wait_pending(req->live_video,
						 CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
	if (IS_ERR(buffer))
		return PTR_ERR(buffer);
	*buffer_out = buffer;
	ret = camss_x1e_pix_v4l2_buffer(req->live_video, buffer);
	if (ret)
		return ret;
	if (buffer != expected)
		return -EPROTO;

	ret = camss_x1e_pix_iq_provider_next_steady(camss, req->live_video,
						     request_id, &materialized->steady);
	if (ret)
		return ret;
	dev_info(camss->dev, "E003I_ES_IQ_CONSUMED R=%llu FRAME=%u SLOT=%u\n",
		 (unsigned long long)request_id, frame_number, slot);
	ret = csid680_x1e_front_poll_next_epoch0(csid, *epoch0_seq,
						      CAMSS_X1E_PIX_RUNNER_EPOCH0_TIMEOUT_US);
	if (ret)
		return ret;
	*epoch0_seq = csid680_x1e_front_epoch0_seq(csid);
	ret = vfe680_x1e_pix_runtime_rebind(pix, slot, buffer);
	if (ret)
		return ret;
	ret = vfe680_x1e_pix_runtime_bus_update(vfe, pix, slot);
	if (ret)
		return ret;
	ret = camss_x1e_pix_rtcdm_submit_epoch0_batch(camss, &materialized->steady);
	if (ret)
		return ret;

	seq = csid680_x1e_front_video_seq(csid);
	delta = seq - video_seq;
	if (delta > frame_number)
		return -EPROTO;
	if (delta < frame_number) {
		ret = csid680_x1e_front_poll_video(csid, seq,
						      CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
		if (ret)
			return ret;
		seq = csid680_x1e_front_video_seq(csid);
		delta = seq - video_seq;
	}
	if (delta != frame_number)
		return -EPROTO;
	ret = vfe680_x1e_pix_runtime_retire_video(pix, slot, done_out);
	if (ret)
		return ret;
	ret = csid680_x1e_front_poll_all_done(csid, video_seq + frame_number,
						       CAMSS_X1E_PIX_RUNNER_VIDEO_TIMEOUT_US);
	if (ret)
		return ret;
	ret = camss_x1e_pix_publish_tlbg(req->live_video, pix, slot,
						  video_seq + frame_number);
	if (ret)
		return ret;
	ret = camss_x1e_pix_publish_3a(req->live_video, pix, slot,
						video_seq + frame_number);
	if (ret)
		return ret;
	ret = vfe680_x1e_pix_runtime_retire_aux(pix, slot);
	if (ret)
		return ret;
	camss_x1e_pix_v4l2_complete_live(result, buffer, frame_number - 1);
	return 0;
}

'''
    s=once(s,decl,helper,'insert frame helper')
    s=once(s,
'''\tstruct camss_x1e_pix_capsule_materialized *materialized_next_next = NULL;\n''',
'''\tstruct camss_x1e_pix_capsule_materialized *materialized_next_next = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r7 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r8 = NULL;\n\tstruct camss_x1e_pix_capsule_materialized *materialized_r9 = NULL;\n''','materialized locals')
    s=once(s,
'''\tstruct camss_buffer *fifth = req ? req->video[4] : NULL;\n\tstruct camss_buffer *sixth = req ? req->video[5] : NULL;\n''',
'''\tstruct camss_buffer *fifth = req ? req->video[4] : NULL;\n\tstruct camss_buffer *sixth = req ? req->video[5] : NULL;\n\tstruct camss_buffer *seventh = NULL, *eighth = NULL, *ninth = NULL;\n''','buffer locals')
    s=once(s,
'''\tif (!result || (frame_limit != 1 && frame_limit != 2 &&\n\t\t\tframe_limit != 3 && frame_limit != 4 && frame_limit != 5 &&\n\t\t\tframe_limit != 6))\n\t\treturn -EINVAL;\n''',
'''\tif (!result || frame_limit < 1 || frame_limit > 9)\n\t\treturn -EINVAL;\n''','frame limit')
    s=once(s,
'''\tif (frame_limit == 6 && !deferred_live_iq &&\n\t    (!req->capsule_next_next || !req->capsule_next_next_size))\n\t\treturn -EINVAL;\n''',
'''\tif (frame_limit >= 6 && !deferred_live_iq &&\n\t    (!req->capsule_next_next || !req->capsule_next_next_size))\n\t\treturn -EINVAL;\n\tif (frame_limit > 6 && !deferred_live_iq)\n\t\treturn -EINVAL;\n''','non-live cap')
    s=once(s,
'''\t\tif (!req->live_video || req->video[4] || (frame_limit == 6 && req->video[5]))\n''',
'''\t\tif (!req->live_video || req->video[4] || (frame_limit >= 6 && req->video[5]))\n''','live video validation')
    s=once(s,
'''\tif (frame_limit == 6 && !req->live_requeue &&\n''',
'''\tif (frame_limit >= 6 && !req->live_requeue &&\n''','sixth validation')
    s=once(s,
'''\tif (frame_limit == 6) {\n\t\tinputs_next_next = kzalloc_obj(*inputs_next_next, GFP_KERNEL);\n\t\tmaterialized_next_next = kzalloc_obj(*materialized_next_next, GFP_KERNEL);\n\t}\n\tif (!inputs || !materialized ||\n\t    (frame_limit >= 5 && (!inputs_next || !materialized_next)) ||\n\t    (frame_limit == 6 && (!inputs_next_next || !materialized_next_next))) {\n''',
'''\tif (frame_limit >= 6) {\n\t\tinputs_next_next = kzalloc_obj(*inputs_next_next, GFP_KERNEL);\n\t\tmaterialized_next_next = kzalloc_obj(*materialized_next_next, GFP_KERNEL);\n\t}\n\tif (frame_limit >= 7)\n\t\tmaterialized_r7 = kzalloc_obj(*materialized_r7, GFP_KERNEL);\n\tif (frame_limit >= 8)\n\t\tmaterialized_r8 = kzalloc_obj(*materialized_r8, GFP_KERNEL);\n\tif (frame_limit >= 9)\n\t\tmaterialized_r9 = kzalloc_obj(*materialized_r9, GFP_KERNEL);\n\tif (!inputs || !materialized ||\n\t    (frame_limit >= 5 && (!inputs_next || !materialized_next)) ||\n\t    (frame_limit >= 6 && (!inputs_next_next || !materialized_next_next)) ||\n\t    (frame_limit >= 7 && !materialized_r7) ||\n\t    (frame_limit >= 8 && !materialized_r8) ||\n\t    (frame_limit >= 9 && !materialized_r9)) {\n''','alloc extension')
    s=once(s,
'''\tif (frame_limit == 6 && !deferred_live_iq) {\n''',
'''\tif (frame_limit >= 6 && !deferred_live_iq) {\n''','r6 static parse')
    s=once(s,
'''\tif (frame_limit == 6 && req->live_requeue) {\n''',
'''\tif (frame_limit >= 6 && req->live_requeue) {\n''','sixth wait')
    # two distinct remaining frame_limit == 6 blocks: request6 gate, then video6.
    s=once(s,
'''\tif (frame_limit == 6) {\n\t\tif (deferred_live_iq) {\n\t\t\tret = camss_x1e_pix_iq_provider_next_steady(\n\t\t\t\tcamss, req->live_video, 6, &materialized_next_next->steady);\n''',
'''\tif (frame_limit >= 6) {\n\t\tif (deferred_live_iq) {\n\t\t\tret = camss_x1e_pix_iq_provider_next_steady(\n\t\t\t\tcamss, req->live_video, 6, &materialized_next_next->steady);\n''','r6 gate')
    s=once(s,
'''\tif (frame_limit == 6) {\n\t\tu32 sixth_seq = csid680_x1e_front_video_seq(csid);\n''',
'''\tif (frame_limit >= 6) {\n\t\tu32 sixth_seq = csid680_x1e_front_video_seq(csid);\n''','r6 video')

    marker='''\tif (frame_limit >= 6) {\n\t\tu32 sixth_seq = csid680_x1e_front_video_seq(csid);\n'''
    # Insert extension after the complete sixth-frame block, just before out_unwind.
    tail='''\t\tif (req->live_requeue)\n\t\t\tcamss_x1e_pix_v4l2_complete_live(result, sixth, 5);\n\t}\n\nout_unwind:\n'''
    ext=r'''		if (req->live_requeue)
			camss_x1e_pix_v4l2_complete_live(result, sixth, 5);
	}

	if (frame_limit >= 7) {
		ret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
			csid, vfe, 7, 7, 0, req->video[2], materialized_r7,
			&epoch0_seq, video_seq, &seventh, &result->video_done_seventh);
		if (seventh) {
			result->video_requeued_third = seventh;
			result->live_requeue_third_acquired = true;
		}
		if (ret)
			goto out_unwind;
		result->epoch0_steady_fourth_seen = true;
		result->video_seventh_seen = true;
		result->slot0_reused_third = true;
		result->slot0_reusable_fourth = true;
	}
	if (frame_limit >= 8) {
		ret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
			csid, vfe, 8, 8, 1, req->video[3], materialized_r8,
			&epoch0_seq, video_seq, &eighth, &result->video_done_eighth);
		if (eighth) {
			result->video_requeued_fourth = eighth;
			result->live_requeue_fourth_acquired = true;
		}
		if (ret)
			goto out_unwind;
		result->epoch0_steady_fifth_seen = true;
		result->video_eighth_seen = true;
		result->slot1_reused_third = true;
		result->slot1_reusable_fourth = true;
	}
	if (frame_limit >= 9) {
		ret = camss_x1e_pix_runner_live_steady_frame(camss, req, result, pix,
			csid, vfe, 9, 9, 0, req->video[0], materialized_r9,
			&epoch0_seq, video_seq, &ninth, &result->video_done_ninth);
		if (ninth) {
			result->video_requeued_fifth = ninth;
			result->live_requeue_fifth_acquired = true;
		}
		if (ret)
			goto out_unwind;
		result->epoch0_steady_sixth_seen = true;
		result->video_ninth_seen = true;
		result->slot0_reused_fourth = true;
		result->slot0_reusable_fifth = true;
	}

out_unwind:
'''
    s=once(s,tail,ext,'post-r6 extension')
    s=once(s,
'''\t\tresult->video_done_fifth = NULL;\n\t\tresult->video_done_sixth = NULL;\n''',
'''\t\tresult->video_done_fifth = NULL;\n\t\tresult->video_done_sixth = NULL;\n\t\tresult->video_done_seventh = NULL;\n\t\tresult->video_done_eighth = NULL;\n\t\tresult->video_done_ninth = NULL;\n''','unsafe nulls')
    s=once(s,
'''out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_next_next);\n''',
'''out_materialized:\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r9);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r8);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_r7);\n\tcamss_x1e_pix_capsule_materialized_release(camss, materialized_next_next);\n''','release extra mats')
    s=once(s,
'''out_free_inputs:\n\tkfree(materialized_next_next);\n''',
'''out_free_inputs:\n\tkfree(materialized_r9);\n\tkfree(materialized_r8);\n\tkfree(materialized_r7);\n\tkfree(materialized_next_next);\n''','free extra mats')

    s=once(s,
'''\tret = camss_x1e_pix_runner_frames(camss, &req, &result, 6);\n''',
'''\tret = camss_x1e_pix_runner_frames(camss, &req, &result, 9);\n''','worker frame count')
    old='''\tif (ret || result.video_done != video0 || result.video_done_next != video1 ||\n\t    result.video_done_third != video2 || result.video_done_fourth != video3 ||\n\t    result.video_done_fifth != video0 || result.video_done_sixth != video1 ||\n\t    result.video_requeued != video0 || result.video_requeued_next != video1 ||\n\t    result.live_completed != 6 || !result.live_requeue_acquired ||\n\t    !result.live_requeue_next_acquired || !result.epoch0_seen ||\n\t    !result.epoch0_next_seen || !result.epoch0_steady_seen ||\n\t    !result.epoch0_steady_next_seen || !result.epoch0_steady_third_seen ||\n\t    !result.video_seen || !result.video_next_seen || !result.video_third_seen ||\n\t    !result.video_fourth_seen || !result.video_fifth_seen || !result.video_sixth_seen ||\n\t    !result.slot0_reusable || !result.slot1_reusable || !result.slot0_reused ||\n\t    !result.slot1_reused || !result.slot0_reused_again || !result.slot1_reused_again ||\n\t    !result.slot0_reusable_again || !result.slot1_reusable_again ||\n\t    !result.slot0_reusable_third || !result.slot1_reusable_third) {\n'''
    new='''\tif (ret || result.video_done != video0 || result.video_done_next != video1 ||\n\t    result.video_done_third != video2 || result.video_done_fourth != video3 ||\n\t    result.video_done_fifth != video0 || result.video_done_sixth != video1 ||\n\t    result.video_done_seventh != video2 || result.video_done_eighth != video3 ||\n\t    result.video_done_ninth != video0 ||\n\t    result.video_requeued != video0 || result.video_requeued_next != video1 ||\n\t    result.video_requeued_third != video2 || result.video_requeued_fourth != video3 ||\n\t    result.video_requeued_fifth != video0 || result.live_completed != 9 ||\n\t    !result.live_requeue_acquired || !result.live_requeue_next_acquired ||\n\t    !result.live_requeue_third_acquired || !result.live_requeue_fourth_acquired ||\n\t    !result.live_requeue_fifth_acquired || !result.epoch0_seen ||\n\t    !result.epoch0_next_seen || !result.epoch0_steady_seen ||\n\t    !result.epoch0_steady_next_seen || !result.epoch0_steady_third_seen ||\n\t    !result.epoch0_steady_fourth_seen || !result.epoch0_steady_fifth_seen ||\n\t    !result.epoch0_steady_sixth_seen || !result.video_seen ||\n\t    !result.video_next_seen || !result.video_third_seen || result.video_fourth_seen == false ||\n\t    !result.video_fifth_seen || !result.video_sixth_seen || !result.video_seventh_seen ||\n\t    !result.video_eighth_seen || !result.video_ninth_seen || !result.slot0_reusable ||\n\t    !result.slot1_reusable || !result.slot0_reused || !result.slot1_reused ||\n\t    !result.slot0_reused_again || !result.slot1_reused_again ||\n\t    !result.slot0_reusable_again || !result.slot1_reusable_again ||\n\t    !result.slot0_reusable_third || !result.slot1_reusable_third ||\n\t    !result.slot0_reused_third || !result.slot1_reused_third ||\n\t    !result.slot0_reused_fourth || !result.slot0_reusable_fourth ||\n\t    !result.slot1_reusable_fourth || !result.slot0_reusable_fifth) {\n'''
    s=once(s,old,new,'worker acceptance')
    s=once(s,
'''\tdev_info(camss->dev,\n\t\t "X1E front PIX completed provider-owned bounded six-frame live requeue\\n");\n''',
'''\tdev_info(camss->dev,\n\t\t "X1E front PIX completed provider-owned bounded nine-frame live requeue\\n");\n''','completion log')
    s=once(s,
'''\t\tif (result.live_requeue_next_acquired && result.live_completed < 6)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_next);\n''',
'''\t\tif (result.live_requeue_next_acquired && result.live_completed < 6)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_next);\n\t\tif (result.live_requeue_third_acquired && result.live_completed < 7)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_third);\n\t\tif (result.live_requeue_fourth_acquired && result.live_completed < 8)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_fourth);\n\t\tif (result.live_requeue_fifth_acquired && result.live_completed < 9)\n\t\t\tcamss_x1e_pix_v4l2_error_buffer(result.video_requeued_fifth);\n''','error buffers')
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('src',type=Path);ap.add_argument('dst',type=Path);a=ap.parse_args()
    b=a.src.read_bytes();need(hashlib.sha256(b).hexdigest()==BASE_SHA,'baseline camss.c SHA drift')
    out=transform(b.decode());a.dst.write_text(out)
    print('BASE_SHA='+BASE_SHA);print('PATCHED_SHA='+hashlib.sha256(out.encode()).hexdigest())
if __name__=='__main__':main()
