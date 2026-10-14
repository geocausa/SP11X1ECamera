#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Source-only qualification, preserving native calibration and runtime."""
from pathlib import Path
import json,hashlib,subprocess,datetime
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-bls121-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 native=json.loads((C/'native04/RESULT.json').read_text())
 build=json.loads((C/'BUILD.json').read_text())
 assert native['status']=='PASS_EXACT_NATIVE_FACTORY_PACKER_COMMAND_ARGUMENTS_AND_C_ENCODER'
 assert native['native_primary_cases']==712 and native['native_other_layout_cases']==8
 assert native['original_image_immutable'] and native['cold_register_image_zero_from_poisoned_allocation']
 assert native['original_callee_saved_and_SP_restored'] and native['allocation_canaries_intact']
 assert native['source_bound_selector_registers']['13']=={
  'module_register':'0x4b60','configuration_register':'0x4b68','offset_shift':14,'offset_width':18}
 assert all(x['result']['native_vectors']==712 and x['result']['rejections']>0 for x in native['compiler_runs'])
 assert len(native['compiled_mutations_rejected_each'])==5
 paths={
 'sp11-front-bls121.h':Q/'sp11-front-bls121.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 assert native['header_pins']==build['header_pins']
 for n,h in native['header_pins'].items():assert sha(paths[n])==h
 for n,h in native['prior_reference_pins'].items():assert sha(R/n)==h
 baseline=json.loads((R/'src/upstream/isp-config/measured-front-reuse-20261014/baseline-audit.json').read_text())
 for n,h in baseline['repository_pins'].items():assert sha(R/n)==h
 for n,h in baseline['native_source_pins'].items():assert sha(Path(baseline['native_stage'])/n)==h
 assert sha(Path(baseline['run93_stage'])/'run-93.json')==baseline['run93_config_pin']
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY'
 assert build['warnings']==build['errors']==0 and not build['installed'] and not build['loaded']
 assert sha(Path(build['module_path']))==build['module_sha256']
 cp=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01/candidate-35/cdm-owner-qual01/source/scripts/checkpatch.pl'
 p=subprocess.run(['perl',str(cp),'--no-tree','--strict','--file',str(Q/'sp11-front-bls121.h')],capture_output=True,text=True)
 (C/'header-style.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0 and '0 errors, 0 warnings, 0 checks' in p.stdout,p.stdout
 rows={}
 for line in (R/'src/native-rgb/front-ae/tuning/imx681-front-open-regs.txt').read_text().splitlines():
  line=line.split('#')[0].strip()
  if line:
   a,m,v=(int(s,0) for s in line.split(','));rows[a]=(m,v)
 assert rows[0x4b68]==(0xffff,1649<<16) and rows[0x4b6c]==(0,0x835)
 result={'schema':'sp11-front-bls121-validation-v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'project_parent':'f3324f7fe0738c5bbdda8840ec694fed207064f3',
 'status':'PASS_IFE18_SOURCE_FACTORY_TO_CONFIGURATION_COMPILER',
 'native_source_bridge':native,'native_ABI_compile':build,
 'package_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'header_style_errors':0,'header_style_warnings':0,'header_style_checks':0,
 'configuration_words':6,'command_bytes':32,'module_activation_commands':0,
 'new_unique_threshold_fields':4,'total_unique_configuration_candidates':33,
 'bls_selector13_bound_to_ife_address_by_source':True,
 'live_front_bls_selector_or_precision_observed':False,
 'calibration_remeasured':False,'private_profile_read':False,'private_tuning_read':False,
 'runtime_changed':False,'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'excluded_attempts':['native01 syntax/context experiment','native02 partial parent output16','native03 partial parent output32','other module constructor exploration with unmodeled CRT boundaries'],
 'limits':['Source bridge uses owned partial context/parent fixtures, not a complete independent Windows runtime',
 'Live front precision/domain and fraction0/threshold0 need physical validation',
 'No module activation, DMI, MMIO, image/frame access, allocation on hardware or private loader replacement',
 'Surrounding independent startup plus standard API, provenance/license/DCO review remain']}
 for p in [C/'QUALIFIED.json',R/'docs/FRONT-BLS121-20261014.json']:
  p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','configuration_words','command_bytes','new_unique_threshold_fields','runtime_changed','upstream_ready']}))
if __name__=='__main__':main()
