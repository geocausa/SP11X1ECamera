/* SPDX-License-Identifier: GPL-2.0-only */
#pragma once
#include <cerrno>
#include <cstdint>
namespace libcamera {
/* One asynchronous IPA calculation at a time, with bounded completion debt.
 * Pool exhaustion keeps credit pending. Epochs reject stopped-stream callbacks.
 */
class CamssX1EParameterSchedule {
public:
 void reset() { epoch_++; next_=5; due_=0; busy_=false; active_=true; failed_=false; }
 void stop() { active_=false; busy_=false; due_=0; }
 int seedAccepted() { if(!active_ || busy_ || due_ || next_>=9) return -EINVAL; next_++;return 0; }
 int add() { if(!active_ || failed_)return -ESHUTDOWN; if(due_>=16)return -ENOSPC; due_++;return 0; }
 bool begin(bool poolAvailable) {
  if(!active_ || failed_ || busy_ || !due_ || !poolAvailable)return false;
  if(next_>UINT32_MAX){failed_=true;return false;}
  busy_=true;due_--;return true;
 }
 int complete(uint64_t epoch,uint64_t request,int status) {
  if(epoch!=epoch_ || !active_)return -ESTALE;
  if(!busy_ || request!=next_)return -EPROTO;
  busy_=false;
  if(status){failed_=true;return status;}
  next_++;return 0;
 }
 uint64_t epoch() const{return epoch_;}
 uint64_t next() const{return next_;}
 bool busy() const{return busy_;}
 unsigned int due() const{return due_;}
private:
 uint64_t epoch_=0,next_=5;
 unsigned int due_=0;
 bool active_=false,busy_=false,failed_=false;
};
}
