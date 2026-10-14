/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-cold-fields.h"
static u32 read32(const u8 *p)
{
	return (u32)p[0] | (u32)p[1]<<8 | (u32)p[2]<<16 | (u32)p[3]<<24;
}
static void rejected(struct sp11_front_cold_policy p, int error, size_t size)
{
	u8 b[80], prior[80];
	memset(b, 0xa5, sizeof(b)); memcpy(prior, b, sizeof(b));
	assert(sp11_front_cold_fields(b, size, &p)==error);
	assert(memcmp(b, prior, sizeof(b))==0);
}
int main(void)
{
	struct sp11_front_cold_policy p = {
		{ SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440 },
		SP11_BLS121_IFE18_SELECTOR,0
	}, q;
	const u32 reg[5]={0x3d60,0x4760,0x5460,0x5a60,0x4b68};
	u8 out[80];
	u32 x=0xa5a5a5a5U, i;
	unsigned int cases=0;
	for (i=0;i<=0x3ffffU;i++) {
		assert(sp11_bls121_ife18_offset(i,&x)==0);
		assert(x==(i<<14)); assert((x&0x3fffU)==0); cases++;
	}
	x=0x12345678;
	assert(sp11_bls121_ife18_offset(0x40000,&x)==-ERANGE && x==0x12345678);
	assert(sp11_bls121_ife18_offset(0xffffffff,&x)==-ERANGE && x==0x12345678);
	assert(sp11_bls121_ife18_offset(0,0)==-EINVAL);
	memset(out,0xa5,sizeof(out));
	assert(sp11_front_cold_fields(out,sizeof(out),&p)==0);
	for(i=0;i<5;i++) {
		assert(read32(out+i*12)==0x03000001);
		assert(read32(out+i*12+4)==reg[i]);
		assert(read32(out+i*12+8)==(i==4?0x06710000U:0));
		assert(reg[i]!=0x4960 && reg[i]!=0x4b60);
	}
	for(i=60;i<80;i++) assert(out[i]==0xa5);
	for(i=0;i<60;i++) rejected(p,-ENOSPC,i);
	q=p;q.domain.calibration=0;rejected(q,-EOPNOTSUPP,80);
	q=p;q.domain.sensor_width=3839;rejected(q,-EOPNOTSUPP,80);
	q=p;q.domain.sensor_height=2640;rejected(q,-EOPNOTSUPP,80);
	q=p;q.domain.output_width=2559;rejected(q,-EOPNOTSUPP,80);
	q=p;q.domain.output_height=1439;rejected(q,-EOPNOTSUPP,80);
	q=p;q.bls_selector=199;rejected(q,-EOPNOTSUPP,80);
	q=p;q.bls_selector=0;rejected(q,-EOPNOTSUPP,80);
	for(i=1;i<5;i++) { q=p;q.bls_fraction=i;rejected(q,-EOPNOTSUPP,80); }
	assert(sp11_front_cold_fields(0,80,&p)==-EINVAL);
	memset(out,0xa5,sizeof(out));
	assert(sp11_front_cold_fields(out,80,0)==-EINVAL);
	for(i=0;i<80;i++) assert(out[i]==0xa5);
	union { u8 bytes[128]; struct sp11_front_cold_policy policy; } alias;
	alias.policy=p;u8 old[128];memcpy(old,alias.bytes,128);
	assert(sp11_front_cold_fields(alias.bytes,128,&alias.policy)==-EINVAL);
	assert(memcmp(old,alias.bytes,128)==0);
	printf("{\"exhaustive_offset_vectors\":%u,\"status\":\"PASS\"}\n",cases);
	return 0;
}
