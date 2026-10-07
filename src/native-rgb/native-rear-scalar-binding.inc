/* SPDX-License-Identifier: GPL-2.0-only */
/* Bind libipa-produced integer scalars to four unsubmitted rear packet states.
 * Does not fabricate the remaining geometry/statistics/DMI bootstrap.
 */
#ifndef SP11_NATIVE_REAR_SCALAR_BINDING_INC
#define SP11_NATIVE_REAR_SCALAR_BINDING_INC
#include "native-rear-startup-scalars.h"

static int native_rear_bind_startup_scalars(
 struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
 const struct native_rear_startup_scalars *values)
{
 struct native_rear_startup_scalars snapshot;
 unsigned int p, i;
 int ret;

 if (!base || !values)
  return -EINVAL;
 /* Own a stable copy; callers pass kernel memory, never an unchecked user ptr. */
 memcpy(&snapshot, values, sizeof(snapshot));
 ret = native_rear_scalars_validate(snapshot.data, sizeof(snapshot));
 if (ret)
  return ret;
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
  const u8 *slot = snapshot.data + 16 + p * NATIVE_REAR_SCALARS_SLOT_BYTES;
  if (base[p].ready)
   return -EBUSY;
  if (base[p].request_id != native_rear_scalars_get(slot, 8))
   return -ESTALE;
 }
 /* Every identity/range admitted before modifying any packet. */
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
  const u8 *slot = snapshot.data + 16 + p * NATIVE_REAR_SCALARS_SLOT_BYTES;
  struct e006z_rear_scalar_state *s = &base[p].regs.scalar;
  s->epoch_kind = E006Z_EPOCH_STARTUP;
  s->startup_phase = p;
  s->request_id = base[p].request_id;
  for (i = 0; i < 4; i++) {
   s->demux_q10[i] = native_rear_scalars_get(slot + 16 + 2 * i, 2);
   s->pdpc_q12[i] = native_rear_scalars_get(slot + 24 + 4 * i, 4);
  }
  s->wb_b_q10 = native_rear_scalars_get(slot + 40, 2);
  s->wb_r_q10 = native_rear_scalars_get(slot + 42, 2);
 }
 return 0;
}
struct native_rear_scalar_binding_ops {
 int (*bind)(struct e008o_rear_packet_semantics *,
             const struct native_rear_startup_scalars *);
};
static const struct native_rear_scalar_binding_ops
native_rear_scalar_binding_recipe __used = {
 .bind = native_rear_bind_startup_scalars,
};
#endif
