/* SPDX-License-Identifier: GPL-2.0-only */
/* Exercise the actual IPA implementation and real shared memfd mappings. */
#include <cmath>
#include <iostream>
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
  std::vector<uint8_t> packet{0xa5};
  if (ipa.computeParameters(6, &packet) != -EINVAL || packet != std::vector<uint8_t>{0xa5} ||
      ipa.computeParameters(5, &packet) ||
      native_front_params_validate(packet.data(), packet.size()) ||
      native_front_stats_u64(packet.data()+8) != 5 ||
      native_front_stats_u32(packet.data()+16) != 0)
   return TestFail;
  auto saved = packet;
  if (ipa.computeParameters(5, &packet) != -EINVAL || packet != saved ||
      ipa.computeParameters(6, &packet))
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
  if (!result(2, 0, 71, 0) || std::abs(luma_ - 49.32134f) > 0.001f)
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
  if (ipa.computeParameters(7, &packet) != -EINVAL || packet != saved)
   return TestFail;
  ipa.processStatistics(1, 71, 1, 1000000999);
  if (!result(6, -EINVAL, 71, 1) || ipa.start() ||
      ipa.computeParameters(5, &packet))
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
