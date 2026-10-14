/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-cst12-policy.h"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static unsigned accepted,rejected,negatives;
static u32 get32(const u8 *p) {return (u32)p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;}
static void reject(struct sp11_cst_config s,struct sp11_front_cold_policy p,unsigned bits,size_t bytes,int ret)
{
 u8 out[96],before[96];memset(out,0xa5,96);memcpy(before,out,96);
 assert(sp11_front_cst12_config(out,bytes,&p,&s,bits)==ret);
 assert(!memcmp(out,before,96));negatives++;
}
int main(void)
{
 struct sp11_cst_config s=sp11_front_cst12_bt601;
 struct sp11_front_cold_policy p=policy;
 u8 out[96],generic[92],oracle[80],saved[96];
 for(unsigned n=0;n<80;n++) reject(s,p,12,n,-ENOSPC);
 for(unsigned bits=0;bits<16;bits++) if(bits!=12) reject(s,p,bits,80,-EOPNOTSUPP);
 for(unsigned field=0;field<9;field++) {
  struct sp11_cst_config t=s;t.matrix[field]=4096;reject(t,p,12,80,-ERANGE);
  t=s;t.matrix[field]=-4097;reject(t,p,12,80,-ERANGE);
 }
 for(unsigned i=0;i<3;i++) {
  struct sp11_cst_config t=s;t.auxiliary[i]=1;reject(t,p,12,80,-EOPNOTSUPP);
  t=s;t.offset[i]++;reject(t,p,12,80,-EOPNOTSUPP);
  t=s;t.minimum[i]=1;reject(t,p,12,80,-EOPNOTSUPP);
  t=s;t.maximum[i]=1023;reject(t,p,12,80,-EOPNOTSUPP);
  t=s;t.maximum[i]=4096;reject(t,p,12,80,-ERANGE);
 }
 s.enabled=true;reject(s,p,12,80,-EOPNOTSUPP);s=sp11_front_cst12_bt601;
 p.domain.sensor_height=2640;reject(s,p,12,80,-EOPNOTSUPP);
 p=policy;p.domain.calibration=0;reject(s,p,12,80,-EOPNOTSUPP);
 p=policy;p.bls_selector=199;reject(s,p,12,80,-EOPNOTSUPP);
 p=policy;p.bls_fraction=1;reject(s,p,12,80,-EOPNOTSUPP);p=policy;
 assert(sp11_front_cst12_config(NULL,80,&p,&s,12)==-EINVAL);
 memset(out,0xa5,96);memcpy(saved,out,96);
 assert(sp11_front_cst12_config(out,80,NULL,&s,12)==-EINVAL);
 assert(sp11_front_cst12_config(out,80,&p,NULL,12)==-EINVAL);
 assert(!memcmp(out,saved,96));
 union {u8 b[256];struct sp11_cst_config s;struct sp11_front_cold_policy p;} alias;
 memset(alias.b,0xa5,256);alias.s=s;u8 before[256];memcpy(before,alias.b,256);
 assert(sp11_front_cst12_config(alias.b,80,&p,&alias.s,12)==-EINVAL);
 assert(!memcmp(before,alias.b,256));
 alias.p=p;memcpy(before,alias.b,256);
 assert(sp11_front_cst12_config(alias.b,80,&alias.p,&s,12)==-EINVAL);
 assert(!memcmp(before,alias.b,256));
 u32 admission,clamps[6];s16 values[15];
 while(fread(&admission,4,1,stdin)==1) {
  assert(fread(values,sizeof(values),1,stdin)==1);
  assert(fread(clamps,sizeof(clamps),1,stdin)==1);
  assert(fread(oracle,80,1,stdin)==1);
  s=(struct sp11_cst_config){0};
  memcpy(s.matrix,values,18);memcpy(s.offset,values+9,6);memcpy(s.auxiliary,values+12,6);
  memcpy(s.minimum,clamps,12);memcpy(s.maximum,clamps+3,12);
  struct sp11_cst_config copy=s;
  assert(sp11_cst_commands(generic,92,&s)==0);
  assert(get32(generic)==0x03000001 && get32(generic+4)==0x6160 && get32(generic+8)==0);
  assert(!memcmp(generic+12,oracle,80));
  memset(out,0xa5,96);memcpy(saved,out,96);
  int ret=sp11_front_cst12_config(out,96,&policy,&s,12);
  assert(!memcmp(&copy,&s,sizeof(s)));
  if(admission) {
   assert(ret==0 && !memcmp(out,oracle,80));
   for(unsigned i=80;i<96;i++) assert(out[i]==0xa5);
   accepted++;
  } else {assert(ret==-EOPNOTSUPP && !memcmp(out,saved,96));rejected++;}
 }
 assert(feof(stdin) && accepted && rejected);
 s=sp11_front_cst12_bt601;assert(sp11_front_cst12_bt601_config(out,96,&policy,12)==0);
 assert(sp11_cst_commands(generic,92,&s)==0 && !memcmp(out,generic+12,80));
 for(unsigned g=0;g<4096;g++) {
  for(unsigned row=0;row<3;row++) {
   int sum=s.matrix[3*row]+s.matrix[3*row+1]+s.matrix[3*row+2];
   assert(sum==(row?0:1024));
   assert(sum*(int)g/1024+s.offset[row]==(row?2048:(int)g));
  }
 }
 printf("{\"status\":\"PASS\",\"accepted_native_configurations\":%u,\"rejected_native_nonpolicy_states\":%u,\"atomic_negatives\":%u,\"mathematical_neutral_values\":4096}\n",accepted,rejected,negatives);
 return 0;
}
