#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Revalidate final source/module/model/replay pins; no hardware operations."""
from pathlib import Path
import json,hashlib,re,subprocess,datetime
Q=Path(__file__).resolve().parent;R=Q.parents[3]
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01'
C=B/'candidate-35/cdm-owner-qual01';S=C/'source'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads((Q/'manifest.json').read_text());P=Path(m['parent'])
 for n,h in m['parent_pins'].items():assert sha(P/n)==h
 for n,h in m['output_sha256'].items():assert sha(S/n)==h and sha(Q/Path(n).name)==h
 for n,h in m['independent_compiler_pins'].items():
  original=R/'src/upstream/isp-config'/n;assert sha(original)==h
  candidate=S/'drivers/media/platform/qcom/camss'/n
  assert re.sub(r'\s+','',candidate.read_text())==re.sub(r'\s+','',original.read_text())
 build=json.loads((C/'BUILD.json').read_text())
 assert build['status']=='PASS_CDM21_OWNER_CAMSS_MODULE_ARM64_W1_WERROR' and build['source_sha256']==m['output_sha256']
 a=build['artifacts']['camss'];assert sha(Path(a['module_path']))==a['sha256']
 binaries=[json.loads((C/n).read_text())['artifacts']['camss']['sha256'] for n in ['BUILD-attempt01.json','BUILD-attempt02.json','BUILD.json']]
 assert len(set(binaries))==1
 models=json.loads((C/'host05/RESULT.json').read_text());assert models['status']=='PASS_ACTUAL_COHERENT_OWNER_AND_SUBMISSION_BODIES'
 for n,h in models['source_sha256'].items():assert sha(S/'drivers/media/platform/qcom/camss'/n)==h
 style=[]
 for n in m['output_sha256']:
  if Path(n).suffix not in ['.h','.c']:continue
  p=subprocess.run(['perl',str(S/'scripts/checkpatch.pl'),'--no-tree','--file',str(S/n)],capture_output=True,text=True)
  (C/(Path(n).name+'-final-style.log')).write_text(p.stdout+p.stderr)
  assert not p.returncode and '0 errors, 0 warnings' in p.stdout
  style.append({'file':n,'errors':0,'warnings':0})
 for label,extra in [('standard',[]),('reviewed-code-style',['--no-signoff','--ignore','FILE_PATH_CHANGES'])]:
  p=subprocess.run(['perl',str(S/'scripts/checkpatch.pl'),'--show-types','--no-tree']+extra+[str(Q/'0001-cdm21-coherent-program-owner.patch')],capture_output=True,text=True)
  (C/(label+'-final-patch.log')).write_text(p.stdout+p.stderr)
  if extra:assert not p.returncode and '0 errors, 0 warnings' in p.stdout
  else:assert '1 errors, 1 warnings' in p.stdout and 'MISSING_SIGN_OFF' in p.stdout and 'FILE_PATH_CHANGES' in p.stdout
 replay=C/'replay01'
 if not replay.exists():
  p=subprocess.run(['python3',str(Q/'prepare.py'),str(replay)],capture_output=True,text=True)
  assert not p.returncode,p.stdout+p.stderr
 for n,h in m['output_sha256'].items():assert sha(replay/'source'/n)==h
 rel='drivers/media/platform/qcom/camss/'
 unchanged=['camss-cdm-2-1.c','camss-cdm-power.c','sp11-cdm.h','sp11-cdm21-state.h','sp11-cdm21-command.h','camss.c','camss-video.c','camss-vfe-680.c']
 assert all(sha(S/rel/n)==sha(P/rel/n) for n in unchanged)
 refs={}
 for name in ['camss_cdm21_program_create','camss_cdm21_program_submit','camss_cdm21_program_destroy_unused','camss_cdm21_power_detach_ready']:
  hits=[]
  for p in (S/rel).glob('*.[ch]'):
   text=re.sub(r'/\*.*?\*/|//[^\n]*','',p.read_text(),flags=re.S)
   if name in text:hits.append({'file':p.name,'count':text.count(name)})
  assert len(hits)==2 and sum(x['count'] for x in hits)==2
  refs[name]=hits
 result={'schema':'sp11-cdm21-coherent-owner-qualification-v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'PASS_DORMANT_TYPED_COHERENT_COMMAND_OWNER_SOURCE_ONLY',
 'prior_reuse_audit':'docs/UPSTREAM-COMMAND-OWNER-PRIOR-AUDIT-20261014.json',
 'candidate':m,'kernel_build':build,'actual_owner_and_submission_models':models,
 'compiler_helpers_whitespace_only_identical':True,'all_three_module_builds_byte_identical':binaries[0],
 'unchanged_prior_runtime_sources':{n:sha(S/rel/n) for n in unchanged},
 'fresh_zero_fuzz_patch_replay':str(replay),'style':style,'dormant_api_references':refs,
 'draft_patch_review':'One MISSING_SIGN_OFF error and FILE_PATH_CHANGES advisory remain. Existing CAMSS MAINTAINERS covers new files; reviewed code check ignores that advisory and signoff requirement only. No author signoff fabricated.',
 'attempt_history':['host01 fixture used incorrect geometry member names; corrected to retained header fields.',
 'host02 fixture kept a stale caller handle across simulated reboot; cleared fixture handle. No production behavior fix.',
 'host03/04 ownership suites passed. host05 recompiled final wrapped helper format with per-process core limit0 for intentional unsafe mutants.',
 'BUILD01/02/03 all pass and identical module bytes. Two copied helper headers required whitespace-only declaration/statement/line wrapping; original retained source unchanged. Draft description wrapping corrected.'],
 'validation_source_pins':{p.name:sha(p) for p in Q.iterdir() if p.is_file() and p.suffix in ['.py','.in']},
 'limits':['No module installation/load, physical allocation, register access, reboot or runtime parent call.',
 'Opaque typed compiler owner and refusal predicate are implemented; actual parent binding/resource routing and pre-detach exclusion are not wired.',
 'Platform remove is void and devres still releases IRQ/mapping/clock resources; get_device/module pins and a refusal predicate cannot replace that teardown architecture.',
 'Power/backend/clock handle storage must outlive the owner under parent exclusion. Refuse hardware admission until that is guaranteed.',
 'No exposed free/rewrite/retry/post-command reset or physical DMA-retirement authority. Holds remain pinned until reboot in the current design.',
 'Host locks, allocation, DMA, IRQ, time, device/module refs are models; no real concurrency/cache/IOMMU/AXI/pause/CDM proof.',
 'Minimum compiler1204-byte input geometry3840x2640 does not prove CFA/precision/bypass/optical IQ, sensor clock/control domains or complete PIX/CSID/BUS/params/stats/IPA startup.',
 'No proprietary startup/tuning/firmware payloads copied; full provenance/attribution/DCO/bindings/generic API and upstream review remain open.'],
 'installed':False,'hardware_qualified':False,'upstream_ready':False,
 'hardware_baseline':'docs/UPSTREAM-RAW-STRESS11-HARDWARE-20261014.json','hardware_source_candidate':33,
 'private_processed_runtime_consumers_remaining':2}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 (R/'docs/UPSTREAM-CDM21-COMMAND-OWNER-20261014.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'cases_per_compiler':models['runs'][0]['result']['cases'],'compiled_mutations_each':len(models['compiled_mutations_rejected_each']),'module_sha256':a['sha256'],'code_style_errors':0,'code_style_warnings':0,'parent_detach_wired':False,'upstream_ready':False}))
if __name__=='__main__':main()
