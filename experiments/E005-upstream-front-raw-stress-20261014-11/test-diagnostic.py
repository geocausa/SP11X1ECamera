#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import subprocess,re,json,sys,hashlib
Q=Path(__file__).resolve().parent;O=Path(sys.argv[1]);O.mkdir(parents=True,exist_ok=False)
S=Q/'kmod/sp11_rdi_idle_probe.c';t=S.read_text()
def extract(name):
 a=t.index(('static int __init ' if name.endswith('_init') else 'static int ')+name+'(');b=t.index('{',a);i=b+1;depth=1
 while depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
test=(Q/'test-diagnostic.c.in').read_text().replace('/* ACTUAL_OBSERVER_FUNCTIONS */','\n'.join(extract(n) for n in ['read_snapshot','match_device','sp11_rdi_idle_probe_init']))
(O/'actual-observer.c').write_text(test);runs=[]
for cc in ['gcc','clang']:
 exe=O/cc
 p=subprocess.run([cc,'-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',str(O/'actual-observer.c'),'-o',str(exe)],capture_output=True,text=True)
 (O/(cc+'-compile.log')).write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stderr)
 p=subprocess.run([str(exe)],capture_output=True,text=True);(O/(cc+'-run.log')).write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(p.stderr)
 runs.append(dict(compiler=cc,output=p.stdout.strip()))
r=dict(status='PASS_ACTUAL_READ_ONLY_RDI_OBSERVER_MODEL',runs=runs,source_sha256=hashlib.sha256(S.read_bytes()).hexdigest(),hardware_access=False,scope='Actual observer bodies, deterministic adapters; no physical concurrency claim')
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
