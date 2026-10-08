/* SPDX-License-Identifier: GPL-2.0-only */
#include "native-rear-video-dma.h"

/* Called by the future rear queue while VB2 retains the ACTIVE buffer.
 * Walk every DMA-mapped segment, not orig_nents or the cached first addr[].
 * No CPU pixel mapping/copy, MMIO, VB2 completion, or ownership transfer.
 */
static int __used
native_rear_video_buffer_dma(struct vfe_device *vfe, struct camss_video *video,
                            struct camss_buffer *buffer,
                            struct native_rear_video_dma *out)
{
 struct native_rear_video_dma_scan scan = {};
 const struct v4l2_pix_format_mplane *format;
 struct sg_table *table;
 struct scatterlist *sg;
 unsigned int i;
 int ret;

 if (!vfe680_e004nt_rear_4k_target(vfe) || !video || !buffer || !out ||
     vfe != &vfe->camss->vfe[1] ||
     video != &vfe->line[VFE_LINE_PIX].video_out ||
     video->camss != vfe->camss ||
     video->active_fmt.type != V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE ||
     buffer->vb.vb2_buf.num_planes != 1 ||
     buffer->vb.vb2_buf.state != VB2_BUF_STATE_ACTIVE ||
     buffer->vb.vb2_buf.planes[0].data_offset)
  return -EINVAL;
 format = &video->active_fmt.fmt.pix_mp;
 if (format->pixelformat != V4L2_PIX_FMT_NV12 || format->num_planes != 1 ||
     format->width != NATIVE_REAR_NV12_WIDTH ||
     format->height != NATIVE_REAR_NV12_HEIGHT ||
     format->plane_fmt[0].bytesperline != NATIVE_REAR_NV12_STRIDE ||
     format->plane_fmt[0].sizeimage != NATIVE_REAR_NV12_BYTES)
  return -EINVAL;
 table = vb2_dma_sg_plane_desc(&buffer->vb.vb2_buf, 0);
 if (!table || !table->sgl || !table->nents)
  return -EINVAL;
 for_each_sgtable_dma_sg(table, sg, i) {
  ret = native_rear_video_dma_append(&scan, sg_dma_address(sg),
                                    sg_dma_len(sg));
  if (ret)
   return ret;
 }
 if (scan.segments != table->nents)
  return -EPROTO;
 return native_rear_video_dma_finish(&scan,
        vb2_plane_size(&buffer->vb.vb2_buf, 0), out);
}
