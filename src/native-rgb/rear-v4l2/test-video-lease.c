
#define DMA_FROM_DEVICE 2
#define VB2_MEMORY_MMAP 1
#define VB2_MEMORY_DMABUF 4
#define O_CLOEXEC 02000000
#define O_RDWR 2
#define IS_ERR(p) ((uintptr_t)(p) >= (uintptr_t)-4095)
#define IS_ERR_OR_NULL(p) (!(p) || IS_ERR(p))
#define PTR_ERR(p) ((int)(intptr_t)(p))
#define ERR_PTR(x) ((void *)(intptr_t)(x))
struct dma_buf {int refs;};
struct dma_buf_attachment {struct dma_buf *dbuf;};
static struct dma_buf dbuf;
static struct dma_buf_attachment attachment;
static struct scatterlist mapped_entries[2];
static struct sg_table retained_table;
static unsigned fault,live_maps,detach_calls,put_calls;
static char trace[32];static unsigned trace_n;
static void mark(char c){CHECK(trace_n<sizeof(trace)-1);trace[trace_n++]=c;trace[trace_n]=0;}
static struct dma_buf *export_buffer(struct vb2_buffer *vb,void *priv,unsigned long flags){
 CHECK(vb&&priv&&flags==(O_CLOEXEC|O_RDWR));mark('E');
 if(fault==1)return NULL;dbuf.refs++;return &dbuf;
}
const struct vb2_mem_ops vb2_dma_sg_memops={export_buffer};
static void get_dma_buf(struct dma_buf *b){CHECK(b==&dbuf);mark('G');b->refs++;}
static void dma_buf_put(struct dma_buf *b){CHECK(b==&dbuf&&b->refs>0);mark('P');b->refs--;put_calls++;}
static struct dma_buf_attachment *dma_buf_attach(struct dma_buf *b,void *dev){
 CHECK(b==&dbuf&&dev==&cam&&b->refs>0);mark('A');
 if(fault==2)return ERR_PTR(-EIO);attachment.dbuf=b;return &attachment;
}
static struct sg_table *dma_buf_map_attachment_unlocked(struct dma_buf_attachment *a,int direction){
 CHECK(a==&attachment&&direction==DMA_FROM_DEVICE);mark('M');
 if(fault==3)return ERR_PTR(-EIO);
 live_maps++;if(fault==4)mapped_entries[1].dma++;return &retained_table;
}
static void dma_buf_unmap_attachment_unlocked(struct dma_buf_attachment *a,struct sg_table *t,int direction){
 CHECK(a==&attachment&&t==&retained_table&&direction==DMA_FROM_DEVICE&&live_maps==1);mark('U');live_maps--;
}
static void dma_buf_detach(struct dma_buf *b,struct dma_buf_attachment *a){
 CHECK(b==&dbuf&&a==&attachment&&!live_maps);mark('D');detach_calls++;
}
#include "native-rear-video-lease.inc"
static unsigned cases;
static void lease_init(unsigned memory){
 init();dbuf.refs=0;live_maps=detach_calls=put_calls=fault=trace_n=0;trace[0]=0;
 cam.dev=&cam;struct camss_video *video=&cam.vfe[1].line[0].video_out;
 video->vb2_q=(struct vb2_queue){&vb2_dma_sg_memops,DMA_FROM_DEVICE};
 buffer.vb.vb2_buf.vb2_queue=&video->vb2_q;buffer.vb.vb2_buf.memory=memory;
 buffer.vb.vb2_buf.planes[0].mem_priv=&cam;buffer.vb.vb2_buf.planes[0].dbuf=&dbuf;
 mapped_entries[0]=(struct scatterlist){0x20000000,4096,&mapped_entries[1]};
 mapped_entries[1]=(struct scatterlist){0x20001000,12439552,NULL};
 retained_table=(struct sg_table){mapped_entries,2,19};
}
static int lease_get(struct native_rear_video_lease *l){
 return native_rear_video_lease_get(&cam.vfe[1],&cam.vfe[1].line[0].video_out,&buffer,l);
}
int main(void){
 /* Also retain the fixture's ordinary adapter coverage helpers. */
 init();CHECK(admit()==0);init();entries[0].dma++;reject();
 for(unsigned m=0;m<2;m++){
  unsigned memory=m?VB2_MEMORY_DMABUF:VB2_MEMORY_MMAP;
  struct native_rear_video_lease l={};lease_init(memory);
  CHECK(lease_get(&l)==0);CHECK(native_rear_video_lease_valid(&l));
  CHECK(l.span.y_iova==0x20000000&&l.span.y_iova!=span.y_iova);CHECK(dbuf.refs==1&&live_maps==1);
  CHECK(lease_get(&l)==-EBUSY);
  CHECK(native_rear_video_lease_stop(&l,true,true,true,true)==-EBUSY);
  CHECK(native_rear_video_lease_put(&l)==0);CHECK(dbuf.refs==0&&!live_maps&&!native_rear_video_lease_valid(&l));
  CHECK(!strcmp(trace,m?"GAMUDP":"EAMUDP"));cases++;
  for(unsigned mask=0;mask<16;mask++){
   memset(&l,0,sizeof(l));lease_init(memory);CHECK(lease_get(&l)==0);
   CHECK(native_rear_video_lease_expose(&l)==0);CHECK(native_rear_video_lease_expose(&l)==-EINVAL);
   /* VB2's own wrapper/attachment may now vanish. The retained lease has no pointer to it. */
   memset(&buffer,0,sizeof(buffer));table.sgl=NULL;cam.vfe[1].line[0].video_out.vb2_q.mem_ops=NULL;
   CHECK(native_rear_video_lease_put(&l)==-EBUSY);CHECK(l.acquired&&dbuf.refs==1&&live_maps==1);
   int ret=native_rear_video_lease_stop(&l,mask&1,mask&2,mask&4,mask&8);
   if(mask==15){
    CHECK(ret==0);CHECK(native_rear_video_lease_put(&l)==0);
    CHECK(!live_maps&&dbuf.refs==0&&!memcmp(&l,&(struct native_rear_video_lease){},sizeof(l)));
   }else{
    CHECK(ret==-EBUSY);CHECK(native_rear_video_lease_put(&l)==-EBUSY);
    CHECK(l.exposed&&!l.stop_proven&&dbuf.refs==1&&live_maps==1&&put_calls==0&&detach_calls==0);
    /* End model safely; a real uncertain lease stays pinned until hardware reset/reboot. */
    CHECK(native_rear_video_lease_stop(&l,true,true,true,true)==0);CHECK(native_rear_video_lease_put(&l)==0);
   }
   cases++;
  }
  for(unsigned f=m?2:1;f<=4;f++){
   memset(&l,0,sizeof(l));lease_init(memory);fault=f;
   CHECK(lease_get(&l)<0);CHECK(!native_rear_video_lease_valid(&l));
   CHECK(!live_maps&&dbuf.refs==0);CHECK(!memcmp(&l,&(struct native_rear_video_lease){},sizeof(l)));
   const char *expected=f==1?"E":f==2?(m?"GAP":"EAP"):f==3?(m?"GAMDP":"EAMDP"):(m?"GAMUDP":"EAMUDP");
   CHECK(!strcmp(trace,expected));cases++;
  }
 }
 struct native_rear_video_lease l={};
 for(unsigned f=0;f<7;f++){
  lease_init(VB2_MEMORY_MMAP);
  switch(f){
   case 0:buffer.vb.vb2_buf.vb2_queue=NULL;break;
   case 1:cam.vfe[1].line[0].video_out.vb2_q.mem_ops=NULL;break;
   case 2:cam.vfe[1].line[0].video_out.vb2_q.dma_dir=0;break;
   case 3:buffer.vb.vb2_buf.memory=2;break;
   case 4:buffer.vb.vb2_buf.planes[0].mem_priv=NULL;break;
   case 5:buffer.vb.vb2_buf.memory=VB2_MEMORY_DMABUF;buffer.vb.vb2_buf.planes[0].dbuf=NULL;break;
   case 6:buffer.vb.vb2_buf.vb2_queue=(void *)0x1234;break;
  }
  CHECK(lease_get(&l)<0);CHECK(!trace_n&&dbuf.refs==0&&!live_maps);cases++;
 }
 CHECK(native_rear_video_lease_get(NULL,NULL,NULL,NULL)==-EINVAL);
 CHECK(native_rear_video_lease_expose(NULL)==-EINVAL);
 CHECK(native_rear_video_lease_put(NULL)==-EINVAL);
 printf("{\"assertions\":%u,\"lease_cases\":%u,\"MMAP_and_DMABUF\":true,\"own_mapping_differs_from_VB2_and_survives_VB2_cancel\":true,\"all_16_stop_flag_combinations\":true,\"partial_get_unwinds_reverse_order\":true,\"unproven_exposed_mapping_never_released\":true}\n",assertions,cases);
 return 0;
}
