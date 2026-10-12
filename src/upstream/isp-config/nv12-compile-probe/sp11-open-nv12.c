// SPDX-License-Identifier: GPL-2.0-only
/* Compile-only object; never load. No hardware caller or enable command. */
#include <linux/module.h>
#include "sp11-vfe680-nv12.h"

int sp11_vfe680_nv12_compile_probe(u8 *out, size_t capacity,
                                 const struct sp11_vfe680_nv12 *mode);
int sp11_vfe680_nv12_compile_probe(u8 *out, size_t capacity,
                                 const struct sp11_vfe680_nv12 *mode)
{
    return sp11_vfe680_nv12_setup_disabled(out, capacity, mode);
}
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Compile-only VFE680 disabled NV12 setup builder; never load");
