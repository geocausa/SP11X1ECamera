#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent
r=json.loads((D/'RESULT.json').read_text())
assert r['status']=='PREPARED_OFFLINE_NOT_ARMED'
assert r['corrections']['front_pix_source_pad']==4 and r['corrections']['bash_errtrace'] is True
for f in ['prearm-check.sh','install-candidate.sh','arm-once.sh','runtime-preflight.sh','load.sh','invoke-once.sh','golden-return-check.sh','retire-candidate.sh']:
    subprocess.check_call(['bash','-n',str(D/f)])
for f in ['discover-unified.py','route-state.py','verify-live.py']:
    subprocess.check_call(['python3','-m','py_compile',str(D/f)])
t=(D/'invoke-once.sh').read_text()
assert t.startswith('#!/usr/bin/env bash\nset -Eeuo pipefail')
assert '\"msm_csid1\":4 -> \"msm_vfe1_pix\":0 [0]' in t
assert '\"msm_csid1\":1 -> \"msm_vfe1_pix\":0 [0]' not in t
assert ('corrected'+'-corrected') not in '\n'.join(x.read_text(errors='ignore') for x in D.iterdir() if x.is_file() and x.name!='verify-prep.py')
for tok in ['rear_leg 1','front_leg 1','rear_leg 2','front_leg 2','rear_leg 3','front_leg 3','FINAL-NEUTRAL','ATTEMPT1-CONSUMED.marker']:
    assert tok in t
print('E004dl PREP VERIFY: PASS (pad4 + ERR inheritance + six-leg no-retry soak)')
