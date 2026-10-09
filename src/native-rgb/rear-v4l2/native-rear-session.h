/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_REAR_SESSION_H
#define NATIVE_REAR_SESSION_H
/* Caller holds native_rear_generation_lock across begin, transaction and finish.
 * Qualification is bounded to three sessions in one disposable candidate boot.
 * A failed attempt permanently poisons this gate; no reset API exists.
 */
#define NATIVE_REAR_SESSION_LIMIT 3U
struct native_rear_session_gate {
 unsigned int attempted, completed;
 bool active, poisoned;
 u64 last_owner;
};
static inline int native_rear_session_begin(struct native_rear_session_gate *g)
{
 if (!g)
  return -EINVAL;
 if (g->poisoned)
  return -EIO;
 if (g->active)
  return -EBUSY;
 if (g->completed != g->attempted) {
  g->poisoned = true;
  return -ESTALE;
 }
 if (g->attempted >= NATIVE_REAR_SESSION_LIMIT)
  return -ENOSPC;
 g->attempted++;
 g->active = true;
 return 0;
}
static inline int native_rear_session_finish(struct native_rear_session_gate *g,
                                            int ret, bool clean, u64 owner)
{
 if (!g || !g->active)
  return -EINVAL;
 g->active = false;
 if (ret || !clean || !owner || owner <= g->last_owner) {
  g->poisoned = true;
  return ret ? ret : -EPROTO;
 }
 g->last_owner = owner;
 g->completed++;
 return 0;
}
#endif
