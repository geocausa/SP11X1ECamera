#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Rebuild an SP7 player log from per-loop first/last step times.

The player runs a fixed sequence; within a loop the steps drift linearly, so
a loop's step start = first + (last - first) * nominal_cumulative / nominal_span.
Inputs: a template log (any earlier run, for the sequence), T0 (ISO UTC) and a
text file of 'loop count last_index first_s last_s' lines (seconds from T0).
Usage: rebuild-play-log.py template.csv.gz T0 loops.txt out.csv.gz
"""
import csv, gzip, io, sys
from datetime import datetime, timedelta, timezone


def main():
    tmpl = list(csv.DictReader(io.StringIO(gzip.open(sys.argv[1], 'rt').read())))
    seq = [r for r in tmpl if r['loop'] == '0']
    t0 = datetime.fromisoformat(sys.argv[2].replace('Z', '')[:26]).replace(tzinfo=timezone.utc)
    cum = [0.0]
    for r in seq[:-1]:
        cum.append(cum[-1] + int(r['hold_ms']) / 1000)
    rate = 1.0
    out = io.StringIO()
    w = csv.writer(out, lineterminator='\n')
    w.writerow(['loop', 'index', 'id', 'r', 'g', 'b', 'hold_ms', 'start_utc', 'screen'])
    for line in open(sys.argv[3]):
        if not line.strip():
            continue
        loop, count, last, first_s, last_s = line.split()
        last, first_s, last_s = int(last), float(first_s), float(last_s)
        if last == len(seq) - 1:
            rate = (last_s - first_s) / cum[last]
        for i in range(last + 1):
            s = seq[i]
            t = t0 + timedelta(seconds=first_s + cum[i] * rate)
            w.writerow([loop, i, s['id'], s['r'], s['g'], s['b'], s['hold_ms'],
                        t.strftime('%Y-%m-%dT%H:%M:%S.%f') + '0Z', s['screen']])
    gzip.open(sys.argv[4], 'wt').write(out.getvalue())


if __name__ == '__main__':
    main()
