/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008k rear CSID bridge. Packet0/packet1 RT-CDM materializers own startup
 * programming; this bridge intentionally exposes only exact-route validation
 * and the source-locked final IPP enable.
 */
#ifndef CAMSS_CSID_E008K_REAR_BRIDGE_INC
#define CAMSS_CSID_E008K_REAR_BRIDGE_INC

#include "camss-e008k-rear-bridge.h"

bool csid680_e008k_rear_mode0(struct csid_device *csid)
{
	return csid_e004ns_rear_ipp_mode0(csid);
}

int csid680_e008k_rear_enable(struct csid_device *csid)
{
	return csid_e004ns_rear_ipp_enable(csid);
}

#endif
