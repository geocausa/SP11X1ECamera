#!/usr/bin/env python3
"""Geometry ratio hypothesis against independent live scalar and private DMI."""
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
src=PARENT/'e008u-rear-bf-roi-geometry-audit/audit-private.py'
spec=importlib.util.spec_from_file_location('e009f_private',src)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
with tempfile.TemporaryDirectory(prefix='e009f-source-') as tmp:
    ratio_bin=str(Path(tmp)/'ratio')
    forward_bin=str(Path(tmp)/'forward')
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',
                    str(HERE/'compile-check.c'),'-o',ratio_bin],check=True,capture_output=True)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',
                    str(PARENT/'e009e-rear-af-live-zoom-forward/offline-roi.c'),
                    '-o',forward_bin],check=True,capture_output=True)
    candidate_bits=int(subprocess.check_output([ratio_bin]).strip(),16)
    candidate_zoom=struct.unpack('<f',struct.pack('<I',candidate_bits))[0]
    generated=subprocess.check_output([forward_bin,candidate_zoom.hex(),'1.0'])
assert candidate_bits == 0x3f7f3f0f
assert len(generated)==1200
observed=audit.observed()
counts={f'startup{i}':sum(x==y for x,y in zip(generated[i*300:(i+1)*300],observed[f'startup{i}'])) for i in range(4)}
counts['steady_ac8']=sum(x==y for x,y in zip(generated[600:900],observed['steady_ac8']))
assert all(v==300 for v in counts.values())
result={'schema':'E009F-crop-width-ratio-hypothesis-v1',
        'ratio_expression':'float32(camif_width) / float32(sensor_width)',
        'sensor_width':4076,'camif_width':4064,
        'candidate_float32_bits':f'{candidate_bits:08x}',
        'independent_live_float32_bits':'3f7f3f0f',
        'candidate_matches_live_scalar_bits':True,
        'source_of_transient_zoom_proven':False,
        'derived_request_policy_runtime_authorized':False,
        'selector1_matching_bytes':counts,
        'native_rear_isp_runtime_authorized':False,
        'captured_roi_bytes_or_coordinates_emitted':False}
(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print('E009F_RATIO_HYPOTHESIS_PASS float32 bits match live; 5 selectors 300/300; producer open')
