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
                int32_t ret,uint64_t owner,uint64_t generation){
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
  if(ipa.start()!=-EINVAL||ipa.init(s)!=-EINVAL)return TestFail;
  s.sensorModel="ov13858";
  if(ipa.init(s)||ipa.init(s)!=-EINVAL||ipa.start()!=-EINVAL)return TestFail;
  std::vector<IPABuffer> buffers;
  for(uint32_t i=1;i<=8;i++){
   SharedFD fd(memfd_create("rear-statistics-synthetic",MFD_CLOEXEC));
   if(!fd.isValid()||ftruncate(fd.get(),NATIVE_REAR_STATS_BYTES))return TestFail;
   FrameBuffer::Plane p;p.fd=fd;p.offset=0;p.length=NATIVE_REAR_STATS_BYTES;
   buffers.emplace_back(i,std::vector<FrameBuffer::Plane>{p});
  }
  auto bad=buffers;bad[1].id=1;
  if(ipa.mapBuffers(bad)!=-EINVAL||ipa.start()!=-EINVAL)return TestFail;
  bad=buffers;bad[1].planes[0].length--;
  if(ipa.mapBuffers(bad)!=-EINVAL||ipa.start()!=-EINVAL)return TestFail;
  bad=buffers;bad.pop_back();
  if(ipa.mapBuffers(bad)!=-EINVAL||ipa.mapBuffers(buffers)||ipa.start()||
     ipa.start()!=-EINVAL||ipa.mapBuffers(buffers)!=-EINVAL)return TestFail;
  std::array<std::vector<uint8_t>,6> payload;
  std::array<const void *,6> planes;
  std::array<size_t,6> sizes;
  for(unsigned i=0;i<6;i++){payload[i].assign(native_rear_stats_capacity[i],uint8_t(i+1));planes[i]=payload[i].data();sizes[i]=payload[i].size();}
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
  if(ipa.start())return TestFail;
  id.stream=72;id.owner=12;id.sequence=0;id.generation=1;id.timestamp=2000000999;
  if(!write())return TestFail;
  ipa.processStatistics(1,72,0,id.timestamp);
  if(!result(8,0,0,72,id.timestamp)||owner_!=12)return TestFail;
  ipa.stop();ipa.unmapBuffers({1,2,3,4,5,6,7,8});
  if(ipa.start()!=-EINVAL||ipa.mapBuffers(buffers)||ipa.start())return TestFail;
  ipa.stop();ipa.unmapBuffers({1,2,3,4,5,6,7,8});
  std::cout<<"PASS rear actual IPA mappings, atomic admission, foreign/dropped/repeated statistics rejection and restart reset\n";
  return TestPass;
 }
private:
 unsigned calls_=0;
 uint32_t id_=0,sequence_=0;
 uint64_t stream_=0,time_=0,owner_=0,generation_=0;
 int32_t ret_=0;
};
TEST_REGISTER(RearStatisticsIPATest)
