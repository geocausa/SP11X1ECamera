#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, struct
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CAP=HERE/'oracle-live-20260904-current-repair'
OUT=HERE/'atomic-runtime-capsules'
OUT.mkdir(exist_ok=True)

BASE={
 4: ROOT/'experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate/firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin',
 5: ROOT/'experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate/firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R5.bin',
 6: HERE/'E003H_PIX_ORACLE_CAPSULE_R6.bin',
}
BASE_SHA={
 4:'1d1b118796dea2e62910e48fff5c18a51cbc0d53c609229828db908000b96505',
 5:'5ffdec1d41416b02d12a6abc76936c72328f6298fd8c940f698c1f286b2b6d98',
 6:'f9b6b6bef1d13cafb27d4ff9af6f6d36abe6643aff512dcd108da62ef8300647',
}
STAGING_SHA={
 4:'1a085983c3e1b09249514e26a9f449deffd9af3c343a0ce12f3de24f5cba1e33',
 5:'09bec0160fd78bee6a7d23e5fe440b4ca4e6ea0ce51561865e6b9f19a511df7d',
 6:'be1ca980a7e486c1b245f226c1827d0eecefb14f5b065ad4845917a30989e218',
}
EXPECTED={
 4:{'bank':1,'lsc0':'eb41b13a2049ecfe835266fefedd2d41c3e15564a8826ee06437f48a533234e5','lsc1':'c140edeb7b40eaefa5f904116cc4ce25478494bc9508160742cdc18881bfc676','lsc2':'6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','gic':'f25ba0e9841133d7505cc3c34bef7c8a5b5c0e79f9f53b8163eb8a5d2ed63a94'},
 5:{'bank':0,'lsc0':'1033e0732a1f2edf2263351be7ad213a98864ba0b9feb0a1d2eb27fbcf31953c','lsc1':'eab65d435c04a768bc53009c0cfdf05055168213b50c83385459679dfc790590','lsc2':'6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','gic':'25882eeae1fe0a61a9f4feb08c2387d32f83c17b1592155995a6d730875ac86c'},
 6:{'bank':1,'lsc0':'94dda0dd0c221da88a1087b13305c1cbe440cd314b3f0f6e324504494aab758e','lsc1':'5322633904bc97e2d647cf27c9f4f21a92b532272d063a4175028b3a8ad90076','lsc2':'6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','gic':'fea286613a8dd7ad4445effa63479efef71fc52ce539220928e135a0894bdc44'},
}

def sha(b): return hashlib.sha256(b).hexdigest()
def need(v,m):
 if not v: raise RuntimeError(m)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
pack=load('lscpack',HERE/'prove-lsc-live-staging-pack.py')

def descriptors(b):
 need(b[:8]==b'E3HPIX01','capsule magic')
 n=struct.unpack_from('<I',b,20)[0]
 return [struct.unpack_from('<IIII',b,64+i*16) for i in range(n)]

def steady_request_id(b): return struct.unpack_from('<Q',b,44)[0]

def ranges(vals):
 if not vals:return []
 out=[]; a=p=vals[0]
 for x in vals[1:]:
  if x==p+1:p=x;continue
  out.append([a,p+1]);a=p=x
 out.append([a,p+1]);return out

manifest={'schema':'sp11-e003h-atomic-runtime-capsule-refresh-v1','accepted':True,'policy':'Only DMI payload sections LSC0/LSC1/LSC2 and deterministic Surface GIC alias are replaced. Main packet/register skeleton, startup, priming, all other IQ modules and bank selectors remain byte-identical to the accepted base capsules.','requests':{}}
for req in (4,5,6):
 base=BASE[req].read_bytes(); need(sha(base)==BASE_SHA[req],f'R{req} base SHA drift')
 need(steady_request_id(base)==req,f'R{req} header request id drift')
 ds=descriptors(base)
 mod=next(d for d in ds if d[0]==4 and d[1]==0)
 mb=base[mod[2]:mod[2]+mod[3]]
 # LSC module index2 and GIC module index4: first two values are bank selectors.
 lvals=struct.unpack_from('<6I',mb,2*32+4); gvals=struct.unpack_from('<6I',mb,4*32+4)
 need(lvals[0]==EXPECTED[req]['bank'] and lvals[1]==EXPECTED[req]['bank'],f'R{req} LSC bank drift')
 need(gvals[0]==EXPECTED[req]['bank'] and gvals[1]==EXPECTED[req]['bank'],f'R{req} GIC bank drift')
 st=(CAP/f'atomic-req{req}-lsc-staging.bin').read_bytes(); need(sha(st)==STAGING_SHA[req],f'R{req} staging SHA drift')
 geom,l0,l1,l2=pack.pack_live_staging(st); alias=(l0+l1)[0x22e:0x42e]
 repl={1:l0,2:l1,3:l2,4:alias}
 got={'bank':geom['bank'],'lsc0':sha(l0),'lsc1':sha(l1),'lsc2':sha(l2),'gic':sha(alias)}
 need(got==EXPECTED[req],f'R{req} fresh atomic wire mismatch {got}')
 out=bytearray(base); permitted=[]; old={}
 for idx,payload in repl.items():
  d=next(d for d in ds if d[0]==5 and d[1]==idx)
  need(d[3]==len(payload),f'R{req} type5/{idx} size mismatch')
  old[str(idx)]=sha(base[d[2]:d[2]+d[3]])
  out[d[2]:d[2]+d[3]]=payload; permitted.extend(range(d[2],d[2]+d[3]))
 changed=[i for i,(a,b) in enumerate(zip(base,out)) if a!=b]
 permit=set(permitted); need(all(i in permit for i in changed),f'R{req} changed byte outside adaptive DMI sections')
 # Header and all descriptors remain exactly unchanged.
 need(out[:1024]==base[:1024],f'R{req} header changed')
 op=OUT/f'E003H_PIX_ORACLE_CAPSULE_ATOMIC_R{req}.bin'; op.write_bytes(out)
 manifest['requests'][str(req)]={
  'base':str(BASE[req]),'base_sha256':BASE_SHA[req],'output':str(op),'output_sha256':sha(out),
  'staging_sha256':STAGING_SHA[req],'bank':geom['bank'],'wire':got,'replaced_type5_indices':{'1':'LSC0','2':'LSC1','3':'LSC2','4':'GIC_ALIAS'},
  'old_payload_sha256':old,'changed_bytes':len(changed),'changed_ranges':[[hex(a),hex(b)] for a,b in ranges(changed)],
  'header_byte_identical':True,'other_sections_byte_identical':True,
 }
mp=HERE/'atomic-runtime-capsules-manifest.json'; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(json.dumps(manifest,indent=2,sort_keys=True))
