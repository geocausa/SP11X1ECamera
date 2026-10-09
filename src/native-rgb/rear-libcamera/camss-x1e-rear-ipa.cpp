/* SPDX-License-Identifier: GPL-2.0-only */
/* Rear hardware statistics envelope admission. No AE or photometric decoder. */
#include <cerrno>
#include <map>
#include <memory>
#include <vector>
#include <libcamera/ipa/camss_x1e_rear_ipa_interface.h>
#include <libcamera/ipa/ipa_module_info.h>
#include "libcamera/internal/mapped_framebuffer.h"
#include "rear-statistics-receiver.h"
namespace libcamera {
class IPACamssX1ERear final : public ipa::camss_x1e_rear::IPACamssX1ERearInterface {
public:
 int init(const IPASettings &s) override {
  if(initialized_||running_||s.sensorModel!="ov13858"||!s.configurationFile.empty())
   return -EINVAL;
  initialized_=true;return 0;
 }
 int mapBuffers(const std::vector<IPABuffer> &buffers) override {
  if(!initialized_||running_||!buffers_.empty()||buffers.size()!=8)return -EINVAL;
  std::map<uint32_t,std::unique_ptr<MappedFrameBuffer>> pending;
  for(const auto &b:buffers){
   if(!b.id||pending.count(b.id)||b.planes.size()!=1||
      b.planes[0].length<NATIVE_REAR_STATS_BYTES)return -EINVAL;
   FrameBuffer fb(b.planes);
   auto map=std::make_unique<MappedFrameBuffer>(&fb,MappedFrameBuffer::MapFlag::Read);
   if(!map->isValid()||map->planes().size()!=1||
      map->planes()[0].size()<NATIVE_REAR_STATS_BYTES)return -EINVAL;
   pending.emplace(b.id,std::move(map));
  }
  buffers_=std::move(pending);return 0;
 }
 void unmapBuffers(const std::vector<uint32_t> &ids) override {
  if(running_)return;
  for(uint32_t id:ids)buffers_.erase(id);
 }
 int start() override {
  if(!initialized_||running_||buffers_.size()!=8)return -EINVAL;
  receiver_.reset();running_=true;return 0;
 }
 void stop() override { running_=false;receiver_.reset(); }
 void processStatistics(uint32_t id,uint64_t stream,uint32_t seq,uint64_t ts) override {
  int ret=-EINVAL;
  uint64_t owner=0,generation=0;
  auto it=buffers_.find(id);
  if(running_&&it!=buffers_.end()){
   auto &plane=it->second->planes()[0];
   ret=receiver_.accept(plane.data(),NATIVE_REAR_STATS_BYTES,stream,seq,ts,&owner,&generation);
  }
  statisticsValidated.emit(id,stream,seq,ts,ret,owner,generation);
 }
private:
 bool initialized_=false,running_=false;
 RearStatisticsReceiver receiver_;
 std::map<uint32_t,std::unique_ptr<MappedFrameBuffer>> buffers_;
};
extern "C" {
extern const IPAModuleInfo ipaModuleInfo={IPA_MODULE_API_VERSION,0,"camss-x1e-rear","camss-x1e-rear"};
IPAInterface *ipaCreate(){return new IPACamssX1ERear();}
}
}
