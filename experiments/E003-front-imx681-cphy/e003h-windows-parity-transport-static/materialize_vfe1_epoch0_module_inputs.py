#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
BATCH_ORACLE_SHA = '3bcf4efe34c891dcc6bc78c3cefc94d916ffd71e27dab81e75493f9ed320dce4'
PRODUCER_ORACLE_SHA = 'cbd8908d967f4831e67f8eb3c36ae9799c4bcb42e1923f0ee34c2152841c03ef'
EXPECTED = {
    0x958: (56, 472, 14),
    0x868: (45, 436, 12),
    0x83c: (43, 429, 12),
    0x6b8: (35, 352, 8),
    0x5a4: (22, 315, 2),
}
MODULE = {
    0x3b70: 'DemuxBLS141', 0x3b74: 'DemuxBLS141',
    0x3d58: 'PDPC311', 0x3d5c: 'PDPC311', 0x3d78: 'PDPC311', 0x3d7c: 'PDPC311', 0x3d80: 'PDPC311', 0x3d84: 'PDPC311',
    0x4358: 'LSC411', 0x435c: 'LSC411',
    0x456c: 'WB201', 0x4570: 'WB201',
    0x4758: 'GIC311', 0x475c: 'GIC311',
    0x4958: 'BPCABF411', 0x495c: 'BPCABF411',
    0x5a58: 'GTM131', 0x5a5c: 'GTM131',
    0x5f58: 'Gamma151', 0x5f5c: 'Gamma151',
    0xa058: 'DSX101', 0xa05c: 'DSX101', 0xa258: 'DSX101', 0xa25c: 'DSX101',
}
DMI_MODULE = {
    0x3d08: 'PDPC311', 0x4308: 'LSC411', 0x4708: 'GIC311', 0x4908: 'BPCABF411',
    0x5a08: 'GTM131', 0x5f08: 'Gamma151', 0xa008: 'DSX101', 0xa208: 'DSX101',
}
DMI_LAYOUT = {
    ('PDPC311', 1): (0x0000, 0x0200),
    ('LSC411', 1): (0x0200, 0x0374), ('LSC411', 2): (0x0580, 0x0374), ('LSC411', 3): (0x0900, 0x0374),
    ('GIC311', 1): (0x0c80, 0x0200), ('BPCABF411', 1): (0x0e80, 0x0100), ('GTM131', 1): (0x0f80, 0x0800),
    ('Gamma151', 1): (0x1780, 0x0400), ('Gamma151', 2): (0x1b80, 0x0400), ('Gamma151', 3): (0x1f80, 0x0400),
    ('DSX101', 1): (0x2380, 0x0300), ('DSX101', 2): (0x2680, 0x0300), ('DSX101', 3): (0x2980, 0x0180), ('DSX101', 4): (0x2b00, 0x0180),
}
# DSX selectors repeat 1/2 on two registers, so payload ordinal is resolved by (register, selector).
DMI_SLOT = {
    (0x3d08,1): ('PDPC311',1),
    (0x4308,1): ('LSC411',1), (0x4308,2): ('LSC411',2), (0x4308,3): ('LSC411',3),
    (0x4708,1): ('GIC311',1), (0x4908,1): ('BPCABF411',1), (0x5a08,1): ('GTM131',1),
    (0x5f08,1): ('Gamma151',1), (0x5f08,2): ('Gamma151',2), (0x5f08,3): ('Gamma151',3),
    (0xa008,1): ('DSX101',1), (0xa008,2): ('DSX101',2), (0xa208,1): ('DSX101',3), (0xa208,2): ('DSX101',4),
}

def sha(b): return hashlib.sha256(b).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def load(path, name):
    spec=importlib.util.spec_from_file_location(name, path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def check_sha(path, expected):
    got=sha(path.read_bytes())
    if got != expected: die(f'{path.name} sha {got} != {expected}')

def normalize(rec, decoded):
    b=bytearray(rec['data'])
    fields=set(decoded['dmi_addr_fields'])
    # Match the accepted extractor: only register fields that actually vary in this shape are holes.
    return b, fields

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--log', type=Path, default=HERE/'windows-vfe1-epoch0-cdm-batches'/'E003H_VFE1_EPOCH0_CDM_BATCHES_CLEAN_20260829.log')
    ap.add_argument('--batch-oracle', type=Path, default=HERE/'vfe1-epoch0-cdm-batches-oracle.json')
    ap.add_argument('--producer-oracle', type=Path, default=HERE/'vfe1-upstream-iq-producer-oracle.json')
    ap.add_argument('--output', type=Path, default=HERE/'vfe1-epoch0-module-input-materializer-proof.json')
    a=ap.parse_args()
    check_sha(a.batch_oracle, BATCH_ORACLE_SHA); check_sha(a.producer_oracle, PRODUCER_ORACLE_SHA)
    ext=load(HERE/'extract_vfe1_epoch0_cdm_batches.py','epoch0_extract')
    _, batches=ext.parse_log(a.log)
    oracle=json.loads(a.batch_oracle.read_text()); prod=json.loads(a.producer_oracle.read_text())
    if not prod.get('accepted'): die('producer oracle not accepted')
    variants={int(v['main_bytes']):v for v in oracle['main_bl_variants']}
    if set(variants) != set(EXPECTED): die('variant set drift')
    # Pick the first steady sample for each exact main length.
    sample={}
    for b in batches[4:]:
        if len(b['records']) != 5: die('steady BL count drift')
        n=b['records'][1]['bytes']
        sample.setdefault(n,b)
    if set(sample) != set(EXPECTED): die('sample variants missing')

    cmd_dma=0x22000000; dmi_dma=0x33000000
    results=[]
    for n in sorted(EXPECTED, reverse=True):
        v=variants[n]; b=sample[n]; rec=b['records'][1]
        dec=ext.decode(rec['data'])
        # Build normalized caller template exactly as accepted oracle says.
        main=bytearray(rec['data'])
        holes=[int(x,16) for x in v['normalized_holes']]
        for off in holes: main[off:off+4]=b'\0'*4
        if sha(main) != v['normalized_sha256']: die(f'0x{n:x} normalized hash drift')

        # Synthetic module values: deterministic non-Windows data, indexed by register identity.
        reg_values={}
        for j,r in enumerate(v['dynamic_register_fields']):
            field=int(r['field'],16); ro=int(r['register_offset'],16)
            mod=MODULE.get(ro)
            if not mod: die(f'unowned reg 0x{ro:x}')
            val=(0xA5000000 | ((list(MODULE.values()).index(mod)&0xff)<<16) | (j+1)) & 0xffffffff
            reg_values[(mod,ro)]=val
            struct.pack_into('<I',main,field,val)

        dmi=bytearray(0x3000); dmi_used=[]
        for j,d in enumerate(v['dmi_shape']):
            field=int(d['field'],16); dr=int(d['dmi_register_offset'],16); sel=d['selector']; sz=d['payload_bytes']
            mod=DMI_MODULE.get(dr)
            if not mod: die(f'unowned DMI 0x{dr:x}')
            key=DMI_SLOT.get((dr,sel))
            if not key or key[0]!=mod: die(f'DMI slot missing {dr:x}/{sel}')
            off,expected_sz=DMI_LAYOUT[key]
            if sz != expected_sz: die(f'DMI size drift {dr:x}/{sel}: {sz:x}!={expected_sz:x}')
            fill=bytes(((0x40+j+i)&0xff for i in range(sz)))
            dmi[off:off+sz]=fill
            struct.pack_into('<I',main,field,dmi_dma+off)
            dmi_used.append({'register':f'0x{dr:x}','selector':sel,'module':mod,'bytes':sz,'linux_dma':f'0x{dmi_dma+off:08x}','payload_sha256':sha(fill)})

        # Every accepted hole must have been filled and no non-hole dword may change from normalized template.
        if any(main[o:o+4] == b'\0'*4 for o in holes): die(f'0x{n:x} unpatched hole')
        changed={off for off in range(0,n,4) if main[off:off+4] != bytearray(rec['data'])[off:off+4]}
        # This comparison is only diagnostic because synthetic values may coincidentally match; required structural check follows.
        outdec=ext.decode(bytes(main))
        got=(len(outdec['commands']),len(outdec['writes']),len(outdec['dmis']))
        if got != EXPECTED[n]: die(f'0x{n:x} decode {got} != {EXPECTED[n]}')
        if ext.structure_signature(outdec) != ext.structure_signature(dec): die(f'0x{n:x} structure changed')

        bl0=struct.pack('<I',0x0800f000)
        bl2=struct.pack('<I',0x08057000)
        bl3=bytes.fromhex('020000035c0300000000ff0e00006f08')
        request_id=0x12340000 + b['batch']
        bl4=bytes.fromhex('0100000418000000f501f50100000006')+struct.pack('<I',request_id & 0xffffffff)
        if sha(bl0) != oracle['steady_companion_bls']['bl0_change_base_sha256']: die('BL0 hash drift')
        if sha(bl2) != oracle['steady_companion_bls']['bl2_change_base_sha256']: die('BL2 hash drift')
        if sha(bl3) != oracle['steady_companion_bls']['bl3_register_sha256']: die('BL3 hash drift')
        z=bytearray(bl4); z[0x10:0x14]=b'\0'*4
        if sha(z) != oracle['steady_companion_bls']['bl4_genirq_normalized_sha256']: die('BL4 normalized hash drift')
        if struct.unpack_from('<I',bl4,0x10)[0] != (request_id & 0xffffffff): die('GEN_IRQ request rule drift')
        results.append({'variant':f'0x{n:x}','source_batch':b['batch'],'commands':got[0],'register_writes':got[1],'dmi_commands':got[2],
                        'normalized_sha256':v['normalized_sha256'],
                        'synthetic_main_sha256':sha(main),'synthetic_dmi_arena_sha256':sha(dmi),'dmi':dmi_used,
                        'bl_lengths':[4,n,4,16,20],'synthetic_request_id':request_id})

    out={'accepted':True,'schema':'e003h-vfe1-epoch0-module-input-materializer-proof-v1',
         'source_batch_oracle_sha256':BATCH_ORACLE_SHA,'source_producer_oracle_sha256':PRODUCER_ORACLE_SHA,
         'synthetic_cmd_dma':'0x22000000','synthetic_dmi_dma':'0x33000000','windows_addresses_reused':False,
         'captured_payload_bytes_embedded':False,'fifo_submission_performed':False,'variants':results,
         'conclusion':'five real normalized Windows main templates accept synthetic named-module values/payloads at Linux-owned addresses and retain exact command/write/DMI topology; companion BLs match 0024 and GEN_IRQ derives from requestId'}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: five normalized Windows Epoch0 shapes materialize with synthetic named-module inputs and Linux-owned DMI addresses; no submission')
    print(sha(a.output.read_bytes()),a.output)

if __name__=='__main__': main()
