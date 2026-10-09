/* SPDX-License-Identifier: GPL-2.0-only */
#include <cassert>
#include <cstdlib>
#include <cstdio>
#include <array>
#include <vector>
#include <algorithm>
#include "rear-statistics-receiver.h"
static unsigned checks=0,negatives=0;
#define CHECK(x) do{checks++;if(!(x)){std::fprintf(stderr,"check %u line %d failed\n",checks,__LINE__);std::abort();}}while(0)
int main(){
 std::array<std::vector<uint8_t>,6> storage;
 std::array<const void *,6> planes;
 std::array<size_t,6> sizes;
 for(unsigned i=0;i<6;i++){
  storage[i].assign(native_rear_stats_capacity[i],uint8_t(0x31+i));
  planes[i]=storage[i].data();sizes[i]=storage[i].size();
 }
 std::vector<uint8_t> wire(NATIVE_REAR_STATS_BYTES),sentinel(wire.size(),0xa7);
 native_rear_stats_identity id{9,123456789,7,1,0,0,37};
 auto make=[&](uint32_t seq){
  id.sequence=seq;id.generation=uint64_t(seq)+1;id.timestamp=123456789+uint64_t(seq)*33333333;
  CHECK(native_rear_stats_pack(wire.data(),wire.size(),&id,planes.data(),sizes.data())==0);
 };
 make(0);
 CHECK(wire[0]=='Q'&&wire[1]=='X'&&wire[2]=='A'&&wire[3]=='2');
 CHECK(wire[4]==2&&wire[5]==0&&wire[6]==96&&wire[7]==0);
 CHECK(wire.size()==82016);
 CHECK(std::all_of(wire.begin()+96,wire.end(),[](uint8_t b){return b==0x31;}));
 CHECK(native_rear_stats_u32(wire.data()+60)==81920);
 for(unsigned i=1;i<6;i++)CHECK(native_rear_stats_u32(wire.data()+60+4*i)==0);
 CHECK(native_rear_stats_u32(wire.data()+84)==(1U<<11));
 CHECK(native_rear_stats_validate(wire.data(),wire.size(),9,0,id.timestamp)==0);
 CHECK(native_rear_stats_validate(wire.data(),wire.size(),9,0,id.timestamp/1000*1000)==0);
 auto badPack=[&](size_t bytes){
  wire=sentinel;
  CHECK(native_rear_stats_pack(wire.data(),bytes,&id,planes.data(),sizes.data())!=0);
  CHECK(wire==sentinel);negatives++;
 };
 for(size_t n:{size_t(0),size_t(95),size_t(96),wire.size()-1,wire.size()+1})badPack(n);
 for(unsigned i=0;i<6;i++){
  auto p=planes[i];planes[i]=nullptr;badPack(wire.size());planes[i]=p;
  sizes[i]--;badPack(wire.size());sizes[i]+=2;badPack(wire.size());sizes[i]--;
 }
 for(unsigned i=0;i<5;i++){
  auto saved=id;
  if(i==0)id.stream=0;
  if(i==1)id.timestamp=0;
  if(i==2)id.owner=0;
  if(i==3)id.generation=2;
  if(i==4)id.cursor=0;
  badPack(wire.size());id=saved;
 }
 make(0);
 auto good=wire;
 auto rejectMutation=[&](unsigned off,unsigned width,uint64_t value){
  wire=good;native_rear_stats_put(wire.data()+off,value,width);
  CHECK(native_rear_stats_validate(wire.data(),wire.size(),9,0,id.timestamp)!=0);
  negatives++;
 };
 rejectMutation(0,4,0);rejectMutation(4,2,1);rejectMutation(6,2,64);
 rejectMutation(8,8,10);rejectMutation(16,8,id.timestamp+1000);
 rejectMutation(24,8,0);rejectMutation(32,8,2);rejectMutation(40,4,1);
 rejectMutation(44,4,0);rejectMutation(48,8,1);
 for(unsigned f:{0U,1U,2U,3U,5U,0xffffffffU})rejectMutation(56,4,f);
 for(unsigned i=0;i<6;i++)rejectMutation(60+4*i,4,native_rear_stats_payload_length[i]+1);
 rejectMutation(84,4,0);rejectMutation(88,8,1);
 RearStatisticsReceiver receiver;
 uint64_t owner=0xaaaa,generation=0xbbbb;
 make(0);
 CHECK(receiver.accept(wire.data(),wire.size(),9,0,id.timestamp,&owner,&generation)==0);
 CHECK(owner==7&&generation==1);
 owner=0xaaaa;generation=0xbbbb;
 CHECK(receiver.accept(wire.data(),wire.size(),9,0,id.timestamp,&owner,&generation)==-ESTALE);
 CHECK(owner==0xaaaa&&generation==0xbbbb);negatives++;
 make(2);
 CHECK(receiver.accept(wire.data(),wire.size(),9,2,id.timestamp,&owner,&generation)==-ESTALE);negatives++;
 make(1);id.owner=8;CHECK(native_rear_stats_pack(wire.data(),wire.size(),&id,planes.data(),sizes.data())==0);
 CHECK(receiver.accept(wire.data(),wire.size(),9,1,id.timestamp,&owner,&generation)==-ESTALE);negatives++;
 id.owner=7;id.stream=10;make(1);
 CHECK(receiver.accept(wire.data(),wire.size(),10,1,id.timestamp,&owner,&generation)==-ESTALE);negatives++;
 id.stream=9;make(1);native_rear_stats_put(wire.data()+16,123456789,8);
 CHECK(receiver.accept(wire.data(),wire.size(),9,1,123456789,&owner,&generation)==-ESTALE);negatives++;
 make(1);id.dropped=1;CHECK(native_rear_stats_pack(wire.data(),wire.size(),&id,planes.data(),sizes.data())==0);
 CHECK(receiver.accept(wire.data(),wire.size(),9,1,id.timestamp,&owner,&generation)==-EPIPE);negatives++;
 id.dropped=0;make(1);
 CHECK(receiver.accept(wire.data(),wire.size(),9,1,id.timestamp,&owner,&generation)==0);
 CHECK(owner==7&&generation==2);
 receiver.reset();id.stream=10;id.owner=8;make(0);
 CHECK(receiver.accept(wire.data(),wire.size(),10,0,id.timestamp,&owner,&generation)==0);
 CHECK(owner==8&&generation==1);
 CHECK(receiver.accept(nullptr,wire.size(),10,1,id.timestamp,&owner,&generation)!=0);negatives++;
 CHECK(receiver.accept(wire.data(),wire.size(),10,0,id.timestamp,nullptr,&generation)!=0);negatives++;
 std::printf("{\"status\":\"PASS_COMPACT_AEC_V2_RECEIVER\",\"assertions\":%u,\"negative_cases\":%u}\n",checks,negatives);
}
