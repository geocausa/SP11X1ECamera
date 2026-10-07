/* SPDX-License-Identifier: GPL-2.0-only
 * Audit the local derived bootstrap with the actual kernel command helper.
 * Reports counts only. Never writes the input file or accesses hardware.
 */
#include "../native-front-nv12-commands.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv)
{
	u8 original[41088], working[41088];
	unsigned startup = 0, steady = 0, changed = 0;
	FILE *f;
	if (argc != 2 || !(f = fopen(argv[1], "rb")))
		return 1;
	size_t n = fread(original, 1, sizeof(original), f);
	int tail = fgetc(f);
	fclose(f);
	if (n != sizeof(original) || tail != EOF)
		return 1;
	memcpy(working, original, n);
	for (unsigned i = 0; i < 36; i++) {
		const u8 *d = original + 64 + i * 16;
		u32 type = native_nv12_le32(d), index = native_nv12_le32(d + 4);
		u32 offset = native_nv12_le32(d + 8), bytes = native_nv12_le32(d + 12);
		if (offset > n || bytes > n - offset)
			return 1;
		if (type == 1) {
			int rc = native_nv12_commands_transform(working + offset, bytes, index < 2);
			if (index > 3 || rc) {
				fprintf(stderr, "STARTUP_COMMAND_VALIDATION_FAILED index=%u rc=%d\n", index, rc);
				return 1;
			}
			startup |= 1U << index;
		} else if (type == 3) {
			int rc = native_nv12_commands_validate(working + offset, bytes, 0);
			if (index || rc) {
				fprintf(stderr, "STEADY_COMMAND_VALIDATION_FAILED rc=%d\n", rc);
				return 1;
			}
			steady++;
		}
	}
	for (size_t i = 0; i < n; i += 4)
		changed += memcmp(original + i, working + i, 4) != 0;
	if (startup != 15 || steady != 1 || changed != 12) {
		fprintf(stderr, "TRANSFORM_COUNT_FAILED startup_mask=%u steady=%u changed=%u\n", startup, steady, changed);
		return 1;
	}
	puts("{\"status\":\"PASS_LOCAL_BOOTSTRAP_NATIVE_NV12_TRANSFORM\","
	     "\"startup_packets\":4,\"steady_packets\":1,\"changed_words\":12,"
	     "\"original_file_modified\":false,\"hardware_access\":false}");
	return 0;
}
