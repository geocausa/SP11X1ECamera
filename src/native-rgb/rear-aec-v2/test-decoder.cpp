/* SPDX-License-Identifier: GPL-2.0-only */
#include "rear-aec-statistics.h"
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <vector>
using namespace RearAec;
static unsigned checks,negatives;
#define CHECK(x) do{checks++;assert(x);}while(0)
static void put(uint8_t *p,uint64_t v){for(unsigned i=0;i<8;i++)p[i]=uint8_t(v>>(8*i));}
int main(){
 std::vector<uint8_t> data(kCapacity);
 for(size_t r=0;r<kRegions;r++)for(unsigned c=0;c<4;c++)put(data.data()+r*kStride+c*8,(kSamples<<48)|((c+1)*300*kSamples));
 Meter out{1,2,3,4};CHECK(!decodeNormal(data.data(),data.size(),&out));
 CHECK(out.r==300&&out.gr==600&&out.gb==900&&out.b==1200);
 auto reject=[&](const uint8_t *p,size_t n){
  Meter before{1,2,3,4},got=before;CHECK(decodeNormal(p,n,&got)<0);CHECK(!memcmp(&before,&got,sizeof(got)));negatives++;
 };
 reject(nullptr,kCapacity);reject(data.data(),0);reject(data.data(),kCapacity-1);reject(data.data(),kCapacity+1);
 CHECK(decodeNormal(data.data(),kCapacity,nullptr)==-EINVAL);negatives++;
 for(size_t r:{0U,1U,511U,1023U})for(unsigned c=0;c<4;c++){
  uint8_t *p=data.data()+r*kStride+c*8;uint64_t old=le64(p);
  for(uint64_t count:{0ULL,1980ULL,2204ULL,2206ULL,65535ULL}){
   put(p,(count<<48)|(old&kSumMask));reject(data.data(),kCapacity);
  }
  put(p,old|(1ULL<<34));reject(data.data(),kCapacity);put(p,old|(1ULL<<47));reject(data.data(),kCapacity);put(p,old);
 }
 CHECK(!decodeNormal(data.data(),kCapacity,&out)&&out.b==1200);
 for(size_t r=0;r<kRegions;r++)for(unsigned c=0;c<4;c++)put(data.data()+r*kStride+c*8,kSamples<<48);
 CHECK(!decodeNormal(data.data(),kCapacity,&out)&&out.r==0&&out.gr==0&&out.gb==0&&out.b==0);
 for(size_t r=0;r<kRegions;r++)for(unsigned c=0;c<4;c++)put(data.data()+r*kStride+c*8,(kSamples<<48)|kSumMask);
 CHECK(!decodeNormal(data.data(),kCapacity,&out));
 CHECK(std::abs(out.r-double(kSumMask)/kSamples)<1e-8);
 printf("{\"status\":\"PASS_ACTUAL_REAR_NORMAL_AEC_DECODER\",\"assertions\":%u,\"negative_cases\":%u}\n",checks,negatives);
}
