#!/usr/bin/env python3
"""Compare caller-supplied candidate ROIs to retained private packet words."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MFT = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
RECORDS = Path('/home/geoca/Documents/SP11-PROJECT/06-camera/private/e006a/E006A-PRIVATE-RECORDS-v2.json')
DECODER = ROOT / 'experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py'
assert hashlib.sha256(MFT.read_bytes()).hexdigest() == 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
spec = importlib.util.spec_from_file_location('e009g_decoder', DECODER)
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)
records = json.loads(RECORDS.read_text(encoding='utf-8-sig'))['records']
observed = []
for packet in range(4):
    rec = next(r for r in records if r['n'] == packet and r['idx'] == 1)
    values = [v for addr,v,*_ in decoder.decode(bytes.fromhex(rec['hex']))['writes'] if addr == 0xb26c]
    assert len(values) == 1
    observed.append(values[0])

with tempfile.TemporaryDirectory(prefix='e009g-') as temp:
    executable = str(Path(temp) / 'handoff')
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    str(HERE / 'compile-check.c'), '-o', executable],
                   check=True, capture_output=True)
    def generated(w, h):
        return int(subprocess.check_output([executable,'0','0',str(w),str(h)], text=True), 16)
    first = generated(3658, 2058)   # offline 90% candidate, not a driver default
    later = generated(4064, 2286)   # accepted active rear CAMIF crop
    assert subprocess.run([executable,'4060','0','16','8'],capture_output=True).returncode == 3
    assert subprocess.run([executable,'0','0','0','1'],capture_output=True).returncode == 3
    matches = [first == observed[0]] + [later == observed[i] for i in range(1,4)]
    assert all(matches)
    assert first != later and later != observed[0]
    assert all(first != observed[i] for i in range(1,4))

safe = {
    'schema': 'E009G-explicit-AEC-BHist-ROI-v1',
    'classification': 'FOUR_STARTUP_REGION_WORDS_EXACT_OFFLINE_WITH_CALLER_ROI',
    'same_sp11_startup_matches': matches,
    'startup0_90_percent_geometry_candidate_matches': True,
    'startup1_through_3_full_crop_matches': True,
    'full_crop_negative_control_startup0_matches': False,
    'ninety_percent_negative_control_later_matches': [False,False,False],
    'aec_upstream_initial_roi_policy_source_closed': False,
    'initial_roi_origin_directly_observed': False,
    'native_rear_isp_runtime_authorized': False,
    'captured_register_values_or_packet_bytes_emitted': False,
}
(HERE / 'RESULT.json').write_text(json.dumps(safe,indent=2,sort_keys=True)+'\n')
print('E009G_PRIVATE_AUDIT_PASS four explicit-ROI BHist region words exact; upstream startup policy open')
