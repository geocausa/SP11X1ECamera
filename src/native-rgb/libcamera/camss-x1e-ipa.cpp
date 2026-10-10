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

#include <libcamera/base/file.h>
#include "libcamera/internal/yaml_parser.h"
#include "libcamera/internal/mapped_framebuffer.h"
extern "C" {
#include "libipa/native-front-isp-params.h"
}
#include "libipa/camss_x1e_helpers.h"

namespace libcamera {
class IPACamssX1E final : public ipa::camss_x1e::IPACamssX1EInterface
{
public:
 int init(const IPASettings &settings) override
 {
  if (running_ || !buffers_.empty() || settings.sensorModel != "imx681")
   return -EINVAL;
  std::vector<uint8_t> candidate(NF_ISP_HEADER_BYTES);
  int ret = native_front_isp_encode(nullptr, 0, candidate.data(), candidate.size());
  if (!settings.configurationFile.empty()) {
   File file(settings.configurationFile);
   if (!file.open(File::OpenModeFlag::ReadOnly))
    return file.error();
   auto data = YamlParser::parse(file);
   if (!data || !data->isDictionary() || data->size() != 6 ||
       (*data)["version"].get<uint32_t>(0) != 1 ||
       (*data)["sensor"].get<std::string>("") != "imx681" ||
       (*data)["layout"].get<std::string>("") != "rgb257-u10") return -EINVAL;
   std::array<uint16_t, NF_GAMMA_POINT_COUNT> points{};
   size_t at = 0;
   for (const char *key : {"gamma_r", "gamma_g", "gamma_b"}) {
    auto values = (*data)[key].getList<uint16_t>();
    if (!values || values->size() != NF_GAMMA_POINTS) return -EINVAL;
    for (uint16_t value : *values) points[at++] = value;
   }
   candidate.resize(NF_ISP_MAX_BYTES);
   ret = native_front_isp_encode(points.data(), points.size(),
                                 candidate.data(), candidate.size());
  }
  if (ret) return ret;
  ispTemplate_ = std::move(candidate);
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

 int computeParameters(uint64_t request, std::vector<uint8_t> *packet,
                       std::vector<uint8_t> *ispPacket) override
 {
  if (!packet || !ispPacket || packet == ispPacket || !running_ ||
      request != nextParameter_ || request > 0xffffffffULL)
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
  *ispPacket = ispTemplate_;
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
 std::vector<uint8_t> ispTemplate_;
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
