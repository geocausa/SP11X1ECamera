#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Record source-only qualification; no hardware admission."""
from pathlib import Path
import json,hashlib,datetime,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-cold-fields-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 native=json.loads((C/'native01/RESULT.json').read_text())
 build=json.loads((C/'BUILD.json').read_text())
 host=json.loads(Path(build['host_result_path']).read_text())
 assert native['status']=='PASS_SYNTHETIC_EXACT_NATIVE_FIELD_ROUTINES'
 assert (native['module_cases'],native['bls_cases'],native['old_mask_fraction_cases'])==(560,1668,4)
 for f,h in native['prior_reused_source_pins'].items():assert sha(R/f)==h
 audit=json.loads((R/'src/upstream/isp-config/measured-front-reuse-20261014/baseline-audit.json').read_text())
 for f,h in audit['repository_pins'].items():assert sha(R/f)==h
 for f,h in audit['native_source_pins'].items():assert sha(Path(audit['native_stage'])/f)==h
 assert sha(Path(audit['run93_stage'])/'run-93.json')==audit['run93_config_pin']
 assert host['status']=='PASS'
 assert all(x['result']['exhaustive_offset_vectors']==262144 for x in host['runs'])
 assert len(host['compiled_mutations_rejected_each'])==4
 for name,h in host['source_pins'].items():
  p=Q/name if name=='sp11-front-cold-fields.h' else R/'src/upstream/isp-config/measured-front-reuse-20261014'/name if name=='sp11-front-measured-config.h' else R/'src/upstream/isp-config'/name
  assert sha(p)==h
 assert build['header_sha256']==sha(Q/'sp11-front-cold-fields.h')
 assert sha(Path(build['module_path']))==build['module_sha256']
 assert build['warnings']==build['errors']==0 and not build['loaded'] and not build['installed']
 cp=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01/candidate-35/cdm-owner-qual01/source/scripts/checkpatch.pl'
 p=subprocess.run(['perl',str(cp),'--no-tree','--strict','--file',str(Q/'sp11-front-cold-fields.h')],capture_output=True,text=True)
 (C/'header-style.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0 and '0 errors, 0 warnings, 0 checks' in p.stdout,p.stdout
 rows={}
 for line in (R/'src/native-rgb/front-ae/tuning/imx681-front-open-regs.txt').read_text().splitlines():
  line=line.split('#')[0].strip()
  if line:
   a,m,v=(int(x,0) for x in line.split(','));rows[a]=(m,v)
 assert rows[0x4b68]==(0xffff,1649<<16)
 assert all(rows[a]==(0xfffffffe,0) for a in [0x3d60,0x4760,0x5460,0x5a60])
 result={'schema':'sp11-cold-front-fields-validation-v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'project_parent':'3a77f40ab2a68b952460f524f29974e5c0cb067f',
 'status':'PASS_SOURCE_COLD_POLICY_NATIVE_FIELD_SEMANTICS','native_field_tests':native,
 'host_tests':host,'native_ABI_compile':build,'header_style_errors':0,'header_style_warnings':0,'header_style_checks':0,
 'package_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'new_fragment_words':5,'new_fragment_bytes':60,'prior_measured_fragment_words':24,
 'calibration_remeasured':False,'runtime_changed':False,'private_profile_read':False,
 'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'limits':['Source policy only, not full startup or equality with inherited private words',
 'Native BLS selector13/precision not yet observed in live calibrated front context',
 'Chosen offset fraction0 and four cold-zero images need original-domain physical qualification',
 'Other functional scalar setup, own DMI binding, independent startup/steady loader replacement remain',
 'No fresh calibration, camera allocation, frame/pixel access, MMIO, module installation/load or reboot',
 'No parent teardown, standard API, whole-series provenance/license/DCO approval established']}
 for p in [C/'QUALIFIED.json',R/'docs/COLD-FRONT-FIELDS-20261014.json']:
  p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','new_fragment_words','new_fragment_bytes','runtime_changed','upstream_ready']}))
if __name__=='__main__':main()
