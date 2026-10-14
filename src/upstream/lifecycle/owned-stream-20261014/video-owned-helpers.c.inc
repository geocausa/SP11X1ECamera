struct camss_video_dma_hold {
	struct list_head list;
	struct dma_buf *planes[3];
	unsigned int count;
	bool exposed;
};

static bool video_owned_lifecycle(struct camss_video *video)
{
	return video->camss->res->version == CAMSS_X1E80100 &&
	       video->vb2_q.type == V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
}

static bool video_raw_output(struct camss_video *video)
{
	struct camss *camss = video->camss;
	unsigned int v, l;

	for (v = 0; v < camss->res->vfe_num; v++)
		for (l = 0; l < camss->vfe[v].res->line_num; l++)
			if (&camss->vfe[v].line[l].output[0].video_out == video)
				return !camss->vfe[v].line[l].is_pix;

	return false;
}

static void video_dma_hold_put(struct camss_video_dma_hold *hold)
{
	while (hold->count)
		dma_buf_put(hold->planes[--hold->count]);
	kfree(hold);
}

static int video_dma_hold_get(struct camss_video *video,
			      struct vb2_buffer *vb,
			      struct camss_buffer *buffer)
{
	struct camss_video_dma_hold *hold;
	struct dma_buf *plane;
	unsigned int i;

	if (!video_owned_lifecycle(video))
		return 0;
	if (!vb->num_planes || !vb->vb2_queue->mem_ops->get_dmabuf ||
	    vb->vb2_queue->memory != VB2_MEMORY_MMAP ||
	    vb->num_planes > ARRAY_SIZE(hold->planes))
		return -EOPNOTSUPP;

	hold = kzalloc_obj(*hold);
	if (!hold)
		return -ENOMEM;

	for (i = 0; i < vb->num_planes; i++) {
		plane = vb->vb2_queue->mem_ops->get_dmabuf(vb,
				vb->planes[i].mem_priv, O_RDWR);
		if (IS_ERR_OR_NULL(plane)) {
			video_dma_hold_put(hold);
			return -ENOMEM;
		}
		hold->planes[hold->count++] = plane;
	}

	list_add_tail(&hold->list, &video->dma_holds);
	buffer->dma_hold = hold;
	return 0;
}

static void video_buf_cleanup(struct vb2_buffer *vb)
{
	struct camss_video *video = vb2_get_drv_priv(vb->vb2_queue);
	struct camss_buffer *buffer = container_of(to_vb2_v4l2_buffer(vb),
						  struct camss_buffer, vb);
	struct camss_video_dma_hold *hold = buffer->dma_hold;

	if (!hold)
		return;

	buffer->dma_hold = NULL;
	if (video->lifecycle.fault && hold->exposed)
		return; /* Independent hold remains mapped until candidate reboot. */

	list_del(&hold->list);
	video_dma_hold_put(hold);
}

static void video_mark_dma_exposed(struct camss_video *video)
{
	struct camss_video_dma_hold *hold;

	list_for_each_entry(hold, &video->dma_holds, list)
		hold->exposed = true;
}

static int video_collect_subdevs(struct camss_video *video, void **subdevs)
{
	struct media_entity *entity = &video->vdev.entity;
	struct media_pad *pad;
	struct v4l2_subdev *subdev;
	unsigned int count = 0, i;

	while (entity->num_pads) {
		pad = &entity->pads[0];
		if (!(pad->flags & MEDIA_PAD_FL_SINK))
			break;

		pad = media_pad_remote_pad_first(pad);
		if (!pad || !is_media_entity_v4l2_subdev(pad->entity))
			break;
		subdev = media_entity_to_v4l2_subdev(pad->entity);
		if (count == CAMSS_VIDEO_MAX_SUBDEVS)
			return -E2BIG;
		for (i = 0; i < count; i++)
			if (subdevs[i] == subdev)
				return -ELOOP;
		subdevs[count++] = subdev;
		entity = pad->entity;
	}

	return count;
}

static bool video_subdev_is_csid(struct camss *camss,
				 struct v4l2_subdev *subdev)
{
	unsigned int i;

	for (i = 0; i < camss->res->csid_num; i++)
		if (subdev == &camss->csid[i].subdev)
			return true;
	return false;
}

static bool video_subdev_is_vfe(struct camss *camss,
				struct v4l2_subdev *subdev)
{
	unsigned int i, l;

	for (i = 0; i < camss->res->vfe_num; i++)
		for (l = 0; l < camss->vfe[i].res->line_num; l++)
			if (subdev == &camss->vfe[i].line[l].subdev)
				return true;
	return false;
}

static int video_owned_stage_call(void *context, void *device, bool on)
{
	struct camss_video *video = context;
	struct v4l2_subdev *subdev = device;
	int ret;

	ret = v4l2_subdev_call(subdev, video, s_stream, on);
	if (ret < 0 && ret != -ENOIOCTLCMD)
		dev_err(video->camss->dev, "Stream %s failed on %s: %d\n",
			on ? "start" : "stop", subdev->name, ret);
	return ret;
}

static void video_lifecycle_fault(struct camss_video *video)
{
	mutex_lock(&video->camss->stream_guard);
	video->camss->stream_fault = true;
	mutex_unlock(&video->camss->stream_guard);
	vb2_queue_error(&video->vb2_q);
	dev_err(video->camss->dev,
		"Stream teardown fault: DMA, graph, power and module held until reboot\n");
}

static int video_stop_owned(struct camss_video *video)
{
	struct camss_video_lifecycle *state = &video->lifecycle;
	unsigned int order[CAMSS_VIDEO_MAX_SUBDEVS];
	unsigned int count = 0, i;

	/* Reuse the native X1E CSID -> VFE -> PHY/sensor normal stop order. */
	for (i = 0; i < state->count; i++)
		if (video_subdev_is_csid(video->camss, state->stages[i].device))
			order[count++] = i;
	for (i = 0; i < state->count; i++)
		if (video_subdev_is_vfe(video->camss, state->stages[i].device))
			order[count++] = i;
	for (i = 0; i < state->count; i++)
		if (!video_subdev_is_csid(video->camss, state->stages[i].device) &&
		    !video_subdev_is_vfe(video->camss, state->stages[i].device))
			order[count++] = i;

	return camss_video_stop_owned(state, order, video, video_owned_stage_call);
}
