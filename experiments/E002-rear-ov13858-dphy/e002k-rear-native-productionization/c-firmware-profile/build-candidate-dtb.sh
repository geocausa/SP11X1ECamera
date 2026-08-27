#!/bin/sh
set -eu
BASE=$1
OUT=$2
NODE=/soc@0/cci@ac15000/i2c-bus@1/rear-probe@10
cp "$BASE" "$OUT"
for p in microsoft,e002e-no-stream microsoft,e002f-validate-mode0 microsoft,e002g-native-mode0 microsoft,e002h-allow-stream; do
    fdtput -d "$OUT" "$NODE" "$p"
done
