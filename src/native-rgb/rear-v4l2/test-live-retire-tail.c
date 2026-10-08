
static void live_positive(void){
 fixture();
 struct e008d_rear_dma_set next=pair.dma[1];
 struct e007z_rear_frame old_frame=pair.frame[0], next_frame=pair.frame[1];
 struct e008d_rear_aux_buffer old_aux[8];memcpy(old_aux,pair.dma[0].aux,sizeof(old_aux));
 CHECK(native_rear_live_retire_full(&camss.vfe[1],&camss.csid[1],&pair,&result,15)==0);
 CHECK(unmaps==1&&detaches==1&&put_calls==1&&result.live_full_retired);
 CHECK(native_rear_live_full_retired_valid(&pair.dma[0],&pair.frame[0],41));
 CHECK(!memcmp(&next,&pair.dma[1],sizeof(next)));
 CHECK(!memcmp(&old_frame,&pair.frame[0],sizeof(old_frame)));
 CHECK(!memcmp(&next_frame,&pair.frame[1],sizeof(next_frame)));
 CHECK(!memcmp(old_aux,pair.dma[0].aux,sizeof(old_aux)));
 CHECK(!result.csid_quiesced&&!result.bus_stopped&&!result.rtcdm_stopped&&!result.source_stopped);
 CHECK(!e007z_rear_retireable(&pair.frame[0],41,1,false,false));
 CHECK(native_rear_live_retire_full(&camss.vfe[1],&camss.csid[1],&pair,&result,15)==-EALREADY);
 CHECK(unmaps==1&&detaches==1&&put_calls==1);
 struct e008d_rear_dma_set old=pair.dma[0];
 e008d_rear_release_partial(&camss.vfe[1],&pair.dma[0]);
 CHECK(!memcmp(&old,&pair.dma[0],sizeof(old))&&aux_frees==0);
 pair.dma[0].retired_aux_stop_proven=true;
 e008d_rear_release_partial(&camss.vfe[1],&pair.dma[0]);
 CHECK(aux_frees==8&&unmaps==1&&detaches==1&&put_calls==1);
 CHECK(!pair.dma[0].allocated);
}
static void extra_matrix(void){
 for(unsigned s=0;s<2;s++)for(unsigned kind=0;kind<23;kind++){
  fixture();struct e008d_rear_dma_set *d=&pair.dma[s];
  struct native_rear_video_lease *l=&d->public_full;
  switch(kind){
   case 0:d->allocated=false;break;case 1:d->full.in_flight=false;break;
   case 2:d->full.cpu=&camss;break;case 3:d->full.size--;break;case 4:d->full.dma++;break;
   case 5:l->acquired=false;break;case 6:l->exposed=false;break;case 7:l->stop_proven=true;break;
   case 8:l->dbuf=NULL;break;case 9:l->attachment=NULL;break;case 10:l->table=NULL;break;
   case 11:l->span.y_iova++;break;case 12:l->span.uv_iova++;break;
   case 13:l->span.mapped_bytes=NATIVE_REAR_NV12_BYTES-1;break;
   case 14:d->public_full_retired=true;break;case 15:d->retired_aux_stop_proven=true;break;
   case 16:d->retired_owner_epoch=41;break;case 17:d->retired_request_generation=s+1;break;
   case 18:pair.frame[s].slot[0].owned_bytes--;break;case 19:pair.frame[s].slot[1].owned_bytes--;break;
   case 20:pair.frame[s].slot[0].owned_base_iova++;break;case 21:pair.frame[s].slot[1].owned_base_iova++;break;
   case 22:result.both_frames_complete=false;break;
  }
  negative();
 }
 for(unsigned s=0;s<2;s++)for(unsigned i=0;i<8;i++)for(unsigned kind=0;kind<3;kind++){
  fixture();struct e008d_rear_aux_buffer *a=&pair.dma[s].aux[i];
  if(kind==0)a->cpu=NULL;else if(kind==1)a->wm=99;else a->size--;
  negative();
 }
 for(unsigned kind=0;kind<3;kind++){
  fixture();
  if(kind==0)pair.dma[0].public_full.dbuf=pair.dma[1].public_full.dbuf;
  if(kind==1)pair.dma[0].public_full.attachment=pair.dma[1].public_full.attachment;
  if(kind==2)pair.dma[0].public_full.table=pair.dma[1].public_full.table;
  negative();
 }
 for(unsigned kind=0;kind<13;kind++){
  fixture();CHECK(native_rear_live_retire_full(&camss.vfe[1],&camss.csid[1],&pair,&result,15)==0);
  struct e008d_rear_dma_set *d=&pair.dma[0];
  switch(kind){
   case 0:d->public_full_retired=false;break;case 1:d->retired_aux_stop_proven=true;break;
   case 2:d->retired_owner_epoch++;break;case 3:d->retired_request_generation++;break;
   case 4:d->full.cpu=&camss;break;case 5:d->full.in_flight=true;break;
   case 6:d->full.size--;break;case 7:d->full.dma++;break;
   case 8:d->public_full.dbuf=(void*)1;break;case 9:d->public_full.attachment=(void*)1;break;
   case 10:d->public_full.table=(void*)1;break;case 11:d->public_full.span.y_iova=1;break;
   case 12:d->public_full.exposed=true;break;
  }
  CHECK(!native_rear_live_full_retired_valid(d,&pair.frame[0],41));negative_cases++;
 }
 fixture();native_rear_live_retire_full_observe(&camss.vfe[1],&camss.csid[1],&pair,&result,15);
 CHECK(strstr(scalar_log,"released=1")&&strstr(scalar_log,"stop_flags=0")&&strstr(scalar_log,"aux_pinned=8"));
 CHECK(unmaps==1&&detaches==1&&put_calls==1);
}
