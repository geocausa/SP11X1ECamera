#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
# Lab probe: rear start WB steps on the flat field, unity LSC; centre output per channel.
import json, subprocess, sys
from pathlib import Path
import numpy as np
W, H = 3840, 2160
S = 255 / 256
M = np.array([[0.299, 0.587, 0.114], [-0.168736 * S, -0.331264 * S, 0.5 * S], [0.5 * S, -0.418688 * S, -0.081312 * S]])
Mi = np.linalg.inv(M)
FW = '/var/lib/sp11-camera-daily2/firmware/qcom/sp11/ov13858-rear-open-v1.bin'
src = json.load(open('loop-src.json'))
for r, b in [tuple(int(x) for x in a.split(',')) for a in sys.argv[1:]]:
    src['start_3a']['wb_r_q10'], src['start_3a']['wb_b_q10'] = r, b
    json.dump(src, open('/root/ab/probe-src.json', 'w'))
    subprocess.run(['python3', 'gen-rear-open-input.py', '/root/ab/probe-src.json', 'unity-lsc.txt', FW], check=True, stdout=subprocess.DEVNULL)
    cap = Path('/root/ab/probe-%d-%d' % (r, b))
    subprocess.run(['sh', 'capture-rear-frames.sh', str(cap), '60'], check=True, stdout=subprocess.DEVNULL)
    f = sorted(cap.glob('*.bin'))[-1]
    d = np.fromfile(f, np.uint8)
    y = d[:W * H].reshape(H, W)[980:1180, 1820:2020].mean()
    uv = d[W * H:].reshape(H // 2, W // 2, 2)[490:590, 910:1010].reshape(-1, 2).mean(0)
    rgb = Mi @ np.array([y, uv[0] - 128, uv[1] - 128])
    print(json.dumps({'wb': [r, b], 'Y': round(float(y), 1), 'U': round(float(uv[0]), 1), 'V': round(float(uv[1]), 1), 'rgb': [round(float(v), 1) for v in rgb]}), flush=True)
    for p in cap.glob('*.bin'):
        p.unlink()
