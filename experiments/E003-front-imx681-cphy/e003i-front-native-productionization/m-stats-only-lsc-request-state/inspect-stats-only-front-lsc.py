#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,tempfile,shutil
HERE=Path(__file__).resolve().parent
tmp=Path(tempfile.mkdtemp(prefix='e003i-m-'))
try:
 m=tmp/'manifest.json'
 subprocess.run([str(HERE/'generate-stats-only-front-lsc.py'),'--output-dir',str(tmp/'out'),'--manifest',str(m)],check=True,stdout=subprocess.DEVNULL)
 j=json.loads(m.read_text())
 if j['schema']!='sp11-e003i-stats-only-front-lsc-v1' or not j['accepted']:raise SystemExit('manifest drift')
 if j['device_mft_required'] or j['unicorn_required']:raise SystemExit('native dependency returned')
 if j['remaining_lsc_live_input']!='raw Tintless statistics plus ordinary trigger state for tuning interpolation':raise SystemExit('live-input boundary drift')
 s=(HERE/'generate-stats-only-front-lsc.py').read_text()
 # Captures may appear only as validation; calculation must construct config/descriptors/fresh state.
 for x in ('def build_front_x1():','def descriptor(base):','m.mem_write(WRAP,bytes(0x1090))'):
  if x not in s:raise SystemExit('missing normalized constructor: '+x)
 print('E003I_STATS_ONLY_FRONT_LSC_INSPECT=PASS')
 print('CAPTURED_X1_INPUT=false')
 print('CAPTURED_DESCRIPTOR_INPUT=false')
 print('CAPTURED_WRAPPER_CORE_INPUT=false')
 print('LIVE_ADAPTIVE_INPUT=Tintless_stats')
 print('RUNTIME_AUTHORIZED=false')
finally:shutil.rmtree(tmp)
