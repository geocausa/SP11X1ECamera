/* SPDX-License-Identifier: GPL-2.0-only */
/* Real IPA class, generated interface, shared memfd mappings and callbacks. */
#include <array>
#include <iostream>
#include <sys/mman.h>
#include <unistd.h>
#include "test.h"
#include "../../../src/ipa/camss-x1e-rear/camss-x1e-rear.cpp"
using namespace libcamera;
class RearStatisticsIPATest : public Test {
 void validated(uint32_t id,uint64_t stream,uint32_t sequence,uint64_t timestamp,
                int32_t ret,uint64_t owner,uint64_t generation,double meter,bool apply,int32_t lines,int32_t gain,bool limited){
  meter_=meter;apply_=apply;lines_=lines;gain_=gain;limited_=limited;
  calls_++;id_=id;stream_=stream;sequence_=sequence;time_=timestamp;
  ret_=ret;owner_=owner;generation_=generation;
 }
 bool result(unsigned calls,int ret,uint32_t seq,uint64_t stream,uint64_t time){
  return calls_==calls&&id_==1&&ret_==ret&&sequence_==seq&&stream_==stream&&time_==time&&
    (ret?(owner_==0&&generation_==0):(owner_!=0&&generation_==uint64_t(seq)+1));
 }
protected:
 int run() override {
  IPACamssX1ERear ipa;
  ipa.statisticsValidated.connect(this,&RearStatisticsIPATest::validated);
  IPASettings s{};s.sensorModel="imx681";
  if(ipa.start(false,1600,128,12000)!=-EINVAL||ipa.init(s)!=-EINVAL)return TestFail;
  s.sensorModel="ov13858";
  if(ipa.init(s)||ipa.init(s)!=-EINVAL||ipa.start(false,1600,128,12000)!=-EINVAL)return TestFail;
  std::vector<IPABuffer> buffers;
  for(uint32_t i=1;i<=8;i++){
   SharedFD fd(memfd_create("rear-statistics-synthetic",MFD_CLOEXEC));
   if(!fd.isValid()||ftruncate(fd.get(),NATIVE_REAR_STATS_BYTES))return TestFail;
   FrameBuffer::Plane p;p.fd=fd;p.offset=0;p.length=NATIVE_REAR_STATS_BYTES;
   buffers.emplace_back(i,std::vector<FrameBuffer::Plane>{p});
  }
  auto bad=buffers;bad[1].id=1;
  if(ipa.mapBuffers(bad)!=-EINVAL||ipa.start(false,1600,128,12000)!=-EINVAL)return TestFail;
  bad=buffers;bad[1].planes[0].length--;
  if(ipa.mapBuffers(bad)!=-EINVAL||ipa.start(false,1600,128,12000)!=-EINVAL)return TestFail;
  bad=buffers;bad.pop_back();
  if(ipa.mapBuffers(bad)!=-EINVAL||ipa.mapBuffers(buffers)||ipa.start(false,1600,128,12000)||
     ipa.start(false,1600,128,12000)!=-EINVAL||ipa.mapBuffers(buffers)!=-EINVAL)return TestFail;
  std::array<std::vector<uint8_t>,6> payload;
  std::array<const void *,6> planes;
  std::array<size_t,6> sizes;
  for(unsigned i=0;i<6;i++){payload[i].assign(native_rear_stats_capacity[i],uint8_t(i+1));planes[i]=payload[i].data();sizes[i]=payload[i].size();}
  for(size_t region=0;region<RearAec::kRegions;region++)for(unsigned channel=0;channel<4;channel++){
   uint64_t word=(RearAec::kSamples<<48)|(600*RearAec::kSamples);
   for(unsigned b=0;b<8;b++)payload[0][region*RearAec::kStride+channel*8+b]=uint8_t(word>>(8*b));
  }
  std::vector<uint8_t> data(NATIVE_REAR_STATS_BYTES);
  native_rear_stats_identity id{71,1000000999,11,1,0,0,19};
  auto write=[&](){
   return !native_rear_stats_pack(data.data(),data.size(),&id,planes.data(),sizes.data())&&
    pwrite(buffers[0].planes[0].fd.get(),data.data(),data.size(),0)==ssize_t(data.size());
  };
  if(!write())return TestFail;
  ipa.processStatistics(1,72,0,id.timestamp);
  if(!result(1,-ESTALE,0,72,id.timestamp))return TestFail;
  ipa.processStatistics(1,71,0,id.timestamp);
  if(!result(2,0,0,71,id.timestamp)||owner_!=11)return TestFail;
  ipa.processStatistics(1,71,0,id.timestamp);
  if(!result(3,-ESTALE,0,71,id.timestamp))return TestFail;
  id.sequence=1;id.generation=2;id.timestamp+=33333333;id.owner=12;
  if(!write())return TestFail;
  ipa.processStatistics(1,71,1,id.timestamp);
  if(!result(4,-ESTALE,1,71,id.timestamp))return TestFail;
  id.owner=11;id.dropped=1;if(!write())return TestFail;
  ipa.processStatistics(1,71,1,id.timestamp);
  if(!result(5,-EPIPE,1,71,id.timestamp))return TestFail;
  id.dropped=0;if(!write())return TestFail;
  /* Running unmap is rejected: the actual mapped buffer remains valid. */
  ipa.unmapBuffers({1});
  ipa.processStatistics(1,71,1,id.timestamp);
  if(!result(6,0,1,71,id.timestamp))return TestFail;
  ipa.stop();
  ipa.processStatistics(1,71,1,id.timestamp);
  if(!result(7,-EINVAL,1,71,id.timestamp))return TestFail;
  if(ipa.start(false,1600,128,12000))return TestFail;
  id.stream=72;id.owner=12;id.sequence=0;id.generation=1;id.timestamp=2000000999;
  if(!write())return TestFail;
  ipa.processStatistics(1,72,0,id.timestamp);
  if(!result(8,0,0,72,id.timestamp)||owner_!=12)return TestFail;
  ipa.stop();ipa.unmapBuffers({1,2,3,4,5,6,7,8});
  if(ipa.start(false,1600,128,12000)!=-EINVAL||ipa.mapBuffers(buffers)||ipa.start(false,1600,128,12000))return TestFail;
  ipa.stop();
  if(ipa.start(true,1600,128,12000))return TestFail;
  unsigned updates=0;uint32_t previous=0;
  id.stream=73;id.owner=13;
  for(uint32_t n=0;n<=32;n++){
   id.sequence=n;id.generation=uint64_t(n)+1;id.timestamp=3000000999+uint64_t(n)*66666666;
   if(!write())return TestFail;
   unsigned before=calls_;ipa.processStatistics(1,73,n,id.timestamp);
   if(!result(before+1,0,n,73,id.timestamp)||meter_!=600||lines_<4||lines_>3206||gain_<128||gain_>2048)return TestFail;
   if(n<8&&apply_)return TestFail;
   if(apply_){
    if(updates&&n-previous<8)return TestFail;
    previous=n;updates++;ipa.controlsApplied(999,n,0);
    ipa.controlsApplied(73,n+1,0);ipa.controlsApplied(73,n,0);
   }
  }
  if(updates<3)return TestFail;
  id.sequence=33;id.generation=34;id.timestamp+=66666666;payload[0][4]^=4;
  if(!write())return TestFail;
  unsigned before=calls_;ipa.processStatistics(1,73,33,id.timestamp);
  if(!result(before+1,-EPROTO,33,73,id.timestamp)||apply_)return TestFail;
  ipa.stop();ipa.unmapBuffers({1,2,3,4,5,6,7,8});
  std::cout<<"PASS rear actual IPA mappings, atomic admission, foreign/dropped/repeated statistics rejection and restart reset\n";
  return TestPass;
 }
private:
 unsigned calls_=0;
 uint32_t id_=0,sequence_=0;
 uint64_t stream_=0,time_=0,owner_=0,generation_=0;
 int32_t ret_=0,lines_=0,gain_=0;
 double meter_=0;bool apply_=false,limited_=false;
};
TEST_REGISTER(RearStatisticsIPATest)
