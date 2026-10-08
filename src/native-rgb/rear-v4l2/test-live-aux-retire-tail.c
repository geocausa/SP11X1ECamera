static void aux_fixture(void){
 fixture();
 CHECK(native_rear_live_retire_full(&camss.vfe[1],&camss.csid[1],&pair,&result,15)==0);
 read_count=sync_count=0;
}
static void aux_negative(void){
 struct camss before_camss=camss;
 struct e008h_rear_prime_pair before_pair=pair;
 struct e008k_rear_result before_result=result;
 CHECK(native_rear_live_retire_aux(&camss.vfe[1],&camss.csid[1],&pair,&result,15)<0);
 CHECK(aux_frees==0&&unmaps==1&&detaches==1&&put_calls==1);
 CHECK(!memcmp(&before_pair,&pair,sizeof(pair)));
 CHECK(!memcmp(&before_result,&result,sizeof(result)));
 if(race_at<0)CHECK(!memcmp(&before_camss,&camss,sizeof(camss)));
 negative_cases++;
}
static void aux_matrix(void){
 aux_fixture();
 struct e008d_rear_dma_set next=pair.dma[1];
 struct e007z_rear_frame old_frame=pair.frame[0],next_frame=pair.frame[1];
 CHECK(native_rear_live_retire_aux(&camss.vfe[1],&camss.csid[1],&pair,&result,15)==0);
 CHECK(aux_frees==8&&unmaps==1&&detaches==1&&put_calls==1);
 CHECK(result.live_aux_retired&&pair.dma[0].auxiliary_live_retired);
 CHECK(native_rear_live_aux_retired_valid(&pair.dma[0],&pair.frame[0],41));
 CHECK(!memcmp(&next,&pair.dma[1],sizeof(next)));
 CHECK(!memcmp(&old_frame,&pair.frame[0],sizeof(old_frame)));
 CHECK(!memcmp(&next_frame,&pair.frame[1],sizeof(next_frame)));
 CHECK(!result.csid_quiesced&&!result.bus_stopped&&!result.rtcdm_stopped&&!result.source_stopped);
 CHECK(native_rear_live_retire_aux(&camss.vfe[1],&camss.csid[1],&pair,&result,15)==-EALREADY);
 CHECK(aux_frees==8);
 struct e008d_rear_dma_set old=pair.dma[0];
 e008d_rear_release_partial(&camss.vfe[1],&pair.dma[0]);
 CHECK(!memcmp(&old,&pair.dma[0],sizeof(old))&&aux_frees==8);
 pair.dma[0].retired_aux_stop_proven=true;
 e008d_rear_release_partial(&camss.vfe[1],&pair.dma[0]);
 CHECK(!pair.dma[0].allocated&&aux_frees==8);

 for(unsigned s=0;s<2;s++)for(unsigned i=0;i<8;i++)for(unsigned kind=0;kind<6;kind++){
  aux_fixture();struct e008d_rear_aux_buffer *a=&pair.dma[s].aux[i];
  if(kind==0)a->cpu=NULL;else if(kind==1)a->wm=99;else if(kind==2)a->size--;
  else if(kind==3)a->dma++;else if(kind==4)a->dma+=(u64)1<<32;
  else pair.frame[s].slot[e007z_rear_index(a->wm)].owned_bytes--;
  aux_negative();
 }
 for(unsigned first=0;first<16;first++)for(unsigned second=0;second<first;second++){
  aux_fixture();pair.dma[first/8].aux[first%8].cpu=pair.dma[second/8].aux[second%8].cpu;
  aux_negative();
 }
 for(unsigned kind=0;kind<36;kind++){
  aux_fixture();struct e008d_rear_dma_set *old=&pair.dma[0],*next=&pair.dma[1];
  switch(kind){
   case 0:result.both_frames_complete=false;break;case 1:result.live_full_retired=false;break;
   case 2:old->public_full_retired=false;break;case 3:old->retired_aux_stop_proven=true;break;
   case 4:old->retired_owner_epoch++;break;case 5:old->retired_request_generation++;break;
   case 6:old->full.in_flight=true;break;case 7:old->full.dma++;break;
   case 8:old->public_full.dbuf=(void*)1;break;case 9:result.live_aux_retired=true;break;
   case 10:old->auxiliary_live_retired=true;break;case 11:next->auxiliary_live_retired=true;break;
   case 12:next->public_full_retired=true;break;case 13:next->retired_aux_stop_proven=true;break;
   case 14:next->retired_owner_epoch=41;break;case 15:next->retired_request_generation=2;break;
   case 16:next->full.in_flight=false;break;case 17:next->full.dma++;break;
   case 18:next->public_full.exposed=false;break;case 19:next->public_full.stop_proven=true;break;
   case 20:next->public_full.span.uv_iova++;break;
   case 21:pair.frame[1].slot[0].owned_bytes--;break;
   case 22:pair.frame[1].slot[1].owned_bytes--;break;
   case 23:result.owner_epoch++;break;case 24:pair.frame[0].pending=1;break;
   case 25:pair.frame[1].pending=1;break;case 26:camss.e005y_vfe1_owner.active_epoch++;break;
   case 27:camss.csid[1].overflow=1;break;case 28:camss.csid[1].latch_errors=1;break;
   case 29:camss.csid[1].produced++;break;case 30:result.csid_quiesced=true;break;
   case 31:result.bus_stopped=true;break;case 32:result.rtcdm_stopped=true;break;
   case 33:result.source_stopped=true;break;case 34:pair.dma[0].allocated=false;break;
   case 35:pair.dma[1].allocated=false;break;
  }
  aux_negative();
 }
 for(unsigned kind=1;kind<=7;kind++)for(unsigned at=0;at<30;at++){
  aux_fixture();race_kind=kind;race_at=at;aux_negative();
 }
 aux_fixture();
 CHECK(native_rear_live_retire_aux(&camss.vfe[1],&camss.csid[1],&pair,&result,15)==0);
 for(unsigned i=0;i<8;i++)for(unsigned kind=0;kind<4;kind++){
  struct e008d_rear_aux_buffer *a=&pair.dma[0].aux[i];
  if(kind==0)a->cpu=(void*)1;else if(kind==1)a->dma=1;else if(kind==2)a->size=1;else a->wm=1;
  CHECK(!native_rear_live_aux_retired_valid(&pair.dma[0],&pair.frame[0],41));negative_cases++;
  memset(a,0,sizeof(*a));
 }
 aux_fixture();native_rear_live_retire_aux_observe(&camss.vfe[1],&camss.csid[1],&pair,&result,15);
 CHECK(strstr(scalar_log,"released=8")&&strstr(scalar_log,"stop_flags=0")&&strstr(scalar_log,"next_aux_pinned=8"));
 CHECK(aux_frees==8);
}
