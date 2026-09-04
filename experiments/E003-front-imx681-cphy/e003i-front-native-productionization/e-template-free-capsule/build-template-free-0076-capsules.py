#!/usr/bin/env python3
"""Build the accepted 0076 R4/R5/R6 capsules without a capsule template.

Inputs are individual normalized command/DMI source oracles plus the fresh atomic
LSC staging outputs. Existing 41088-byte capsules are never opened by this
builder. They are regression authorities only via their expected SHA256 values.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path

MAGIC=b'E3HPIX01'; VERSION=1; HEADER_BYTES=1024; ALIGN=64
TYPE_STARTUP_MAIN=1; TYPE_STARTUP_PAYLOAD=2; TYPE_STEADY_MAIN=3
TYPE_STEADY_MODULES=4; TYPE_STEADY_PAYLOAD=5
MODULES=['DEMUX_BLS','PDPC','LSC','WB','GIC','BPC_ABF','GTM','GAMMA','DSX']
REG_SLOT={
  0x3b70:(0,0),0x3b74:(0,1),
  0x3d58:(1,0),0x3d5c:(1,1),0x3d78:(1,2),0x3d7c:(1,3),0x3d80:(1,4),0x3d84:(1,5),
  0x4358:(2,0),0x435c:(2,1),0x456c:(3,0),0x4570:(3,1),0x4758:(4,0),0x475c:(4,1),
  0x4958:(5,0),0x495c:(5,1),0x5a58:(6,0),0x5a5c:(6,1),0x5f58:(7,0),0x5f5c:(7,1),
  0xa058:(8,0),0xa05c:(8,1),0xa258:(8,2),0xa25c:(8,3),
}
DMI_SOURCE=[
 ('PDPC0',0x0000,0x200),('LSC0',0x0400,0x374),('LSC1',0x0774,0x374),('LSC2',0x0ae8,0x374),
 ('GIC0',0x062e,0x200),('BPC_ABF0',0x1ab8,0x100),('GTM0',0x34cc,0x800),
 ('GAMMA0',0x3ccc,0x400),('GAMMA1',0x40cc,0x400),('GAMMA2',0x44cc,0x400),
 ('DSX0',0x4acc,0x300),('DSX1',0x4dcc,0x300),('DSX2',0x50cc,0x180),('DSX3',0x524c,0x180),
]
EXPECTED={
 4:'1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa',
 5:'8e447a662a47e47db7dd211d6a109d590531309f944e52b729a4351b5a00da11',
 6:'c88e7a75f228fac7b69a4a122fd618aa054bdbf98e83ff541be9c20177844583',
}
RAW_SHA={
 5:{'main':'01fd399d37aea3c5fda0b848a73763a2b40bff2e822f9425bf6570626dcf226f',
    'slot':'fb172ee2e4e407d823a255e84427e68f1c3ef6a985ba2e00f32c4c4dea4997f8'},
 6:{'main':'20c24428b61f59a28441228307556a18f9c350e3d1bcd4f74c95ef2ba31b57c3',
    'slot':'841d6f993acf392e8c4b0766ef0e55e3085ce96d2bef13c3830a221bb2223c8b'},
}
ATOMIC_STAGING_SHA={
 4:'1a085983c3e1b09249514e26a9f449deffd9af3c343a0ce12f3de24f5cba1e33',
 5:'09bec0160fd78bee6a7d23e5fe440b4ca4e6ea0ce51561865e6b9f19a511df7d',
 6:'be1ca980a7e486c1b245f226c1827d0eecefb14f5b065ad4845917a30989e218',
}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def need(v,msg):
    if not v: raise RuntimeError(msg)
def align(v):return (v+ALIGN-1)&~(ALIGN-1)
def load_py(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); assert spec.loader
    spec.loader.exec_module(mod); return mod

def static_recipe(root:Path):
    e=root/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
    w=e/'windows-ife-cdm'
    own=json.loads((e/'rtcdm-startup-dynamic-ownership-oracle.json').read_text())
    corpus=json.loads((e/'rtcdm-corpus-materializer-oracle.json').read_text())
    prime=json.loads((e/'vfe1-epoch0-priming-replay-oracle.json').read_text())
    batch=json.loads((e/'vfe1-epoch0-cdm-batches-oracle.json').read_text())
    ext=load_py(e/'extract_vfe1_epoch0_cdm_batches.py','e003i_epoch0_extract')
    _,batches=ext.parse_log(e/'windows-vfe1-epoch0-cdm-batches/E003H_VFE1_EPOCH0_CDM_BATCHES_CLEAN_20260829.log')

    dmi_by={i:[] for i in range(4)}
    for d in corpus['dmi_references']:
        dmi_by[int(d['packet'])].append(int(d['address_field_offset'],16))
    period={int(x['packet']):int(x['period_field_offset'],16) for x in own['refined_main_slots']}
    startup=[]
    for i,slot in enumerate(own['refined_main_slots']):
        b=bytearray((w/f'packet{i}-main-cdm.bin').read_bytes())
        for off in dmi_by[i]: b[off:off+4]=b'\0'*4
        b[period[i]:period[i]+4]=b'\0'*4
        need(sha(b)==slot['normalized_sha256'],f'startup packet{i} normalized identity drift')
        startup.append(bytes(b))
    payloads=[]
    for x in corpus['payload_catalog']:
        b=(w/'dmi-payloads'/f"{x['sha256']}.bin").read_bytes()
        need(len(b)==x['bytes'] and sha(b)==x['sha256'],'startup payload identity drift')
        payloads.append(b)
    need(len(payloads)==16,'startup payload count drift')
    startup_period=(int(own['refined_main_slots'][0]['period_initial'],16),
                    int(own['refined_main_slots'][1]['period_initial'],16))
    pp=prime['replay']['packets']
    priming_period=(int(pp[0]['replay_period_cfg'],16),int(pp[1]['replay_period_cfg'],16))
    need(all(int(x['replay_period_cfg'],16)==priming_period[1] for x in pp[1:]),'priming period relation drift')

    variant=next(x for x in batch['main_bl_variants'] if int(x['main_bytes'])==0x958)
    b4=next(x for x in batches[4:] if x['records'][1]['bytes']==0x958)
    raw4=b4['records'][1]['data']
    main=bytearray(raw4)
    for x in variant['normalized_holes']:
        off=int(x,16); main[off:off+4]=b'\0'*4
    need(sha(main)==variant['normalized_sha256'],'steady normalized main identity drift')
    slot4=(e/'windows-vfe1-epoch0-dmi-payloads/E003H_DMI_SLOT4.bin').read_bytes()
    need(len(slot4)==0x8000,'R4 DMI slot size drift')
    return e,variant,bytes(main),raw4,slot4,startup,payloads,startup_period,priming_period

def raw_request(root:Path, req:int, raw4:bytes, slot4:bytes):
    if req==4:return raw4,slot4,'request4 accepted batch/DMI slot4'
    if req==5:
        base=root/'experiments/E003-front-imx681-cphy/e003h-request5-exact-oracle-0070-static/windows-oracle-raw'
        main=(base/'E003H_REQ5_MAIN_0958_EXACT_20260901.bin').read_bytes()
        slot=(base/'E003H_REQ5_DMI_SLOT_EXACT_20260901.bin').read_bytes()
    elif req==6:
        base=root/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/oracle-request6'
        main=(base/'E003H_REQ6_MAIN_0958_EXACT_20260901.bin').read_bytes()
        slot=(base/'E003H_REQ6_DMI_SLOT_EXACT_20260901.bin').read_bytes()
    else:raise ValueError(req)
    need(len(main)==0x958 and len(slot)==0x8000,f'R{req} raw size drift')
    need(sha(main)==RAW_SHA[req]['main'] and sha(slot)==RAW_SHA[req]['slot'],f'R{req} raw identity drift')
    return main,slot,f'request{req} exact Windows raw main/DMI pair'

def atomic_lsc(root:Path,req:int,packer):
    here=root/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
    p=here/'oracle-live-20260904-current-repair'/f'atomic-req{req}-lsc-staging.bin'
    b=p.read_bytes(); need(sha(b)==ATOMIC_STAGING_SHA[req],f'R{req} atomic staging identity drift')
    geom,l0,l1,l2=packer.pack_live_staging(b)
    alias=(l0+l1)[0x22e:0x42e]
    need(len(l0)==len(l1)==len(l2)==0x374 and len(alias)==0x200,'atomic LSC wire shape drift')
    return geom,[l0,l1,l2,alias]

def request_state(root:Path,req:int,variant,raw4,slot4,packer):
    raw,slot,source=raw_request(root,req,raw4,slot4)
    values=[[0]*6 for _ in MODULES]; vmask=[0]*len(MODULES)
    for r in variant['dynamic_register_fields']:
        off=int(r['field'],16); ro=int(r['register_offset'],16)
        mi,si=REG_SLOT[ro]; values[mi][si]=struct.unpack_from('<I',raw,off)[0]; vmask[mi]|=1<<si
    payload=[slot[o:o+n] for _,o,n in DMI_SOURCE]
    geom,lsc=atomic_lsc(root,req,packer)
    # 0076 compatibility refresh: LSC0/1/2 and deterministic GIC alias only.
    payload[1],payload[2],payload[3],payload[4]=lsc
    pmask=[0]*len(MODULES)
    for mi,indices in {1:[0],2:[1,2,3],4:[4],5:[5],6:[6],7:[7,8,9],8:[10,11,12,13]}.items():
        for j,_ in enumerate(indices):pmask[mi]|=1<<j
    module=bytearray()
    for i in range(len(MODULES)):
        module += struct.pack('<BBH6I4x',vmask[i],pmask[i],0,*values[i])
    need(len(module)==0x120,'module state size drift')
    return {'module':bytes(module),'payload':payload,'source':source,'geometry':geom,
            'values':values,'vmask':vmask,'pmask':pmask}

def compose(req:int,main:bytes,startup,payloads,startup_period,priming_period,state):
    sections=[]
    for i,b in enumerate(startup):sections.append((TYPE_STARTUP_MAIN,i,b))
    for i,b in enumerate(payloads):sections.append((TYPE_STARTUP_PAYLOAD,i,b))
    sections.append((TYPE_STEADY_MAIN,0,main))
    sections.append((TYPE_STEADY_MODULES,0,state['module']))
    for i,b in enumerate(state['payload']):sections.append((TYPE_STEADY_PAYLOAD,i,b))
    need(len(sections)==36,'section count drift')
    hdr=bytearray(HEADER_BYTES)
    struct.pack_into('<8sIIIIIIIIIQIII',hdr,0,MAGIC,VERSION,HEADER_BYTES,0,len(sections),
                     startup_period[0],startup_period[1],priming_period[0],priming_period[1],0x958,req,0,0,0)
    off=align(HEADER_BYTES); body=bytearray(); desc=[]
    for typ,idx,b in sections:
        target=off; cur=HEADER_BYTES+len(body)
        if cur<target:body+=b'\0'*(target-cur)
        body+=b;desc.append((typ,idx,target,len(b),sha(b)));off=align(target+len(b))
    for i,(typ,idx,o,n,_) in enumerate(desc):struct.pack_into('<IIII',hdr,64+i*16,typ,idx,o,n)
    total=HEADER_BYTES+len(body);struct.pack_into('<I',hdr,16,total)
    cap=bytes(hdr)+bytes(body);need(len(cap)==41088,'capsule byte size drift')
    return cap,desc

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[4])
    ap.add_argument('--output-dir',type=Path,default=Path('/tmp/e003i-template-free-0076'))
    ap.add_argument('--manifest',type=Path)
    a=ap.parse_args();root=a.root.resolve();a.output_dir.mkdir(parents=True,exist_ok=True)
    prod=root/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
    packer=load_py(prod/'prove-lsc-live-staging-pack.py','e003i_lsc_packer')
    e,variant,main,raw4,slot4,startup,payloads,sp,pp=static_recipe(root)
    manifest={'schema':'sp11-e003i-template-free-0076-composer-v1','accepted':True,
      'capsule_template_reads':0,'capsule_bytes':41088,
      'classification':'0076 compatibility composer from individual normalized command/DMI state; not yet live 3A producer',
      'requests':{},'safety':{'offline_only':True,'linux_camera_runtime':False}}
    for req in (4,5,6):
        state=request_state(root,req,variant,raw4,slot4,packer)
        cap,desc=compose(req,main,startup,payloads,sp,pp,state)
        got=sha(cap);need(got==EXPECTED[req],f'R{req} template-free capsule mismatch {got}')
        op=a.output_dir/f'E003I_TEMPLATE_FREE_R{req}.bin';op.write_bytes(cap)
        manifest['requests'][str(req)]={
          'output':str(op),'sha256':got,'expected_0076_sha256':EXPECTED[req],
          'byte_exact_0076':True,'module_source':state['source'],
          'atomic_lsc_geometry':state['geometry'],
          'section_sha256':[{'type':t,'index':i,'bytes':n,'sha256':h} for t,i,o,n,h in desc]}
        print(f'R{req} PASS {len(cap)} {got}')
    mp=a.manifest or a.output_dir/'MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('TEMPLATE_FREE_0076=PASS')
    print('MANIFEST',mp)
if __name__=='__main__':main()
