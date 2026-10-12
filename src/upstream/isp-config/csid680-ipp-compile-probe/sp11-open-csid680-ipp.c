// SPDX-License-Identifier: GPL-2.0-only
/* Compile-only object. No hardware caller; never load. */
#include <linux/module.h>
#include "sp11-csid680-ipp.h"

int sp11_csid680_ipp_compile_probe(struct sp11_csid680_ipp_plan *out,
                                 const struct sp11_csid680_ipp_input *input);
int sp11_csid680_ipp_compile_probe(struct sp11_csid680_ipp_plan *out,
                                 const struct sp11_csid680_ipp_input *input)
{
    return sp11_csid680_ipp_prepare(out, input);
}
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Compile-only CSID680 disabled RAW10 IPP input plan; never load");
