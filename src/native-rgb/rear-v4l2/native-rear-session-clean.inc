/* SPDX-License-Identifier: GPL-2.0-only */
static bool native_rear_session_clean(const struct e008n_rear_result *r)
{
 const struct e008k_rear_result *t = &r->transaction;
 return r->identity_consumed && r->command_arena_allocated &&
        r->preflight_materialized && r->command_arena_released &&
        t->packet_submitted[0] && t->packet_submitted[1] &&
        t->packet_submitted[2] && t->packet_submitted[3] &&
        t->slot0_enabled && t->slot1_programmed && t->both_frames_complete &&
        t->csid_quiesced && t->bus_stopped && t->rtcdm_stopped &&
        t->source_stopped && t->ledgers_released && t->owner_released &&
        t->dma_reclaimed && !t->dma_intentionally_pinned;
}
