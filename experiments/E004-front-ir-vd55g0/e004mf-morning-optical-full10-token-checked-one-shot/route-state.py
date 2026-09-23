#!/usr/bin/python3
import argparse, runpy
from pathlib import Path
m=runpy.run_path(str(Path(__file__).with_name('camera-session-contract.py')))
a=argparse.ArgumentParser();a.add_argument('topology',type=Path);a.add_argument('--expect')
v=a.parse_args();phase,flags=m['classify'](v.topology.read_text())
if v.expect and v.expect!=phase: raise SystemExit('UNEXPECTED_SESSION_ROUTE')
print('E004KH_MEDIA_ROUTE='+phase+' COMPLETE_119_EDGE_GRAPH=PASS')
