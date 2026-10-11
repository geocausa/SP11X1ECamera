
/*
 * Robust IQ hand-off for the native front queue (native_front_queue_robust).
 * The newest pending IQ packet is used and older pending ones are dropped, so a
 * consumer that catches up after a stall does not leave stale parameters in the
 * FIFO. Request ids only have to increase. When no packet is pending, the newest
 * parameters received are materialized again for this frame. The BL4 completion
 * tag always carries the hardware frame number.
 */
static struct camss_x1e_pix_iq_packet *native_front_iq_last;
static struct camss_x1e_pix_capsule_inputs *native_front_iq_last_inputs;

static void camss_x1e_pix_iq_robust_reset(void)
{
	camss_x1e_pix_iq_packet_release(native_front_iq_last);
	native_front_iq_last = NULL;
	kfree(native_front_iq_last_inputs);
	native_front_iq_last_inputs = NULL;
}

static int camss_x1e_pix_iq_provider_next_robust(
	struct camss *camss, struct camss_video *video, u64 frame,
	struct camss_x1e_epoch0_materialized *steady, bool *reused)
{
	struct camss_x1e_pix_iq_packet *packet = NULL, *stale;
	struct camss_x1e_pix_capsule_inputs *inputs;
	struct camss_x1e_epoch0_input input;
	int ret;

	if (!camss || !video || !steady || !reused || steady->materialized || !frame)
		return -EINVAL;
	*reused = false;
	if (READ_ONCE(video->x1e_pix_stop_requested))
		return -ECANCELED;

	mutex_lock(&video->x1e_pix_iq_lock);
	while (!list_empty(&video->x1e_pix_iq_pending)) {
		stale = packet;
		packet = list_first_entry(&video->x1e_pix_iq_pending,
					  struct camss_x1e_pix_iq_packet, node);
		list_del(&packet->node);
		video->x1e_pix_iq_depth--;
		camss_x1e_pix_iq_packet_release(stale);
		if (packet->request_id <= video->x1e_pix_iq_last_dequeued) {
			camss_x1e_pix_iq_packet_release(packet);
			packet = NULL;
			continue;
		}
		video->x1e_pix_iq_last_dequeued = packet->request_id;
	}
	mutex_unlock(&video->x1e_pix_iq_lock);

	if (packet) {
		inputs = kzalloc_obj(*inputs, GFP_KERNEL);
		if (!inputs) {
			camss_x1e_pix_iq_packet_release(packet);
			return -ENOMEM;
		}
		ret = camss_x1e_pix_capsule_parse(packet->capsule, packet->capsule_size, inputs);
		if (!ret && inputs->steady.subrequest)
			ret = -EPROTO;
		if (!ret && camss_x1e_native_front_queue_trial_allowed(camss))
			ret = native_nv12_commands_validate(inputs->steady.normalized_main.data,
							   inputs->steady.normalized_main.size, false);
		if (ret) {
			/* A malformed packet is dropped; the last good parameters stay. */
			kfree(inputs);
			camss_x1e_pix_iq_packet_release(packet);
			if (!native_front_iq_last_inputs)
				return ret;
			*reused = true;
		} else {
			camss_x1e_pix_iq_robust_reset();
			native_front_iq_last = packet;
			native_front_iq_last_inputs = inputs;
		}
	} else {
		*reused = true;
	}
	if (!native_front_iq_last_inputs)
		return -EAGAIN;

	input = native_front_iq_last_inputs->steady;
	input.request_id = frame;
	return camss_x1e_epoch0_materialize(camss, steady, &input);
}

