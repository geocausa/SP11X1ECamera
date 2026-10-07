/* SPDX-License-Identifier: GPL-2.0-only */
/* Internal four-phase rear scalar envelope, not a published V4L2 UAPI.
 * Quantized values only; no floating-point, callbacks, pointers or register
 * replay. The consumer must independently validate the full semantic state.
 */
#ifndef SP11_NATIVE_REAR_STARTUP_SCALARS_H
#define SP11_NATIVE_REAR_STARTUP_SCALARS_H
#ifdef __KERNEL__
#include <linux/errno.h>
#include <linux/types.h>
typedef u8 native_rear_u8;
typedef u64 native_rear_u64;
#else
#include <errno.h>
#include <stdint.h>
typedef uint8_t native_rear_u8;
typedef uint64_t native_rear_u64;
#endif
#define NATIVE_REAR_SCALARS_MAGIC 0x3153524eU
#define NATIVE_REAR_SCALARS_VERSION 1
#define NATIVE_REAR_SCALARS_PACKETS 4
#define NATIVE_REAR_SCALARS_SLOT_BYTES 48
#define NATIVE_REAR_SCALARS_BYTES 208
struct native_rear_startup_scalars {
 native_rear_u8 data[NATIVE_REAR_SCALARS_BYTES];
};
static inline native_rear_u64 native_rear_scalars_get(
 const native_rear_u8 *p, unsigned int bytes)
{
 native_rear_u64 value = 0;
 unsigned int i;
 for (i = 0; i < bytes; i++)
  value |= (native_rear_u64)p[i] << (8 * i);
 return value;
}
static inline int native_rear_scalars_validate(
 const native_rear_u8 *data, unsigned long bytes)
{
 unsigned int p, i;
 if (!data || bytes != NATIVE_REAR_SCALARS_BYTES ||
     native_rear_scalars_get(data, 4) != NATIVE_REAR_SCALARS_MAGIC ||
     native_rear_scalars_get(data + 4, 2) != NATIVE_REAR_SCALARS_VERSION ||
     native_rear_scalars_get(data + 6, 2) != NATIVE_REAR_SCALARS_BYTES ||
     native_rear_scalars_get(data + 8, 4) != NATIVE_REAR_SCALARS_PACKETS ||
     native_rear_scalars_get(data + 12, 4))
  return -EINVAL;
 for (p = 0; p < NATIVE_REAR_SCALARS_PACKETS; p++) {
  const native_rear_u8 *s = data + 16 + p * NATIVE_REAR_SCALARS_SLOT_BYTES;
  if (native_rear_scalars_get(s, 8) < 4 ||
      native_rear_scalars_get(s + 8, 4) != p ||
      native_rear_scalars_get(s + 12, 4) ||
      native_rear_scalars_get(s + 44, 4))
   return -EPROTO;
  for (i = 0; i < 4; i++)
   if (native_rear_scalars_get(s + 16 + 2 * i, 2) > 0x7fff ||
       native_rear_scalars_get(s + 24 + 4 * i, 4) > 0x3ffff)
    return -ERANGE;
  if (native_rear_scalars_get(s + 40, 2) > 0x7fff ||
      native_rear_scalars_get(s + 42, 2) > 0x7fff)
   return -ERANGE;
 }
 return 0;
}
#endif
