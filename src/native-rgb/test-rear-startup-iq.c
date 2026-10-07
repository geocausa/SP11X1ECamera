/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdio.h>
#include "rear-iq-host-fixture.h"
#include "../../experiments/E004-front-ir-vd55g0/e008x-rear-af-bf-roi-map/af-bf-roi-map.h"
static unsigned tests;
#define CHECK(x) do{tests++;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);abort();}}while(0)
static u32 le32(const u8 *b){return (u32)b[0]|((u32)b[1]<<8)|((u32)b[2]<<16)|((u32)b[3]<<24);}
static void positive(void){
 struct e008o_rear_packet_semantics base[4],before[4];
 struct native_rear_startup_iq_input input;
 unsigned p,j;u32 word;u8 roi[300],gamma[128];
 CHECK(native_rear_iq_test_initialize(base,&input)==0);
 memcpy(before,base,sizeof(base));
 CHECK(native_rear_bind_startup_iq(base,&input)==0);
 for(p=0;p<4;p++){
  struct e007e_bf_dmi_state *d=e008t_rear_bf_dmi(&base[p].dmi);
  CHECK(base[p].request_id==before[p].request_id && !base[p].ready);
  CHECK(!memcmp(&base[p].regs.scalar,&before[p].regs.scalar,sizeof(base[p].regs.scalar)));
  CHECK(!memcmp(&base[p].regs.mnds,&before[p].regs.mnds,sizeof(base[p].regs.mnds)));
  CHECK(!memcmp(base[p].regs.unrelated,before[p].regs.unrelated,64));
  CHECK(!memcmp(base[p].dmi.dmi.dmi.dmi.dmi.dmi.dmi.unrelated,
                before[p].dmi.dmi.dmi.dmi.dmi.dmi.dmi.unrelated,64));
  CHECK(!memcmp(&base[p].regs.cst,&input.packet[p].cst,sizeof(base[p].regs.cst)));
  CHECK(!memcmp(&base[p].regs.bpcabf,&input.packet[p].bpcabf,sizeof(base[p].regs.bpcabf)));
  CHECK(e007e_bfstats25_dmi(d,1,roi,sizeof(roi))==0);
  for(j=0;j<25;j++){
   CHECK(d->roi[j].rid==j && d->roi[j].oid==j);
   CHECK(!d->roi[j].merge && !d->roi[j].type);
   CHECK(!!(le32(roi+j*12+8)&256)==(j==24));
  }
  CHECK(e007e_bfstats25_dmi(d,2,gamma,sizeof(gamma))==(p?0:-EOPNOTSUPP));
  CHECK(e007b_bfstats25_lookup(&base[p].regs.bfstats,0xbc58,&word)==0 && word==(p&1));
  CHECK(e007b_bfstats25_lookup(&base[p].regs.bfstats,0xbc60,&word)==0 && !!(word&512)==!!p);
  CHECK(e006r_cst12_word(&base[p].regs.cst,1,&word)==0 && word==1024);
  CHECK(e007a_bpcabf411_lookup(&base[p].regs.bpcabf,0x49b8,&word)==0);
  CHECK((word&1023)==((u32)(u16)input.packet[p].bpcabf.signed10[0]&1023));
 }
 memcpy(before,base,sizeof(base));
 CHECK(native_rear_bind_startup_iq(base,&input)==0);
 CHECK(!memcmp(before,base,sizeof(base)));
 CHECK(iq_allocations==0 && !iq_freed_uncleared);
}
static void failures(void){
 struct e008o_rear_packet_semantics base[4],before[4];
 struct native_rear_startup_iq_input input;
 unsigned p,k;
 for(p=0;p<4;p++)for(k=0;k<17;k++){
  CHECK(native_rear_iq_test_initialize(base,&input)==0);
  switch(k){
   case 0:input.packet[p].request_id++;break;
   case 1:input.packet[p].phase^=1;break;
   case 2:input.packet[p].controls_valid=false;break;
   case 3:input.packet[p].active_width--;break;
   case 4:input.packet[p].active_height--;break;
   case 5:base[p].ready=true;break;
   case 6:base[p].regs.scalar.request_id++;break;
   case 7:input.packet[p].cst.m22=4096;break;
   case 8:input.packet[p].cst.c21=4096;break;
   case 9:input.packet[p].bpcabf.signed10[1]=-513;break;
   case 10:input.packet[p].bpcabf.unsigned9[1]=512;break;
   case 11:input.packet[p].bpcabf.nibble_group[1][3]=16;break;
   case 12:input.packet[p].af.x=0;input.packet[p].af.width=p?1016:1;break;
   case 13:input.packet[p].af.y=0;input.packet[p].af.height=p?571:1;break;
   case 14:input.packet[p].af.width=4064;break;
   case 15:input.packet[p].af.height=2286;break;
   case 16:base[p].regs.mnds.input_width--;break;
  }
  memcpy(before,base,sizeof(base));
  CHECK(native_rear_bind_startup_iq(base,&input)<0);
  CHECK(!memcmp(base,before,sizeof(base)));
  CHECK(iq_allocations==0 && !iq_freed_uncleared);
 }
 CHECK(native_rear_iq_test_initialize(base,&input)==0);memcpy(before,base,sizeof(base));
 iq_fail_allocation=true;
 CHECK(native_rear_bind_startup_iq(base,&input)==-ENOMEM);
 CHECK(!memcmp(base,before,sizeof(base)));iq_fail_allocation=false;
 CHECK(native_rear_bind_startup_iq(NULL,&input)==-EINVAL);
 CHECK(native_rear_bind_startup_iq(base,NULL)==-EINVAL);
}
static void reference_geometry(void){
 struct e007e_bf_dmi_state d,before;
 struct native_rear_af_rect af;struct e008x_roi ref[25];
 unsigned w,h,j;
 for(w=1;w<=8192;w++)CHECK((u32)((float)w*(1.0f/5.0f))==w/5);
 for(h=1;h<=16384;h++)CHECK((u32)((float)h*(1.0f/5.0f))==h/5);
 /* Exercise parity of offsets, dimensions, minimum and boundary rejection. */
 for(w=30;w<=1200;w+=13)for(h=40;h<=800;h+=19){
  memset(&d,0,sizeof(d));d.roi_count=25;d.gamma_valid=true;
  af=(struct native_rear_af_rect){1525,701,w,h};
  CHECK(native_rear_finalize_bf_roi(&d,&af,4064,2286)==0);
  CHECK(e008x_normal_roi_map((struct e008x_rect){af.x&~1U,af.y&~1U,af.width&~1U,(af.height&~1U)+16},ref)==0);
  for(j=0;j<25;j++)CHECK(d.roi[j].left==ref[j].left && d.roi[j].top==ref[j].top &&
                         d.roi[j].width==ref[j].width && d.roi[j].height==ref[j].height);
 }
 before=d;af.x=75;
 CHECK(native_rear_finalize_bf_roi(&d,&af,4064,2286)<0);
 CHECK(!memcmp(&before,&d,sizeof(d)));
}
int main(void){positive();failures();reference_geometry();
 printf("NATIVE_REAR_IQ_PASS assertions=%u hardware_callbacks=0\n",tests);return 0;}
