#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
T=$(mktemp -d /tmp/sp11-e004kq-tests.XXXXXX)
trap 'rm -rf "$T"' EXIT
F=(-O3 -std=c11 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off)
for camera in front rear; do
 gcc "${F[@]}" "$camera-direct-publisher.c" -o "$T/$camera"
 if "$T/$camera" --source /dev/video0 1; then exit 1; fi
 gcc "${F[@]}" "test_$camera.c" -Wl,--wrap=fopen,--wrap=geteuid,--wrap=open,--wrap=fstat,--wrap=close,--wrap=mmap,--wrap=munmap,--wrap=poll,--wrap=write,--wrap=ioctl -o "$T/test"
 "$T/test"
done
