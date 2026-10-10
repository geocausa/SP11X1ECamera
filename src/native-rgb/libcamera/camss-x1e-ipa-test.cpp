/* SPDX-License-Identifier: GPL-2.0-only */
/* Exercise the actual IPA implementation and real shared memfd mappings. */
#include <cmath>
#include <iostream>
#include <sstream>
#include <sys/mman.h>
#include <unistd.h>
#include "test.h"
#include "../../../src/ipa/camss-x1e/camss-x1e.cpp"

using namespace libcamera;

class CamssX1EIPATest : public Test
{
 void ready(uint32_t buffer, uint64_t stream, uint32_t sequence,
            uint64_t timestamp, int32_t ret, float luma)
 {
  calls_++;
  buffer_ = buffer;
  stream_ = stream;
  sequence_ = sequence;
  timestamp_ = timestamp;
  ret_ = ret;
  luma_ = luma;
 }
 bool result(uint32_t calls, int ret, uint64_t stream, uint32_t sequence)
 {
  return calls_ == calls && buffer_ == 1 && ret_ == ret &&
         stream_ == stream && sequence_ == sequence && timestamp_ == 1000000999;
 }
 static void le(std::vector<uint8_t> &data, size_t at, uint64_t value, size_t bytes)
 {
  for (size_t i = 0; i < bytes; i++)
   data[at+i] = value >> (8*i);
 }
protected:
 int run() override
 {
  IPACamssX1E ipa;
  ipa.statisticsProcessed.connect(this, &CamssX1EIPATest::ready);
  IPASettings settings{};
  settings.sensorModel = "other";
  if (ipa.start() != -EINVAL || ipa.init(settings) != -EINVAL)
   return TestFail;
  settings.sensorModel = "imx681";
  if (ipa.init(settings) || ipa.start() != -EINVAL)
   return TestFail;
  std::vector<IPABuffer> buffers;
  for (uint32_t i = 1; i <= 8; i++) {
   SharedFD fd(memfd_create("camss-x1e-ipa-test", MFD_CLOEXEC));
   if (!fd.isValid() || ftruncate(fd.get(), NATIVE_FRONT_STATS_BYTES))
    return TestFail;
   FrameBuffer::Plane plane;
   plane.fd = fd;
   plane.offset = 0;
   plane.length = NATIVE_FRONT_STATS_BYTES;
   buffers.emplace_back(i, std::vector<FrameBuffer::Plane>{ plane });
  }
  auto invalid = buffers;
  invalid[1].id = 1;
  if (ipa.mapBuffers(invalid) != -EINVAL || ipa.start() != -EINVAL ||
      ipa.mapBuffers(buffers) || ipa.start() || ipa.start() != -EINVAL)
   return TestFail;
  std::vector<uint8_t> packet{0xa5}, ispPacket{0xa6};
  if (ipa.computeParameters(6, &packet, &ispPacket) != -EINVAL || packet != std::vector<uint8_t>{0xa5} ||
      ipa.computeParameters(5, &packet, &ispPacket) ||
      native_front_params_validate(packet.data(), packet.size()) ||
      native_front_stats_u64(packet.data()+8) != 5 ||
      native_front_stats_u32(packet.data()+16) != 0)
   return TestFail;
  if (ispPacket.size() != NF_ISP_HEADER_BYTES || nf_gamma_get32(ispPacket.data()+4)) return TestFail;
  auto saved = packet;
  if (ipa.computeParameters(5, &packet, &ispPacket) != -EINVAL || packet != saved ||
      ipa.computeParameters(6, &packet, &ispPacket))
   return TestFail;

  std::vector<uint8_t> data(NATIVE_FRONT_STATS_BYTES);
  le(data, 0, NATIVE_FRONT_STATS_MAGIC, 4);
  le(data, 4, 1, 2);
  le(data, 6, NATIVE_FRONT_STATS_HEADER_BYTES, 2);
  le(data, 8, 71, 8);
  le(data, 16, 1000000999, 8);
  le(data, 28, 1, 4);
  le(data, 44, NATIVE_FRONT_STATS_AEC_BYTES, 4);
  le(data, 48, NATIVE_FRONT_STATS_BHIST_BYTES, 4);
  le(data, 52, NATIVE_FRONT_STATS_AWB_BYTES, 4);
  le(data, 56, NATIVE_FRONT_STATS_TLBG_BYTES, 4);
  for (size_t region = 0; region < 1024; region++) {
   for (size_t offset : {0x06, 0x0e, 0x16, 0x1e})
    le(data, 64 + region*0x50 + offset, 1980, 2);
   for (size_t offset : {0x00, 0x08, 0x10, 0x18})
    le(data, 64 + region*0x50 + offset, 100000000, 5);
  }
  auto write = [&]() {
   return pwrite(buffers[0].planes[0].fd.get(), data.data(), data.size(), 0) ==
          ssize_t(data.size());
  };
  if (!write())
   return TestFail;
  ipa.processStatistics(1, 72, 0, 1000000999);
  if (!result(1, -ESTALE, 72, 0))
   return TestFail;
  ipa.processStatistics(1, 71, 0, 1000000999);
  if (!result(2, 0, 71, 0) || std::abs(luma_ - float(100000000.0/1980.0)) > 0.01f)
   return TestFail;
  ipa.processStatistics(1, 71, 0, 1000000999);
  if (!result(3, -EINVAL, 71, 0))
   return TestFail;
  le(data, 24, 1, 4);
  le(data, 28, 2, 4);
  le(data, 64+6, 0, 2);
  if (!write())
   return TestFail;
  ipa.processStatistics(1, 71, 1, 1000000999);
  if (!result(4, -EINVAL, 71, 1))
   return TestFail;
  le(data, 64+6, 1980, 2);
  if (!write())
   return TestFail;
  ipa.processStatistics(1, 71, 1, 1000000999);
  if (!result(5, 0, 71, 1))
   return TestFail;
  ipa.stop();
  saved = packet;
  if (ipa.computeParameters(7, &packet, &ispPacket) != -EINVAL || packet != saved)
   return TestFail;
  ipa.processStatistics(1, 71, 1, 1000000999);
  if (!result(6, -EINVAL, 71, 1) || ipa.start() ||
      ipa.computeParameters(5, &packet, &ispPacket))
   return TestFail;
  le(data, 8, 72, 8);
  le(data, 24, 0, 4);
  le(data, 28, 1, 4);
  if (!write())
   return TestFail;
  ipa.processStatistics(1, 72, 0, 1000000999);
  if (!result(7, 0, 72, 0))
   return TestFail;
  ipa.stop();
  ipa.unmapBuffers({1,2,3,4,5,6,7,8});
  if (ipa.start() != -EINVAL)
   return TestFail;
  /* Synthetic independent tuning only: actual YAML reader, real shared
   * mappings, actual IPA encoder. No camera image or OEM tuning. */
  auto configure = [&](IPACamssX1E &target, const std::string &yaml) {
   char path[] = "/tmp/camss-x1e-tuning-test-XXXXXX";
   int fd = mkstemp(path);
   if (fd < 0) return -EIO;
   ssize_t n = ::write(fd, yaml.data(), yaml.size());
   close(fd);
   if (n != ssize_t(yaml.size())) { unlink(path); return -EIO; }
   IPASettings tune{};
   tune.sensorModel = "imx681";
   tune.configurationFile = path;
   int ret = target.init(tune);
   unlink(path);
   return ret;
  };
  std::ostringstream yaml;
  yaml << "version: 1\nsensor: imx681\nlayout: rgb257-u10\n";
  std::array<uint16_t, NF_GAMMA_POINT_COUNT> points{};
  size_t at = 0;
  for (unsigned c = 0; c < 3; c++) {
   yaml << (c == 0 ? "gamma_r: [" : c == 1 ? "gamma_g: [" : "gamma_b: [");
   for (unsigned i = 0; i < 257; i++) {
    points[at] = 100*c + 3*i;
    yaml << (i ? ", " : "") << points[at++];
   }
   yaml << "]\n";
  }
  IPACamssX1E tuned;
  auto valid = yaml.str();
  for (const std::string &bad : {
       std::string("version: 1\n"),
       std::string(valid + "unsupported: true\n"),
       std::string("version: 2") + valid.substr(10),
       std::string(valid).replace(valid.find("gamma_b: [200"), 13, "gamma_b: [1024")}) {
   if (configure(tuned, bad) == 0 || tuned.start() != -EINVAL) return TestFail;
  }
  if (configure(tuned, valid) || tuned.mapBuffers(buffers) || tuned.start())
   return TestFail;
  std::vector<uint8_t> scalar{0xa5}, isp{0xa6}, expected(NF_ISP_MAX_BYTES);
  if (tuned.computeParameters(6, &scalar, &isp) != -EINVAL ||
      scalar != std::vector<uint8_t>{0xa5} || isp != std::vector<uint8_t>{0xa6} ||
      native_front_isp_encode(points.data(), points.size(), expected.data(), expected.size()) ||
      tuned.computeParameters(5, &scalar, &isp) || isp != expected)
   return TestFail;
  auto prior = isp;
  if (tuned.computeParameters(6, &scalar, &scalar) != -EINVAL ||
      isp != prior || tuned.computeParameters(6, &scalar, &isp) || isp != expected)
   return TestFail;
  tuned.stop();
  tuned.unmapBuffers({1,2,3,4,5,6,7,8});
  std::cout << "PASS actual IPA: shared mappings, atomic admission, typed order, "
               "metering, stale/duplicate/malformed rejection and restart reset\\n";
  return TestPass;
 }
private:
 uint32_t calls_ = 0, buffer_ = 0, sequence_ = 0;
 uint64_t stream_ = 0, timestamp_ = 0;
 int32_t ret_ = 0;
 float luma_ = 0.0f;
};
TEST_REGISTER(CamssX1EIPATest)
