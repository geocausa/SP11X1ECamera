/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "native-front-gamma.h"
static unsigned checks;
static void need(int value){checks++;assert(value);}
static unsigned read32(const unsigned char *p)
{return (unsigned)p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static int slope12(unsigned word)
{unsigned v=word>>12&4095;return v&2048?(int)v-4096:(int)v;}
static void verify(const unsigned char *out,const unsigned short *p)
{
 for(unsigned c=0;c<3;c++)for(unsigned i=0;i<256;i++){
  unsigned word=read32(out+4*(c*256+i));
  need((word&4095)==p[c*257+i]);
  need((int)(word&4095)+slope12(word)==p[c*257+i+1]);
  need((word&0xff000000U)==0);
 }
}
int main(void)
{
 unsigned short points[771],badpoints[771];
 unsigned words[768],badwords[768];
 unsigned char out[3072],before[3072];
 for(unsigned c=0;c<3;c++)for(unsigned i=0;i<257;i++)
  points[c*257+i]=(unsigned short)((i*4095U+128U)/256U);
 need(native_front_gamma12_pack(points,771,out,3072)==0);verify(out,points);
 /* Hand-calculated signed slope and exact LE bytes. */
 points[0]=100;points[1]=99;
 need(native_front_gamma12_pack(points,771,out,3072)==0);
 need(out[0]==0x64 && out[1]==0xf0 && out[2]==0xff && out[3]==0);
 verify(out,points);
 memcpy(before,out,sizeof(out));
 memcpy(badpoints,points,sizeof(points));badpoints[770]=4096;
 need(native_front_gamma12_pack(badpoints,771,out,3072)==-ERANGE);
 need(!memcmp(out,before,sizeof(out)));
 memcpy(badpoints,points,sizeof(points));badpoints[769]=0;badpoints[770]=2048;
 need(native_front_gamma12_pack(badpoints,771,out,3072)==-ERANGE);
 need(!memcmp(out,before,sizeof(out)));
 for(unsigned n=0;n<771;n++){
  need(native_front_gamma12_pack(points,n,out,3072)==-EINVAL);
  need(!memcmp(out,before,sizeof(out)));
 }
 for(unsigned n=0;n<3072;n+=17)
  need(native_front_gamma12_pack(points,771,out,n)==-EINVAL);
 need(native_front_gamma12_pack(NULL,771,out,3072)==-EINVAL);
 need(native_front_gamma12_pack(points,771,NULL,3072)==-EINVAL);
 union {unsigned short p[1600];unsigned char b[3200];} alias;
 memcpy(alias.p,points,sizeof(points));
 need(native_front_gamma12_pack(alias.p,771,alias.b,3072)==-EINVAL);
 /* Three distinct mathematical channel curves; no retained tuning fixture. */
 for(unsigned c=0;c<3;c++)for(unsigned i=0;i<256;i++){
  unsigned base=c==0?i*1023U/256U:c==1?1023U-i*1023U/256U:500U;
  unsigned end=c==0?(i+1)*1023U/256U:c==1?1023U-(i+1)*1023U/256U:500U;
  int delta=(int)end-(int)base;
  words[c*256+i]=base|(((unsigned)delta&1023U)<<10);
  points[c*257+i]=(unsigned short)nf_gamma10_scale12(base);
  if(i==255)points[c*257+256]=(unsigned short)nf_gamma10_scale12(end);
 }
 need(native_front_gamma10_expand(words,768,out,3072)==0);verify(out,points);
 need(read32(out)==(12U<<12)); /* 0 -> 3 in 10-bit becomes 0 -> 12 in 12-bit. */
 need((read32(out+4*255)&4095U)+slope12(read32(out+4*255))==4095);
 memcpy(before,out,sizeof(out));
 memcpy(badwords,words,sizeof(words));badwords[767]|=0x1000000U;
 need(native_front_gamma10_expand(badwords,768,out,3072)==-EINVAL);
 need(!memcmp(out,before,sizeof(out)));
 memcpy(badwords,words,sizeof(words));badwords[767]=(badwords[767]&~1023U)|501U;
 need(native_front_gamma10_expand(badwords,768,out,3072)==-EINVAL);
 need(!memcmp(out,before,sizeof(out)));
 memcpy(badwords,words,sizeof(words));badwords[0]=1023U<<10; /* base0, delta -1 */
 need(native_front_gamma10_expand(badwords,768,out,3072)==-ERANGE);
 need(!memcmp(out,before,sizeof(out)));
 memcpy(badwords,words,sizeof(words));
 badwords[766]=500U|(12U<<10);badwords[767]=512U|(512U<<10);
 need(native_front_gamma10_expand(badwords,768,out,3072)==-ERANGE);
 need(!memcmp(out,before,sizeof(out))); /* native -2049 must not wrap or clamp */
 for(unsigned n=0;n<768;n++){
  need(native_front_gamma10_expand(words,n,out,3072)==-EINVAL);
  need(!memcmp(out,before,sizeof(out)));
 }
 need(native_front_gamma10_expand(NULL,768,out,3072)==-EINVAL);
 need(native_front_gamma10_expand(words,768,NULL,3072)==-EINVAL);
 need(native_front_gamma10_expand(words,768,out,3071)==-EINVAL);
 need(native_front_gamma10_expand(words,768,(unsigned char *)words,3072)==-EINVAL);
 need(!memcmp(out,before,sizeof(out)));
 printf("PASS_FRONT_GAMMA_DATA_COMPILER checks=%u hardware_access=false\n",checks);
 return 0;
}
