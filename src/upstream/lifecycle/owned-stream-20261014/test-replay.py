#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify preparation templates and exact patch reproduce the built candidate."""
from pathlib import Path
import ast,hashlib,json,subprocess,tempfile,sys
Q=Path(__file__).resolve().parent
P,S,O=map(Path,sys.argv[1:4])
O.mkdir(parents=True,exist_ok=False)
names=['camss-video.c','camss-video.h','camss.h','camss.c','camss-video-lifecycle.h']
relative=Path('drivers/media/platform/qcom/camss')
tree=ast.parse((Q/'prepare.py').read_text())
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
def target(n,key):
 return isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id==key
a=next(i for i,n in enumerate(main.body) if target(n,'path'))
b=next(i for i,n in enumerate(main.body) if target(n,'names'))
result={'status':'PASS_EXACT_REPLAY','template_replay':{},'patch_replay':{}}
for mode in ['template','patch']:
 with tempfile.TemporaryDirectory(dir=O,prefix=mode+'-') as t:
  T=Path(t);d=T/relative;d.mkdir(parents=True)
  for n in names[:-1]:(d/n).write_bytes((P/relative/n).read_bytes())
  if mode=='template':
   def write(p,data):p.write_text(data)
   exec(compile(ast.Module(body=main.body[a:b],type_ignores=[]),'<prepare-replay>','exec'),{'S':T,'Q':Q,'write':write})
  else:
   p=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(Q/'lifecycle.patch')],cwd=T,capture_output=True,text=True)
   (O/'patch.log').write_text(p.stdout+p.stderr)
   if p.returncode:raise RuntimeError(p.stdout+p.stderr)
   if any(x in p.stdout.lower() for x in ['offset','fuzz']):raise RuntimeError(p.stdout)
  for n in names:
   if (d/n).read_bytes()!=(S/relative/n).read_bytes():raise RuntimeError((mode,n))
   result[mode+'_replay'][n]=hashlib.sha256((d/n).read_bytes()).hexdigest()
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
