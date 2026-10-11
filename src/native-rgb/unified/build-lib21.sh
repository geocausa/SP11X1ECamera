#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
# Build libcamera tree 21 (both SP11 pipelines) and the sp11-webcam bridge.
set -e
U=$(cd "$(dirname "$0")" && pwd)
P=/home/geoca/Documents/SP11-PROJECT
python3 $U/build-lib21.py --build
L=$P/06-camera/reference/libcamera-unified-21; B=$P/02-kernel/libcamera-unified-21
g++ -std=c++17 -Wall -Wextra -Werror -O2 -pthread -I$L/include -I$B/include $U/sp11-webcam.cpp -L$B/src/libcamera -L$B/src/libcamera/base -lcamera -lcamera-base -o $B/sp11-webcam
echo LIB21_WEBCAM_PASS
