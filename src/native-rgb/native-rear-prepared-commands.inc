/* SPDX-License-Identifier: GPL-2.0-only
 * Validate the Linux-owned, packet-isolated rear command arena.
 * No register generation, MMIO, ownership grant, or hardware submission.
 */
#ifndef SP11_NATIVE_REAR_PREPARED_COMMANDS_INC
#define SP11_NATIVE_REAR_PREPARED_COMMANDS_INC

static bool native_rear_memory_overlap(const void *a, size_t an,
                                      const void *b, size_t bn)
{
 unsigned long x = (unsigned long)a, y = (unsigned long)b;
 if (!a || !b || !an || !bn || an > (unsigned long)-1 - x ||
     bn > (unsigned long)-1 - y)
  return true;
 return x < y + bn && y < x + an;
}

static bool native_rear_bl_matches(const struct e007y_rear_startup_output *out,
                                  unsigned int index, u32 dma, u16 bytes)
{
 return out->bl[index].dma == dma && out->bl[index].bytes == bytes;
}

static int native_rear_validate_packet_commands(
 const struct e008l_rear_packet_dma *p, unsigned int packet)
{
 const struct e007y_rear_startup_variant *v = &e007y_startup_variants[packet];
 const struct e007y_rear_startup_output *out = &p->out;
 size_t expected, offset, cmd = 0, index = 0;
 unsigned int i;
 int ret;

 ret = e008l_rear_packet_sizing(packet, &expected);
 if (ret)
  return ret;
 if (!p->allocated || !p->slab_cpu || !p->dmi || !p->dynamic ||
     p->slab_bytes != expected || !p->slab_dma ||
     !IS_ALIGNED(p->slab_dma, E008L_REAR_ALIGN) ||
     !vfe680_x1e_dma_span_32bit(p->slab_dma, expected))
  return -ERANGE;
 offset = ALIGN((size_t)v->main_bytes, E008L_REAR_ALIGN);
 if (out->main != p->slab_cpu || out->main_bytes != v->main_bytes ||
     out->main_dma != p->slab_dma ||
     out->wrapper != (u8 *)p->slab_cpu + offset ||
     out->wrapper_bytes != E007Y_WRAPPER_BYTES ||
     out->wrapper_dma != p->slab_dma + offset ||
     out->dmi != p->dmi || out->dmi_count != v->dmi_count ||
     out->dynamic != p->dynamic)
  return -EPROTO;
 offset = ALIGN(offset + E007Y_WRAPPER_BYTES, E008L_REAR_ALIGN);
 while (cmd < v->main_bytes) {
  u32 word = get_unaligned_le32(v->skeleton + cmd);
  u8 opcode = word >> 24;
  if (opcode == E007Y_OPCODE_REG_CONT) {
   cmd += 8 + (size_t)(word & 0xffff) * sizeof(u32);
   continue;
  }
  if (opcode == E007Y_OPCODE_DMI || opcode == E007Y_OPCODE_DMI_32 ||
      opcode == E007Y_OPCODE_DMI_64) {
   size_t bytes = (word & 0xffff) + 1U;
   const struct e007y_rear_dmi_target *target;
   if (index >= out->dmi_count || bytes > expected - offset)
    return -EPROTO;
   target = &out->dmi[index++];
   if (target->cpu != (u8 *)p->slab_cpu + offset ||
       target->dma != p->slab_dma + offset || target->bytes != bytes)
    return -EPROTO;
   offset = ALIGN(offset + bytes, E008L_REAR_ALIGN);
   cmd += 12;
   continue;
  }
  return -EPROTO;
 }
 if (cmd != v->main_bytes || index != out->dmi_count || offset != expected)
  return -EPROTO;
 if (out->bl_count != (packet ? 6 : 4) ||
     !native_rear_bl_matches(out, 0, out->wrapper_dma + E007Y_WRAPPER_VFE_OFF, 4) ||
     !native_rear_bl_matches(out, 1, out->main_dma, out->main_bytes))
  return -EPROTO;
 if (!packet) {
  if (!native_rear_bl_matches(out, 2, out->wrapper_dma + E007Y_WRAPPER_CSID_OFF, 4) ||
      !native_rear_bl_matches(out, 3, out->wrapper_dma + E007Y_WRAPPER_COMPANION_OFF, 0x3c))
   return -EPROTO;
 } else {
  if (!native_rear_bl_matches(out, 2, out->wrapper_dma + E007Y_WRAPPER_EXTRA_OFF, 0x0c) ||
      !native_rear_bl_matches(out, 3, out->wrapper_dma + E007Y_WRAPPER_CSID_OFF, 4) ||
      !native_rear_bl_matches(out, 4, out->wrapper_dma + E007Y_WRAPPER_COMPANION_OFF, 0x10) ||
      !native_rear_bl_matches(out, 5, out->wrapper_dma + E007Y_WRAPPER_IRQ_OFF, 0x14) ||
      get_unaligned_le32(out->wrapper + E007Y_WRAPPER_IRQ_OFF + 0x10) != packet)
   return -EPROTO;
 }
 if (get_unaligned_le32(out->wrapper + E007Y_WRAPPER_VFE_OFF) != E007Y_CDM_CHANGE_VFE1 ||
     get_unaligned_le32(out->wrapper + E007Y_WRAPPER_CSID_OFF) != E007Y_CDM_CHANGE_CSID1)
  return -EPROTO;
 for (i = out->bl_count; i < E007Y_MAX_BL; i++)
  if (out->bl[i].dma || out->bl[i].bytes)
   return -EPROTO;
 return 0;
}

static int native_rear_validate_prepared_commands(
 const struct e008l_rear_command_set *set)
{
 unsigned int p, q;
 int ret;
 if (!set || !set->allocated || !set->prepared)
  return -EINVAL;
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
  const struct e008l_rear_packet_dma *a = &set->packet[p];
  if (set->packet_request_id[p] < 4 ||
      a->submitted != set->hardware_exposed)
   return -ESTALE;
  ret = native_rear_validate_packet_commands(a, p);
  if (ret)
   return ret;
  for (q = 0; q < p; q++) {
   const struct e008l_rear_packet_dma *b = &set->packet[q];
   if ((a->slab_dma < b->slab_dma + b->slab_bytes &&
        b->slab_dma < a->slab_dma + a->slab_bytes) ||
       native_rear_memory_overlap(a->slab_cpu, a->slab_bytes,
                                  b->slab_cpu, b->slab_bytes) ||
       native_rear_memory_overlap(a->dmi, a->out.dmi_count * sizeof(*a->dmi),
                                  b->dmi, b->out.dmi_count * sizeof(*b->dmi)) ||
       native_rear_memory_overlap(a->dynamic, sizeof(*a->dynamic),
                                  b->dynamic, sizeof(*b->dynamic)))
    return -EADDRINUSE;
  }
 }
 return 0;
}
#endif
