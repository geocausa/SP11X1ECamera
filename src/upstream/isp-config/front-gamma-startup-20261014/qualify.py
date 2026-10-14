#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import datetime,hashlib,json,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-gamma-startup-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 host=json.loads((C/'host02/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 assert host['status']=='PASS_STARTUP_BYTES_EQUAL_WORKING_NATIVE_TONE_BRIDGE'
 assert len(host['compiler_runs'])==2 and len(host['compiled_mutations_rejected_each'])==4
 for run in host['compiler_runs']:
  assert run['result']=={'status':'PASS','differential_cases':6209,'slope_rejections':1024,
   'boundary_rejections':3850,'own_v15_curves':1,'workspace_bytes':6160}
 assert len(host['unchanged_prior_tests'])==4
 assert host['header_pins']==build['header_pins']
 closure={
 'sp11-front-gamma-startup.h':Q/'sp11-front-gamma-startup.h',
 'native-front-gamma.h':R/'src/native-rgb/native-front-gamma.h',
 'native-front-isp-params.h':R/'src/native-rgb/native-front-isp-params.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,h in host['header_pins'].items():assert sha(closure[n])==h
 for n,h in host['prior_reference_pins'].items():assert sha(R/n)==h
 baseline=json.loads((R/'src/upstream/isp-config/measured-front-reuse-20261014/baseline-audit.json').read_text())
 for n,h in baseline['repository_pins'].items():assert sha(R/n)==h
 for n,h in baseline['native_source_pins'].items():assert sha(Path(baseline['native_stage'])/n)==h
 run_path=Path(baseline['run93_stage'])/'run-93.json'
 assert sha(run_path)==baseline['run93_config_pin']
 params=json.loads(run_path.read_text())['camss_params']
 assert any(x.startswith('native_front_ccm_q7=') for x in params)
 assert not any(x.startswith('native_front_cst_q10=') for x in params)
 assert host['own_v15_tuning_sha256']==sha(R/'src/native-rgb/front-ae/tuning/imx681-front-v15.yaml')
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY' and build['warnings']==build['errors']==0
 assert not build['installed'] and not build['loaded'] and not build['workspace_on_kernel_stack']
 assert sha(Path(build['module_path']))==build['module_sha256']
 cp=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01/candidate-35/cdm-owner-qual01/source/scripts/checkpatch.pl'
 p=subprocess.run(['perl',str(cp),'--no-tree','--strict','--file',str(Q/'sp11-front-gamma-startup.h')],capture_output=True,text=True)
 (C/'header-style.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0 and '0 errors, 0 warnings, 0 checks' in p.stdout,p.stdout
 refs=['experiments/E004-front-ir-vd55g0/e006r-rear-cst12-tuning-packer/README.md',
 'experiments/E004-front-ir-vd55g0/e006r-rear-cst12-tuning-packer/camss-e006r-cst12.inc',
 'experiments/E004-front-ir-vd55g0/e011m-rs-titan680-capability-origin/README.md',
 'src/upstream/isp-config/FRONT-MINIMAL-PROVENANCE-20261011.md']
 result={'schema':'sp11-front-gamma-startup-validation-v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'project_parent':'d4a6095081a78c0104833d4d707f0f66b36e8a3d',
 'status':'PASS_OWN_TONE_STARTUP_DATA_REUSES_CALIBRATED_NATIVE_PRECISION_BRIDGE',
 'host_qualification':host,'native_ABI_compile':build,
 'package_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'precision_reference_pins':{n:sha(R/n) for n in refs},
 'semantic_tone_bits':10,'native_Gamma_base_delta_bits':12,'startup_generated_data_bytes':3072,
 'workspace_bytes':6160,'configuration_register_addresses_added':0,'total_unique_configuration_candidates':45,
 'module_activation_commands':0,'DMI_commands_or_selectors_emitted':0,
 'run93_own_CCM_override_present':True,'run93_CST_matrix_override_present':False,
 'inherited_CST_auxiliary_state_removed':False,'full_core_CST_processing_precision_bound':False,
 'prior_native_codecs_or_calibration_modified':False,'calibration_remeasured':False,
 'private_startup_or_tuning_read':False,'pixels_read_or_exported':False,
 'runtime_changed':False,'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'header_style_errors':0,'header_style_warnings':0,'header_style_checks':0,
 'excluded_attempts':['host01/native-compile01 functional pass with two alignment style checks; final source pins in02'],
 'next':'Reuse retained functional CST12 packer and original front source to bind calibrated core/colour precision, offsets/scales/clamps; preserve measured CCM/tone/native lifecycle, complete startup before private loader replacement and fresh physical parity'}
 for p in [C/'QUALIFIED.json',R/'docs/FRONT-GAMMA-STARTUP-20261014.json']:
  p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','startup_generated_data_bytes','semantic_tone_bits','native_Gamma_base_delta_bits','runtime_changed','upstream_ready']}))
if __name__=='__main__':main()
