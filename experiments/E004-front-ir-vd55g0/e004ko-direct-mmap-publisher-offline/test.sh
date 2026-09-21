#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
T=$(mktemp -d /tmp/sp11-e004ko-tests.XXXXXX)
trap 'rm -rf "$T"' EXIT
F=(-O3 -std=c11 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off)
gcc "${F[@]}" rear-direct-publisher.c -o "$T/publisher"
# Golden refusal is tested without root; no device is opened.
if "$T/publisher" --source /dev/video0 1; then exit 1; fi
gcc "${F[@]}" test_fake_devices.c -Wl,--wrap=fopen,--wrap=geteuid,--wrap=open,--wrap=fstat,--wrap=close,--wrap=mmap,--wrap=munmap,--wrap=poll,--wrap=write,--wrap=ioctl -o "$T/test"
"$T/test"
