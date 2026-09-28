#!/usr/bin/env python3
"""Retrospective AF scalar equivalence, not a source-backed live zoom value."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
SOURCE = PARENT / 'e009b-rear-af-settled-forward/offline-roi.c'
PRIVATE = PARENT / 'e008u-rear-bf-roi-geometry-audit/audit-private.py'
spec = importlib.util.spec_from_file_location('e009d_private', PRIVATE)
audit = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(audit)
source = SOURCE.read_text()
assert source.count('.zoom = 1.0f') == 1

def generate(zoom: str) -> bytes:
    with tempfile.TemporaryDirectory(prefix='e009d-private-') as tmp:
        tmp = Path(tmp)
        code = tmp / 'candidate.c'
        code.write_text(source.replace('.zoom = 1.0f', f'.zoom = {zoom}f'))
        binary = tmp / 'candidate'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-I', str(SOURCE.parent), str(code), '-o', str(binary)],
                       check=True, capture_output=True)
        return subprocess.check_output([str(binary)])

settled = generate('1.0')
transient = generate('0.998')
assert len(settled) == len(transient) == 1200
observed = audit.observed()
def match(blob: bytes, i: int) -> int:
    label = f'startup{i}'
    return sum(a == b for a, b in zip(blob[i*300:(i+1)*300], observed[label]))
results = {f'startup{i}': {
    'settled_zoom_1_matching_bytes': match(settled, i),
    'illustrative_zoom_0_998_matching_bytes': match(transient, i),
} for i in range(4)}
assert results['startup0']['settled_zoom_1_matching_bytes'] == 300
assert results['startup1'] == {
    'settled_zoom_1_matching_bytes': 250,
    'illustrative_zoom_0_998_matching_bytes': 300,
}
assert all(results[f'startup{i}'] == {
    'settled_zoom_1_matching_bytes': 300,
    'illustrative_zoom_0_998_matching_bytes': 250,
} for i in (2,3))
safe = {
    'schema': 'E009D-transient-AF-scalar-equivalence-v1',
    'classification': 'RETROSPECTIVE_EQUIVALENCE_ONLY',
    'candidate_source_path': 'default_AF_inverse_zoom',
    'candidate_packet1_zoom_calibrated_from_final_DMI': 0.998,
    'selected_live_packet1_zoom_observed': False,
    'other_AF_input_explanations_excluded': False,
    'compared': results,
    'runtime_seed_authorized': False,
    'captured_values_or_hashes_emitted': False,
}
(HERE / 'RESULT.json').write_text(json.dumps(safe, indent=2, sort_keys=True)+'\n')
print('E009D_PRIVATE_EQUIVALENCE_PASS illustrative packet1 300/300; live input open')
