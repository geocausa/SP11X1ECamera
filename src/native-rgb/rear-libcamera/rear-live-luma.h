/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef SP11_REAR_LIVE_LUMA_H
#define SP11_REAR_LIVE_LUMA_H
#include "rear-private-optical-v6.h"
namespace RearLiveLuma {
inline double mean(const RearOptical::Layout &layout,
 int (*sync)(int,bool)=RearOptical::syncRead,
 void *(*map)(int,size_t)=RearOptical::mapRead,
 int (*unmap)(void *,size_t)=RearOptical::unmapRead) {
 RearOptical::validate(layout);
 RearOptical::require(lseek(layout.yfd,0,SEEK_END)>=static_cast<off_t>(RearOptical::ImageBytes),"live luma DMA extent");
 RearOptical::require(sync(layout.yfd,true)==0,"live luma CPU START READ");
 void *p=map(layout.yfd,RearOptical::YBytes);
 if(p==MAP_FAILED) {
  (void)sync(layout.yfd,false);
  throw std::runtime_error("live luma readonly mapping");
 }
 uint64_t sum=0;
 const auto *y=static_cast<const uint8_t *>(p);
 for(size_t i=0;i<RearOptical::YBytes;i++)sum+=y[i];
 int u=unmap(p,RearOptical::YBytes),e=sync(layout.yfd,false);
 RearOptical::require(!u && !e,"live luma unmap/CPU END READ");
 return double(sum)/RearOptical::YBytes;
}
}
#endif
