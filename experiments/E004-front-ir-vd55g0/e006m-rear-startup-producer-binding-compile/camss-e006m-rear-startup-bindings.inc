/* SPDX-License-Identifier: MIT */
/*
 * E006m compile-only rear startup-register binding.
 *
 * Generated from the safe E006l owner map. No captured Windows values,
 * pointers, IOVAs or command bytes are embedded. This file is unreachable
 * at runtime and exists only to make startup ownership compiler-visible.
 */

enum e006m_rear_startup_source {
	E006M_SOURCE_STEADY_SINGLETON = 0,
	E006M_SOURCE_STEADY_DYNAMIC,
	E006M_SOURCE_SHARED_STARTUP,
	E006M_SOURCE_EXTRA_STARTUP,
};

enum e006m_rear_startup_owner {
	E006M_OWNER_NONE = 0,
	E006M_OWNER_AEC_BE_STATS17,
	E006M_OWNER_AWB_BG_STATS17,
	E006M_OWNER_BAYER_GTM101,
	E006M_OWNER_BAYER_LTM101,
	E006M_OWNER_BC101,
	E006M_OWNER_BFSTATS25,
	E006M_OWNER_BHIST_STATS16,
	E006M_OWNER_BPC_ABF,
	E006M_OWNER_CROP12,
	E006M_OWNER_CST12,
	E006M_OWNER_LCAC111,
	E006M_OWNER_MNDS23,
	E006M_OWNER_PDPC,
	E006M_OWNER_ROUND_CLAMP12,
	E006M_OWNER_RS_STATS14,
	E006M_OWNER_TINTLESS_BG_STATS17,
	E006M_OWNER_UV_GAMMA101,
	E006M_OWNER_VFE680_PERIOD_CFG,
	E006M_OWNER_WB,
	E006M_OWNER_COUNT,
};

struct e006m_rear_startup_reg {
	u16 reg;
	u8 source;
	u8 owner;
};

static const struct e006m_rear_startup_reg e006m_rear_startup_regs[] = {
	{ .reg = 0x0024, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x002c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x008c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_VFE680_PERIOD_CFG },
	{ .reg = 0x0090, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b6c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b70, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b74, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b78, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b7c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b80, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b84, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b88, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b8c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b90, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3b94, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d58, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d5c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d70, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d78, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_PDPC },
	{ .reg = 0x3d7c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d80, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_PDPC },
	{ .reg = 0x3d84, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d88, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3d8c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3db4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3db8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3dd4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3dd8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x3f60, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_BC101 },
	{ .reg = 0x3f64, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_BC101 },
	{ .reg = 0x3f68, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_BC101 },
	{ .reg = 0x4358, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x435c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4360, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4368, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x436c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4370, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4374, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4378, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x437c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4380, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4384, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4388, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x438c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4390, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4394, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4398, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4560, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4568, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x456c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4570, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_WB },
	{ .reg = 0x4574, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4578, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x457c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4580, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4584, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4588, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x458c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4590, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4594, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4758, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x475c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4760, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4770, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4774, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4958, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x495c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4960, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4968, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x496c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4980, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4984, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4988, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x498c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49a0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49a4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49a8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49ac, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49b0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49b4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49b8, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49bc, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49c8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49cc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49d0, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BPC_ABF },
	{ .reg = 0x49d4, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BPC_ABF },
	{ .reg = 0x49d8, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BPC_ABF },
	{ .reg = 0x49dc, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BPC_ABF },
	{ .reg = 0x49e0, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BPC_ABF },
	{ .reg = 0x49e4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x49e8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4b60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4b68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4b6c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4b70, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4b74, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4b78, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4b7c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x4d60, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_BAYER_GTM101 },
	{ .reg = 0x5260, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_BAYER_LTM101 },
	{ .reg = 0x5460, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_LCAC111 },
	{ .reg = 0x5660, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5668, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x566c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5670, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5674, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5860, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5868, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x586c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5870, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5874, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5878, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x587c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5880, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5884, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5888, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x588c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a58, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a5c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a64, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a6c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a70, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a74, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a78, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a7c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a80, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a84, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a88, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a8c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a90, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a94, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a98, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5a9c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5aa0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5aa4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5aa8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5aac, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ab0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ab4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ab8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5abc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ac0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ac4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ac8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5acc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ad0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ad4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ad8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5adc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ae0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ae4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ae8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5aec, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5af0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5af4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5af8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5afc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b00, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b04, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b08, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b0c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b10, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b14, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b18, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b1c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b20, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b24, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b28, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b2c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b30, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b34, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b38, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b3c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b40, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b44, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b48, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b4c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b50, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b54, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b58, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b5c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b64, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b6c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b70, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b74, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b78, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b7c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b80, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b84, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b88, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b8c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b90, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b94, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b98, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5b9c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ba0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ba4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ba8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bac, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bb0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bb4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bb8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bbc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bc0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bc4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bc8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bcc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bd0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bd4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bd8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bdc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5be0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5be4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5be8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bec, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bf0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bf4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bf8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5bfc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c00, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c04, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c08, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c0c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c10, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c14, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c18, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c1c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c20, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c24, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c28, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c2c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c30, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c34, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c38, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c3c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c40, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c44, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c48, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c4c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c50, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c54, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c58, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c5c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c64, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c6c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c70, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c74, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c78, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c7c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c80, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c84, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c88, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c8c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c90, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c94, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c98, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5c9c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ca0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ca4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ca8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cac, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cb0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cb4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cb8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cbc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cc0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cc4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cc8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ccc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cd0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cd4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cd8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cdc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ce0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ce4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ce8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cec, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cf0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cf4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cf8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5cfc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d00, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d04, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d08, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d0c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d10, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d14, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d18, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d1c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d20, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d24, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d28, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d2c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d30, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d34, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d38, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d3c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d40, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d44, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d48, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d4c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d50, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d54, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d58, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d5c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d64, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d6c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d70, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d74, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d78, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d7c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d80, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d84, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d88, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d8c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d90, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d94, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d98, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5d9c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5da0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5da4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5da8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dac, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5db0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5db4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5db8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dbc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dc0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dc4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dc8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dcc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dd0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dd4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dd8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5ddc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5de0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5de4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5de8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dec, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5df0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5df4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5df8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5dfc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e00, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e04, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e08, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e0c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e10, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e14, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e18, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e1c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e20, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e24, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e28, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e2c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e30, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e34, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e38, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e3c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e40, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e44, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e48, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e4c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e50, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e54, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e58, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e5c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e64, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e6c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5e70, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5f58, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5f5c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0x5f60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0x6160, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6168, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x616c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6170, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6174, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6178, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x617c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6180, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6184, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6188, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x618c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6190, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6194, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6198, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x619c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x61a0, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x61a4, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x61a8, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x61ac, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CST12 },
	{ .reg = 0x6360, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_UV_GAMMA101 },
	{ .reg = 0x9860, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9864, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9868, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x986c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9870, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9874, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9878, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x987c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9880, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9884, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a60, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a64, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a68, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a6c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a70, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a74, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a78, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a7c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a80, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9a84, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_MNDS23 },
	{ .reg = 0x9c60, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c68, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0x9c6c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0x9c70, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c74, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c78, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c7c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c80, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c84, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c88, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c8c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c90, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9c94, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e60, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e68, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0x9e6c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0x9e70, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e74, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e78, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e7c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e80, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e84, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e88, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e8c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e90, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0x9e94, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa058, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa05c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa060, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa064, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa068, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa06c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa070, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa074, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa078, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa07c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa080, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa084, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa088, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa08c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa090, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa094, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa098, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa09c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0a0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0a4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0a8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0ac, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0b0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0b4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0b8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0bc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0c0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0c4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0c8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0cc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0d0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0d4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0d8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa0dc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa100, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa104, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa108, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa10c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa110, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa114, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa118, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa11c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa120, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa124, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa128, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa12c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa130, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa134, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa138, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa13c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa140, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa144, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa148, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa14c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa150, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa154, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa158, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa15c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa258, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa25c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa260, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa264, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa268, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa26c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa270, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa274, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa278, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa27c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa280, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa284, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa288, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa28c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa290, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa294, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa298, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2c0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2c4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2c8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2cc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2d0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2d4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2d8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2dc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa2e0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa460, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa468, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0xa46c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0xa470, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa474, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa478, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa47c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa480, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa484, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa488, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa48c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa490, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa494, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa660, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa668, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0xa66c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0xa670, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa674, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa678, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa67c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa680, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa684, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa688, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa68c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa690, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa694, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xa860, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa868, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa904, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xa908, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xaa60, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xab04, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xab08, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xac60, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac68, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0xac6c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0xac70, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac74, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac78, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac7c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac80, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac84, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac88, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac8c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac90, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xac94, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae60, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae68, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0xae6c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_CROP12 },
	{ .reg = 0xae70, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae74, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae78, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae7c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae80, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae84, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae88, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae8c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae90, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xae94, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_ROUND_CLAMP12 },
	{ .reg = 0xb060, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb064, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb068, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb06c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb070, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb074, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb078, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb07c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb080, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb084, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb088, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb08c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb090, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb094, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb098, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb09c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb0a0, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb0a4, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AEC_BE_STATS17 },
	{ .reg = 0xb258, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_BHIST_STATS16 },
	{ .reg = 0xb25c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_BHIST_STATS16 },
	{ .reg = 0xb260, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb264, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb268, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb26c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_BHIST_STATS16 },
	{ .reg = 0xb270, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb274, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb278, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb27c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb280, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb284, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb288, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb28c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb290, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb294, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb298, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb29c, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb2a0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb2a4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xb660, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb664, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb668, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb66c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb670, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb674, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb678, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb67c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb680, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb684, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb688, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb68c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb690, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb694, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb698, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb69c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb6a0, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb6a4, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_TINTLESS_BG_STATS17 },
	{ .reg = 0xb860, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb864, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb868, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb86c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb870, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb874, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb878, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb87c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb880, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb884, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb888, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb88c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb890, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb894, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb898, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb89c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb8a0, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xb8a4, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_AWB_BG_STATS17 },
	{ .reg = 0xbc58, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbc5c, .source = E006M_SOURCE_STEADY_DYNAMIC, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbc60, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc64, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbc68, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbc6c, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc70, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc74, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc78, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc7c, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc80, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc84, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc88, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc8c, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc90, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc94, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc98, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbc9c, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbca0, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbca4, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbca8, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcac, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcb0, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcb4, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcb8, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcbc, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcc0, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcc4, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcc8, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbccc, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcd0, .source = E006M_SOURCE_SHARED_STARTUP, .owner = E006M_OWNER_BFSTATS25 },
	{ .reg = 0xbcd4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbcd8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbcdc, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbce0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbce4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbce8, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbcec, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbcf0, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbcf4, .source = E006M_SOURCE_STEADY_SINGLETON, .owner = E006M_OWNER_NONE },
	{ .reg = 0xbe60, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_RS_STATS14 },
	{ .reg = 0xbe68, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_RS_STATS14 },
	{ .reg = 0xbe6c, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_RS_STATS14 },
	{ .reg = 0xbe70, .source = E006M_SOURCE_EXTRA_STARTUP, .owner = E006M_OWNER_RS_STATS14 },
};

static_assert(ARRAY_SIZE(e006m_rear_startup_regs) == 714);

typedef int (*e006m_scalar_fn)(void *ctx, u16 reg, u32 *value);

struct e006m_rear_extra_scalar_ops {
	e006m_scalar_fn steady_singleton;
	e006m_scalar_fn bc101;
	e006m_scalar_fn bayer_gtm101;
	e006m_scalar_fn bayer_ltm101;
	e006m_scalar_fn lcac111;
	e006m_scalar_fn cst12;
	e006m_scalar_fn uv_gamma101;
	e006m_scalar_fn mnds23;
	e006m_scalar_fn round_clamp12;
	e006m_scalar_fn crop12;
	e006m_scalar_fn aec_be_stats17;
	e006m_scalar_fn bhist_stats16;
	e006m_scalar_fn tintless_bg_stats17;
	e006m_scalar_fn awb_bg_stats17;
	e006m_scalar_fn rs_stats14;
	e006m_scalar_fn period_cfg;
};

struct e006m_rear_startup_bundle {
	struct e006j_rear_scalar_ops steady;
	struct e006m_rear_extra_scalar_ops extra;
};

static e006m_scalar_fn
e006m_shared_fn_for(const struct e006j_rear_scalar_ops *ops, u8 owner)
{
	if (!ops)
		return NULL;

	switch (owner) {
	case E006M_OWNER_PDPC:
		return ops->pdpc;
	case E006M_OWNER_WB:
		return ops->wb;
	case E006M_OWNER_BPC_ABF:
		return ops->bpc_abf;
	case E006M_OWNER_BFSTATS25:
		return ops->bfstats25;
	default:
		return NULL;
	}
}

static e006m_scalar_fn
e006m_extra_fn_for(const struct e006m_rear_extra_scalar_ops *ops, u8 owner)
{
	if (!ops)
		return NULL;

	switch (owner) {
	case E006M_OWNER_BC101:
		return ops->bc101;
	case E006M_OWNER_BAYER_GTM101:
		return ops->bayer_gtm101;
	case E006M_OWNER_BAYER_LTM101:
		return ops->bayer_ltm101;
	case E006M_OWNER_LCAC111:
		return ops->lcac111;
	case E006M_OWNER_CST12:
		return ops->cst12;
	case E006M_OWNER_UV_GAMMA101:
		return ops->uv_gamma101;
	case E006M_OWNER_MNDS23:
		return ops->mnds23;
	case E006M_OWNER_ROUND_CLAMP12:
		return ops->round_clamp12;
	case E006M_OWNER_CROP12:
		return ops->crop12;
	case E006M_OWNER_AEC_BE_STATS17:
		return ops->aec_be_stats17;
	case E006M_OWNER_BHIST_STATS16:
		return ops->bhist_stats16;
	case E006M_OWNER_TINTLESS_BG_STATS17:
		return ops->tintless_bg_stats17;
	case E006M_OWNER_AWB_BG_STATS17:
		return ops->awb_bg_stats17;
	case E006M_OWNER_RS_STATS14:
		return ops->rs_stats14;
	case E006M_OWNER_VFE680_PERIOD_CFG:
		return ops->period_cfg;
	default:
		return NULL;
	}
}

static int
e006m_rear_validate_startup_contract(const struct e006m_rear_startup_bundle *b)
{
	unsigned int i;
	unsigned int n_singleton = 0, n_dynamic = 0, n_shared = 0, n_extra = 0;
	bool saw_period = false;

	if (!b || !b->extra.steady_singleton)
		return -EINVAL;
	if (e006j_rear_validate_scalar_contract(&b->steady))
		return -EOPNOTSUPP;

	for (i = 0; i < ARRAY_SIZE(e006m_rear_startup_regs); i++) {
		const struct e006m_rear_startup_reg *r = &e006m_rear_startup_regs[i];

		if (i && e006m_rear_startup_regs[i - 1].reg >= r->reg)
			return -EINVAL;

		switch (r->source) {
		case E006M_SOURCE_STEADY_SINGLETON:
			if (r->owner != E006M_OWNER_NONE)
				return -EINVAL;
			n_singleton++;
			break;
		case E006M_SOURCE_STEADY_DYNAMIC:
			if (r->owner != E006M_OWNER_NONE)
				return -EINVAL;
			n_dynamic++;
			break;
		case E006M_SOURCE_SHARED_STARTUP:
			if (!e006m_shared_fn_for(&b->steady, r->owner))
				return -EOPNOTSUPP;
			n_shared++;
			break;
		case E006M_SOURCE_EXTRA_STARTUP:
			if (!e006m_extra_fn_for(&b->extra, r->owner))
				return -EOPNOTSUPP;
			if (r->owner == E006M_OWNER_VFE680_PERIOD_CFG)
				saw_period = true;
			n_extra++;
			break;
		default:
			return -EINVAL;
		}
	}

	if (n_singleton != 468 || n_dynamic != 25 ||
	    n_shared != 35 || n_extra != 186 || !saw_period)
		return -EINVAL;

	return 0;
}

static int
e006m_rear_fill_startup_scalar(const struct e006m_rear_startup_bundle *b,
				void *ctx, u16 reg, u32 *value)
{
	unsigned int i;
	e006m_scalar_fn fn;

	if (!b || !value)
		return -EINVAL;

	for (i = 0; i < ARRAY_SIZE(e006m_rear_startup_regs); i++) {
		const struct e006m_rear_startup_reg *r = &e006m_rear_startup_regs[i];

		if (r->reg != reg)
			continue;

		switch (r->source) {
		case E006M_SOURCE_STEADY_SINGLETON:
			return b->extra.steady_singleton(ctx, reg, value);
		case E006M_SOURCE_STEADY_DYNAMIC:
			return e006j_rear_fill_scalar(&b->steady, ctx, reg, value);
		case E006M_SOURCE_SHARED_STARTUP:
			fn = e006m_shared_fn_for(&b->steady, r->owner);
			break;
		case E006M_SOURCE_EXTRA_STARTUP:
			fn = e006m_extra_fn_for(&b->extra, r->owner);
			break;
		default:
			return -EINVAL;
		}
		if (!fn)
			return -EOPNOTSUPP;
		return fn(ctx, reg, value);
	}

	return -ENOENT;
}

struct e006m_rear_startup_binding_static_ops {
	int (*validate)(const struct e006m_rear_startup_bundle *b);
	int (*fill)(const struct e006m_rear_startup_bundle *b,
		    void *ctx, u16 reg, u32 *value);
};

/* Retention only. There is deliberately no runtime caller. */
static const struct e006m_rear_startup_binding_static_ops
e006m_rear_startup_binding_recipe __used = {
	.validate = e006m_rear_validate_startup_contract,
	.fill = e006m_rear_fill_startup_scalar,
};
