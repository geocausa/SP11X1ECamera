#!/usr/bin/env python3
"""Validate and distill the ordinary Windows internal CapExposure capture."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def qwords(text):
    return [int(word.replace('`', ''), 16)
            for line in re.finditer(r'[0-9a-f]{8}`[0-9a-f]{8}  ([^\r\n]+)', text)
            for word in re.findall(r'[0-9a-f]{8}`[0-9a-f]{8}', line[1])]


def parse(root):
    raw = (root / 'E003I-DM-oracle.log').read_bytes()
    text = raw.decode()
    pattern = (r'DM_PRE n=(\d+) conv=\w+ out=\w+ bounds=\w+ pred=(\w+) flag=(\w+) '
               r'DM_COMPACT_PRE ([\s\S]*?)DM_BOUNDS_238 ([\s\S]*?)'
               r'DM_POST n=\1 conv=\w+ out=\w+ pred=(\w+) '
               r'DM_COMPACT_POST ([\s\S]*?)DM_REQUEST n=(\d+) frame=(\d+) '
               r'out=\w+ capflag=(\d+)')
    samples = []
    for m in re.finditer(pattern, text):
        n = int(m[1])
        pre, bounds, post = qwords(m[4]), qwords(m[5]), qwords(m[7])
        assert len(pre) == len(post) == 7 and len(bounds) == 0x47
        minima, maxima = bounds[3:70:10], bounds[8:70:10]
        assert minima == [37516] * 7
        assert maxima == [66666664 * 92] * 7
        assert bounds[-1] == 37516
        assert int(m[8]) == int(m[9]) == n + 1
        assert m[2] == m[6] == '3f800000' and int(m[3], 16) == int(m[10]) == 0
        # Every sample bypasses the conditional proportional-rescale prelude.
        assert not (pre[2] > maxima[2] and pre[0] < maxima[0] and pre[0] < pre[2])
        expected = [max(lo, min(v, hi)) for v, lo, hi in zip(pre, minima, maxima)]
        expected[0] = min(expected[:3])
        expected[1] = max(expected[1], expected[2])
        expected[3] = expected[0]
        for i in range(4, 7):
            expected[i] = max(expected[i], expected[i-1])
        assert post == expected
        samples.append(dict(request=n+1, pre=pre, post=post, minimum=minima,
                            maximum=maxima, pred_gain_bits=int(m[2], 16),
                            compact_98_bits=0, prelude_eligible=False))
    assert [s['request'] for s in samples] == list(range(1, 19))
    assert text.count('DM_CAPTURE_COMPLETE caps=18 requests=18 Closing') == 1
    holder = (root / 'E003I-DM-holder-output.txt').read_text()
    assert 'START_STATUS=Success' in holder and 'STOP_PASS' in holder and 'DM_HOLDER_END' in holder
    changed = sum(s['pre'] != s['post'] for s in samples)
    assert changed == 11
    return dict(status='PASS', scope='ordinary front preview; conditional prelude bypassed',
                dll_sha256='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35',
                log_sha256=hashlib.sha256(raw).hexdigest(), samples=samples,
                changed_samples=changed, common_230=37516,
                bound_note='CDB default radix: literal 12 means decimal 18 requests')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('evidence', type=Path)
    ap.add_argument('output', type=Path)
    args = ap.parse_args()
    result = parse(args.evidence)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(f"PASS {len(result['samples'])} samples; {result['changed_samples']} changed by cap")
