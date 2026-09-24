#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Offline only; exact SAME header compiled in isolated ARM64 CAMSS and C11.
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d /tmp/e004pz-front-scope-XXXXXX)"
trap 'rm -rf -- "$T"' EXIT
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O2 \
 "$D/test-front-owner-observer.c" -o "$T/test-gcc"
"$T/test-gcc"
clang -std=c11 -Wall -Wextra -Werror -pedantic -O1 \
 -fsanitize=address,undefined -fno-omit-frame-pointer \
 "$D/test-front-owner-observer.c" -o "$T/test-clang-asan-ubsan"
"$T/test-clang-asan-ubsan"
echo E004PZ_EXACT_SHARED_HEADER_GCC_CLANG_ASAN_UBSAN_PASS
