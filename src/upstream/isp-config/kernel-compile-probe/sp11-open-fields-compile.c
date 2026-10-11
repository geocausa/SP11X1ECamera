// SPDX-License-Identifier: GPL-2.0-only
/* Compile-only probe. Never load this module; there is no camera integration. */
#include <linux/module.h>
#include "sp11-front-fields.h"
static int __init open_fields_init(void)
{
 u8 out[128];
 const s16 cst[9] = {601,117,306,-339,512,-173,-429,-83,512};
 const s16 ccm[9] = {128,0,0,0,128,0,0,0,128};
 int ret;
 ret=sp11_front_cst_commands(out,sizeof(out),cst);
 if(ret) return ret;
 ret=sp11_front_ccm_commands(out,sizeof(out),ccm);
 if(ret) return ret;
 ret=sp11_front_round_commands(out,sizeof(out),8);
 if(ret) return ret;
 return sp11_cdm_dmi(out,sizeof(out),0x500,1,0x100000,1024,0,1024);
}
static void __exit open_fields_exit(void) {}
module_init(open_fields_init);
module_exit(open_fields_exit);
MODULE_LICENSE("GPL");
