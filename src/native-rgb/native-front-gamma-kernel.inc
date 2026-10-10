/* SPDX-License-Identifier: GPL-2.0-only */
/* Internal backend only. No ioctl, metadata format or userspace ABI here.
 * The v41x proposal names DMI selectors 1/2/3 as G/B/R. The retained front
 * descriptor topology uses those selectors with payloads 0/1/2. Hardware
 * channel interpretation and the candidate 12-bit encoding still need a
 * fresh optical qualification before any caller enables this path.
 */
#include "native-front-gamma-kernel.h"

static int native_front_gamma_bind(u8 *capsule, size_t capsule_bytes,
                                    const u8 *gamma, size_t gamma_bytes)
{
 const u8 *sections[NF_GAMMA_CHANNELS] = { NULL, NULL, NULL };
 const unsigned int semantic_channel[] = { 1, 2, 0 }; /* G, B, R */
 unsigned int i, found = 0;
 int ret;

 if (!capsule || capsule_bytes != CAMSS_X1E_PIX_CAPSULE_BYTES)
  return -EINVAL;
 ret = native_front_gamma12_validate(gamma, gamma_bytes);
 if (ret)
  return ret;
 if (nf_gamma_overlap(capsule, capsule_bytes, gamma, gamma_bytes))
  return -EINVAL;
 ret = camss_x1e_pix_capsule_validate_sections(capsule, capsule_bytes);
 if (ret)
  return ret;
 /* Resolve named payload sections rather than assuming file offsets. Full
  * section validation above proves bounds and pairwise disjointness.
  */
 for (i = 0; i < ARRAY_SIZE(camss_x1e_epoch0_payloads); i++) {
  const struct camss_x1e_epoch0_payload_desc *d = &camss_x1e_epoch0_payloads[i];
  const u8 *section;
  size_t bytes;

  if (d->module != CAMSS_X1E_IQ_GAMMA)
   continue;
  if (d->payload >= NF_GAMMA_CHANNELS || sections[d->payload] ||
      d->size != NF_GAMMA_WORDS * 4)
   return -EINVAL;
  ret = camss_x1e_pix_capsule_section(capsule,
        CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_PAYLOAD, i, &section, &bytes);
  if (ret || bytes != NF_GAMMA_WORDS * 4)
   return -EINVAL;
  sections[d->payload] = section;
  found++;
 }
 if (found != NF_GAMMA_CHANNELS)
  return -EINVAL;
 /* All rejection paths precede the first output write. */
 for (i = 0; i < NF_GAMMA_CHANNELS; i++)
  memcpy((u8 *)sections[i], gamma + semantic_channel[i] * NF_GAMMA_WORDS * 4,
         NF_GAMMA_WORDS * 4);
 return 0;
}
