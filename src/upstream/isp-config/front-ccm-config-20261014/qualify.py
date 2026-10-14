#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,re,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-ccm-config-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 subprocess.run(['python3',str(Q/'generate-policy.py'),'--check'],check=True,capture_output=True)
 source=json.loads((C/'native03/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 assert source['status']=='PASS_OWN_MEASURED_Q7_COMPLETE_CONFIGURATION'
 assert source['source_cases']==456 and source['comparison_records']==453 and source['original_common_cases']==13 and source['original_common_comparison_cases']==12
 assert source['original_PE_immutable'] and not source['arithmetic_or_branch_shims']
 assert source['SP_callee_saved_restored'] and source['canaries_intact']
 assert source['original_builder_fixed_addresses_observed'] and not source['addresses_substituted']
 assert source['source_coefficient_field_bits']==12 and source['source_offset_field_bits']==13
 assert source['coefficient_numeric_values_unchanged'] and source['canonicalized_reserved_sign_fill']
 assert source['source_common_qfactor4_packer_wrap_counterexample']
 assert source['configuration_words']==10 and source['configuration_bytes']==48
 assert not source['module_control_commands_emitted'] and not source['constructor_executed']
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY'
 assert not (build['warnings'] or build['errors'] or any(any(v.values()) for v in build['header_styles'].values()))
 assert sha(Path(build['module_path']))==build['module_sha256']
 headers={
 'sp11-front-ccm-config.h':Q/'sp11-front-ccm-config.h',
 'sp11-front-ccm-measured.h':Q/'sp11-front-ccm-measured.h',
 'sp11-front-fields.h':R/'src/upstream/isp-config/sp11-front-fields.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():assert sha(p)==source['header_pins'][n]==build['header_pins'][n]
 for n,h in source['prior_reference_pins'].items():assert sha(R/n)==h
 for run in source['compiler_runs']:
  result=run['result'];assert run['ASan_UBSan'] and result['status']=='PASS'
  assert result['admitted_native_cases']==408 and result['rejected_other_policy_cases']==45
  assert result['atomic_negatives']==108
 for k in ['private_profile_read','private_tuning_read','pixels_read','calibration_remeasured','new_optical_fit','runtime_changed','installed','loaded','hardware']:assert not source[k]
 for k in ['installed','loaded','CAMSS_or_kernel_rebuilt','runtime_changed','hardware']:assert not build[k]
 text=headers['sp11-front-measured-config.h'].read_text()
 prior=set(int(x,16) for x in re.findall(r'\{ (0x[0-9a-f]+)U,',text));assert len(prior)==24
 prior.update([0x3d60,0x4760,0x5460,0x5a60,0x4b68])
 for lo,hi in [(0x4b68,0x4b80),(0x3b68,0x3b98),(0x6168,0x61b0),(0x9c70,0x9c98),(0x9e70,0x9e98),(0x9864,0x9888),(0x9a64,0x9a88)]:prior.update(range(lo,hi,4))
 new=set(range(0x5868,0x5890,4))
 assert len(prior)==101 and len(new)==10 and not (prior&new)
 result={'schema':'sp11-front-complete-ccm-qualification-v1','status':'PASS_SOURCE_AND_COMPILE_ONLY',
 'prior_measured_matrix_and_transpose_reused_unchanged':True,'new_optical_calibration':False,
 'legacy_encoder_reserved_bits_canonicalized_to_original_source':True,
 'source_acceptance':'native03','compile_acceptance':'native-compile01',
 'excluded_attempts':['native01 direct source comparison exposed thirteen-bit legacy sign-fill vs actual twelve-bit CC131 and declaration alignment; native02 uses canonicalization; final native03 corrects common census to13 incl qfactor4'],
 'source':source,'build':build,
 'new_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file() and p.suffix in ['.h','.c','.py','.md']},
 'configuration_registers':[hex(x) for x in sorted(new)],
 'candidate_unique_configuration_addresses_before':len(prior),
 'candidate_unique_configuration_addresses_after':len(prior|new),
 'retained_crop_static_method_entries':{'packer':'0xb57980','builder':'0xb57740','scope':'static binding in CCM proof; separately executed in FRONT-CROP-CONFIG-20261014'},
 'coefficient_fractional_precision_bound_to_scale_control':True,
 'physical_CCM_sample_precision_qualified':False,
 'full_Gamma_CST_video_precision_bound':False,
 'candidate_leaves_are_not_a_complete_program':True,
 'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'next':'Reuse retained Crop12 and core/Gamma field work to complete explicit module/precision/startup around native lifetime; replace private loading in fresh candidate, then physical/image parity'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/FRONT-CCM-CONFIG-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','candidate_unique_configuration_addresses_after','coefficient_fractional_precision_bound_to_scale_control','complete_startup','upstream_ready']}))
if __name__=='__main__':main()
