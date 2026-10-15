#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Lab check: field-by-field differences between two rear start-up inputs (names only)."""
import sys
from rearprof import Input
a = Input.from_buffer_copy(open(sys.argv[1], 'rb').read()).dict()
b = Input.from_buffer_copy(open(sys.argv[2], 'rb').read()).dict()
diff = []
def walk(x, y, path):
    if isinstance(x, dict):
        for k in x: walk(x[k], y[k], path + '.' + k)
    elif isinstance(x, list) and len(x) > 64:
        if x != y: diff.append(path + '[table]')
    elif isinstance(x, list):
        for i, (p, q) in enumerate(zip(x, y)): walk(p, q, '%s[%d]' % (path, i))
    elif x != y:
        diff.append(path)
walk(a, b, '')
import collections, re
print(sorted(collections.Counter(re.sub(r'\[\d\]', '[]', d) for d in diff).items()))
