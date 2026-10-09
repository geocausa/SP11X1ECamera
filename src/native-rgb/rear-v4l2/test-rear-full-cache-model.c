#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef uint64_t u64;
typedef uint32_t u32;
#define __used __attribute__((unused))
#define NATIVE_REAR_NV12_BYTES 12441600U
#define NATIVE_REAR_NV12_UV_OFFSET 8294400U
#define DMA_FROM_DEVICE 1
static unsigned int assertions, negatives, unmaps, detaches, put_count;
#define CHECK(x) do { assertions++; if(!(x)){fprintf(stderr,"FAIL line %u: %s\n",__LINE__,#x);exit(1);} } while(0)
struct native_rear_video_dma { u64 y_iova, uv_iova, mapped_bytes; };
struct dma_buf { int identity; };
struct dma_buf_attachment { int identity; };
struct sg_table { struct native_rear_video_dma span; };
struct camss { void *dev; };
struct vfe_device { struct camss *camss; };
static int model_log(void *dev,const char *fmt,...) { (void)dev;(void)fmt;return 0; }
#define dev_info model_log
static int native_rear_video_dma_table(struct sg_table *t,size_t bytes,struct native_rear_video_dma *out)
{ if(!t||bytes<NATIVE_REAR_NV12_BYTES)return -EINVAL;*out=t->span;return 0; }
static void dma_buf_unmap_attachment_unlocked(struct dma_buf_attachment *a,struct sg_table *t,int dir)
{ CHECK(a&&t&&dir==DMA_FROM_DEVICE);unmaps++; }
static void dma_buf_detach(struct dma_buf *b,struct dma_buf_attachment *a)
{ CHECK(b&&a);detaches++; }
static void dma_buf_put(struct dma_buf *b){CHECK(b);put_count++;}
/* ACTUAL_LEASE_TYPES */
/* ACTUAL_LEASE_HELPERS */
#include "native-rear-full-cache.inc"
static struct dma_buf bufs[8];
static struct dma_buf_attachment attachments[8];
static struct sg_table tables[8];
static struct native_rear_video_lease lease(unsigned int n)
{
 CHECK(n<8);
 tables[n].span=(struct native_rear_video_dma){0x10000000ULL+0x1000000ULL*n,0x10000000ULL+0x1000000ULL*n+NATIVE_REAR_NV12_UV_OFFSET,NATIVE_REAR_NV12_BYTES};
 return (struct native_rear_video_lease){.dbuf=&bufs[n],.attachment=&attachments[n],.table=&tables[n],.span=tables[n].span,.acquired=true,.exposed=true};
}
static void unchanged(struct native_rear_full_cache before,unsigned int count)
{CHECK(memcmp(&before,&native_rear_full_cache,sizeof(before))==0);CHECK(unmaps==count);negatives++;}
int main(void)
{
 struct camss camss={0};struct vfe_device vfe={&camss};
 struct native_rear_video_lease old,next,out;
 struct native_rear_full_cache saved,before;
 unsigned int i,n,initial;
 CHECK(native_rear_full_cache_idle());
 CHECK(native_rear_full_cache_begin(7)==0);
 old=lease(0);CHECK(native_rear_full_cache_retire(&old,7,1)==0);CHECK(!old.acquired);
 saved=native_rear_full_cache;
 /* Foreign owner, missing generation, exposed/stop state, aliases and dirty
  * destination rejection leave physical ownership and all mappings untouched. */
 for(i=0;i<10;i++){
  native_rear_full_cache=saved;before=native_rear_full_cache;initial=unmaps;
  old=lease(1);
  switch(i){
  case 0:CHECK(native_rear_full_cache_begin(8)==-EBUSY);break;
  case 1:CHECK(native_rear_full_cache_retire(&old,8,2)<0);break;
  case 2:CHECK(native_rear_full_cache_retire(&old,7,0)<0);break;
  case 3:old.exposed=false;CHECK(native_rear_full_cache_retire(&old,7,2)<0);break;
  case 4:old.stop_proven=true;CHECK(native_rear_full_cache_retire(&old,7,2)<0);break;
  case 5:old.dbuf=&bufs[0];CHECK(native_rear_full_cache_retire(&old,7,2)<0);break;
  case 6:old.attachment=&attachments[0];CHECK(native_rear_full_cache_retire(&old,7,2)<0);break;
  case 7:old.table=&tables[0];CHECK(native_rear_full_cache_retire(&old,7,2)<0);break;
  case 8:old.span.y_iova=tables[0].span.y_iova+NATIVE_REAR_NV12_BYTES-1;old.span.uv_iova=old.span.y_iova+NATIVE_REAR_NV12_UV_OFFSET;CHECK(native_rear_full_cache_retire(&old,7,2)<0);break;
  case 9:out=(struct native_rear_video_lease){.acquired=true};CHECK(native_rear_full_cache_take(&bufs[0],NATIVE_REAR_NV12_BYTES,7,&out)<0);break;
  }
  unchanged(before,initial);
 }
 for(i=0;i<5;i++){
  native_rear_full_cache=saved;
  if(i==0)native_rear_full_cache.entry[0].owner=8;
  if(i==1)native_rear_full_cache.entry[0].generation=0;
  if(i==2)native_rear_full_cache.entry[0].lease.exposed=false;
  if(i==3)native_rear_full_cache.entry[0].lease.stop_proven=true;
  if(i==4)native_rear_full_cache.entry[1].lease.exposed=true;
  before=native_rear_full_cache;initial=unmaps;
  CHECK(native_rear_full_cache_stop_check(7,true,true,true,true)<0);
  unchanged(before,initial);
 }
 native_rear_full_cache=saved;
 out=(struct native_rear_video_lease){0};before=native_rear_full_cache;initial=unmaps;
 CHECK(native_rear_full_cache_take(&bufs[0],NATIVE_REAR_NV12_BYTES,8,&out)<0);unchanged(before,initial);
 CHECK(native_rear_full_cache_take(&bufs[0],NATIVE_REAR_NV12_BYTES-1,7,&out)<0);unchanged(before,initial);
 tables[0].span.mapped_bytes++;before=native_rear_full_cache;
 CHECK(native_rear_full_cache_take(&bufs[0],NATIVE_REAR_NV12_BYTES,7,&out)<0);unchanged(before,initial);tables[0].span.mapped_bytes--;
 CHECK(native_rear_full_cache_take(&bufs[0],NATIVE_REAR_NV12_BYTES,7,&out)==0);
 CHECK(native_rear_video_lease_valid(&out)&&!out.exposed&&!out.stop_proven);
 CHECK(native_rear_video_lease_expose(&out)==0);
 CHECK(native_rear_full_cache_retire(&out,7,2)==0);
 for(i=0;i<15;i++){
  before=native_rear_full_cache;initial=unmaps;
  CHECK(native_rear_full_cache_flush(&vfe,7,i&1,i&2,i&4,i&8)<0);unchanged(before,initial);
 }
 before=native_rear_full_cache;initial=unmaps;
 CHECK(native_rear_full_cache_flush(&vfe,8,true,true,true,true)<0);unchanged(before,initial);
 CHECK(native_rear_full_cache_flush(&vfe,7,true,true,true,true)==0);
 CHECK(native_rear_full_cache_idle());
 /* Model three independent owners, each with eighty four-buffer handoffs.
  * No physical unmap occurs in the rolling loop. All cached maps survive
  * missing stop barriers, then are freed once, before clean reopen. */
 for(n=1;n<=3;n++){
  CHECK(native_rear_full_cache_begin(n)==0);
  old=lease(1);initial=unmaps;
  for(i=0;i<80;i++){
   unsigned int buffer=(i+2)%4;
   next=(struct native_rear_video_lease){0};
   int ret=native_rear_full_cache_take(&bufs[buffer],NATIVE_REAR_NV12_BYTES,n,&next);
   if(ret==-ENOENT){next=lease(buffer);next.exposed=false;}else CHECK(ret==0);
   CHECK(native_rear_full_cache_disjoint(&next,n)==0);
   CHECK(native_rear_video_lease_expose(&next)==0);
   CHECK(native_rear_full_cache_retire(&old,n,i+2)==0);
   CHECK(!old.acquired);
   old=next;CHECK(unmaps==initial);
  }
  CHECK(native_rear_full_cache.hits==77&&native_rear_full_cache.misses==3);
  CHECK(native_rear_full_cache.stored==80&&native_rear_full_cache.evicted==0);
  CHECK(native_rear_full_cache_flush(&vfe,n,true,true,true,false)<0);
  CHECK(unmaps==initial);
  CHECK(native_rear_full_cache_flush(&vfe,n,true,true,true,true)==0);
  CHECK(unmaps==initial+3&&native_rear_full_cache_idle());
  CHECK(native_rear_video_lease_stop(&old,true,true,true,true)==0);
  CHECK(native_rear_video_lease_put(&old)==0);
  CHECK(unmaps==initial+4&&detaches==unmaps&&put_count==unmaps);
 }
 /* Capacity overflow falls back to the already-proven original live unmap
  * path; it never overwrites, resets or drops an existing cache entry. */
 CHECK(native_rear_full_cache_begin(9)==0);
 for(i=0;i<4;i++){old=lease(i);CHECK(native_rear_full_cache_retire(&old,9,i+1)==0);}
 old=lease(4);initial=unmaps;
 CHECK(native_rear_full_cache_retire(&old,9,5)==1);CHECK(old.acquired&&old.exposed);
 CHECK(unmaps==initial&&native_rear_full_cache.evicted==1);
 CHECK(native_rear_full_cache_flush(&vfe,9,true,true,true,true)==0);
 CHECK(native_rear_video_lease_stop(&old,true,true,true,true)==0);
 CHECK(native_rear_video_lease_put(&old)==0);CHECK(native_rear_full_cache_idle());
 printf("FULL_CACHE_PASS assertions=%u negatives=%u frames=240\n",assertions,negatives);
 return 0;
}
