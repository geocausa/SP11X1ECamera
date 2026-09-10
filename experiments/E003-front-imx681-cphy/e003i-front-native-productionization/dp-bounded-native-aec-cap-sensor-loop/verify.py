#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess, tempfile

D=Path(__file__).resolve().parent
BASE=D.parent
DB=BASE/'db-bounded-native-aec-sensor-loop'
DN=BASE/'dn-native-aec-internal-cap'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for f in ['e003i-db-six-frame-native-aec.c','native-db-schedule.c','native-db-schedule.h','bootstrap-controls.c']:
    assert sha(D/f)==sha(DB/f), f

subprocess.run(['python3',str(DB/'verify.py')],check=True)
subprocess.run(['python3',str(DN/'verify-dn.py')],check=True)

build=(D/'build-helper.sh').read_text()
assert '$DN/native-aec-request-loop.c' in build
assert '$DN/native-internal-cap.c' in build
assert 'dj-native-aec-request4-warmup-rebase' not in build
assert '$DJ/native-aec-request-loop.c' not in build

with tempfile.TemporaryDirectory(prefix='e003i-dp-') as td:
    td=Path(td)
    subprocess.run([str(D/'build-helper.sh'),str(td/'helper')],check=True)
    subprocess.run([str(D/'build-bootstrap.sh'),str(td/'bootstrap')],check=True)

print('DP_DB_LIVE_MACHINERY_BYTE_EXACT=PASS')
print('DP_DN_CAP_LINK=PASS')
print('DP_HELPER_WERROR=PASS')
print('DP_BOOTSTRAP_WERROR=PASS')
print('DP_VERIFY=PASS')
