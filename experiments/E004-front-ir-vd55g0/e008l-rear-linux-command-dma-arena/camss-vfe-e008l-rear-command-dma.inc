/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008l: Linux-owned coherent command-DMA backing for all four E007y rear
 * startup packets. No submit/call site is introduced here.
 */
#ifndef VFE680_E008L_REAR_COMMAND_DMA_ARENA_INC
#define VFE680_E008L_REAR_COMMAND_DMA_ARENA_INC

#define E008L_REAR_ALIGN 4U

struct e008l_rear_packet_dma {
	void *slab_cpu;
	dma_addr_t slab_dma;
	size_t slab_bytes;
	struct e007y_rear_dmi_target *dmi;
	struct e006g_rear_dynamic_payloads *dynamic;
	struct e007y_rear_startup_output out;
	bool allocated;
	bool submitted;
};

struct e008l_rear_command_set {
	struct e008l_rear_packet_dma packet[E007Y_STARTUP_PACKETS];
	bool allocated;
	bool hardware_exposed;
};

static int
e008l_rear_packet_sizing(u8 packet, size_t *slab_bytes)
{
	const struct e007y_rear_startup_variant *v;
	size_t off, total, dmi_seen = 0;

	if (!slab_bytes || packet >= E007Y_STARTUP_PACKETS)
		return -EINVAL;
	v = &e007y_startup_variants[packet];

	total = ALIGN((size_t)v->main_bytes, E008L_REAR_ALIGN);
	if (total > SIZE_MAX - E007Y_WRAPPER_BYTES)
		return -EOVERFLOW;
	total = ALIGN(total + E007Y_WRAPPER_BYTES, E008L_REAR_ALIGN);

	off = 0;
	while (off < v->main_bytes) {
		u32 header;
		u8 opcode;

		if (v->main_bytes - off < sizeof(u32))
			return -EPROTO;
		header = get_unaligned_le32(v->skeleton + off);
		opcode = header >> 24;
		if (opcode == E007Y_OPCODE_REG_CONT) {
			u16 count = header & 0xffff;
			size_t bytes = 8 + (size_t)count * sizeof(u32);

			if (!count || bytes > v->main_bytes - off)
				return -EPROTO;
			off += bytes;
			continue;
		}
		if (opcode == E007Y_OPCODE_DMI ||
		    opcode == E007Y_OPCODE_DMI_32 ||
		    opcode == E007Y_OPCODE_DMI_64) {
			size_t payload = (header & 0xffff) + 1U;

			if (v->main_bytes - off < 12 || dmi_seen >= v->dmi_count)
				return -EPROTO;
			if (payload > SIZE_MAX - total)
				return -EOVERFLOW;
			total = ALIGN(total + payload, E008L_REAR_ALIGN);
			dmi_seen++;
			off += 12;
			continue;
		}
		return -EPROTO;
	}

	if (off != v->main_bytes || dmi_seen != v->dmi_count)
		return -EPROTO;
	*slab_bytes = total;
	return 0;
}

static int
e008l_rear_packet_bind_layout(struct e008l_rear_packet_dma *p, u8 packet)
{
	const struct e007y_rear_startup_variant *v;
	size_t cmd_off = 0, dma_off, dmi_seen = 0;

	if (!p || !p->slab_cpu || !p->slab_bytes ||
	    packet >= E007Y_STARTUP_PACKETS)
		return -EINVAL;
	v = &e007y_startup_variants[packet];

	p->out.main = p->slab_cpu;
	p->out.main_bytes = v->main_bytes;
	p->out.main_dma = (u32)p->slab_dma;

	dma_off = ALIGN((size_t)v->main_bytes, E008L_REAR_ALIGN);
	p->out.wrapper = (u8 *)p->slab_cpu + dma_off;
	p->out.wrapper_bytes = E007Y_WRAPPER_BYTES;
	p->out.wrapper_dma = (u32)(p->slab_dma + dma_off);
	dma_off = ALIGN(dma_off + E007Y_WRAPPER_BYTES, E008L_REAR_ALIGN);

	p->out.dmi = p->dmi;
	p->out.dmi_count = v->dmi_count;
	p->out.dynamic = p->dynamic;

	while (cmd_off < v->main_bytes) {
		u32 header = get_unaligned_le32(v->skeleton + cmd_off);
		u8 opcode = header >> 24;

		if (opcode == E007Y_OPCODE_REG_CONT) {
			u16 count = header & 0xffff;
			cmd_off += 8 + (size_t)count * sizeof(u32);
			continue;
		}
		if (opcode == E007Y_OPCODE_DMI ||
		    opcode == E007Y_OPCODE_DMI_32 ||
		    opcode == E007Y_OPCODE_DMI_64) {
			size_t payload = (header & 0xffff) + 1U;

			if (dmi_seen >= v->dmi_count ||
			    dma_off + payload > p->slab_bytes)
				return -EPROTO;
			p->dmi[dmi_seen].cpu = (u8 *)p->slab_cpu + dma_off;
			p->dmi[dmi_seen].bytes = payload;
			p->dmi[dmi_seen].dma = (u32)(p->slab_dma + dma_off);
			dma_off = ALIGN(dma_off + payload, E008L_REAR_ALIGN);
			dmi_seen++;
			cmd_off += 12;
			continue;
		}
		return -EPROTO;
	}

	if (dmi_seen != v->dmi_count || dma_off != p->slab_bytes)
		return -EPROTO;
	return 0;
}

static void
e008l_rear_packet_release(struct vfe_device *vfe,
			  struct e008l_rear_packet_dma *p)
{
	if (!vfe || !p)
		return;
	if (p->slab_cpu) {
		memzero_explicit(p->slab_cpu, p->slab_bytes);
		dma_free_coherent(vfe->camss->dev, p->slab_bytes,
				  p->slab_cpu, p->slab_dma);
	}
	if (p->dynamic) {
		memzero_explicit(p->dynamic, sizeof(*p->dynamic));
		kfree(p->dynamic);
	}
	kfree(p->dmi);
	memset(p, 0, sizeof(*p));
}

static int __used
e008l_rear_command_alloc(struct vfe_device *vfe,
			 struct e008l_rear_command_set *set)
{
	unsigned int packet;
	int ret;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !set || set->allocated)
		return -EINVAL;
	memset(set, 0, sizeof(*set));

	for (packet = 0; packet < E007Y_STARTUP_PACKETS; packet++) {
		struct e008l_rear_packet_dma *p = &set->packet[packet];
		const struct e007y_rear_startup_variant *v =
			&e007y_startup_variants[packet];
		size_t bytes;

		ret = e008l_rear_packet_sizing(packet, &bytes);
		if (ret)
			goto fail;

		p->dmi = kcalloc(v->dmi_count, sizeof(*p->dmi), GFP_KERNEL);
		p->dynamic = kzalloc(sizeof(*p->dynamic), GFP_KERNEL);
		if (!p->dmi || !p->dynamic) {
			ret = -ENOMEM;
			goto fail;
		}

		p->slab_cpu = dma_alloc_coherent(vfe->camss->dev, bytes,
						 &p->slab_dma, GFP_KERNEL);
		if (!p->slab_cpu) {
			ret = -ENOMEM;
			goto fail;
		}
		p->slab_bytes = bytes;
		if (!IS_ALIGNED(p->slab_dma, E008L_REAR_ALIGN) ||
		    !vfe680_x1e_dma_span_32bit(p->slab_dma, bytes)) {
			ret = -ERANGE;
			goto fail;
		}
		memset(p->slab_cpu, 0, bytes);

		ret = e008l_rear_packet_bind_layout(p, packet);
		if (ret)
			goto fail;
		p->allocated = true;
	}
	set->allocated = true;
	return 0;

fail:
	for (packet = 0; packet < E007Y_STARTUP_PACKETS; packet++)
		e008l_rear_packet_release(vfe, &set->packet[packet]);
	memset(set, 0, sizeof(*set));
	return ret;
}

static struct e007y_rear_startup_output * __used
e008l_rear_command_output(struct e008l_rear_command_set *set, u8 packet)
{
	if (!set || !set->allocated || packet >= E007Y_STARTUP_PACKETS ||
	    !set->packet[packet].allocated)
		return NULL;
	return &set->packet[packet].out;
}

static int __used
e008l_rear_command_mark_submitted(struct e008l_rear_command_set *set, u8 packet)
{
	struct e008l_rear_packet_dma *p;

	if (!set || !set->allocated || packet >= E007Y_STARTUP_PACKETS)
		return -EINVAL;
	p = &set->packet[packet];
	if (!p->allocated || p->submitted || !p->out.bl_count)
		return -EINVAL;
	p->submitted = true;
	set->hardware_exposed = true;
	return 0;
}

/*
 * Before any submit the arena may be released immediately. Once any BL was
 * submitted, retain every packet until RT-CDM is proven stopped; this is
 * deliberately stricter than attempting to infer per-BL fetch completion.
 */
static int __used
e008l_rear_command_release(struct vfe_device *vfe,
			   struct e008l_rear_command_set *set,
			   bool rtcdm_stopped)
{
	unsigned int packet;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !set || !set->allocated)
		return -EINVAL;
	if (set->hardware_exposed && !rtcdm_stopped)
		return -EBUSY;

	for (packet = 0; packet < E007Y_STARTUP_PACKETS; packet++)
		e008l_rear_packet_release(vfe, &set->packet[packet]);
	memset(set, 0, sizeof(*set));
	return 0;
}

struct e008l_rear_command_ops {
	int (*alloc)(struct vfe_device *, struct e008l_rear_command_set *);
	struct e007y_rear_startup_output *(*output)(
		struct e008l_rear_command_set *, u8);
	int (*mark_submitted)(struct e008l_rear_command_set *, u8);
	int (*release)(struct vfe_device *, struct e008l_rear_command_set *,
		       bool);
};

static const struct e008l_rear_command_ops e008l_rear_command_recipe __used = {
	.alloc = e008l_rear_command_alloc,
	.output = e008l_rear_command_output,
	.mark_submitted = e008l_rear_command_mark_submitted,
	.release = e008l_rear_command_release,
};

static int __used e008l_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

#endif
