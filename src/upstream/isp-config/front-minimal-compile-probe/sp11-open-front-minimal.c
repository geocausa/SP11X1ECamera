// SPDX-License-Identifier: GPL-2.0-only
/* Compile-only object, never load. No MMIO, firmware, DMA or camera caller. */
#include <linux/module.h>
#include "sp11-front-minimal.h"
int sp11_front_minimal_compile_probe(u8 *out, size_t capacity,
                                    const struct sp11_front_minimal *mode);
int sp11_front_minimal_compile_probe(u8 *out, size_t capacity,
                                    const struct sp11_front_minimal *mode)
{
    return sp11_front_minimal_commands(out, capacity, mode);
}
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Source-only independent SP11 front processing compiler; never load");
