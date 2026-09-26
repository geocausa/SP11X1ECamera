#!/usr/bin/env python3
import argparse, collections, hashlib, json, struct
from pathlib import Path

OP_NAMES = {
    1: 'DMI', 3: 'REG_CONT', 4: 'REG_RANDOM', 5: 'BUFF_INDIRECT',
    6: 'GEN_IRQ', 7: 'WAIT_EVENT', 8: 'CHANGE_BASE', 9: 'PERF_CTRL',
    10: 'DMI_32', 11: 'DMI_64', 12: 'COMP_WAIT', 13: 'CLEAR_COMP_WAIT',
    14: 'WAIT_PREFETCH_DISABLE',
}
STARTUP_MAIN = {0:0xF1C, 1:0xEBC, 2:0xA00, 3:0x658}
STEADY_MAIN_LENGTHS = {0xAC8,0xA98,0x8F0,0x658}

def die(msg):
    raise SystemExit('FAIL: ' + msg)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def hx(v):
    return f'0x{v:x}'

def decode(data):
    pos=0; cmds=[]; writes=[]; dmis=[]; reg_fields={}; dmi_fields={}
    while pos < len(data):
        if pos+4 > len(data): die(f'truncated command at {pos:#x}')
        w0=struct.unpack_from('<I',data,pos)[0]; op=w0>>24
        name=OP_NAMES.get(op)
        if not name: die(f'unknown opcode {op:#x} at {pos:#x}')
        rec={'offset':pos,'opcode':op,'command':name}
        if op==3:
            n=w0&0xffff; need=8+4*n
            if pos+need>len(data): die('truncated REG_CONT')
            base=struct.unpack_from('<I',data,pos+4)[0]&0xffffff
            for i in range(n):
                f=pos+8+4*i; ro=base+4*i
                writes.append((ro,struct.unpack_from('<I',data,f)[0],f,'REG_CONT'))
                reg_fields[f]=ro
            rec.update(register_offset=base,count=n,bytes=need); pos+=need
        elif op==4:
            n=w0&0xffff; need=4+8*n
            if pos+need>len(data): die('truncated REG_RANDOM')
            ros=[]
            for i in range(n):
                ro=struct.unpack_from('<I',data,pos+4+8*i)[0]&0xffffff
                f=pos+8+8*i
                writes.append((ro,struct.unpack_from('<I',data,f)[0],f,'REG_RANDOM'))
                reg_fields[f]=ro; ros.append(ro)
            rec.update(register_offsets=ros,count=n,bytes=need); pos+=need
        elif op in (1,10,11):
            if pos+12>len(data): die('truncated DMI')
            addr=struct.unpack_from('<I',data,pos+4)[0]
            w2=struct.unpack_from('<I',data,pos+8)[0]
            payload=(w0&0xffff)+1; f=pos+4
            d={'offset':pos,'command':name,'address':addr,'address_field':f,
               'payload_bytes':payload,'dmi_register_offset':w2&0xffffff,'dmi_sel':w2>>24}
            dmis.append(d); dmi_fields[f]=d
            rec.update(payload_bytes=payload,dmi_register_offset=w2&0xffffff,dmi_sel=w2>>24,bytes=12)
            pos+=12
        elif op==5:
            if pos+8>len(data): die('truncated BUFF_INDIRECT')
            rec.update(length_minus_one=w0&0xffff,bytes=8); pos+=8
        elif op==6:
            if pos+8>len(data): die('truncated GEN_IRQ')
            rec.update(userdata=struct.unpack_from('<I',data,pos+4)[0],bytes=8); pos+=8
        elif op in (7,12,13,14):
            if pos+12>len(data): die('truncated fixed12')
            rec.update(bytes=12); pos+=12
        elif op==8:
            rec.update(new_base=w0&0xffffff,bytes=4); pos+=4
        elif op==9:
            rec.update(bytes=4); pos+=4
        cmds.append(rec)
    if pos!=len(data): die('decode length mismatch')
    return {'commands':cmds,'writes':writes,'dmis':dmis,'reg_fields':reg_fields,'dmi_fields':dmi_fields}

def sig(d):
    out=[]
    for c in d['commands']:
        n=c['command']
        if n=='REG_CONT': out.append((n,c['register_offset'],c['count']))
        elif n=='REG_RANDOM': out.append((n,tuple(c['register_offsets'])))
        elif n in ('DMI','DMI_32','DMI_64'): out.append((n,c['dmi_register_offset'],c['dmi_sel'],c['payload_bytes']))
        elif n=='CHANGE_BASE': out.append((n,c['new_base']))
        elif n=='BUFF_INDIRECT': out.append((n,c['length_minus_one']))
        else: out.append((n,c.get('bytes')))
    return tuple(out)

def safe_shape(d):
    return {
        'command_count':len(d['commands']),
        'register_write_count':len(d['writes']),
        'dmi_count':len(d['dmis']),
        'opcode_counts':dict(sorted(collections.Counter(x['command'] for x in d['commands']).items())),
        'dmi_shape':[{
            'field':hx(x['address_field']),
            'dmi_register_offset':hx(x['dmi_register_offset']),
            'selector':x['dmi_sel'],
            'payload_bytes':x['payload_bytes'],
        } for x in d['dmis']],
        'dmi_address_fields':[hx(x) for x in sorted(d['dmi_fields'])],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--private',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    j=json.loads(a.private.read_text(encoding='utf-8-sig'))
    if j.get('schema')!='E006a-private-reduced-records-v2': die('private schema drift')
    recs=[]
    for x in j['records']:
        b=bytes.fromhex(x['hex'])
        if len(b)!=x['bytes'] or not x.get('complete'): die('record byte completeness drift')
        recs.append({**x,'data':b})
    if len(recs)!=207: die(f'record count {len(recs)} != 207')
    byn=collections.defaultdict(list)
    for r in recs: byn[r['n']].append(r)
    for n in byn: byn[n].sort(key=lambda r:r['idx'])
    if sorted(byn)!=list(range(35)): die('batch numbering drift')
    if [r['idx'] for r in byn[0]] != [1,2,3]: die('batch0 expected captured indices 1,2,3')
    for n in range(1,35):
        if [r['idx'] for r in byn[n]] != list(range(6)): die(f'batch {n} index drift')
        if byn[n][0]['count']!=6: die(f'batch {n} count drift')

    # Startup topology.
    startup=[]
    for n,expected in STARTUP_MAIN.items():
        main=next(r for r in byn[n] if r['idx']==1)
        if main['bytes']!=expected: die(f'startup n={n} main length drift')
        d=decode(main['data'])
        z=bytearray(main['data'])
        for off in d['dmi_fields']: z[off:off+4]=b'\0'*4
        startup.append({
            'capture_n':n,'logical_batch':n+1,'main_bytes':main['bytes'],
            **safe_shape(d),
            'raw_sha256':sha(main['data']),
            'dmi_zeroed_sha256':sha(z),
            'dynamic_register_classification':'not closed by this single capture',
        })

    # Steady topology and fixed companions.
    steady=[]
    for n in range(4,35):
        a6=byn[n]
        vec=tuple(r['bytes'] for r in a6)
        if vec[0]!=4 or vec[2:]!=(12,4,16,20): die(f'steady vector drift n={n}: {vec}')
        if vec[1] not in STEADY_MAIN_LENGTHS: die(f'unknown steady main length {vec[1]:#x}')
        steady.append((n,a6))
    fixed={}
    for idx in (0,2,3,4):
        vals={sha(a6[idx]['data']) for _,a6 in steady}
        if len(vals)!=1: die(f'fixed companion idx{idx} drift')
        d=decode(steady[0][1][idx]['data'])
        fixed[str(idx)]={'bytes':steady[0][1][idx]['bytes'],'sha256':next(iter(vals)),'signature':repr(sig(d))}
    irq_norm=set(); irq_rule=[]
    for n,a6 in steady:
        d=decode(a6[5]['data'])
        if [x['command'] for x in d['commands']] != ['REG_RANDOM','GEN_IRQ']: die('GEN_IRQ companion shape drift')
        userdata=d['commands'][1]['userdata']; irq_rule.append((n,userdata))
        z=bytearray(a6[5]['data']); z[-4:]=b'\0'*4; irq_norm.add(sha(z))
    if len(irq_norm)!=1: die('normalized GEN_IRQ wrapper drift')
    if any(n!=u for n,u in irq_rule): die('GEN_IRQ userdata != capture_n')
    fixed['5']={'bytes':20,'normalized_sha256':next(iter(irq_norm)),'userdata_rule':'userdata == capture_n for n=4..34'}

    # Main variants; classify only byte drift observed across repeated steady samples.
    bylen=collections.defaultdict(list)
    for n,a6 in steady: bylen[a6[1]['bytes']].append((n,a6[1]))
    variants=[]
    observed_dynamic_regs=set()
    for nbytes in sorted(bylen,reverse=True):
        samples=bylen[nbytes]; dec=[decode(r['data']) for _,r in samples]
        s0=sig(dec[0])
        if any(sig(x)!=s0 for x in dec[1:]): die(f'main structure drift {nbytes:#x}')
        varying=[]
        if len(samples)>1:
            for off in range(0,nbytes,4):
                if len({r['data'][off:off+4] for _,r in samples})>1: varying.append(off)
        dmi=set(dec[0]['dmi_fields']); regs=dec[0]['reg_fields']
        dyn=[o for o in varying if o in regs]
        unexpected=[o for o in varying if o not in dmi and o not in regs]
        if unexpected: die(f'unclassified drift {nbytes:#x}: {[hx(x) for x in unexpected]}')
        observed_dynamic_regs |= {regs[o] for o in dyn}
        holes=sorted(dmi|set(dyn))
        norms=[]
        for _,r in samples:
            b=bytearray(r['data'])
            for off in holes: b[off:off+4]=b'\0'*4
            norms.append(sha(b))
        converged=len(set(norms))==1
        variants.append({
            'main_bytes':nbytes,
            'capture_n':[n for n,_ in samples],
            'sample_count':len(samples),
            **safe_shape(dec[0]),
            'observed_varying_dwords':[hx(x) for x in varying],
            'observed_dynamic_register_fields':[{'field':hx(o),'register_offset':hx(regs[o])} for o in dyn],
            'normalized_holes_observed_only':[hx(x) for x in holes],
            'normalized_converged':converged,
            'normalized_sha256_if_converged':norms[0] if converged else None,
            'single_sample_dynamic_fields_unresolved':len(samples)<2,
        })

    # Cross-phase 0x658 structural comparison: startup n3 vs steady n34.
    s658=next(r for r in byn[3] if r['idx']==1)
    t658=next(r for r in byn[34] if r['idx']==1)
    ds,dt=decode(s658['data']),decode(t658['data'])
    same_sig=sig(ds)==sig(dt)
    cross={'same_structure_signature':same_sig}
    if same_sig:
        diffs=[o for o in range(0,0x658,4) if s658['data'][o:o+4]!=t658['data'][o:o+4]]
        dmi=set(dt['dmi_fields']); regs=dt['reg_fields']
        cross.update({
            'dword_differences':len(diffs),
            'differences_in_dmi_fields':sum(o in dmi for o in diffs),
            'differences_in_register_value_fields':sum(o in regs for o in diffs),
            'unclassified_differences': [hx(o) for o in diffs if o not in dmi and o not in regs],
            'register_offsets_that_differ':[hx(regs[o]) for o in diffs if o in regs],
        })

    dmi_catalog=collections.Counter()
    for v in variants:
        for d in v['dmi_shape']:
            dmi_catalog[(d['dmi_register_offset'],d['selector'],d['payload_bytes'])]+=1

    out={
        'schema':'sp11-e006a-rear-rtcdm-structural-decode-v1',
        'accepted':True,
        'source':{
            'private_record_file_sha256':sha(a.private.read_bytes()),
            'raw_bytes_committed':False,
            'captured_debugger_addresses_committed':False,
            'records':len(recs),'batches_observed':35,
        },
        'capture_indexing':{
            'capture_n_is_zero_based_batch_index':True,
            'batch0_idx0_missing':True,
            'batch0_missing_record_bytes':4,
            'batch0_missing_record_not_synthesized':True,
        },
        'startup':startup,
        'steady':{
            'batches':31,
            'main_length_census':{hx(k):len(v) for k,v in sorted(bylen.items())},
            'fixed_companions':fixed,
            'main_variants':variants,
            'observed_dynamic_register_offsets_across_repeated_variants':[hx(x) for x in sorted(observed_dynamic_regs)],
            'dmi_shape_catalog':[{
                'dmi_register_offset':k[0],'selector':k[1],'payload_bytes':k[2],'variant_occurrences':c
            } for k,c in sorted(dmi_catalog.items())],
        },
        'startup_vs_steady_0x658':cross,
        'safety':{
            'rear_capsule_materialization_authorized':False,
            'linux_rtcdm_submission_authorized':False,
            'reason':'DMI payload bytes and startup/single-sample dynamic-field closure are not yet complete.',
        },
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: E006a rear RT-CDM private corpus decoded structurally; raw bytes remain private')
    print('steady census',out['steady']['main_length_census'])
    for v in variants:
        print(f"{v['main_bytes']:#x}: samples={v['sample_count']} cmds={v['command_count']} writes={v['register_write_count']} dmi={v['dmi_count']} dyn={len(v['observed_dynamic_register_fields'])} converged={v['normalized_converged']}")
    print('observed dynamic regs',out['steady']['observed_dynamic_register_offsets_across_repeated_variants'])
    print('0x658 startup/steady',cross)

if __name__=='__main__':
    main()
