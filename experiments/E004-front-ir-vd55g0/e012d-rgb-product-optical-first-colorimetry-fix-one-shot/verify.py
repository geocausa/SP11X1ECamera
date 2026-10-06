#!/usr/bin/env python3
from pathlib import Path
import json
r=json.loads((Path(__file__).with_name('RESULT.json')).read_text())
assert r['status']=='FAIL_CLOSED_BEFORE_DAEMON_ADMISSION'
assert r['camera_modules_bound'] and r['loopback_nodes_created']
assert not r['product_daemon_admitted'] and not r['front_started'] and not r['rear_started']
assert not r['front_private_render_created'] and not r['soak_started']
assert r['automatic_golden_recovery'] and r['next_experiment']=='E012E'
print('{"status":"PASS_E012D_FAIL_CLOSED_REVIEW","next":"E012E"}')
