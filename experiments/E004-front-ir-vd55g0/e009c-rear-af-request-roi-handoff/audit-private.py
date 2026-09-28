#!/usr/bin/env python3
"""Private same-SP11 selector-1 comparison; prints aggregates only."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

here = Path(__file__).resolve().parent
src = here.parent / 'e008u-rear-bf-roi-geometry-audit/audit-private.py'
spec = importlib.util.spec_from_file_location('e009c_source', src)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
with tempfile.TemporaryDirectory(prefix='e009c-private-') as tmp:
    binary = str(Path(tmp) / 'check')
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    str(here / 'compile-check.c'), '-o', binary],
                   check=True, capture_output=True)
    generated = subprocess.check_output([binary])
assert len(generated) == 900
observed = audit.observed()
results = {}
for packet in range(1, 4):
    label = f'startup{packet}'
    clean = generated[(packet-1)*300:packet*300]
    actual = observed[label]
    c, a = audit.decode(clean), audit.decode(actual)
    results[label] = {
        'matching_bytes': sum(x == y for x, y in zip(clean, actual)),
        'matching_fields': {k: sum(x[k] == y[k] for x, y in zip(c, a))
                            for k in audit.FIELDS},
    }
assert results['startup1']['matching_bytes'] == 250
assert all(results[f'startup{p}']['matching_bytes'] == 300 for p in (2,3))
safe = {
    'schema': 'E009C-request-af-roi-handoff-v1',
    'classification': 'SETTLED_2_3_EXACT_PACKET1_REQUEST_INPUT_OPEN',
    'compared': results,
    'request_rect_is_caller_owned': True,
    'runtime_call_site': False,
    'native_rear_isp_runtime_authorized': False,
    'captured_values_or_hashes_emitted': False,
}
(here / 'RESULT.json').write_text(json.dumps(safe, indent=2, sort_keys=True)+'\n')
print('E009C_PRIVATE_PASS packets2/3 300/300; packet1 250/300')
