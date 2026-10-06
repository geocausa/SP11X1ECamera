#!/usr/bin/env python3
from pathlib import Path
import json
p=Path(__file__).resolve().parent
r=json.loads((p/'RESULT.json').read_text()); n=json.loads((p/'NEXT-SOURCE.json').read_text())
assert r['status']=='PASS_RGB_PRODUCT_INTEGRATION_SOURCE_OFFLINE'
assert r['product_scope']=='front_rear_rgb_parity'
assert r['existing_rgb_session_service_tests_passed']==42 and r['new_product_tests_passed']==14 and r['route_policy_tests_passed']==11
assert r['rgb_source_suite_passed'] and r['product_publisher_boot_token_denial_on_golden_passed']
assert not r['product_service_default_enabled'] and not r['product_enable_contract_created'] and not r['live_product_install_executed']
assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and not r['new_kernel_build']
assert r['next_experiment']=='E012B' and n['experiment']=='E012B'
print('{"status":"PASS_E012A_PORTABLE_REVIEW","next":"E012B"}')
