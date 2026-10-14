#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,re
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-gamma-handoff-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=json.loads((C/'native02/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 assert source['status']=='PASS_REUSED_GAMMA_BANK_AND_DMI_HANDOFF' and source['source_cases']==34
 for k in ['original_PE_immutable','SP_callee_saved_restored','canaries_intact','inputs_immutable',
 'source_fixed_addresses_observed','source_truncation_counterexamples_checked','nonzero_residual_counterexample_checked']:
  assert source[k]
 for k in ['arithmetic_or_branch_shims','serializer_executed','constructor_executed','addresses_substituted',
 'CPU_DMA_correspondence_proven','physical_channel_binding_proven','activation_after_DMI_hardware_order_proven',
 'request_bank_lifetime_integrated','private_profile_read','private_tuning_read','pixels_read','calibration_remeasured',
 'runtime_changed','installed','loaded','hardware']:assert not source[k]
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY' and not (build['warnings'] or build['errors'] or any(build['style'].values()))
 assert sha(Path(build['module_path']))==build['module_sha256']
 for k in ['installed','loaded','CAMSS_or_kernel_rebuilt','runtime_changed','hardware']:assert not build[k]
 headers={
 'sp11-front-gamma-handoff.h':Q/'sp11-front-gamma-handoff.h',
 'native-front-gamma.h':R/'src/native-rgb/native-front-gamma.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():assert sha(p)==source['header_pins'][n]==build['header_pins'][n]
 for n,h in source['prior_reference_pins'].items():assert sha(R/n)==h
 for run in source['compiler_runs']:
  x=run['result'];assert run['ASan_UBSan'] and x['status']=='PASS' and x['admitted']==2048 and x['atomic_negatives']==3151
 assert len(source['compiled_mutations_rejected_each'])==5
 previous=json.loads((R/'docs/FRONT-CROP-CONFIG-20261014.json').read_text())
 assert previous['status']=='PASS_SOURCE_AND_COMPILE_ONLY' and previous['candidate_unique_configuration_addresses_after']==115
 text=headers['sp11-front-measured-config.h'].read_text()
 prior=set(int(x,16) for x in re.findall(r'\{ (0x[0-9a-f]+)U,',text));assert len(prior)==24
 prior.update([0x3d60,0x4760,0x5460,0x5a60,0x4b68])
 for lo,hi in [(0x4b68,0x4b80),(0x3b68,0x3b98),(0x6168,0x61b0),(0x9c70,0x9c98),(0x9e70,0x9e98),
 (0x9864,0x9888),(0x9a64,0x9a88),(0x5868,0x5890),(0x9c68,0x9c70),(0x9e68,0x9e70)]:prior.update(range(lo,hi,4))
 assert len(prior)==115
 new={0x5f58,0x5f5c};assert not prior&new
 result={'schema':'sp11-front-gamma-handoff-qualification-v1','status':'PASS_SOURCE_AND_COMPILE_ONLY',
 'prior_Gamma_codec_and_CDM_serializers_reused_unchanged':True,
 'source_acceptance':'native02','compile_acceptance':'native-compile02',
 'excluded_attempts':{'native01':'Negative fixture changed base and endpoint; validator rejected continuity first, corrected fixture isolates endpoint overflow',
 'native-compile01':'Native compile passed; one constant-comparison style warning corrected'},
 'source':source,'build':build,'new_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'configuration_registers':[hex(x) for x in sorted(new)],'separate_activation_register':'0x5f60',
 'candidate_unique_configuration_addresses_before':115,'candidate_unique_configuration_addresses_after':117,
 'new_DMI_commands':3,'existing_Gamma_data_bytes':3072,'new_calibration':False,
 'complete_startup':False,'physical_precision_chain_qualified':False,
 'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'next':'Reuse core/module source and own LSC/ABF table handoffs to complete startup; bind Gamma to native request/bank/DMA ownership in fresh isolated loader replacement, then hardware/image parity'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/FRONT-GAMMA-HANDOFF-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','candidate_unique_configuration_addresses_after','complete_startup','upstream_ready']}))
if __name__=='__main__':main()
