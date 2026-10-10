/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_FRONT_ISP_PARAMS_H
#define NATIVE_FRONT_ISP_PARAMS_H
#include "native-front-gamma.h"
/* Development compatibility with the public CAMSS ISP proposal. The generic
 * V4L2 ISP envelope has no frame ID; the queue assigns it in submission order.
 * Supported subset: an empty buffer, or one GAMMA_256 update (flags zero).
 * Enable/disable and other blocks are deliberately unsupported, never ignored.
 * Serialization is little-endian on the qualified little-endian SP11 target.
 */
#define NF_ISP_FORMAT 0x50494351U /* QCIP */
#define NF_ISP_HEADER_BYTES 8U
#define NF_ISP_GAMMA_TYPE 10U
#define NF_ISP_GAMMA_BLOCK_BYTES (8U + NF_GAMMA_BYTES)
#define NF_ISP_MAX_BYTES (NF_ISP_HEADER_BYTES + NF_ISP_GAMMA_BLOCK_BYTES)

static inline unsigned int nf_isp_u16(const nf_gamma_u8 *p)
{ return p[0] | (unsigned int)p[1] << 8; }

/* Scratch words belong to the caller. Only gamma and update are published on
 * success. The input must already be an immutable owned copy in the kernel.
 */
static inline int native_front_isp_decode(const nf_gamma_u8 *data, size_t bytes,
 nf_gamma_u32 *scratch, size_t words, nf_gamma_u8 *gamma, size_t gamma_bytes,
 int *update)
{
 unsigned int i;
 int ret;

 if (!data || !update || bytes < NF_ISP_HEADER_BYTES || bytes > NF_ISP_MAX_BYTES)
  return -EINVAL;
 if (nf_gamma_get32(data) > 1 ||
     nf_gamma_get32(data + 4) != bytes - NF_ISP_HEADER_BYTES)
  return -EINVAL;
 if (bytes == NF_ISP_HEADER_BYTES) {
  *update = 0;
  return 0;
 }
 if (bytes != NF_ISP_MAX_BYTES || nf_isp_u16(data + 8) != NF_ISP_GAMMA_TYPE)
  return -EOPNOTSUPP;
 if (nf_isp_u16(data + 10))
  return -EOPNOTSUPP;
 if (nf_gamma_get32(data + 12) != NF_ISP_GAMMA_BLOCK_BYTES)
  return -EINVAL;
 if (!scratch || words != NF_GAMMA_WORD_COUNT || !gamma || gamma_bytes != NF_GAMMA_BYTES)
  return -EINVAL;
 if (nf_gamma_overlap(data,bytes,scratch,words*sizeof(*scratch)) ||
     nf_gamma_overlap(data,bytes,gamma,gamma_bytes) ||
     nf_gamma_overlap(scratch,words*sizeof(*scratch),gamma,gamma_bytes))
  return -EINVAL;
 for (i = 0; i < NF_GAMMA_WORD_COUNT; i++)
  scratch[i] = nf_gamma_get32(data + 16 + i*4);
 ret = native_front_gamma10_expand(scratch,words,gamma,gamma_bytes);
 if (!ret)
  *update = 1;
 return ret;
}

/* Semantic RGB points in the proposal's 10-bit output domain; independent
 * tuning only. Validate all channels before touching a destination buffer.
 */
static inline int native_front_isp_encode(const nf_gamma_u16 *points,size_t count,
 nf_gamma_u8 *out,size_t bytes)
{
 unsigned int c,i;

 if (!out || bytes != (points ? NF_ISP_MAX_BYTES : NF_ISP_HEADER_BYTES) ||
     count != (points ? NF_GAMMA_POINT_COUNT : 0))
  return -EINVAL;
 if (points) {
  if (nf_gamma_overlap(points,count*sizeof(*points),out,bytes))
   return -EINVAL;
  for (c=0;c<NF_GAMMA_CHANNELS;c++)
   for (i=0;i<NF_GAMMA_POINTS;i++) {
    unsigned int at=c*NF_GAMMA_POINTS+i;
    int delta,native_delta;
    if (points[at]>1023)
     return -ERANGE;
    if (i==NF_GAMMA_WORDS)
     continue;
    delta=(int)points[at+1]-(int)points[at];
    native_delta=(int)nf_gamma10_scale12(points[at+1]) -
                 (int)nf_gamma10_scale12(points[at]);
    if (delta < -512 || delta > 511 || native_delta < -2048 || native_delta > 2047)
     return -ERANGE;
   }
 }
 nf_gamma_put32(out,1);
 nf_gamma_put32(out+4,bytes-NF_ISP_HEADER_BYTES);
 if (!points)
  return 0;
 out[8]=NF_ISP_GAMMA_TYPE;out[9]=0;out[10]=0;out[11]=0;
 nf_gamma_put32(out+12,NF_ISP_GAMMA_BLOCK_BYTES);
 for(c=0;c<NF_GAMMA_CHANNELS;c++)
  for(i=0;i<NF_GAMMA_WORDS;i++) {
   unsigned int at=c*NF_GAMMA_POINTS+i;
   int delta=(int)points[at+1]-(int)points[at];
   nf_gamma_put32(out+16+4*(c*NF_GAMMA_WORDS+i),
                  points[at]|(((nf_gamma_u32)delta&1023U)<<10));
  }
 return 0;
}
#endif
