#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,re
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-abf-config-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=json.loads((C/'native01/RESULT.json').read_text());build=json.loads((C/'BUILD.json').read_text())
 generated=json.loads((Q/'GENERATED.json').read_text())
 assert generated['status']=='PASS_REUSED_OWN_COMPLETE_ABF_MODULE' and generated['and_mask']==0 and generated['own_module_word']==257
 assert source['status']=='PASS_REUSED_COMPLETE_OWN_ABF_CONFIGURATION'
 assert source['original_source_calls']==18 and source['comparison_records']==6
 for k in ['fixed_source_registers_observed','original_PE_immutable','SP_callee_saved_restored',
 'inputs_and_object_metadata_checked','canaries_intact','activation_field_packer_executed',
 'existing_calibration_and_measured_compiler_reused_unchanged']:assert source[k]
 for k in ['addresses_substituted','arithmetic_or_branch_shims','constructors_or_serializer_executed',
 'configuration_arithmetic_packer_executed','bank_words_emitted','DMI_commands_emitted','new_calibration',
 'LSC_core_configuration_complete','physical_precision_or_ordering_qualified','native_lifetime_integrated',
 'private_profile_or_tuning_read','own_optical_arrays_or_pixels_read','runtime_changed','installed','loaded','hardware']:assert not source[k]
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY' and not (build['warnings'] or build['errors'] or any(build['style'].values()))
 assert sha(Path(build['module_path']))==build['module_sha256']
 for k in ['installed','loaded','CAMSS_or_kernel_rebuilt','runtime_changed','hardware']:assert not build[k]
 headers={
 'sp11-front-abf-config.h':Q/'sp11-front-abf-config.h',
 'sp11-front-abf-measured.h':Q/'sp11-front-abf-measured.h',
 'native-front-gamma.h':R/'src/native-rgb/native-front-gamma.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():assert sha(p)==source['header_pins'][n]==build['header_pins'][n]
 for n,h in source['prior_reference_pins'].items():assert sha(R/n)==h
 assert generated['source_sha256']==sha(R/generated['source'])
 for run in source['compiler_runs']:
  x=run['result'];assert run['ASan_UBSan'] and x['status']=='PASS'
  assert x['source_comparisons']==6 and x['atomic_negatives']==152 and x['own_configuration_words']==23
 assert len(source['compiled_mutations_rejected_each'])==5
 previous=json.loads((R/'docs/FRONT-TABLE-BANK-20261014.json').read_text())
 assert previous['status']=='PASS_SOURCE_AND_COMPILE_ONLY' and previous['candidate_unique_configuration_addresses_after']==121
 owned=set(int(r,16) for r in re.findall(r'\{ (0x[0-9a-f]+)U,',headers['sp11-front-measured-config.h'].read_text()))
 needed=set()
 for reg,count in [(0x4968,2),(0x4980,4),(0x49a0,8),(0x49c8,9)]:needed.update(reg+4*i for i in range(count))
 assert len(needed)==23 and needed==owned-{0x4b6c}
 result={'schema':'sp11-front-abf-complete-qualification-v1','status':'PASS_SOURCE_AND_COMPILE_ONLY',
 'source_acceptance':'native01','compile_acceptance':'native-compile01','source':source,'build':build,'generated':generated,
 'new_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'configuration_registers':[hex(x) for x in sorted(needed)],'complete_own_ABF_configuration_words':23,
 'own_measured_ABF_control_complete':True,'separate_module_activation_register':'0x4960',
 'candidate_unique_configuration_addresses_before':121,'candidate_unique_configuration_addresses_after':121,
 'new_configuration_addresses':0,'configuration_bytes':124,'separate_activation_bytes':12,
 'activation_after_owned_DMI_physical_ordering_qualified':False,'complete_startup':False,
 'LSC_core_configuration_complete':False,'physical_precision_chain_qualified':False,
 'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'prior_LSC_geometry_audit':{'file':'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/g-cleanroom-lsc-upstream/cleanroom-front-lsc.py',
 'FULL_W':4048,'FULL_H':3152,'CROP_X':104,'CROP_Y':496,'OUT_CELL_X_HALF':120,'OUT_CELL_Y_HALF':96,'OUT_Y_CENTER_ADJUST_HALF':36,
 'current_native_input':[3840,2160],'current_output':[2560,1440],
 'geometry_transfer_qualified':False,'optical_data_or_hashes_exported':False},
 'next':'Bind full13-word LSC geometry/module and VFE core/input to native mode; reuse complete own ABF/Gamma/CCM/geometry/table/bank leaves with native lifetime in isolated private-loader replacement, then physical/image parity'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/FRONT-ABF-CONFIG-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','complete_own_ABF_configuration_words','candidate_unique_configuration_addresses_after','complete_startup','upstream_ready']}))
if __name__=='__main__':main()
