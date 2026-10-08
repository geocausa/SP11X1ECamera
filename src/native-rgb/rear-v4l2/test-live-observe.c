/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual staged observer and consumed-IOVA ledger; hardware/IRQ are models. */
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <errno.h>
#include <limits.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef uint64_t u64;
#define __used __attribute__((used))
#define __iomem
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define static_assert(e) _Static_assert(e,#e)
#define BIT(i) (1U<<(i))
#define U32_MAX UINT32_MAX
#define U64_MAX UINT64_MAX
#define READ_ONCE(x) (x)
#define NATIVE_REAR_NV12_Y_BYTES 8294400U
#define NATIVE_REAR_NV12_UV_BYTES 4147200U
#define E008H_REAR_SLOTS 2U
#define E007Y_STARTUP_PACKETS 4U
#define E005Y_VFE1_OWNER_REAR 2
#define VFE680_X1E_BUS_CFG 0U
#define VFE680_X1E_BUS_IMAGE_ADDR 4U
#define VFE680_X1E_BUS_ADDR_STATUS0 8U
#define VFE_BUS_WRITE_CLIENT_CFG_EN 1U
static unsigned assertions,negative_cases,read_count,sync_count;
#define CHECK(x) do { assertions++;if(!(x)){fprintf(stderr,"check failed %u: %s\n",__LINE__,#x);exit(2);} } while(0)
#include "camss-e007z-rear-retirement.inc"
struct e008d_rear_addresses {u8 wm[10];u32 image[10];};
struct e008h_rear_prime_pair {
 struct e008d_rear_addresses addr[2];
 struct e007z_rear_frame frame[2];
 bool allocated,enabled,ledgers_bound,programmed[2],faulted;
};
struct e008k_rear_result {
 u64 owner_epoch;bool packet_submitted[4];
 bool csid_quiesced,bus_stopped,rtcdm_stopped,source_stopped,dma_reclaimed,owner_released;
};
struct camss;
struct vfe_device {struct camss *camss;bool valid;u32 registers[20][4];};
struct csid_device {
 bool valid;unsigned irq;u64 e008i_rear_owner_epoch;
 u32 produced,native_rear_done_consumed,epoch,overflow,latch_errors;
};
struct e005y_vfe1_owner {int lock,active_owner;u64 active_epoch;bool unsafe_stop_pinned;};
struct camss {struct vfe_device vfe[2];struct csid_device csid[2];struct e005y_vfe1_owner e005y_vfe1_owner;void *dev;};
#define spin_lock_irqsave(p,flags) do {CHECK(*(p)==0);*(p)=1;(flags)=0;} while(0)
#define spin_unlock_irqrestore(p,flags) do {CHECK(*(p)==1);*(p)=0;(void)(flags);} while(0)
struct vfe680_e004nu_rear_wm_static {u8 wm;u32 cfg;};
static struct vfe680_e004nu_rear_wm_static contracts[10];
static int contract_missing=-1,addr_missing=-1,race_at=-1,race_kind;
static struct camss *active;
static char scalar_log[2048];
static bool vfe680_e004nt_rear_4k_target(struct vfe_device *v){return v->valid;}
static bool csid680_e008k_rear_mode0(struct csid_device *c){return c->valid;}
static const struct vfe680_e004nu_rear_wm_static *e008d_rear_contract_for_wm(u8 wm){
 int i=e007z_rear_index(wm);return i<0||i==contract_missing?NULL:&contracts[i];
}
static int e008h_rear_addr_index(const struct e008d_rear_addresses *a,u8 wm){
 int i=e007z_rear_index(wm);if(i==addr_missing)return -ENOENT;
 for(unsigned j=0;j<10;j++)if(a->wm[j]==wm)return (int)j;
 return -ENOENT;
}
static void *vfe680_x1e_bus_reg(struct vfe_device *v,u8 wm,unsigned offset){CHECK(wm<20&&offset==0);return v->registers[wm];}
static void inject(void){
 struct csid_device *c=&active->csid[1];
 switch(race_kind){
 case 1:c->epoch++;break;
 case 2:c->produced++;break;
 case 3:c->native_rear_done_consumed++;break;
 case 4:active->e005y_vfe1_owner.unsafe_stop_pinned=true;break;
 case 5:c->overflow++;break;
 case 6:c->latch_errors++;break;
 case 7:c->e008i_rear_owner_epoch++;break;
 default:break;
 }
}
static u32 readl_relaxed(const void *p){u32 v=*(const u32*)p;if((int)read_count==race_at)inject();read_count++;return v;}
static void synchronize_irq(unsigned irq){CHECK(irq==11);sync_count++;}
static u32 csid680_e008i_rear_done_count(struct csid_device *c){return c->produced;}
static u32 csid680_e008i_rear_done_overflow(struct csid_device *c){return c->overflow;}
static u32 csid680_e008i_rear_latch_errors(struct csid_device *c){return c->latch_errors;}
static u32 csid680_e008i_rear_epoch0_seq(struct csid_device *c){return c->epoch;}
static void capture_scalar(const char *format,...){va_list a;va_start(a,format);vsnprintf(scalar_log,sizeof(scalar_log),format,a);va_end(a);}
#define dev_info(dev,fmt,...) do {(void)(dev);capture_scalar(fmt,__VA_ARGS__);}while(0)
#include "native-rear-live-observe.inc"
static struct camss camss;
static struct e008h_rear_prime_pair pair;
static struct e008k_rear_result result;
static struct native_rear_live_observation observation;
static void fixture(void){
 memset(&camss,0,sizeof(camss));memset(&pair,0,sizeof(pair));memset(&result,0,sizeof(result));
 active=&camss;read_count=sync_count=0;contract_missing=addr_missing=race_at=-1;race_kind=0;
 camss.e005y_vfe1_owner.active_owner=2;camss.e005y_vfe1_owner.active_epoch=41;
 for(unsigned s=0;s<2;s++){camss.vfe[s].camss=&camss;camss.vfe[s].valid=true;camss.csid[s].valid=true;}
 camss.csid[1].irq=11;camss.csid[1].e008i_rear_owner_epoch=41;camss.csid[1].produced=camss.csid[1].native_rear_done_consumed=15;camss.csid[1].epoch=2;
 pair.allocated=pair.enabled=pair.ledgers_bound=pair.programmed[0]=pair.programmed[1]=true;
 result.owner_epoch=41;for(unsigned i=0;i<4;i++)result.packet_submitted[i]=true;
 for(unsigned s=0;s<2;s++){
  struct e007z_rear_binding b[10]={0};
  for(unsigned i=0;i<10;i++){
   const struct e007z_rear_wm_desc *d=&e007z_rear_wm_descs[i];u32 base=0x10000000U+s*0x20000000U+i*0x01000000U;
   b[i]=(struct e007z_rear_binding){d->wm,base,d->required_bytes,base+d->image_offset};
   pair.addr[s].wm[i]=d->wm;pair.addr[s].image[i]=b[i].programmed_image_iova;
  }
  CHECK(e007z_rear_bind(&pair.frame[s],41,s+1,b)==0);
  for(unsigned i=0;i<10;i++)CHECK(e007z_rear_observe(&pair.frame[s],41,s+1,BIT(e007z_rear_wm_descs[i].comp_group),b[i].wm,b[i].programmed_image_iova)==0);
 }
 for(unsigned i=0;i<10;i++){
  u8 wm=e007z_rear_wm_descs[i].wm;contracts[i]=(struct vfe680_e004nu_rear_wm_static){wm,0x20U+i*0x20U};
  camss.vfe[1].registers[wm][0]=contracts[i].cfg|1;
  camss.vfe[1].registers[wm][1]=camss.vfe[1].registers[wm][2]=pair.addr[1].image[i];
 }
}
static int check_read(u32 cursor){return native_rear_live_replacement_read(&camss.vfe[1],&camss.csid[1],&pair,&result,cursor,&observation);}
static void positive(u32 cursor){
 struct camss old=camss;struct e008h_rear_prime_pair old_pair=pair;struct e008k_rear_result old_result=result;
 CHECK(check_read(cursor)==0);CHECK(read_count==30&&sync_count==1);
 CHECK(observation.enabled_mask==1023&&observation.programmed_mask==1023&&observation.consumed_mask==1023);
 CHECK(observation.owner_current&&observation.old_complete&&observation.next_complete&&observation.receipts_complete);
 CHECK(!memcmp(&old,&camss,sizeof(camss)));CHECK(!memcmp(&old_pair,&pair,sizeof(pair)));CHECK(!memcmp(&old_result,&result,sizeof(result)));
 CHECK(!e007z_rear_retireable(&pair.frame[0],41,1,false,false));
}
static void negative(void){
 struct camss old=camss;struct e008h_rear_prime_pair old_pair=pair;struct e008k_rear_result old_result=result;
 CHECK(check_read(15)<0);negative_cases++;
 if(race_at<0)CHECK(!memcmp(&old,&camss,sizeof(camss)));
 CHECK(!memcmp(&old_pair,&pair,sizeof(pair)));CHECK(!memcmp(&old_result,&result,sizeof(result)));
}
int main(void){
 fixture();positive(15);fixture();native_rear_live_replacement_observe(&camss.vfe[1],&camss.csid[1],&pair,&result,15);CHECK(strstr(scalar_log,"ret=0"));CHECK(strstr(scalar_log,"live_release=0"));CHECK(!strstr(scalar_log,"0x"));
 const u32 sequences[]={1,16,17,1024,4096};
 for(unsigned i=0;i<ARRAY_SIZE(sequences);i++){fixture();camss.csid[1].produced=camss.csid[1].native_rear_done_consumed=sequences[i];positive(sequences[i]);}
 fixture();CHECK(native_rear_live_replacement_read(NULL,&camss.csid[1],&pair,&result,15,&observation)==-EINVAL);
 fixture();CHECK(native_rear_live_replacement_read(&camss.vfe[1],NULL,&pair,&result,15,&observation)==-EINVAL);
 fixture();CHECK(native_rear_live_replacement_read(&camss.vfe[1],&camss.csid[1],NULL,&result,15,&observation)==-EINVAL);
 fixture();CHECK(native_rear_live_replacement_read(&camss.vfe[1],&camss.csid[1],&pair,NULL,15,&observation)==-EINVAL);
 fixture();CHECK(native_rear_live_replacement_read(&camss.vfe[1],&camss.csid[1],&pair,&result,15,NULL)==-EINVAL);
 fixture();camss.vfe[1].valid=false;negative();
 fixture();camss.csid[1].valid=false;negative();
 fixture();camss.csid[1].irq=0;negative();
 fixture();result.owner_epoch=0;negative();
 fixture();camss.e005y_vfe1_owner.active_owner=1;negative();
 fixture();camss.e005y_vfe1_owner.active_epoch++;negative();
 fixture();camss.e005y_vfe1_owner.unsafe_stop_pinned=true;negative();
 fixture();camss.csid[1].e008i_rear_owner_epoch++;negative();
 for(unsigned k=0;k<6;k++){fixture();bool *f[]={&result.csid_quiesced,&result.bus_stopped,&result.rtcdm_stopped,&result.source_stopped,&result.dma_reclaimed,&result.owner_released};*f[k]=true;negative();}
 for(unsigned k=0;k<5;k++){fixture();bool *f[]={&pair.allocated,&pair.enabled,&pair.ledgers_bound,&pair.programmed[0],&pair.programmed[1]};*f[k]=false;negative();}
 fixture();pair.faulted=true;negative();
 for(unsigned s=0;s<2;s++){
  fixture();pair.frame[s].active=false;negative();fixture();pair.frame[s].faulted=true;negative();
  fixture();pair.frame[s].owner_epoch++;negative();fixture();pair.frame[s].request_generation=0;negative();
  for(unsigned i=0;i<10;i++){fixture();pair.frame[s].pending=BIT(i);negative();}
 }
 fixture();pair.frame[1].request_generation++;negative();fixture();pair.frame[0].request_generation=U64_MAX;negative();
 for(unsigned a=0;a<10;a++)for(unsigned b=0;b<10;b++){fixture();pair.frame[0].slot[a].owned_base_iova=pair.frame[1].slot[b].owned_base_iova;pair.frame[0].slot[a].programmed_image_iova=pair.frame[0].slot[a].owned_base_iova;pair.addr[0].image[a]=pair.frame[0].slot[a].programmed_image_iova;negative();}
 for(unsigned i=0;i<10;i++){fixture();pair.frame[0].slot[i].owned_bytes=0;negative();fixture();pair.addr[0].image[i]+=4;negative();}
 for(unsigned i=0;i<4;i++){fixture();result.packet_submitted[i]=false;negative();}
 fixture();camss.csid[1].overflow=1;negative();fixture();camss.csid[1].latch_errors=1;negative();
 fixture();camss.csid[1].produced=0;negative();fixture();camss.csid[1].produced=U32_MAX;negative();
 fixture();camss.csid[1].produced++;negative();fixture();camss.csid[1].native_rear_done_consumed--;negative();fixture();camss.csid[1].native_rear_done_consumed++;negative();
 fixture();camss.csid[1].epoch=1;negative();fixture();camss.csid[1].epoch=U32_MAX;negative();
 for(unsigned i=0;i<10;i++){
  fixture();contract_missing=(int)i;negative();fixture();addr_missing=(int)i;negative();
  fixture();pair.frame[1].slot[i].owned_bytes=0;negative();
  fixture();pair.addr[1].image[i]+=4;negative();
  for(unsigned j=0;j<3;j++){fixture();u8 wm=e007z_rear_wm_descs[i].wm;camss.vfe[1].registers[wm][j]^=j?4U:1U;negative();}
  fixture();camss.vfe[1].registers[e007z_rear_wm_descs[i].wm][0]^=0x1000U;negative();
 }
 for(unsigned kind=1;kind<=7;kind++)for(unsigned at=0;at<30;at++){fixture();race_at=(int)at;race_kind=(int)kind;negative();}
 printf("{\"assertions\":%u,\"negative_cases\":%u,\"read_only_live_observer\":true,\"modelled_MMIO_and_IRQ\":true,\"DMA_release_or_reuse_authority\":false}\n",assertions,negative_cases);
 return 0;
}
