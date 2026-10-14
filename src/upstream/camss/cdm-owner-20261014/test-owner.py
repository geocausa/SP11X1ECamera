#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute complete owner C and actual backend bodies with retained MMIO adapter."""
from pathlib import Path
import re,sys,subprocess,json,hashlib,importlib.util,resource
# Per-process only: expected unsafe mutations must not leave core files.
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
Q=Path(__file__).resolve().parent;R=Q.parents[3];PREV=Q.with_name('cdm-submit-20261014')
S=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir()
spec=importlib.util.spec_from_file_location('prior',PREV/'test-submit.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
for p in S.glob('*.h'):
 (O/p.name).write_text(re.sub(r'^#include <linux/[^\n]*\n','',p.read_text(),flags=re.M))
prefix=(PREV/'test-submit-prefix.c.in').read_text()
start=prefix.index('struct camss_cdm21_power;');end=prefix.index('static void mutex_lock',start)
prefix=prefix[:start]+'''struct device {int marker;};struct clk_bulk_data {void *clk;};
typedef u64 dma_addr_t;typedef int irqreturn_t;
#include "camss-cdm-command.h"
'''+prefix[end:]
prefix=prefix.replace('v==1 && retains==1 && barriers==1','v==1 && model_program_retained() && barriers==1')
# Forward declaration before the imported MMIO adapter.
prefix=prefix.replace('static size_t offset','static bool model_program_retained(void);\nstatic size_t offset')
cd=(S/'camss-cdm-2-1.c').read_text()
defs='\n'.join(l for l in cd.splitlines() if l.startswith('#define CDM21_'))
funcs=['cdm21_mask_and_drain','cdm21_clear_status','cdm21_clear_old','cdm21_request_pause','cdm21_empty','cdm21_command_status','camss_cdm21_submit_owned']
backend='\n'.join(prior.function(cd,n) for n in funcs)
source=re.sub(r'^#include [^\n]*\n','',(S/'camss-cdm-command.c').read_text(),flags=re.M)
mutations={
 'drop_module_pin':source.replace('if (!try_module_get(THIS_MODULE)) {','if (false) {'),
 'admit_bad_dma_extent':source.replace('if (!program->dma || (program->dma & 3) ||\n\t    program->dma > 0xffffffffULL ||\n\t    capacity > 0x100000000ULL - program->dma) {','if (false) {').replace('ret = sp11_cdm21_command_validate(&program->command);','ret = 0;'),
 'free_retained':source.replace('if (program->retained || cdm->retained_command.cpu == program->command.cpu) {','if (false) {'),
 'lose_backend_identity_guard':source.replace('if (program->retained || cdm->retained_command.cpu == program->command.cpu) {','if (program->retained) {'),
 'forget_transfer':source.replace('program->retained = true;','program->retained = false;'),
 'allow_retry':source.replace('if (program->attempted || program->retained) {','if (false) {'),
 'leak_device_ref':source.replace('put_device(program->dma_dev);','/* mutation: leaked device reference */'),
 'detach_with_program':source.replace('if (power->programs || power->held || power->touched || power->fault ||','if (power->held || power->touched || power->fault ||'),
}
extra=(Q/'test-owner-adapter.c.in').read_text();tail=(Q/'test-owner-main.c.in').read_text()
runs=[]
for cc in ['gcc','clang']:
 for name,t in [('actual',source),*mutations.items()]:
  path=O/(cc+'-'+name+'.c');path.write_text(prefix+'\n'+extra+'\n'+defs+'\n'+backend+'\n'+t+'\n'+tail)
  exe=path.with_suffix('')
  p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),str(path),'-o',str(exe)],capture_output=True,text=True)
  if p.returncode:raise RuntimeError(cc+' '+name+' compile '+p.stderr)
  p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15)
  (O/(cc+'-'+name+'.log')).write_text(p.stdout+p.stderr)
  if name=='actual':
   if p.returncode:raise RuntimeError(cc+' actual '+p.stderr)
   runs.append({'compiler':cc,'result':json.loads(p.stdout),'ASan_UBSan':True,'actual_complete_owner_source':True,'actual_submission_backend_bodies':True})
  elif not p.returncode:raise RuntimeError('unsafe compiled mutation survived '+name)
result={'status':'PASS_ACTUAL_COHERENT_OWNER_AND_SUBMISSION_BODIES','runs':runs,
'compiled_mutations_rejected_each':list(mutations),'model_cleanup':'Fixture-only simulated reboot frees retained mock memory; no production exposed-free API, physical retirement or real IRQ/DMA proof.',
'source_sha256':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in ['camss-cdm-command.c','camss-cdm-command.h','camss-cdm-2-1.c','camss-cdm-power.h']},
'hardware_access':False}
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
