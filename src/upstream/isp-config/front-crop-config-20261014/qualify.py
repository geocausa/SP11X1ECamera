#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,re
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-crop-config-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=json.loads((C/'native01/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 assert source['status']=='PASS_REUSED_FRONT_VIDEO_CROP'
 assert source['source_cases']==31 and source['comparison_records']==24
 assert source['original_PE_immutable'] and not source['arithmetic_or_branch_shims']
 assert source['SP_callee_saved_restored'] and source['canaries_intact']
 assert source['source_builder_fixed_addresses_observed'] and not source['addresses_substituted']
 assert not source['constructor_executed'] and source['display_counterexample_checked']
 assert not source['module_or_extra_CFG_commands_emitted']
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY'
 assert not (build['warnings'] or build['errors'] or any(build['style'].values()))
 assert sha(Path(build['module_path']))==build['module_sha256']
 headers={
 'sp11-front-crop-config.h':Q/'sp11-front-crop-config.h',
 'sp11-geometry-stats.h':R/'src/upstream/isp-config/sp11-geometry-stats.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():assert sha(p)==source['header_pins'][n]==build['header_pins'][n]
 for n,h in source['prior_reference_pins'].items():assert sha(R/n)==h
 for run in source['compiler_runs']:
  result=run['result'];assert run['ASan_UBSan'] and result['status']=='PASS'
  assert result['admitted_front_cases']==3 and result['rejected_other_dimensions']==21 and result['atomic_negatives']==36
 for k in ['private_profile_read','private_tuning_read','pixels_read','calibration_remeasured','runtime_changed','installed','loaded','hardware']:assert not source[k]
 for k in ['installed','loaded','CAMSS_or_kernel_rebuilt','runtime_changed','hardware']:assert not build[k]
 previous=json.loads((R/'docs/FRONT-CCM-CONFIG-20261014.json').read_text())
 assert previous['status']=='PASS_SOURCE_AND_COMPILE_ONLY' and previous['candidate_unique_configuration_addresses_after']==111
 text=headers['sp11-front-measured-config.h'].read_text()
 prior=set(int(x,16) for x in re.findall(r'\{ (0x[0-9a-f]+)U,',text));assert len(prior)==24
 prior.update([0x3d60,0x4760,0x5460,0x5a60,0x4b68])
 for lo,hi in [(0x4b68,0x4b80),(0x3b68,0x3b98),(0x6168,0x61b0),(0x9c70,0x9c98),(0x9e70,0x9e98),(0x9864,0x9888),(0x9a64,0x9a88),(0x5868,0x5890)]:prior.update(range(lo,hi,4))
 new={0x9c68,0x9c6c,0x9e68,0x9e6c};assert len(prior)==111 and not (prior&new)
 result={'schema':'sp11-front-crop-qualification-v1','status':'PASS_SOURCE_AND_COMPILE_ONLY',
 'existing_coordinate_arithmetic_reused_unchanged':True,
 'source_acceptance':'native01','compile_acceptance':'native-compile01',
 'source':source,'build':build,
 'new_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file() and p.suffix in ['.h','.c','.py','.md']},
 'configuration_registers':[hex(x) for x in sorted(new)],
 'candidate_unique_configuration_addresses_before':len(prior),
 'candidate_unique_configuration_addresses_after':len(prior|new),
 'full_Gamma_CST_video_precision_bound':False,'candidate_leaves_are_not_a_complete_program':True,
 'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'next':'Reuse source core/Gamma/module inputs to finish full precision/startup around native lifetime; private-loader replacement and fresh physical/image parity remain'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/FRONT-CROP-CONFIG-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','candidate_unique_configuration_addresses_after','complete_startup','upstream_ready']}))
if __name__=='__main__':main()
