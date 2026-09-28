#!/usr/bin/env python3
"""Pinned physical zoom scalar into source-generated ROI; aggregate bytes only."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = HERE.parent / 'e008u-rear-bf-roi-geometry-audit/audit-private.py'
TUNING = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin')
TUNING_SHA = '4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635'
MFT = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
MFT_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
DEC = ROOT / 'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py'
def imported(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

audit = imported(SRC, 'e009e_private')
decoder = imported(DEC, 'e009e_decoder')
assert hashlib.sha256(MFT.read_bytes()).hexdigest() == MFT_SHA
tuning = TUNING.read_bytes()
assert hashlib.sha256(tuning).hexdigest() == TUNING_SHA
header = decoder.parse_header(tuning)
records, _ = decoder.parse_symbol_table(tuning, header['sections'][0], header['sections'][1])
haf = decoder.data_bytes(tuning, header['sections'][1], records[0xB6])
assert all(abs(v - 0.25) < 1e-6 for v in struct.unpack_from('<2f', haf, 0x28))
observed_zoom_bits = 0x3f7f3f0f
observed_zoom = struct.unpack('<f', struct.pack('<I', observed_zoom_bits))[0]
assert observed_zoom.hex() == '0x1.fe7e1e0000000p-1'
with tempfile.TemporaryDirectory(prefix='e009e-source-') as tmp:
    binary = str(Path(tmp) / 'offline-roi')
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',
                    str(HERE / 'offline-roi.c'), '-o', binary],
                   check=True, capture_output=True)
    generated = subprocess.check_output([binary, '0x1.fe7e1ep-1', '1.0'])
    neutral_control = subprocess.check_output([binary, '1.0', '1.0'])
assert len(generated) == len(neutral_control) == 4*300
observed = audit.observed()
assert sum(x==y for x,y in zip(neutral_control[300:600], observed['startup1'])) == 250
results = {}
for i in range(4):
    label = f'startup{i}'
    clean = generated[i*300:(i+1)*300]
    actual = observed[label]
    c, a = audit.decode(clean), audit.decode(actual)
    results[label] = {'matching_bytes': sum(x == y for x,y in zip(clean, actual)),
                      'matching_fields': {k: sum(x[k] == y[k] for x,y in zip(c,a))
                                          for k in audit.FIELDS}}
    assert results[label]['matching_bytes'] == 300
    assert all(v == 25 for v in results[label]['matching_fields'].values())
steady = observed['steady_ac8']
results['steady_ac8'] = {'matching_bytes':sum(x==y for x,y in zip(generated[600:900],steady))}
assert results['steady_ac8']['matching_bytes'] == 300
safe = {'schema':'E009E-physical-scalar-forward-v1',
        'classification':'FOUR_STARTUP_PLUS_ONE_STEADY_SELECTOR1_OFFLINE_EXACT',
        'same_sp11_live_first_normal_zoom_float32_bits':f'{observed_zoom_bits:08x}',
        'same_sp11_live_first_normal_zoom':observed_zoom,
        'live_request_to_packet1_identity_directly_tagged':False,
        'live_zoom_upstream_calculation_source_closed':False,
        'selected_haf_fraction_source_verified':True,
        'packet1_zoom_one_negative_control_matching_bytes':250,
        'compared':results,
        'native_rear_isp_runtime_authorized':False,
        'captured_roi_coordinates_or_dmi_bytes_emitted':False}
(HERE/'RESULT.json').write_text(json.dumps(safe,indent=2,sort_keys=True)+'\n')
print('E009E_PRIVATE_FORWARD_PASS startup0..3 and steady each 300/300')
