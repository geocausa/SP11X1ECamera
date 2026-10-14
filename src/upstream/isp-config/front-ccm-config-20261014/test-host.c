/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-ccm-measured.h"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static unsigned admitted,rejected,negatives;
static u32 get32(const u8 *p) {return (u32)p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;}
static void reject(struct sp11_front_ccm_state s,struct sp11_front_cold_policy p,size_t cap,int expected)
{
 u8 out[64],before[64];memset(out,0xa5,64);memcpy(before,out,64);
 assert(sp11_front_ccm_config(out,cap,&p,&s)==expected);
 assert(!memcmp(out,before,64));negatives++;
}
int main(void)
{
 struct sp11_front_ccm_state s=sp11_front_ccm_run93;
 u8 out[64],coefficients[32],oracle[48],before[64];u32 fraction;s16 fields[12];
 for(unsigned cap=0;cap<48;cap++) reject(s,policy,cap,-ENOSPC);
 for(unsigned q=0;q<33;q++) if(q!=7) {s.fractional_bits=q;reject(s,policy,48,-EOPNOTSUPP);}
 s=sp11_front_ccm_run93;
 for(unsigned i=0;i<9;i++) {
  struct sp11_front_ccm_state t=s;t.matrix[i]=2048;reject(t,policy,48,-ERANGE);
  t.matrix[i]=-2049;reject(t,policy,48,-ERANGE);
 }
 for(unsigned i=0;i<3;i++) {
  struct sp11_front_ccm_state t=s;t.offset[i]=1;reject(t,policy,48,-EOPNOTSUPP);
  t.offset[i]=-1;reject(t,policy,48,-EOPNOTSUPP);
 }
 struct sp11_front_cold_policy p=policy;
 p.domain.sensor_height=2640;reject(s,p,48,-EOPNOTSUPP);
 p=policy;p.domain.calibration=0;reject(s,p,48,-EOPNOTSUPP);
 p=policy;p.bls_selector=199;reject(s,p,48,-EOPNOTSUPP);
 p=policy;p.bls_fraction=1;reject(s,p,48,-EOPNOTSUPP);
 assert(sp11_front_ccm_config(NULL,48,&policy,&s)==-EINVAL);
 memset(out,0xa5,64);memcpy(before,out,64);
 assert(sp11_front_ccm_config(out,48,NULL,&s)==-EINVAL);
 assert(sp11_front_ccm_config(out,48,&policy,NULL)==-EINVAL);
 assert(!memcmp(out,before,64));
 union {u8 bytes[160];struct sp11_front_ccm_state s;struct sp11_front_cold_policy p;} alias;
 memset(alias.bytes,0xa5,160);alias.s=s;u8 saved[160];memcpy(saved,alias.bytes,160);
 assert(sp11_front_ccm_config(alias.bytes,48,&policy,&alias.s)==-EINVAL && !memcmp(saved,alias.bytes,160));
 alias.p=policy;memcpy(saved,alias.bytes,160);
 assert(sp11_front_ccm_config(alias.bytes,48,&alias.p,&s)==-EINVAL && !memcmp(saved,alias.bytes,160));
 while(fread(&fraction,4,1,stdin)==1) {
  assert(fread(fields,sizeof(fields),1,stdin)==1 && fread(oracle,48,1,stdin)==1);
  memcpy(s.matrix,fields,18);memcpy(s.offset,fields+9,6);s.fractional_bits=fraction;
  struct sp11_front_ccm_state copy=s;
  assert(sp11_front_ccm_commands(coefficients,32,s.matrix)==0);
  for(unsigned i=0;i<6;i++)
   assert((get32(coefficients+8+4*i)&0x0fff0fffU)==get32(oracle+8+4*i));
  /* Existing transpose/numeric matrix reused; its extra sign-fill is cleared. */
  memset(out,0xa5,64);memcpy(before,out,64);
  int ret=sp11_front_ccm_config(out,64,&policy,&s);
  if(fraction==7 && !s.offset[0] && !s.offset[1] && !s.offset[2]) {
   assert(ret==0 && !memcmp(out,oracle,48));
   for(unsigned i=48;i<64;i++) assert(out[i]==0xa5);
   assert(get32(out)==0x0300000a && get32(out+4)==0x5868);
   for(unsigned i=32;i<48;i++) assert(out[i]==0);
   admitted++;
  } else {assert(ret==-EOPNOTSUPP && !memcmp(out,before,64));rejected++;}
  assert(!memcmp(&s,&copy,sizeof(s)));
 }
 assert(feof(stdin) && admitted && rejected);
 assert(sp11_front_ccm_measured_config(out,64,&policy)==0);
 assert(sp11_front_ccm_commands(coefficients,32,sp11_front_ccm_run93.matrix)==0);
 for(unsigned i=0;i<6;i++) assert(get32(out+8+4*i)==(get32(coefficients+8+4*i)&0x0fff0fffU));
 printf("{\"status\":\"PASS\",\"admitted_native_cases\":%u,\"rejected_other_policy_cases\":%u,\"atomic_negatives\":%u}\n",admitted,rejected,negatives);
 return 0;
}
