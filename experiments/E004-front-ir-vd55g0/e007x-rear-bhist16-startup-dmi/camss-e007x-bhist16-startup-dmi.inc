/* SPDX-License-Identifier: MIT */
/*
 * E007x startup-only BHistStats16 DMI priming provider.
 *
 * Surface IFEBHistStats16Titan680::CreateCmdList zeroes a 0x1050-byte
 * caller-owned region, then emits:
 *   0xb208 selector 1: first  0x1000 bytes
 *   0xb208 selector 2: next   0x0050 bytes
 *
 * These writes occur only in startup packet 0 for the accepted rear graph.
 * No captured payload bytes are embedded.
 */

#define E007X_BHIST_DMI_REG 0xb208
#define E007X_BHIST_SEL1_BYTES 0x1000
#define E007X_BHIST_SEL2_BYTES 0x0050

static int
e007x_bhist16_startup_dmi(u8 packet, u16 dmi_reg, u8 selector,
			  u8 *dst, size_t bytes)
{
	size_t expected;

	if (!dst)
		return -EINVAL;
	if (packet != 0 || dmi_reg != E007X_BHIST_DMI_REG)
		return -ENOENT;

	if (selector == 1)
		expected = E007X_BHIST_SEL1_BYTES;
	else if (selector == 2)
		expected = E007X_BHIST_SEL2_BYTES;
	else
		return -ENOENT;

	if (bytes != expected)
		return -EINVAL;

	memset(dst, 0, bytes);
	return 0;
}

struct e007x_bhist16_startup_dmi_ops {
	int (*fill)(u8 packet, u16 dmi_reg, u8 selector,
		    u8 *dst, size_t bytes);
};

static const struct e007x_bhist16_startup_dmi_ops
e007x_bhist16_startup_dmi_recipe __used = {
	.fill = e007x_bhist16_startup_dmi,
};
