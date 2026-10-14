/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-round-config.h"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static unsigned vectors,negatives;
static u32 get32(const u8 *p) {return (u32)p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;}
static void reject(struct sp11_front_cold_policy p,unsigned in,unsigned bits,size_t cap,int expected)
{
 u8 out[112],before[112];memset(out,0xa5,112);memcpy(before,out,112);
 assert(sp11_front_round_config(out,cap,&p,in,bits)==expected);
 assert(!memcmp(out,before,112));negatives++;
}
int main(void)
{
 u8 out[112],generic[120],oracle[96],before[112];u32 bits;
 for(unsigned cap=0;cap<96;cap++) reject(policy,10,8,cap,-ENOSPC);
 for(unsigned in=0;in<33;in++) if(in!=10) reject(policy,in,8,96,-EOPNOTSUPP);
 for(unsigned b=0;b<33;b++) if(b!=8 && b!=10) reject(policy,10,b,96,-EOPNOTSUPP);
 struct sp11_front_cold_policy p=policy;
 p.domain.sensor_height=2640;reject(p,10,8,96,-EOPNOTSUPP);
 p=policy;p.domain.calibration=0;reject(p,10,8,96,-EOPNOTSUPP);
 p=policy;p.domain.output_width=1920;reject(p,10,8,96,-EOPNOTSUPP);
 p=policy;p.bls_selector=199;reject(p,10,8,96,-EOPNOTSUPP);
 p=policy;p.bls_fraction=1;reject(p,10,8,96,-EOPNOTSUPP);
 assert(sp11_front_round_config(NULL,96,&policy,10,8)==-EINVAL);
 memset(out,0xa5,112);memcpy(before,out,112);
 assert(sp11_front_round_config(out,96,NULL,10,8)==-EINVAL);
 assert(!memcmp(out,before,112));
 union {u8 bytes[160];struct sp11_front_cold_policy p;} alias;
 memset(alias.bytes,0xa5,160);alias.p=policy;u8 saved[160];memcpy(saved,alias.bytes,160);
 assert(sp11_front_round_config(alias.bytes,96,&alias.p,10,8)==-EINVAL);
 assert(!memcmp(saved,alias.bytes,160));
 while(fread(&bits,4,1,stdin)==1) {
  assert(fread(oracle,96,1,stdin)==1);
  memset(out,0xa5,112);struct sp11_front_cold_policy copy=policy;
  assert(sp11_front_round_config(out,112,&copy,10,bits)==0);
  assert(!memcmp(&copy,&policy,sizeof(copy)));
  assert(!memcmp(out,oracle,96));
  for(unsigned i=96;i<112;i++) assert(out[i]==0xa5);
  for(unsigned enabled=0;enabled<2;enabled++) {
   assert(sp11_front_round_commands_state(generic,120,bits,enabled)==0);
   assert(!memcmp(out,generic+12,48) && !memcmp(out+48,generic+72,48));
  }
  assert(get32(out)==0x0300000a && get32(out+4)==0x9c70);
  assert(get32(out+48)==0x0300000a && get32(out+52)==0x9e70);
  vectors++;
 }
 assert(feof(stdin) && vectors);
 printf("{\"status\":\"PASS\",\"native_full_vectors\":%u,\"atomic_negatives\":%u}\n",vectors,negatives);
 return 0;
}
