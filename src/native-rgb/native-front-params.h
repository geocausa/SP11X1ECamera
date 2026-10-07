/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_FRONT_PARAMS_H
#define NATIVE_FRONT_PARAMS_H
#include <linux/types.h>
#ifdef __KERNEL__
#include <linux/errno.h>
#include <linux/string.h>
typedef u8 native_params_u8;
typedef u16 native_params_u16;
typedef u32 native_params_u32;
typedef u64 native_params_u64;
#else
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
typedef uint8_t native_params_u8;
typedef uint16_t native_params_u16;
typedef uint32_t native_params_u32;
typedef uint64_t native_params_u64;
#endif

#define NATIVE_FRONT_PARAMS_MAGIC 0x31505851U /* QXP1 */
#define NATIVE_FRONT_PARAMS_VERSION 1U
#define NATIVE_FRONT_PARAMS_BYTES 64U
#define NATIVE_FRONT_PARAMS_DEMUX 1U
#define NATIVE_FRONT_PARAMS_PDPC 2U
#define NATIVE_FRONT_PARAMS_WB 4U

/* Experimental typed scalar interface, little-endian and pointer-free.
 * request_id matches the admitted per-frame ISP sequence (first typed request5).
 * demux_q10 uses the four-channel order of the admitted normal-front Bayer0
 * calculation: reg0 packs channel0/channel1, reg1 channel3/channel2.
 * pdpc_q12 ratios: R/G, B/G, G/R, G/B. WB is B/G then R/G, Q10.
 * A WB update must accompany its PDPC ratios. No bank, register, command or
 * DMA address is supplied by userspace. Unknown flags and unused fields reject.
 */
struct native_front_params {
 __le32 magic;
 __le16 version;
 __le16 bytes;
 __le64 request_id;
 __le32 update_mask;
 __le32 reserved0;
 __le16 demux_q10[4];
 __le32 pdpc_q12[4];
 __le16 wb_q10[2];
 __le32 reserved[3];
};

static inline native_params_u16 native_params_le16(const native_params_u8 *p)
{
 return p[0] | (native_params_u16)p[1] << 8;
}
static inline native_params_u32 native_params_le32(const native_params_u8 *p)
{
 return (native_params_u32)p[0] | (native_params_u32)p[1] << 8 |
        (native_params_u32)p[2] << 16 | (native_params_u32)p[3] << 24;
}
static inline native_params_u64 native_params_le64(const native_params_u8 *p)
{
 return native_params_le32(p) | (native_params_u64)native_params_le32(p + 4) << 32;
}
static inline int native_front_params_validate(const void *data, size_t bytes)
{
 const native_params_u8 *p = (const native_params_u8 *)data;
 native_params_u64 request;
 native_params_u32 mask;
 unsigned int i;
 if (!p || bytes != NATIVE_FRONT_PARAMS_BYTES ||
     native_params_le32(p) != NATIVE_FRONT_PARAMS_MAGIC ||
     native_params_le16(p + 4) != NATIVE_FRONT_PARAMS_VERSION ||
     native_params_le16(p + 6) != NATIVE_FRONT_PARAMS_BYTES)
  return -EINVAL;
 request = native_params_le64(p + 8);
 mask = native_params_le32(p + 16);
 if (request < 5 || request > 0xffffffffULL)
  return -ERANGE;
 if (mask & ~7U || native_params_le32(p + 20) ||
     native_params_le32(p + 52) || native_params_le32(p + 56) ||
     native_params_le32(p + 60) ||
     !!(mask & NATIVE_FRONT_PARAMS_WB) != !!(mask & NATIVE_FRONT_PARAMS_PDPC))
  return -EINVAL;
 for (i = 0; i < 4; i++) {
  native_params_u32 q = native_params_le16(p + 24 + 2*i);
  if (mask & NATIVE_FRONT_PARAMS_DEMUX) {
   if (!q || q > 0x7fff)
    return -ERANGE;
  } else if (q) {
   return -EINVAL;
  }
  q = native_params_le32(p + 32 + 4*i);
  if (mask & NATIVE_FRONT_PARAMS_PDPC) {
   if (!q || q > 0x3ffff)
    return -ERANGE;
  } else if (q) {
   return -EINVAL;
  }
 }
 for (i = 0; i < 2; i++) {
  native_params_u32 q = native_params_le16(p + 48 + 2*i);
  if (mask & NATIVE_FRONT_PARAMS_WB) {
   if (!q || q > 0x7fff)
    return -ERANGE;
  } else if (q) {
   return -EINVAL;
  }
 }
 return 0;
}

/* Used by the actual kernel bridge and sanitizer tests. Validation precedes
 * every mutation; caller-owned baseline values remain intact on any rejection.
 */
static inline int native_front_params_apply(const void *data, size_t bytes,
                                            native_params_u32 values[9][6])
{
 const native_params_u8 *p = (const native_params_u8 *)data;
 native_params_u32 pending[9][6], mask, request;
 const unsigned int bank_modules[] = {1,2,4,5,6,7,8};
 unsigned int i, j;
 int ret = native_front_params_validate(data, bytes);
 if (ret)
  return ret;
 if (!values)
  return -EINVAL;
 memcpy(pending, values, sizeof(pending));
 request = native_params_le64(p + 8);
 mask = native_params_le32(p + 16);
 /* Existing source-qualified bank parity, including inverse GTM/Gamma. */
 for (i = 0; i < sizeof(bank_modules)/sizeof(bank_modules[0]); i++) {
  unsigned int module = bank_modules[i];
  native_params_u32 bank = (module == 6 || module == 7) ?
                           request & 1 : (request + 1) & 1;
  for (j = 0; j < (module == 8 ? 4U : 2U); j++)
   pending[module][j] = bank;
 }
 if (mask & NATIVE_FRONT_PARAMS_DEMUX) {
  pending[0][0] = (native_params_u32)native_params_le16(p + 24) << 16 |
                  native_params_le16(p + 26);
  pending[0][1] = (native_params_u32)native_params_le16(p + 30) << 16 |
                  native_params_le16(p + 28);
 }
 if (mask & NATIVE_FRONT_PARAMS_PDPC)
  for (i = 0; i < 4; i++)
   pending[1][i + 2] = native_params_le32(p + 32 + 4*i);
 if (mask & NATIVE_FRONT_PARAMS_WB)
  for (i = 0; i < 2; i++)
   pending[3][i] = (native_params_u32)native_params_le16(p + 48 + 2*i) << 17;
 memcpy(values, pending, sizeof(pending));
 return 0;
}
#endif
