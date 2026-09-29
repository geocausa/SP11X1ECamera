#!/usr/bin/env python3
"""Source-only BPC tuning authority; linked/aliased mode paths fail closed."""
from pathlib import Path
import hashlib,importlib.util,math,struct
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SHA="4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
ROOT_IDS=(0x1a,0xf0,0x100,0x113)
def decoder():
 s=importlib.util.spec_from_file_location("chromatix",REPO/"experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py")
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class Authority:
 def __init__(self,path):
  self.b=Path(path).read_bytes()
  if hashlib.sha256(self.b).hexdigest()!=SHA:raise ValueError("SP11 rear authority SHA mismatch")
  self.d=decoder();self.h=self.d.parse_header(self.b)
  self.symbols,_=self.d.parse_symbol_table(self.b,self.h["sections"][0],self.h["sections"][1])
  sec=self.h["sections"][2]
  if sec["size"]%20:raise ValueError("selector record width")
  self.nodes={}
  for offset in range(sec["offset"],sec["end"],20):
   sid,key,kind,parent,link=struct.unpack_from("<5I",self.b,offset)
   if sid in self.nodes:raise ValueError("selector ID collision")
   self.nodes[sid]={"id":sid,"key":(key&65535,key>>16),"kind":kind,"parent":parent,"link":link}
  self.branches={sid:n for sid,n in self.nodes.items() if n["kind"]==0}
  self.module_by_branch={}
  for sid in ROOT_IDS:
   r=self.symbols[sid]
   if r["type"]!="bpcabf41_ife_v2" or (r["version_major"],r["version_minor"])!=(4,1):
    raise ValueError("BPC root type/version")
   n=self.nodes[r["mode_symbol_id"]]
   if n["kind"]!=2 or n["parent"] not in self.branches:
    raise ValueError("BPC mode-node layout")
   if n["link"]!=0xffffffff:raise ValueError("aliased BPC authority")
   if n["parent"] in self.module_by_branch:raise ValueError("ambiguous BPC branch")
   self.module_by_branch[n["parent"]]=sid
 def resolve(self,modes):
  modes=tuple(tuple(x) for x in modes)
  if not modes or modes[0]!=(0,0) or len(modes)>16:
   raise ValueError("explicit Default-leading selector path required")
  if any(len(x)!=2 or not all(isinstance(i,int) and 0<=i<=65535 for i in x) for x in modes):
   raise ValueError("selector domain")
  if any(a[0]>=b[0] for a,b in zip(modes,modes[1:])):
   raise ValueError("ordered unique mode kinds required")
  roots=[n for n in self.branches.values() if n["key"]==(0,0)]
  if len(roots)!=1:raise ValueError("Default branch ambiguous")
  node=roots[0];selected=self.module_by_branch.get(node["id"])
  if selected is None:raise ValueError("Default BPC absent")
  for key in modes[1:]:
   children=[n for n in self.branches.values() if n["parent"]==node["id"] and n["key"]==key]
   if not children:break # Exact GetModule stops at the first unavailable deeper mode.
   if len(children)!=1:raise ValueError("ambiguous linked selector edge")
   node=children[0]
   if node["link"]!=0xffffffff:raise ValueError("linked branch needs separate source proof")
   module_nodes=[n for n in self.nodes.values() if n["parent"]==node["id"] and n["kind"]==2]
   if len(module_nodes)!=1 or module_nodes[0]["link"]!=0xffffffff:
    raise ValueError("aliased BPC mode path unsupported")
   selected=self.module_by_branch.get(node["id"],selected)
  return selected
 def leaves(self,root):
  if root not in ROOT_IDS:raise ValueError("unproven BPC root")
  r=self.symbols[root];raw=self.d.data_bytes(self.b,self.h["sections"][1],r)
  if len(raw)!=136:raise ValueError("serialized BPC root size")
  trigger=struct.unpack_from("<I",raw,len(raw)-4)[0]
  if self.symbols[trigger]["type"]!="mod_bpcabf41_trigger_data":raise ValueError("trigger type")
  leaves=tuple(range(trigger+4,trigger+15,2))
  for sid in leaves:
   if self.symbols[sid]["type"]!="region" or self.symbols[sid]["data_bytes"]!=428:
    raise ValueError("region inventory drift")
  return leaves
 def region(self,root,leaf):
  if leaf not in self.leaves(root):raise ValueError("leaf does not belong to root")
  return list(struct.unpack("<107f",self.d.data_bytes(self.b,self.h["sections"][1],self.symbols[leaf])))
 def anchors(self,root):
  self.leaves(root)
  raw=self.d.data_bytes(self.b,self.h["sections"][1],self.symbols[root])
  values=list(struct.unpack_from("<5f",raw,27*4))
  if any(not math.isfinite(x) or x<0 for x in values) or values[-1]<=0 or any(a>b for a,b in zip(values,values[1:])):
   raise ValueError("reserve anchors outside normalized domain")
  return values
 def equivalent(self,root,leaves):
  leaves=tuple(leaves)
  if not leaves:raise ValueError("empty equivalent region set")
  values=[self.region(root,sid) for sid in leaves]
  if any(x!=values[0] for x in values[1:]):raise ValueError("regions are not equivalent")
  return list(values[0])
