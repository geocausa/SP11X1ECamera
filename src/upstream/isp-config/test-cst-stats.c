/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-frame-fields.h"
#ifdef SP11_REFERENCE
#include "cst-reference.h"
#endif
static unsigned int cst_cases,rs_cases,bhist_cases;
static u32 rd(const u8 *p)
{
	return p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;
}
static void untouched(const u8 *p,size_t n)
{
	for(size_t i=0;i<n;i++) assert(p[i]==0xa5);
}
static struct sp11_cst_config cst(void)
{
	struct sp11_cst_config s={.matrix={601,117,306,-339,512,-173,-429,-83,512},
		.maximum={4095,4095,4095},.enabled=true};
	return s;
}
static void cst_case(struct sp11_cst_config s)
{
	u8 out[100],coeff[48];
	memset(out,0xa5,sizeof(out));
	assert(sp11_cst_commands(out,sizeof(out),&s)==0);cst_cases++;
	assert(rd(out)==0x03000001 && rd(out+4)==0x6160 && rd(out+8)==(s.enabled?1U:0U));
	assert(rd(out+12)==0x03000012 && rd(out+16)==0x6168);
	assert(sp11_front_cst_commands(coeff,sizeof(coeff),s.matrix)==0);
	for(unsigned int i=0;i<3;i++) {
		u8 *p=out+20+24*i;
		assert(rd(p)==rd(coeff+16*i+8) && rd(p+4)==rd(coeff+16*i+12));
		assert(rd(p+8)==(((u32)s.offset[i]&0x1fff)<<19));
		assert(rd(p+12)==(((u32)s.auxiliary[i]&0x1fff)<<19));
		assert(rd(p+16)==s.minimum[i]<<20 && rd(p+20)==s.maximum[i]<<20);
		assert(!(rd(p+8)&0x7ffff) && !(rd(p+12)&0x7ffff));
	}
#ifdef SP11_REFERENCE
	struct e006r_cst12_state old={.enabled=s.enabled,
		.c00=s.minimum[0],.c10=s.minimum[1],.c20=s.minimum[2],
		.c01=s.maximum[0],.c11=s.maximum[1],.c21=s.maximum[2],
		.m00=s.matrix[0],.m01=s.matrix[1],.m02=s.matrix[2],
		.m10=s.matrix[3],.m11=s.matrix[4],.m12=s.matrix[5],
		.m20=s.matrix[6],.m21=s.matrix[7],.m22=s.matrix[8],
		.o0=s.offset[0],.o1=s.offset[1],.o2=s.offset[2],
		.s0=s.auxiliary[0],.s1=s.auxiliary[1],.s2=s.auxiliary[2]};
	u32 v;assert(e006r_cst12_lookup(&old,0x6160,&v)==0 && v==rd(out+8));
	for(unsigned int i=0;i<18;i++) {
		assert(e006r_cst12_lookup(&old,0x6168+4*i,&v)==0);
		assert(v==rd(out+20+4*i));
	}
#endif
	untouched(out+92,8);
}
static void rs_case(struct sp11_rs_config s,u32 aw,u32 ah)
{
	u8 out[40];u32 cw=s.width/s.columns,ch=(s.height/s.rows)&~1U;
	memset(out,0xa5,sizeof(out));
	assert(sp11_rs_commands(out,sizeof(out),aw,ah,&s)==0);rs_cases++;
	assert(rd(out)==0x03000001 && rd(out+4)==0xbe60);
	assert(rd(out+12)==0x03000003 && rd(out+16)==0xbe68);
	assert(rd(out+20)==(s.top<<16|s.left));
	assert(rd(out+24)==((s.rows-1)<<16|(s.columns-1)));
	assert(rd(out+28)==((ch-1)<<16|(cw-1)));
	/* Independent bit-count oracle, no call to the production shift helper. */
	u32 area=cw*ch;unsigned int bits=0;
	for(unsigned int b=0;b<32;b++) if(area&(1U<<b)) bits=b+1;
	assert(rd(out+8)==(1U|(s.color_conversion?16U:0U)|((bits>4?bits-4:0)<<8)));
	assert((u64)cw*s.columns+s.left<=aw && (u64)ch*s.rows+s.top<=ah);
#ifdef SP11_REFERENCE
	struct e006v_rs14_state old={.h_num=s.columns,.v_num=s.rows,
		.region_width=cw,.region_height=ch,.h_offset=s.left,.v_offset=s.top,
		.enabled=true,.color_conversion=s.color_conversion};
	u32 v;assert(e006v_rs14_lookup(&old,0xbe60,&v)==0 && v==rd(out+8));
	for(unsigned int i=0;i<3;i++) {
		assert(e006v_rs14_lookup(&old,0xbe68+4*i,&v)==0);
		assert(v==rd(out+20+4*i));
	}
#endif
	untouched(out+32,8);
}
static void bhist_case(struct sp11_bhist_geometry s,u32 aw,u32 ah)
{
	u8 out[20];memset(out,0xa5,sizeof(out));
	assert(sp11_bhist_geometry_commands(out,sizeof(out),aw,ah,&s)==0);bhist_cases++;
	assert(rd(out)==0x03000001 && rd(out+4)==0xb26c);
	u32 word=rd(out+8);
	assert(((word&0x1fff)+1)*2==s.width);
	assert((((word>>16)&0x1fff)+1)*2==s.height);
	assert(!(word&0xe000e000U));
#ifdef SP11_REFERENCE
	struct e006u_bhist16_state old={s.width,s.height};u32 v;
	assert(e006u_bhist16_lookup(&old,0xb26c,&v)==0 && v==word);
#endif
	untouched(out+12,8);
}
static void vectors(void)
{
	struct sp11_cst_config s=cst();cst_case(s);s.enabled=false;cst_case(s);
	for(int v=-4096;v<=4095;v++) {
		s.offset[0]=v;s.offset[1]=-v-1;s.offset[2]=v;
		s.auxiliary[0]=-v-1;s.auxiliary[1]=v;s.auxiliary[2]=-v-1;cst_case(s);
	}
	for(u32 v=0;v<4096;v++) {
		s.minimum[0]=s.maximum[0]=v;s.minimum[1]=v;s.maximum[1]=4095;
		s.minimum[2]=0;s.maximum[2]=v;cst_case(s);
	}
	for(u32 cols=1;cols<=16;cols++) for(u32 rows=1;rows<=1024;rows++)
		rs_case((struct sp11_rs_config){2,2,cols*17+1,rows*2+1,cols,rows,(rows&1)!=0},16384,16384);
	for(u32 w=2;w<=8192;w*=2) for(u32 h=2;h<=16;h+=2)
		rs_case((struct sp11_rs_config){0,0,w,h,1,1,false},16384,16384);
	rs_case((struct sp11_rs_config){0,0,3840,2160,16,1024,true},3840,2160);
	rs_case((struct sp11_rs_config){0,0,4064,2286,16,1024,true},4064,2286);
	for(u32 w=4;w<=16384;w+=2) bhist_case((struct sp11_bhist_geometry){w,2},16384,16384);
	for(u32 h=2;h<=16384;h+=2) bhist_case((struct sp11_bhist_geometry){4,h},16384,16384);
	bhist_case((struct sp11_bhist_geometry){3840,2160},3840,2160);
	bhist_case((struct sp11_bhist_geometry){4064,2286},4064,2286);
}
static void rejection(void)
{
	u8 out[688];memset(out,0xa5,sizeof(out));
	struct sp11_cst_config s=cst(),bad;
#define CST_BAD(member,value) do {bad=s;bad.member=value;assert(sp11_cst_commands(out,sizeof(out),&bad)<0);}while(0)
	CST_BAD(matrix[8],4096);CST_BAD(offset[2],-4097);CST_BAD(offset[2],4096);
	CST_BAD(auxiliary[2],-4097);CST_BAD(auxiliary[2],4096);CST_BAD(maximum[2],4096);
	CST_BAD(minimum[2],4096);bad=s;bad.minimum[2]=1;bad.maximum[2]=0;
	assert(sp11_cst_commands(out,sizeof(out),&bad)<0);
#undef CST_BAD
	assert(sp11_cst_commands(out,91,&s)==-ENOSPC);
	assert(sp11_cst_commands(out,sizeof(out),NULL)==-EINVAL);
	struct sp11_rs_config rs={0,0,3840,2160,16,1024,true},br;
#define RS_BAD(member,value) do {br=rs;br.member=value;assert(sp11_rs_commands(out,sizeof(out),3840,2160,&br)<0);}while(0)
	RS_BAD(left,1);RS_BAD(top,1);RS_BAD(left,8192);RS_BAD(width,0xffffffffU);
	RS_BAD(height,0xffffffffU);RS_BAD(columns,0);RS_BAD(columns,17);RS_BAD(rows,0);RS_BAD(rows,1025);
	RS_BAD(width,16);RS_BAD(height,1024);RS_BAD(rows,1);RS_BAD(width,3842);RS_BAD(top,2160);
#undef RS_BAD
	assert(sp11_rs_commands(out,31,3840,2160,&rs)==-ENOSPC);
	assert(sp11_rs_commands(out,sizeof(out),16385,2160,&rs)<0);
	assert(sp11_rs_commands(out,sizeof(out),0,2160,&rs)<0);
	struct sp11_bhist_geometry bh={3840,2160};
	assert(sp11_bhist_geometry_commands(out,11,3840,2160,&bh)==-ENOSPC);
	for(u32 w=0;w<4;w++){bh.width=w;assert(sp11_bhist_geometry_commands(out,sizeof(out),3840,2160,&bh)<0);}
	bh.width=3841;assert(sp11_bhist_geometry_commands(out,sizeof(out),3840,2160,&bh)<0);
	bh.width=16386;assert(sp11_bhist_geometry_commands(out,sizeof(out),16384,16384,&bh)<0);
	bh.width=3840;bh.height=2161;assert(sp11_bhist_geometry_commands(out,sizeof(out),3840,2162,&bh)<0);
	untouched(out,sizeof(out));
	union {u8 out[688];struct sp11_frame_fields s;} alias;
	memset(&alias,0xa5,sizeof(alias));
	assert(sp11_cst_commands((u8 *)&alias.s.cst,sizeof(alias.s.cst),&alias.s.cst)==-ENOSPC);
	assert(sp11_cst_commands((u8 *)&alias.s.cst,92,&alias.s.cst)==-EINVAL);
	assert(sp11_rs_commands((u8 *)&alias.s.rs,32,3840,2160,&alias.s.rs)==-EINVAL);
	assert(sp11_bhist_geometry_commands((u8 *)&alias.s.bhist,12,3840,2160,&alias.s.bhist)==-EINVAL);
	untouched(alias.out,688);
}
static void composite_failure(void)
{
	u8 out[688];memset(out,0xa5,sizeof(out));
	struct sp11_frame_fields s={.geometry={3840,2160,2560,1440},
		.rs={0,0,3840,2160,16,1024,false},.bhist={3840,2160},
		.ccm={128,0,0,0,128,0,0,0,128},.output_bits=8};s.cst=cst();
	for(unsigned int i=0;i<3;i++) s.bg[i]=(struct sp11_bg_config){
		.width=3840,.height=2160,.columns=32,.rows=32,.enabled=true};
	s.bhist.height=2162;assert(sp11_frame_fields_commands(out,sizeof(out),&s)==-ERANGE);
	untouched(out,sizeof(out));s.bhist.height=2160;s.rs.rows=1;
	assert(sp11_frame_fields_commands(out,sizeof(out),&s)==-ERANGE);untouched(out,sizeof(out));
	s.rs.rows=1024;s.cst.maximum[2]=4096;
	assert(sp11_frame_fields_commands(out,sizeof(out),&s)==-ERANGE);untouched(out,sizeof(out));
}
int main(void)
{
	vectors();rejection();composite_failure();
	printf("PASS cst=%u rs=%u bhist_geometry=%u; sparse ownership/bounds/atomicity",cst_cases,rs_cases,bhist_cases);
#ifdef SP11_REFERENCE
	printf("; unchanged pinned MIT packers");
#endif
	puts("");return 0;
}
