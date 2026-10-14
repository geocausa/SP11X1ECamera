/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-abf-config.h"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static u8 out[160],saved[160];
static unsigned comparisons,negatives;
static void compare_old(void)
{
 u8 full[SP11_FRONT_MEASURED_CONFIG_BYTES];
 assert(!sp11_front_measured_config(full,sizeof(full),&policy.domain));
 unsigned words=0;size_t position=0;
 const unsigned counts[]={2,4,8,9};const unsigned bases[]={0x4968,0x4980,0x49a0,0x49c8};
 for(unsigned b=0;b<4;b++) {
  assert(nf_gamma_get32(out+position)==0x03000000+counts[b]);
  assert(nf_gamma_get32(out+position+4)==bases[b]);
  for(unsigned j=0;j<counts[b];j++) {
   unsigned found=0;
   for(unsigned k=0;k<SP11_FRONT_MEASURED_CONFIG_WORDS;k++) {
    const u8 *p=full+k*12;
    if(nf_gamma_get32(p+4)==bases[b]+j*4) {
     assert(nf_gamma_get32(out+position+8+j*4)==nf_gamma_get32(p+8));found++;
    }
   }
   assert(found==1);words++;
  }
  position+=8+counts[b]*4;
 }
 assert(position==124 && words==23);
}
static void reject(const struct sp11_front_cold_policy *p,size_t capacity,int activate,int error)
{
 memset(out,0xa5,sizeof(out));memcpy(saved,out,sizeof(out));
 int actual=activate?sp11_front_abf_activate(out,capacity,p):sp11_front_abf_config(out,capacity,p);
 assert(actual==error && !memcmp(out,saved,sizeof(out)));negatives++;
}
int main(void)
{
 u8 config[124],activation[12];
 for(unsigned placement=0;placement<3;placement++)for(unsigned bank=0;bank<2;bank++) {
  assert(fread(config,sizeof(config),1,stdin)==1 && fread(activation,sizeof(activation),1,stdin)==1);
  memset(out,0xa5,sizeof(out));assert(!sp11_front_abf_config(out,sizeof(out),&policy));
  assert(!memcmp(out,config,124));compare_old();
  for(unsigned i=124;i<sizeof(out);i++)assert(out[i]==0xa5);
  memset(out,0xa5,sizeof(out));assert(!sp11_front_abf_activate(out,sizeof(out),&policy));
  assert(!memcmp(out,activation,12));
  assert(nf_gamma_get32(out)==0x03000001 && nf_gamma_get32(out+4)==0x4960 && nf_gamma_get32(out+8)==0x101);
  for(unsigned i=12;i<sizeof(out);i++)assert(out[i]==0xa5);
  comparisons++;
 }
 assert(fgetc(stdin)==EOF);
 for(unsigned n=0;n<124;n++)reject(&policy,n,0,-ENOSPC);
 for(unsigned n=0;n<12;n++)reject(&policy,n,1,-ENOSPC);
 for(unsigned a=0;a<2;a++) {
  reject(NULL,sizeof(out),a,-EINVAL);
  struct sp11_front_cold_policy p=policy;p.domain.calibration=0;reject(&p,sizeof(out),a,-EOPNOTSUPP);
  p=policy;p.domain.sensor_width=2640;reject(&p,sizeof(out),a,-EOPNOTSUPP);
  p=policy;p.domain.sensor_height=2640;reject(&p,sizeof(out),a,-EOPNOTSUPP);
  p=policy;p.domain.output_width=3840;reject(&p,sizeof(out),a,-EOPNOTSUPP);
  p=policy;p.domain.output_height=2160;reject(&p,sizeof(out),a,-EOPNOTSUPP);
  p=policy;p.bls_selector=199;reject(&p,sizeof(out),a,-EOPNOTSUPP);
  p=policy;p.bls_fraction=1;reject(&p,sizeof(out),a,-EOPNOTSUPP);
  assert((a?sp11_front_abf_activate(NULL,160,&policy):sp11_front_abf_config(NULL,160,&policy))==-EINVAL);
 }
 union {struct sp11_front_cold_policy p;u8 b[160];} alias;
 memset(alias.b,0xa5,sizeof(alias));alias.p=policy;u8 before[160];memcpy(before,alias.b,sizeof(alias));
 assert(sp11_front_abf_config(alias.b,sizeof(alias),&alias.p)==-EINVAL && !memcmp(before,alias.b,sizeof(alias)));
 assert(sp11_front_abf_activate(alias.b,sizeof(alias),&alias.p)==-EINVAL && !memcmp(before,alias.b,sizeof(alias)));
 printf("{\"status\":\"PASS\",\"source_comparisons\":%u,\"atomic_negatives\":%u,\"own_configuration_words\":23}\n",comparisons,negatives);
}
