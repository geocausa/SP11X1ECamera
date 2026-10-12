// SPDX-License-Identifier: GPL-2.0-only
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "sp11-csid680-ipp.h"
#include "csid-reference.h"

int main(void)
{
	struct sp11_csid680_ipp_input input = {0, 0, 10};
	struct sp11_csid680_ipp_plan out, snapshot;
	unsigned int good = 0, bad = 0;
	for (u32 vc = 0; vc < 32; vc++) for (u32 id = 0; id < 4; id++) {
		input.virtual_channel = vc; input.dt_id = id;
		assert(!sp11_csid680_ipp_prepare(&out, &input));
		assert(out.target == SP11_CSID680_IPP_TARGET);
		assert(out.count == SP11_CSID680_IPP_WRITES);
		struct public_csid_words ref = public_csid_ipp(vc, id);
		assert(!(out.writes[0].value & (1U << 31)));
		assert(out.writes[0].offset == public_ipp_offsets[0]);
		assert(out.writes[0].value == ref.cfg0_before_enable);
		assert(out.writes[1].offset == public_ipp_offsets[1]);
		assert(out.writes[1].value == 0);
		assert(out.writes[2].offset == public_ipp_offsets[2]);
		assert(out.writes[2].value == ref.cfg1);
		for (u32 i = 3; i < 7; i++) {
			assert(out.writes[i].offset == public_ipp_offsets[i]);
			assert(out.writes[i].value == ((i & 1) ? 1U : 0U));
		}
		/* No CTRL/IRQ/reset/apply registers, duplicate offsets or enable. */
		for (u32 i = 0; i < 7; i++) for (u32 j = i + 1; j < 7; j++)
			assert(out.writes[i].offset != out.writes[j].offset);
		good++;
	}
#define REJECT(call, code) do { \
	memset(&out, 0xa5, sizeof(out)); memcpy(&snapshot, &out, sizeof(out)); \
	assert((call) == (code)); assert(!memcmp(&out, &snapshot, sizeof(out))); bad++; \
} while (0)
	input = (struct sp11_csid680_ipp_input){0, 0, 10};
	REJECT(sp11_csid680_ipp_prepare(NULL, &input), -EINVAL);
	REJECT(sp11_csid680_ipp_prepare(&out, NULL), -EINVAL);
	for (u32 bits = 0; bits <= 20; bits++) {
		if (bits == 10) continue;
		input.input_bits = bits;
		REJECT(sp11_csid680_ipp_prepare(&out, &input), -EOPNOTSUPP);
	}
	input.input_bits = 10;
	const u32 vc_bad[] = {32, 33, 255, 0xffffffffU};
	for (u32 i = 0; i < 4; i++) {
		input.virtual_channel = vc_bad[i];
		REJECT(sp11_csid680_ipp_prepare(&out, &input), -ERANGE);
	}
	input.virtual_channel = 0;
	const u32 id_bad[] = {4, 5, 255, 0xffffffffU};
	for (u32 i = 0; i < 4; i++) {
		input.dt_id = id_bad[i];
		REJECT(sp11_csid680_ipp_prepare(&out, &input), -ERANGE);
	}
#undef REJECT
	union { struct sp11_csid680_ipp_plan plan; struct sp11_csid680_ipp_input input; } alias;
	memset(&alias, 0xa5, sizeof(alias));
	alias.input = (struct sp11_csid680_ipp_input){0, 0, 10};
	u8 old[sizeof(alias)]; memcpy(old, &alias, sizeof(alias));
	assert(sp11_csid680_ipp_prepare(&alias.plan, &alias.input) == -EINVAL);
	assert(!memcmp(old, &alias, sizeof(alias))); bad++;
	printf("PASS CSID680 IPP routes=%u atomic_rejections=%u writes=7 path_enabled=0 separate_target=CSID\n",
	       good, bad);
	return 0;
}
