#!/usr/bin/env python3
from pathlib import Path
import json
r=json.loads((Path(__file__).with_name('RESULT.json')).read_text())
assert r['status']=='FAIL_CLOSED_BEFORE_FIRST_OPTICAL_FRAME'
assert r['front_select_succeeded'] and r['front_publisher_frames']==0
assert not r['front_private_render_created'] and not r['rear_started'] and not r['soak_started']
assert r['automatic_golden_recovery'] and r['next_experiment']=='E012D'
print('{"status":"PASS_E012C_FAIL_CLOSED_REVIEW","next":"E012D"}')
