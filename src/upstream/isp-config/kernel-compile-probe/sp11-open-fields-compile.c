// SPDX-License-Identifier: GPL-2.0-only
/* Compile-only probe. Never load; no camera integration. */
#include <linux/module.h>
#include "sp11-frame-fields.h"
static u8 output[SP11_FRAME_FIELDS_BYTES];
#define OPEN_BG { .width=3840, .height=2160, .columns=32, .rows=32, \
 .threshold_r=0x3ffff, .threshold_b=0x3ffff, .threshold_gr=0x3ffff, \
 .threshold_gb=0x3ffff, .y_weight_q4={4,8,4}, .enabled=true }
static const struct sp11_frame_fields fields = {
 .geometry={3840,2160,2560,1440}, .bg={OPEN_BG,OPEN_BG,OPEN_BG},
 .cst={601,117,306,-339,512,-173,-429,-83,512},
 .ccm={128,0,0,0,128,0,0,0,128}, .output_bits=8
};
#undef OPEN_BG
static int __init open_fields_init(void)
{
 int ret=sp11_frame_fields_commands(output,sizeof(output),&fields);
 if(ret) return ret;
 return sp11_cdm_dmi(output,sizeof(output),0x500,1,0x100000,1024,0,1024);
}
static void __exit open_fields_exit(void) {}
module_init(open_fields_init);
module_exit(open_fields_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Compile-only SP11 open ISP field type probe; never load");
