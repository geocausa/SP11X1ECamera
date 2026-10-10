/* SPDX-License-Identifier: GPL-2.0-only */
/* Synthetic codec/state contract tests; provider below is an explicit mock. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "native-front-param-state.h"
static unsigned checks,calls;
static int error;
static native_params_u64 receipt;
static unsigned char copy[NF_GAMMA_BYTES];
static int copied;
static void need(int ok) {checks++;assert(ok);}
static int submit(void *ctx,native_params_u64 id,const nf_gamma_u8 *gamma,size_t bytes)
{
 (void)ctx;calls++;
 if(error)return error;
 receipt=id;copied=gamma!=NULL;
 need(bytes==(gamma?NF_GAMMA_BYTES:0));
 if(gamma)memcpy(copy,gamma,bytes);
 return 0;
}
int main(void)
{
 nf_gamma_u16 points[NF_GAMMA_POINT_COUNT];
 nf_gamma_u32 scratch[NF_GAMMA_WORD_COUNT];
 nf_gamma_u8 packet[NF_ISP_MAX_BYTES],good[NF_ISP_MAX_BYTES];
 nf_gamma_u8 gamma[NF_GAMMA_BYTES],saved[NF_GAMMA_BYTES],empty[8];
 struct native_front_param_state state;
 int update=99;
 for(unsigned c=0;c<3;c++)for(unsigned i=0;i<257;i++)points[c*257+i]=100*c+i*3;
 need(!native_front_isp_encode(points,NF_GAMMA_POINT_COUNT,packet,sizeof(packet)));
 memcpy(good,packet,sizeof(good));
 need(!native_front_isp_decode(packet,sizeof(packet),scratch,NF_GAMMA_WORD_COUNT,gamma,sizeof(gamma),&update));
 need(update==1 && !native_front_gamma12_validate(gamma,sizeof(gamma)));
 memcpy(saved,gamma,sizeof(saved));
 /* Real envelope truncation, trailing bytes, unknown blocks/flags, malformed
  * late-channel data: no partially published gamma or success marker. */
 for(unsigned n=0;n<NF_ISP_MAX_BYTES;n++) {
  update=99;
  need(native_front_isp_decode(packet,n,scratch,NF_GAMMA_WORD_COUNT,gamma,sizeof(gamma),&update)!=0);
  need(update==99 && !memcmp(gamma,saved,sizeof(gamma)));
 }
 for(unsigned mode=0;mode<7;mode++) {
  memcpy(packet,good,sizeof(good));
  if(mode==0)packet[0]=2;
  if(mode==1)packet[4]^=1;
  if(mode==2)packet[8]=9;
  if(mode==3)packet[10]=2;
  if(mode==4)packet[12]^=1;
  if(mode==5)packet[NF_ISP_MAX_BYTES-1]=1;
  if(mode==6)packet[NF_ISP_MAX_BYTES-4]^=1;
  update=99;
  need(native_front_isp_decode(packet,sizeof(packet),scratch,NF_GAMMA_WORD_COUNT,gamma,sizeof(gamma),&update)!=0);
  need(update==99 && !memcmp(gamma,saved,sizeof(gamma)));
 }
 memcpy(packet,good,sizeof(good));points[NF_GAMMA_POINT_COUNT-1]=1024;
 need(native_front_isp_encode(points,NF_GAMMA_POINT_COUNT,packet,sizeof(packet))==-ERANGE);
 need(!memcmp(packet,good,sizeof(good)));
 need(!native_front_isp_encode(NULL,0,empty,sizeof(empty)));
 update=99;
 need(!native_front_isp_decode(empty,8,NULL,0,NULL,0,&update));need(!update);
 empty[0]=0;need(!native_front_isp_decode(empty,8,NULL,0,NULL,0,&update));
 native_front_param_state_reset(&state);
 need(!native_front_param_state_submit(&state,NULL,0,submit,NULL));
 need(receipt==5 && !copied && state.next==6);
 need(!native_front_param_state_submit(&state,gamma,1,submit,NULL));
 need(receipt==6 && copied && !memcmp(copy,saved,sizeof(copy)));
 memset(gamma,0xa5,sizeof(gamma));
 need(!native_front_param_state_submit(&state,NULL,0,submit,NULL));
 need(receipt==7 && copied && !memcmp(copy,saved,sizeof(copy)));
 /* Failed enqueue cannot commit the next ID or replacement curve, and makes
  * further submissions fail until a new stream reset. */
 memcpy(gamma,saved,sizeof(gamma));error=-ENOSPC;
 need(native_front_param_state_submit(&state,gamma,1,submit,NULL)==-ENOSPC);
 need(state.next==8 && state.failed && !memcmp(state.gamma,saved,sizeof(saved)));
 unsigned before=calls;
 need(native_front_param_state_submit(&state,gamma,1,submit,NULL)==-EINVAL);
 need(calls==before);error=0;
 native_front_param_state_reset(&state);
 need(!state.has_gamma && state.next==5 && !state.failed);
 need(!native_front_param_state_submit(&state,NULL,0,submit,NULL));
 state.next=0xffffffffULL;
 need(!native_front_param_state_submit(&state,NULL,0,submit,NULL));
 need(native_front_param_state_submit(&state,NULL,0,submit,NULL)==-EOVERFLOW);
 printf("PASS_FRONT_ISP_CODEC_STATE checks=%u provider=mock hardware_access=false\n",checks);
 return 0;
}
