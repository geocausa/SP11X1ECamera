/* SPDX-License-Identifier: GPL-2.0-only */
/* CPU-only META_OUTPUT control-plane endpoint; provider owns every submitted
 * capsule before DQBUF. No user buffer is mapped for hardware or held by DMA.
 * Proposed CAMSS gamma subset, trial-only; upstream ABI review is still needed.
 */
#include <linux/media/v4l2-isp.h>
#include "native-front-param-state.h"
#include "native-front-gamma-kernel.h"
static_assert(sizeof(struct v4l2_isp_params_block_header)==8);
static_assert(offsetof(struct v4l2_isp_params_buffer,data)==NF_ISP_HEADER_BYTES);

struct native_front_param_buffer {
 struct vb2_v4l2_buffer vb;
 struct list_head node;
 u8 gamma[NF_GAMMA_BYTES];
 int update;
};
struct native_front_param_queue {
 struct camss_video *owner;
 struct video_device vdev;
 struct media_pad pad;
 struct vb2_queue queue;
 struct mutex lock,dispatch_lock;
 struct list_head pending;
 struct native_front_param_state state;
 bool detached;
};

static int native_front_param_submit_backend(void *ctx,u64 request,
                                             const u8 *gamma,size_t bytes)
{
 struct native_front_params packet={};
 packet.magic=cpu_to_le32(NATIVE_FRONT_PARAMS_MAGIC);
 packet.version=cpu_to_le16(NATIVE_FRONT_PARAMS_VERSION);
 packet.bytes=cpu_to_le16(NATIVE_FRONT_PARAMS_BYTES);
 packet.request_id=cpu_to_le64(request);
 return gamma ? camss_x1e_front_params_gamma_submit(ctx,(u8 *)&packet,sizeof(packet),gamma,bytes) :
                camss_x1e_front_params_submit(ctx,(u8 *)&packet,sizeof(packet));
}
static void native_front_param_process(struct native_front_param_queue *q,
                                       struct native_front_param_buffer *buffer)
{
 u64 request=q->state.next;
 int ret=q->detached ? -ENODEV : native_front_param_state_submit(&q->state,buffer->gamma,buffer->update,
                                         native_front_param_submit_backend,q->owner);
 if(ret) {
  q->state.failed=1;
  atomic_set(&q->owner->native_param_queue_ready,0);
  dev_err(q->owner->camss->dev,"NATIVE_FRONT_PARAM_QUEUE_ERROR request=%llu ret=%d\n",
          (unsigned long long)request,ret);
 }
 buffer->vb.sequence=request;
 buffer->vb.field=V4L2_FIELD_NONE;
 buffer->vb.vb2_buf.timestamp=ktime_get_ns();
 vb2_buffer_done(&buffer->vb.vb2_buf,ret?VB2_BUF_STATE_ERROR:VB2_BUF_STATE_DONE);
}
static void native_front_param_return(struct native_front_param_queue *q,
                                      enum vb2_buffer_state state)
{
 struct native_front_param_buffer *b,*tmp;
 list_for_each_entry_safe(b,tmp,&q->pending,node) {
  list_del(&b->node);
  vb2_buffer_done(&b->vb.vb2_buf,state);
 }
}
static int native_front_param_setup(struct vb2_queue *q,unsigned int *count,
                                    unsigned int *planes,unsigned int sizes[],
                                    struct device *alloc_devs[])
{
 if(*planes)return *planes==1 && sizes[0]>=NF_ISP_MAX_BYTES?0:-EINVAL;
 *planes=1;sizes[0]=NF_ISP_MAX_BYTES;return 0;
}
static int native_front_param_prepare(struct vb2_buffer *vb)
{
 struct native_front_param_buffer *b=container_of(to_vb2_v4l2_buffer(vb),
                                                   struct native_front_param_buffer,vb);
 size_t bytes=vb2_get_plane_payload(vb,0);
 const void *data=vb2_plane_vaddr(vb,0);
 u32 *scratch;
 u8 *owned;
 int update=0,ret;
 if(!data || bytes<NF_ISP_HEADER_BYTES || bytes>NF_ISP_MAX_BYTES ||
    bytes>vb2_plane_size(vb,0))return -EINVAL;
 owned=kmemdup(data,bytes,GFP_KERNEL);
 scratch=kmalloc(NF_GAMMA_WORD_COUNT*sizeof(*scratch),GFP_KERNEL);
 if(!owned || !scratch) {ret=-ENOMEM;goto out;}
 ret=native_front_isp_decode(owned,bytes,scratch,NF_GAMMA_WORD_COUNT,
                             b->gamma,NF_GAMMA_BYTES,&update);
 if(!ret) {
  b->update=update;
  if(!update)memzero_explicit(b->gamma,sizeof(b->gamma));
 }
out:
 if(owned) {memzero_explicit(owned,bytes);kfree(owned);}
 if(scratch) {memzero_explicit(scratch,NF_GAMMA_WORD_COUNT*sizeof(*scratch));kfree(scratch);}
 return ret;
}
static void native_front_param_finish(struct vb2_buffer *vb)
{
 struct native_front_param_buffer *b=container_of(to_vb2_v4l2_buffer(vb),
                                                   struct native_front_param_buffer,vb);
 memzero_explicit(b->gamma,sizeof(b->gamma));b->update=0;
}
static void native_front_param_queue_buffer(struct vb2_buffer *vb)
{
 struct native_front_param_queue *q=vb2_get_drv_priv(vb->vb2_queue);
 struct native_front_param_buffer *b=container_of(to_vb2_v4l2_buffer(vb),
                                                   struct native_front_param_buffer,vb);
 mutex_lock(&q->dispatch_lock);
 if(q->state.active)native_front_param_process(q,b);
 else list_add_tail(&b->node,&q->pending);
 mutex_unlock(&q->dispatch_lock);
}
static bool native_front_param_pixel_open(struct camss_video *video)
{
 unsigned long flags;
 bool singular;
 spin_lock_irqsave(&video->vdev.fh_lock,flags);
 singular=list_is_singular(&video->vdev.fh_list);
 spin_unlock_irqrestore(&video->vdev.fh_lock,flags);
 return singular;
}
static int native_front_param_start(struct vb2_queue *vb,unsigned int count)
{
 struct native_front_param_queue *q=vb2_get_drv_priv(vb);
 struct camss_video *video=q->owner;
 struct native_front_param_buffer *b,*tmp;
 int ret=0;
 mutex_lock(&q->dispatch_lock);
 if(q->detached || count<4 || video->vb2_q.streaming || READ_ONCE(video->x1e_pix_runner_pinned) ||
    READ_ONCE(video->x1e_pix_worker_started) || READ_ONCE(video->x1e_pix_live_active) ||
    !native_front_param_pixel_open(video)) {
  native_front_param_return(q,VB2_BUF_STATE_QUEUED);
  ret=-EBUSY;goto out;
 }
 /* No hardware is live. Retire any previous producer session before assigning
  * IDs5 onward; the startup profile loader seeds provider request4.
  */
 camss_x1e_pix_iq_session_close(video);
 native_front_param_state_reset(&q->state);
 list_for_each_entry_safe(b,tmp,&q->pending,node) {
  list_del(&b->node);native_front_param_process(q,b);
 }
 atomic_set(&video->native_param_queue_ready,!q->state.failed);
out:
 mutex_unlock(&q->dispatch_lock);return ret;
}
static void native_front_param_stop(struct vb2_queue *vb)
{
 struct native_front_param_queue *q=vb2_get_drv_priv(vb);
 mutex_lock(&q->dispatch_lock);
 atomic_set(&q->owner->native_param_queue_ready,0);
 native_front_param_return(q,VB2_BUF_STATE_ERROR);
 memzero_explicit(&q->state,sizeof(q->state));
 /* Pixel STREAMOFF owns hardware/provider retirement. These user buffers have
  * already transferred independent CPU copies, so freeing them touches no DMA.
  */
 mutex_unlock(&q->dispatch_lock);
}
static const struct vb2_ops native_front_param_ops={
 .queue_setup=native_front_param_setup,.buf_prepare=native_front_param_prepare,
 .buf_queue=native_front_param_queue_buffer,.buf_finish=native_front_param_finish,
 .buf_cleanup=native_front_param_finish,
 .start_streaming=native_front_param_start,.stop_streaming=native_front_param_stop,
};
static int native_front_param_querycap(struct file *file,void *fh,
                                       struct v4l2_capability *cap)
{
 struct native_front_param_queue *q=video_drvdata(file);
 strscpy(cap->driver,"qcom-camss",sizeof(cap->driver));
 strscpy(cap->card,q->vdev.name,sizeof(cap->card));
 snprintf(cap->bus_info,sizeof(cap->bus_info),"platform:%s",dev_name(q->owner->camss->dev));
 return 0;
}
static int native_front_param_enum_fmt(struct file *file,void *fh,struct v4l2_fmtdesc *fmt)
{
 if(fmt->index)return -EINVAL;
 fmt->pixelformat=NF_ISP_FORMAT;
 strscpy(fmt->description,"CAMSS ISP parameters (trial subset)",sizeof(fmt->description));
 return 0;
}
static int native_front_param_format(struct file *file,void *fh,struct v4l2_format *fmt)
{
 if(fmt->type!=V4L2_BUF_TYPE_META_OUTPUT)return -EINVAL;
 memset(&fmt->fmt,0,sizeof(fmt->fmt));
 fmt->fmt.meta.dataformat=NF_ISP_FORMAT;fmt->fmt.meta.buffersize=NF_ISP_MAX_BYTES;return 0;
}
static int native_front_param_set_format(struct file *file,void *fh,struct v4l2_format *fmt)
{
 struct native_front_param_queue *q=video_drvdata(file);
 if(vb2_is_busy(&q->queue))return -EBUSY;
 return native_front_param_format(file,fh,fmt);
}
static int native_front_param_open(struct file *file)
{
 int ret=v4l2_fh_open(file);
 if(ret)return ret;
 if(!v4l2_fh_is_singular_file(file)) {v4l2_fh_release(file);return -EBUSY;}
 return 0;
}
static const struct v4l2_ioctl_ops native_front_param_ioctl_ops={
 .vidioc_querycap=native_front_param_querycap,
 .vidioc_enum_fmt_meta_out=native_front_param_enum_fmt,
 .vidioc_g_fmt_meta_out=native_front_param_format,
 .vidioc_try_fmt_meta_out=native_front_param_format,
 .vidioc_s_fmt_meta_out=native_front_param_set_format,
 .vidioc_reqbufs=vb2_ioctl_reqbufs,.vidioc_create_bufs=vb2_ioctl_create_bufs,
 .vidioc_prepare_buf=vb2_ioctl_prepare_buf,.vidioc_querybuf=vb2_ioctl_querybuf,
 .vidioc_qbuf=vb2_ioctl_qbuf,.vidioc_dqbuf=vb2_ioctl_dqbuf,.vidioc_expbuf=vb2_ioctl_expbuf,
 .vidioc_streamon=vb2_ioctl_streamon,.vidioc_streamoff=vb2_ioctl_streamoff,
};
static const struct v4l2_file_operations native_front_param_fops={
 .owner=THIS_MODULE,.open=native_front_param_open,.release=vb2_fop_release,
 .unlocked_ioctl=video_ioctl2,.poll=vb2_fop_poll,.mmap=vb2_fop_mmap,
};
static void native_front_param_release(struct video_device *vdev)
{
 struct native_front_param_queue *q=video_get_drvdata(vdev);
 struct camss *camss=q->owner->camss;
 media_entity_cleanup(&vdev->entity);
 memzero_explicit(&q->state,sizeof(q->state));
 mutex_destroy(&q->dispatch_lock);mutex_destroy(&q->lock);kfree(q);
 if(atomic_dec_and_test(&camss->ref_count))camss_delete(camss);
}
static int native_front_param_register(struct camss_video *video)
{
 struct native_front_param_queue *q;
 struct vb2_queue *vb;
 struct video_device *vdev;
 int ret;
 if(!video_is_x1e_front_pix(video) ||
    !camss_x1e_native_front_param_queue_trial_allowed(video->camss))return 0;
 q=kzalloc(sizeof(*q),GFP_KERNEL);if(!q)return -ENOMEM;
 q->owner=video;mutex_init(&q->lock);mutex_init(&q->dispatch_lock);INIT_LIST_HEAD(&q->pending);
 vb=&q->queue;vb->type=V4L2_BUF_TYPE_META_OUTPUT;vb->io_modes=VB2_MMAP;
 vb->drv_priv=q;vb->buf_struct_size=sizeof(struct native_front_param_buffer);
 vb->ops=&native_front_param_ops;vb->mem_ops=&vb2_vmalloc_memops;
 vb->timestamp_flags=V4L2_BUF_FLAG_TIMESTAMP_MONOTONIC;vb->lock=&q->lock;
 vb->dev=video->camss->dev;vb->min_queued_buffers=4;
 ret=vb2_queue_init(vb);if(ret)goto fail;
 vdev=&q->vdev;q->pad.flags=MEDIA_PAD_FL_SOURCE;vdev->entity.function=MEDIA_ENT_F_IO_V4L;
 ret=media_entity_pads_init(&vdev->entity,1,&q->pad);if(ret)goto fail;
 strscpy(vdev->name,"msm_vfe1_params",sizeof(vdev->name));
 vdev->fops=&native_front_param_fops;vdev->ioctl_ops=&native_front_param_ioctl_ops;
 vdev->device_caps=V4L2_CAP_META_OUTPUT|V4L2_CAP_STREAMING|V4L2_CAP_IO_MC;
 vdev->release=native_front_param_release;vdev->v4l2_dev=video->vdev.v4l2_dev;
 vdev->vfl_dir=VFL_DIR_TX;vdev->queue=vb;vdev->lock=&q->lock;video_set_drvdata(vdev,q);
 atomic_inc(&video->camss->ref_count);
 ret=video_register_device(vdev,VFL_TYPE_VIDEO,-1);
 if(ret) {atomic_dec(&video->camss->ref_count);media_entity_cleanup(&vdev->entity);goto fail;}
 /* Control-plane association is the owning VFE, not an image data link.
  * Final topology/capability negotiation remains part of upstream review.
  */
 video->native_param_queue=q;return 0;
fail:
 mutex_destroy(&q->dispatch_lock);mutex_destroy(&q->lock);kfree(q);return ret;
}
static void native_front_param_unregister(struct camss_video *video)
{
 struct native_front_param_queue *q=video->native_param_queue;
 video->native_param_queue=NULL;atomic_set(&video->native_param_queue_ready,0);
 if(q) {
  mutex_lock(&q->dispatch_lock);q->detached=true;q->state.failed=1;
  mutex_unlock(&q->dispatch_lock);vb2_video_unregister_device(&q->vdev);
 }
}
