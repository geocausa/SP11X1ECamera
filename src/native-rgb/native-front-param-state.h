/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_FRONT_PARAM_STATE_H
#define NATIVE_FRONT_PARAM_STATE_H
#include "native-front-params.h"
#include "native-front-isp-params.h"
struct native_front_param_state {
 native_params_u64 next;
 int active,failed,has_gamma;
 nf_gamma_u8 gamma[NF_GAMMA_BYTES];
};
typedef int (*native_front_param_submit_fn)(void *,native_params_u64,
                                            const nf_gamma_u8 *,size_t);
static inline void native_front_param_state_reset(struct native_front_param_state *s)
{ memset(s,0,sizeof(*s));s->next=5;s->active=1; }
/* Serialized by the actual queue's dispatch lock. No state commit on error.
 * An omitted gamma block preserves the last successfully submitted curve.
 */
static inline int native_front_param_state_submit(struct native_front_param_state *s,
 const nf_gamma_u8 *gamma,int update,native_front_param_submit_fn submit,void *ctx)
{
 const nf_gamma_u8 *selected;
 int ret;
 if (!s || !submit || !s->active || s->failed || (update!=0 && update!=1))
  return -EINVAL;
 if (s->next<5 || s->next>0xffffffffULL)
  return -EOVERFLOW;
 if (update) {
  ret=native_front_gamma12_validate(gamma,NF_GAMMA_BYTES);
  if(ret)return ret;
 }
 selected=update?gamma:s->has_gamma?s->gamma:NULL;
 ret=submit(ctx,s->next,selected,selected?NF_GAMMA_BYTES:0);
 if(ret) {s->failed=1;return ret;}
 if(update) {memcpy(s->gamma,gamma,NF_GAMMA_BYTES);s->has_gamma=1;}
 s->next++;
 return 0;
}
#endif
