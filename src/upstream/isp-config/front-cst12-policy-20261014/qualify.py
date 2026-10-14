#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import datetime,hashlib,json,re,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-cst12-policy-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 native=json.loads((C/'native02/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 assert native['status']=='PASS_REUSED_CST_ENCODER_ORIGINAL_NATIVE_CONFIGURATION_AND_OWN_POLICY'
 assert native['native_cases']==675 and native['policy_admitted_cases']==558 and native['policy_rejected_generic_source_cases']==117
 assert native['original_image_immutable'] and native['original_named_callee_saved_and_SP_restored']
 assert native['owned_inputs_and_canaries_intact'] and native['nonzero_old_image_residual_counterexample']
 assert not native['constructor_executed'] and not native['field_or_branch_shims']
 assert len(native['compiled_mutations_rejected_each'])==4 and len(native['compiler_runs'])==2
 for run in native['compiler_runs']:
  result=run['result']
  assert result['accepted_native_configurations']==558 and result['rejected_native_nonpolicy_states']==117
  assert result['mathematical_neutral_values']==4096 and result['atomic_negatives']>=133
 closure={
 'sp11-front-cst12-config.h':Q/'sp11-front-cst12-config.h',
 'sp11-front-cst12-policy.h':Q/'sp11-front-cst12-policy.h',
 'sp11-cst-stats.h':R/'src/upstream/isp-config/sp11-cst-stats.h',
 'sp11-front-fields.h':R/'src/upstream/isp-config/sp11-front-fields.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 assert native['header_pins']==build['header_pins']
 for n,h in native['header_pins'].items():assert sha(closure[n])==h
 for n,h in native['prior_reference_pins'].items():assert sha(R/n)==h
 baseline=json.loads((R/'src/upstream/isp-config/measured-front-reuse-20261014/baseline-audit.json').read_text())
 for n,h in baseline['repository_pins'].items():assert sha(R/n)==h
 for n,h in baseline['native_source_pins'].items():assert sha(Path(baseline['native_stage'])/n)==h
 assert sha(Path(baseline['run93_stage'])/'run-93.json')==baseline['run93_config_pin']
 p=subprocess.run(['python3',str(Q/'generate-policy.py'),'--check'],capture_output=True,text=True);assert p.returncode==0,p.stderr
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY' and build['warnings']==build['errors']==0
 assert not build['installed'] and not build['loaded']
 assert sha(Path(build['module_path']))==build['module_sha256']
 cp=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01/candidate-35/cdm-owner-qual01/source/scripts/checkpatch.pl'
 for name in ['sp11-front-cst12-config.h','sp11-front-cst12-policy.h']:
  p=subprocess.run(['perl',str(cp),'--no-tree','--strict','--file',str(Q/name)],capture_output=True,text=True)
  (C/(name+'.style.log')).write_text(p.stdout+p.stderr)
  assert p.returncode==0 and '0 errors, 0 warnings, 0 checks' in p.stdout,p.stdout
 measured=set(int(x,16) for x in re.findall(r'\{ (0x[0-9a-f]+)U,',closure['sp11-front-measured-config.h'].read_text()))
 previous=measured|{0x3d60,0x4760,0x5460,0x5a60,0x4b68}|set(range(0x4b68,0x4b80,4))|set(range(0x3b68,0x3b98,4))
 cst=set(range(0x6168,0x61b0,4));assert len(previous)==45 and len(cst)==18 and not previous&cst
 result={'schema':'sp11-front-cst12-policy-validation-v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'project_parent':'86d4235c7cfb7af2702c63b2c43dbd0d89b4dd4f',
 'status':'PASS_REUSED_ENCODER_SOURCE_BOUND_CST12_CONFIGURATION_OWN_MATHEMATICAL_POLICY',
 'native_source_bridge':native,'native_ABI_compile':build,
 'package_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'configuration_words':18,'configuration_bytes':80,'new_configuration_candidate_addresses':18,
 'total_unique_configuration_candidate_addresses':len(previous|cst),
 'existing_generic_encoder_modified':False,'existing_matrix_generator_modified':False,
 'policy_matrix_origin':'Existing exact-rational BT.601 GBR generator; neutral-preserving row sums',
 'policy_output_bits':12,'policy_suboffsets':'Zero only','nonzero_suboffset_math_in_hardware_qualified':False,
 'source_builder_fixed_registers_observed':True,'module_control_commands_emitted':0,'DMI_commands_emitted':0,
 'private_coefficients_or_reserve_imported':False,'private_startup_or_tuning_read':False,
 'calibration_remeasured':False,'pixels_read_or_exported':False,'runtime_changed':False,
 'hardware':False,'full_Gamma_CST_scaler_rounding_precision_bound':False,
 'installed_private_CST_dependency_removed':False,'complete_startup':False,
 'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'header_style_errors':0,'header_style_warnings':0,'header_style_checks':0,
 'excluded_attempts':['native01 host signed/unsigned offset warning; final signed expression accepted with02 source/build pins'],
 'limits':['Own12-bit range/zero image policy, not inherited-front equality or physical reset/precision proof',
 'Source constructor not executed; original serializer replaced only by argument observation/success status',
 'No module control, MMIO or runtime caller; existing10-bit round helper cannot imply12-to8 correctness'],
 'next':'Reuse retained scaler/RoundClamp/core source to bind12-bit Gamma/CST output to8-bit NV12 and own measured CCM auxiliary state; complete startup before private loader replacement and fresh original-domain physical/image parity'}
 for p in [C/'QUALIFIED.json',R/'docs/FRONT-CST12-POLICY-20261014.json']:
  p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','configuration_words','configuration_bytes','total_unique_configuration_candidate_addresses','runtime_changed','upstream_ready']}))
if __name__=='__main__':main()
