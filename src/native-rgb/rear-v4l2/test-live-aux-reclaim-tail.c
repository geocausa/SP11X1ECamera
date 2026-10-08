static void make_aux_retired(void){
 make_retired();result.live_aux_retired=true;pair.dma[0].auxiliary_live_retired=true;
 memset(pair.dma[0].aux,0,sizeof(pair.dma[0].aux));
}
/* MATRIX */
 init();make_aux_retired();
 CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)==0);CHECK(releases==2);
 for(unsigned kind=0;kind<4;kind++){
  init();make_aux_retired();
  if(kind==0)result.live_aux_retired=false;
  else if(kind==1)pair.dma[0].auxiliary_live_retired=false;
  else if(kind==2)pair.dma[1].auxiliary_live_retired=true;
  else result.live_full_retired=false;
  struct e008h_rear_prime_pair before=pair;
  CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);
  CHECK(releases==0&&!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
 }
 for(unsigned i=0;i<8;i++)for(unsigned kind=0;kind<4;kind++){
  init();make_aux_retired();struct aux *a=&pair.dma[0].aux[i];
  if(kind==0)a->cpu=&cam;else if(kind==1)a->dma=1;else if(kind==2)a->size=1;else a->wm=1;
  struct e008h_rear_prime_pair before=pair;
  CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);
  CHECK(releases==0&&!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
 }
 for(unsigned mask=0;mask<15;mask++){
  init();make_aux_retired();
  result.csid_quiesced=mask&1;result.bus_stopped=mask&2;result.rtcdm_stopped=mask&4;result.source_stopped=mask&8;
  struct e008h_rear_prime_pair before=pair;
  CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);
  CHECK(releases==0&&!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
 }
