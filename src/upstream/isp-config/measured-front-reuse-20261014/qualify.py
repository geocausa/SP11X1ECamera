#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Validate reuse fragment and old native behavior; no hardware operations."""
from pathlib import Path
import json,hashlib,subprocess,datetime
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-measured-reuse-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 audit=json.loads((Q/'baseline-audit.json').read_text())
 for n,h in audit['repository_pins'].items():assert sha(R/n)==h
 for n,h in audit['native_source_pins'].items():assert sha(Path(audit['native_stage'])/n)==h
 assert sha(Path(audit['run93_stage'])/'run-93.json')==audit['run93_config_pin']
 header=Q/'sp11-front-measured-config.h';data=header.read_bytes()
 p=subprocess.run(['python3',str(Q/'generate.py')],capture_output=True,text=True);assert not p.returncode,p.stderr
 assert header.read_bytes()==data,'generator not deterministic'
 g=json.loads((Q/'GENERATED.json').read_text())
 assert g['full_configuration_words']==24 and g['activation_writes']==0 and not g['complete_startup']
 host=json.loads((C/'host01/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 assert host['header_sha256']==build['header_sha256']==sha(header)
 assert host['status']=='PASS_OWN_CONFIGURATION_MATCHES_ACTUAL_NATIVE_OVERRIDES'
 assert build['status']=='PASS_NATIVE_ABI_ARM64_COMPILE_ONLY'
 assert sha(Path(build['module_path']))==build['module_sha256']
 p=subprocess.run(['perl',str(R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01/candidate-35/cdm-owner-qual01/source/scripts/checkpatch.pl'),'--no-tree','--file',str(header)],capture_output=True,text=True)
 (C/'header-style.log').write_text(p.stdout+p.stderr)
 assert not p.returncode and '0 errors, 0 warnings' in p.stdout,p.stdout
 result={'schema':'sp11-calibrated-native-reuse-validation-v1',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'PASS_EXISTING_MEASURED_CONFIG_EXTRACTED_WITH_NATIVE_BEHAVIOR_PARITY',
 'project_parent':audit['project_parent'],'baseline_audit':audit,'generated':g,
 'actual_native_override_tests':host,'native_ABI_compile':build,
 'deterministic_regeneration':True,'header_style_errors':0,'header_style_warnings':0,
 'package_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'reused_calibration':True,'calibration_remeasured':False,'private_profile_read':False,
 'physical_capture_or_runtime_changed':False,'installed':False,
 'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'limits':['Fragment only; private startup loader/materializer still required by installed calibrated stack',
 'Five partial mask words and ABF activation are deferred; other profile scalars/tables also remain',
 'Own LSC/ABF/tone/CCM/AE/AWB calibration remains valid in original domain and must be reused; no new measurement done',
 'Host synthetic command seeds are not optical pixels, physical register access, frame parity, timing or IRQ/DMA proof',
 'Only original native2160->1440 mode allowed; other domains including standard2640 need explicit compatibility proof',
 'Complete independent startup, loader replacement, native hardware qualification and full standard API/provenance/DCO/upstream review remain open']}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/CALIBRATED-NATIVE-REUSE-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'reused_configuration_words':24,'private_partial_masks_deferred':5,
 'activation_deferred':1,'new_calibration':False,'native_ABI_compile':'PASS','upstream_ready':False}))
if __name__=='__main__':main()
