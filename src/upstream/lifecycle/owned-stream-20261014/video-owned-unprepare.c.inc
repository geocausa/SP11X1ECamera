static void video_unprepare_streaming(struct vb2_queue *q)
{
	struct camss_video *video = vb2_get_drv_priv(q);

	if (video->lifecycle.fault)
		return;

	if (video->pm_held) {
		v4l2_pipeline_pm_put(&video->vdev.entity);
		video->pm_held = false;
	}
	if (video_owned_lifecycle(video)) {
		mutex_lock(&video->camss->stream_guard);
		if (video->camss->stream_owner == video)
			video->camss->stream_owner = NULL;
		mutex_unlock(&video->camss->stream_guard);
	}
	if (video->module_held) {
		video->module_held = false;
		module_put(THIS_MODULE);
	}
}
