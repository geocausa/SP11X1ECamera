/* SPDX-License-Identifier: GPL-2.0-only */
/* MMIO/current receipt APIs and output contracts are explicit models.
 * Command allocator, layout, receipt binding, live free and cleanup are actual.
 */
struct vfe680_e004nu_rear_wm_static {u8 wm;u32 frame_incr;};
static struct vfe680_e004nu_rear_wm_static contracts[10];
static const u8 output_wms[10]={0,1,2,3,11,12,13,14,16,18};
static int e007z_rear_index(u8 wm){
 for(unsigned i=0;i<10;i++)if(output_wms[i]==wm)return (int)i;
 return -ENOENT;
}
static const struct vfe680_e004nu_rear_wm_static *e008d_rear_contract_for_wm(u8 wm){
 int i=e007z_rear_index(wm);return i<0?NULL:&contracts[i];
}
static int observe_error,current_error;
static unsigned observe_calls,current_calls,retire_negatives,cpu_aliases,aux_aliases,dma_aliases;
static struct native_rear_bl_receipt model_last;
static int native_rear_live_replacement_read(struct vfe_device *v,struct csid_device *c,
 const struct e008h_rear_prime_pair *p,const struct e008k_rear_result *r,u32 cursor,
 struct native_rear_live_observation *o){
 CHECK(v&&c&&p&&r&&o&&cursor==9&&allocations==12);observe_calls++;
 if(r->csid_quiesced||r->bus_stopped||r->rtcdm_stopped||r->source_stopped)return -EPROTO;
 return observe_error;
}
static int e008k_rear_rtcdm_receipt_current(struct camss *c,const struct native_rear_bl_receipt *r){
 CHECK(c&&r&&allocations==12);current_calls++;
 CHECK(!memcmp(r,&model_last,sizeof(*r)));return current_error;
}
#include <stdarg.h>
static void dev_info(void *dev,const char *format,...){va_list args;(void)dev;va_start(args,format);vprintf(format,args);va_end(args);}
#include "native-rear-command-retire.inc"
static unsigned char aux_cpu[2][8][4096];
static void output_fixture(struct e008h_rear_prime_pair *pair,bool retired){
 memset(pair,0,sizeof(*pair));observe_error=current_error=0;observe_calls=current_calls=0;
 for(unsigned i=0;i<10;i++)contracts[i]=(struct vfe680_e004nu_rear_wm_static){output_wms[i],i<2?(i?4147200:8294400):4096};
 for(unsigned s=0;s<2;s++){
  struct e008d_rear_dma_set *d=&pair->dma[s];struct e007z_rear_frame *fr=&pair->frame[s];
  u32 base=0x20000000+s*0x04000000;
  fr->active=true;fr->owner_epoch=7;fr->request_generation=s+1;
  d->allocated=true;d->full.dma=base;d->full.size=NATIVE_REAR_NV12_BYTES;d->full.in_flight=true;
  d->public_full=(struct native_rear_video_lease){.dbuf=(void*)1,.attachment=(void*)2,.table=(void*)3,.span={base,base+NATIVE_REAR_NV12_UV_OFFSET,NATIVE_REAR_NV12_BYTES+2048},.acquired=true,.exposed=true};
  for(unsigned i=0;i<10;i++)fr->slot[i].owned_bytes=contracts[i].frame_incr;
  fr->slot[0].owned_base_iova=base;fr->slot[1].owned_base_iova=base+NATIVE_REAR_NV12_UV_OFFSET;
  for(unsigned i=0;i<8;i++){
   fr->slot[i+2].owned_base_iova=base+0x02000000+i*0x10000;
   d->aux[i]=(struct e008d_rear_aux_buffer){aux_cpu[s][i],fr->slot[i+2].owned_base_iova,4096,e008d_rear_aux_wms[i]};
  }
 }
 if(retired){
  struct e008d_rear_dma_set *d=&pair->dma[0];
  d->public_full_retired=d->auxiliary_live_retired=true;d->retired_owner_epoch=7;d->retired_request_generation=1;
  d->full.in_flight=false;memset(&d->public_full,0,sizeof(d->public_full));memset(d->aux,0,sizeof(d->aux));
 }
}
static void retire_reject(struct vfe_device *v,struct csid_device *c,struct e008h_rear_prime_pair *p,
 struct e008k_rear_request *q,struct e008k_rear_result *r){
 struct e008l_rear_command_set before=*q->commands;
 struct e008h_rear_prime_pair pair_before=*p;struct e008k_rear_result result_before=*r;
 unsigned live=allocations,calls=submit_calls;
 CHECK(native_rear_live_retire_commands(v,c,p,q,r,9)<0);
 CHECK(!memcmp(&before,q->commands,sizeof(before)));
 CHECK(!memcmp(&pair_before,p,sizeof(*p)));CHECK(!memcmp(&result_before,r,sizeof(*r)));
 CHECK(allocations==live&&submit_calls==calls);retire_negatives++;
}
static void **command_cpu_pointer(struct e008l_rear_command_set *s,unsigned index){
 struct e008l_rear_packet_dma *p=&s->packet[index/3];
 switch(index%3){case 0:return &p->slab_cpu;case 1:return (void**)&p->dmi;default:return (void**)&p->dynamic;}
}
static void command_retire_tests(struct vfe_device *v){
 struct csid_device c={0};struct e008l_rear_command_set s,good;
 struct e008k_rear_request q;struct e008k_rear_result r,rgood;
 struct e008h_rear_prime_pair pair,pgood;
 receipt_fixture(v,&s,&q,&r);receipt_complete(v,&q,&r);
 r.both_frames_complete=r.live_full_retired=r.live_aux_retired=true;rgood=r;good=s;
 model_last=s.packet[3].receipt[5];
 output_fixture(&pair,false);
 CHECK(native_rear_command_allocations_check(&q,&pair,7)==0);
 /* All 66 cross-type aliases rejected before any descriptor dereference. */
 for(unsigned i=0;i<12;i++)for(unsigned j=0;j<i;j++){
  s=good;*command_cpu_pointer(&s,i)=*command_cpu_pointer(&s,j);
  CHECK(native_rear_command_allocations_check(&q,&pair,7)==-EADDRINUSE);cpu_aliases++;
 }
 s=good;
 for(unsigned slot=0;slot<2;slot++)for(unsigned a=0;a<8;a++)for(unsigned i=0;i<12;i++){
  void *saved=pair.dma[slot].aux[a].cpu;pair.dma[slot].aux[a].cpu=*command_cpu_pointer(&s,i);
  CHECK(native_rear_command_allocations_check(&q,&pair,7)==-EADDRINUSE);
  pair.dma[slot].aux[a].cpu=saved;aux_aliases++;
 }
 for(unsigned p=0;p<4;p++)for(unsigned slot=0;slot<2;slot++)for(unsigned i=0;i<10;i++){
  s=good;s.packet[p].slab_dma=pair.frame[slot].slot[i].owned_base_iova;
  CHECK(native_rear_command_allocations_check(&q,&pair,7)==-EADDRINUSE);dma_aliases++;
 }
 /* Full mapping tail, outside the image ledger, still must not alias commands. */
 for(unsigned p=0;p<4;p++)for(unsigned slot=0;slot<2;slot++){
  s=good;s.packet[p].slab_dma=pair.dma[slot].full.dma+NATIVE_REAR_NV12_BYTES;
  CHECK(native_rear_command_allocations_check(&q,&pair,7)==-EADDRINUSE);dma_aliases++;
 }
 s=good;
 pair.dma[1].public_full.span.mapped_bytes+=1ULL<<32;
 CHECK(native_rear_command_allocations_check(&q,&pair,7)==-EPROTO);
 output_fixture(&pair,true);pgood=pair;
 CHECK(native_rear_command_allocations_check(&q,&pair,7)==0);
 for(unsigned i=0;i<12;i++)for(unsigned j=0;j<i;j++){
  s=good;*command_cpu_pointer(&s,i)=*command_cpu_pointer(&s,j);retire_reject(v,&c,&pair,&q,&r);
 }
 s=good;
 for(unsigned slot=0;slot<2;slot++)for(unsigned i=0;i<8;i++)for(unsigned f=0;f<4;f++){
  pair=pgood;
  switch(f){case 0:pair.dma[slot].aux[i].cpu=slot?NULL:(void*)1;break;case 1:pair.dma[slot].aux[i].dma++;break;case 2:pair.dma[slot].aux[i].size++;break;case 3:pair.dma[slot].aux[i].wm=255;break;}
  retire_reject(v,&c,&pair,&q,&r);
 }
 pair=pgood;
 for(unsigned f=0;f<18;f++){
  s=good;r=rgood;pair=pgood;observe_error=current_error=0;
  switch(f){
   case 0:r.owner_epoch++;break;case 1:r.both_frames_complete=false;break;
   case 2:r.live_full_retired=false;break;case 3:r.live_aux_retired=false;break;
   case 4:pair.dma[0].retired_owner_epoch++;break;case 5:pair.dma[0].retired_request_generation++;break;
   case 6:pair.frame[0].faulted=true;break;case 7:pair.frame[0].pending=true;break;
   case 8:s.receipt_faulted=true;break;case 9:s.retired_owner=1;break;
   case 10:s.retired_BL_count=1;break;case 11:s.retired_last.sequence=1;break;
   case 12:observe_error=-EAGAIN;break;case 13:current_error=-ESTALE;break;
   case 14:r.csid_quiesced=true;break;case 15:r.bus_stopped=true;break;
   case 16:r.rtcdm_stopped=true;break;case 17:r.source_stopped=true;break;
  }
  retire_reject(v,&c,&pair,&q,&r);
 }
 observe_error=current_error=0;
 for(unsigned p=0;p<4;p++)for(unsigned i=0;i<good.packet[p].receipt_count;i++)for(unsigned f=0;f<5;f++){
  s=good;r=rgood;pair=pgood;struct native_rear_bl_receipt *rr=&s.packet[p].receipt[i];
  switch(f){case 0:rr->sequence++;break;case 1:rr->dma++;break;case 2:rr->bytes--;break;case 3:rr->complete=false;break;case 4:rr->irq_status=1;break;}
  retire_reject(v,&c,&pair,&q,&r);
 }
 s=good;r=rgood;pair=pgood;observe_calls=current_calls=0;
 CHECK(allocations==12);
 native_rear_live_retire_commands_observe(v,&c,&pair,&q,&r,9);
 CHECK(r.live_commands_retired&&s.live_retired&&observe_calls==1&&current_calls==1);
 CHECK(allocations==0&&native_rear_live_commands_retired_valid(&s,7));
 CHECK(!memcmp(&pair,&pgood,sizeof(pair)));CHECK(submit_calls==22);
 CHECK(!r.csid_quiesced&&!r.bus_stopped&&!r.rtcdm_stopped&&!r.source_stopped);
 CHECK(e008l_rear_command_release(v,&s,false)==-EBUSY);
 good=s;
 CHECK(native_rear_live_retire_commands(v,&c,&pair,&q,&r,9)==-EALREADY);
 CHECK(e008l_rear_command_alloc(v,&s)==-EINVAL);
 CHECK(!memcmp(&good,&s,sizeof(s)));
 for(unsigned p=0;p<4;p++)for(unsigned i=0;i<sizeof(s.packet[p]);i++){
  s=good;((u8*)&s.packet[p])[i]=1;
  CHECK(!native_rear_live_commands_retired_valid(&s,7));
  CHECK(e008l_rear_command_release(v,&s,true)==-EPROTO);
  CHECK(allocations==0);retire_negatives++;
 }
 for(unsigned f=0;f<10;f++){
  s=good;
  switch(f){case 0:s.retired_owner=0;break;case 1:s.retired_BL_count--;break;
   case 2:s.retired_last.complete=false;break;case 3:s.retired_last.sequence++;break;
   case 4:s.retired_last.dma=0;break;case 5:s.retired_last.bytes=0;break;
   case 6:s.retired_last.irq_status=1;break;case 7:s.receipt_faulted=true;break;
   case 8:s.prepared=false;break;case 9:s.packet_request_id[0]=0;break;}
  CHECK(!native_rear_live_commands_retired_valid(&s,7));
  CHECK(e008l_rear_command_release(v,&s,true)==-EPROTO);retire_negatives++;
 }
 s=good;CHECK(e008l_rear_command_release(v,&s,true)==0);
 CHECK(all_zero(&s,sizeof(s))&&allocations==0);
 materializations=0;
 printf("COMMAND_RETIRE_PASS assertions=%u negatives=%u CPU_aliases=%u aux_aliases=%u DMA_aliases=%u\n",tests,retire_negatives,cpu_aliases,aux_aliases,dma_aliases);
}
