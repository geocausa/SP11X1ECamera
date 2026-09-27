#!/usr/bin/env python3
import json
from pathlib import Path

D=Path(__file__).resolve().parent
s=(D/'camss-vfe-e008l-rear-command-dma.inc').read_text()
r=json.loads((D/'RESULT.json').read_text())

for x in [
    'e008l_rear_packet_sizing',
    'e008l_rear_packet_bind_layout',
    'e008l_rear_command_alloc',
    'e008l_rear_command_output',
    'e008l_rear_command_mark_submitted',
    'e008l_rear_command_release',
    'e007y_startup_variants',
    'get_unaligned_le32',
    'dma_alloc_coherent',
    'vfe680_x1e_dma_span_32bit',
    'dma_free_coherent',
    'set->hardware_exposed && !rtcdm_stopped',
    'return -EOPNOTSUPP',
]:
    assert x in s, x

assert s.count('dma_alloc_coherent') == 1
assert 'Windows' not in s
assert r['packets'] == 4
assert r['dmi_sizes_derived_from_e007y_skeleton']
assert r['full_dma_span_32bit_checked']
assert r['release_after_submit_requires_rtcdm_stopped']
assert not r['runtime_call_site_present']
assert not r['runtime_actions_performed']
print('E008l VERIFY PASS')
