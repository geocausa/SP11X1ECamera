#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
r=json.load(open(D/'RESULT.json'))

assert r['classification']=='OFFLINE_FIRST_FRAME_BLOCKER_AUDIT_PASS'
assert r['rear_register_providers_integrated']=='714/714'
assert r['stable_dmi']['pdpc_0x3d08_selector1']['rear_all_zero'] is True
assert r['stable_dmi']['lsc_0x4308_selector3']['rear_all_zero'] is True
for k in (
    'bpc_abf_0x4908_selector1',
    'gamma_0x5f08_selectors1_2_3',
    'dsx_0xa008_selectors1_2',
    'dsx_0xa208_selectors1_2',
):
    assert r['stable_dmi'][k]['cross_sensor_identical'] is True
assert r['transport']['period_cfg_0x008c']['materializer_boundary_closed'] is True
assert r['transport']['period_cfg_0x008c']['upstream_derivation_closed'] is False
assert r['windows_boot_required_for_next_step'] is False
assert r['linux_camera_runtime_performed'] is False

print('E007R_AUDIT_VERIFY_PASS')
print('bind_only=PDPC_zero,LSC_selector3_zero')
print('blockers=BPC_ABF,Gamma,DSX,PERIOD_CFG,offline_full_request')
