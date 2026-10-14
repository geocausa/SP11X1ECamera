#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify reuse/source/native-build pins and record explicit precision limits."""
from pathlib import Path
import hashlib,json,re
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-scaler-config-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=json.loads((C/'native05/RESULT.json').read_text())
 build=json.loads((C/'BUILD.json').read_text())
 assert source['status']=='PASS_REUSED_FRONT_VIDEO_SCALER_CONFIGURATION'
 assert source['native_source_cases']==30 and source['native_comparison_records']==24
 assert source['original_PE_immutable'] and not source['arithmetic_or_branch_shims']
 assert source['SP_callee_saved_restored'] and source['canaries_intact']
 assert source['original_builder_fixed_addresses_observed'] and not source['addresses_substituted']
 assert source['source_video_image_offset']==160 and not source['constructor_executed']
 assert source['configuration_words']==18 and source['configuration_bytes']==88
 assert not source['module_control_commands_emitted'] and not source['Crop12_commands_emitted']
 assert not source['normal_MNDS_sample_depth_conversion_proven']
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY'
 assert not (build['errors'] or build['warnings'] or any(build['style'].values()))
 assert sha(Path(build['module_path']))==build['module_sha256']
 headers={
 'sp11-front-scaler-config.h':Q/'sp11-front-scaler-config.h',
 'sp11-geometry-stats.h':R/'src/upstream/isp-config/sp11-geometry-stats.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():assert sha(p)==source['header_pins'][n]==build['header_pins'][n]
 for n,h in source['prior_reference_pins'].items():assert sha(R/n)==h
 for run in source['compiler_runs']:
  result=run['result']
  assert run['ASan_UBSan'] and result['status']=='PASS'
  assert result['native_vectors']==24 and result['admitted_front_vectors']==3
  assert result['rejected_other_geometry']==21 and result['atomic_negatives']==93
 for key in ['private_profile_read','private_tuning_read','pixels_read','calibration_remeasured','runtime_changed','installed','loaded','hardware']:
  assert not source[key]
 for key in ['installed','loaded','CAMSS_or_kernel_rebuilt','runtime_changed','hardware']:assert not build[key]
 measured=headers['sp11-front-measured-config.h'].read_text()
 prior=set(int(x,16) for x in re.findall(r'\{ (0x[0-9a-f]+)U,',measured));assert len(prior)==24
 prior.update([0x3d60,0x4760,0x5460,0x5a60,0x4b68])
 prior.update(range(0x4b68,0x4b80,4));prior.update(range(0x3b68,0x3b98,4))
 prior.update(range(0x6168,0x61b0,4))
 prior.update(range(0x9c70,0x9c98,4));prior.update(range(0x9e70,0x9e98,4))
 new=set(base+4*i for base in [0x9864,0x9a64] for i in range(9))
 assert len(prior)==83 and len(new)==18 and not (prior & new)
 result={'schema':'sp11-front-scaler-qualification-v1','status':'PASS_SOURCE_AND_COMPILE_ONLY',
  'prior_implementations_reused_unchanged':True,'new_scaler_arithmetic':False,
  'source_acceptance':'native05','compile_acceptance':'native-compile01',
  'excluded_attempts':['native01/02 assumed wrong source image span; native03 wrong Video Full slot80',
   'native04 original source PASS but host legacy u16 type shim missing; final native05 repeats with actual slot160'],
  'source':source,'build':build,
  'new_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file() and p.suffix in ['.h','.c','.py','.md']},
  'configuration_registers':[hex(x) for x in sorted(new)],
  'candidate_unique_configuration_addresses_before':len(prior),
  'candidate_unique_configuration_addresses_after':len(prior|new),
  'candidate_leaves_are_not_a_precision_bound_complete_program':True,
  'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
  'next':'Reuse retained Crop12 and source core/Gamma precision work; bind module and full colour pipeline policy, complete own CCM auxiliary state and startup before private-loader replacement and fresh hardware parity'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/FRONT-SCALER-CONFIG-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','prior_implementations_reused_unchanged','candidate_unique_configuration_addresses_after','complete_startup','upstream_ready']}))
if __name__=='__main__':main()
