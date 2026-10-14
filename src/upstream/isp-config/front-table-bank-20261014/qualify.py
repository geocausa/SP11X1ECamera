#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,re
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-table-bank-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=json.loads((C/'native01/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 assert source['status']=='PASS_SOURCE_TABLE_BANK_FIELDS'
 assert source['original_source_calls']==50 and source['comparison_records']==12
 for k in ['complete_packers_and_builders_executed','original_PE_immutable','SP_callee_saved_restored',
 'input_and_object_metadata_checks','canaries_intact','LSC_bit13_source_counterexample_checked']:assert source[k]
 for k in ['arithmetic_or_branch_shims','constructors_or_serializer_executed','existing_table_policy_or_data_changed',
 'bank_scheduling_reimplemented','full_LSC_ABF_configuration_or_geometry_qualified','native_request_lifetime_integrated',
 'hardware_reset_or_reserved_bits_proven','private_profile_read','private_tuning_read','own_optical_arrays_or_pixels_read',
 'runtime_changed','installed','loaded','hardware']:assert not source[k]
 assert source['source_bank_field_bits']==1 and source['LSC_hardware_gain_lane_bits']==14 and source['own_LSC_prepared_policy_bits']==13
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY'
 assert not (build['warnings'] or build['errors'] or any(build['style'].values()))
 assert sha(Path(build['module_path']))==build['module_sha256']
 for k in ['installed','loaded','CAMSS_or_kernel_rebuilt','runtime_changed','hardware']:assert not build[k]
 headers={
 'sp11-front-table-bank.h':Q/'sp11-front-table-bank.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():assert sha(p)==source['header_pins'][n]==build['header_pins'][n]
 for n,h in source['prior_reference_pins'].items():assert sha(R/n)==h
 for run in source['compiler_runs']:
  x=run['result'];assert run['ASan_UBSan'] and x['status']=='PASS'
  assert x['source_comparisons']==12 and x['atomic_negatives']==2081
 assert len(source['compiled_mutations_rejected_each'])==5
 previous=json.loads((R/'docs/FRONT-TABLE-HANDOFF-20261014.json').read_text())
 assert previous['status']=='PASS_SOURCE_AND_COMPILE_ONLY' and previous['candidate_unique_configuration_addresses_after']==117
 text=headers['sp11-front-measured-config.h'].read_text()
 prior=set(int(x,16) for x in re.findall(r'\{ (0x[0-9a-f]+)U,',text));assert len(prior)==24
 prior.update([0x3d60,0x4760,0x5460,0x5a60,0x4b68,0x5f58,0x5f5c])
 for lo,hi in [(0x4b68,0x4b80),(0x3b68,0x3b98),(0x6168,0x61b0),(0x9c70,0x9c98),(0x9e70,0x9e98),
 (0x9864,0x9888),(0x9a64,0x9a88),(0x5868,0x5890),(0x9c68,0x9c70),(0x9e68,0x9e70)]:prior.update(range(lo,hi,4))
 assert len(prior)==117
 new={0x4358,0x435c,0x4958,0x495c};assert not new&prior
 result={'schema':'sp11-front-table-bank-qualification-v1','status':'PASS_SOURCE_AND_COMPILE_ONLY',
 'source_acceptance':'native01','compile_acceptance':'native-compile01',
 'source':source,'build':build,'new_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'prior_startup_and_steady_scheduling_reused_not_reimplemented':True,
 'new_configuration_words':4,'command_bytes':32,
 'candidate_unique_configuration_addresses_before':117,'candidate_unique_configuration_addresses_after':121,
 'module_activation_emitted':False,'complete_LSC_ABF_configuration':False,
 'complete_startup':False,'physical_precision_chain_qualified':False,
 'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'next':'Bind remaining13 LSC and23 ABF configuration words/module controls plus VFE core to own geometry/noise policy; integrate handoffs with native lifetime in isolated private-loader replacement, then hardware/image parity'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/FRONT-TABLE-BANK-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','candidate_unique_configuration_addresses_after','complete_startup','upstream_ready']}))
if __name__=='__main__':main()
