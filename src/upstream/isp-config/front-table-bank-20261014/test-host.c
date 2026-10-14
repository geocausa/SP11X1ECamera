/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "sp11-front-table-bank.h"
static const struct sp11_front_cold_policy policy = {
 {SP11_FRONT_MEASURED_NATIVE_AE74_93,3840,2160,2560,1440},
 SP11_BLS121_IFE18_SELECTOR,0
};
static u8 out[64],saved[64];
static unsigned cases,negatives;
static u32 read32(const u8 *p) {return (u32)p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;}
static void reject(const struct sp11_front_table_bank_state *s,
 const struct sp11_front_cold_policy *p,size_t bytes,int error)
{
 memset(out,0xa5,sizeof(out));memcpy(saved,out,sizeof(out));
 assert(sp11_front_table_bank_config(out,bytes,p,s)==error);
 assert(!memcmp(out,saved,sizeof(out)));negatives++;
}
int main(void)
{
 u32 reference[4];
 for(unsigned placement=0;placement<3;placement++) for(unsigned l=0;l<2;l++)for(unsigned a=0;a<2;a++) {
  assert(fread(reference,sizeof(reference),1,stdin)==1);
  struct sp11_front_table_bank_state state={l,a};
  memset(out,0xa5,sizeof(out));assert(!sp11_front_table_bank_config(out,sizeof(out),&policy,&state));
  assert(read32(out)==0x03000002 && read32(out+4)==0x4358);
  assert(read32(out+16)==0x03000002 && read32(out+20)==0x4958);
  for(unsigned i=0;i<2;i++)assert(read32(out+8+i*4)==reference[i] && reference[i]==l);
  for(unsigned i=0;i<2;i++)assert(read32(out+24+i*4)==reference[i+2] && reference[i+2]==a);
  for(unsigned i=32;i<sizeof(out);i++)assert(out[i]==0xa5);
  cases++;
 }
 assert(fgetc(stdin)==EOF);
 struct sp11_front_table_bank_state state={0,0};
 for(unsigned n=0;n<32;n++)reject(&state,&policy,n,-ENOSPC);
 for(unsigned n=2;n<1024;n++) {
  state.lsc=n;state.abf=0;reject(&state,&policy,sizeof(out),-ERANGE);
  state.lsc=0;state.abf=n;reject(&state,&policy,sizeof(out),-ERANGE);
 }
 state.lsc=(u32)-1;state.abf=0;reject(&state,&policy,sizeof(out),-ERANGE);
 state.lsc=0;state.abf=(u32)-1;reject(&state,&policy,sizeof(out),-ERANGE);
 state=(struct sp11_front_table_bank_state){0,0};
 struct sp11_front_cold_policy bad=policy;bad.domain.sensor_height=2640;
 reject(&state,&bad,sizeof(out),-EOPNOTSUPP);
 reject(&state,NULL,sizeof(out),-EINVAL);reject(NULL,&policy,sizeof(out),-EINVAL);
 assert(sp11_front_table_bank_config(NULL,32,&policy,&state)==-EINVAL);
 union {u8 b[64];struct sp11_front_cold_policy policy;struct sp11_front_table_bank_state state;} alias;
 memset(alias.b,0xa5,sizeof(alias));alias.policy=policy;u8 before[64];memcpy(before,alias.b,sizeof(alias));
 assert(sp11_front_table_bank_config(alias.b,32,&alias.policy,&state)==-EINVAL);
 assert(!memcmp(before,alias.b,sizeof(alias)));
 alias.state=state;memcpy(before,alias.b,sizeof(alias));
 assert(sp11_front_table_bank_config(alias.b,32,&policy,&alias.state)==-EINVAL);
 assert(!memcmp(before,alias.b,sizeof(alias)));
 printf("{\"status\":\"PASS\",\"source_comparisons\":%u,\"atomic_negatives\":%u}\n",cases,negatives);
}
