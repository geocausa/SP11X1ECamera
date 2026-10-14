/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-channel-bayer0.h"
#include "rear-neutral-scalar.h"
#include "native-front-params.h"
static const struct sp11_front_cold_policy policy = {
	{ SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440 },
	SP11_BLS121_IFE18_SELECTOR,0
};
static void rejected(struct sp11_front_channel_gain_state s,
	struct sp11_front_cold_policy p, size_t capacity, int code)
{
	u8 out[72],old[72];memset(out,0xa5,sizeof(out));memcpy(old,out,sizeof(old));
	assert(sp11_front_channel_bayer0_config(out,capacity,&p,&s)==code);
	assert(memcmp(old,out,sizeof(out))==0);
}
static u32 get32(const u8 *p)
{
	return (u32)p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;
}
int main(void)
{
	struct sp11_front_channel_gain_state s={{1024,1024,1024,1024},{0},{0}};
	struct sp11_front_cold_policy p=policy;
	u8 out[72],oracle[56],old[72];unsigned i,j,cases=0,producer=0;
	for(i=0;i<56;i++) rejected(s,p,i,-ENOSPC);
	for(i=0;i<4;i++) {
		struct sp11_front_channel_gain_state t=s;
		t.gain_q10[i]=0;rejected(t,p,56,-ERANGE);
		t=s;t.gain_q10[i]=0x8000;rejected(t,p,56,-ERANGE);
		t=s;t.black_in14[i]=0x4000;rejected(t,p,56,-ERANGE);
		t=s;t.black_out14[i]=0x4000;rejected(t,p,56,-ERANGE);
	}
	p.domain.sensor_height=2640;rejected(s,p,56,-EOPNOTSUPP);
	p=policy;p.domain.calibration=0;rejected(s,p,56,-EOPNOTSUPP);
	p=policy;p.bls_selector=199;rejected(s,p,56,-EOPNOTSUPP);
	p=policy;p.bls_fraction=1;rejected(s,p,56,-EOPNOTSUPP);p=policy;
	assert(sp11_front_channel_bayer0_config(0,56,&p,&s)==-EINVAL);
	memset(out,0xa5,sizeof(out));memcpy(old,out,sizeof(old));
	assert(sp11_front_channel_bayer0_config(out,56,0,&s)==-EINVAL);
	assert(sp11_front_channel_bayer0_config(out,56,&p,0)==-EINVAL);
	assert(memcmp(old,out,sizeof(old))==0);
	union { u8 b[128]; struct sp11_front_channel_gain_state state; } alias;
	alias.state=s;u8 before[128];memcpy(before,alias.b,128);
	assert(sp11_front_channel_bayer0_config(alias.b,128,&p,&alias.state)==-EINVAL);
	assert(memcmp(before,alias.b,128)==0);
	union { u8 b[128]; struct sp11_front_cold_policy policy; } pa;
	pa.policy=p;memcpy(before,pa.b,128);
	assert(sp11_front_channel_bayer0_config(pa.b,128,&pa.policy,&s)==-EINVAL);
	assert(memcmp(before,pa.b,128)==0);
	u32 kind,words[12];float values[5];
	while(fread(&kind,sizeof(kind),1,stdin)==1) {
		assert(fread(values,sizeof(values),1,stdin)==1);
		assert(fread(words,sizeof(words),1,stdin)==1);
		assert(fread(oracle,sizeof(oracle),1,stdin)==1);
		for(i=0;i<4;i++) {s.gain_q10[i]=words[i];s.black_in14[i]=words[4+i];s.black_out14[i]=words[8+i];}
		if(kind==1) {
			struct e012k_rear_scalar_input in={0};struct e012k_rear_scalar_output derived;
			in.demux_gain=values[0];for(i=0;i<4;i++) in.channel[i]=values[1+i];
			in.awb_g=in.awb_b=in.awb_r=in.predictive_gain=1;in.bayer=2;
			assert(e012k_rear_scalar_calculate(&in,&derived)==0);
			for(i=0;i<4;i++) assert(derived.demux_q10[i]==words[i]);
			producer++;
		} else assert(kind==2);
		memset(out,0xa5,sizeof(out));
		assert(sp11_front_channel_bayer0_config(out,sizeof(out),&p,&s)==0);
		assert(memcmp(out,oracle,56)==0);
		for(i=56;i<72;i++) assert(out[i]==0xa5);
		/* Actual existing per-frame typed bridge; reuse its gain packing. */
		u8 wire[64]={0};u32 table[9][6]={{0}};
		sp11_cdm_put32(wire,NATIVE_FRONT_PARAMS_MAGIC);
		wire[4]=1;wire[6]=64;wire[8]=5;wire[16]=NATIVE_FRONT_PARAMS_DEMUX;
		for(i=0;i<4;i++) {wire[24+2*i]=s.gain_q10[i];wire[25+2*i]=s.gain_q10[i]>>8;}
		assert(native_front_params_apply(wire,64,table)==0);
		assert(get32(out+16)==table[0][0] && get32(out+20)==table[0][1]);
		cases++;
	}
	assert(feof(stdin)&&cases&&producer);
	p=policy;s=(struct sp11_front_channel_gain_state){{1024,1024,1024,1024},{0},{0}};
	memset(out,0xa5,sizeof(out));assert(sp11_front_channel_bayer0_cold_config(out,72,&p)==0);
	const u32 cold[14]={0x0300000c,0x3b68,0xc9,0xac,0x04000400,0x04000400,0,0,0,0,0,0,0,0};
	for(j=0;j<14;j++) assert(get32(out+4*j)==cold[j]);
	printf("{\"native_vectors\":%u,\"prior_producer_vectors\":%u,\"status\":\"PASS\"}\n",cases,producer);
	return 0;
}
