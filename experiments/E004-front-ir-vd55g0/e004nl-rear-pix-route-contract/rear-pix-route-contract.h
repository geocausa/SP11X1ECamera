/* SPDX-License-Identifier: MIT
 * E004nl: independent source-only OV13858 rear PIX identity/route contract.
 * NOT imported by CAMSS, not a register/firmware writer, not an arm gate.
 * Explicitly separate the input-route proof from 4K ISP output validation.
 */
#ifndef SP11_E004NL_REAR_PIX_ROUTE_CONTRACT_H
#define SP11_E004NL_REAR_PIX_ROUTE_CONTRACT_H

#include <stdbool.h>
#include <stdint.h>

enum sp11_rear_pix_check {
    SP11_REAR_ROUTE_SOURCE_ONLY = 0,
    SP11_REAR_ERR_SENSOR = 1,
    SP11_REAR_ERR_BOARD,
    SP11_REAR_ERR_SENSOR_ID,
    SP11_REAR_ERR_CSIPHY,
    SP11_REAR_ERR_CSID,
    SP11_REAR_ERR_VFE,
    SP11_REAR_ERR_PHY_BUS,
    SP11_REAR_ERR_LANES,
    SP11_REAR_ERR_BAYER,
    SP11_REAR_ERR_SENSOR_MODE,
    SP11_REAR_ERR_GRAPH,
    SP11_REAR_ERR_IR_OR_STANDBY
};

enum sp11_rear_phy_bus {
    SP11_REAR_BUS_CPHY = 1,
    SP11_REAR_BUS_DPHY = 4
};
enum sp11_rear_bayer {
    SP11_REAR_BAYER_RGGB = 0,
    SP11_REAR_BAYER_GRBG = 1,
    SP11_REAR_BAYER_BGGR = 2,
    SP11_REAR_BAYER_GBRG = 3
};

/* Only scalar observed/verified metadata; no sensor/ISP register addresses.
 * Node numbers are discovered per-boot, not persisted in this contract.
 */
struct sp11_rear_pix_route {
    bool is_ov13858;
    uint32_t surface_board_id;
    uint32_t observed_sensor_id;
    uint32_t csiphy_id;
    uint32_t csid_id;
    uint32_t vfe_id;
    enum sp11_rear_phy_bus phy_bus;
    uint32_t lane_count;
    enum sp11_rear_bayer bayer;
    uint32_t sensor_width;
    uint32_t sensor_height;
    bool sensor_to_csiphy_link;
    bool csiphy_to_csid_link;
    bool csid0_to_vfe0_pix_link;
    bool vfe0_pix_to_video_link;
    bool ir_emitter_off;
    bool linux_os_awake;
};

/* Validates ONLY the archived E003i-IG graph + real E004lr RAW input
 * identity, and the E002 Windows sensor ID/board mapping. The accepted
 * input is NOT native rear ISP output or approval to configure hardware.
 */
static inline enum sp11_rear_pix_check
sp11_rear_pix_validate_source_route(const struct sp11_rear_pix_route *r)
{
    if (!r || !r->is_ov13858)
        return SP11_REAR_ERR_SENSOR;
    if (r->surface_board_id != 0x0491U)
        return SP11_REAR_ERR_BOARD;
    if (r->observed_sensor_id != 0xd855U)
        return SP11_REAR_ERR_SENSOR_ID;
    if (r->csiphy_id != 1U)
        return SP11_REAR_ERR_CSIPHY;
    if (r->csid_id != 0U)
        return SP11_REAR_ERR_CSID;
    if (r->vfe_id != 0U)
        return SP11_REAR_ERR_VFE;
    if (r->phy_bus != SP11_REAR_BUS_DPHY)
        return SP11_REAR_ERR_PHY_BUS;
    if (r->lane_count != 4U)
        return SP11_REAR_ERR_LANES;
    if (r->bayer != SP11_REAR_BAYER_GRBG)
        return SP11_REAR_ERR_BAYER;
    if (r->sensor_width != 4076U || r->sensor_height != 2806U)
        return SP11_REAR_ERR_SENSOR_MODE;
    if (!r->sensor_to_csiphy_link || !r->csiphy_to_csid_link ||
        !r->csid0_to_vfe0_pix_link || !r->vfe0_pix_to_video_link)
        return SP11_REAR_ERR_GRAPH;
    if (!r->ir_emitter_off || !r->linux_os_awake)
        return SP11_REAR_ERR_IR_OR_STANDBY;
    return SP11_REAR_ROUTE_SOURCE_ONLY;
}

/* Pure CFA phase transform for an input GRBG Bayer mosaic, ONLY when
 * a source-validated output crop offset becomes available. An odd crop
 * offset changes the output Bayer tag; it does not imply that Windows uses
 * that crop. Never use this helper to guess an ISP crop or AWB gains.
 */
static inline enum sp11_rear_bayer
sp11_rear_pix_bayer_after_crop(uint32_t x_offset, uint32_t y_offset)
{
    const unsigned int parity = ((y_offset & 1U) << 1) | (x_offset & 1U);
    switch (parity) {
    case 0U: return SP11_REAR_BAYER_GRBG;
    case 1U: return SP11_REAR_BAYER_RGGB;
    case 2U: return SP11_REAR_BAYER_BGGR;
    default: return SP11_REAR_BAYER_GBRG;
    }
}

/* 4076x2806 RAW is larger than 3840x2160 output. Merely observing or
 * selecting 3840x2160 output cannot establish correct rear crop, Bayer
 * parity, color, stride, memory ownership, firmware IPC or actual frames.
 * Crucially the front 2560x1440 QC10C surface is NOT rear 4K evidence.
 */
static inline bool sp11_rear_pix_has_proven_4k_output(void)
{
    return false; /* Unconditional: no rear native-ISP optical proof yet. */
}

#endif
