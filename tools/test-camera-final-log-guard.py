#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Regression check: final teardown warnings cannot be omitted from qualification."""
from pathlib import Path
import importlib.util,json,sys
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('camera_final_log_guard',Q/'camera-final-log-guard.py')
guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
before='[1.000000] baseline\n'
normal='[1.000000] baseline\n[2.000000] clean shutdown\n'
assert guard.analyse(before,normal,'a','a')['status']=='PASS_FINAL_KERNEL_LOG'
signatures=('BUG:','Oops:','Kernel panic','Unable to handle kernel',
            'general protection fault','use-after-free','KASAN:','DMA-API:',
            'WARNING:','status stuck at','failed to enable xclk',
            'power-on cleanup failed','failed to disable avdd',
            'failed to disable dovdd','remove power-off failed','Stream teardown fault','CSID quiesce failed','RDI pause failed','Missing ready buf','Received completion for invalid port',
          'Received wm done for unmapped index','Received completion for invalid output count',
          'Invalid completion group')
for signature in signatures:
    assert guard.analyse(before,'[2.000000] '+signature+'\n continuation\n','a','a')['status']=='FAIL_FINAL_KERNEL_LOG'
try:
    guard.analyse(before,normal,'a','b')
except ValueError:
    pass
else:
    raise AssertionError('boot change admitted')
records={}
if '--retained-sp11' in sys.argv[1:]:
    for identity in ['20261013-02','20261013-03','20261014-04']:
        d=Path('/var/lib/sp11-camera-upstream-front-'+identity)
        result=json.loads((d/'RESULT.json').read_text())
        r=guard.analyse((d/'PRIVATE-PRE-DMESG.txt').read_text(),
                        (d/'PRIVATE-RETURN-DMESG.txt').read_text(),
                        result['boot_id'],(d/'RETURN-BOOT-ID').read_text().strip())
        assert r['status']=='FAIL_FINAL_KERNEL_LOG'
        assert r['signature_counts']['WARNING:']==1
        assert r['signature_counts']['failed to enable xclk']==1
        records[identity]=r
print(json.dumps({'status':'PASS_FINAL_LOG_REGRESSION','positive':1,
                  'negative_diagnostics':len(signatures),'boot_change_refused':True,
                  'retained_regression_runs':records}))
