#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Lab tool: write the open rear start-up source (JSON) from a lab reference input.

Keeps only functional values: request ids, mode geometry, statistics windows/
grids/thresholds/luma weights, AF window, packet phases and valid flags.
Not copied: LSC and GTM tables, BPC/ABF parameters, colour transform (generated
by gen-rear-open-input.py) and the reference's 3A start state, which is replaced
by the values given on the command line (our measurement).
Usage: extract-rear-startup.py reference.bin demux_q10 wb_r_q10 wb_b_q10 > source.json
"""
import json
import sys
from rearprof import Input

STRIP_IQ = ("cst", "bpcabf")


def main():
    ref = Input.from_buffer_copy(open(sys.argv[1], "rb").read())
    d = ref.dict()
    demux, wb_r, wb_b = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    out = {
        "_comment": "SP11 rear ov13858 ISP start-up source for gen-rear-open-input.py. "
                    "Functional values: 4064x2286 GRBG 10-bit -> 3840x2160 NV12, statistics windows, "
                    "AF window. start_3a is our own measurement (open-profile docs).",
        "request_ids": d["request_id"],
        "start_3a": {"demux_q10": [demux] * 4, "wb_r_q10": wb_r, "wb_b_q10": wb_b},
        "geometry": d["geometry"],
        "stats": d["stats"],
        "iq": [{k: v for k, v in q.items() if k not in STRIP_IQ} for q in d["iq"]],
        "adaptive": [{k: a[k] for k in ("request_id", "phase", "valid")} for a in d["adaptive"]],
    }
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
