/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native-front-stats.h"
static unsigned checks;
static void put(unsigned char *p, unsigned offset, uint64_t value, unsigned bytes)
{
 for (unsigned i = 0; i < bytes; i++)
  p[offset + i] = value >> (8*i);
}
static void need(int value) { checks++; assert(value); }
int main(void)
{
 unsigned char *raw = calloc(1, NATIVE_FRONT_STATS_BYTES + 1);
 need(raw != NULL);
 need(sizeof(struct native_front_stats_header) == 64);
 put(raw,0,NATIVE_FRONT_STATS_MAGIC,4);
 put(raw,4,NATIVE_FRONT_STATS_VERSION,2);
 put(raw,6,NATIVE_FRONT_STATS_HEADER_BYTES,2);
 put(raw,8,67,8);
 put(raw,16,2345678901ULL,8);
 put(raw,24,0,4);
 put(raw,28,109,4);
 put(raw,44,NATIVE_FRONT_STATS_AEC_BYTES,4);
 put(raw,48,NATIVE_FRONT_STATS_BHIST_BYTES,4);
 put(raw,52,NATIVE_FRONT_STATS_AWB_BYTES,4);
 put(raw,56,NATIVE_FRONT_STATS_TLBG_BYTES,4);
 need(!native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,67,0));
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,68,0) == -ESTALE);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,67,1) == -ESTALE);
 for (size_t size = 0; size < 64; size++)
  need(native_front_stats_validate(raw,size,67,0) == -EINVAL);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES-1,67,0) == -EINVAL);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES+1,67,0) == -EINVAL);
 need(native_front_stats_validate(NULL,NATIVE_FRONT_STATS_BYTES,67,0) == -EINVAL);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,0,0) == -EINVAL);
 /* Corruption in structural words, while leaving the stored payload untouched. */
 const unsigned offsets[] = {0,4,6,16,28,44,48,52,56,60};
 for (unsigned i = 0; i < sizeof(offsets)/sizeof(offsets[0]); i++) {
  unsigned offset = offsets[i];
  unsigned char saved = raw[offset];
  raw[offset] ^= 0x80;
  /* Altering one nonzero timestamp/source counter remains a valid envelope. */
  if (offset != 16 && offset != 28)
   need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,67,0) == -EINVAL);
  raw[offset] = saved;
 }
 put(raw,16,0,8);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,67,0) == -EINVAL);
 put(raw,16,2345678901ULL,8);
 put(raw,28,0,4);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,67,0) == -EINVAL);
 put(raw,28,109,4);
 put(raw,40,2,4);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,67,0) == -EINVAL);
 put(raw,40,1,4);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,67,0) == -EPIPE);
 put(raw,40,0,4);
 put(raw,32,1,8);
 need(native_front_stats_validate(raw,NATIVE_FRONT_STATS_BYTES,67,0) == -EPIPE);
 free(raw);
 printf("PASS native frame statistics identity/framing: %u checks\n",checks);
 return 0;
}
