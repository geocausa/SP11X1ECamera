/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-crop-config.h"
typedef uint16_t u16;
typedef int (*e006m_scalar_fn)(void *,u16,u32 *);
#define __used __attribute__((used))
#include "camss-e006p-crop-roundclamp.inc"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static unsigned admitted,rejected,negatives;
static u32 get32(const u8 *p) {return (u32)p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;}
static void reject(struct sp11_front_cold_policy p,size_t cap,int expected)
{
 u8 out[48],before[48];memset(out,0xa5,48);memcpy(before,out,48);
 assert(sp11_front_crop_config(out,cap,&p)==expected);
 assert(!memcmp(out,before,48));negatives++;
}
int main(void)
{
 u8 out[48],generic[128],oracle[32],before[48];u32 dims[2];
 for(unsigned cap=0;cap<32;cap++) reject(policy,cap,-ENOSPC);
 struct sp11_front_cold_policy p=policy;
 p.domain.sensor_height=2640;reject(p,32,-EOPNOTSUPP);
 p=policy;p.domain.calibration=0;reject(p,32,-EOPNOTSUPP);
 p=policy;p.bls_selector=199;reject(p,32,-EOPNOTSUPP);
 p=policy;p.bls_fraction=1;reject(p,32,-EOPNOTSUPP);
 assert(sp11_front_crop_config(NULL,32,&policy)==-EINVAL);
 memset(out,0xa5,48);memcpy(before,out,48);
 assert(sp11_front_crop_config(out,32,NULL)==-EINVAL && !memcmp(out,before,48));
 union {u8 bytes[96];struct sp11_front_cold_policy p;} alias;
 memset(alias.bytes,0xa5,96);alias.p=policy;u8 saved[96];memcpy(saved,alias.bytes,96);
 assert(sp11_front_crop_config(alias.bytes,32,&alias.p)==-EINVAL && !memcmp(saved,alias.bytes,96));
 while(fread(dims,8,1,stdin)==1) {
  assert(fread(oracle,32,1,stdin)==1);
  struct sp11_geometry g={dims[0],dims[1],dims[0],dims[1]};
  assert(sp11_geometry_commands_state(generic,128,&g,false)==0);
  assert(!memcmp(oracle,generic+96,32));
  for(unsigned plane=0;plane<2;plane++) {
   struct e006p_crop_info old={0,0,dims[0]/(plane?2:1)-1,dims[1]/(plane?2:1)-1};
   u32 word;
   assert(get32(oracle+16*plane)==0x03000002);
   assert(get32(oracle+16*plane+4)==(plane?0x9e68:0x9c68));
   for(unsigned pixel=0;pixel<2;pixel++) {
    assert(e006p_crop12_pack(&old,pixel,&word)==0);
    assert(word==get32(oracle+16*plane+8+4*pixel));
   }
  }
  p=policy;p.domain.output_width=dims[0];p.domain.output_height=dims[1];
  struct sp11_front_cold_policy copy=p;
  memset(out,0xa5,48);memcpy(before,out,48);
  int ret=sp11_front_crop_config(out,48,&p);
  if(dims[0]==2560 && dims[1]==1440) {
   assert(ret==0 && !memcmp(out,oracle,32));
   for(unsigned i=32;i<48;i++) assert(out[i]==0xa5);
   admitted++;
  } else {assert(ret==-EOPNOTSUPP && !memcmp(out,before,48));rejected++;}
  assert(!memcmp(&copy,&p,sizeof(p)));
 }
 assert(feof(stdin) && admitted && rejected);
 printf("{\"status\":\"PASS\",\"admitted_front_cases\":%u,\"rejected_other_dimensions\":%u,\"atomic_negatives\":%u}\n",admitted,rejected,negatives);
 return 0;
}
