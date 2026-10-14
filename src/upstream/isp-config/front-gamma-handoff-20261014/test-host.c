/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-gamma-handoff.h"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static u8 gamma[NF_GAMMA_BYTES],before[NF_GAMMA_BYTES],out[80],saved[80];
static unsigned admitted,negatives;
static void reject(struct sp11_front_gamma_mapping *m,
 const struct sp11_front_cold_policy *p,size_t capacity,size_t bytes,int expected)
{
 memset(out,0xa5,sizeof(out));memcpy(saved,out,sizeof(out));
 int actual=sp11_front_gamma_prepare(out,capacity,p,m,gamma,bytes);
 if(actual!=expected)fprintf(stderr,"negative case%u got%d expected%d\n",negatives,actual,expected);
 assert(actual==expected);
 assert(!memcmp(out,saved,sizeof(out)));negatives++;
}
int main(void)
{
 u32 source[3];
 for(unsigned bank=0;bank<2;bank++) {
  assert(fread(source,sizeof(source),1,stdin)==1);
  assert(source[0]==bank && source[1]==bank && source[2]==1);
  for(unsigned address=0;address<32;address++) for(unsigned offset=0;offset<32;offset++) {
   struct sp11_front_gamma_mapping m={0x1000+address*4,4096,offset*4,bank};
   for(unsigned c=0;c<3;c++) for(unsigned i=0;i<256;i++)
    nf_gamma_put32(gamma+4*(c*256+i),100+c*100);
   memcpy(before,gamma,sizeof(gamma));memset(out,0xa5,sizeof(out));
   assert(!sp11_front_gamma_prepare(out,sizeof(out),&policy,&m,gamma,sizeof(gamma)));
   assert(!memcmp(before,gamma,sizeof(gamma)));
   assert(nf_gamma_get32(out)==0x03000002 && nf_gamma_get32(out+4)==0x5f58);
   assert(nf_gamma_get32(out+8)==source[0] && nf_gamma_get32(out+12)==source[1]);
   const unsigned ch[]={1,2,0};
   for(unsigned c=0;c<3;c++) {
    assert(nf_gamma_get32(out+16+c*12)==0x010003ff);
    assert(nf_gamma_get32(out+20+c*12)==m.dma_base+m.offset+ch[c]*1024);
    assert(nf_gamma_get32(out+24+c*12)==0x5f08+((c+1)<<24));
   }
   for(unsigned i=52;i<sizeof(out);i++)assert(out[i]==0xa5);
   assert(!sp11_front_gamma_enable(out+52,sizeof(out)-52));
   assert(nf_gamma_get32(out+52)==0x03000001 && nf_gamma_get32(out+56)==0x5f60);
   assert(nf_gamma_get32(out+60)==source[2]);
   for(unsigned i=64;i<sizeof(out);i++)assert(out[i]==0xa5);
   admitted++;
  }
 }
 assert(fgetc(stdin)==EOF);
 struct sp11_front_gamma_mapping m={0x1000,4096,0,0},bad;
 for(unsigned n=0;n<52;n++)reject(&m,&policy,n,sizeof(gamma),-ENOSPC);
 for(unsigned n=0;n<NF_GAMMA_BYTES;n++)reject(&m,&policy,sizeof(out),n,-EINVAL);
 bad=m;bad.bank=2;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 bad=m;bad.dma_base=0x100000000ULL;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 bad=m;bad.dma_base=0xfffff000ULL;bad.allocation_bytes=4097;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 bad=m;bad.dma_base=0x1001;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 bad=m;bad.offset=1;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 bad=m;bad.offset=4097;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 bad=m;bad.offset=(size_t)-1;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 bad=m;bad.allocation_bytes=3071;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 bad=m;bad.offset=1028;reject(&bad,&policy,sizeof(out),sizeof(gamma),-ERANGE);
 struct sp11_front_cold_policy p=policy;p.domain.sensor_height=2640;
 reject(&m,&p,sizeof(out),sizeof(gamma),-EOPNOTSUPP);
 reject(&m,NULL,sizeof(out),sizeof(gamma),-EINVAL);
 for(unsigned c=0;c<3;c++) {
  gamma[c*1024+3]=0xff;reject(&m,&policy,sizeof(out),sizeof(gamma),-EINVAL);gamma[c*1024+3]=0;
 }
 nf_gamma_put32(gamma+3068,300U|(0x800U<<12));
 reject(&m,&policy,sizeof(out),sizeof(gamma),-ERANGE);memcpy(gamma,before,sizeof(gamma));
 assert(sp11_front_gamma_prepare(NULL,52,&policy,&m,gamma,sizeof(gamma))==-EINVAL);
 assert(sp11_front_gamma_prepare(out,52,&policy,NULL,gamma,sizeof(gamma))==-EINVAL);
 assert(sp11_front_gamma_prepare(out,52,&policy,&m,NULL,sizeof(gamma))==-EINVAL);
 assert(sp11_front_gamma_prepare(gamma,52,&policy,&m,gamma,sizeof(gamma))==-EINVAL);
 assert(!memcmp(gamma,before,sizeof(gamma)));
 union {struct sp11_front_gamma_mapping m;struct sp11_front_cold_policy p;u8 b[80];} alias;
 memset(alias.b,0xa5,sizeof(alias));alias.m=m;u8 alias_saved[80];memcpy(alias_saved,alias.b,sizeof(alias));
 assert(sp11_front_gamma_prepare(alias.b,52,&policy,&alias.m,gamma,sizeof(gamma))==-EINVAL);
 assert(!memcmp(alias_saved,alias.b,sizeof(alias)));
 alias.p=policy;memcpy(alias_saved,alias.b,sizeof(alias));
 assert(sp11_front_gamma_prepare(alias.b,52,&alias.p,&m,gamma,sizeof(gamma))==-EINVAL);
 assert(!memcmp(alias_saved,alias.b,sizeof(alias)));
 for(unsigned n=0;n<12;n++) {
  memset(out,0xa5,sizeof(out));memcpy(saved,out,sizeof(out));
  assert(sp11_front_gamma_enable(out,n)==-ENOSPC && !memcmp(out,saved,sizeof(out)));negatives++;
 }
 assert(sp11_front_gamma_enable(NULL,12)==-EINVAL);
 printf("{\"status\":\"PASS\",\"admitted\":%u,\"atomic_negatives\":%u}\n",admitted,negatives);
}
