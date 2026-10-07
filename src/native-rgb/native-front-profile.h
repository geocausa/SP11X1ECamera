/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_FRONT_PROFILE_H
#define NATIVE_FRONT_PROFILE_H
#include "native-front-nv12-commands.h"
#include "native-front-profile-schema.h"
#define NATIVE_FRONT_PROFILE_FIRMWARE "qcom/sp11/imx681-2560x1440-nv12-v1.bin"

/* The caller computes SHA256 over the entire immutable firmware buffer.
 * This qualification admits exactly one board/mode profile. It does not grant
 * arbitrary scalar register programming or a general executable firmware ABI.
 */
static inline int native_front_profile_validate(const u8 *data, size_t bytes,
                                                const u8 *digest)
{
 static const u32 identity[] = {
  1, 64, NATIVE_FRONT_PROFILE_BYTES, 0x80100,
  2560, 1440, 3840, 2160, 0x3231564e,
  NATIVE_FRONT_PROFILE_SCALAR_WORDS, NATIVE_FRONT_PROFILE_TABLE_BYTES, 0, 0, 0
 };
 unsigned int i;
 if (!data || !digest || bytes != NATIVE_FRONT_PROFILE_BYTES)
  return -EINVAL;
 if (memcmp(digest, native_front_profile_digest, 32))
  return -EKEYREJECTED;
 if (memcmp(data, "QXTPRF01", 8))
  return -EINVAL;
 for (i = 0; i < sizeof(identity)/sizeof(identity[0]); i++)
  if (native_nv12_le32(data+8+4*i) != identity[i])
   return -EINVAL;
 return 0;
}

/* Reconstruct the private internal carrier from kernel-owned instruction
 * topology and data-only profile fields. No MMIO, DMA, allocation or enqueue.
 * Validate everything before changing output. Input and output must be disjoint.
 */
static inline int native_front_profile_materialize(const u8 *data, size_t bytes,
                                                    const u8 *digest, u8 *out,
                                                    size_t out_bytes)
{
 size_t i;
 int ret = native_front_profile_validate(data, bytes, digest);
 if (ret)
  return ret;
 if (!out || out_bytes != NATIVE_FRONT_PROFILE_CAPSULE_BYTES)
  return -EINVAL;
 if ((unsigned long)data <= (unsigned long)out ?
     (unsigned long)out - (unsigned long)data < bytes :
     (unsigned long)data - (unsigned long)out < out_bytes)
  return -EINVAL;
 for (i = 0; i < sizeof(native_front_profile_fixed)/sizeof(native_front_profile_fixed[0]); i++) {
  const struct native_front_profile_fixed *f = &native_front_profile_fixed[i];
  if (f->destination > out_bytes - 4)
   return -EINVAL;
 }
 for (i = 0; i < sizeof(native_front_profile_copies)/sizeof(native_front_profile_copies[0]); i++) {
  const struct native_front_profile_copy *c = &native_front_profile_copies[i];
  if (c->source > bytes || c->bytes > bytes-c->source ||
      c->destination > out_bytes || c->bytes > out_bytes-c->destination)
   return -EINVAL;
 }
 memset(out, 0, out_bytes);
 memcpy(out, "E3HPIX01", 8);
 for (i = 0; i < sizeof(native_front_profile_fixed)/sizeof(native_front_profile_fixed[0]); i++) {
  const struct native_front_profile_fixed *f = &native_front_profile_fixed[i];
  native_nv12_put32(out+f->destination, f->value);
 }
 for (i = 0; i < sizeof(native_front_profile_copies)/sizeof(native_front_profile_copies[0]); i++) {
  const struct native_front_profile_copy *c = &native_front_profile_copies[i];
  memcpy(out+c->destination, data+c->source, c->bytes);
 }
 return 0;
}
#endif
