#!/usr/bin/env python3
import os, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
CV=BASE/'cv-native-aec-offline-sensor-control-join'
LOCAL=os.environ.get('E003I_CW_LOCAL')=='1'
if not LOCAL:
    cp=subprocess.run([sys.executable,str(CV/'verify-cv.py')],cwd=CV,text=True,capture_output=True)
    if cp.returncode: raise SystemExit(cp.stdout+'\n'+cp.stderr)
    assert 'CV_VERIFY=PASS' in cp.stdout
else:
    print('CV_LOCAL_PARENT_PIN=1')
cp=subprocess.run([sys.executable,str(HERE/'prove-cw.py')],cwd=HERE,text=True,capture_output=True)
if cp.returncode: raise SystemExit(cp.stdout+'\n'+cp.stderr)
print(cp.stdout,end='')
assert 'CW_PROOF=PASS' in cp.stdout
print('CW_VERIFY=PASS')
