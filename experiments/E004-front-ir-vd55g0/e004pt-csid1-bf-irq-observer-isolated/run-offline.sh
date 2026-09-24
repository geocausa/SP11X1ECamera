#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E004pt has no hardware access; standalone 262144-domain-case observer.
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
tmp="$(mktemp -d /tmp/e004pt-bf-observer-XXXXXX)"
trap 'rm -rf -- "$tmp"' EXIT
gcc -std=c11 -Wall -Wextra -Werror -pedantic -O2 \
    "$D/test-e004pt-observer.c" -o "$tmp/e004pt-gcc"
"$tmp/e004pt-gcc"
clang -std=c11 -Wall -Wextra -Werror -pedantic -O1 \
    -fsanitize=address,undefined -fno-omit-frame-pointer \
    "$D/test-e004pt-observer.c" -o "$tmp/e004pt-clang-sanitize"
"$tmp/e004pt-clang-sanitize"
echo E004PT_OFFLINE_GCC_CLANG_ASAN_UBSAN_PASS
