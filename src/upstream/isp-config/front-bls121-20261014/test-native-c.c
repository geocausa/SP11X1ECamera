/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-bls121.h"
static unsigned int rejects;
static void reject(struct sp11_bls121_ife18_config s, size_t capacity, int error)
{
	u8 out[48], before[48];
	memset(out, 0xa5, sizeof(out)); memcpy(before, out, sizeof(out));
	assert(sp11_bls121_ife18_config_encode(out, capacity, &s) == error);
	assert(memcmp(out, before, sizeof(out)) == 0); rejects++;
}
static void policy_reject(struct sp11_front_cold_policy p)
{
	u8 out[48], before[48];
	memset(out, 0xa5, sizeof(out)); memcpy(before, out, sizeof(out));
	assert(sp11_front_measured_bls121_config(out, sizeof(out), &p) == -EOPNOTSUPP);
	assert(memcmp(out, before, sizeof(out)) == 0); rejects++;
}
int main(void)
{
	struct sp11_bls121_ife18_config s = { 0 };
	struct sp11_front_cold_policy p = {
		{ SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440 },
		SP11_BLS121_IFE18_SELECTOR,0
	}, q;
	u8 out[48], expected[32], before[48]; unsigned int i, vectors=0;
	assert(sp11_bls121_ife18_config_encode(0,32,&s) == -EINVAL);
	memset(out,0xa5,sizeof(out));memcpy(before,out,sizeof(out));
	assert(sp11_bls121_ife18_config_encode(out,32,0) == -EINVAL);
	assert(memcmp(out,before,sizeof(out))==0);
	for(i=0;i<32;i++) reject(s,i,-ENOSPC);
	s.offset18=0x40000;reject(s,32,-ERANGE);s.offset18=0;
	s.gain17=0x20000;reject(s,32,-ERANGE);s.gain17=0;
	for(i=0;i<4;i++) { s.threshold18[i]=0x40000;reject(s,32,-ERANGE);s.threshold18[i]=0; }
	s.offset18=0xffffffff;reject(s,32,-ERANGE);s.offset18=0;
	union { u8 bytes[96]; struct sp11_bls121_ife18_config state; } alias;
	alias.state=s;u8 old[96];memcpy(old,alias.bytes,sizeof(old));
	assert(sp11_bls121_ife18_config_encode(alias.bytes,96,&alias.state)==-EINVAL);
	assert(memcmp(old,alias.bytes,sizeof(old))==0);
	q=p;q.domain.calibration=0;policy_reject(q);
	q=p;q.domain.sensor_width=3839;policy_reject(q);
	q=p;q.domain.sensor_height=2640;policy_reject(q);
	q=p;q.domain.output_width=2559;policy_reject(q);
	q=p;q.domain.output_height=1439;policy_reject(q);
	q=p;q.bls_selector=199;policy_reject(q);
	for(i=1;i<4;i++) { q=p;q.bls_fraction=i;policy_reject(q); }
	assert(sp11_front_measured_bls121_config(0,32,&p)==-EINVAL);
	memset(out,0xa5,sizeof(out));memcpy(before,out,sizeof(out));
	assert(sp11_front_measured_bls121_config(out,32,0)==-EINVAL);
	assert(memcmp(out,before,sizeof(out))==0);
	for(i=0;i<32;i++) {
		assert(sp11_front_measured_bls121_config(out,i,&p)==-ENOSPC);
		assert(memcmp(out,before,sizeof(out))==0);
	}
	union { u8 bytes[96]; struct sp11_front_cold_policy policy; } pa;
	pa.policy=p;memcpy(old,pa.bytes,sizeof(old));
	assert(sp11_front_measured_bls121_config(pa.bytes,96,&pa.policy)==-EINVAL);
	assert(memcmp(old,pa.bytes,sizeof(old))==0);
	memset(out,0xa5,sizeof(out));
	assert(sp11_front_measured_bls121_config(out,sizeof(out),&p)==0);
	const u32 own[8]={0x03000006,0x4b68,0x06710000,0x835,0,0,0,0};
	for(i=0;i<8;i++) sp11_cdm_put32(expected+4*i,own[i]);
	assert(memcmp(out,expected,32)==0);
	for(i=32;i<48;i++) assert(out[i]==0xa5);
	/* Each oracle came from actual constructor/packer/CreateCmdList execution
	 * on independent synthetic inputs; no profile/tuning/captured words.
	 */
	u32 input[6];
	while(fread(input,sizeof(input),1,stdin)==1) {
		assert(fread(expected,sizeof(expected),1,stdin)==1);
		s.offset18=input[0];s.gain17=input[1];
		for(i=0;i<4;i++) s.threshold18[i]=input[2+i];
		memset(out,0xa5,sizeof(out));
		assert(sp11_bls121_ife18_config_encode(out,sizeof(out),&s)==0);
		assert(memcmp(out,expected,32)==0);
		for(i=32;i<48;i++) assert(out[i]==0xa5);
		vectors++;
	}
	assert(feof(stdin) && vectors>0);
	printf("{\"native_vectors\":%u,\"rejections\":%u,\"status\":\"PASS\"}\n",vectors,rejects);
	return 0;
}
