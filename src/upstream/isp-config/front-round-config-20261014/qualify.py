#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify source/build evidence and publish only derived, non-optical facts."""
from pathlib import Path
import hashlib,json,re
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-round-config-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=json.loads((C/'native05/RESULT.json').read_text())
 build=json.loads((C/'BUILD.json').read_text())
 assert source['status']=='PASS_REUSED_FULL_VIDEO_CONFIGURATION'
 assert source['source_cases']==110 and source['admitted_full_config_cases']==18
 assert source['original_PE_immutable'] and not source['arithmetic_or_branch_shims']
 assert source['SP_callee_saved_restored'] and source['canaries_intact']
 assert source['native_source_register_binding'] and not source['builder_addresses_substituted']
 assert source['compiler_excludes_all_module_control']
 assert not source['constructor_executed'] and not source['unsupported_source_output_widths_executed']
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY'
 assert build['errors']==build['warnings']==0 and not any(build['style'].values())
 assert sha(Path(build['module_path']))==build['module_sha256']
 headers={
 'sp11-front-round-config.h':Q/'sp11-front-round-config.h',
 'sp11-front-fields.h':R/'src/upstream/isp-config/sp11-front-fields.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():assert sha(p)==source['header_pins'][n]==build['header_pins'][n]
 for n,h in source['prior_reference_pins'].items():assert sha(R/n)==h
 for run in source['compiler_runs']:
  assert run['ASan_UBSan'] and run['result']['status']=='PASS'
  assert run['result']['native_full_vectors']==18 and run['result']['atomic_negatives']==164
 for key in ['private_profile_read','private_tuning_read','pixels_read','calibration_changed','runtime_changed','hardware']:
  assert not source[key]
 for key in ['installed','loaded','CAMSS_or_kernel_rebuilt','runtime_changed','hardware']:assert not build[key]
 measured=(R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h').read_text()
 prior=set(int(x,16) for x in re.findall(r'\{ (0x[0-9a-f]+)U,',measured))
 assert len(prior)==24
 prior.update([0x3d60,0x4760,0x5460,0x5a60,0x4b68])
 prior.update(range(0x4b68,0x4b80,4))
 prior.update(range(0x3b68,0x3b98,4))
 prior.update(range(0x6168,0x61b0,4))
 ledger=json.loads((R/'experiments/E004-front-ir-vd55g0/e011dj-selected-baseline-input-ledger/INPUT-LEDGER.json').read_text())
 assert not ledger['complete_deterministic_source_bootstrap_closed']
 assert not ledger['minimal_enabled_module_dependency_closure_proven']
 new=set(base+4*i for base in [0x9c70,0x9e70] for i in range(10))
 assert len(prior)==63 and len(new)==20 and not (prior & new)
 result={'schema':'sp11-front-round-configuration-qualification-v1','status':'PASS_SOURCE_AND_COMPILE_ONLY',
  'prior_implementations_reused_unchanged':True,'new_field_math':False,
  'source_acceptance':'native05','compile_acceptance':'native-compile02',
  'excluded_attempts':['native01/02 fixture omitted original builder object+40 store',
   'native03 attempted unsupported output declaration0 logging path outside bounded fixture',
   'native04 source PASS superseded after final header formatting'],
  'excluded_compile_attempts':['native-compile01 header alignment check only'],
  'source':source,'build':build,
  'new_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file() and p.suffix in ['.h','.c','.py','.md']},
  'configuration_registers':[hex(base+4*i) for base in [0x9c70,0x9e70] for i in range(10)],
  'candidate_unique_configuration_addresses_before':len(prior),
  'candidate_unique_configuration_addresses_after':len(prior|new),
  'candidate_leaves_are_not_a_precision_bound_complete_program':True,
  'retained_scaler_and_bootstrap_audit':{
   'MNDS_packer_already_exists_unchanged':True,
   'MNDS_source_fixture_is_rear4064x2286_to3840x2160_not_front_mode':True,
   'existing_full_bootstrap_ledger_claims_complete_independent_bootstrap':False,
   'prior_reference_pins':{
    'experiments/E004-front-ir-vd55g0/e006q-rear-mnds23-packer/camss-e006q-mnds23.inc':sha(R/'experiments/E004-front-ir-vd55g0/e006q-rear-mnds23-packer/camss-e006q-mnds23.inc'),
    'experiments/E004-front-ir-vd55g0/e011dj-selected-baseline-input-ledger/INPUT-LEDGER.json':sha(R/'experiments/E004-front-ir-vd55g0/e011dj-selected-baseline-input-ledger/INPUT-LEDGER.json')}
  },
  'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
  'next':'Bind original core/MNDS video precision to own CST/Gamma policy; reuse retained scaler and own CCM auxiliary fields before private-loader replacement and guarded hardware parity'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/FRONT-ROUND-CONFIG-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','prior_implementations_reused_unchanged','candidate_unique_configuration_addresses_after','complete_startup','upstream_ready']}))
if __name__=='__main__':main()
