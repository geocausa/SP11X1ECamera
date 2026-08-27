#!/bin/bash
set -euo pipefail
if [ "$#" -ne 2 ]; then echo "usage: $0 BASE_DTB OUT_DTB" >&2; exit 2; fi
BASE=$1; OUT=$2
NODE=/soc@0/cci@ac15000/i2c-bus@1/rear-probe@10
cp "$BASE" "$OUT"
DOVDD=$(fdtget -tx "$BASE" "$NODE" ldo6m-supply)
DVDD=$(fdtget -tx "$BASE" "$NODE" ldo1m-supply)
AVDD=$(fdtget -tx "$BASE" "$NODE" ldo5m-supply)
for p in ldo6m-supply ldo1m-supply ldo5m-supply ldo16b-supply; do
    fdtput -d "$OUT" "$NODE" "$p"
done
fdtput -tx "$OUT" "$NODE" dovdd-supply "0x$DOVDD"
fdtput -tx "$OUT" "$NODE" dvdd-supply "0x$DVDD"
fdtput -tx "$OUT" "$NODE" avdd-supply "0x$AVDD"
# Mechanical assertions.
[ "$(fdtget -tx "$OUT" "$NODE" dovdd-supply)" = "$DOVDD" ]
[ "$(fdtget -tx "$OUT" "$NODE" dvdd-supply)" = "$DVDD" ]
[ "$(fdtget -tx "$OUT" "$NODE" avdd-supply)" = "$AVDD" ]
for p in ldo6m-supply ldo1m-supply ldo5m-supply ldo16b-supply; do
    if fdtget "$OUT" "$NODE" "$p" >/dev/null 2>&1; then
        echo "old property still present: $p" >&2; exit 1
    fi
done
