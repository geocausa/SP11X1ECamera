/* SPDX-License-Identifier: GPL-2.0-only */
#pragma once
#include <algorithm>
#include <cerrno>
#include <cmath>
#include <cstdint>
namespace RearAe {
/* Opt-in fixed-mode engineering controller. Target is in admitted raw meter
 * units, not a claim about sensor full scale, black level or Windows tuning.
 * Exposure/gain are never associated with a particular optical frame.
 */
constexpr int32_t MinLines=4,MaxLines=3206,MinGain=128,MaxGain=2048;
constexpr uint32_t SettleFrames=8;
struct Proposal { bool apply=false,limited=false;int32_t lines=0,gain=0; };
class Controller {
public:
 int start(bool enabled,int32_t lines,int32_t gain,double target){
  if(running_||lines<MinLines||lines>MaxLines||gain<MinGain||gain>MaxGain||
     !std::isfinite(target)||target<=0||target>1000000)return -EINVAL;
  running_=true;enabled_=enabled;lines_=lines;gain_=gain;target_=target;
  haveSequence_=pending_=poisoned_=false;waitUntil_=SettleFrames;return 0;
 }
 void stop(){running_=enabled_=pending_=poisoned_=haveSequence_=false;}
 int observe(uint32_t sequence,double meter,Proposal *out){
  if(!running_||poisoned_||!out||!std::isfinite(meter)||meter<0)return -EINVAL;
  if(haveSequence_&&(lastSequence_==UINT32_MAX||sequence!=lastSequence_+1))return -ESTALE;
  if(!haveSequence_&&sequence!=0)return -ESTALE;
  lastSequence_=sequence;haveSequence_=true;
  Proposal p{};p.lines=lines_;p.gain=gain_;
  if(enabled_&&!pending_&&sequence>=waitUntil_){
   double ratio=target_/std::max(meter,1.0);
   if(ratio<0.9||ratio>1.1){
    const double product=double(lines_)*gain_*std::clamp(ratio,0.5,2.0);
    p.lines=int32_t(std::clamp<long long>(std::llround(product/MinGain),MinLines,MaxLines));
    p.gain=int32_t(std::clamp<long long>(std::llround(product/p.lines),MinGain,MaxGain));
    p.apply=p.lines!=lines_||p.gain!=gain_;p.limited=!p.apply;
    if(p.apply){pending_=true;pendingSequence_=sequence;proposal_=p;}
   }
  }
  *out=p;return 0;
 }
 int applied(uint32_t sequence,int ret){
  if(!running_||!pending_||sequence!=pendingSequence_)return -ESTALE;
  pending_=false;
  if(ret){poisoned_=true;return ret<0?ret:-EIO;}
  lines_=proposal_.lines;gain_=proposal_.gain;
  waitUntil_=uint64_t(sequence)+SettleFrames;return 0;
 }
 bool pending()const{return pending_;}
 bool enabled()const{return enabled_;}
 int32_t lines()const{return lines_;}
 int32_t gain()const{return gain_;}
 double target()const{return target_;}
private:
 bool running_=false,enabled_=false,haveSequence_=false,pending_=false,poisoned_=false;
 uint32_t lastSequence_=0,pendingSequence_=0;
 uint64_t waitUntil_=0;
 int32_t lines_=1600,gain_=128;
 double target_=0;
 Proposal proposal_{};
};
}
