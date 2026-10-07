/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "native-front-params.h"
static unsigned checks;
static void need(int condition) { checks++; assert(condition); }
static void put(unsigned char *p, unsigned offset, uint64_t value, unsigned bytes)
{
 for (unsigned i = 0; i < bytes; i++) p[offset+i] = value >> (8*i);
}
static void header(unsigned char *p, uint64_t request, unsigned mask)
{
 memset(p,0,64);
 put(p,0,NATIVE_FRONT_PARAMS_MAGIC,4);
 put(p,4,1,2);
 put(p,6,64,2);
 put(p,8,request,8);
 put(p,16,mask,4);
}
int main(void)
{
 unsigned char packet[64], bad[64];
 uint32_t values[9][6], before[9][6];
 need(sizeof(struct native_front_params) == 64);
 for (unsigned i = 0; i < 9; i++)
  for (unsigned j = 0; j < 6; j++) values[i][j] = 0xdead0000 + i*6+j;
 memcpy(before,values,sizeof(values));
 for (unsigned request = 5; request <= 100; request++) {
  header(packet,request,0);
  need(!native_front_params_apply(packet,64,values));
  for (unsigned m = 1; m < 9; m++) {
   if (m == 3) continue;
   unsigned bank = m == 6 || m == 7 ? request&1 : (request+1)&1;
   for (unsigned j = 0; j < (m == 8 ? 4U : 2U); j++)
    need(values[m][j] == bank);
  }
  need(values[0][0] == before[0][0] && values[3][0] == before[3][0]);
  need(values[1][5] == before[1][5] && values[2][4] == before[2][4]);
 }
 header(packet,101,7);
 const unsigned gains[] = {1024,2048,4096,8192};
 const unsigned ratios[] = {8192,6144,2048,2731};
 for (unsigned i=0;i<4;i++) { put(packet,24+2*i,gains[i],2); put(packet,32+4*i,ratios[i],4); }
 put(packet,48,1536,2);
 put(packet,50,2048,2);
 need(!native_front_params_apply(packet,64,values));
 need(values[0][0] == 0x04000800 && values[0][1] == 0x20001000);
 need(values[3][0] == 0x0c000000 && values[3][1] == 0x10000000);
 for (unsigned i=0;i<4;i++) need(values[1][i+2] == ratios[i]);
 memcpy(before,values,sizeof(values));
 for (unsigned size=0;size<64;size++) {
  need(native_front_params_apply(packet,size,values) == -EINVAL);
  need(!memcmp(values,before,sizeof(values)));
 }
 for (unsigned offset=20;offset<64;offset+=4) {
  if (offset>=24 && offset<52) continue;
  memcpy(bad,packet,64);bad[offset]=1;
  need(native_front_params_apply(bad,64,values) == -EINVAL);
  need(!memcmp(values,before,sizeof(values)));
 }
 memcpy(bad,packet,64);put(bad,16,8,4);
 need(native_front_params_apply(bad,64,values) == -EINVAL);
 memcpy(bad,packet,64);put(bad,16,4,4);
 need(native_front_params_apply(bad,64,values) == -EINVAL);
 memcpy(bad,packet,64);put(bad,24,0x8000,2);
 need(native_front_params_apply(bad,64,values) == -ERANGE);
 memcpy(bad,packet,64);put(bad,32,0x40000,4);
 need(native_front_params_apply(bad,64,values) == -ERANGE);
 memcpy(bad,packet,64);put(bad,48,0,2);
 need(native_front_params_apply(bad,64,values) == -ERANGE);
 memcpy(bad,packet,64);put(bad,8,4,8);
 need(native_front_params_apply(bad,64,values) == -ERANGE);
 put(bad,8,0x100000000ULL,8);
 need(native_front_params_apply(bad,64,values) == -ERANGE);
 need(!memcmp(values,before,sizeof(values)));
 header(bad,101,0);put(bad,24,1,2);
 need(native_front_params_apply(bad,64,values) == -EINVAL);
 need(native_front_params_apply(NULL,64,values) == -EINVAL);
 need(native_front_params_apply(packet,64,NULL) == -EINVAL);
 printf("PASS typed front scalar packing/admission: %u checks\n",checks);
 return 0;
}
