#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent
r=json.loads((D/'RESULT.json').read_text()); assert r['status']=='PREPARED_OFFLINE_NOT_ARMED' and r['planned_cross_camera_transitions']==5
for f in ['prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-once.sh','golden-return-check.sh','retire-candidate.sh']:
    subprocess.check_call(['bash','-n',str(D/f)])
for f in ['discover-unified.py','route-state.py','verify-live.py']:
    subprocess.check_call(['python3','-m','py_compile',str(D/f)])
text=(D/'invoke-once.sh').read_text()
for tok in ['rear_leg 1','front_leg 1','rear_leg 2','front_leg 2','rear_leg 3','front_leg 3','FINAL-NEUTRAL','ATTEMPT1-CONSUMED.marker']:
    assert tok in text
assert 'same_boot_retry_authorized": false' in (D/'RESULT.json').read_text()
print('E004dk PREP VERIFY: PASS (six legs / five transitions / one-shot / no retry)')
