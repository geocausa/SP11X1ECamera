/* SPDX-License-Identifier: GPL-2.0-only */
#pragma once
#include <algorithm>
#include <cerrno>
#include <cstddef>
#include <deque>
#include <utility>

namespace libcamera {
/* Accepted app requests remain ordered when their control slot is too late.
 * Padding admits only retired internal images; exhaustion waits for completion.
 * The caller preserves the exact control horizon and cancels take() on stop.
 */
template<typename Buffer> class CamssX1EOrderedAdmission {
public:
 int push(Buffer *buffer, size_t limit)
 {
  if (!buffer || !limit) return -EINVAL;
  if (std::find(pending_.begin(), pending_.end(), buffer) != pending_.end()) return -EEXIST;
  if (pending_.size() >= limit) return -ENOSPC;
  pending_.push_back(buffer);
  return 0;
 }
 template<typename Admit, typename Pad> int drain(Admit admit, Pad pad)
 {
  while (!pending_.empty()) {
   int ret = admit(pending_.front());
   if (ret == -ETIME) {
    ret = pad();
    if (ret == -EAGAIN) return 0; /* Keep the same head; no app cancellation. */
    if (ret) return ret;
    continue;
   }
   if (ret) return ret;
   pending_.pop_front();
  }
  return 0;
 }
 size_t size() const { return pending_.size(); }
 std::deque<Buffer *> take()
 {
  auto pending = std::move(pending_);
  pending_.clear();
  return pending;
 }
private:
 std::deque<Buffer *> pending_;
};
} /* namespace libcamera */
