#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Daily 65 = daily 64 + statistics transport copies only the AEC grid the IPA
# decodes (32x32 regions x 80 bytes of plane 0) from uncached DMA memory; all
# other statistics planes are zero-filled. Removes ~21 ms of uncached reads
# per frame that made the capture loop miss every second sensor frame.
set -Eeuo pipefail
P=/home/geoca/Documents/SP11-PROJECT
K64=$P/02-kernel/native-rgb-rear-daily-64
K=$P/02-kernel/native-rgb-rear-daily-65
KSOURCE=$P/02-kernel/e003i-front-production-src
KOUTPUT=$P/02-kernel/build-runtime-v4-headers-20260826
rm -rf "$K"; mkdir -p "$K/camss"
find "$K64/camss" -maxdepth 1 -type f \( -name '*.c' -o -name '*.h' -o -name '*.inc' -o -name Makefile -o -name Kconfig \) -exec cp -p {} "$K/camss/" \;
python3 - "$K/camss/native-rear-stats.h" <<'EOF'
import sys
from pathlib import Path
p=Path(sys.argv[1]);t=p.read_text()
a="  memcpy(out+offset,planes[i],lengths[i]);\n"
b=("#ifdef __KERNEL__\n"
   "  /* Only plane 0's normal AEC grid is decoded downstream: read just that\n"
   "   * prefix from uncached DMA memory and zero-fill the rest (fast, cached). */\n"
   "  if(i==0){\n"
   "   memcpy(out+offset,planes[0],NATIVE_REAR_STATS_AEC_USED_BYTES);\n"
   "   memset(out+offset+NATIVE_REAR_STATS_AEC_USED_BYTES,0,lengths[0]-NATIVE_REAR_STATS_AEC_USED_BYTES);\n"
   "  }else{\n"
   "   memset(out+offset,0,lengths[i]);\n"
   "  }\n"
   "#else\n"
   "  memcpy(out+offset,planes[i],lengths[i]);\n"
   "#endif\n")
assert t.count(a)==1;t=t.replace(a,b)
a="#define NATIVE_REAR_STATS_BYTES (NATIVE_REAR_STATS_HEADER_BYTES+NATIVE_REAR_STATS_PAYLOAD_BYTES)\n"
assert t.count(a)==1
t=t.replace(a,a+"#define NATIVE_REAR_STATS_AEC_USED_BYTES (32U*32U*80U)\n")
p.write_text(t)
EOF
sed -i 's/identity=64daily/identity=65daily/' "$K/camss/native-rear-generation-hook.inc"
make -C "$KSOURCE" O="$KOUTPUT" M="$K/camss" CONFIG_VIDEO_QCOM_CAMSS=m W=1 KCFLAGS=-Werror -j8 modules > "$K/camss-compile.log" 2>&1
modinfo -F vermagic "$K/camss/qcom-camss.ko"
echo BUILD_DAILY65_PASS
