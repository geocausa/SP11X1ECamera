/* SPDX-License-Identifier: GPL-2.0-only */
/* Same-SP11 offline source inputs -> current full composer/materializer. */
#include "rear-startup-host-fixture.h"
static unsigned checks;
#define CHECK(x) do { checks++;if(!(x)){fprintf(stderr,"check %u failed at %d\n",checks,__LINE__);abort();}}while(0)
static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static u16 read16(void){u8 b[2];read_exact(b,2);return b[0]|((u16)b[1]<<8);}
static u32 read32(void){u8 b[4];read_exact(b,4);return get_unaligned_le32(b);}
static void write_private(const char *dir,const char *kind,unsigned p,unsigned i,const void *data,size_t n){
 char name[4096];CHECK(snprintf(name,sizeof(name),"%s/p%u-%s-%u.bin",dir,p,kind,i)>0);
 FILE *f=fopen(name,"wb");CHECK(f);CHECK(fwrite(data,1,n,f)==n);CHECK(fclose(f)==0);
}
static void read_bpc(struct e007a_bpcabf411_calc_state *s){
 for(unsigned i=0;i<2;i++)s->signed10[i]=(s16)read16();
 for(unsigned i=0;i<2;i++)s->unsigned9[i]=read16();
 read_exact(s->nibble4,2);read_exact(s->byte_group0,8);
 read_exact(s->byte_group1,8);read_exact(s->nibble_group,8);
}
int main(int argc,char **argv){
 const u64 ids[4]={4,5,6,6};struct device dev={1};struct camss camss={&dev};struct vfe_device vfe={&camss};
 struct native_rear_startup_input *in=calloc(1,sizeof(*in));
 struct e008o_rear_semantic_set *set=calloc(1,sizeof(*set));
 struct e008l_rear_command_set cmd={0};
 struct native_rear_af_rect af[3];
 u8 weights[2][4];u32 bg[4][14],rs[3][6];
 struct e007a_bpcabf411_calc_state bpc[3]={0};
 u8 lsc[2][2][884],gtm[2048];
 CHECK(argc==2&&in&&set);
 read_exact(in->scalars.data,sizeof(in->scalars));
 for(unsigned p=0;p<3;p++){af[p].x=read16();af[p].y=read16();af[p].width=read16();af[p].height=read16();}
 read_exact(weights,sizeof(weights));
 for(unsigned p=0;p<4;p++)for(unsigned j=0;j<14;j++)bg[p][j]=read32();
 for(unsigned p=0;p<3;p++)for(unsigned j=0;j<6;j++)rs[p][j]=read32();
 for(unsigned p=0;p<3;p++)read_bpc(&bpc[p]);
 read_exact(lsc[0][0],884);read_exact(lsc[1][0],884);
 read_exact(lsc[0][1],884);read_exact(lsc[1][1],884);read_exact(gtm,2048);
 CHECK(fgetc(stdin)==EOF);
 in->geometry=(struct native_rear_geometry_mode){
  .sensor_width=4076,.sensor_height=2806,.isp_width=4064,.isp_height=2286,
  .output_width=3840,.output_height=2160,.bit_width=10
 };
 for(unsigned p=0;p<4;p++){
  struct native_rear_packet_stats_input *s=&in->statistics.packet[p];
  struct native_rear_packet_iq_input *iq=&in->iq.packet[p];
  struct native_rear_packet_adaptive_input *a=&in->adaptive[p];
  struct native_rear_bg_input *family[3]={&s->aec,&s->tintless,&s->awb};
  unsigned n=p?1:0,r=p<2?p:2;
  in->request_id[p]=in->geometry.request_id[p]=s->request_id=iq->request_id=a->request_id=ids[p];
  s->phase=iq->phase=a->phase=p;
  s->active_width=iq->active_width=4064;s->active_height=iq->active_height=2286;
  CHECK(native_rear_stats_geometry_preset(s,p?NATIVE_REAR_STATS_NORMAL:NATIVE_REAR_STATS_COLD)==0);
  for(unsigned f=0;f<3;f++){
   family[f]->threshold_r=family[f]->threshold_b=family[f]->threshold_gr=family[f]->threshold_gb=0x3ffff;
   family[f]->enabled=family[f]->controls_valid=true;
   /* Explicit bounded zero black/unused weights policy, not recovered 3A policy. */
  }
  for(unsigned f=0;f<2;f++){
   const u32 *v=bg[(f?2:0)+n];struct native_rear_bg_input *out=f?&s->awb:&s->aec;
   CHECK(v[0]==4064&&v[1]==2286&&v[12]==18&&v[13]==0x3f800000);
   CHECK(v[2]<=UINT16_MAX&&v[3]<=UINT16_MAX&&v[4]<=UINT16_MAX&&v[5]<=UINT16_MAX&&v[6]<=UINT16_MAX&&v[7]<=UINT16_MAX);
   out->h_num=v[2];out->v_num=v[3];out->roi=(struct native_rear_stats_roi){v[4],v[5],v[6],v[7]};
   out->threshold_r=v[8];out->threshold_b=v[9];out->threshold_gr=v[10];out->threshold_gb=v[11];
  }
  memcpy(s->aec.y_weight_q4,weights[n],3);s->awb.quad_sync_enable=weights[n][3];
  CHECK(weights[n][3]<=1);
  CHECK(rs[r][0]==4064&&rs[r][1]==2286&&rs[r][2]<=16&&rs[r][3]<=1024&&rs[r][4]<=1&&rs[r][5]<=1);
  s->rs.roi.width=rs[r][4]?4064/2:4064;s->rs.h_num=rs[r][2];s->rs.v_num=rs[r][3];s->rs.color_conversion=rs[r][5];
  iq->controls_valid=true;iq->bpcabf=bpc[r];
  if(p)iq->af=af[p-1];
  /* CST_SOURCE */
  a->valid=true;memcpy(a->lsc1,lsc[n][0],884);memcpy(a->lsc2,lsc[n][1],884);memcpy(a->gtm,gtm,2048);
 }
 CHECK(native_rear_compose_startup(set,in)==0);
 CHECK(full_allocations==0);
 CHECK(e008o_rear_validate_semantic_set(set)==0);
 CHECK(e008l_rear_command_alloc(&vfe,&cmd)==0);
 CHECK(e008o_rear_materialize_commands(set,&cmd)==0);
 CHECK(native_rear_validate_prepared_commands(&cmd)==0);
 unsigned regs[4]={0},dmis[4]={0};size_t payload=0;
 for(unsigned p=0;p<4;p++){
  struct e007y_rear_startup_output *out=&cmd.packet[p].out;
  CHECK(cmd.packet_request_id[p]==ids[p]);CHECK(!cmd.hardware_exposed);
  for(size_t off=0;off<out->main_bytes;){
   u32 header=get_unaligned_le32(out->main+off),op=header>>24;
   if(op==3){regs[p]+=header&0xffff;off+=8+4*(header&0xffff);}
   else{CHECK(op==1||op==10||op==11);payload+=(header&0xffff)+1;dmis[p]++;off+=12;}
  }
  CHECK(dmis[p]==out->dmi_count);
  write_private(argv[1],"main",p,0,out->main,out->main_bytes);
  for(size_t j=0;j<out->dmi_count;j++)write_private(argv[1],"dmi",p,j,out->dmi[j].cpu,out->dmi[j].bytes);
 }
 CHECK(e008o_rear_runtime_authorization()==-EOPNOTSUPP);
 CHECK(e008l_rear_command_release(&vfe,&cmd,false)==0);CHECK(full_allocations==0);
 printf("{\"status\":\"PASS\",\"assertions\":%u,\"register_writes\":[%u,%u,%u,%u],\"dmi_slots\":[%u,%u,%u,%u],\"dmi_payload_bytes\":%zu}\n",checks,regs[0],regs[1],regs[2],regs[3],dmis[0],dmis[1],dmis[2],dmis[3],payload);
 memzero_explicit(in,sizeof(*in));memzero_explicit(set,sizeof(*set));free(in);free(set);return 0;
}
