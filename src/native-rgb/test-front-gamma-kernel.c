/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual kernel bridge included below; allocation, locks, eligibility and
 * provider enqueue are hosted mocks. No hardware, profile, camera or image.
 */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native-front-nv12-commands.h"
typedef uint64_t u64;
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define BIT(i) (1U<<(i))
#define GENMASK(h,l) (((~0U) << (l)) & ((~0U) >> (31-(h))))
#define IS_ALIGNED(x,a) (!((x)&((a)-1)))
#define GFP_KERNEL 0
#define READ_ONCE(x) (x)
#define static_assert _Static_assert
#define dev_info(...) do { } while (0)
#define CAMSS_RTCDM1_CORPUS_PACKET_COUNT 4
#define CAMSS_RTCDM1_CORPUS_PAYLOAD_COUNT 16
#define CAMSS_X1E_PIX_CAPSULE_BYTES 41088
static unsigned checks;
static void need(int condition) { checks++; assert(condition); }
static u32 get_unaligned_le32(const void *p) { return native_nv12_le32(p); }
static u64 get_unaligned_le64(const void *p)
{ return get_unaligned_le32(p)|(u64)get_unaligned_le32((const u8 *)p+4)<<32; }
static void put_unaligned_le32(u32 v,void *p) { native_nv12_put32(p,v); }
static void put_unaligned_le64(u64 v,void *p)
{ put_unaligned_le32(v,p);put_unaligned_le32(v>>32,(u8 *)p+4); }
#include "front-capsule-sections.inc"
struct camss { void *dev; };
struct camss_video {
 struct camss *camss;
 struct { bool streaming; } vb2_q;
 bool x1e_pix_runner_pinned,x1e_pix_live_active,x1e_pix_worker_started;
 int native_params_lock;
 u8 *native_params_profile;
};
struct camss_x1e_pix_capsule_inputs {
 struct { struct { size_t size; const u8 *data; } normalized_main; } steady;
};
static int camss_x1e_pix_capsule_parse(const u8 *p,size_t n,
                                      struct camss_x1e_pix_capsule_inputs *in)
{
 (void)p;(void)n;in->steady.normalized_main.size=0x958;return 0;
}
static bool eligible=true,allowed=true;
static bool camss_x1e_pix_iq_video(struct camss_video *v) { return v && eligible; }
static bool camss_x1e_native_front_params_trial_allowed(struct camss *c)
{ (void)c;return allowed; }
static int locks;
static void mutex_lock(int *lock) { (void)lock;locks++; }
static void mutex_unlock(int *lock) { (void)lock;need(locks>0);locks--; }
struct allocation { void *p; size_t n; bool erase; };
static struct allocation allocation[8];
static unsigned active,attempts,fail_at,cleared;
static void *allocate(size_t n,bool erase)
{
 attempts++;
 if(fail_at && attempts==fail_at)return NULL;
 void *p=calloc(1,n);need(p!=NULL && active<8);
 allocation[active++]=(struct allocation){p,n,erase};
 return p;
}
static void *kmemdup(const void *p,size_t n,int flags)
{
 (void)flags;void *out=allocate(n,true);if(out)memcpy(out,p,n);return out;
}
#define kzalloc_obj(obj,flags) allocate(sizeof(obj),false)
static void memzero_explicit(void *p,size_t n) { memset(p,0,n);cleared++; }
static void kfree(void *p)
{
 if(!p)return;
 unsigned i;
 for(i=0;i<active;i++)if(allocation[i].p==p)break;
 need(i<active);
 if(allocation[i].erase) {
  bool zero=true;
  for(size_t j=0;j<allocation[i].n;j++)zero=zero && ((u8 *)p)[j]==0;
  need(zero);
 }
 free(p);allocation[i]=allocation[--active];
}
static u8 *queued;
static unsigned enqueues,closes,purges;
static u64 last_request=4;
static int queue_error;
static int camss_x1e_pix_iq_provider_enqueue(struct camss_video *v,
                                             const void *p,size_t n)
{
 (void)v;enqueues++;
 if(queue_error)return queue_error;
 if(get_unaligned_le64((const u8 *)p+0x2c)!=last_request+1)return -EPROTO;
 need(!queued);queued=malloc(n);need(queued!=NULL);memcpy(queued,p,n);
 last_request++;return 0;
}
static void camss_x1e_pix_iq_provider_close(struct camss_video *v)
{ (void)v;closes++; }
static void camss_x1e_pix_iq_provider_purge(struct camss_video *v)
{ (void)v;purges++;free(queued);queued=NULL; }
static int profile_error;
static int native_front_profile_load(struct camss_video *v)
{ (void)v;return profile_error; }
#include "hosted-front-params-kernel.inc"
#include "native-front-param-state.h"

static void description(u8 *data,unsigned slot,unsigned type,unsigned index,
                         unsigned offset,unsigned size)
{
 u8 *d=data+CAMSS_X1E_PIX_CAPSULE_DESC_OFFSET+slot*CAMSS_X1E_PIX_CAPSULE_DESC_BYTES;
 put_unaligned_le32(type,d);put_unaligned_le32(index,d+4);
 put_unaligned_le32(offset,d+8);put_unaligned_le32(size,d+12);
}
static void capsule_fixture(u8 *data)
{
 memset(data,0x5a,CAMSS_X1E_PIX_CAPSULE_BYTES);
 memset(data,0,CAMSS_X1E_PIX_CAPSULE_HEADER_BYTES);
 unsigned slot=0,offset=1024;
 for(unsigned type=1;type<=5;type++) {
  unsigned count=type==1?4:type==2?16:type==5?14:1;
  for(unsigned i=0;i<count;i++) {
   unsigned bytes=type==4?9*32:type==5?camss_x1e_epoch0_payloads[i].size:64;
   description(data,slot++,type,i,offset,bytes);
   offset=(offset+bytes+63)&~63U;
  }
 }
 need(slot==36 && offset<=CAMSS_X1E_PIX_CAPSULE_BYTES);
 put_unaligned_le64(4,data+0x2c);
 need(!camss_x1e_pix_capsule_validate_sections(data,CAMSS_X1E_PIX_CAPSULE_BYTES));
}
static void packet_fixture(u8 *packet,u64 request)
{
 memset(packet,0,64);
 put_unaligned_le32(NATIVE_FRONT_PARAMS_MAGIC,packet);
 packet[4]=1;packet[6]=64;put_unaligned_le64(request,packet+8);
}
static int queue_adapter(void *ctx,u64 request,const u8 *gamma,size_t bytes)
{
 u8 packet[64];packet_fixture(packet,request);
 return gamma?camss_x1e_front_params_gamma_submit(ctx,packet,64,gamma,bytes):
              camss_x1e_front_params_submit(ctx,packet,64);
}
static void clean_request(void) { free(queued);queued=NULL;need(active==0 && locks==0); }
int main(void)
{
 u8 *baseline=malloc(CAMSS_X1E_PIX_CAPSULE_BYTES);
 u8 *before=malloc(CAMSS_X1E_PIX_CAPSULE_BYTES);
 u8 *candidate=malloc(CAMSS_X1E_PIX_CAPSULE_BYTES);
 u8 packet[64],gamma[NF_GAMMA_BYTES],saved_gamma[NF_GAMMA_BYTES];
 nf_gamma_u16 points[NF_GAMMA_POINT_COUNT];
 struct camss camss={0};
 struct camss_video video={.camss=&camss,.native_params_profile=baseline};
 need(baseline && before && candidate);
 capsule_fixture(baseline);memcpy(before,baseline,CAMSS_X1E_PIX_CAPSULE_BYTES);
 for(unsigned c=0;c<3;c++)for(unsigned i=0;i<257;i++)
  points[c*257+i]=(c+1)*100+i;
 need(!native_front_gamma12_pack(points,NF_GAMMA_POINT_COUNT,gamma,sizeof(gamma)));
 need(!native_front_gamma12_validate(gamma,sizeof(gamma)));
 memcpy(saved_gamma,gamma,sizeof(gamma));
 packet_fixture(packet,5);
 /* Early profile-store rejection exercises the unmodified startup gate. */
 put_unaligned_le64(3,candidate+0x2c);
 need(native_front_params_profile_store(&video,candidate,CAMSS_X1E_PIX_CAPSULE_BYTES)==-EOPNOTSUPP);
 /* Actual submission, section validator/lookup and scalar bank binder. */
 need(!camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,sizeof(gamma)));
 need(queued && active==0 && locks==0 && cleared==2);
 need(!memcmp(before,baseline,CAMSS_X1E_PIX_CAPSULE_BYTES));
 need(!memcmp(saved_gamma,gamma,sizeof(gamma)));
 need(get_unaligned_le64(queued+0x2c)==5);
 const u8 *modules;size_t bytes;
 need(!camss_x1e_pix_capsule_section(queued,4,0,&modules,&bytes));
 need(get_unaligned_le32(modules+7*32+4)==1);
 need(get_unaligned_le32(modules+7*32+8)==1);
 const unsigned order[]={1,2,0};
 for(unsigned i=0;i<3;i++) {
  const u8 *section;
  need(!camss_x1e_pix_capsule_section(queued,5,7+i,&section,&bytes));
  need(bytes==1024 && !memcmp(section,saved_gamma+order[i]*1024,1024));
 }
 /* Only request ID, admitted scalar fields and three gamma tables may change. */
 memcpy(candidate,before,CAMSS_X1E_PIX_CAPSULE_BYTES);
 put_unaligned_le64(5,candidate+0x2c);
 const u8 *cm;need(!camss_x1e_pix_capsule_section(candidate,4,0,&cm,&bytes));
 for(unsigned i=0;i<9;i++)for(unsigned j=0;j<6;j++)
  memcpy((u8 *)cm+i*32+4+j*4,modules+i*32+4+j*4,4);
 need(!native_front_gamma_bind(candidate,CAMSS_X1E_PIX_CAPSULE_BYTES,saved_gamma,sizeof(saved_gamma)));
 need(!memcmp(candidate,queued,CAMSS_X1E_PIX_CAPSULE_BYTES));
 memset(gamma,0xa5,sizeof(gamma));memset(packet,0xa5,sizeof(packet));
 need(!memcmp(candidate,queued,CAMSS_X1E_PIX_CAPSULE_BYTES));
 clean_request();memcpy(gamma,saved_gamma,sizeof(gamma));packet_fixture(packet,6);
 unsigned calls=enqueues;
 gamma[3071]=1; /* late third-channel reserved byte */
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,sizeof(gamma))==-EINVAL);
 need(enqueues==calls);clean_request();memcpy(gamma,saved_gamma,sizeof(gamma));
 for(unsigned n=0;n<3072;n+=127) {
  need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,n)==-EINVAL);
  need(enqueues==calls);clean_request();
 }
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,NULL,3072)==-EINVAL);
 need(camss_x1e_front_params_gamma_submit(NULL,packet,64,gamma,3072)==-EOPNOTSUPP);
 allowed=false;
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-EOPNOTSUPP);
 allowed=true;video.x1e_pix_runner_pinned=true;
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-EBUSY);
 video.x1e_pix_runner_pinned=false;video.vb2_q.streaming=true;
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-EBUSY);
 video.vb2_q.streaming=false;video.native_params_profile=NULL;
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-ENODATA);
 clean_request();video.native_params_profile=baseline;
 for(unsigned i=1;i<=2;i++) {
  attempts=0;fail_at=i;
  need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-ENOMEM);
  need(enqueues==calls);clean_request();
 }
 fail_at=0;profile_error=-EKEYREJECTED;
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-EKEYREJECTED);
 need(enqueues==calls);clean_request();profile_error=0;
 /* Late malformed third destination rejects atomically and never enqueues. */
 u8 *last=baseline+64+31*16;
 u32 saved=get_unaligned_le32(last+12);
 put_unaligned_le32(1,last+12);
 memcpy(before,baseline,CAMSS_X1E_PIX_CAPSULE_BYTES);
 memcpy(candidate,before,CAMSS_X1E_PIX_CAPSULE_BYTES);
 need(native_front_gamma_bind(candidate,CAMSS_X1E_PIX_CAPSULE_BYTES,gamma,3072)==-EINVAL);
 need(!memcmp(candidate,before,CAMSS_X1E_PIX_CAPSULE_BYTES));
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-EINVAL);
 need(enqueues==calls);clean_request();put_unaligned_le32(saved,last+12);
 /* Descriptor bounds, overlap, duplicate identity and absent table reject
  * without mutating the owned destination or touching the provider FIFO. */
 memcpy(before,baseline,CAMSS_X1E_PIX_CAPSULE_BYTES);
 for(unsigned mode=0;mode<4;mode++) {
  memcpy(candidate,before,CAMSS_X1E_PIX_CAPSULE_BYTES);
  u8 *desc=candidate+64+31*16;
  if(mode==0)put_unaligned_le32(CAMSS_X1E_PIX_CAPSULE_BYTES,desc+8);
  if(mode==1)put_unaligned_le32(get_unaligned_le32(desc-16+8),desc+8);
  if(mode==2)put_unaligned_le32(8,desc+4);
  if(mode==3)put_unaligned_le32(3,desc+4);
  u8 *saved_bad=malloc(CAMSS_X1E_PIX_CAPSULE_BYTES);need(saved_bad!=NULL);
  memcpy(saved_bad,candidate,CAMSS_X1E_PIX_CAPSULE_BYTES);
  need(native_front_gamma_bind(candidate,CAMSS_X1E_PIX_CAPSULE_BYTES,gamma,3072)==-EINVAL);
  need(!memcmp(candidate,saved_bad,CAMSS_X1E_PIX_CAPSULE_BYTES));free(saved_bad);
 }
 memcpy(candidate,before,CAMSS_X1E_PIX_CAPSULE_BYTES);
 need(native_front_gamma_bind(candidate,CAMSS_X1E_PIX_CAPSULE_BYTES,candidate+1024,3072)!=0);
 need(!memcmp(candidate,before,CAMSS_X1E_PIX_CAPSULE_BYTES));
 /* Provider rejection closes/purges as before; both owned copies are erased. */
 queue_error=-ENOSPC;
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-ENOSPC);
 need(closes==1 && purges==1);clean_request();queue_error=0;
 /* Existing scalar-only wrapper still submits the exact old packet. */
 need(!camss_x1e_front_params_submit(&video,packet,64));need(queued!=NULL);
 need(!camss_x1e_pix_capsule_section(queued,4,0,&modules,&bytes));
 need(get_unaligned_le32(modules+7*32+4)==0);
 need(get_unaligned_le32(modules+7*32+8)==0);
 for(unsigned i=0;i<3;i++) {
  const u8 *original,*current;
  size_t original_bytes,current_bytes;
  need(!camss_x1e_pix_capsule_section(baseline,5,7+i,&original,&original_bytes));
  need(!camss_x1e_pix_capsule_section(queued,5,7+i,&current,&current_bytes));
  need(original_bytes==current_bytes && !memcmp(original,current,current_bytes));
 }
 clean_request();packet_fixture(packet,6);
 need(camss_x1e_front_params_gamma_submit(&video,packet,64,gamma,3072)==-EPROTO);
 need(closes==2 && purges==2);clean_request();
 /* Generic envelope -> persistent queue state -> actual scalar/gamma bridge.
  * Only allocation/profile/provider/hardware primitives remain mocked. */
 struct native_front_param_state state;
 u8 isp[NF_ISP_MAX_BYTES],empty[NF_ISP_HEADER_BYTES];
 u32 scratch[NF_GAMMA_WORD_COUNT];int update;
 for(unsigned c=0;c<3;c++)for(unsigned i=0;i<257;i++)points[c*257+i]=c*100+i*3;
 need(!native_front_isp_encode(points,NF_GAMMA_POINT_COUNT,isp,sizeof(isp)));
 need(!native_front_isp_decode(isp,sizeof(isp),scratch,NF_GAMMA_WORD_COUNT,gamma,3072,&update));
 memcpy(saved_gamma,gamma,sizeof(gamma));last_request=4;
 native_front_param_state_reset(&state);
 need(!native_front_param_state_submit(&state,gamma,update,queue_adapter,&video));
 for(unsigned i=0;i<3;i++) {
  const u8 *section;
  need(!camss_x1e_pix_capsule_section(queued,5,7+i,&section,&bytes));
  need(!memcmp(section,saved_gamma+order[i]*1024,1024));
 }
 clean_request();memset(isp,0xa5,sizeof(isp));memset(gamma,0xa5,sizeof(gamma));
 need(!native_front_isp_encode(NULL,0,empty,sizeof(empty)));
 need(!native_front_isp_decode(empty,sizeof(empty),NULL,0,NULL,0,&update));
 need(!native_front_param_state_submit(&state,NULL,update,queue_adapter,&video));
 need(get_unaligned_le64(queued+0x2c)==6);
 for(unsigned i=0;i<3;i++) {
  const u8 *section;
  need(!camss_x1e_pix_capsule_section(queued,5,7+i,&section,&bytes));
  need(!memcmp(section,saved_gamma+order[i]*1024,1024));
 }
 clean_request();queue_error=-ENOSPC;
 need(native_front_param_state_submit(&state,NULL,0,queue_adapter,&video)==-ENOSPC);
 need(state.next==7 && state.failed);clean_request();queue_error=0;
 video.native_params_profile=NULL;camss_x1e_front_params_clear(&video);
 free(candidate);free(before);free(baseline);
 printf("PASS_FRONT_GAMMA_KERNEL_BRIDGE checks=%u hardware_access=false provider_enqueue=mock\n",checks);
 return 0;
}
