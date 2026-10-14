#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Aggregate source-only startup qualification; preserve native calibration."""
from pathlib import Path
import datetime,hashlib,json,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3]
C=R.parents[1]/'02-kernel/front-channel-gain-20261014-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 native=json.loads((C/'native04/RESULT.json').read_text())
 build=json.loads((C/'BUILD.json').read_text())
 assert native['status']=='PASS_RETAINED_PRODUCERS_AND_NORMAL_SLOT_NATIVE_CONFIGURATION'
 assert native['native_cases']==927 and native['prior_producer_cases']==210
 assert native['original_executable_and_other_image_bytes_immutable']
 assert native['SP_callee_saved_restored'] and native['image_canaries_intact']
 assert native['nonzero_old_image_counterexample_checked']
 assert not native['constructor_executed'] and not native['packing_arithmetic_or_field_shims']
 assert all(x['result']['native_vectors']==927 and x['result']['prior_producer_vectors']==210 for x in native['compiler_runs'])
 assert len(native['compiled_mutations_rejected_each'])==5
 paths={
 'sp11-front-channel-gain.h':Q/'sp11-front-channel-gain.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 assert native['header_pins']==build['header_pins']
 for n,h in native['header_pins'].items():assert sha(paths[n])==h
 for n,h in native['prior_reference_pins'].items():assert sha(R/n)==h
 baseline=json.loads((R/'src/upstream/isp-config/measured-front-reuse-20261014/baseline-audit.json').read_text())
 for n,h in baseline['repository_pins'].items():assert sha(R/n)==h
 for n,h in baseline['native_source_pins'].items():assert sha(Path(baseline['native_stage'])/n)==h
 assert sha(Path(baseline['run93_stage'])/'run-93.json')==baseline['run93_config_pin']
 assert build['status']=='PASS_NATIVE_ABI_COMPILE_ONLY'
 assert build['warnings']==build['errors']==0 and not build['installed'] and not build['loaded']
 assert sha(Path(build['module_path']))==build['module_sha256']
 public=R.parents[1]/'02-kernel/upstream-public-vfe680-20261011-01/source/drivers/media/platform/qcom/camss/camss-vfe-680-pp-regs.h'
 assert sha(public)=='bce9607bac5b46ce907a1434b3a772c5c40b753b1c933db7d37822b9c26e020e'
 cp=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01/candidate-35/cdm-owner-qual01/source/scripts/checkpatch.pl'
 p=subprocess.run(['perl',str(cp),'--no-tree','--strict','--file',str(Q/'sp11-front-channel-gain.h')],capture_output=True,text=True)
 (C/'header-style.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0 and '0 errors, 0 warnings, 0 checks' in p.stdout,p.stdout
 measured_text=paths['sp11-front-measured-config.h'].read_text()
 measured=set(int(x,16) for x in __import__('re').findall(r'\{ (0x[0-9a-f]+)U,',measured_text))
 cold={0x3d60,0x4760,0x5460,0x5a60,0x4b68}
 bls=set(range(0x4b68,0x4b80,4));channel=set(range(0x3b68,0x3b98,4))
 previous=measured|cold|bls
 assert len(measured)==24 and len(previous)==33 and not previous&channel
 assert len(previous|channel)==45
 result={'schema':'sp11-front-channel-gain-validation-v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'project_parent':'4cb935ae7a59eb78a49c37ea8e109887f88ce87f',
 'status':'PASS_CHANNEL_GAIN_SOURCE_CONFIGURATION_PRIOR_PRODUCERS_REUSED',
 'native_source_bridge':native,'native_ABI_compile':build,
 'public_register_header_sha256':sha(public),
 'package_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file()},
 'header_style_errors':0,'header_style_warnings':0,'header_style_checks':0,
 'configuration_words':12,'command_bytes':56,'module_activation_commands':0,
 'prior_unique_configuration_candidates':33,'total_unique_configuration_candidates':45,
 'source_bayer2_normal_slot_pattern_qualified':True,'live_front_bayer_or_precision_observed':False,
 'prior_gain_producer_modified':False,'prior_native_bridge_modified':False,
 'calibration_remeasured':False,'private_profile_read':False,'private_tuning_read':False,
 'runtime_changed':False,'complete_startup':False,'private_runtime_consumers_remaining':2,'upstream_ready':False,
 'excluded_attempts':['missing parent output stage before any oracle work','native01 whole-image immutability assertion did not account for original writable data stores','native02 redundant conflicting host endian typedef','native03 verifier register enum arithmetic did not include actual X29; use explicit named registers in native04'],
 'limits':['Normal slots0/0, source Bayer2 and period0 only; native front Bayer0 enum equivalence unbound',
 'Public addresses are owned builder metadata; full native constructor binding not executed',
 'Neutral zero initial image/offsets and unity gains need original-domain physical parity',
 'E012k source producer checked only below native gain normalization boundary with zero channel BLS',
 'Separate DEMUX, other startup, private loader replacement and standard API/provenance review remain']}
 for path in [C/'QUALIFIED.json',R/'docs/FRONT-CHANNEL-GAIN-20261014.json']:
  path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','configuration_words','command_bytes','total_unique_configuration_candidates','runtime_changed','upstream_ready']}))
if __name__=='__main__':main()
