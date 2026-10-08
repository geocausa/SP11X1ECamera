/* SPDX-License-Identifier: GPL-2.0-only */
#ifdef __KERNEL__
#include <linux/dma-buf.h>
#include <linux/fcntl.h>
MODULE_IMPORT_NS("DMA_BUF");
#endif

/* A driver-owned attachment/mapping, independent of VB2's attachment.
 * It retains no camss_buffer/VB2 pointer after admission. On uncertain hardware
 * stop it stays pinned even if VB2 cancels/frees its own wrapper/mapping.
 */
struct native_rear_video_lease {
 struct dma_buf *dbuf;
 struct dma_buf_attachment *attachment;
 struct sg_table *table;
 struct native_rear_video_dma span;
 bool acquired, exposed, stop_proven;
};

static bool __used
native_rear_video_lease_valid(const struct native_rear_video_lease *lease)
{
 return lease && lease->acquired && lease->dbuf && lease->attachment &&
        lease->table && lease->span.y_iova && lease->span.uv_iova ==
        lease->span.y_iova + NATIVE_REAR_NV12_UV_OFFSET &&
        lease->span.mapped_bytes >= NATIVE_REAR_NV12_BYTES;
}

static int __used
native_rear_video_lease_get(struct vfe_device *vfe, struct camss_video *video,
                          struct camss_buffer *buffer,
                          struct native_rear_video_lease *lease)
{
 struct native_rear_video_lease candidate = {};
 struct native_rear_video_dma initial;
 struct vb2_buffer *vb;
 int ret;

 if (!lease)
  return -EINVAL;
 if (lease->acquired || lease->dbuf || lease->attachment || lease->table ||
     lease->exposed || lease->stop_proven)
  return -EBUSY;
 ret = native_rear_video_buffer_dma(vfe, video, buffer, &initial);
 if (ret)
  return ret;
 vb = &buffer->vb.vb2_buf;
 if (!vb->vb2_queue || vb->vb2_queue != &video->vb2_q ||
     vb->vb2_queue->mem_ops != &vb2_dma_sg_memops ||
     vb->vb2_queue->dma_dir != DMA_FROM_DEVICE)
  return -EINVAL;
 if (vb->memory == VB2_MEMORY_MMAP) {
  if (!vb->planes[0].mem_priv)
   return -EINVAL;
  candidate.dbuf = vb2_dma_sg_memops.get_dmabuf(vb,
                   vb->planes[0].mem_priv, O_CLOEXEC | O_RDWR);
  if (IS_ERR_OR_NULL(candidate.dbuf))
   return candidate.dbuf ? PTR_ERR(candidate.dbuf) : -ENOMEM;
 } else if (vb->memory == VB2_MEMORY_DMABUF) {
  candidate.dbuf = vb->planes[0].dbuf;
  if (!candidate.dbuf)
   return -EINVAL;
  get_dma_buf(candidate.dbuf);
 } else {
  return -EOPNOTSUPP;
 }
 candidate.attachment = dma_buf_attach(candidate.dbuf, vfe->camss->dev);
 if (IS_ERR(candidate.attachment)) {
  ret = PTR_ERR(candidate.attachment);
  goto put_dbuf;
 }
 candidate.table = dma_buf_map_attachment_unlocked(candidate.attachment,
                                                   DMA_FROM_DEVICE);
 if (IS_ERR(candidate.table)) {
  ret = PTR_ERR(candidate.table);
  goto detach;
 }
 /* Program this retained mapping, which may differ from VB2's mapping. */
 ret = native_rear_video_dma_table(candidate.table, vb2_plane_size(vb, 0),
                                   &candidate.span);
 if (ret)
  goto unmap;
 candidate.acquired = true;
 *lease = candidate;
 return 0;
unmap:
 dma_buf_unmap_attachment_unlocked(candidate.attachment, candidate.table,
                                   DMA_FROM_DEVICE);
detach:
 dma_buf_detach(candidate.dbuf, candidate.attachment);
put_dbuf:
 dma_buf_put(candidate.dbuf);
 return ret;
}

static int __used
native_rear_video_lease_expose(struct native_rear_video_lease *lease)
{
 if (!native_rear_video_lease_valid(lease) || lease->exposed ||
     lease->stop_proven)
  return -EINVAL;
 lease->exposed = true; /* Set before any potentially exposing MMIO. */
 return 0;
}

static int __used
native_rear_video_lease_stop(struct native_rear_video_lease *lease,
                           bool csid_quiesced, bool bus_stopped,
                           bool rtcdm_stopped, bool source_stopped)
{
 if (!native_rear_video_lease_valid(lease) || !lease->exposed ||
     !csid_quiesced || !bus_stopped || !rtcdm_stopped || !source_stopped)
  return -EBUSY;
 lease->stop_proven = true;
 return 0;
}

static int __used
native_rear_video_lease_put(struct native_rear_video_lease *lease)
{
 if (!native_rear_video_lease_valid(lease))
  return -EINVAL;
 if (lease->exposed && !lease->stop_proven)
  return -EBUSY;
 dma_buf_unmap_attachment_unlocked(lease->attachment, lease->table,
                                   DMA_FROM_DEVICE);
 dma_buf_detach(lease->dbuf, lease->attachment);
 dma_buf_put(lease->dbuf);
 memset(lease, 0, sizeof(*lease));
 return 0;
}
