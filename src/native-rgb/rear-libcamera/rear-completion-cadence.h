/* SPDX-License-Identifier: GPL-2.0-only */
/* Driver completion timing aggregates only; no pixel access or sensor SOF claim. */
#pragma once
#include <cstdint>
struct RearCompletionCadence {
 uint64_t first = 0, previous = 0, prefixLast = 0;
 uint64_t prefixMin = 0, prefixMax = 0, maximum = 0;
 unsigned count = 0, longGaps = 0, lateLongGaps = 0;
 unsigned firstLongSequence = 0, maximumSequence = 0;
 void observe(uint64_t timestamp, unsigned sequence)
 {
  if (!sequence) {
   first = timestamp;
  } else {
   const uint64_t gap = timestamp - previous;
   if (gap > maximum) { maximum = gap; maximumSequence = sequence; }
   if (gap > 50000000ULL) {
    if (!longGaps) firstLongSequence = sequence;
    longGaps++;
    if (sequence >= 80U) lateLongGaps++;
   }
   if (sequence < 80U) {
    if (!prefixMin || gap < prefixMin) prefixMin = gap;
    if (gap > prefixMax) prefixMax = gap;
   }
  }
  if (sequence < 80U) prefixLast = timestamp;
  previous = timestamp;
  count++;
 }
};
