/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include "native-rear-stats.h"
static unsigned checks,negative;
#define CHECK(x) do { checks++;if(!(x)){fprintf(stderr,"line%d: %s\n",__LINE__,#x);abort();} }while(0)
int main(void){
 const size_t active=81920,pages=(size_t)sysconf(_SC_PAGESIZE);
 CHECK(active%pages==0&&NATIVE_REAR_STATS_BYTES==82016);
 unsigned char *mapping=mmap(NULL,active+pages,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
 void *unreadable=mmap(NULL,pages,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
 CHECK(mapping!=MAP_FAILED&&unreadable!=MAP_FAILED);
 CHECK(!mprotect(mapping+active,pages,PROT_NONE));
 memset(mapping,0x53,active);
 const void *planes[6]={mapping,unreadable,unreadable,unreadable,unreadable,unreadable};
 size_t sizes[6];for(unsigned i=0;i<6;i++)sizes[i]=native_rear_stats_capacity[i];
 unsigned char *output=malloc(NATIVE_REAR_STATS_BYTES+32),*sentinel=malloc(NATIVE_REAR_STATS_BYTES+32);
 CHECK(output&&sentinel);memset(output,0xa7,NATIVE_REAR_STATS_BYTES+32);memset(sentinel,0xa7,NATIVE_REAR_STATS_BYTES+32);
 struct native_rear_stats_identity id={9,123456789,7,1,0,0,37};
 CHECK(!native_rear_stats_pack(output+16,NATIVE_REAR_STATS_BYTES,&id,planes,sizes));
 CHECK(!memcmp(output,sentinel,16)&&!memcmp(output+16+NATIVE_REAR_STATS_BYTES,sentinel,16));
 CHECK(!memcmp(output+16+96,mapping,active));
 CHECK(!native_rear_stats_validate(output+16,NATIVE_REAR_STATS_BYTES,9,0,id.timestamp));
 CHECK(native_rear_stats_u32(output+16)==0x32415851U);
 for(unsigned i=0;i<6;i++)CHECK(native_rear_stats_u32(output+16+60+4*i)==(i?0:active));
 for(unsigned i=0;i<6;i++){
  const void *saved=planes[i];planes[i]=NULL;memcpy(output,sentinel,NATIVE_REAR_STATS_BYTES+32);
  CHECK(native_rear_stats_pack(output+16,NATIVE_REAR_STATS_BYTES,&id,planes,sizes)<0);
  CHECK(!memcmp(output,sentinel,NATIVE_REAR_STATS_BYTES+32));planes[i]=saved;negative++;
  sizes[i]--;CHECK(native_rear_stats_pack(output+16,NATIVE_REAR_STATS_BYTES,&id,planes,sizes)<0);
  CHECK(!memcmp(output,sentinel,NATIVE_REAR_STATS_BYTES+32));sizes[i]++;negative++;
 }
 CHECK(!native_rear_stats_pack(output+16,NATIVE_REAR_STATS_BYTES,&id,planes,sizes));
 native_rear_stats_put(output+16,0x31525851,4);
 CHECK(native_rear_stats_validate(output+16,NATIVE_REAR_STATS_BYTES,9,0,id.timestamp)<0);negative++;
 free(output);free(sentinel);CHECK(!munmap(mapping,active+pages));CHECK(!munmap(unreadable,pages));
 printf("{\"status\":\"PASS_EXACT_ACTIVE_PREFIX_AND_NO_OTHER_DMA_READ\",\"assertions\":%u,\"negative_cases\":%u,\"guard_page_tail_and_absent_planes\":true,\"output_canaries\":true}\n",checks,negative);
 return 0;
}
