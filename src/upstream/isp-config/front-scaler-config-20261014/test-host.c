/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-scaler-config.h"
typedef uint16_t u16;
typedef int (*e006m_scalar_fn)(void *,u16,u32 *);
#define __used __attribute__((used))
#include "camss-e006q-mnds23.inc"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static unsigned vectors,admitted,rejected,negatives;
static u32 get32(const u8 *p) {return (u32)p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;}
static void reject(struct sp11_front_cold_policy p,size_t cap,int expected)
{
 u8 out[104],before[104];memset(out,0xa5,104);memcpy(before,out,104);
 assert(sp11_front_scaler_config(out,cap,&p)==expected);
 assert(!memcmp(out,before,104));negatives++;
}
int main(void)
{
 u8 out[104],generic[128],oracle[88],before[104];u32 dims[4];
 for(unsigned cap=0;cap<88;cap++) reject(policy,cap,-ENOSPC);
 struct sp11_front_cold_policy p=policy;
 p.domain.sensor_height=2640;reject(p,88,-EOPNOTSUPP);
 p=policy;p.domain.calibration=0;reject(p,88,-EOPNOTSUPP);
 p=policy;p.domain.output_width=1920;reject(p,88,-EOPNOTSUPP);
 p=policy;p.bls_selector=199;reject(p,88,-EOPNOTSUPP);
 p=policy;p.bls_fraction=1;reject(p,88,-EOPNOTSUPP);
 assert(sp11_front_scaler_config(NULL,88,&policy)==-EINVAL);
 memset(out,0xa5,104);memcpy(before,out,104);
 assert(sp11_front_scaler_config(out,88,NULL)==-EINVAL && !memcmp(out,before,104));
 union {u8 bytes[128];struct sp11_front_cold_policy p;} alias;
 memset(alias.bytes,0xa5,128);alias.p=policy;u8 saved[128];memcpy(saved,alias.bytes,128);
 assert(sp11_front_scaler_config(alias.bytes,88,&alias.p)==-EINVAL);
 assert(!memcmp(saved,alias.bytes,128));
 while(fread(dims,sizeof(dims),1,stdin)==1) {
  assert(fread(oracle,88,1,stdin)==1);
  struct sp11_geometry s={dims[0],dims[1],dims[2],dims[3]};
  struct e006q_mnds23_state old={dims[0],dims[1],dims[2],dims[3],2,2,
   {0,0,dims[0]-1,dims[1]-1},true,false};
  for(unsigned enabled=0;enabled<2;enabled++) {
   assert(sp11_geometry_commands_state(generic,128,&s,enabled)==0);
   for(unsigned plane=0;plane<2;plane++) {
    assert(get32(oracle+44*plane)==0x03000009);
    assert(get32(oracle+44*plane+4)==(plane?0x9a64:0x9864));
    assert(!memcmp(oracle+44*plane+8,generic+48*plane+12,36));
    for(unsigned i=1;i<10;i++) {
     u32 w;assert(e006q_mnds23_word(&old,plane,i,&w)==0);
     assert(w==get32(oracle+44*plane+8+4*(i-1)));
    }
   }
  }
  p=policy;p.domain.sensor_width=dims[0];p.domain.sensor_height=dims[1];
  p.domain.output_width=dims[2];p.domain.output_height=dims[3];
  struct sp11_front_cold_policy copy=p;
  memset(out,0xa5,104);memcpy(before,out,104);
  int ret=sp11_front_scaler_config(out,104,&p);
  if(!memcmp(dims,&policy.domain.sensor_width,16)) {
   assert(ret==0 && !memcmp(out,oracle,88));
   for(unsigned i=88;i<104;i++) assert(out[i]==0xa5);
   admitted++;
  } else {assert(ret==-EOPNOTSUPP && !memcmp(out,before,104));rejected++;}
  assert(!memcmp(&copy,&p,sizeof(p)));vectors++;
 }
 assert(feof(stdin) && admitted && rejected);
 printf("{\"status\":\"PASS\",\"native_vectors\":%u,\"admitted_front_vectors\":%u,\"rejected_other_geometry\":%u,\"atomic_negatives\":%u}\n",vectors,admitted,rejected,negatives);
 return 0;
}
