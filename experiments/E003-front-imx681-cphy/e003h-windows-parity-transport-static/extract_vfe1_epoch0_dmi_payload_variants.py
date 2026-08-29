#!/usr/bin/env python3
import argparse, hashlib, json, re, struct
from collections import defaultdict
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

DRIVER_SHA = '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c'
DRIVER_BYTES = 376560
LOG_SHA = 'f44d09f8669576fe868a51d2b410c443dd863c8d00b7ab53ad1375b3b4acf3b0'
LOG_BYTES = 8868
BLOBS = {
    'ring_p37': ('6708575f409829b0df14cc4ea41a7ce60fad72249b7d7142aa0436de2cd5dc10', 0x78000),
    'slot_958_a': ('6460f831e92acc3f40d12a291600cc6bf0b50ed99212d4230e88058e813b2374', 0x8000),
    'slot_958_b': ('ae190b55035b991627f94dbd92f439f765d540485f4ef48856cb282f2309c3bf', 0x8000),
    'slot_5a4_a': ('3216624294597cc95e767fdd01bdf7195f07fe6bd375821bc40b079d4e8dd20e', 0x8000),
    'slot_5a4_b': ('c121d6213129953fd13051b1b912adb3bbda649a72023391f75a2e2582d5f9b1', 0x8000),
}
# Same 0x8000 DMI source-slot layout already mechanically established by the
# initial Windows patch/DMI oracle. The steady-state ring uses the same layout.
SOURCE = {
    '3d08/1': (0x0000, 0x200),
    '4308/1': (0x0400, 0x374),
    '4308/2': (0x0774, 0x374),
    '4308/3': (0x0ae8, 0x374),
    '4708/1': (0x062e, 0x200),
    '4908/1': (0x1ab8, 0x100),
    '5a08/1': (0x34cc, 0x800),
    '5f08/1': (0x3ccc, 0x400),
    '5f08/2': (0x40cc, 0x400),
    '5f08/3': (0x44cc, 0x400),
    'a008/1': (0x4acc, 0x300),
    'a008/2': (0x4dcc, 0x300),
    'a208/1': (0x50cc, 0x180),
    'a208/2': (0x524c, 0x180),
}
# P37's 15-slot circular source ring. The live log supplies P23..P37's packet
# variant sequence; the ring capture at P37 mechanically resolves this wrapped
# ordering by the frame-varying 0x4308 selector-1/2 payloads.
RING_MAP = [
    ('P2d','868'), ('P2e','868'), ('P2f','868'), ('P30','868'),
    ('P31','6b8'), ('P32','83c'), ('P33','6b8'), ('P34','868'),
    ('P35','6b8'), ('P36','868'), ('P37','6b8'), ('P29','868'),
    ('P2a','868'), ('P2b','868'), ('P2c','868'),
]
SINGLE = [
    ('958A','958','slot_958_a'), ('958B','958','slot_958_b'),
    ('5a4A','5a4','slot_5a4_a'), ('5a4B','5a4','slot_5a4_b'),
]
EXPECTED_LIVE = [
    ('23','6b8','8'), ('24','83c','c'), ('25','5a4','2'), ('26','958','e'),
    ('27','6b8','8'), ('28','958','e'), ('29','868','c'), ('2a','868','c'),
    ('2b','868','c'), ('2c','868','c'), ('2d','868','c'), ('2e','868','c'),
    ('2f','868','c'), ('30','868','c'), ('31','6b8','8'), ('32','83c','c'),
    ('33','6b8','8'), ('34','868','c'), ('35','6b8','8'), ('36','868','c'),
    ('37','6b8','8'),
]

def die(s): raise SystemExit('FAIL: '+s)
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())

def pe_text(data):
    pe=struct.unpack_from('<I',data,0x3c)[0]; n=struct.unpack_from('<H',data,pe+6)[0]
    opt=struct.unpack_from('<H',data,pe+20)[0]; sh=pe+24+opt
    for i in range(n):
        o=sh+i*40; name=data[o:o+8].rstrip(b'\0').decode('ascii',errors='ignore')
        vs,va,rs,raw=struct.unpack_from('<IIII',data,o+8)
        if name=='.text': return va,raw,rs
    die('.text missing')

def verify_driver(path):
    data=Path(path).read_bytes()
    if len(data)!=DRIVER_BYTES or sha_bytes(data)!=DRIVER_SHA: die('driver identity drift')
    va,raw,rs=pe_text(data); md=Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN); md.skipdata=True
    ins={x.address-0x140000000:(x.mnemonic,x.op_str) for x in md.disasm(data[raw:raw+rs],0x140000000+va) if x.mnemonic!='.byte'}
    anchors={
        0x269ec:('mov','x0, x22'), 0x269f0:('bl','#0x140028080'),
        0x26a00:('mov','x1, x22'), 0x26a08:('bl','#0x140028238'),
        0x26a24:('str','w2, [x20, #0x33d4]'), 0x26a48:('mov','x0, x22'),
        0x26a4c:('bl','#0x1400267d0'), 0x26a60:('mov','x1, x22'),
        0x26a68:('bl','#0x140028238'), 0x26a94:('bl','#0x1400274c8'),
        0x26b94:('ldr','w10, [x22, #0x8c]'), 0x26bb8:('cmp','w10, #0xc'),
        0x26bc4:('add','x1, x22, #0x74'), 0x26bd0:('bl','#0x140027920'),
    }
    got={}
    for r,(mn,frag) in anchors.items():
        x=ins.get(r)
        if not x or x[0]!=mn or frag not in x[1]: die(f'KMD anchor drift at 0x{r:x}: {x}')
        got[f'0x{r:x}']=f'{x[0]} {x[1]}'
    return got

def variant_identities(batch_oracle):
    out={}
    for v in batch_oracle['main_bl_variants']:
        key=f"{v['main_bytes']:x}"
        ids=[]
        for d in v['dmi_shape']:
            ident=f"{int(d['dmi_register_offset'],16):x}/{d['selector']}"
            ids.append(ident)
            if ident not in SOURCE: die('unknown source identity '+ident)
            if SOURCE[ident][1] != d['payload_bytes']: die('payload size drift '+ident)
        out[key]=ids
    expected={'958':14,'868':12,'83c':12,'6b8':8,'5a4':2}
    if {k:len(v) for k,v in out.items()}!=expected: die('variant DMI topology drift')
    return out

def sample(label,variant,blob,ids):
    rows=[]
    for ident in ids[variant]:
        off,n=SOURCE[ident]
        rows.append({'identity':ident,'bytes':n,'sha256':sha_bytes(blob[off:off+n])})
    return {'label':label,'variant':variant,'slot_sha256':sha_bytes(blob),'payloads':rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--driver',type=Path,required=True); ap.add_argument('--live-log',type=Path,required=True)
    ap.add_argument('--batch-oracle',type=Path,required=True)
    for k in BLOBS: ap.add_argument('--'+k.replace('_','-'),dest=k,type=Path,required=True)
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(); anchors=verify_driver(a.driver)
    logb=a.live_log.read_bytes()
    if len(logb)!=LOG_BYTES or sha_bytes(logb)!=LOG_SHA: die('live log identity drift')
    log=logb.decode('utf-16')
    live=re.findall(r'^P=([0-9a-f]+) U=([0-9a-f]+) N=([0-9a-f]+)\r?$',log,re.M|re.I)
    if live[:len(EXPECTED_LIVE)]!=EXPECTED_LIVE: die('live packet/variant sequence drift')
    for needle in ('P=57 U=5a4 N=2','P=4 U=958 N=e','P=38 U=5a4 N=2'):
        if needle not in log: die('missing targeted slot capture '+needle)
    bo=json.loads(a.batch_oracle.read_text())
    if not bo.get('accepted') or bo['capture']['steady_state_batches']!=175: die('0024 batch oracle drift')
    ids=variant_identities(bo)
    blobs={}
    evidence={}
    for k,(h,n) in BLOBS.items():
        p=getattr(a,k); b=p.read_bytes()
        if len(b)!=n or sha_bytes(b)!=h: die(k+' identity drift')
        blobs[k]=b; evidence[k]={'bytes':len(b),'sha256':sha_bytes(b)}
    samples=[]
    ring=blobs['ring_p37']
    for i,(label,var) in enumerate(RING_MAP): samples.append(sample(label,var,ring[i*0x8000:(i+1)*0x8000],ids))
    for label,var,k in SINGLE: samples.append(sample(label,var,blobs[k],ids))
    byvar=defaultdict(list); allid=defaultdict(list)
    for s in samples:
        byvar[s['variant']].append(s)
        for p in s['payloads']:
            allid[p['identity']].append((s['variant'],s['label'],p['sha256']))
    variants={}
    for var in ('958','868','83c','6b8','5a4'):
        ss=byvar[var]; rows=[]
        for ident in ids[var]:
            hs=[p['sha256'] for s in ss for p in s['payloads'] if p['identity']==ident]
            u=sorted(set(hs)); n=len(hs)
            status='single_sample' if n==1 else ('observed_invariant' if len(u)==1 else 'frame_varying')
            rows.append({'identity':ident,'bytes':SOURCE[ident][1],'sample_count':n,'unique_payloads':len(u),'status':status,'sha256':u})
        variants[var]={'sample_count':len(ss),'samples':[s['label'] for s in ss],'dmi_identities':rows}
    global_rows=[]
    for ident,rows in sorted(allid.items()):
        hs=sorted(set(h for _,_,h in rows))
        global_rows.append({'identity':ident,'bytes':SOURCE[ident][1],'sample_count':len(rows),'unique_payloads':len(hs),
                            'cross_variant_status':'observed_invariant' if len(hs)==1 else 'frame_or_variant_varying','sha256':hs})
    out={
      'schema':'sp11-e003h-vfe1-epoch0-dmi-payload-variants-v1','accepted':True,
      'policy':'same-machine Windows is behavioral oracle; raw DMI payload bytes remain local and untracked',
      'driver':{'bytes':DRIVER_BYTES,'sha256':DRIVER_SHA,'kmd_input_driven_anchors':anchors},
      'live_log':{'bytes':len(logb),'sha256':sha_bytes(logb),'packet_variant_sequence':[{'packet':'0x'+p,'main_bytes':'0x'+u,'dmi_count':int(n,16)} for p,u,n in EXPECTED_LIVE]},
      'local_payload_evidence':evidence,
      'windows_source_layout':{'slot_bytes':0x8000,'ring_slots_observed':15,'ring_bytes_observed':0x78000,
          'interpretation':'Windows source-ring allocation observation only; Linux must not freeze this ring geometry'},
      'variants':variants,'payload_identities':global_rows,
      'kmd_variant_ownership':{
        'ife_process_iq_packet_rva':'0x26838',
        'rule':'main-BL shape is derived from the incoming IQ packet/resource records and changed group masks; qccamisp8380 KMD does not expose a five-way 0x958/0x868/0x83c/0x6b8/0x5a4 selector',
        'group_mask_helpers':['0x28080','0x28168','0x267d0'],
        'changed_group_programmer':'0x28238',
        'iq_record_type_load':'0x26b94 object-entry +0x8c',
        'bw_record_type_0x0c_dispatch':'0x26bb8 -> 0x26bd0 / 0x27920',
        'upstream_consequence':'variant choice and frame-varying IQ payload values remain upstream IQ-producer inputs, not constants to invent in the Linux kernel'},
      'gen_irq':{'observed_rule':'0024 proves steady BL4 userdata equals the monotonically observed batch index','exact_upstream_tag_source_closed':False},
      'linux_consequence':{
        'raw_payloads_embedded':False,'windows_ring_geometry_frozen':False,
        'steady_state_materializer_ready':False,
        'remaining':'recover/define the upstream IQ producer contract for frame-varying payload values and GEN_IRQ request/tag source before any steady-state materializer or runtime caller'},
    }
    txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output: a.output.write_text(txt)
    else: print(txt,end='')
    print('PASS: all five steady-state DMI variant payload topologies are hash-pinned; KMD variant ownership is input-driven; raw payload bytes stay local')
if __name__=='__main__': main()
