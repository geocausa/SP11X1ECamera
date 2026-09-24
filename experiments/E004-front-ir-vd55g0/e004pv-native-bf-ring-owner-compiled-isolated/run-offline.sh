#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Compile exact shared native ring header as standalone C11 under GCC+Clang.
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d /tmp/e004pv-owner-ring-XXXXXX)"
trap 'rm -rf -- "$T"' EXIT
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O2 \
 "$D/test-bf-owner-ring.c" -o "$T/test-gcc"
"$T/test-gcc"
clang -std=c11 -Wall -Wextra -Werror -pedantic -O1 \
 -fsanitize=address,undefined -fno-omit-frame-pointer \
 "$D/test-bf-owner-ring.c" -o "$T/test-clang-asan-ubsan"
"$T/test-clang-asan-ubsan"
echo E004PV_EXACT_SAME_C11_HEADER_GCC_CLANG_ASAN_UBSAN_PASS
