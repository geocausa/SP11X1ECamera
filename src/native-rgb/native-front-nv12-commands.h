/* SPDX-License-Identifier: GPL-2.0-only
 * Native front FULL round/clamp conversion for a bounded NV12 diagnostic.
 * CDM command encoding: Qualcomm camera-driver cam_cdm_util.{c,h}.
 * RoundClamp12 semantics: retained, independently reconstructed E006p.
 * No captured command, tuning payload, device address or pixel is embedded.
 */
#ifndef NATIVE_FRONT_NV12_COMMANDS_H
#define NATIVE_FRONT_NV12_COMMANDS_H
#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
#include <linux/string.h>
#else
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
#include <string.h>
typedef uint8_t u8;
typedef uint32_t u32;
#endif

static inline u32 native_nv12_le32(const u8 *p)
{
	return (u32)p[0] | ((u32)p[1] << 8) | ((u32)p[2] << 16) | ((u32)p[3] << 24);
}

static inline void native_nv12_put32(u8 *p, u32 v)
{
	p[0] = v;
	p[1] = v >> 8;
	p[2] = v >> 16;
	p[3] = v >> 24;
}

static inline int native_nv12_round_index(u32 reg, unsigned *chroma)
{
	u32 base;

	if (reg >= 0x9c60 && reg <= 0x9c94) {
		base = 0x9c60;
		*chroma = 0;
	} else if (reg >= 0x9e60 && reg <= 0x9e94) {
		base = 0x9e60;
		*chroma = 1;
	} else {
		return -1;
	}
	/* Crop12 at +8/+12 is independent and must stay untouched. */
	if (reg == base)
		return 0;
	if (reg < base + 0x10 || ((reg - base) & 3))
		return -1;
	return 1 + (reg - base - 0x10) / 4;
}

static inline u32 native_nv12_round_word(unsigned chroma, unsigned index, unsigned bits)
{
	u32 maximum = (1U << bits) - 1;
	u32 round = 10 - bits;

	if (!index)
		return (chroma ? 0x3c01 : 0x0c01) | 0x200;
	if (chroma) {
		if (index == 2 || index == 4)
			return 7 | (round << 3);
		if (index == 7 || index == 8)
			return maximum;
	} else {
		if (index == 2)
			return 6 | (round << 3);
		if (index == 7)
			return maximum;
	}
	return 0;
}

/* Validate the complete command stream before changing one byte. Reject bus
 * programming, unknown commands, malformed spans and late bad FULL values.
 * Packet 0/1 must each own all eleven luma/chroma fields exactly once.
 * Packet 2/3 and steady requests must not write any FULL round/clamp field.
 */
static inline int native_nv12_commands_validate(const u8 *data, size_t bytes,
					       int full_fields)
{
	u32 seen[2] = { 0, 0 };
	size_t pos = 0;

	if (!data || !bytes || (bytes & 3) || (full_fields != 0 && full_fields != 1))
		return -EINVAL;
	while (pos < bytes) {
		u32 header, count, op;

		if (bytes - pos < 4)
			return -EINVAL;
		header = native_nv12_le32(data + pos);
		count = header & 0xffff;
		op = header >> 24;
		if (op == 1) { /* DMI, no indirect command admission. */
			/* Preserve target-specific DMI header bits. The existing pinned
			 * corpus validator/materializer owns their payload/address binding.
			 * This conversion changes no DMI header, selector or address. */
			if (bytes - pos < 12)
				return -EINVAL;
			pos += 12;
		} else if (op == 3) { /* contiguous register command */
			u32 reg;
			size_t used;

			if ((header & 0x00ff0000) || bytes - pos < 8 || !count ||
			    count > (bytes - pos - 8) / 4)
				return -EINVAL;
			reg = native_nv12_le32(data + pos + 4);
			used = 8 + (size_t)count * 4;
			if ((reg & 0xff000003) || reg > 0x00ffffff - (count - 1) * 4)
				return -EINVAL;
			for (u32 i = 0; i < count; i++) {
				u32 r = reg + i * 4;
				unsigned chroma = 0;
				int index;

				/* BUS common and all 32 WM register windows. */
				if (r >= 0xc00 && r < 0x2e00)
					return -EPERM;
				index = native_nv12_round_index(r, &chroma);
				if (index < 0)
					continue;
				if (!full_fields || (seen[chroma] & (1U << index)) ||
				    native_nv12_le32(data + pos + 8 + i * 4) !=
						native_nv12_round_word(chroma, index, 10))
					return -EINVAL;
				seen[chroma] |= 1U << index;
			}
			pos += used;
		} else {
			return -EOPNOTSUPP;
		}
	}
	return seen[0] == (full_fields ? 0x7ffU : 0U) &&
	       seen[1] == (full_fields ? 0x7ffU : 0U) ? 0 : -EINVAL;
}

/* Owned, unsubmitted memory only. Complete validation guarantees atomicity. */
static inline int native_nv12_commands_transform(u8 *data, size_t bytes, int full_fields)
{
	size_t pos = 0;
	int ret = native_nv12_commands_validate(data, bytes, full_fields);

	if (ret)
		return ret;
	while (pos < bytes) {
		u32 header = native_nv12_le32(data + pos);
		u32 count = header & 0xffff;

		if (header >> 24 == 1) {
			pos += 12;
		} else {
			u32 reg = native_nv12_le32(data + pos + 4);

			for (u32 i = 0; i < count; i++) {
				unsigned chroma = 0;
				int index = native_nv12_round_index(reg + i * 4, &chroma);

				if (index >= 0)
					native_nv12_put32(data + pos + 8 + i * 4,
						native_nv12_round_word(chroma, index, 8));
			}
			pos += 8 + (size_t)count * 4;
		}
	}
	return 0;
}
#endif
