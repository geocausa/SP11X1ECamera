/* SPDX-License-Identifier: GPL-2.0-only */
/* Native hardware-statistics IPA. Fixed typed defaults; no automatic feedback. */
#include <array>
#include <cerrno>
#include <cstdint>
#include <map>
#include <memory>
#include <vector>

#include <libcamera/ipa/camss_x1e_ipa_interface.h>
#include <libcamera/ipa/ipa_module_info.h>

#include "libcamera/internal/mapped_framebuffer.h"
#include "libipa/camss_x1e_helpers.h"

namespace libcamera {
class IPACamssX1E final : public ipa::camss_x1e::IPACamssX1EInterface
{
public:
 int init(const IPASettings &settings) override
 {
  if (running_ || settings.sensorModel != "imx681" ||
      !settings.configurationFile.empty())
   return -EINVAL;
  initialized_ = true;
  return 0;
 }

 int mapBuffers(const std::vector<IPABuffer> &buffers) override
 {
  if (!initialized_ || running_ || !buffers_.empty() || buffers.size() != 8)
   return -EINVAL;
  std::map<uint32_t, std::unique_ptr<MappedFrameBuffer>> pending;
  for (const IPABuffer &buffer : buffers) {
   if (!buffer.id || pending.count(buffer.id) || buffer.planes.size() != 1 ||
       buffer.planes[0].length < NATIVE_FRONT_STATS_BYTES)
    return -EINVAL;
   FrameBuffer fb(buffer.planes);
   auto map = std::make_unique<MappedFrameBuffer>(&fb, MappedFrameBuffer::MapFlag::Read);
   if (!map->isValid() || map->planes().size() != 1 ||
       map->planes()[0].size() < NATIVE_FRONT_STATS_BYTES)
    return -EINVAL;
   pending.emplace(buffer.id, std::move(map));
  }
  buffers_ = std::move(pending);
  return 0;
 }

 void unmapBuffers(const std::vector<uint32_t> &ids) override
 {
  if (running_)
   return;
  for (uint32_t id : ids)
   buffers_.erase(id);
 }

 int start() override
 {
  if (!initialized_ || running_ || buffers_.size() != 8)
   return -EINVAL;
  stream_ = 0;
  nextSequence_ = 0;
  nextParameter_ = 5;
  running_ = true;
  return 0;
 }
 void stop() override { running_ = false; }

 int computeParameters(uint64_t request, std::vector<uint8_t> *packet) override
 {
  if (!packet || !running_ || request != nextParameter_)
   return -EINVAL;
  const std::array<uint16_t, 4> demux{};
  const std::array<uint32_t, 4> pdpc{};
  const std::array<uint16_t, 2> wb{};
  native_front_params parameters;
  int ret = ipa::camssX1EFrontParameters(request, 0, demux, pdpc, wb, &parameters);
  if (ret)
   return ret;
  const auto *bytes = reinterpret_cast<const uint8_t *>(&parameters);
  packet->assign(bytes, bytes + sizeof(parameters));
  nextParameter_++;
  return 0;
 }

 void processStatistics(uint32_t bufferId, uint64_t stream,
                        uint32_t sequence, uint64_t timestamp) override
 {
  float luma = 0.0f;
  int ret = -EINVAL;
  auto it = buffers_.find(bufferId);
  if (running_ && it != buffers_.end() && stream &&
      sequence == nextSequence_ && (!stream_ || stream == stream_)) {
   const auto &plane = it->second->planes()[0];
   ret = ipa::camssX1EFrameLuma(
       Span<const uint8_t>(plane.data(), NATIVE_FRONT_STATS_BYTES),
       stream, sequence, timestamp, &luma);
   if (!ret) {
    stream_ = stream;
    nextSequence_++;
   }
  }
  statisticsProcessed.emit(bufferId, stream, sequence, timestamp, ret, luma);
 }
private:
 bool initialized_ = false;
 bool running_ = false;
 uint64_t stream_ = 0;
 uint64_t nextParameter_ = 5;
 uint32_t nextSequence_ = 0;
 std::map<uint32_t, std::unique_ptr<MappedFrameBuffer>> buffers_;
};

extern "C" {
extern const IPAModuleInfo ipaModuleInfo = {
 IPA_MODULE_API_VERSION, 0, "camss-x1e", "camss-x1e",
};
IPAInterface *ipaCreate() { return new IPACamssX1E(); }
}
} /* namespace libcamera */
