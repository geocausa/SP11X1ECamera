/* SPDX-License-Identifier: GPL-2.0-only */
#pragma once
#include <cerrno>
#include <cstddef>
#include <cstdint>
namespace RearAec {
/* Current rear normal32x32 grid: even126x70 Bayer cells,2205 samples/channel.
 * 80-byte records share the admitted front AEC sum/count field layout.
 * Opaque extra fields and allocated tail remain uninterpreted.
 * Raw sum/count means have NO declared bit depth, black subtraction, target,
 * display transform, color calibration or same-exposure metadata association.
 */
constexpr size_t kCapacity=0xa0000,kRegions=32*32,kStride=80;
constexpr uint64_t kSamples=2205,kSumMask=0x3ffffffffULL;
struct Meter {double r=0,gr=0,gb=0,b=0;};
inline uint64_t le64(const uint8_t *p){
 uint64_t out=0;for(unsigned i=0;i<8;i++)out|=uint64_t(p[i])<<(8*i);return out;
}
inline int decodeNormal(const uint8_t *data,size_t bytes,Meter *out){
 if(!data||!out||bytes!=kCapacity)return -EINVAL;
 uint64_t total[4]={};
 for(size_t region=0;region<kRegions;region++)for(unsigned channel=0;channel<4;channel++){
  uint64_t value=le64(data+region*kStride+channel*8);
  if((value>>48)!=kSamples||(value&0x0000fffc00000000ULL))return -EPROTO;
  total[channel]+=value&kSumMask;
 }
 const double denominator=double(kSamples*kRegions);
 Meter pending{total[0]/denominator,total[1]/denominator,total[2]/denominator,total[3]/denominator};
 *out=pending;return 0;
}
}
