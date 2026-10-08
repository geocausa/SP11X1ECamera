/* SPDX-License-Identifier: GPL-2.0-only */
/* Candidate-only public V4L2 capture, bounded to two exact generations.
 * Native startup/profile qualification remains single use. This is the
 * transport/lifetime proof before continuous rear request/IPA integration.
 */
bool camss_x1e_rear_public_trial_allowed(struct camss_video *video)
{
 return video && camss_x1e_rear_generation_trial_allowed(video->camss) &&
        video == &video->camss->vfe[1].line[VFE_LINE_PIX].video_out &&
        video->active_fmt.fmt.pix_mp.pixelformat == V4L2_PIX_FMT_NV12 &&
        video->active_fmt.fmt.pix_mp.width == NATIVE_REAR_NV12_WIDTH &&
        video->active_fmt.fmt.pix_mp.height == NATIVE_REAR_NV12_HEIGHT;
}

static void native_rear_public_work(struct work_struct *work)
{
 struct camss_video *video = container_of(work, struct camss_video, x1e_pix_work);
 struct native_rear_startup_result result = {};
 struct camss_buffer *buffer[2] = {};
 struct vfe_device *vfe = &video->camss->vfe[1];
 unsigned long flags;
 unsigned int s;
 int ret;

 spin_lock_irqsave(&vfe->output_lock, flags);
 buffer[0] = vfe_buf_get_pending(&vfe->line[VFE_LINE_PIX].output);
 buffer[1] = vfe_buf_get_pending(&vfe->line[VFE_LINE_PIX].output);
 spin_unlock_irqrestore(&vfe->output_lock, flags);
 if (!buffer[0] || !buffer[1])
  ret = -ENOBUFS;
 else if (READ_ONCE(video->x1e_pix_stop_requested))
  ret = -ECANCELED;
 else
  ret = native_rear_public_once(video, buffer, &result);
 /* Never publish success unless output mappings, hardware and command arena
  * all retired. No camss_buffer pointer is retained in an uncertain lease.
  */
 if (!ret && (!result.once.transaction.both_frames_complete ||
              !result.once.transaction.dma_reclaimed ||
              !result.once.transaction.owner_released ||
              !result.once.command_arena_released))
  ret = -EPROTO;
 if (ret) {
  vb2_queue_error(&video->vb2_q);
  /* The retained DMA-BUF maps outlive VB2 wrappers on uncertain hardware. */
  WRITE_ONCE(video->x1e_pix_runner_pinned,
             result.once.transaction.dma_intentionally_pinned);
 }
 for (s = 0; s < 2; s++) {
  if (!buffer[s])
   continue;
  if (!ret) {
   vb2_set_plane_payload(&buffer[s]->vb.vb2_buf, 0, NATIVE_REAR_NV12_BYTES);
   buffer[s]->vb.sequence = s;
   buffer[s]->vb.vb2_buf.timestamp = ktime_get_ns();
   vb2_buffer_done(&buffer[s]->vb.vb2_buf, VB2_BUF_STATE_DONE);
  } else {
   vb2_buffer_done(&buffer[s]->vb.vb2_buf, VB2_BUF_STATE_ERROR);
  }
 }
 WRITE_ONCE(video->x1e_pix_runner_stopped, !ret);
 WRITE_ONCE(video->x1e_pix_worker_ret, ret);
 WRITE_ONCE(video->x1e_pix_live_active, false);
 dev_info(video->camss->dev,
  "NATIVE_REAR_PUBLIC_V4L2_RESULT ret=%d frames=%u width=3840 height=2160 bytes=12441600 retained_public_FULL=1 cpu_pixel_copy=0\n",
  ret, ret ? 0U : 2U);
}

int camss_x1e_rear_public_start(struct camss_video *video, unsigned int count)
{
 if (!camss_x1e_rear_public_trial_allowed(video) || count < 2)
  return -EINVAL;
 if (READ_ONCE(video->x1e_pix_runner_pinned) ||
     READ_ONCE(video->x1e_pix_worker_started) ||
     READ_ONCE(video->x1e_pix_live_active))
  return -EBUSY;
 INIT_WORK(&video->x1e_pix_work, native_rear_public_work);
 WRITE_ONCE(video->x1e_pix_runner_stopped, false);
 WRITE_ONCE(video->x1e_pix_stop_requested, false);
 WRITE_ONCE(video->x1e_pix_worker_ret, -EINPROGRESS);
 WRITE_ONCE(video->x1e_pix_live_active, true);
 WRITE_ONCE(video->x1e_pix_worker_started, true);
 if (!schedule_work(&video->x1e_pix_work)) {
  WRITE_ONCE(video->x1e_pix_worker_started, false);
  WRITE_ONCE(video->x1e_pix_live_active, false);
  return -EBUSY;
 }
 return 0;
}

/* Join before VB2 cancels its wrappers; pending unexposed buffers are returned
 * even when the runner held an uncertain independent mapping. Hardware stop
 * was performed by the same worker, never by the generic one-WM callback.
 */
void camss_x1e_rear_public_join(struct camss_video *video)
{
 WRITE_ONCE(video->x1e_pix_stop_requested, true);
 if (READ_ONCE(video->x1e_pix_worker_started)) {
  flush_work(&video->x1e_pix_work);
  WRITE_ONCE(video->x1e_pix_worker_started, false);
 }
}
