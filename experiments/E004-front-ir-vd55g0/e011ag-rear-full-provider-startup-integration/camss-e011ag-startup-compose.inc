/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * E011AG: offline full-provider startup composition.
 * The caller owns four complete non-adaptive bases and an unsubmitted arena.
 * This is a composition contract, not a complete semantic bootstrap producer.
 * No MMIO, submission, DMA completion or runtime camera entry point exists.
 */
#ifndef VFE680_E011AG_STARTUP_COMPOSE_INC
#define VFE680_E011AG_STARTUP_COMPOSE_INC

static bool e011ag_overlap(const void *a, size_t an, const void *b, size_t bn)
{
	unsigned long x = (unsigned long)a, y = (unsigned long)b;
	return x <= y ? y - x < an : x - y < bn;
}

/* Check the actual E008l layout before any write/clear. The allocation
 * metadata and descriptor arrays must be valid, caller-owned objects. */
static int e011ag_validate_arena(struct e008l_rear_command_set *commands)
{
 unsigned int p;
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
  struct e008l_rear_packet_dma *d = &commands->packet[p];
  struct e007y_rear_startup_output *o = &d->out;
  const struct e007y_rear_startup_variant *v = &e007y_startup_variants[p];
  size_t bytes, off = 0, index = 0;
  size_t payload_off = ALIGN((size_t)v->main_bytes, E008L_REAR_ALIGN);
  if (e008l_rear_packet_sizing(p, &bytes) || !d->slab_cpu ||
      !d->dmi || !d->dynamic || d->slab_bytes != bytes ||
      !IS_ALIGNED(d->slab_dma, E008L_REAR_ALIGN) ||
      !vfe680_x1e_dma_span_32bit(d->slab_dma, bytes) ||
      o->main != d->slab_cpu || o->main_bytes != v->main_bytes ||
      o->main_dma != (u32)d->slab_dma ||
      o->wrapper != (u8 *)d->slab_cpu + payload_off ||
      o->wrapper_bytes != E007Y_WRAPPER_BYTES ||
      o->wrapper_dma != (u32)(d->slab_dma + payload_off) ||
      o->dmi != d->dmi || o->dmi_count != v->dmi_count ||
      o->dynamic != d->dynamic)
   return -EINVAL;
  payload_off = ALIGN(payload_off + E007Y_WRAPPER_BYTES, E008L_REAR_ALIGN);
  while (off < v->main_bytes) {
   u32 h = get_unaligned_le32(v->skeleton + off);
   if ((h >> 24) == E007Y_OPCODE_REG_CONT) {
    off += 8 + 4 * (h & 0xffff);
   } else {
    size_t n = (h & 0xffff) + 1;
    if (index >= o->dmi_count || o->dmi[index].bytes != n ||
        o->dmi[index].cpu != (u8 *)d->slab_cpu + payload_off ||
        o->dmi[index].dma != (u32)(d->slab_dma + payload_off))
     return -EINVAL;
    payload_off = ALIGN(payload_off + n, E008L_REAR_ALIGN);
    index++;
    off += 12;
   }
  }
  if (index != o->dmi_count || payload_off != d->slab_bytes)
   return -EPROTO;
 }
 return 0;
}

static void e011ag_clear_commands(struct e008l_rear_command_set *commands)
{
	unsigned int p;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		struct e008l_rear_packet_dma *d = &commands->packet[p];
		memzero_explicit(d->slab_cpu, d->slab_bytes);
		memzero_explicit(d->dynamic, sizeof(*d->dynamic));
		memset(d->out.bl, 0, sizeof(d->out.bl));
		d->out.bl_count = 0;
	}
}

/* Validate the complete register-family union, including currently unused
 * fields, using the real packet-aware providers and this packet's identity. */
static int e011ag_validate_registers(struct e008o_rear_semantic_set *set)
{
 unsigned int p, recipe;
 for (p = 0; p < E007Y_STARTUP_PACKETS; p++)
  for (recipe = 0; recipe < E007Y_STARTUP_PACKETS; recipe++) {
   const struct e007y_rear_startup_variant *v = &e007y_startup_variants[recipe];
   size_t off = 0;
   while (off < v->main_bytes) {
    u32 h = get_unaligned_le32(v->skeleton + off);
    if ((h >> 24) == E007Y_OPCODE_REG_CONT) {
     unsigned int i, n = h & 0xffff;
     u32 reg = get_unaligned_le32(v->skeleton + off + 4);
     for (i = 0; i < n; i++) {
      u32 ignored;
      int ret = e007d_rear_fill_startup(&set->packet[p].regs, p,
                                        (u16)(reg + 4 * i), &ignored);
      if (ret)
       return ret;
     }
     off += 8 + 4 * n;
    } else {
     off += 12;
    }
   }
  }
 return 0;
}

static int e011ag_rear_compose_startup(
	struct e008o_rear_semantic_set *set,
	struct e008o_rear_semantic_set *work,
	const struct e008o_rear_packet_semantics base[E007Y_STARTUP_PACKETS],
	const struct e011ae_rear_startup_bpc_source *bpc,
	const struct e011z_rear_startup_adaptive_wire *wire,
	struct e008l_rear_command_set *commands)
{
	unsigned int p;
	int ret;

	/* Rejected exposed/invalid arenas are never changed or cleared. */
	if (!set || !work || !base || !bpc || !wire || !commands ||
	    !commands->allocated || commands->hardware_exposed)
		return -EINVAL;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++)
		if (!commands->packet[p].allocated ||
		    commands->packet[p].submitted)
			return -EINVAL;
	if (e011ag_overlap(set, sizeof(*set), work, sizeof(*work)) ||
	    e011ag_overlap(set, sizeof(*set), base,
			    sizeof(*base) * E007Y_STARTUP_PACKETS) ||
	    e011ag_overlap(work, sizeof(*work), base,
			    sizeof(*base) * E007Y_STARTUP_PACKETS) ||
	    e011ag_overlap(set, sizeof(*set), bpc, sizeof(*bpc)) ||
	    e011ag_overlap(work, sizeof(*work), bpc, sizeof(*bpc)) ||
	    e011ag_overlap(set, sizeof(*set), wire, sizeof(*wire)) ||
	    e011ag_overlap(work, sizeof(*work), wire, sizeof(*wire)))
		return -EINVAL;

	ret = e011ag_validate_arena(commands);
	if (ret)
		return ret;

	/* Caller serializes preparation and guarantees disjoint arena backing. */
	memset(set, 0, sizeof(*set));
	memset(work, 0, sizeof(*work));
	e011ag_clear_commands(commands);
	memcpy(work->packet, base, sizeof(work->packet));
	ret = e011ae_rear_bind_startup_bpc(work, bpc);
	if (ret)
		goto fail;
	/* Value-copy plus actual recursive validation rebases every callback. */
	ret = e011z_rear_bind_startup_adaptive(set, work->packet, wire);
	if (ret)
		goto fail;
	ret = e011ag_validate_registers(set);
	if (ret)
		goto fail;
	/* Exercise every register/DMI provider in each real packet recipe. */
	ret = e008o_rear_materialize_commands(set, commands);
	if (ret)
		goto fail;
	memzero_explicit(work, sizeof(*work));
	return 0;
fail:
	e011ag_clear_commands(commands);
	memzero_explicit(set, sizeof(*set));
	memzero_explicit(work, sizeof(*work));
	return ret;
}

struct e011ag_rear_startup_ops {
 int (*compose)(struct e008o_rear_semantic_set *,
                struct e008o_rear_semantic_set *,
                const struct e008o_rear_packet_semantics *,
                const struct e011ae_rear_startup_bpc_source *,
                const struct e011z_rear_startup_adaptive_wire *,
                struct e008l_rear_command_set *);
};
static const struct e011ag_rear_startup_ops e011ag_rear_startup_recipe __used = {
 .compose = e011ag_rear_compose_startup,
};

static int __used e011ag_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}
#endif
