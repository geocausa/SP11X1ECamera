/* SPDX-License-Identifier: GPL-2.0-only */
/* Both complete generation ledgers and all hardware stop/IRQ barriers are
 * mandatory. The shared BUS/static configuration is prepared once with slot0
 * disabled. Slot1 is installed and read back at Epoch while enabled; it never
 * claims prepared_disabled. Do not invent that flag to authorize release.
 * Validate EVERY allocation under the same exclusive owner before freeing ANY.
 */
static int
e011i_rear_reclaim_after_stop(struct camss *camss, struct vfe_device *vfe,
                             struct e008h_rear_prime_pair *pair,
                             u64 owner_epoch,
                             const struct e008k_rear_result *result)
{
    u64 current_epoch;
    unsigned int s, i;

    if (!camss || !vfe || vfe->camss != camss ||
        !vfe680_e004nt_rear_4k_target(vfe) || !pair || !owner_epoch || !result ||
        !result->csid_quiesced || !result->bus_stopped ||
        !result->rtcdm_stopped || !result->source_stopped ||
        result->owner_released || result->dma_reclaimed ||
        !pair->allocated || !pair->enabled || !pair->slot0_preloaded_disabled ||
        !pair->dma[0].prepared_disabled ||
        !e008h_rear_both_complete(pair, owner_epoch) ||
        !e005y_vfe1_rear_sample_begin(&camss->e005y_vfe1_owner,
                                      true, &current_epoch) ||
        current_epoch != owner_epoch)
        return -EBUSY;

    for (s = 0; s < E008H_REAR_SLOTS; s++) {
        const struct e008d_rear_dma_set *set = &pair->dma[s];

        if (!set->allocated ||
            !set->full.in_flight || !set->full.cpu ||
            set->full.size != VFE680_E004NT_REAR_TOTAL_BYTES ||
            pair->frame[s].owner_epoch != owner_epoch ||
            !pair->frame[s].request_generation || pair->frame[s].pending ||
            pair->frame[s].faulted)
            return -EPROTO;
        for (i = 0; i < E008D_REAR_AUX_COUNT; i++) {
            const struct vfe680_e004nu_rear_wm_static *c;

            c = e008d_rear_contract_for_wm(set->aux[i].wm);
            if (!c || set->aux[i].wm != e008d_rear_aux_wms[i] || !set->aux[i].cpu ||
                set->aux[i].size != c->frame_incr)
                return -EPROTO;
        }
    }

    for (s = 0; s < E008H_REAR_SLOTS; s++) {
        pair->dma[s].full.in_flight = false;
        e008d_rear_release_partial(vfe, &pair->dma[s]);
    }
    return 0;
}

