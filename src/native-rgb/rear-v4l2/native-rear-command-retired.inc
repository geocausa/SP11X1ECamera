/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_REAR_COMMAND_RETIRED_INC
#define NATIVE_REAR_COMMAND_RETIRED_INC
static bool native_rear_command_zero(const void *ptr, size_t size)
{
 const u8 *bytes = ptr;
 size_t i;
 for (i = 0; i < size; i++)
  if (bytes[i])
   return false;
 return true;
}

static bool
native_rear_live_commands_retired_valid(const struct e008l_rear_command_set *set,
                                       u64 owner)
{
 unsigned int p;
 if (!set || !owner || !set->allocated || !set->prepared ||
     !set->hardware_exposed || set->receipt_faulted || !set->live_retired ||
     set->retired_owner != owner || set->retired_BL_count != 22 ||
     !set->retired_last.complete || set->retired_last.sequence != 22 ||
     !set->retired_last.dma || !set->retired_last.bytes ||
     !native_rear_bl_status_valid(set->retired_last.irq_status))
  return false;
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++)
  if (set->packet_request_id[p] < 4 ||
      !native_rear_command_zero(&set->packet[p], sizeof(set->packet[p])))
   return false;
 return true;
}
#endif
