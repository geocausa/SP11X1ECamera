/* SPDX-License-Identifier: MIT
 * E004nl pure C/ARM64 source-only fixture. Zero IO/sensor/firmware access.
 */
#include "rear-pix-route-contract.h"
#include <stdio.h>
#include <stdlib.h>

static unsigned int tests;
#define ASSERT(x) do { ++tests; if (!(x)) { \
    fprintf(stderr, "FAIL line %d: %s\\n", __LINE__, #x); exit(1); \
} } while (0)

static struct sp11_rear_pix_route accepted(void)
{
    return (struct sp11_rear_pix_route) {
        .is_ov13858 = true,
        .surface_board_id = 0x0491U,
        .observed_sensor_id = 0xd855U,
        .csiphy_id = 1U,
        .csid_id = 0U,
        .vfe_id = 0U,
        .phy_bus = SP11_REAR_BUS_DPHY,
        .lane_count = 4U,
        .bayer = SP11_REAR_BAYER_GRBG,
        .sensor_width = 4076U,
        .sensor_height = 2806U,
        .sensor_to_csiphy_link = true,
        .csiphy_to_csid_link = true,
        .csid0_to_vfe0_pix_link = true, /* topology ONLY, not streaming */
        .vfe0_pix_to_video_link = true,
        .ir_emitter_off = true,
        .linux_os_awake = true,
    };
}

int main(void)
{
    struct sp11_rear_pix_route r;
    ASSERT(sp11_rear_pix_validate_source_route(NULL) == SP11_REAR_ERR_SENSOR);
    r = accepted();
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ROUTE_SOURCE_ONLY);
    ASSERT(!sp11_rear_pix_has_proven_4k_output());
    ASSERT(sp11_rear_pix_bayer_after_crop(0U, 0U) == SP11_REAR_BAYER_GRBG);
    ASSERT(sp11_rear_pix_bayer_after_crop(1U, 0U) == SP11_REAR_BAYER_RGGB);
    ASSERT(sp11_rear_pix_bayer_after_crop(0U, 1U) == SP11_REAR_BAYER_BGGR);
    ASSERT(sp11_rear_pix_bayer_after_crop(1U, 1U) == SP11_REAR_BAYER_GBRG);
    /* This is only a hypothetical center-crop arithmetic example, NOT a
       claim about actual OEM rear camera crop or final ISP Bayer output. */
    ASSERT(sp11_rear_pix_bayer_after_crop(118U, 323U) == SP11_REAR_BAYER_BGGR);

    r = accepted(); r.is_ov13858 = false;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_SENSOR);
    r = accepted(); r.surface_board_id = 0x0561U;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_BOARD);
    r = accepted(); r.observed_sensor_id = 0U;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_SENSOR_ID);
    r = accepted(); r.csiphy_id = 2U; /* front C-PHY route */
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_CSIPHY);
    r = accepted(); r.csid_id = 1U;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_CSID);
    r = accepted(); r.vfe_id = 1U;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_VFE);
    r = accepted(); r.phy_bus = SP11_REAR_BUS_CPHY;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_PHY_BUS);
    r = accepted(); r.lane_count = 1U;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_LANES);
    r = accepted(); r.bayer = SP11_REAR_BAYER_RGGB;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_BAYER);
    r = accepted(); r.bayer = SP11_REAR_BAYER_BGGR;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_BAYER);
    r = accepted(); r.sensor_width = 3840U; r.sensor_height = 2160U;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_SENSOR_MODE);
    r = accepted(); r.sensor_to_csiphy_link = false;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_GRAPH);
    r = accepted(); r.csiphy_to_csid_link = false;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_GRAPH);
    r = accepted(); r.csid0_to_vfe0_pix_link = false;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_GRAPH);
    r = accepted(); r.vfe0_pix_to_video_link = false;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_GRAPH);
    r = accepted(); r.ir_emitter_off = false;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_IR_OR_STANDBY);
    r = accepted(); r.linux_os_awake = false;
    ASSERT(sp11_rear_pix_validate_source_route(&r) == SP11_REAR_ERR_IR_OR_STANDBY);
    printf("PASS E004nl %u source-only assertions; rear_4k_hardware_proven=0\n", tests);
    return 0;
}
