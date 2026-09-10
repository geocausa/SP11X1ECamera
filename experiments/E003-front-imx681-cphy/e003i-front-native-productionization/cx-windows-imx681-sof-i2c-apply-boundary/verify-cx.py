#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[4]
CW=ROOT/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/cw-imx681-atomic-dynamic-control-cluster/verify-cw.py'
AW=ROOT/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/aw-windows-sensor-request-submit/verify-aw.py'
HERE=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(CW)],check=True,stdout=subprocess.DEVNULL)
subprocess.run([sys.executable,str(AW)],check=True,stdout=subprocess.DEVNULL)
subprocess.run([sys.executable,str(HERE/'prove-cx.py')],check=True)
print('CX_VERIFY=PASS')
