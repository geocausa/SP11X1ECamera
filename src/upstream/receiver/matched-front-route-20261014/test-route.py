#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import re,json,sys,subprocess,hashlib
Q=Path(__file__).resolve().parent;S=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir(parents=True,exist_ok=False)
p=S/'drivers/media/platform/qcom/camss/camss-csid.c';t=p.read_text()
a=t.index('static int csid_link_setup(');b=t.index('{',a);i=b+1;d=1
while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
test=(Q/'test-route.c.in').read_text().replace('/* ACTUAL_LINK_SETUP */',t[a:i]);(O/'actual-route.c').write_text(test)
runs=[]
for cc in ['gcc','clang']:
 exe=O/cc
 p1=subprocess.run([cc,'-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',str(O/'actual-route.c'),'-o',str(exe)],capture_output=True,text=True)
 (O/(cc+'-compile.log')).write_text(p1.stdout+p1.stderr)
 if p1.returncode:raise RuntimeError(p1.stderr)
 p1=subprocess.run([str(exe)],capture_output=True,text=True);(O/(cc+'-run.log')).write_text(p1.stdout+p1.stderr)
 if p1.returncode:raise RuntimeError(p1.stderr)
 runs.append(dict(compiler=cc,output=p1.stdout.strip()))
r=dict(status='PASS_ACTUAL_FRONT_CPHY_LINK_POLICY',runs=runs,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),hardware_access=False)
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
