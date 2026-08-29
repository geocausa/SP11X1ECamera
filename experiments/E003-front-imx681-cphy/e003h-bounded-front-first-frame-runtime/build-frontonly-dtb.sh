#!/bin/sh
set -eu
BASE=${1:?usage: build-frontonly-dtb.sh BASE.dtb OUT.dtb}
OUT=${2:?usage: build-frontonly-dtb.sh BASE.dtb OUT.dtb}
EXPECTED=e9fd13a29b6580955d2662c27377dbd1caba14f7f89613510b5e23bd6c266293
GOT=$(sha256sum "$BASE" | awk '{print $1}')
[ "$GOT" = "$EXPECTED" ] || { echo "base DTB identity drift: $GOT" >&2; exit 1; }
cp "$BASE" "$OUT"
# RDI transport diagnostic is front-only. Removing the rear endpoint prevents
# CAMSS notifier completion from depending on an unrelated OV13858 bind.
fdtput -r "$OUT" /soc@0/isp@acb7000/ports/port@1
fdtput -t s "$OUT" /soc@0/cci@ac15000/i2c-bus@1/camera@10 status disabled
fdtput -r "$OUT" /soc@0/cci@ac15000/i2c-bus@1/camera@10/port
# Fail closed on the accepted front electrical tuple.
[ "$(fdtget -t x "$OUT" /soc@0/isp@acb7000/ports/port@2/endpoint bus-type)" = 1 ]
[ "$(fdtget -t x "$OUT" /soc@0/isp@acb7000/ports/port@2/endpoint data-lanes)" = 0 ]
[ "$(fdtget -t s "$OUT" /soc@0/cci@ac15000/i2c-bus@1/camera@10 status)" = disabled ]
# Round-trip to make graph validation fatal while ignoring pre-existing unrelated
# duplicate unit-address diagnostics emitted by dtc.
dtc -I dtb -O dtb "$OUT" -o "$OUT.check" 2>"$OUT.dtc.log"
if grep -qE 'graph_endpoint|graph_child_address' "$OUT.dtc.log"; then
  cat "$OUT.dtc.log" >&2
  rm -f "$OUT.check"
  exit 1
fi
rm -f "$OUT.check"
sha256sum "$OUT"
