/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdio.h>
#include <stdlib.h>
#include "native-front-owner.h"
static unsigned int checks;
#define CHECK(x) do { checks++; if (!(x)) { fprintf(stderr, "failed line%d\n", __LINE__); exit(1); } } while (0)
int main(void)
{
	struct native_owner_history h;
	native_owner_u32 expected[NATIVE_OWNER_WMS], observed[NATIVE_OWNER_WMS];
	unsigned int group, i, frame;
	CHECK(native_owner_reset(&h, 0) == -EINVAL);
	CHECK(native_owner_reset(&h, 1234) == 0);
	for (frame = 1; frame <= 96; frame++) {
		for (i = 0; i < NATIVE_OWNER_WMS; i++)
			expected[i] = 0x10000000u + frame * 0x10000u + i * 0x100u;
		for (group = 0; group < NATIVE_OWNER_GROUPS; group++) {
			memcpy(observed, expected, sizeof(observed));
			CHECK(native_owner_publish(&h, group, frame,
			      native_owner_group_masks[group], observed) == 0);
			CHECK(native_owner_check(&h, 1234, group, frame, expected) == 0);
			/* Requeued same userspace object must match its current IOVA. */
			for (i = 0; i < NATIVE_OWNER_WMS; i++) {
				if (!(native_owner_group_masks[group] & (1u << i)))
					continue;
				expected[i] ^= 0x1000;
				CHECK(native_owner_check(&h, 1234, group, frame, expected) == -EPROTO);
				expected[i] ^= 0x1000;
			}
			CHECK(native_owner_check(&h, 1235, group, frame, expected) == -ESTALE);
			CHECK(native_owner_check(&h, 1234, group, frame + 1, expected) == -ESTALE);
			if (frame > NATIVE_OWNER_HISTORY)
				CHECK(native_owner_check(&h, 1234, group,
				      frame - NATIVE_OWNER_HISTORY, expected) == -ESTALE);
		}
	}
	CHECK(native_owner_publish(&h, 0, 96, 0xf, observed) == -EPROTO);
	CHECK(native_owner_check(&h, 1234, 0, 96, expected) == -EPROTO);
	CHECK(native_owner_reset(&h, 1235) == 0);
	CHECK(native_owner_check(&h, 1234, 0, 96, expected) == -ESTALE);
	CHECK(native_owner_publish(&h, 0, 2, 0xf, observed) == -EPROTO);
	CHECK(native_owner_reset(&h, 1236) == 0);
	CHECK(native_owner_publish(&h, 0, 1, 1, observed) == -EPROTO);
	CHECK(native_owner_reset(&h, 1237) == 0);
	CHECK(native_owner_publish(&h, 0, 1, 0xf, observed) == 0);
	h.event[0][1].mask = 1;
	CHECK(native_owner_check(&h, 1237, 0, 1, expected) == -EPROTO);
	CHECK(native_owner_reset(&h, 1238) == 0);
	CHECK(native_owner_publish(&h, 0, 1, 0xf, observed) == 0);
	expected[0] = 0;
	CHECK(native_owner_check(&h, 1238, 0, 1, expected) == -EPROTO);
	h.last[0] = UINT32_MAX;
	CHECK(native_owner_publish(&h, 0, 0, 0xf, observed) == -EPROTO);
	CHECK(native_owner_check(&h, 1238, 5, 1, expected) == -EINVAL);
	CHECK(native_owner_publish(&h, 5, 1, 0xf, observed) == -EINVAL);
	printf("PASS_NATIVE_FRONT_OWNER %u checks; 96 generations/group; no hardware\n", checks);
	return 0;
}
