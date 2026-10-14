#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute actual submission/MMIO/power-wrapper bodies, never camera hardware."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,tempfile,shutil
Q=Path(__file__).resolve().parent
def function(t,name):
 m=re.search(r'(?:static\s+)?(?:int|void|bool)\s+'+name+r'\s*\(',t)
 if not m:raise RuntimeError('function missing '+name)
 a=t.index('{',m.start());depth=1;b=a+1
 while depth:
  depth+=(t[b]=='{')-(t[b]=='}');b+=1
 return t[m.start():b]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
 S=Path(args.source);O=Path(args.out);O.mkdir()
 cd=(S/'camss-cdm-2-1.c').read_text()
 funcs=['cdm21_mask_and_drain','cdm21_clear_status','cdm21_clear_old','cdm21_request_pause','cdm21_empty','cdm21_command_status','camss_cdm21_submit_owned']
 body='\n'.join(function(cd,n) for n in funcs)
 defs='\n'.join(l for l in cd.splitlines() if l.startswith('#define CDM21_'))
 wrap=function((S/'camss-cdm-power.c').read_text(),'camss_cdm21_power_submit')
 for n in ['sp11-cdm.h','sp11-cdm21-state.h','sp11-cdm21-command.h']:shutil.copyfile(S/n,O/n)
 isp=Q.parents[1]/'isp-config'
 for p in isp.glob('sp11-*.h'):
  if not (O/p.name).exists():shutil.copyfile(p,O/p.name)
 prefix=(Q/'test-submit-prefix.c.in').read_text();tail=(Q/'test-submit-main.c.in').read_text()
 mutations={
  'skip_extent_check':body.replace('ret = sp11_cdm21_command_validate(&next);','ret = 0;'),
  'accept_inline_as_done':body.replace('return sp11_cdm21_command_status_valid(*seen) ? 0 : -EAGAIN;','return *seen ? 0 : -EAGAIN;').replace('if (!ret && !sp11_cdm21_command_status_valid(seen))','if (!ret && !seen)'),
  'ignore_late_error':body.replace('if (!ret && ((!i && (status[i] & ~6U)) || (i && status[i])))','if (false)'),
  'ignore_pending':body.replace('ret = cdm21_empty(cdm);','ret = 0;'),
  'drop_retention':body.replace('cdm->command_held = true;','cdm->command_held = false;'),
  'wrong_length':body.replace('sp11_cdm21_command_length(next.bytes)','(u32)next.bytes'),
 }
 runs=[]
 for cc in ['gcc','clang']:
  for name,b in [('actual',body),*mutations.items()]:
   src=O/(cc+'-'+name+'.c');src.write_text(prefix+'\n'+defs+'\n'+b+'\n'+wrap+'\n'+tail)
   exe=src.with_suffix('')
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),str(src),'-o',str(exe)],capture_output=True,text=True)
   if p.returncode:raise RuntimeError('compile '+name+' '+p.stderr)
   p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15)
   (O/(cc+'-'+name+'.log')).write_text(p.stdout+p.stderr)
   if name=='actual':
    if p.returncode:raise RuntimeError(cc+' actual body '+p.stderr)
    runs.append({'compiler':cc,'result':json.loads(p.stdout),'sanitizers':['ASan','UBSan'],'actual_source':True})
   elif not p.returncode:raise RuntimeError('unsafe compiled mutation survived '+name)
 result={'status':'PASS_ACTUAL_CDM21_SUBMISSION_BODIES','runs':runs,'mutations_rejected_each_compiler':list(mutations),'hardware':False,'source_sha256':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in ['camss-cdm-2-1.c','camss-cdm-power.c','sp11-cdm21-command.h']}}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
