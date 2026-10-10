/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_FRONT_GAMMA_KERNEL_H
#define NATIVE_FRONT_GAMMA_KERNEL_H
#include "native-front-gamma.h"
struct camss_video;

/* Kernel-internal queue backend. Prepared semantic R/G/B data belongs to the
 * caller for this synchronous call; success transfers an independent capsule
 * copy to the existing frame-owned provider FIFO. No new userspace ABI.
 */
int camss_x1e_front_params_gamma_submit(struct camss_video *video,
                                      const nf_gamma_u8 *packet, size_t bytes,
                                      const nf_gamma_u8 *gamma, size_t gamma_bytes);
#endif
