/* SPDX-License-Identifier: GPL-2.0-only */
/* Included after original completed/replacement proof, before any AUX zero/free.
 * Exclusive worker only. No ISR pixel/statistic processing or new DMA right.
 */
static int native_rear_statistics_before_aux_release(struct vfe_device *vfe,
 const struct e008h_rear_prime_pair *pair,const struct e008k_rear_result *result,
 u32 cursor)
{
 struct camss_video *video=&vfe->line[VFE_LINE_PIX].video_out;
 const struct e008d_rear_dma_set *set=&pair->dma[0];
 const struct e007z_rear_frame *frame=&pair->frame[0];
 const void *planes[6];
 size_t lengths[6];
 unsigned int i,j;
 u64 timestamp;
 int ret;
 if(!video->native_rear_inflight[0]||!result->both_frames_complete||
    !result->live_full_retired||result->live_aux_retired||
    set->auxiliary_live_retired||!set->allocated||!frame->active||frame->pending||
    frame->faulted||frame->owner_epoch!=result->owner_epoch||
    frame->request_generation!=(u64)video->native_rear_completed+1||
    video->native_rear_statistics_tick)
  return -EPROTO;
 for(i=0;i<6;i++){
  const struct e008d_rear_aux_buffer *aux=NULL;
  int index=e007z_rear_index(native_rear_stats_wm(i));
  for(j=0;j<E008D_REAR_AUX_COUNT;j++)
   if(set->aux[j].wm==native_rear_stats_wm(i)){
    if(aux)return -EPROTO;
    aux=&set->aux[j];
   }
  if(index<0||!aux||!aux->cpu||aux->size!=native_rear_stats_capacity[i]||
     aux->dma!=frame->slot[index].owned_base_iova||
     aux->size!=frame->slot[index].owned_bytes)
   return -EPROTO;
  planes[i]=aux->cpu;
  lengths[i]=aux->size;
 }
 /* Completion/consumed-address proof precedes coherent CPU reads. */
 dma_rmb();
 timestamp=ktime_get_ns();
 ret=camss_x1e_rear_meta_publish(video,result->owner_epoch,
      frame->request_generation,cursor,timestamp,planes,lengths);
 if(ret)return ret;
 video->native_rear_statistics_tick=timestamp;
 return 0;
}
