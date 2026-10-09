/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef REAR_STATISTICS_RECEIVER_H
#define REAR_STATISTICS_RECEIVER_H
#include <cstdint>
#include "native-rear-stats.h"
/* Shared actual IPA admission state. No payload decoding or metering claim.
 * Failed envelopes publish no receipt and never advance owner/sequence.
 */
class RearStatisticsReceiver {
public:
 void reset() { stream_=owner_=0; next_=0; lastTimestamp_=0; }
 int accept(const void *data,size_t bytes,uint64_t stream,uint32_t sequence,
            uint64_t timestamp,uint64_t *owner,uint64_t *generation) {
  if(!owner||!generation)return -EINVAL;
  int ret=native_rear_stats_validate(data,bytes,stream,sequence,timestamp);
  if(ret)return ret;
  const auto *p=static_cast<const uint8_t *>(data);
  uint64_t foundOwner=native_rear_stats_u64(p+24);
  uint64_t foundTime=native_rear_stats_u64(p+16);
  if(sequence!=next_||(stream_&&stream!=stream_)||
     (owner_&&foundOwner!=owner_)||foundTime<=lastTimestamp_)
   return -ESTALE;
  if(next_==UINT32_MAX-1)return -EOVERFLOW;
  stream_=stream;owner_=foundOwner;lastTimestamp_=foundTime;next_++;
  *owner=foundOwner;*generation=native_rear_stats_u64(p+32);
  return 0;
 }
private:
 uint64_t stream_=0,owner_=0,lastTimestamp_=0;
 uint32_t next_=0;
};
#endif
