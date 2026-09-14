#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent
r=json.loads((D/'RESULT.json').read_text())
assert r['status']=='PREPARED_OFFLINE_NOT_ARMED' and r['planned_cross_camera_transitions']==5
assert r['same_boot_retry_authorized'] is False and r['accepted_module_rebuilds_used'] is False
for f in ['prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-once.sh','golden-return-check.sh','retire-candidate.sh']:
    subprocess.check_call(['bash','-n',str(D/f)])
for f in ['discover-unified.py','route-state.py','verify-live.py']:
    compile((D/f).read_text(),str(D/f),'exec')
t=(D/'invoke-once.sh').read_text()
assert t.startswith('#!/usr/bin/env bash\nset -Eeuo pipefail')
assert '\"msm_csid1\":4 -> \"msm_vfe1_pix\":0 [0]' in t
for tok in ['rear_leg 1','front_leg 1','rear_leg 2','front_leg 2','rear_leg 3','front_leg 3','FINAL-NEUTRAL','ATTEMPT1-CONSUMED.marker']:
    assert tok in t
pre=(D/'prearm-check.sh').read_text();run=(D/'runtime-preflight.sh').read_text()
for x in ['60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a','7c13bc25517698cf53a8b362857852de7dd674de5c108eed4c9f5b788eed3f61','06bfd6cd4dc4b059e2aa021d3f261b90ed2ceff90450af4bcbe4545fc5c14c0f']:
    assert x in pre and x in run
assert 'build-production.sh' not in pre
assert 'stage-package.sh' in pre
print('E004dn PREP VERIFY: PASS (E004dm userspace + accepted modules + six-leg no-retry soak)')
