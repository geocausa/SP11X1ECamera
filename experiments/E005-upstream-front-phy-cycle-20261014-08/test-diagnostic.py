#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import re,subprocess,json,sys
Q=Path(__file__).resolve().parent;O=Path(sys.argv[1]);O.mkdir(exist_ok=False)
s=(Q/'kmod/sp11_phy_owned_cycle.c').read_text()
s=re.sub(r'^#include[^\n]+\n','',s,flags=re.M)
(O/'actual-diagnostic-test.c').write_text((Q/'test-diagnostic.c.in').read_text().replace('/* ACTUAL_DIAGNOSTIC */',s))
runs=[]
for cc in ['gcc','clang']:
 exe=O/cc
 p=subprocess.run([cc,'-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-g',str(O/'actual-diagnostic-test.c'),'-o',str(exe)],capture_output=True,text=True)
 (O/(cc+'-compile.log')).write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
 p=subprocess.run([str(exe)],capture_output=True,text=True);(O/(cc+'-run.log')).write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
 runs.append({'compiler':cc,'output':p.stdout.strip()})
result={'status':'PASS_ACTUAL_DIAGNOSTIC_API_MODEL','runs':runs}
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
