#!/usr/bin/env python3
"""SP11-private source execution and tuning-selection validation; counts only."""
from pathlib import Path
import hashlib,importlib.util,json,random,re,struct,sys
import pefile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent
TUNE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
DLL=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
PRIVATE=HERE.parents[2].parent/"private"/"E011AC-20260929-2140A"
DLL_SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=load("authority",HERE/"authority.py");I=load("interpolation",HERE/"interpolate.py");P=load("producer",HERE/"producer.py")
def native():
 blob=DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==DLL_SHA
 pe=pefile.PE(data=blob);base=pe.OPTIONAL_HEADER.ImageBase
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,pe.get_memory_mapped_image())
 heap=0x70000000;stack=0x71000000;stop=heap+0xf000
 u.mem_map(heap,0x10000);u.mem_map(stack,0x10000)
 def hook(uc,address,size,data):
  word=struct.unpack("<I",uc.mem_read(address,4))[0]
  if word in (0xD503237F,0xD50323FF):uc.reg_write(UC_ARM64_REG_PC,address+4)
  elif word==0xD65F0FFF:uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 def run(lower,upper,ratio):
  u.mem_write(heap,struct.pack("<107f",*lower));u.mem_write(heap+0x1000,struct.pack("<107f",*upper));u.mem_write(heap+0x2000,b"\xa5"*428)
  u.reg_write(UC_ARM64_REG_SP,stack+0xf000);u.reg_write(UC_ARM64_REG_LR,stop)
  u.reg_write(UC_ARM64_REG_X0,heap);u.reg_write(UC_ARM64_REG_X1,heap if lower is upper else heap+0x1000);u.reg_write(UC_ARM64_REG_X2,heap+0x2000)
  u.reg_write(UC_ARM64_REG_S0,struct.unpack("<I",struct.pack("<f",ratio))[0])
  u.emu_start(base+0x94e570,stop,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==stop,"original callback failed to return"
  return u.reg_read(UC_ARM64_REG_X0),bytes(u.mem_read(heap+0x2000,428))
 return run
def main():
 t=A.Authority(TUNE);run=native();cases=[]
 for root in A.ROOT_IDS:
  leaves=t.leaves(root)
  for a,b in zip(leaves,leaves[1:]):
   for ratio in (0,.25,.5,.75,1):cases.append((t.region(root,a),t.region(root,b),ratio))
 rng=random.Random(0xE011AC)
 for n in range(128):
  cases.append(([I.f32(rng.uniform(-2500,2500)) for _ in range(107)],
                [I.f32(rng.uniform(-2500,2500)) for _ in range(107)],I.f32(rng.random())))
 a=[I.f32(x*.01) for x in range(107)];b=[I.f32(-x*.02) for x in range(107)]
 for ratio in (-1e-7,0,1e-7,1-1e-7,1,1+1e-7):cases.append((a,b,ratio))
 cases.append((a,a,2))
 matched=0
 for case_index,(a,b,r) in enumerate(cases):
  good,actual=run(a,b,r);assert good==1
  expected=struct.pack("<107f",*I.interpolate(a,b,r));assert actual==expected, str({"case":case_index,"ratio":r,"fields_different":[i for i in range(107) if actual[i*4:i*4+4]!=expected[i*4:i*4+4]]})
  matched+=1
 rejects=0
 # Distinct source pointers: the alias case intentionally ignores interval bounds.
 a=[I.f32(x*.01) for x in range(107)];b=[I.f32(-x*.02) for x in range(107)]
 for ratio in (-.1,1.1):
  good,actual=run(a,b,ratio);assert good==0 and actual==b"\xa5"*428
  try:I.interpolate(a,b,ratio)
  except ValueError:rejects+=1
  else:raise AssertionError("invalid ratio admitted")
 live_roots=[];reserve_matches=region_matches=0
 for n in range(1,4):
  c=PRIVATE/"capture";rootbytes=(c/f"COMMON{n:02}_ROOT.bin").read_bytes();root=struct.unpack_from("<I",rootbytes)[0];live_roots.append(root)
  assert len(rootbytes)==184
  reserve=(c/f"COMMON{n:02}_RESERVE.bin").read_bytes();assert len(reserve)==24 and reserve==rootbytes[0xa0:0xb8]
  anchors=list(struct.unpack_from("<5f",reserve,4));assert anchors==t.anchors(root);reserve_matches+=5
  region=list(struct.unpack("<107f",(c/f"COMMON{n:02}_REGION.bin").read_bytes()))
  compatible=[sid for sid in t.leaves(root) if t.region(root,sid)==region]
  assert compatible,"live region not in selected-root source inventory";region_matches+=107
 assert live_roots==[0x1a,0x100,0x100]
 mode_vectors=[]
 for n in (1,2):
  b=(PRIVATE/"capture"/f"SELECT{n:02}_MODES.bin").read_bytes();assert len(b)%8==0
  modes=[struct.unpack_from("<2I",b,o) for o in range(0,len(b),8)];mode_vectors.append(modes)
  assert t.resolve(modes)==live_roots[n-1],"source selector resolved wrong root"
 # Explicit leaf choices validate the producer API, not runtime interval policy.
 explicit_matches=0
 for n,root in enumerate(live_roots,1):
  raw=(PRIVATE/"capture"/f"COMMON{n:02}_REGION.bin").read_bytes()
  region=list(struct.unpack("<107f",raw))
  leaf=next(sid for sid in t.leaves(root) if t.region(root,sid)==region)
  result=P.produce(t,mode_vectors[0 if n==1 else 1],leaf,leaf,0)
  assert struct.pack("<107f",*result["region"])==raw
  assert len(result["registers"])==7
  explicit_matches+=107
 domain_rejects=0
 for call in (lambda:t.resolve([(1,1)]),lambda:t.resolve([(0,0),(2,2),(1,1)]),
              lambda:t.region(0x1a,t.leaves(0x100)[0]),lambda:t.leaves(0xdead),
              lambda:t.equivalent(0x100,t.leaves(0x100)),
              lambda:I.interpolate([0]*107,[0]*107,float("nan"))):
  try:call()
  except ValueError:domain_rejects+=1
  else:raise AssertionError("unsupported authority/domain admitted")
 cold=P.cold_seed(t);assert cold["root"]==live_roots[0]
 assert struct.pack("<107f",*cold["region"])==(PRIVATE/"capture"/"COMMON01_REGION.bin").read_bytes()
 report={"experiment":"E011AC","status":"TUNING_SELECTION_RESERVE_AND_BLEND_PASS",
         "native_interpolation_cases_exact":matched,"interpolated_field_matches":matched*107,
         "invalid_ratio_differential_rejects":rejects,"authority_domain_rejects":domain_rejects,
         "explicit_leaf_producer_region_field_matches":explicit_matches,"live_root_ids":[hex(x) for x in live_roots],
         "mode_vectors":mode_vectors,"mode_vectors_source_resolved":2,"serialized_runtime_anchor_matches":reserve_matches,
         "selected_root_live_region_field_matches":region_matches,"clean_cold_region_fields_exact":107,
         "runtime_trigger_interval_selection_proven":False,"complete_e008o_composition_closed":False,
         "native_rear_linux_runtime_allowed":False,"original_source_execution":"Unicorn arithmetic only",
         "raw_runtime_bytes_exported":False}
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
