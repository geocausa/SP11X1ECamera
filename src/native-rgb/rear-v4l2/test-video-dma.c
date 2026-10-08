/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native-rear-video-dma.h"
#define __used __attribute__((unused))
#define V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE 9
#define V4L2_PIX_FMT_NV12 0x3231564eU
#define VB2_BUF_STATE_ACTIVE 3
#define VFE_LINE_PIX 0
struct scatterlist {u64 dma,len;struct scatterlist *next;};
struct sg_table {struct scatterlist *sgl;unsigned int nents,orig_nents;};
struct vb2_buffer {unsigned int num_planes,state;struct {unsigned int data_offset;} planes[1];u64 bytes;struct sg_table *table;};
struct camss_buffer {struct {struct vb2_buffer vb2_buf;} vb;u64 addr[3];};
struct v4l2_pix_format_mplane {unsigned int width,height,pixelformat,num_planes;struct {unsigned int bytesperline,sizeimage;} plane_fmt[1];};
struct camss;
struct camss_video {struct camss *camss;struct {unsigned int type;struct {struct v4l2_pix_format_mplane pix_mp;} fmt;} active_fmt;};
struct vfe_device {struct camss *camss;bool exact;struct {struct camss_video video_out;} line[1];};
struct camss {struct vfe_device vfe[2];};
static bool vfe680_e004nt_rear_4k_target(struct vfe_device *v){return v&&v->camss&&v->exact;}
static struct sg_table *vb2_dma_sg_plane_desc(struct vb2_buffer *v,unsigned int plane){if(plane)abort();return v->table;}
static u64 vb2_plane_size(struct vb2_buffer *v,unsigned int plane){if(plane)abort();return v->bytes;}
#define sg_dma_address(sg) ((sg)->dma)
#define sg_dma_len(sg) ((sg)->len)
#define for_each_sgtable_dma_sg(table,sg,i) for(i=0,sg=(table)->sgl;i<(table)->nents&&sg;sg=sg->next,i++)
#include "native-rear-video-dma.inc"
static unsigned int assertions,negatives,partitions;
#define CHECK(x) do {assertions++;if(!(x)){fprintf(stderr,"line%d %s\n",__LINE__,#x);exit(1);}}while(0)
static struct camss cam;
static struct camss_buffer buffer;
static struct scatterlist entries[64];
static struct sg_table table;
static struct native_rear_video_dma span;
static void init(void){
 memset(&cam,0,sizeof(cam));memset(&buffer,0,sizeof(buffer));memset(entries,0,sizeof(entries));
 cam.vfe[1].camss=&cam;cam.vfe[1].exact=true;
 struct camss_video *video=&cam.vfe[1].line[0].video_out;
 video->camss=&cam;video->active_fmt.type=V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
 video->active_fmt.fmt.pix_mp=(struct v4l2_pix_format_mplane){.width=3840,.height=2160,.pixelformat=V4L2_PIX_FMT_NV12,.num_planes=1,.plane_fmt={{3840,12441600}}};
 entries[0]=(struct scatterlist){0x10000000,12443648,NULL};
 table=(struct sg_table){entries,1,13}; /* Coalesced mapped nents != physical orig_nents. */
 buffer.vb.vb2_buf=(struct vb2_buffer){.num_planes=1,.state=VB2_BUF_STATE_ACTIVE,.bytes=12441600,.table=&table};
 buffer.addr[0]=0xdead0000; /* Cached first address must never be trusted. */
 span=(struct native_rear_video_dma){0xabcdef00,0x12345678,42};
}
static int admit(void){return native_rear_video_buffer_dma(&cam.vfe[1],&cam.vfe[1].line[0].video_out,&buffer,&span);}
static void reject(void){
 struct native_rear_video_dma before=span;
 CHECK(admit()<0);CHECK(!memcmp(&before,&span,sizeof(span)));negatives++;
 CHECK(buffer.vb.vb2_buf.state==VB2_BUF_STATE_ACTIVE);
}
int main(void){
 init();CHECK(admit()==0);CHECK(span.y_iova==0x10000000);CHECK(span.uv_iova==0x107e9000);CHECK(span.mapped_bytes==12443648);
 CHECK(buffer.addr[0]==0xdead0000&&buffer.vb.vb2_buf.state==VB2_BUF_STATE_ACTIVE);
 /* Partition the same device aperture into 1..64 adjacent mapped entries. */
 for(unsigned n=1;n<=64;n++){
  init();u64 position=0x10000000,left=12443648;
  for(unsigned i=0;i<n;i++){u64 bytes=i==n-1?left:4096+(i*37U)%9000U;entries[i]=(struct scatterlist){position,bytes,i==n-1?NULL:&entries[i+1]};position+=bytes;left-=bytes;}
  table.nents=n;table.orig_nents=n+7;
  CHECK(admit()==0);CHECK(span.y_iova==0x10000000&&span.uv_iova==0x107e9000);CHECK(span.mapped_bytes==12443648);partitions++;
  /* Even a hole in the last segment is rejected; no first-entry shortcut. */
  if(n>1){entries[n-1].dma++;reject();entries[n-1].dma-=2;reject();}
 }
 for(unsigned i=0;i<23;i++){
  init();struct camss_video *video=&cam.vfe[1].line[0].video_out;
  struct v4l2_pix_format_mplane *f=&video->active_fmt.fmt.pix_mp;
  switch(i){
   case 0:cam.vfe[1].exact=false;break;
   case 1:video->camss=NULL;break;
   case 2:video->active_fmt.type=1;break;
   case 3:buffer.vb.vb2_buf.num_planes=2;break;
   case 4:buffer.vb.vb2_buf.planes[0].data_offset=1;break;
   case 5:f->pixelformat=0;break;
   case 6:f->num_planes=2;break;
   case 7:f->width--;break;
   case 8:f->height--;break;
   case 9:f->plane_fmt[0].bytesperline--;break;
   case 10:f->plane_fmt[0].sizeimage--;break;
   case 11:buffer.vb.vb2_buf.table=NULL;break;
   case 12:table.sgl=NULL;break;
   case 13:table.nents=0;break;
   case 14:entries[0].len=0;break;
   case 15:entries[0].dma=0;break;
   case 16:entries[0].dma++;break;
   case 17:entries[0].dma=0x100000000ULL;break;
   case 18:entries[0].dma=0xfffff000ULL;break;
   case 19:entries[0].len=12441599;break;
   case 20:buffer.vb.vb2_buf.bytes=12441599;break;
   case 21:buffer.vb.vb2_buf.bytes=12443649;break;
   case 22:table.nents=2;break; /* Linked SG ends before mapped nents. */
  }
  reject();
 }
 init();buffer.vb.vb2_buf.state=2;CHECK(admit()==-EINVAL);negatives++;
 init();struct native_rear_video_dma before=span;
 CHECK(native_rear_video_buffer_dma(NULL,&cam.vfe[1].line[0].video_out,&buffer,&span)==-EINVAL);
 CHECK(native_rear_video_buffer_dma(&cam.vfe[1],NULL,&buffer,&span)==-EINVAL);
 CHECK(native_rear_video_buffer_dma(&cam.vfe[1],&cam.vfe[1].line[0].video_out,NULL,&span)==-EINVAL);
 CHECK(native_rear_video_buffer_dma(&cam.vfe[1],&cam.vfe[1].line[0].video_out,&buffer,NULL)==-EINVAL);
 CHECK(native_rear_video_buffer_dma(&cam.vfe[1],&cam.vfe[0].line[0].video_out,&buffer,&span)==-EINVAL);
 CHECK(!memcmp(&before,&span,sizeof(span)));negatives+=5;
 init();entries[0].dma=0xff421000ULL;CHECK(admit()==0); /* Last valid page-aligned aperture. */
 CHECK((u64)span.y_iova+span.mapped_bytes<=0x100000000ULL);
 struct native_rear_video_dma_scan scan={};CHECK(native_rear_video_dma_append(&scan,0x10000000,4096)==0);
 CHECK(native_rear_video_dma_append(&scan,0x10002000,12443648)<0);
 CHECK(native_rear_video_dma_finish(&scan,12441600,&span)<0); /* Error cannot be forgiven by finish. */
 CHECK(native_rear_video_dma_append(NULL,0x10000000,4096)==-EINVAL);
 CHECK(native_rear_video_dma_finish(NULL,12441600,&span)==-EINVAL);
 printf("{\"assertions\":%u,\"negative_cases\":%u,\"valid_mapped_segment_partitions\":%u,\"cached_first_address_ignored\":true,\"ACTIVE_VB2_ownership_unchanged\":true,\"CPU_pixel_access_or_MMIO\":false}\n",assertions,negatives,partitions);
 return 0;
}
