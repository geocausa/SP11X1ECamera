/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef SP11_REAR_MANUAL_CONTROLS_H
#define SP11_REAR_MANUAL_CONTROLS_H
#include <cmath>
#include <cstdint>
namespace RearManual {
constexpr int32_t MinLines=4,MaxLines=3206,DefaultLines=1600;
constexpr int32_t MinGainCode=128,MaxGainCode=1024;
constexpr uint64_t PixelRate=432732960,PixelsPerLine=4488;
inline int32_t exposureUs(int32_t lines) {
 return static_cast<int32_t>(std::llround(double(lines)*PixelsPerLine*1000000.0/PixelRate));
}
inline bool exposureLines(int32_t us,int32_t *lines) {
 if (!lines || us<exposureUs(MinLines) || us>exposureUs(MaxLines))return false;
 const auto n=std::llround(double(us)*PixelRate/(PixelsPerLine*1000000.0));
 if(n<MinLines || n>MaxLines)return false;
 *lines=static_cast<int32_t>(n);return true;
}
inline bool gainCode(float gain,int32_t *code) {
 if(!code || !std::isfinite(gain) || gain<1.0f || gain>8.0f)return false;
 const auto n=std::llround(double(gain)*128.0);
 if(n<MinGainCode || n>MaxGainCode)return false;
 *code=static_cast<int32_t>(n);return true;
}
/* Conservative qualification window, not the sensor's entire gain range.
 * One control register is written per ioctl entry: no group-hold/atomic pair
 * or per-request exposure association is claimed.
 */
inline bool sampleSequence(uint32_t n) {
 return (n>=56 && n<80)||(n>=120 && n<144)||(n>=184 && n<208)||(n>=248 && n<272);
}
}
#endif
