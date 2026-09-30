/* SPDX-License-Identifier: MIT */
/* Host-only integration harness; allocators use malloc and synthetic IOVAs. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
typedef uint8_t u8; typedef int8_t s8;
typedef uint16_t u16; typedef int16_t s16;
typedef uint32_t u32; typedef int32_t s32;
typedef uint64_t u64; typedef int64_t s64;
typedef uint64_t dma_addr_t;
#define BIT(n) (1U << (n))
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define static_assert(expr) _Static_assert((expr), #expr)
#define __used __attribute__((used))
#define ALIGN(x,a) (((x)+(a)-1)&~((a)-1))
#define IS_ALIGNED(x,a) (!((x)&((a)-1)))
#define GFP_KERNEL 0
#define U32_MAX UINT32_MAX
#define min_t(t,a,b) ((t)(a) < (t)(b) ? (t)(a) : (t)(b))
#define max_t(t,a,b) ((t)(a) > (t)(b) ? (t)(a) : (t)(b))
static void memzero_explicit(void *p,size_t n) { volatile u8 *b=p;while(n--)*b++=0; }
static u32 get_unaligned_le32(const void *p) { const u8 *b=p;return (u32)b[0]|((u32)b[1]<<8)|((u32)b[2]<<16)|((u32)b[3]<<24); }
static void put_unaligned_le32(u32 v,void *p) { u8 *b=p;for(unsigned int i=0;i<4;i++)b[i]=(u8)(v>>(8*i)); }
struct device { int fixture; }; struct camss { struct device *dev; };
struct vfe_device { struct camss *camss; };
static bool vfe680_e004nt_rear_4k_target(struct vfe_device *v) { return v&&v->camss&&v->camss->dev&&v->camss->dev->fixture==1; }
static bool vfe680_x1e_dma_span_32bit(dma_addr_t a,size_t n) { return n&&a<=UINT32_MAX&&n-1<=UINT32_MAX-a; }
static void *kcalloc(size_t n,size_t size,int flag) { (void)flag;return calloc(n,size); }
static void *kzalloc(size_t n,int flag) { (void)flag;return calloc(1,n); }
static void kfree(void *p) { free(p); }
static void *dma_alloc_coherent(struct device *d,size_t n,dma_addr_t *a,int flag) {
    static dma_addr_t next=0x10000000;
    (void)d;(void)flag;*a=next;next+=ALIGN(n,0x1000);return calloc(1,n);
}
static void dma_free_coherent(struct device *d,size_t n,void *p,dma_addr_t a) { (void)d;(void)n;(void)a;free(p); }
/* PROVIDERS */
#define e008o_rear_packet_state e008o_rear_packet_semantics
struct e008o_rear_bootstrap { struct e008o_rear_packet_semantics packet[4]; u8 next_packet; bool initialized; };
/* BF_PROVIDER */
#undef e008o_rear_packet_state
#include "camss-e011ag-startup-compose.inc"

static unsigned int checks;
#define CHECK(expr) do { checks++; if(!(expr)) { fprintf(stderr,"CHECK failed line %d\n",__LINE__);abort(); } } while(0)
static bool zero(const void *p,size_t n) { const u8 *b=p;while(n--)if(*b++)return false;return true; }
static void crop_path(struct e006p_output_path *p,u16 w,u16 h) {
    *p=(struct e006p_output_path){.luma={0,0,(u16)(w-1),(u16)(h-1)},.chroma={0,0,(u16)(w/2-1),(u16)(h/2-1)},.bit_width=10,.enabled=true};
}
static struct e006w_aecbe17_state bg_fixture(u16 h,u16 v,u16 w,u16 height) {
    return (struct e006w_aecbe17_state){.h_num=h,.v_num=v,.region_width=(u16)((w/h)&~1U),.region_height=(u16)((height/v)&~1U),
        .threshold_r=0x3ffff,.threshold_b=0x3ffff,.threshold_gr=0x3ffff,.threshold_gb=0x3ffff,.enabled=true};
}
static void init_base(struct e008o_rear_packet_semantics base[4]) {
    struct e008o_rear_bootstrap *bf=calloc(1,sizeof(*bf)); CHECK(bf);bf->initialized=true;
    CHECK(e008t_rear_seed_bootstrap_bf(bf,4064,2286)==0);
    for(unsigned int p=0;p<4;p++) {
        struct e007d_rear_register_state *r=&base[p].regs;
        base[p]=bf->packet[p];
        base[p].request_id=100+p;
        r->scalar.epoch_kind=E006Z_EPOCH_STARTUP;r->scalar.startup_phase=p;r->scalar.request_id=100+p;
        for(unsigned int c=0;c<4;c++){r->scalar.demux_q10[c]=1024;r->scalar.pdpc_q12[c]=4096;}
        r->scalar.wb_b_q10=r->scalar.wb_r_q10=1024;
        crop_path(&r->geometry.full,3840,2160);crop_path(&r->geometry.ds4,960,540);crop_path(&r->geometry.ds16,240,136);
        r->mnds=(struct e006q_mnds23_state){.input_width=4064,.input_height=2286,.luma_width=3840,.luma_height=2160,
            .chroma_h_div=2,.chroma_v_div=2,.pre_crop={0,0,4063,2285},.enabled=true};
        /* CST_SOURCE */
        r->bc101.enabled=false; /* E006s selected rear tuning disables BC101. */
        r->bhist=(struct e006u_bhist16_state){p?4064:3658,p?2286:2058};
        r->rs=(struct e006v_rs14_state){.h_num=16,.v_num=1024,.region_width=254,.region_height=2,.enabled=true};
        r->aec_be=bg_fixture(64,48,p?4064:3658,p?2286:2058);
        r->awb_bg=r->aec_be;r->tintless_bg=bg_fixture(32,24,4064,2286);
        CHECK(e007w_period_cfg_state_init(&r->period,1)==0);
        /* Explicit host-only completion of an UNUSED cold gamma state.
         * Packet0's hardware gamma enable stays zero and selector2 is absent.
         * This is not a Windows cold gamma policy or a clean bootstrap closure. */
        if(!p) { struct e007e_bf_dmi_state *d=e008t_rear_bf_dmi(&base[p].dmi);
            memcpy(d->gamma,e008t_normal_gamma,sizeof(d->gamma));d->gamma_valid=true; }
    }
    free(bf);
}
static void read_exact(void *p,size_t n) { CHECK(fread(p,1,n,stdin)==n); }
static void read_sources(struct e011ae_rear_startup_bpc_source *b,struct e011z_rear_startup_adaptive_wire *w) {
    for(unsigned int p=0;p<3;p++) {
        u8 wire[34]; struct e007a_bpcabf411_calc_state *s=&b->common[p];
        read_exact(wire,sizeof(wire));size_t o=0;
        for(unsigned int i=0;i<2;i++,o+=2)s->signed10[i]=(s16)((u16)wire[o]|((u16)wire[o+1]<<8));
        for(unsigned int i=0;i<2;i++,o+=2)s->unsigned9[i]=(u16)wire[o]|((u16)wire[o+1]<<8);
        memcpy(s->nibble4,wire+o,2);o+=2;memcpy(s->byte_group0,wire+o,8);o+=8;
        memcpy(s->byte_group1,wire+o,8);o+=8;memcpy(s->nibble_group,wire+o,8);
        b->source_request_id[p]=p;
    }
    read_exact(w->lsc_selector1,sizeof(w->lsc_selector1));read_exact(w->lsc_selector2,sizeof(w->lsc_selector2));read_exact(w->gtm,sizeof(w->gtm));CHECK(fgetc(stdin)==EOF);
}
static void outputs_zero(struct e008l_rear_command_set *commands) {
    for(unsigned int p=0;p<4;p++) { struct e007y_rear_startup_output *o=&commands->packet[p].out;
        CHECK(zero(o->main,o->main_bytes));CHECK(zero(o->wrapper,o->wrapper_bytes));CHECK(!o->bl_count);
        CHECK(zero(o->dynamic,sizeof(*o->dynamic)));
        for(size_t i=0;i<o->dmi_count;i++)CHECK(zero(o->dmi[i].cpu,o->dmi[i].bytes));
    }
}
static void rejected(struct e008o_rear_semantic_set *s,struct e008o_rear_semantic_set *work,struct e008o_rear_packet_semantics *base,
    struct e011ae_rear_startup_bpc_source *b,struct e011z_rear_startup_adaptive_wire *w,struct e008l_rear_command_set *commands) {
    CHECK(e011ag_rear_compose_startup(s,work,base,b,w,commands)<0);
    CHECK(zero(s,sizeof(*s)));CHECK(zero(work,sizeof(*work)));outputs_zero(commands);
}
static void write_private(const char *dir,const char *kind,unsigned int p,unsigned int i,const void *data,size_t n) {
    char name[4096];CHECK(snprintf(name,sizeof(name),"%s/p%u-%s-%u.bin",dir,p,kind,i)>0);
    FILE *f=fopen(name,"wb");CHECK(f);CHECK(fwrite(data,1,n,f)==n);CHECK(fclose(f)==0);
}
int main(int argc,char **argv) {
    struct device dev={1};struct camss camss={&dev};struct vfe_device vfe={&camss};
    struct e008o_rear_packet_semantics *base=calloc(4,sizeof(*base)),*saved=calloc(4,sizeof(*saved));
    struct e008o_rear_semantic_set *s=calloc(1,sizeof(*s)),*work=calloc(1,sizeof(*work));
    struct e011ae_rear_startup_bpc_source b={0};struct e011z_rear_startup_adaptive_wire *w=calloc(1,sizeof(*w));
    struct e008l_rear_command_set commands={0};
    CHECK(base&&saved&&s&&work&&w);init_base(base);memcpy(saved,base,4*sizeof(*base));read_sources(&b,w);
    CHECK(e008l_rear_command_alloc(&vfe,&commands)==0);
    CHECK(e011ag_rear_compose_startup(s,work,base,&b,w,&commands)==0);
    CHECK(s->sealed&&zero(work,sizeof(*work)));CHECK(!commands.hardware_exposed);CHECK(memcmp(base,saved,4*sizeof(*base))==0);
    unsigned int reg_counts[4]={0},dmi_counts[4]={0};size_t payload_bytes=0;bool cold_gamma=false;
    for(unsigned int p=0;p<4;p++) {
        struct e007y_rear_startup_output *o=&commands.packet[p].out;
        CHECK(s->packet[p].ready);CHECK(s->packet[p].request_id==100+p);CHECK(!commands.packet[p].submitted);
        CHECK(o->bl_count==(p?6:4));CHECK(zero(o->dynamic,sizeof(*o->dynamic)));
        for(size_t off=0;off<o->main_bytes;) {
            u32 h=get_unaligned_le32(o->main+off),op=h>>24;
            if(op==3) { reg_counts[p]+=h&0xffff;off+=8+4*(h&0xffff); }
            else { CHECK(op==1||op==10||op==11);u32 ctl=get_unaligned_le32(o->main+off+8);
                if(!p&&(ctl&0xffff)==0xbc08&&(ctl>>24)==2)cold_gamma=true;
                payload_bytes+=(h&0xffff)+1;dmi_counts[p]++;off+=12; }
        }
        CHECK(dmi_counts[p]==o->dmi_count);
        if(argc==2) { write_private(argv[1],"main",p,0,o->main,o->main_bytes);
            for(size_t i=0;i<o->dmi_count;i++)write_private(argv[1],"dmi",p,(unsigned int)i,o->dmi[i].cpu,o->dmi[i].bytes); }
    }
    CHECK(!cold_gamma);
    /* Source-preserving value copy must rebase callbacks onto the final set. */
    memset(work,0xa5,sizeof(*work));
    CHECK(e008o_rear_validate_semantic_set(s)==0);
    CHECK(e008o_rear_materialize_commands(s,&commands)==0);
    memzero_explicit(work,sizeof(*work));
    unsigned int negatives=0;
    for(unsigned int p=0;p<4;p++) {
        base[p].regs.scalar.startup_phase=4;rejected(s,work,base,&b,w,&commands);base[p]=saved[p];negatives++;
        base[p].regs.scalar.request_id++;rejected(s,work,base,&b,w,&commands);base[p]=saved[p];negatives++;
        base[p].regs.period.valid_mask=0;rejected(s,work,base,&b,w,&commands);base[p]=saved[p];negatives++;
        e008t_rear_bf_dmi(&base[p].dmi)->roi_count=24;rejected(s,work,base,&b,w,&commands);base[p]=saved[p];negatives++;
        e008t_rear_bf_dmi(&base[p].dmi)->gamma_valid=false;rejected(s,work,base,&b,w,&commands);base[p]=saved[p];negatives++;
    }
    /* Late packet failures must clear all already-produced earlier packets. */
    base[3].regs.rs.region_height=3;rejected(s,work,base,&b,w,&commands);base[3]=saved[3];negatives++;
    e008t_rear_bf_dmi(&base[3].dmi)->roi[0].left=0xffff;rejected(s,work,base,&b,w,&commands);base[3]=saved[3];negatives++;
    b.source_request_id[2]=3;rejected(s,work,base,&b,w,&commands);b.source_request_id[2]=2;negatives++;
    s16 keep=b.common[2].signed10[0];b.common[2].signed10[0]=512;rejected(s,work,base,&b,w,&commands);b.common[2].signed10[0]=keep;negatives++;

    CHECK(e011ag_rear_compose_startup(s,work,base,&b,w,&commands)==0);
    for(unsigned int p=0;p<4;p++) {
        size_t bytes=commands.packet[p].out.dmi[0].bytes;
        commands.packet[p].out.dmi[0].bytes=SIZE_MAX;
        CHECK(e011ag_rear_compose_startup(s,work,base,&b,w,&commands)==-EINVAL);
        CHECK(s->sealed&&commands.packet[0].out.bl_count==4);
        commands.packet[p].out.dmi[0].bytes=bytes;negatives++;
    }
    CHECK(e011ag_rear_compose_startup(s,s,base,&b,w,&commands)==-EINVAL);CHECK(s->sealed);negatives++;
    CHECK(e011ag_rear_compose_startup(s,work,s->packet,&b,w,&commands)==-EINVAL);CHECK(s->sealed);negatives++;
    commands.hardware_exposed=true;
    CHECK(e011ag_rear_compose_startup(s,work,base,&b,w,&commands)==-EINVAL);CHECK(s->sealed&&commands.packet[0].out.bl_count==4);negatives++;
    commands.hardware_exposed=false;commands.packet[3].submitted=true;
    CHECK(e011ag_rear_compose_startup(s,work,base,&b,w,&commands)==-EINVAL);CHECK(s->sealed);negatives++;
    commands.packet[3].submitted=false;
    CHECK(e008o_rear_runtime_authorization()==-EOPNOTSUPP);CHECK(e011ag_rear_runtime_authorization()==-EOPNOTSUPP);
    CHECK(e008l_rear_command_release(&vfe,&commands,false)==0);
    printf("{\"status\":\"PASS\",\"assertions\":%u,\"negative_cases\":%u,\"register_writes\":[%u,%u,%u,%u],\"dmi_slots\":[%u,%u,%u,%u],\"dmi_payload_bytes\":%zu,\"cold_bf_gamma_emitted\":false}\n",
        checks,negatives,reg_counts[0],reg_counts[1],reg_counts[2],reg_counts[3],dmi_counts[0],dmi_counts[1],dmi_counts[2],dmi_counts[3],payload_bytes);
    free(base);free(saved);free(s);free(work);free(w);return 0;
}
