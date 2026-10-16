#!/bin/sh
# Trace every register write/read an IR sensor driver makes (regmap trace events), around a lab capture.
# Usage: trace-ir.sh <out-file> <command...>
OUT=$1; shift
T=/sys/kernel/tracing
[ -d $T/events ] || mount -t tracefs nodev $T
echo 0 > $T/tracing_on
echo > $T/trace
echo 65536 > $T/buffer_size_kb
for e in regmap_reg_write regmap_reg_read regmap_bulk_write; do
  [ -d $T/events/regmap/$e ] && echo 1 > $T/events/regmap/$e/enable
done
echo 1 > $T/tracing_on
"$@"
echo 0 > $T/tracing_on
grep -E '0060' $T/trace > $OUT
for e in regmap_reg_write regmap_reg_read regmap_bulk_write; do
  [ -d $T/events/regmap/$e ] && echo 0 > $T/events/regmap/$e/enable
done
wc -l $OUT
