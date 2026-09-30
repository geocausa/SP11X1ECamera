/* Offline host contract tests and exact E007a register-provider bridge. */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <assert.h>
typedef int16_t s16;
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define static_assert _Static_assert
#define __used __attribute__((used))
#define E007Y_STARTUP_PACKETS 4
#define E006Z_EPOCH_STARTUP 1
#include "../e007a-rear-bpcabf411-calculated-provider/camss-e007a-bpcabf411.inc"

/* E008o shape adapter only; full DMI validation is not exercised by this test. */
struct scalar_state { u64 request_id; u8 epoch_kind; u8 startup_phase; };
struct e007d_rear_register_state {
	struct scalar_state scalar;
	struct e007a_bpcabf411_calc_state bpcabf;
	u32 unrelated_marker;
};
struct e008o_rear_packet_semantics {
	struct e007d_rear_register_state regs;
	u64 request_id;
	bool ready;
};
struct e008o_rear_semantic_set {
	struct e008o_rear_packet_semantics packet[E007Y_STARTUP_PACKETS];
	bool sealed;
};
#include "camss-e011ae-rear-startup-bpc-bind.inc"

static void init_set(struct e008o_rear_semantic_set *set)
{
	unsigned int p;
	memset(set, 0, sizeof(*set));
	set->sealed = true;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		set->packet[p].request_id = 4 + p;
		set->packet[p].regs.scalar.request_id = 4 + p;
		set->packet[p].regs.scalar.epoch_kind = E006Z_EPOCH_STARTUP;
		set->packet[p].regs.scalar.startup_phase = p;
		set->packet[p].regs.unrelated_marker = 0x100 + p;
		set->packet[p].ready = true;
	}
}

int main(int argc, char **argv)
{
	struct e011ae_rear_startup_bpc_source source = {0};
	struct e008o_rear_semantic_set set, prior;
	unsigned int p;
	if (argc == 2 && strcmp(argv[1], "bind-source") == 0) {
		if (fread(source.common, sizeof(source.common), 1, stdin) != 1) return 5;
		for (p = 0; p < 3; p++) source.source_request_id[p] = p;
		init_set(&set); /* Explicit host materializer fixture identities 4/5/6/7. */
		if (e011ae_rear_bind_startup_bpc(&set, &source)) return 6;
		if (set.sealed) return 7;
		for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
			u32 words[ARRAY_SIZE(e007a_bpcabf411_closed_regs)];
			unsigned int i;
			if (set.packet[p].ready || set.packet[p].request_id != 4 + p ||
			    set.packet[p].regs.scalar.request_id != 4 + p ||
			    set.packet[p].regs.unrelated_marker != 0x100 + p) return 8;
			for (i = 0; i < ARRAY_SIZE(words); i++)
				if (e007a_bpcabf411_lookup(&set.packet[p].regs.bpcabf,
						e007a_bpcabf411_closed_regs[i], &words[i])) return 9;
			if (fwrite(words, sizeof(words), 1, stdout) != 1) return 10;
		}
		return 0;
	}
	if (argc == 2 && strcmp(argv[1], "pack") == 0) {
		struct e007a_bpcabf411_calc_state state;
		_Static_assert(sizeof(state) == 34, "semantic wire shape changed");
		while (fread(&state, sizeof(state), 1, stdin) == 1) {
			u32 words[ARRAY_SIZE(e007a_bpcabf411_closed_regs)];
			for (p = 0; p < ARRAY_SIZE(words); p++)
				if (e007a_bpcabf411_lookup(&state, e007a_bpcabf411_closed_regs[p],
							 &words[p])) return 2;
			if (fwrite(words, sizeof(words), 1, stdout) != 1) return 3;
		}
		return ferror(stdin) ? 4 : 0;
	}
	for (p = 0; p < 3; p++) {
		source.source_request_id[p] = p;
		source.common[p].signed10[0] = (s16)p - 2;
		source.common[p].unsigned9[1] = 8 + p;
		source.common[p].nibble_group[0][0] = p;
	}
	init_set(&set);
	assert(e011ae_rear_bind_startup_bpc(&set, &source) == 0);
	assert(!set.sealed);
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		assert(!set.packet[p].ready);
		assert(set.packet[p].request_id == 4 + p);
		assert(set.packet[p].regs.scalar.request_id == 4 + p);
		assert(set.packet[p].regs.unrelated_marker == 0x100 + p);
		assert(memcmp(&set.packet[p].regs.bpcabf,
			      &source.common[p < 3 ? p : 2],
			      sizeof(source.common[0])) == 0);
	}
	/* Value copies are independent, including the held request2/request3 pair. */
	set.packet[2].regs.bpcabf.signed10[0] = 99;
	assert(set.packet[3].regs.bpcabf.signed10[0] == source.common[2].signed10[0]);
	assert(e011ae_rear_runtime_authorization() == -EOPNOTSUPP);
	assert(e011ae_rear_bind_startup_bpc(NULL, &source) == -EINVAL);
	assert(e011ae_rear_bind_startup_bpc(&set, NULL) == -EINVAL);

	for (p = 0; p < 4; p++) {
		init_set(&set);
		set.packet[p].regs.scalar.request_id++;
		prior = set;
		assert(e011ae_rear_bind_startup_bpc(&set, &source) == -EPROTO);
		assert(memcmp(&set, &prior, sizeof(set)) == 0);
		init_set(&set);
		set.packet[p].regs.scalar.startup_phase = 4;
		prior = set;
		assert(e011ae_rear_bind_startup_bpc(&set, &source) == -EPROTO);
		assert(memcmp(&set, &prior, sizeof(set)) == 0);
		init_set(&set);
		set.packet[p].request_id = 3;
		prior = set;
		assert(e011ae_rear_bind_startup_bpc(&set, &source) == -EINVAL);
		assert(memcmp(&set, &prior, sizeof(set)) == 0);
	}
	for (p = 0; p < 3; p++) {
		struct e011ae_rear_startup_bpc_source invalid = source;
		init_set(&set); prior = set;
		invalid.source_request_id[p] = 9;
		assert(e011ae_rear_bind_startup_bpc(&set, &invalid) == -EPROTO);
		assert(memcmp(&set, &prior, sizeof(set)) == 0);
		invalid = source;
		invalid.common[p].signed10[0] = -513;
		assert(e011ae_rear_bind_startup_bpc(&set, &invalid) == -ERANGE);
		assert(memcmp(&set, &prior, sizeof(set)) == 0);
	}
	puts("E011AE_BPC_BINDER_HOST_PASS packets=4 schedule=0,1,2,2 rejects=20");
	return 0;
}
