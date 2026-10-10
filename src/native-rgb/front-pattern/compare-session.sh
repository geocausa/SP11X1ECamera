#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Analyse one back-to-back Linux/Windows front session (private data stays on SP11).
# Usage: compare-session.sh <n> <play-log T0> <loops.txt>   (run from 06-camera)
set -euo pipefail
n=$1; F=SP11X1ECamera-driver/src/native-rgb/front-pattern; P=private
ROI=${FRONT_ROI:-7,8:6,7,8,9,10}
if [ ! -f $P/front-ae$n-windows/records.csv ]; then
  mkdir -p /mnt/win; mountpoint -q /mnt/win || mount -t ntfs3 -o ro /dev/nvme0n1p3 /mnt/win
  S=/mnt/win/Users/Geoca/Documents/SP11-Camera-FrontF$n
  mkdir -p -m 700 $P/front-ae$n-windows
  cp $S/records.csv $S/run.log $S/RESULT.json $P/front-ae$n-windows/
  umount /mnt/win
fi
python3 $F/rebuild-play-log.py $P/play-log-f13.csv.gz "$2" "$3" $P/play-log-f$n.csv.gz
chmod 600 $P/play-log-f$n.csv.gz
FRONT_ROI=$ROI python3 $F/analyze-front-pattern.py /var/lib/sp11-camera-front-ae-$n $P/play-log-f$n.csv.gz 1 > $P/front-ae$n-analysis-roi.json
FRONT_ROI=$ROI python3 $F/analyze-front-windows.py $P/front-ae$n-windows/records.csv $P/play-log-f$n.csv.gz 1 > $P/front-ae${n}w-analysis-roi.json
python3 $F/compare-front.py $P/front-ae$n-analysis-roi.json $P/front-ae${n}w-analysis-roi.json 1 0 > $P/front-ae$n-cmp-roi.json
python3 - $P/front-ae$n-cmp-roi.json <<'E'
import json, sys
d = json.load(open(sys.argv[1]))
print({k: v for k, v in d.items() if not isinstance(v, list)})
for v in d.values():
    if isinstance(v, list):
        for r in v:
            print(r['pattern'], [round(x) for x in r['linux']], [round(x) for x in r['windows']], r['dY'], r['dC'])
E
python3 $F/scene-check.py /var/lib/sp11-camera-front-ae-$n 1 $P/front-ae$n-windows/records.csv 0 -
