#!/bin/sh
T=/root/imx681-test; O=$T/nx2s; rm -rf $O; mkdir -p $O; export ALL=1
for s in 6 14 20 34 48 64; do
  SETTLE=$s EXTRA=test_pattern=2 $T/lab-next2.sh front $O/s$s 1500 0
  echo "settle=$s $(md5sum < $O/s$s/raw.bin) $(grep -o '[0-9.]* fps' $O/s$s/log.txt | tail -1)" >> $O/summary.txt
done
echo done >> $O/summary.txt
