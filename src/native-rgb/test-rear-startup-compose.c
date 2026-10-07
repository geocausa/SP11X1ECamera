/* SPDX-License-Identifier: GPL-2.0-only */
/* Full real provider/allocator/materializer integration. Inputs synthetic. */
#include "rear-startup-host-fixture.h"
static unsigned tests;
#define CHECK(x) do {tests++;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);abort();}}while(0)
static void putn(u64 value,u8 *p,unsigned n){for(unsigned i=0;i<n;i++)p[i]=(u8)(value>>(8*i));}
static void initialize(struct native_rear_startup_input *input){
 const u64 ids[4]={4,5,6,6};unsigned p,f,j;
 memset(input,0,sizeof(*input));
 input->geometry.sensor_width=4076;input->geometry.sensor_height=2806;
 input->geometry.isp_width=4064;input->geometry.isp_height=2286;
 input->geometry.output_width=3840;input->geometry.output_height=2160;
 input->geometry.bit_width=10;
 putn(NATIVE_REAR_SCALARS_MAGIC,input->scalars.data,4);
 putn(1,input->scalars.data+4,2);putn(208,input->scalars.data+6,2);
 putn(4,input->scalars.data+8,4);
 for(p=0;p<4;p++){
  struct native_rear_packet_stats_input *s=&input->statistics.packet[p];
  struct native_rear_bg_input *bg[3]={&s->aec,&s->tintless,&s->awb};
  struct native_rear_packet_iq_input *iq=&input->iq.packet[p];
  struct native_rear_packet_adaptive_input *a=&input->adaptive[p];
  u8 *scalar=input->scalars.data+16+p*48;
  input->request_id[p]=input->geometry.request_id[p]=s->request_id=iq->request_id=a->request_id=ids[p];
  putn(ids[p],scalar,8);putn(p,scalar+8,4);
  for(j=0;j<4;j++){putn(1024+p,scalar+16+2*j,2);putn(4096+p,scalar+24+4*j,4);}
  putn(1024+p,scalar+40,2);putn(1024+p,scalar+42,2);
  s->phase=iq->phase=a->phase=p;
  s->active_width=iq->active_width=4064;s->active_height=iq->active_height=2286;
  CHECK(native_rear_stats_geometry_preset(s,p?NATIVE_REAR_STATS_NORMAL:NATIVE_REAR_STATS_COLD)==0);
  for(f=0;f<3;f++){
   bg[f]->threshold_r=bg[f]->threshold_b=bg[f]->threshold_gr=bg[f]->threshold_gb=0x3ffff;
   bg[f]->y_weight_q4[0]=4;bg[f]->y_weight_q4[1]=8;bg[f]->y_weight_q4[2]=4;
   bg[f]->enabled=bg[f]->controls_valid=true;
  }
  iq->controls_valid=true;
  if(p)iq->af=(struct native_rear_af_rect){1524,858,1016,571};
  iq->cst.enabled=true;iq->cst.c01=iq->cst.c11=iq->cst.c21=4095;
  iq->cst.m00=iq->cst.m11=iq->cst.m22=1024;
  iq->bpcabf.signed10[0]=-100-p;iq->bpcabf.signed10[1]=100+p;
  a->valid=true;memset(a->lsc1,10+p,sizeof(a->lsc1));
  memset(a->lsc2,20+p,sizeof(a->lsc2));memset(a->gtm,30+p,sizeof(a->gtm));
 }
}
static void check_self_pointers(struct e008o_rear_semantic_set *set){
 for(unsigned p=0;p<4;p++){
  struct e007v_rear_dmi_state *v=&set->packet[p].dmi;
  struct e007u_rear_dmi_state *u=&v->dmi;
  struct e007t_rear_dmi_state *t=&u->dmi;
  struct e007s_rear_dmi_state *s=&t->dmi;
  struct e007q_rear_dmi_state *q=&s->dmi;
  struct e007i_rear_dmi_state *i=&q->dmi;
  CHECK(u->stable_ctx==v && t->stable_ctx==u && s->stable_ctx==t);
  CHECK(q->stable_ctx==s && i->gtm_ctx==&q->gtm && i->stable_ctx==q);
  CHECK(i->dmi.lsc_ctx==&i->lsc && i->dmi.gtm_ctx==i && i->dmi.stable_ctx==i);
 }
}
static bool zero(const void *ptr,size_t n){const u8 *p=ptr;for(size_t i=0;i<n;i++)if(p[i])return false;return true;}
static void positive(struct vfe_device *v){
 struct native_rear_startup_input *input=calloc(1,sizeof(*input));
 struct e008o_rear_semantic_set *set=calloc(1,sizeof(*set));
 struct e008l_rear_command_set commands={0};
 CHECK(input&&set);initialize(input);
 CHECK(native_rear_compose_startup(set,input)==0);
 CHECK(full_allocations==0);check_self_pointers(set);
 /* Heap candidate has been freed; all provider pointers must still work. */
 CHECK(e008o_rear_validate_semantic_set(set)==0);
 CHECK(e008l_rear_command_alloc(v,&commands)==0);
 CHECK(e008o_rear_materialize_commands(set,&commands)==0);
 CHECK(commands.prepared && !commands.hardware_exposed);
 CHECK(native_rear_validate_prepared_commands(&commands)==0);
 for(unsigned p=0;p<4;p++){
  struct e007e_bf_dmi_state *bf=e008t_rear_bf_dmi(&set->packet[p].dmi);
  CHECK(bf->gamma_inactive==!p && bf->gamma_valid==!!p);
  CHECK(commands.packet_request_id[p]==input->request_id[p]);
  CHECK(commands.packet[p].out.bl_count==(p?6:4));
  CHECK(zero(commands.packet[p].dynamic,sizeof(*commands.packet[p].dynamic)));
 }
 /* Revalidation does not rewrite already generated command bytes. */
 for(unsigned p=0;p<4;p++){
  u8 *snapshot=malloc(commands.packet[p].slab_bytes);CHECK(snapshot);
  memcpy(snapshot,commands.packet[p].slab_cpu,commands.packet[p].slab_bytes);
  for(unsigned j=0;j<25;j++)CHECK(native_rear_validate_prepared_commands(&commands)==0);
  CHECK(!memcmp(snapshot,commands.packet[p].slab_cpu,commands.packet[p].slab_bytes));free(snapshot);
 }
 CHECK(native_rear_compose_startup(set,input)==-EBUSY);
 CHECK(e008o_rear_materialize_commands(set,&commands)==-EINVAL);
 CHECK(e008o_rear_runtime_authorization()==-EOPNOTSUPP);
 CHECK(e008l_rear_runtime_authorization()==-EOPNOTSUPP);
 CHECK(e011as_rear_gamma_runtime_authorization()==-EOPNOTSUPP);
 CHECK(e008l_rear_command_release(v,&commands,false)==0);
 CHECK(full_allocations==0);free(set);free(input);
}
static void atomic_failure(void){
 struct native_rear_startup_input *input=calloc(1,sizeof(*input));
 struct e008o_rear_semantic_set *set=calloc(1,sizeof(*set)),*before=calloc(1,sizeof(*before));
 CHECK(input&&set&&before);
 for(unsigned p=0;p<4;p++)for(unsigned kind=0;kind<12;kind++){
  initialize(input);memset(set,0,sizeof(*set));
  set->packet[0].request_id=12345;memcpy(before,set,sizeof(*set));
  switch(kind){
   case 0:input->request_id[p]=3;break;
   case 1:input->geometry.request_id[p]++;break;
   case 2:input->adaptive[p].request_id++;break;
   case 3:input->adaptive[p].phase^=1;break;
   case 4:input->adaptive[p].valid=false;break;
   case 5:putn(3,input->scalars.data+16+p*48,8);break;
   case 6:input->statistics.packet[p].awb.threshold_b=0x40000;break;
   case 7:input->statistics.packet[p].request_id++;break;
   case 8:input->iq.packet[p].cst.m22=4096;break;
   case 9:input->iq.packet[p].controls_valid=false;break;
   case 10:input->iq.packet[p].request_id++;break;
   case 11:input->iq.packet[p].af.width=4064;break;
  }
  CHECK(native_rear_compose_startup(set,input)<0);
  CHECK(!memcmp(before,set,sizeof(*set)));CHECK(full_allocations==0);
 }
 for(int nth=0;nth<3;nth++){
  initialize(input);memset(set,0,sizeof(*set));memcpy(before,set,sizeof(*set));
  full_fail_after=nth;CHECK(native_rear_compose_startup(set,input)==-ENOMEM);full_fail_after=-1;
  CHECK(!memcmp(before,set,sizeof(*set)));CHECK(full_allocations==0);
 }
 initialize(input);memset(set,0,sizeof(*set));set->packet[3].ready=true;memcpy(before,set,sizeof(*set));
 CHECK(native_rear_compose_startup(set,input)==-EBUSY);CHECK(!memcmp(before,set,sizeof(*set)));
 free(before);free(set);free(input);
}
static void materializer_failure(struct vfe_device *v){
 struct native_rear_startup_input *input=calloc(1,sizeof(*input));
 struct e008o_rear_semantic_set *set=calloc(1,sizeof(*set));
 struct e008l_rear_command_set commands={0};
 CHECK(input&&set);initialize(input);CHECK(native_rear_compose_startup(set,input)==0);
 CHECK(e008l_rear_command_alloc(v,&commands)==0);
 set->packet[3].regs.bfstats.signed6[0]=33; /* BF is emitted in phase3; CST is not. */
 CHECK(e008o_rear_materialize_commands(set,&commands)==-ERANGE);
 CHECK(!commands.prepared && !commands.hardware_exposed);
 for(unsigned p=0;p<4;p++){
  CHECK(!commands.packet_request_id[p]);
  CHECK(!commands.packet[p].out.bl_count);
  CHECK(zero(commands.packet[p].out.main,commands.packet[p].out.main_bytes));
  CHECK(zero(commands.packet[p].out.wrapper,commands.packet[p].out.wrapper_bytes));
  for(unsigned j=0;j<commands.packet[p].out.dmi_count;j++)
   CHECK(zero(commands.packet[p].out.dmi[j].cpu,commands.packet[p].out.dmi[j].bytes));
 }
 CHECK(e008l_rear_command_release(v,&commands,false)==0);CHECK(full_allocations==0);
 free(set);free(input);
}
int main(void){
 struct device d={1};struct camss c={&d};struct vfe_device v={&c};
 positive(&v);atomic_failure();materializer_failure(&v);
 printf("NATIVE_REAR_COMPLETE_STARTUP_PASS assertions=%u real_semantic_materializer=1 hardware_access=0\n",tests);
 return 0;
}
