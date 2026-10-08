/* SPDX-License-Identifier: GPL-2.0-only */
/* Hardware return values are models; allocation/layout/consumer are actual. */
static unsigned negative_cases, submit_calls;
static int injected_at=-1, injected_kind;
static u32 fifo_sequence;
static int e008k_rear_rtcdm_submit_bl_receipt(struct camss *cam, u32 dma,
 u16 bytes, struct native_rear_bl_receipt *r){
 CHECK(cam&&r&&dma&&bytes);
 unsigned n=submit_calls++;
 *r=(struct native_rear_bl_receipt){.sequence=++fifo_sequence,.dma=dma,
  .bytes=bytes,.irq_status=NATIVE_REAR_COMMAND_BL_DONE,.complete=true};
 if((int)n==injected_at)switch(injected_kind){
  case 0:return -ETIMEDOUT;
  case 1:r->complete=false;break;
  case 2:r->sequence++;break;
  case 3:r->dma+=4;break;
  case 4:r->bytes--;break;
  case 5:r->irq_status=0;break;
  case 6:r->irq_status|=1;break;
  case 7:r->sequence=0;break;
 }
 return 0;
}
#include "native-rear-command-receipts.inc"
static void receipt_fixture(struct vfe_device *v,struct e008l_rear_command_set *s,
                            struct e008k_rear_request *q,struct e008k_rear_result *r){
 struct e008o_rear_semantic_set semantic;
 init_semantics(&semantic);memset(s,0,sizeof(*s));memset(q,0,sizeof(*q));memset(r,0,sizeof(*r));
 CHECK(e008l_rear_command_alloc(v,s)==0);
 CHECK(e008o_rear_materialize_commands(&semantic,s)==0);
 q->commands=s;r->owner_epoch=7;
 for(unsigned p=0;p<4;p++){
  q->packet_request_id[p]=s->packet_request_id[p];
  CHECK(e008l_rear_command_mark_submitted(s,p)==0);
 }
 fifo_sequence=0;submit_calls=0;injected_at=-1;
}
static void receipt_complete(struct vfe_device *v,struct e008k_rear_request *q,
                              struct e008k_rear_result *r){
 for(unsigned p=0;p<4;p++){
  CHECK(native_rear_submit_receipted_packet(v->camss,q,p,7)==0);
  r->packet_submitted[p]=true;
 }
}
static void receipt_reject(struct e008k_rear_request *q,struct e008k_rear_result *r){
 struct e008l_rear_command_set before=*q->commands;
 unsigned live=allocations,calls=submit_calls;u32 n=77;
 CHECK(native_rear_command_receipts_check(q,r,&n)<0);CHECK(n==0);
 CHECK(!memcmp(&before,q->commands,sizeof(before)));
 CHECK(allocations==live&&submit_calls==calls);negative_cases++;
}
static void receipt_tests(struct vfe_device *v){
 struct e008l_rear_command_set s,good;
 struct e008k_rear_request q;
 struct e008k_rear_result r;
 u32 n;
 receipt_fixture(v,&s,&q,&r);
 receipt_complete(v,&q,&r);
 CHECK(submit_calls==22&&fifo_sequence==22);
 CHECK(native_rear_command_receipts_check(&q,&r,&n)==0&&n==22);
 CHECK(e008l_rear_command_release(v,&s,false)==-EBUSY);
 good=s;
 for(unsigned p=0;p<4;p++){
  unsigned calls=submit_calls;
  CHECK(native_rear_submit_receipted_packet(v->camss,&q,p,7)==-EALREADY);
  CHECK(submit_calls==calls&&!memcmp(&s,&good,sizeof(s)));
  for(unsigned f=0;f<11;f++){
   s=good;
   struct e008l_rear_packet_dma *a=&s.packet[p];
   switch(f){
    case 0:a->receipt_owner++;break;case 1:a->receipt_request++;break;
    case 2:a->receipt_slab_cpu=(void*)(uintptr_t)4;break;
    case 3:a->receipt_slab_dma++;break;case 4:a->receipt_slab_bytes--;break;
    case 5:a->receipt_dmi=NULL;break;case 6:a->receipt_dynamic=NULL;break;
    case 7:a->receipt_count--;break;case 8:a->receipt_count=255;break;
    case 9:a->receipt_count++;break;case 10:q.packet_request_id[p]++;break;
   }
   receipt_reject(&q,&r);q.packet_request_id[p]=good.packet_request_id[p];
  }
  for(unsigned i=0;i<E007Y_MAX_BL;i++)for(unsigned f=0;f<5;f++){
   s=good;struct native_rear_bl_receipt *a=&s.packet[p].receipt[i];
   switch(f){
    case 0:a->sequence++;break;case 1:a->dma++;break;
    case 2:a->bytes++;break;case 3:a->irq_status++;break;case 4:a->complete=!a->complete;break;
   }
   receipt_reject(&q,&r);
  }
  s=good;r.packet_submitted[p]=false;receipt_reject(&q,&r);r.packet_submitted[p]=true;
 }
 s=good;s.receipt_faulted=true;receipt_reject(&q,&r);
 s=good;s.hardware_exposed=false;receipt_reject(&q,&r);
 s=good;r.owner_epoch++;receipt_reject(&q,&r);r.owner_epoch--;
 s=good;CHECK(e008l_rear_command_release(v,&s,true)==0);CHECK(allocations==0);
 for(unsigned fail=0;fail<22;fail++)for(unsigned kind=0;kind<8;kind++){
  receipt_fixture(v,&s,&q,&r);injected_at=fail;injected_kind=kind;
  int ret=0;
  for(unsigned p=0;p<4;p++){
   ret=native_rear_submit_receipted_packet(v->camss,&q,p,7);
   if(ret)break;
   r.packet_submitted[p]=true;
  }
  CHECK(ret<0&&s.receipt_faulted&&submit_calls==fail+1);
  receipt_reject(&q,&r);
  unsigned calls=submit_calls;
  CHECK(native_rear_submit_receipted_packet(v->camss,&q,0,7)==-EIO);
  CHECK(submit_calls==calls);CHECK(e008l_rear_command_release(v,&s,false)==-EBUSY);
  CHECK(e008l_rear_command_release(v,&s,true)==0);CHECK(allocations==0);
 }
 for(unsigned p=1;p<4;p++){
  receipt_fixture(v,&s,&q,&r);
  CHECK(native_rear_submit_receipted_packet(v->camss,&q,p,7)==-ESTALE);
  CHECK(submit_calls==0);negative_cases++;
  CHECK(e008l_rear_command_release(v,&s,true)==0);CHECK(allocations==0);
 }
 materializations=0;
 printf("COMMAND_RECEIPTS_PASS assertions=%u negatives=%u\n",tests,negative_cases);
}
