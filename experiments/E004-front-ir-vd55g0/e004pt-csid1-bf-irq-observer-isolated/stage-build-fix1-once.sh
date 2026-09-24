#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# New compile attempt ID; does not touch or replay consumed E004pt build.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e004pt-csid1-bf-irq-observer-isolated"
FIRST=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pt-csid1-bf-irq-observer-build
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pt-csid1-bf-irq-observer-build-fix1
test -s "$FIRST/qcom-camss.ko"
test ! -e "$B" || { echo E004PT_FIX1_BUILD_ALREADY_CONSUMED >&2; exit 3; }
tmp="$(mktemp /tmp/e004pt-fix1-builder-XXXXXXXX.sh)"
chmod 700 "$tmp"
trap 'rm -f -- "$tmp"' EXIT
python3 - "$D/stage-build-once.sh" "$tmp" <<'PY'
from pathlib import Path
import sys
src=Path(sys.argv[1]).read_text()
old='B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pt-csid1-bf-irq-observer-build\n'
new='B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pt-csid1-bf-irq-observer-build-fix1\n'
assert src.count(old)==1
src=src.replace(old,new,1)
needle='inject("camss-csid-680.c",\n       "/*\\n * csid_isr - CSID module interrupt service routine\\n",'
assert src.count(needle)==1
inject=('inject("camss-csid.h",\n'
        '       "u32 csid680_x1e_front_video_seq(struct csid_device *csid);\\n",\n'
        '       "u32 csid680_x1e_front_video_seq(struct csid_device *csid);\\n"\n'
        '       "u64 csid680_e004pt_bf_status_observations(struct csid_device *csid);\\n")\n')
src=src.replace(needle,inject+needle,1)
Path(sys.argv[2]).write_text(src)
print("E004PT_FIX1_NEW_UNIQUE_BUILD_WITH_BF_OBSERVER_PROTOTYPE")
PY
bash "$tmp"
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pt-csid1-bf-irq-observer-build-fix1
if grep -E '(warning:|error:)' "$B/E004PT-CAMSS-BUILD.log"; then
 echo E004PT_FIX1_HAS_COMPILER_WARNINGS_OR_ERRORS >&2
 exit 4
fi
echo E004PT_FIX1_W1_ARM64_CAMSS_ZERO_WARNINGS
