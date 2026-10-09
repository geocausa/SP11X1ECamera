/* SPDX-License-Identifier: GPL-2.0-only */
/* Synchronous copy into independent VB2 metadata after original all-ten-WM
 * proof. This copy neither retires nor retains a hardware DMA allocation.
 */
int camss_x1e_rear_meta_publish(struct camss_video *video,u64 owner,
 u64 generation,u32 cursor,u64 timestamp,const void *const planes[6],
 const size_t lengths[6])
{
 struct native_front_meta *meta;
 struct native_front_meta_buffer *buffer;
 struct native_rear_stats_identity id={};
 void *out;
 int ret=0;
 if(!video||!owner||!generation||!cursor||!timestamp)return -EINVAL;
 mutex_lock(&video->native_meta_lock);
 meta=video->native_meta;
 if(!meta||!meta->rear){
  ret=-EOPNOTSUPP;
  goto out_owner;
 }
 mutex_lock(&meta->delivery_lock);
 if(!meta->streaming||list_empty(&meta->pending)){
  if(meta->dropped==U64_MAX){ret=-EOVERFLOW;goto out_delivery;}
  meta->dropped++;
  goto out_delivery; /* Existing manual video remains usable without meta. */
 }
 buffer=list_first_entry(&meta->pending,struct native_front_meta_buffer,node);
 out=vb2_plane_vaddr(&buffer->vb.vb2_buf,0);
 id.stream=meta->stream_id;
 id.timestamp=timestamp;
 id.owner=owner;
 id.generation=generation;
 id.sequence=video->native_rear_completed;
 id.cursor=cursor;
 id.dropped=meta->dropped;
 if(vb2_plane_size(&buffer->vb.vb2_buf,0)<NATIVE_REAR_STATS_BYTES){ret=-EINVAL;goto out_delivery;}
 ret=native_rear_stats_pack(out,NATIVE_REAR_STATS_BYTES,
                            &id,planes,lengths);
 if(ret)goto out_delivery; /* Leave the pending buffer unchanged on rejection. */
 list_del(&buffer->node);
 buffer->vb.vb2_buf.timestamp=timestamp;
 buffer->vb.sequence=id.sequence;
 buffer->vb.field=V4L2_FIELD_NONE;
 vb2_set_plane_payload(&buffer->vb.vb2_buf,0,NATIVE_REAR_STATS_BYTES);
 vb2_buffer_done(&buffer->vb.vb2_buf,VB2_BUF_STATE_DONE);
out_delivery:
 mutex_unlock(&meta->delivery_lock);
out_owner:
 mutex_unlock(&video->native_meta_lock);
 return ret;
}
