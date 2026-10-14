/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-table-handoff.h"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static u8 lsc[SP11_FRONT_LSC_BYTES],abf[SP11_FRONT_ABF_BYTES];
static u8 saved_lsc[SP11_FRONT_LSC_BYTES],saved_abf[SP11_FRONT_ABF_BYTES];
static u8 out[80],saved[80];
static unsigned admitted,negatives,own;
static u32 source[4][4];
static void check(struct sp11_front_table_mapping *m)
{
 memcpy(saved_lsc,lsc,sizeof(lsc));memcpy(saved_abf,abf,sizeof(abf));
 memset(out,0xa5,sizeof(out));
 assert(!sp11_front_tables_prepare(out,sizeof(out),&policy,m,m->request_id,lsc,sizeof(lsc),abf,sizeof(abf)));
 for(unsigned i=0;i<4;i++) {
  unsigned offset=i<3 ? m->lsc_offset+i*884 : m->abf_offset;
  assert(nf_gamma_get32(out+i*12)==0x01000000+source[i][3]-1);
  assert(nf_gamma_get32(out+i*12+4)==m->dma_base+offset);
  assert(nf_gamma_get32(out+i*12+8)==source[i][0]+(source[i][1]<<24));
 }
 for(unsigned i=48;i<sizeof(out);i++)assert(out[i]==0xa5);
 assert(!memcmp(saved_lsc,lsc,sizeof(lsc)) && !memcmp(saved_abf,abf,sizeof(abf)));
 admitted++;
}
static void reject(struct sp11_front_table_mapping *m,u64 expected,
 const struct sp11_front_cold_policy *p,size_t capacity,size_t lb,size_t ab,int error)
{
 memset(out,0xa5,sizeof(out));memcpy(saved,out,sizeof(out));
 int actual=sp11_front_tables_prepare(out,capacity,p,m,expected,lsc,lb,abf,ab);
 if(actual!=error)fprintf(stderr,"negative%u got%d expected%d\n",negatives,actual,error);
 assert(actual==error && !memcmp(out,saved,sizeof(out)));negatives++;
}
static void synthetic(unsigned n)
{
 for(unsigned i=0;i<221;i++) {
  unsigned g=(n+i)%8192,r=(n*3+i*7)%8192,b=(n*5+i*13)%8192;
  nf_gamma_put32(lsc+i*4,r|(g<<14));nf_gamma_put32(lsc+884+i*4,b|(g<<14));
  nf_gamma_put32(lsc+1768+i*4,0);
 }
 for(unsigned i=0;i<64;i++) {
  unsigned v=511-i;
  nf_gamma_put32(abf+i*4,v|(i==63 ? 0 : 1U<<9));
 }
}
int main(void)
{
 assert(fread(source,sizeof(source),1,stdin)==1);
 for(unsigned i=0;i<4;i++) {
  assert(source[i][0]==(i<3?0x4308:0x4908));
  assert(source[i][1]==(i<3?i+1:1));
  assert(source[i][2]==148+(i<3?i*884:0));
  assert(source[i][3]==(i<3?884:256));
 }
 struct sp11_front_table_mapping m={1,0x1000,8192,0,4096};
 for(unsigned address=0;address<32;address++)for(unsigned offset=0;offset<32;offset++) {
  synthetic(address*32+offset);m.dma_base=0x1000+address*4;m.lsc_offset=offset*4;
  for(unsigned req=1;req<3;req++){m.request_id=req;check(&m);}
 }
 assert(fread(lsc,sizeof(lsc),1,stdin)==1 && fread(abf,sizeof(abf),1,stdin)==1 && fgetc(stdin)==EOF);
 check(&m);own++;
 m=(struct sp11_front_table_mapping){1,0x1000,8192,0,4096};
 for(unsigned n=0;n<48;n++)reject(&m,1,&policy,n,sizeof(lsc),sizeof(abf),-ENOSPC);
 for(unsigned n=0;n<sizeof(lsc);n++)reject(&m,1,&policy,sizeof(out),n,sizeof(abf),-EINVAL);
 for(unsigned n=0;n<sizeof(abf);n++)reject(&m,1,&policy,sizeof(out),sizeof(lsc),n,-EINVAL);
 reject(&m,2,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EPROTO);
 reject(&m,0,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);
 struct sp11_front_table_mapping bad=m;
 bad.request_id=0;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);
 bad=m;bad.lsc_offset=(size_t)-1;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 bad=m;bad.abf_offset=(size_t)-1;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 bad=m;bad.allocation_bytes=4351;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 bad=m;bad.abf_offset=2651;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);
 bad=m;bad.lsc_offset=4097;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);
 bad=m;bad.abf_offset=2652;check(&bad);
 bad=m;bad.dma_base=0x100000000ULL;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 bad=m;bad.dma_base=0xfffff000ULL;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 bad=m;bad.dma_base=0x1001;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 bad=m;bad.lsc_offset=1;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 bad=m;bad.abf_offset=4097;reject(&bad,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 struct sp11_front_cold_policy p=policy;p.domain.sensor_width=2640;
 reject(&m,1,&p,sizeof(out),sizeof(lsc),sizeof(abf),-EOPNOTSUPP);
 reject(&m,1,NULL,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);
 for(unsigned i=0;i<221;i++) {
  u32 w=nf_gamma_get32(lsc+i*4);nf_gamma_put32(lsc+i*4,w|(1U<<13));
  reject(&m,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);nf_gamma_put32(lsc+i*4,w);
  w=nf_gamma_get32(lsc+884+i*4);nf_gamma_put32(lsc+884+i*4,w^(1U<<14));
  reject(&m,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);nf_gamma_put32(lsc+884+i*4,w);
  nf_gamma_put32(lsc+1768+i*4,1);
  reject(&m,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);nf_gamma_put32(lsc+1768+i*4,0);
 }
 for(unsigned i=0;i<64;i++) {
  u32 w=nf_gamma_get32(abf+i*4);nf_gamma_put32(abf+i*4,w|(1U<<18));
  reject(&m,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);nf_gamma_put32(abf+i*4,w);
 }
 synthetic(1);
 nf_gamma_put32(abf+252,448|(1U<<9));reject(&m,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);
 synthetic(1);nf_gamma_put32(abf+252,0);reject(&m,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);
 synthetic(1);nf_gamma_put32(abf+252,449);reject(&m,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-EINVAL);
 synthetic(1);nf_gamma_put32(abf,0);reject(&m,1,&policy,sizeof(out),sizeof(lsc),sizeof(abf),-ERANGE);
 synthetic(1);
 memcpy(saved_lsc,lsc,sizeof(lsc));memcpy(saved_abf,abf,sizeof(abf));
 assert(sp11_front_tables_prepare(lsc,48,&policy,&m,1,lsc,sizeof(lsc),abf,sizeof(abf))==-EINVAL);
 assert(sp11_front_tables_prepare(abf,48,&policy,&m,1,lsc,sizeof(lsc),abf,sizeof(abf))==-EINVAL);
 assert(!memcmp(lsc,saved_lsc,sizeof(lsc)) && !memcmp(abf,saved_abf,sizeof(abf)));
 union {struct sp11_front_table_mapping m;struct sp11_front_cold_policy p;u8 b[80];} alias;
 memset(alias.b,0xa5,sizeof(alias));alias.m=m;u8 alias_saved[80];memcpy(alias_saved,alias.b,sizeof(alias));
 assert(sp11_front_tables_prepare(alias.b,48,&policy,&alias.m,1,lsc,sizeof(lsc),abf,sizeof(abf))==-EINVAL);
 assert(!memcmp(alias.b,alias_saved,sizeof(alias)));
 alias.p=policy;memcpy(alias_saved,alias.b,sizeof(alias));
 assert(sp11_front_tables_prepare(alias.b,48,&alias.p,&m,1,lsc,sizeof(lsc),abf,sizeof(abf))==-EINVAL);
 assert(!memcmp(alias.b,alias_saved,sizeof(alias)));
 assert(sp11_front_tables_prepare(out,48,&policy,&m,1,lsc,sizeof(lsc),lsc+100,sizeof(abf))==-EINVAL);
 assert(sp11_front_tables_prepare(NULL,48,&policy,&m,1,lsc,sizeof(lsc),abf,sizeof(abf))==-EINVAL);
 assert(sp11_front_tables_prepare(out,48,&policy,NULL,1,lsc,sizeof(lsc),abf,sizeof(abf))==-EINVAL);
 assert(sp11_front_tables_prepare(out,48,&policy,&m,1,NULL,sizeof(lsc),abf,sizeof(abf))==-EINVAL);
 assert(sp11_front_tables_prepare(out,48,&policy,&m,1,lsc,sizeof(lsc),NULL,sizeof(abf))==-EINVAL);
 printf("{\"status\":\"PASS\",\"admitted\":%u,\"atomic_negatives\":%u,\"existing_own_table_pairs\":%u}\n",admitted,negatives,own);
}
