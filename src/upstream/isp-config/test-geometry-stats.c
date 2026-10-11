/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-frame-fields.h"
#ifdef SP11_REFERENCE
#include "reference.h"
#endif
static unsigned int geometry_cases, grid_cases;
static u32 rd(const u8 *p)
{
	return p[0] | (u32)p[1] << 8 | (u32)p[2] << 16 | (u32)p[3] << 24;
}
static void untouched(const u8 *p, size_t n)
{
	for (size_t i = 0; i < n; i++) assert(p[i] == 0xa5);
}
static void geometry_case(struct sp11_geometry s)
{
	u8 out[136];
	memset(out, 0xa5, sizeof(out));
	assert(sp11_geometry_commands(out, sizeof(out), &s) == 0);
	geometry_cases++;
	for (unsigned int c = 0; c < 2; c++) {
		u32 base = c ? 0x9a60 : 0x9860, d = c ? 2 : 1;
		assert(rd(out + 48 * c) == 0x0300000a);
		assert(rd(out + 48 * c + 4) == base);
		assert(rd(out + 48 * c + 16) == ((s.input_width - 1) << 16 | (s.input_height - 1)));
		assert(rd(out + 100 + 16 * c) == (c ? 0x9e68U : 0x9c68U));
		assert(rd(out + 104 + 16 * c) == s.output_height / d - 1);
		assert(rd(out + 108 + 16 * c) == s.output_width / d - 1);
#ifdef SP11_REFERENCE
		struct e006q_mnds23_state old = {
			.input_width=s.input_width, .input_height=s.input_height,
			.luma_width=s.output_width, .luma_height=s.output_height,
			.chroma_h_div=2, .chroma_v_div=2, .enabled=true,
			.pre_crop={.last_pixel=s.input_width-1, .last_line=s.input_height-1},
		};
		struct e006p_rear_geometry crop = {.full={
			.luma={.last_pixel=s.output_width-1, .last_line=s.output_height-1},
			.chroma={.last_pixel=s.output_width/2-1, .last_line=s.output_height/2-1},
		}};
		u32 v;
		for (unsigned int i = 0; i < 10; i++) {
			assert(e006q_mnds23_lookup(&old, base+4*i, &v) == 0);
			assert(v == rd(out+48*c+8+4*i));
		}
		for (unsigned int i = 0; i < 2; i++) {
			assert(e006p_crop12_lookup(&crop, (c?0x9e68:0x9c68)+4*i, &v) == 0);
			assert(v == rd(out+104+16*c+4*i));
		}
#endif
	}
	untouched(out+128, 8);
}
static struct sp11_bg_config grid(u32 width, u32 height)
{
	struct sp11_bg_config s = {.width=width, .height=height, .columns=32, .rows=32,
		.threshold_r=0x3ffff, .threshold_b=123, .threshold_gr=234, .threshold_gb=345,
		.black_level=17, .y_weight_q4={4,8,4}, .enabled=true};
	return s;
}
static void grid_case(struct sp11_bg_config s, u32 aw, u32 ah)
{
	u8 out[88];
	u32 cw=(s.width/s.columns)&~1U, ch=(s.height/s.rows)&~1U;
	for (unsigned int k=0; k<3; k++) {
		memset(out, 0xa5, sizeof(out));
		assert(sp11_bg_commands(out, sizeof(out), (enum sp11_bg_kind)k, aw, ah, &s) == 0);
		grid_cases++;
		assert(rd(out)==0x03000012);
		assert(rd(out+4)==(k==0?0xb060U:k==1?0xb660U:0xb860U));
		assert(rd(out+20)==((s.columns-1)<<16|s.left));
		assert(rd(out+24)==cw-1 && rd(out+32)==ch-1);
		assert((u64)cw*s.columns+s.left<=aw && (u64)ch*s.rows+s.top<=ah);
		assert(rd(out+40)==s.threshold_gr<<14);
		assert(rd(out+44)==s.threshold_r<<14);
		for (unsigned int i=13; i<18; i++) assert(rd(out+8+4*i)==0U-(s.black_level<<13));
#ifdef SP11_REFERENCE
		struct e006w_aecbe17_state old={
			.h_num=s.columns,.v_num=s.rows,.h_offset=s.left,.v_offset=s.top,
			.region_width=cw,.region_height=ch,.threshold_r=s.threshold_r,
			.threshold_b=s.threshold_b,.threshold_gr=s.threshold_gr,.threshold_gb=s.threshold_gb,
			.black_level_offset=s.black_level,.quad_sync_enable=s.quad_sync,.enabled=s.enabled};
		memcpy(old.y_weight_q4,s.y_weight_q4,3);
		for(unsigned int i=0;i<18;i++) {
			u32 v, reg=(k==0?0xb060:k==1?0xb660:0xb860)+4*i;
			int ret=k==0?e006w_aecbe17_lookup(&old,reg,&v):
				k==1?e006x_tintless_bg17_lookup(&old,reg,&v):e006y_awbbg17_lookup(&old,reg,&v);
			assert(ret==0 && v==rd(out+8+4*i));
		}
#endif
		untouched(out+80,8);
	}
}
static void valid_cases(void)
{
	geometry_case((struct sp11_geometry){3840,2160,2560,1440});
	geometry_case((struct sp11_geometry){4064,2286,3840,2160});
	for(u32 ratio=1;ratio<=64;ratio++)
		geometry_case((struct sp11_geometry){256*ratio,128*ratio,256,128});
	for(u32 width=258;width<514;width+=2)
		geometry_case((struct sp11_geometry){width,514,256,258});
	/* All representable grid counts with supported physical cell dimensions. */
	for(u32 cols=1;cols<=64;cols++) for(u32 rows=1;rows<=64;rows++) {
		struct sp11_bg_config s=grid(cols*16+1,rows*18+1);
		s.columns=cols;s.rows=rows;s.left=2;s.top=4;
		s.threshold_r=(cols*4097)&0x3ffff;s.black_level=(rows*4097)&0x3ffff;
		s.quad_sync=cols&1;s.enabled=rows&1;
		grid_case(s,16384,16384);
	}
	grid_case(grid(3840,2160),3840,2160);
	grid_case(grid(4064,2286),4064,2286);
	struct sp11_bg_config s=grid(16384,16384);s.threshold_r=s.threshold_b=s.threshold_gr=s.threshold_gb=s.black_level=0x3ffff;
	s.y_weight_q4[0]=s.y_weight_q4[1]=s.y_weight_q4[2]=127;grid_case(s,16384,16384);
}
static void rejections(void)
{
	u8 out[600];struct sp11_geometry g={3840,2160,2560,1440};
	struct sp11_bg_config s=grid(3840,2160),bad;
	memset(out,0xa5,sizeof(out));
	assert(sp11_geometry_commands(out,127,&g)==-ENOSPC);
	assert(sp11_geometry_commands(NULL,sizeof(out),&g)==-EINVAL);
	assert(sp11_geometry_commands(out,sizeof(out),NULL)==-EINVAL);
#define GEOM_BAD(member,value) do {struct sp11_geometry b=g;b.member=value;assert(sp11_geometry_commands(out,sizeof(out),&b)<0);} while(0)
	GEOM_BAD(input_width,0);GEOM_BAD(input_height,2161);GEOM_BAD(input_width,16386);
	GEOM_BAD(output_width,3842);GEOM_BAD(output_height,2162);GEOM_BAD(output_width,2);
	GEOM_BAD(output_height,2);GEOM_BAD(output_width,0xffffffffU);
#undef GEOM_BAD
	assert(sp11_bg_commands(out,79,SP11_BG_AEC,3840,2160,&s)==-ENOSPC);
	assert(sp11_bg_commands(out,sizeof(out),(enum sp11_bg_kind)-1,3840,2160,&s)==-EINVAL);
	assert(sp11_bg_commands(out,sizeof(out),(enum sp11_bg_kind)3,3840,2160,&s)==-EINVAL);
#define GRID_BAD(member,value) do {bad=s;bad.member=value;assert(sp11_bg_commands(out,sizeof(out),SP11_BG_AEC,3840,2160,&bad)<0);}while(0)
	GRID_BAD(left,1);GRID_BAD(top,1);GRID_BAD(left,3840);GRID_BAD(top,2160);
	GRID_BAD(width,3842);GRID_BAD(height,2162);GRID_BAD(width,0xffffffffU);
	GRID_BAD(columns,0);GRID_BAD(rows,0);GRID_BAD(columns,65);GRID_BAD(rows,65);
	GRID_BAD(width,32*14);GRID_BAD(height,32*14);GRID_BAD(columns,1);
	GRID_BAD(threshold_r,0x40000);GRID_BAD(threshold_b,0x40000);
	GRID_BAD(threshold_gr,0x40000);GRID_BAD(threshold_gb,0x40000);GRID_BAD(black_level,0x40000);
	GRID_BAD(y_weight_q4[2],128);
#undef GRID_BAD
	assert(sp11_bg_validate(&s,0,2160)<0);assert(sp11_bg_validate(&s,16385,2160)<0);
	struct sp11_bg_config set[3]={s,s,s};set[2].threshold_b=0x40000;
	assert(sp11_bg_set_commands(out,sizeof(out),3840,2160,set)==-ERANGE);
	untouched(out,sizeof(out));
	union {struct sp11_frame_fields s;u8 out[600];} alias;
	memset(&alias,0xa5,sizeof(alias));
	assert(sp11_geometry_commands(alias.out,600,&alias.s.geometry)==-EINVAL);
	assert(sp11_bg_commands(alias.out,600,SP11_BG_AEC,3840,2160,alias.s.bg)==-EINVAL);
	assert(sp11_bg_set_commands(alias.out,600,3840,2160,alias.s.bg)==-EINVAL);
	assert(sp11_frame_fields_commands(alias.out,600,&alias.s)==-EINVAL);
	untouched(alias.out,sizeof(alias.out));
}
static void composition(void)
{
	u8 out[600],part[240];
	struct sp11_frame_fields s={.geometry={3840,2160,2560,1440},
		.cst={601,117,306,-339,512,-173,-429,-83,512},
		.ccm={128,0,0,0,128,0,0,0,128},.output_bits=8};
	for(unsigned int i=0;i<3;i++) s.bg[i]=grid(3840,2160);
	assert(SP11_FRAME_FIELDS_BYTES==568);
	memset(out,0xa5,sizeof(out));
	assert(sp11_frame_fields_commands(out,sizeof(out),&s)==0);
	assert(sp11_geometry_commands(part,sizeof(part),&s.geometry)==0);
	assert(memcmp(part,out+200,128)==0);
	assert(sp11_bg_set_commands(part,sizeof(part),3840,2160,s.bg)==0);
	assert(memcmp(part,out+328,240)==0);
	untouched(out+568,32);
	/* Walk commands: exactly 112 unique owned registers, no duplicates. */
	u32 regs[112];size_t pos=0,n=0;
	while(pos<568){u32 count=rd(out+pos)&0xffff,base=rd(out+pos+4);
		assert(rd(out+pos)>>24==3 && count>0);
		for(u32 j=0;j<count;j++){u32 reg=base+4*j;assert(n<112);
			for(size_t k=0;k<n;k++)
				assert(regs[k]!=reg);
			regs[n++]=reg;}
		pos+=8+count*4;}
	assert(pos==568 && n==112);
	memset(out,0xa5,sizeof(out));s.bg[2].y_weight_q4[2]=128;
	assert(sp11_frame_fields_commands(out,sizeof(out),&s)==-ERANGE);
	s.bg[2].y_weight_q4[2]=4;s.geometry.output_width=4000;
	assert(sp11_frame_fields_commands(out,sizeof(out),&s)==-ERANGE);
	s.geometry.output_width=2560;s.ccm[8]=2048;
	assert(sp11_frame_fields_commands(out,sizeof(out),&s)==-ERANGE);
	s.ccm[8]=128;
	assert(sp11_frame_fields_commands(out,567,&s)==-ENOSPC);
	assert(sp11_frame_fields_commands(out,sizeof(out),NULL)==-EINVAL);
	untouched(out,sizeof(out));
}
int main(void)
{
	valid_cases();rejections();composition();
	printf("PASS geometry_cases=%u grid_cases=%u; bounds/atomic rejection/112-field composition",geometry_cases,grid_cases);
#ifdef SP11_REFERENCE
	printf("; unchanged pinned semantic references");
#endif
	puts("");return 0;
}
