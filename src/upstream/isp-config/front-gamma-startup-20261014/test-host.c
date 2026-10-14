/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "sp11-front-gamma-startup.h"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static nf_gamma_u16 points[NF_GAMMA_POINT_COUNT],saved_points[NF_GAMMA_POINT_COUNT];
static nf_gamma_u32 reference_words[NF_GAMMA_WORD_COUNT];
static nf_gamma_u8 out[NF_GAMMA_BYTES+16],saved[NF_GAMMA_BYTES+16];
static nf_gamma_u8 reference[NF_GAMMA_BYTES],packet[NF_ISP_MAX_BYTES];
static struct sp11_front_gamma_workspace workspace;
static unsigned cases,failures,rejections,own_curves;
static unsigned scale(unsigned x) {return (x*4095U+511U)/1023U;}
static unsigned word(const nf_gamma_u8 *p) {return nf_gamma_get32(p);}
static void compare(void)
{
 int update=0;
 memcpy(saved_points,points,sizeof(points));
 memset(out,0xa5,sizeof(out));memcpy(saved,out,sizeof(out));
 int original=native_front_isp_encode(points,NF_GAMMA_POINT_COUNT,packet,sizeof(packet));
 if(!original) original=native_front_isp_decode(packet,sizeof(packet),reference_words,
  NF_GAMMA_WORD_COUNT,reference,sizeof(reference),&update);
 int ret=sp11_front_gamma_startup(out,sizeof(out),&policy,points,NF_GAMMA_POINT_COUNT,&workspace);
 assert(ret==original);
 assert(!memcmp(saved_points,points,sizeof(points)));
 if(ret) {assert(!memcmp(saved,out,sizeof(out)));failures++;}
 else {
  assert(update==1 && !memcmp(out,reference,NF_GAMMA_BYTES));
  assert(native_front_gamma12_validate(out,NF_GAMMA_BYTES)==0);
  for(unsigned c=0;c<3;c++) for(unsigned i=0;i<256;i++) {
   unsigned a=c*257+i,v=scale(points[a]);int delta=(int)scale(points[a+1])-(int)v;
   assert(word(out+4*(c*256+i))==(v|(((unsigned)delta&4095U)<<12)));
  }
  for(unsigned i=NF_GAMMA_BYTES;i<sizeof(out);i++) assert(out[i]==0xa5);
 }
 cases++;
}
static void reject(const struct sp11_front_cold_policy *p,size_t count,size_t capacity,int ret)
{
 memset(out,0xa5,sizeof(out));memcpy(saved,out,sizeof(out));
 assert(sp11_front_gamma_startup(out,capacity,p,points,count,&workspace)==ret);
 assert(!memcmp(saved,out,sizeof(out)));rejections++;
}
static void flat(unsigned b)
{
 for(unsigned i=0;i<257;i++) {points[i]=b;points[257+i]=1023-b;points[514+i]=b;}
}
int main(void)
{
 for(unsigned b=0;b<1024;b++) {flat(b);compare();}
 const int delta[]={-512,-511,-1,0,1,511,512};
 for(unsigned b=0;b<1024;b++) for(unsigned j=0;j<7;j++)
  if((int)b+delta[j]>=0 && (int)b+delta[j]<=1023) {
   flat(b);points[770]=b+delta[j];compare();
  }
 unsigned rng=681;
 for(unsigned n=0;n<64;n++) {
  for(unsigned c=0;c<3;c++) {
   int v=100+c*300;
   for(unsigned i=0;i<257;i++) {rng=rng*1664525U+1013904223U;v+=(int)(rng%61)-30;v=v<0?0:v>1023?1023:v;points[c*257+i]=v;}
  }
  compare();
 }
 flat(512);
 for(unsigned n=0;n<NF_GAMMA_BYTES;n++) reject(&policy,NF_GAMMA_POINT_COUNT,n,-ENOSPC);
 for(unsigned n=0;n<NF_GAMMA_POINT_COUNT;n++) reject(&policy,n,sizeof(out),-EINVAL);
 reject(&policy,NF_GAMMA_POINT_COUNT+1,sizeof(out),-EINVAL);
 points[770]=1024;reject(&policy,NF_GAMMA_POINT_COUNT,sizeof(out),-ERANGE);flat(512);
 struct sp11_front_cold_policy p=policy;p.domain.sensor_height=2640;
 reject(&p,NF_GAMMA_POINT_COUNT,sizeof(out),-EOPNOTSUPP);
 p=policy;p.domain.calibration=0;reject(&p,NF_GAMMA_POINT_COUNT,sizeof(out),-EOPNOTSUPP);
 p=policy;p.bls_selector=199;reject(&p,NF_GAMMA_POINT_COUNT,sizeof(out),-EOPNOTSUPP);
 p=policy;p.bls_fraction=1;reject(&p,NF_GAMMA_POINT_COUNT,sizeof(out),-EOPNOTSUPP);
 reject(NULL,NF_GAMMA_POINT_COUNT,sizeof(out),-EINVAL);
 assert(sp11_front_gamma_startup(NULL,NF_GAMMA_BYTES,&policy,points,NF_GAMMA_POINT_COUNT,&workspace)==-EINVAL);
 assert(sp11_front_gamma_startup(out,NF_GAMMA_BYTES,&policy,NULL,NF_GAMMA_POINT_COUNT,&workspace)==-EINVAL);
 assert(sp11_front_gamma_startup(out,NF_GAMMA_BYTES,&policy,points,NF_GAMMA_POINT_COUNT,NULL)==-EINVAL);
 union {struct sp11_front_gamma_workspace w;nf_gamma_u16 p[4096];u8 b[8192];struct sp11_front_cold_policy policy;} alias;
 memset(alias.b,0xa5,sizeof(alias));memcpy(alias.p,points,sizeof(points));
 u8 before[8192];memcpy(before,alias.b,sizeof(before));
 assert(sp11_front_gamma_startup(alias.b,NF_GAMMA_BYTES,&policy,alias.p,NF_GAMMA_POINT_COUNT,&workspace)==-EINVAL);
 assert(!memcmp(before,alias.b,sizeof(before)));
 assert(sp11_front_gamma_startup(out,NF_GAMMA_BYTES,&policy,alias.p,NF_GAMMA_POINT_COUNT,&alias.w)==-EINVAL);
 assert(!memcmp(before,alias.b,sizeof(before)));
 assert(sp11_front_gamma_startup(alias.b,NF_GAMMA_BYTES,&policy,points,NF_GAMMA_POINT_COUNT,&alias.w)==-EINVAL);
 alias.policy=policy;memcpy(before,alias.b,sizeof(before));
 assert(sp11_front_gamma_startup(alias.b,NF_GAMMA_BYTES,&alias.policy,points,NF_GAMMA_POINT_COUNT,&workspace)==-EINVAL);
 assert(!memcmp(before,alias.b,sizeof(before)));
 assert(sp11_front_gamma_startup(out,NF_GAMMA_BYTES,&alias.policy,points,NF_GAMMA_POINT_COUNT,&alias.w)==-EINVAL);
 assert(!memcmp(before,alias.b,sizeof(before)));
 size_t n=fread(points,sizeof(*points),NF_GAMMA_POINT_COUNT,stdin);
 if(n) {assert(n==NF_GAMMA_POINT_COUNT && fgetc(stdin)==EOF);compare();own_curves++;}
 assert(own_curves==1 && failures>0);
 printf("{\"status\":\"PASS\",\"differential_cases\":%u,\"slope_rejections\":%u,\"boundary_rejections\":%u,\"own_v15_curves\":%u,\"workspace_bytes\":%zu}\n",cases,failures,rejections,own_curves,sizeof(workspace));
 return 0;
}
