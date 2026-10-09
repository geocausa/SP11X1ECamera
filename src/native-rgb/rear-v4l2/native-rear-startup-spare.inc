/* SPDX-License-Identifier: GPL-2.0-only */
/* First rolling DMA set is allocated before any pipeline power/MMIO.
 * Pending VB2 wrapper stays on its FIFO until the original queue pops it.
 * The exclusive worker owns this descriptor; failure after hardware exposure
 * retains it with the faulted pair until reboot. No completion proof changes.
 */
struct native_rear_startup_spare {
 struct e008d_rear_dma_set dma;
 struct camss_buffer *buffer;
 u64 owner, generation, prepare_ns;
 bool taken;
};

static int native_rear_startup_spare_prepare(struct vfe_device *vfe,
 struct e008h_rear_prime_pair *pair, struct e008k_rear_request *req, u64 owner)
{
 struct camss_video *video = &vfe->line[VFE_LINE_PIX].video_out;
 struct vfe_output *output = &vfe->line[VFE_LINE_PIX].output;
 struct native_rear_startup_spare *spare;
 struct e008h_rear_prime_pair *check;
 struct e007z_rear_binding bindings[E007Z_REAR_WMS];
 unsigned long flags;
 unsigned int s, attempt;
 u64 tick = ktime_get_ns();
 int ret = -ENOBUFS;
 if (!pair || !req || !owner || pair->startup_spare || !pair->allocated ||
     pair->enabled || pair->slot0_preloaded_disabled || pair->faulted ||
     !pair->ledgers_bound || req->first_request_generation > U64_MAX - 2 ||
     !native_rear_full_cache_idle())
  return -EBUSY;
 spare = kzalloc(sizeof(*spare), GFP_KERNEL);
 if (!spare)
  return -ENOMEM;
 pair->startup_spare = spare; /* Every error path retains or frees this owner. */
 check = kzalloc(sizeof(*check), GFP_KERNEL);
 if (!check)
  return -ENOMEM;
 for (attempt = 0; attempt < 1000; attempt++) {
  if (READ_ONCE(video->x1e_pix_stop_requested)) {
   ret = -ECANCELED;
   goto out;
  }
  spin_lock_irqsave(&vfe->output_lock, flags);
  if (!list_empty(&output->pending_bufs))
   spare->buffer = list_first_entry(&output->pending_bufs,
                                    struct camss_buffer, queue);
  spin_unlock_irqrestore(&vfe->output_lock, flags);
  if (spare->buffer)
   break;
  usleep_range(500, 1000); /* Before power/MMIO/sensor startup only. */
 }
 if (!spare->buffer)
  goto out;
 if (spare->buffer == req->public_video[0] ||
     spare->buffer == req->public_video[1]) {
  ret = -EADDRINUSE;
  goto out;
 }
 ret = native_rear_public_dma_alloc(vfe, &spare->dma, spare->buffer);
 if (ret)
  goto out;
 check->dma[1] = spare->dma; /* Borrowed, never released from this scratch pair. */
 ret = e008d_rear_build_addresses(vfe, &check->dma[1], &check->addr[1]);
 if (ret)
  goto out;
 ret = e008h_rear_build_binding(check, 1, bindings);
 if (ret)
  goto out;
 spare->owner = owner;
 spare->generation = req->first_request_generation + 2;
 ret = e007z_rear_bind(&check->frame[1], owner, spare->generation, bindings);
 if (ret)
  goto out;
 /* Validate whole FULL mappings, all8 AUX DMA+CPU spans, and command arenas
  * against BOTH startup generations before any of the three can be exposed.
  */
 for (s = 0; s < E008H_REAR_SLOTS; s++) {
  check->dma[0] = pair->dma[s];
  check->addr[0] = pair->addr[s];
  check->frame[0] = pair->frame[s];
  ret = native_rear_queue_allocations_check(check);
  if (ret)
   goto out;
  ret = native_rear_command_allocations_check(req, check, owner);
  if (ret)
   goto out;
 }
 spare->prepare_ns = ktime_get_ns() - tick;
out:
 kfree(check); /* All DMA descriptors above are borrowed copies. */
 return ret;
}

static int native_rear_startup_spare_take(
 const struct e008h_rear_prime_pair *pair, struct e008d_rear_dma_set *dst,
 struct camss_buffer *buffer, u64 owner)
{
 struct native_rear_startup_spare *spare = pair->startup_spare;
 if (!spare)
  return -EPROTO;
 if (spare->taken)
  return -ENOENT; /* Later handoffs keep the original allocation/cache path. */
 if (owner != spare->owner || buffer != spare->buffer ||
     spare->generation != pair->frame[1].request_generation + 1 ||
     !native_rear_dma_full_valid(&spare->dma) ||
     spare->dma.public_full.exposed || spare->dma.public_full.stop_proven ||
     spare->dma.full.in_flight || spare->dma.prepared_disabled ||
     spare->dma.public_full_retired || spare->dma.auxiliary_live_retired ||
     dst->allocated || dst->public_full.acquired)
  return -ESTALE;
 *dst = spare->dma; /* Move exactly once; original bind/alias proof still follows. */
 memset(&spare->dma, 0, sizeof(spare->dma));
 spare->buffer = NULL;
 spare->taken = true;
 return 0;
}

static void native_rear_startup_spare_release(struct vfe_device *vfe,
 struct e008h_rear_prime_pair *pair, bool all_stops)
{
 struct native_rear_startup_spare *spare = pair->startup_spare;
 bool unused;
 if (!spare)
  return;
 unused = spare->dma.allocated;
 /* This set was never exposed. If exposure is uncertain, the caller never
  * reaches this function and retains the entire pair instead.
  */
 e008d_rear_release_partial(vfe, &spare->dma);
 dev_info(vfe->camss->dev,
  "NATIVE_REAR_PREFETCH_RELEASE owner=%llu taken=%u unused_freed=%u all_stops=%u wrapper_idle=1 pixel_bytes_read=0\n",
  spare->owner, spare->taken, unused, all_stops ? 15U : 0U);
 kfree(spare);
 pair->startup_spare = NULL;
}
