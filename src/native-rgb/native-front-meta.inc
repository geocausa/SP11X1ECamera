/* SPDX-License-Identifier: GPL-2.0-only */
/* Included in camss-video.c; no pixel processing or extra hardware producer. */
#include <media/videobuf2-vmalloc.h>
#include "native-front-stats.h"

struct native_front_meta_buffer {
 struct vb2_v4l2_buffer vb;
 struct list_head node;
};

struct native_front_meta {
 struct camss_video *owner;
 struct video_device vdev;
 struct media_pad pad;
 struct vb2_queue queue;
 struct mutex lock;
 struct mutex delivery_lock;
 struct list_head pending;
 u64 stream_id;
 u64 dropped;
 bool streaming;
};
static atomic64_t native_front_meta_stream_ids = ATOMIC64_INIT(0);
static_assert(sizeof(struct native_front_stats_header) == NATIVE_FRONT_STATS_HEADER_BYTES);
static_assert(CAMSS_X1E_3A_RAW_BYTES + CAMSS_X1E_TLBG_RAW_BYTES ==
              NATIVE_FRONT_STATS_BYTES - NATIVE_FRONT_STATS_HEADER_BYTES);

static int native_front_meta_queue_setup(struct vb2_queue *q, unsigned int *count,
                                         unsigned int *planes, unsigned int sizes[],
                                         struct device *alloc_devs[])
{
 if (*planes)
  return *planes == 1 && sizes[0] >= NATIVE_FRONT_STATS_BYTES ? 0 : -EINVAL;
 *planes = 1;
 sizes[0] = NATIVE_FRONT_STATS_BYTES;
 return 0;
}
static int native_front_meta_prepare(struct vb2_buffer *vb)
{
 if (vb2_plane_size(vb, 0) < NATIVE_FRONT_STATS_BYTES || !vb2_plane_vaddr(vb, 0))
  return -EINVAL;
 vb2_set_plane_payload(vb, 0, 0);
 return 0;
}
static void native_front_meta_queue(struct vb2_buffer *vb)
{
 struct native_front_meta *meta = vb2_get_drv_priv(vb->vb2_queue);
 struct native_front_meta_buffer *buffer =
  container_of(to_vb2_v4l2_buffer(vb), struct native_front_meta_buffer, vb);
 mutex_lock(&meta->delivery_lock);
 list_add_tail(&buffer->node, &meta->pending);
 mutex_unlock(&meta->delivery_lock);
}
static int native_front_meta_start(struct vb2_queue *q, unsigned int count)
{
 struct native_front_meta *meta = vb2_get_drv_priv(q);
 mutex_lock(&meta->delivery_lock);
 meta->streaming = true;
 mutex_unlock(&meta->delivery_lock);
 return 0;
}
static void native_front_meta_stop(struct vb2_queue *q)
{
 struct native_front_meta *meta = vb2_get_drv_priv(q);
 struct native_front_meta_buffer *buffer, *tmp;
 /* Serializes any ongoing CPU copy. No hardware owns these metadata buffers. */
 mutex_lock(&meta->delivery_lock);
 meta->streaming = false;
 list_for_each_entry_safe(buffer, tmp, &meta->pending, node) {
  list_del(&buffer->node);
  vb2_buffer_done(&buffer->vb.vb2_buf, VB2_BUF_STATE_ERROR);
 }
 mutex_unlock(&meta->delivery_lock);
}
static const struct vb2_ops native_front_meta_queue_ops = {
 .queue_setup = native_front_meta_queue_setup,
 .buf_prepare = native_front_meta_prepare,
 .buf_queue = native_front_meta_queue,
 .start_streaming = native_front_meta_start,
 .stop_streaming = native_front_meta_stop,
};
static int native_front_meta_querycap(struct file *file, void *fh,
                                      struct v4l2_capability *cap)
{
 struct native_front_meta *meta = video_drvdata(file);
 strscpy(cap->driver, "qcom-camss", sizeof(cap->driver));
 strscpy(cap->card, meta->vdev.name, sizeof(cap->card));
 snprintf(cap->bus_info, sizeof(cap->bus_info), "platform:%s",
          dev_name(meta->owner->camss->dev));
 return 0;
}
static int native_front_meta_enum_fmt(struct file *file, void *fh,
                                      struct v4l2_fmtdesc *fmt)
{
 if (fmt->index)
  return -EINVAL;
 fmt->pixelformat = NATIVE_FRONT_STATS_MAGIC;
 strscpy(fmt->description, "X1E frame-associated statistics", sizeof(fmt->description));
 return 0;
}
static int native_front_meta_format(struct file *file, void *fh,
                                    struct v4l2_format *fmt)
{
 if (fmt->type != V4L2_BUF_TYPE_META_CAPTURE)
  return -EINVAL;
 memset(&fmt->fmt, 0, sizeof(fmt->fmt));
 fmt->fmt.meta.dataformat = NATIVE_FRONT_STATS_MAGIC;
 fmt->fmt.meta.buffersize = NATIVE_FRONT_STATS_BYTES;
 return 0;
}
static int native_front_meta_set_format(struct file *file, void *fh,
                                        struct v4l2_format *fmt)
{
 struct native_front_meta *meta = video_drvdata(file);
 if (vb2_is_busy(&meta->queue))
  return -EBUSY;
 return native_front_meta_format(file, fh, fmt);
}
static const struct v4l2_ioctl_ops native_front_meta_ioctl_ops = {
 .vidioc_querycap = native_front_meta_querycap,
 .vidioc_enum_fmt_meta_cap = native_front_meta_enum_fmt,
 .vidioc_g_fmt_meta_cap = native_front_meta_format,
 .vidioc_try_fmt_meta_cap = native_front_meta_format,
 .vidioc_s_fmt_meta_cap = native_front_meta_set_format,
 .vidioc_reqbufs = vb2_ioctl_reqbufs,
 .vidioc_create_bufs = vb2_ioctl_create_bufs,
 .vidioc_prepare_buf = vb2_ioctl_prepare_buf,
 .vidioc_querybuf = vb2_ioctl_querybuf,
 .vidioc_qbuf = vb2_ioctl_qbuf,
 .vidioc_dqbuf = vb2_ioctl_dqbuf,
 .vidioc_expbuf = vb2_ioctl_expbuf,
 .vidioc_streamon = vb2_ioctl_streamon,
 .vidioc_streamoff = vb2_ioctl_streamoff,
};
static const struct v4l2_file_operations native_front_meta_fops = {
 .owner = THIS_MODULE,
 .open = v4l2_fh_open,
 .release = vb2_fop_release,
 .unlocked_ioctl = video_ioctl2,
 .poll = vb2_fop_poll,
 .mmap = vb2_fop_mmap,
};
static void native_front_meta_release(struct video_device *vdev)
{
 struct native_front_meta *meta = video_get_drvdata(vdev);
 struct camss *camss = meta->owner->camss;
 media_entity_cleanup(&vdev->entity);
 mutex_destroy(&meta->delivery_lock);
 mutex_destroy(&meta->lock);
 kfree(meta);
 if (atomic_dec_and_test(&camss->ref_count))
  camss_delete(camss);
}
static int native_front_meta_register(struct camss_video *video)
{
 struct native_front_meta *meta;
 struct video_device *vdev;
 struct vb2_queue *q;
 int ret;
 if (!camss_x1e_native_front_meta_trial_allowed(video->camss) ||
     !video_is_x1e_front_pix(video))
  return 0;
 meta = kzalloc(sizeof(*meta), GFP_KERNEL);
 if (!meta)
  return -ENOMEM;
 meta->owner = video;
 mutex_init(&meta->lock);
 mutex_init(&meta->delivery_lock);
 INIT_LIST_HEAD(&meta->pending);
 q = &meta->queue;
 q->type = V4L2_BUF_TYPE_META_CAPTURE;
 q->io_modes = VB2_MMAP | VB2_DMABUF;
 q->drv_priv = meta;
 q->buf_struct_size = sizeof(struct native_front_meta_buffer);
 q->ops = &native_front_meta_queue_ops;
 q->mem_ops = &vb2_vmalloc_memops;
 q->timestamp_flags = V4L2_BUF_FLAG_TIMESTAMP_MONOTONIC;
 q->lock = &meta->lock;
 q->dev = video->camss->dev;
 ret = vb2_queue_init(q);
 if (ret)
  goto fail;
 vdev = &meta->vdev;
 meta->pad.flags = MEDIA_PAD_FL_SINK;
 vdev->entity.function = MEDIA_ENT_F_IO_V4L;
 ret = media_entity_pads_init(&vdev->entity, 1, &meta->pad);
 if (ret)
  goto fail;
 strscpy(vdev->name, "msm_vfe1_stats", sizeof(vdev->name));
 vdev->fops = &native_front_meta_fops;
 vdev->ioctl_ops = &native_front_meta_ioctl_ops;
 vdev->device_caps = V4L2_CAP_META_CAPTURE | V4L2_CAP_STREAMING | V4L2_CAP_IO_MC;
 vdev->release = native_front_meta_release;
 vdev->v4l2_dev = video->vdev.v4l2_dev;
 vdev->vfl_dir = VFL_DIR_RX;
 vdev->queue = q;
 vdev->lock = &meta->lock;
 video_set_drvdata(vdev, meta);
 atomic_inc(&video->camss->ref_count);
 ret = video_register_device(vdev, VFL_TYPE_VIDEO, -1);
 if (ret) {
  atomic_dec(&video->camss->ref_count);
  media_entity_cleanup(&vdev->entity);
  goto fail;
 }
 ret = media_create_pad_link(
  &video->camss->vfe[1].line[VFE_LINE_PIX].subdev.entity, MSM_VFE_PAD_SRC,
  &vdev->entity, 0, MEDIA_LNK_FL_ENABLED | MEDIA_LNK_FL_IMMUTABLE);
 if (ret) {
  vb2_video_unregister_device(vdev);
  return ret;
 }
 mutex_lock(&video->native_meta_lock);
 video->native_meta = meta;
 mutex_unlock(&video->native_meta_lock);
 return 0;
fail:
 mutex_destroy(&meta->delivery_lock);
 mutex_destroy(&meta->lock);
 kfree(meta);
 return ret;
}
static void native_front_meta_unregister(struct camss_video *video)
{
 struct native_front_meta *meta;
 /* A publisher cannot retain a freed metadata-node pointer across unregister. */
 mutex_lock(&video->native_meta_lock);
 meta = video->native_meta;
 video->native_meta = NULL;
 mutex_unlock(&video->native_meta_lock);
 if (meta)
  vb2_video_unregister_device(&meta->vdev);
}
static void native_front_meta_reset(struct camss_video *video)
{
 struct native_front_meta *meta;
 mutex_lock(&video->native_meta_lock);
 meta = video->native_meta;
 if (meta) {
  mutex_lock(&meta->delivery_lock);
  meta->stream_id = atomic64_inc_return(&native_front_meta_stream_ids);
  meta->dropped = 0;
  mutex_unlock(&meta->delivery_lock);
 }
 mutex_unlock(&video->native_meta_lock);
}

void camss_x1e_front_meta_complete(struct camss_video *video,
                                 u32 sequence, u64 timestamp)
{
 struct native_front_meta *meta;
 struct native_front_meta_buffer *buffer;
 struct native_front_stats_header header = {};
 enum vb2_buffer_state state = VB2_BUF_STATE_ERROR;
 u8 *out;

 mutex_lock(&video->native_meta_lock);
 meta = video->native_meta;
 if (!meta)
  goto out_owner;
 mutex_lock(&meta->delivery_lock);
 if (!meta->streaming)
  goto out_delivery;
 if (list_empty(&meta->pending)) {
  meta->dropped++;
  goto out_delivery;
 }
 buffer = list_first_entry(&meta->pending, struct native_front_meta_buffer, node);
 list_del(&buffer->node);
 out = vb2_plane_vaddr(&buffer->vb.vb2_buf, 0);
 mutex_lock(&video->x1e_3a_lock);
 mutex_lock(&video->x1e_tlbg_lock);
 /* Both owned snapshots came from this retirement, after all owner checks. */
 if (!out || !meta->stream_id || !video->x1e_3a_valid || !video->x1e_tlbg_valid ||
     video->x1e_3a_generation != (u64)sequence + 1 ||
     video->x1e_tlbg_generation != video->x1e_3a_generation ||
     video->x1e_tlbg_source_seq != video->x1e_3a_source_seq ||
     video->x1e_tlbg_slot != video->x1e_3a_slot)
  goto out_snapshots;
 header.magic = cpu_to_le32(NATIVE_FRONT_STATS_MAGIC);
 header.version = cpu_to_le16(NATIVE_FRONT_STATS_VERSION);
 header.header_bytes = cpu_to_le16(sizeof(header));
 header.stream_id = cpu_to_le64(meta->stream_id);
 header.timestamp_ns = cpu_to_le64(timestamp);
 header.sequence = cpu_to_le32(sequence);
 header.source_sequence = cpu_to_le32(video->x1e_3a_source_seq);
 header.dropped = cpu_to_le64(meta->dropped);
 header.flags = cpu_to_le32(meta->dropped ? NATIVE_FRONT_STATS_F_DISCONTINUITY : 0);
 header.aec_bytes = cpu_to_le32(NATIVE_FRONT_STATS_AEC_BYTES);
 header.bhist_bytes = cpu_to_le32(NATIVE_FRONT_STATS_BHIST_BYTES);
 header.awb_bytes = cpu_to_le32(NATIVE_FRONT_STATS_AWB_BYTES);
 header.tlbg_bytes = cpu_to_le32(NATIVE_FRONT_STATS_TLBG_BYTES);
 memcpy(out, &header, sizeof(header));
 memcpy(out + sizeof(header), video->x1e_3a_snapshot, CAMSS_X1E_3A_RAW_BYTES);
 memcpy(out + sizeof(header) + CAMSS_X1E_3A_RAW_BYTES,
        video->x1e_tlbg_snapshot, CAMSS_X1E_TLBG_RAW_BYTES);
 buffer->vb.vb2_buf.timestamp = timestamp;
 buffer->vb.sequence = sequence;
 buffer->vb.field = V4L2_FIELD_NONE;
 vb2_set_plane_payload(&buffer->vb.vb2_buf, 0, NATIVE_FRONT_STATS_BYTES);
 state = VB2_BUF_STATE_DONE;
out_snapshots:
 mutex_unlock(&video->x1e_tlbg_lock);
 mutex_unlock(&video->x1e_3a_lock);
 vb2_buffer_done(&buffer->vb.vb2_buf, state);
out_delivery:
 mutex_unlock(&meta->delivery_lock);
out_owner:
 mutex_unlock(&video->native_meta_lock);
}
