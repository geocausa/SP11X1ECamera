#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-table-handoff-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=json.loads((C/'native02/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 assert source['status']=='PASS_REUSED_FRONT_MEASURED_TABLE_HANDOFF' and source['source_cases']==38
 for k in ['original_PE_immutable','SP_callee_saved_restored','canaries_intact','inputs_immutable',
 'source_fixed_DMI_addresses_observed','source_word_to_byte_offsets_observed','ordinary_stripe_context']:assert source[k]
 for k in ['arithmetic_or_branch_shims','serializer_executed','constructor_executed','arithmetic_packers_executed',
 'addresses_substituted','optional_ABF_flag1_context_qualified','own_data_values_or_hashes_exported',
 'new_calibration','module_or_bank_commands_emitted','CPU_DMA_correspondence_proven','bank_config_integrated',
 'completion_lifetime_integrated','physical_channel_or_mesh_binding_proven','private_profile_read',
 'private_tuning_read','pixels_read','runtime_changed','installed','loaded','hardware']:assert not source[k]
 assert source['existing_own_measured_table_pairs_validated_each_compiler']==1
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY'
 assert not (build['warnings'] or build['errors'] or any(build['style'].values()))
 assert sha(Path(build['module_path']))==build['module_sha256']
 for k in ['installed','loaded','CAMSS_or_kernel_rebuilt','runtime_changed','hardware']:assert not build[k]
 headers={
 'sp11-front-table-handoff.h':Q/'sp11-front-table-handoff.h',
 'native-front-gamma.h':R/'src/native-rgb/native-front-gamma.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():assert sha(p)==source['header_pins'][n]==build['header_pins'][n]
 for n,h in source['prior_reference_pins'].items():assert sha(R/n)==h
 for run in source['compiler_runs']:
  x=run['result'];assert run['ASan_UBSan'] and x['status']=='PASS'
  assert x['admitted']==2050 and x['atomic_negatives']==3702 and x['existing_own_table_pairs']==1
 assert len(source['compiled_mutations_rejected_each'])==6
 previous=json.loads((R/'docs/FRONT-GAMMA-HANDOFF-20261014.json').read_text())
 assert previous['status']=='PASS_SOURCE_AND_COMPILE_ONLY' and previous['candidate_unique_configuration_addresses_after']==117
 result={'schema':'sp11-front-table-handoff-qualification-v1','status':'PASS_SOURCE_AND_COMPILE_ONLY',
 'existing_own_measured_LSC_ABF_data_and_generators_reused_unchanged':True,
 'source_acceptance':'native02','compile_acceptance':'native-compile02',
 'excluded_attempts':{'native01':'Source/host PASS, superseded only by final header style pin',
 'native-compile01':'Native compile PASS; one parameter-alignment style check corrected'},
 'source':source,'build':build,'new_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'prepared_table_bytes':{'LSC':2652,'ABF':256},'command_bytes':48,'DMI_transfers':4,
 'candidate_unique_configuration_addresses_before':117,'candidate_unique_configuration_addresses_after':117,
 'module_or_bank_commands_emitted':0,'full_LSC_ABF_configuration_qualified':False,
 'complete_startup':False,'physical_precision_chain_qualified':False,
 'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'next':'Reuse retained core/module source and full LSC/ABF configuration; bind own Gamma/LSC/ABF handoffs to native request/bank/DMA lifetime in fresh isolated private-loader replacement, then hardware/image parity'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/FRONT-TABLE-HANDOFF-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','DMI_transfers','complete_startup','upstream_ready']}))
if __name__=='__main__':main()
