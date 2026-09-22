#!/usr/bin/env bash
set -Eeuo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
[[ $# == 1 && ! -e "$1" ]] || { echo 'usage: build.sh NEW_OUTPUT_DIRECTORY' >&2; exit 2; }
mkdir -m 0755 "$1"
OUT=$(cd "$1" && pwd)
F=(-O3 -std=c11 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off)
for camera in front rear; do
 gcc "${F[@]}" "$HERE/$camera-direct-publisher.c" -o "$OUT/$camera-direct-publisher"
done
(cd "$OUT" && sha256sum front-direct-publisher rear-direct-publisher > BINARIES.sha256)
echo RGB_DEFAULT_DENY_BUILD=PASS LIVE_CAPTURE=DISABLED
