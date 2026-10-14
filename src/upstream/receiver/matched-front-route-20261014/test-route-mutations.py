#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile actual-function unsafe route variants; require runtime refusal."""
from pathlib import Path
import json,subprocess,sys
C=Path(sys.argv[1]);O=C/'route-mutations01';O.mkdir(exist_ok=False)
variants=[
 ('old_csid0_allowlist',C/'route02/actual-route.c','csid->id != 1 || csiphy->id != 2','csid->id != 0 || csiphy->id != 2'),
 ('allow_all_csids',C/'route02/actual-route.c','csid->id != 1 || csiphy->id != 2','false || csiphy->id != 2'),
 ('allow_cross_vfe_route',C/'integration02/actual-body-test.c','pad->entity == &camss->csid[v].subdev.entity &&','true &&')]
r=[]
for name,p,old,new in variants:
 t=p.read_text();assert t.count(old)==1;f=O/(name+'.c');f.write_text(t.replace(old,new));exe=O/name
 args=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-I',str(Path(__file__).resolve().parent),str(f),'-o',str(exe)]
 x=subprocess.run(args,capture_output=True,text=True);(O/(name+'-compile.log')).write_text(x.stdout+x.stderr)
 if x.returncode:raise RuntimeError(x.stderr)
 x=subprocess.run([str(exe)],capture_output=True,text=True);(O/(name+'-run.log')).write_text(x.stdout+x.stderr)
 assert x.returncode!=0
 r.append(dict(name=name,compiled=True,rejected=True,returncode=x.returncode))
result=dict(status='PASS_THREE_COMPILED_UNSAFE_ROUTE_MUTATIONS_REJECTED',mutations=r,hardware_access=False)
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
