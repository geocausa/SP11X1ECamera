#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Build the daily rear camera stack (identity 64):
#  * kernel: run-63 measured tone/colour module + unlimited clean sessions per boot
#    (any unclean session still poisons the gate until reboot);
#  * libcamera lib20: lib19 + private statistics recording optional (off unless
#    SP11_REAR_STATISTICS_DIR is set), so sessions can repeat in one boot.
set -Eeuo pipefail
P=/home/geoca/Documents/SP11-PROJECT
K63=$P/02-kernel/native-rgb-rear-tone-63
K=$P/02-kernel/native-rgb-rear-daily-64
KSOURCE=$P/02-kernel/e003i-front-production-src
KOUTPUT=$P/02-kernel/build-runtime-v4-headers-20260826
L19=$P/06-camera/reference/libcamera-rear-pattern61-19
L=$P/06-camera/reference/libcamera-rear-daily-20
B=$P/02-kernel/libcamera-rear-daily-20
HERE=$(cd "$(dirname "$0")" && pwd)
rm -rf "$K"; mkdir -p "$K"
for n in camss imx681 ov13858; do
  mkdir "$K/$n"
  find "$K63/$n" -maxdepth 1 -type f \( -name '*.c' -o -name '*.h' -o -name '*.inc' -o -name Makefile -o -name Kconfig \) -exec cp -p {} "$K/$n/" \;
done
sed -i 's/^#define NATIVE_REAR_SESSION_LIMIT 3U$/#define NATIVE_REAR_SESSION_LIMIT 1000000U/' "$K/camss/native-rear-session.h"
grep -q 'NATIVE_REAR_SESSION_LIMIT 1000000U' "$K/camss/native-rear-session.h"
sed -i 's/identity=63tone/identity=64daily/' "$K/camss/native-rear-generation-hook.inc"
make -C "$KSOURCE" O="$KOUTPUT" M="$K/camss" CONFIG_VIDEO_QCOM_CAMSS=m W=1 KCFLAGS=-Werror -j8 modules > "$K/camss-compile.log" 2>&1
modinfo -F vermagic "$K/camss/qcom-camss.ko"
rm -rf "$L" "$B"
cp -a "$L19" "$L"
F=$L/src/libcamera/pipeline/camss-x1e-rear/camss-x1e-rear.cpp
python3 - "$F" <<'EOF'
import sys
from pathlib import Path
p=Path(sys.argv[1]);t=p.read_text()
a=' const char *value=std::getenv("SP11_REAR_STATISTICS_DIR");\n if(!value)return -EINVAL;\n'
b=' const char *value=std::getenv("SP11_REAR_STATISTICS_DIR");\n if(!value){privateDirectory_=-1;privateDisabled_=true;return 0;}\n privateDisabled_=false;\n'
assert t.count(a)==1;t=t.replace(a,b)
a=' if(!selected)return 0;\n if(privateDirectory_<0||privateSaved_>=24)return -EINVAL;\n'
b=' if(!selected||privateDisabled_)return 0;\n if(privateDirectory_<0||privateSaved_>=24)return -EINVAL;\n'
assert t.count(a)==1;t=t.replace(a,b)
a=' int privateDirectory_=-1;\n'
assert t.count(a)==1
t=t.replace(a,' bool privateDisabled_=true;\n int privateDirectory_=-1;\n')
p.write_text(t)
EOF
meson setup "$B" "$L" -Ddebug=false -Dpipelines=camss-x1e-rear -Dipas=camss-x1e-rear -Dcam=enabled -Dtest=false -Ddocumentation=disabled -Dgstreamer=disabled -Dqcam=disabled -Dv4l2=disabled -Dpycamera=disabled -Dlibunwind=disabled -Dtracing=disabled -Dlc-compliance=disabled -Dwerror=true > "$B.setup.log" 2>&1
meson compile -C "$B" -j 8 > "$B.compile.log" 2>&1
g++ -std=c++17 -Wall -Wextra -Werror -O2 -pthread -I"$L/include" -I"$B/include" "$HERE/../rear-pattern61/capture-pattern61.cpp" -L"$B/src/libcamera" -L"$B/src/libcamera/base" -lcamera -lcamera-base -o "$B/capture-pattern"
echo BUILD_DAILY64_PASS
