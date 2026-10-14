static int video_prepare_streaming(struct vb2_queue *q)
{
	struct camss_video *video = vb2_get_drv_priv(q);
	struct camss *camss = video->camss;
	bool owned = video_owned_lifecycle(video);
	int ret;

	mutex_lock(&camss->stream_guard);
	if (camss->stream_fault || (owned && camss->stream_owner)) {
		ret = camss->stream_fault ? -EIO : -EBUSY;
		mutex_unlock(&camss->stream_guard);
		return ret;
	}
	if (owned && (!video_raw_output(video) || q->memory != VB2_MEMORY_MMAP)) {
		mutex_unlock(&camss->stream_guard);
		return -EOPNOTSUPP;
	}
	if (owned)
		camss->stream_owner = video;
	mutex_unlock(&camss->stream_guard);

	if (owned) {
		if (!try_module_get(THIS_MODULE)) {
			ret = -ENODEV;
			goto release_owner;
		}
		video->module_held = true;
	}

	ret = v4l2_pipeline_pm_get(&video->vdev.entity);
	if (ret) {
		dev_err(camss->dev, "Failed to power up pipeline: %d\n", ret);
		if (video->module_held) {
			video->module_held = false;
			module_put(THIS_MODULE);
		}
		goto release_owner;
	}
	video->pm_held = true;
	return 0;

release_owner:
	if (owned) {
		mutex_lock(&camss->stream_guard);
		camss->stream_owner = NULL;
		mutex_unlock(&camss->stream_guard);
	}
	return ret;
}
