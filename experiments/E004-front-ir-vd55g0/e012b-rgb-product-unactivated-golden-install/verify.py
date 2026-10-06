#!/usr/bin/env python3
from pathlib import Path
import json
p=Path(__file__).resolve().parent;r=json.loads((p/'RESULT.json').read_text());n=json.loads((p/'NEXT-SOURCE.json').read_text())
assert r['status']=='PASS_RGB_PRODUCT_UNACTIVATED_GOLDEN_INSTALL'
assert r['product_service_installed'] and not r['product_service_enabled'] and not r['product_service_active']
assert not r['product_enable_contract_present'] and not r['product_boot_entry_created'] and not r['product_boot_token_present']
assert not r['camera_media_nodes_present'] and not r['camera_modules_loaded']
assert r['installed_asset_hashes_verified'] and r['systemd_units_verified'] and r['post_install_overlap_guard_passed']
assert r['new_front_camera_starts']==r['new_rear_camera_starts']==r['new_reboots']==0 and not r['new_kernel_build']
assert r['next_experiment']=='E012C' and n['experiment']=='E012C'
print('{"status":"PASS_E012B_PORTABLE_REVIEW","next":"E012C"}')
