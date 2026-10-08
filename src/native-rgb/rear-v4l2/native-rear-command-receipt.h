/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef NATIVE_REAR_COMMAND_RECEIPT_H
#define NATIVE_REAR_COMMAND_RECEIPT_H
#include <linux/types.h>
/* Filled only under the FIFO0 submission mutex after synchronous BL_DONE.
 * Sequence is a software serialization tag, not a hardware request ID.
 */
struct native_rear_bl_receipt {
 u32 sequence, dma, irq_status;
 u16 bytes;
 bool complete;
};
#define NATIVE_REAR_COMMAND_BL_DONE (1U << 2)
static inline bool native_rear_bl_status_valid(u32 status)
{
 return (status & NATIVE_REAR_COMMAND_BL_DONE) &&
        !(status & ~(NATIVE_REAR_COMMAND_BL_DONE | (1U << 1)));
}

#endif
