#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path

MAGIC=b'E3HPIX01'; VERSION=1; HEADER_BYTES=1024; ALIGN=64
TYPE_STARTUP_MAIN=1; TYPE_STARTUP_PAYLOAD=2; TYPE_STEADY_MAIN=3; TYPE_STEADY_MODULES=4; TYPE_STEADY_PAYLOAD=5
MODULES=['DEMUX_BLS','PDPC','LSC','WB','GIC','BPC_ABF','GTM','GAMMA','DSX']
REG_SLOT={
  0x3b70:(0,0),0x3b74:(0,1),
  0x3d58:(1,0),0x3d5c:(1,1),0x3d78:(1,2),0x3d7c:(1,3),0x3d80:(1,4),0x3d84:(1,5),
  0x4358:(2,0),0x435c:(2,1),0x456c:(3,0),0x4570:(3,1),0x4758:(4,0),0x475c:(4,1),
  0x4958:(5,0),0x495c:(5,1),0x5a58:(6,0),0x5a5c:(6,1),0x5f58:(7,0),0x5f5c:(7,1),
  0xa058:(8,0),0xa05c:(8,1),0xa258:(8,2),0xa25c:(8,3),
}
DMI_SOURCE=[
 # Surface GIC311 wire alias: 0x062e is the exact Windows DMI source byte offset; logical GIC output is at 0x18b8.
 ('PDPC0',0x0000,0x200),('LSC0',0x0400,0x374),('LSC1',0x0774,0x374),('LSC2',0x0ae8,0x374),
 ('GIC0',0x062e,0x200),('BPC_ABF0',0x1ab8,0x100),('GTM0',0x34cc,0x800),
 ('GAMMA0',0x3ccc,0x400),('GAMMA1',0x40cc,0x400),('GAMMA2',0x44cc,0x400),
 ('DSX0',0x4acc,0x300),('DSX1',0x4dcc,0x300),('DSX2',0x50cc,0x180),('DSX3',0x524c,0x180),
]

def sha(b): return hashlib.sha256(b).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def align(v): return (v+ALIGN-1)&~(ALIGN-1)
def load_py(path,name):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
 ap.add_argument('--output',type=Path,default=Path(__file__).with_name('E003H_PIX_ORACLE_CAPSULE_R6_MATCHED.bin'))
 ap.add_argument('--manifest',type=Path,default=Path(__file__).with_name('pix-oracle-capsule-r6-matched-manifest.json'))
 a=ap.parse_args(); root=a.root.resolve()
 e=root/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
 w=e/'windows-ife-cdm'
 own=json.loads((e/'rtcdm-startup-dynamic-ownership-oracle.json').read_text())
 corpus=json.loads((e/'rtcdm-corpus-materializer-oracle.json').read_text())
 prime=json.loads((e/'vfe1-epoch0-priming-replay-oracle.json').read_text())
 batch=json.loads((e/'vfe1-epoch0-cdm-batches-oracle.json').read_text())
 ext=load_py(e/'extract_vfe1_epoch0_cdm_batches.py','epoch0_extract_capsule')
 _,batches=ext.parse_log(e/'windows-vfe1-epoch0-cdm-batches/E003H_VFE1_EPOCH0_CDM_BATCHES_CLEAN_20260829.log')

 # Current 0020/0021 startup normalized inputs: zero only DMI addresses + period_cfg.
 dmi_by={i:[] for i in range(4)}
 for d in corpus['dmi_references']: dmi_by[int(d['packet'])].append(int(d['address_field_offset'],16))
 period={int(x['packet']):int(x['period_field_offset'],16) for x in own['refined_main_slots']}
 startup=[]
 for i,slot in enumerate(own['refined_main_slots']):
  b=bytearray((w/f'packet{i}-main-cdm.bin').read_bytes())
  for off in dmi_by[i]: b[off:off+4]=b'\0'*4
  b[period[i]:period[i]+4]=b'\0'*4
  if sha(b)!=slot['normalized_sha256']: die(f'startup normalized packet{i} hash drift')
  startup.append(bytes(b))

 payloads=[]
 for x in corpus['payload_catalog']:
  b=(w/'dmi-payloads'/f"{x['sha256']}.bin").read_bytes()
  if len(b)!=x['bytes'] or sha(b)!=x['sha256']: die('startup payload drift')
  payloads.append(b)
 if len(payloads)!=16: die('startup payload count')

 # Same-machine sample values for disposable oracle test only.
 startup_period=(int(own['refined_main_slots'][0]['period_initial'],16),int(own['refined_main_slots'][1]['period_initial'],16))
 pp=prime['replay']['packets']; priming_period=(int(pp[0]['replay_period_cfg'],16),int(pp[1]['replay_period_cfg'],16))
 if any(int(x['replay_period_cfg'],16)!=priming_period[1] for x in pp[1:]): die('priming two-value relation drift')

 # Request6 steady sample. Keep the proven request4 normalized template, including its per-stream
 # period_cfg +0x8c value, but source every caller-owned IQ register/DMI payload from the
 # exact request6 pair captured in a fresh Windows stream. Cross-stream normalization proves
 # that +0x948 is the only additional per-stream field omitted by the older same-boot oracle.
 v=next(x for x in batch['main_bl_variants'] if int(x['main_bytes'])==0x958)
 b4=next(x for x in batches[4:] if x['records'][1]['bytes']==0x958)
 old_raw=b4['records'][1]['data']; main=bytearray(old_raw)
 for x in v['normalized_holes']:
  off=int(x,16); main[off:off+4]=b'\0'*4
 if sha(main)!=v['normalized_sha256']: die('steady request4 template normalized hash drift')
 period_cfg=struct.unpack_from('<I',old_raw,0x948)[0]

 raw_dir=Path(__file__).with_name('oracle-request6-matched')
 req6_raw=(raw_dir/'E003H_REQ6_MAIN_0958_MATCHED_TRIGGER_20260901.bin').read_bytes()
 slot=(raw_dir/'E003H_REQ6_DMI_SLOT_MATCHED_TRIGGER_20260901.bin').read_bytes()
 if len(req6_raw)!=0x958 or len(slot)!=0x8000: die('request6 exact source size')
 if sha(req6_raw)!='2277aebae7559227b0ce745b7d73b464b57b4b5e62baf8033940ee7f7180e4b4': die('request6 main identity')
 if sha(slot)!='ff5f0f04bee8491c76451838743a28e3793ee5d2a0ecbff8f6589dca5c92f955': die('request6 DMI identity')
 # Prove request6 differs from the old template only in known IQ holes plus per-stream period_cfg.
 cross_old=bytearray(old_raw); cross_new=bytearray(req6_raw)
 for x in list(v['normalized_holes'])+['0x948']:
  off=int(x,16); cross_old[off:off+4]=b'\0'*4; cross_new[off:off+4]=b'\0'*4
 if cross_old!=cross_new: die('request6 matched cross-stream skeleton drift')
 matched_skeleton_sha256=sha(cross_new)

 values=[[0]*6 for _ in MODULES]; vmask=[0]*len(MODULES)
 for r in v['dynamic_register_fields']:
  off=int(r['field'],16); ro=int(r['register_offset'],16)
  if ro not in REG_SLOT: die(f'unmapped reg {ro:x}')
  mi,si=REG_SLOT[ro]; values[mi][si]=struct.unpack_from('<I',req6_raw,off)[0]; vmask[mi]|=1<<si
 steady_payload=[]
 for _,off,n in DMI_SOURCE: steady_payload.append(slot[off:off+n])
 pmask=[0]*len(MODULES)
 for mi,indices in {1:[0],2:[1,2,3],4:[4],5:[5],6:[6],7:[7,8,9],8:[10,11,12,13]}.items():
  for j,_ in enumerate(indices): pmask[mi]|=1<<j
 module_blob=bytearray()
 for i in range(len(MODULES)):
  module_blob += struct.pack('<BBH6I4x',vmask[i],pmask[i],0,*values[i])
 if len(module_blob)!=len(MODULES)*32: die('module blob size')

 sections=[]
 for i,b in enumerate(startup): sections.append((TYPE_STARTUP_MAIN,i,b))
 for i,b in enumerate(payloads): sections.append((TYPE_STARTUP_PAYLOAD,i,b))
 sections.append((TYPE_STEADY_MAIN,0,bytes(main)))
 sections.append((TYPE_STEADY_MODULES,0,bytes(module_blob)))
 for i,b in enumerate(steady_payload): sections.append((TYPE_STEADY_PAYLOAD,i,b))
 if len(sections)!=36: die('section count')

 hdr=bytearray(HEADER_BYTES)
 struct.pack_into('<8sIIIIIIIIIQIII',hdr,0,MAGIC,VERSION,HEADER_BYTES,0,len(sections),startup_period[0],startup_period[1],priming_period[0],priming_period[1],0x958,6,0,0,0)
 off=align(HEADER_BYTES); body=bytearray(); desc=[]
 for typ,idx,b in sections:
  target=off
  cur=HEADER_BYTES+len(body)
  if cur<target: body += b'\0'*(target-cur)
  body += b; desc.append((typ,idx,target,len(b),sha(b))); off=align(target+len(b))
 for i,(typ,idx,o,n,_) in enumerate(desc): struct.pack_into('<IIII',hdr,64+i*16,typ,idx,o,n)
 total=HEADER_BYTES+len(body); struct.pack_into('<I',hdr,16,total)
 capsule=bytes(hdr)+bytes(body)
 if len(capsule)!=total: die('total size mismatch')
 a.output.write_bytes(capsule)
 manifest={
  'schema':'sp11-e003h-pix-oracle-capsule-v1','accepted':True,'capsule_committed':False,
  'capsule':{'bytes':len(capsule),'sha256':sha(capsule),'magic':MAGIC.decode(),'version':VERSION,'header_bytes':HEADER_BYTES,'section_count':len(sections),'section_alignment':ALIGN},
  'period_cfg':{'startup':[f'0x{x:08x}' for x in startup_period],'priming':[f'0x{x:08x}' for x in priming_period],'mapping':'packet0=value0; packets1,2,3=value1','classification':'same-machine disposable oracle sample; not production formula'},
  'steady':{'variant':'0x958','source_batch':'exact-Windows-request6-matched-trigger-stream','normalized_main_sha256':v['normalized_sha256'],'request_id':6,'subrequest':0,'module_value_valid':[f'0x{x:02x}' for x in vmask],'module_payload_valid':[f'0x{x:02x}' for x in pmask]},
  'sections':[{'type':t,'index':i,'offset':f'0x{o:x}','bytes':n,'sha256':h} for t,i,o,n,h in desc],
  'source_oracles':{
   'startup_ownership_sha256':sha((e/'rtcdm-startup-dynamic-ownership-oracle.json').read_bytes()),
   'priming_replay_sha256':sha((e/'vfe1-epoch0-priming-replay-oracle.json').read_bytes()),
   'epoch0_batch_sha256':sha((e/'vfe1-epoch0-cdm-batches-oracle.json').read_bytes()),
   'steady_dmi_slot_sha256':sha(slot),'request6_raw_main_sha256':sha(req6_raw),'steady_period_cfg_same_stream':f'0x{period_cfg:08x}','cross_stream_skeleton_sha256':matched_skeleton_sha256},
  'policy':'Capsule contains same-machine proprietary oracle bytes and remains local/untracked. Git stores only builder/schema/hash manifest. Windows source allocation offsets are not encoded; section offsets are Linux capsule layout only.'}
 a.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print('PASS',a.output,len(capsule),sha(capsule))
 print('MANIFEST',a.manifest,sha(a.manifest.read_bytes()))
if __name__=='__main__': main()
