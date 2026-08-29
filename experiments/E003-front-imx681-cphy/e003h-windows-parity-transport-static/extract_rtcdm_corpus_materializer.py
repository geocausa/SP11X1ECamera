#!/usr/bin/env python3
from pathlib import Path
import argparse, csv, hashlib, importlib.util, json, re, struct

INITIAL_PACKET_SHA = [
    'dea5956975ba241fd3809a55a9005d1ba0055e92d31b73476ddb7942fdef4e89',
    '45e73b067b486762546018bb0c712aa156124ad2c458aca1e439bf92e09528ae',
    '03fa6fb28c23563b02d0cb8120afdfedcec186c0da2c9874408ff9c68e7459dc',
    '0a1cc423d7fca7acba6d1c4507d52fdb960221f19c6026468881334af4857a7e',
]
FINAL_PACKET_SHA = [
    '8f1b08159b15cc22676a56802131a22a91768c8d8df99432d69b6bbfe6375cb6',
    'f5346de79249e64537f1da04b46fb8f72e37ddefd840782492780a2a935380dd',
    'f8bbe757a3bf3c1c43e473f1848104ecbc8392fc71410d309460dbfaaf35d052',
    '2f299be42c688915a825a890588557bcce3c2ab6fa9b97e09d4100133eee3aae',
]
USED = [0xe94, 0xe34, 0x904, 0x4e8]
LIVE_VOLATILE = [0x3b70, 0x3d78, 0x3d7c, 0x3d80, 0x3d84]
PERIOD_CFG = 0x8c
MAIN_SLOT_ALIGN = 0x1000
DMI_PAYLOAD_ALIGN = 0x40

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def die(s): raise SystemExit('FAIL: ' + s)
def align(v, a): return (v + a - 1) & ~(a - 1)
def hx(v): return f'0x{v:x}'

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def final_main_streams(w):
    x = load_module(w / 'extract_patch_dmi_oracle.py', 'e003h_patch')
    raw_path = w / 'raw/E003H_IFE_PATCH_DMI_EXACT_20260828.log'
    raw = raw_path.read_bytes()
    if len(raw) != x.RAW_BYTES or sha_bytes(raw) != x.RAW_SHA:
        die('final patch/DMI raw identity drift')
    lines = raw.decode('utf-16').splitlines()
    marks = [i for i,l in enumerate(lines) if l == x.MARK]
    if len(marks) != 4: die('final patch/DMI marker count drift')
    out=[]
    for pi,mi in enumerate(marks):
        block=lines[mi:marks[pi+1] if pi+1<len(marks) else len(lines)]
        dd,dq=x.parse_dd(block),x.parse_dq(block)
        xm=re.search(r'x2=([0-9a-f]+) x8=([0-9a-f]+)', next(l for l in block if l.startswith('x2=')), re.I)
        x2=int(xm.group(1),16)
        d0=x2+0x74+dd[x2+0x18]
        h=dd[d0] | (dd[d0+4] << 32)
        off,used=dd[d0+8],dd[d0+0x10]
        if used != USED[pi]: die(f'packet {pi} final used length drift')
        _,cpu0=dq[h]
        main=x.bytes_at(block,cpu0+off,0xf00)[:used]
        if sha_bytes(main) != FINAL_PACKET_SHA[pi]: die(f'packet {pi} final main hash drift')
        out.append(main)
    return out, {'bytes': len(raw), 'sha256': sha_bytes(raw)}

def value_positions(data, wanted):
    pos=0; found={}
    while pos < len(data):
        w0=struct.unpack_from('<I',data,pos)[0]; op=w0>>24
        if op==3:
            n=w0&0xffff; base=struct.unpack_from('<I',data,pos+4)[0]&0xffffff
            for i in range(n):
                ro=base+4*i
                if ro in wanted:
                    if ro in found: die(f'register 0x{ro:x} appears twice in one packet')
                    found[ro]=pos+8+4*i
            pos += 8+4*n
        elif op==4: pos += 4+8*(w0&0xffff)
        elif op in (1,10,11,7,12,13,14): pos += 12
        elif op in (5,6): pos += 8
        elif op in (8,9): pos += 4
        else: die(f'unknown CDM opcode 0x{op:x} at 0x{pos:x}')
    if pos != len(data): die('command decode did not end exactly')
    return found

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--windows-dir',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); w=a.windows_dir

    prior=json.loads((w/'initial-ife-cdm-summary.json').read_text())
    patch=json.loads((w/'patch-dmi-summary.json').read_text())
    own=json.loads((w/'vfe1-startup-ownership-summary.json').read_text())
    if prior.get('status')!='PASS' or patch.get('status')!='PASS' or own.get('status')!='PASS': die('upstream oracle not PASS')
    if patch['closure']['total_dmi_commands'] != 46 or patch['closure']['unique_payload_sha256_count'] != 16: die('DMI closure drift')
    if own['windows_corpus']['ordinary_register_writes'] != 2131: die('ordinary write count drift')
    if [int(x,16) for x in own['behavior']['independent_live_volatile_overlap_offsets']] != LIVE_VOLATILE: die('live-volatile set drift')

    initial=[]
    for pi in range(4):
        b=(w/f'packet{pi}-main-cdm.bin').read_bytes()
        if len(b)!=USED[pi] or sha_bytes(b)!=INITIAL_PACKET_SHA[pi]: die(f'packet {pi} initial main identity drift')
        initial.append(b)
    final, final_raw = final_main_streams(w)

    # Exact DMI address fields from the final same-machine patch oracle.
    dmi_fields=[]
    for p in patch['packets']:
        pi=p['packet']
        if p['main_used_length'] != USED[pi] or len(p['dmi']) != p['num_patches']: die(f'packet {pi} patch summary drift')
        for d in p['dmi']:
            so=int(d['stream_offset'],16); field=so+4
            if field+4 > USED[pi]: die('DMI field outside main stream')
            dmi_fields.append((pi,field,d))
    if len(dmi_fields)!=46: die('DMI field count drift')

    # The original ownership pass proved five live-volatile register offsets.
    # Cross-capture comparison adds period_cfg +0x8c: after DMI IOVA
    # normalization it is the only byte-level difference between independent
    # Windows startup captures.
    dynamic_regs=[PERIOD_CFG]+LIVE_VOLATILE
    dynamic=[]; period_positions=[]
    for pi,b in enumerate(initial):
        pos=value_positions(b,set(dynamic_regs))
        required=set(LIVE_VOLATILE if pi < 3 else [0x3b70]) | {PERIOD_CFG}
        if set(pos)!=required: die(f'packet {pi} dynamic register presence drift: {sorted(pos)}')
        for ro in sorted(pos):
            o=pos[ro]
            iv=struct.unpack_from('<I',initial[pi],o)[0]
            fv=struct.unpack_from('<I',final[pi],o)[0]
            cls='cross_capture_dynamic_period_cfg' if ro==PERIOD_CFG else 'runtime_volatile_do_not_freeze'
            dynamic.append({'packet':pi,'register_offset':hx(ro),'value_field_offset':hx(o),'classification':cls,
                            'initial_value':f'0x{iv:08x}','final_value':f'0x{fv:08x}'})
            if ro==PERIOD_CFG: period_positions.append((pi,o))

    # Prove independent captures differ only in DMI addresses and period_cfg.
    dmi_by_packet={i:[] for i in range(4)}
    for pi,o,d in dmi_fields: dmi_by_packet[pi].append(o)
    diff_after_dmi=[]
    normalized=[]
    for pi in range(4):
        x=bytearray(initial[pi]); y=bytearray(final[pi])
        for o in dmi_by_packet[pi]: x[o:o+4]=b'\0'*4; y[o:o+4]=b'\0'*4
        diffs=[o for o in range(0,len(x),4) if x[o:o+4]!=y[o:o+4]]
        expected=[o for p,o in period_positions if p==pi]
        if diffs != expected: die(f'packet {pi} unexpected cross-capture differences after DMI normalization: {diffs} != {expected}')
        diff_after_dmi += [{'packet':pi,'value_field_offset':hx(o),'register_offset':hx(PERIOD_CFG),
                            'initial_value':f'0x{struct.unpack_from("<I",initial[pi],o)[0]:08x}',
                            'final_value':f'0x{struct.unpack_from("<I",final[pi],o)[0]:08x}'} for o in diffs]
        # Normalize every caller-supplied field, including the five live-volatile
        # fields even where the two startup captures happened to match.
        dyn_pos=[int(d['value_field_offset'],16) for d in dynamic if d['packet']==pi]
        for o in dyn_pos: x[o:o+4]=b'\0'*4; y[o:o+4]=b'\0'*4
        if x != y: die(f'packet {pi} normalized templates differ')
        normalized.append(bytes(x))

    # Payload catalog: do not freeze Windows source-window offsets. Linux packs
    # the 16 unique payloads at deterministic 64-byte aligned offsets.
    groups=patch['dmi_groups']; hashes=sorted({g['payload_sha256'] for g in groups})
    if len(hashes)!=16: die('payload hash count drift')
    cat=[]; cur=0; hash_to_id={}
    for pid,h in enumerate(hashes):
        p=w/'dmi-payloads'/f'{h}.bin'; b=p.read_bytes()
        if sha_bytes(b)!=h: die('payload file hash drift '+h)
        lens={g['payload_bytes'] for g in groups if g['payload_sha256']==h}
        if lens != {len(b)}: die('payload length drift '+h)
        cur=align(cur,DMI_PAYLOAD_ALIGN)
        cat.append({'id':pid,'sha256':h,'bytes':len(b),'linux_offset':hx(cur)})
        hash_to_id[h]=pid; cur += len(b)
    dmi_linux_bytes=align(cur,DMI_PAYLOAD_ALIGN)

    refs=[]
    for pi,o,d in dmi_fields:
        h=d['payload_sha256']; pid=hash_to_id[h]
        refs.append({'packet':pi,'dmi_index':d['dmi_index'],'address_field_offset':hx(o),
                     'dmi_register_offset':d['dmi_register_offset'],'dmi_sel':d['dmi_sel'],
                     'payload_id':pid,'payload_bytes':d['payload_bytes'],
                     'windows_src_offset':d['src_offset'],
                     'linux_payload_offset':cat[pid]['linux_offset']})

    main_slots=[]
    for pi,n in enumerate(USED):
        off=pi*MAIN_SLOT_ALIGN
        if n > MAIN_SLOT_ALIGN: die('main packet exceeds Linux page slot')
        main_slots.append({'packet':pi,'linux_offset':hx(off),'used_bytes':n,'normalized_sha256':sha_bytes(normalized[pi]),
                           'initial_sha256':INITIAL_PACKET_SHA[pi],'final_sha256':FINAL_PACKET_SHA[pi]})

    out={
      'schema':'sp11-e003h-rtcdm-corpus-materializer-oracle-v1','accepted':True,
      'policy':'raw command/payload binaries remain local and untracked; Linux materializer accepts normalized templates and exact payload blobs as inputs, never embeds Windows IOVAs or allocation strides',
      'source_oracles':{
        'initial_cdm_raw_sha256':prior['raw']['sha256'],
        'final_patch_dmi_raw':final_raw,
        'patch_dmi_summary_sha256':sha_file(w/'patch-dmi-summary.json'),
        'ownership_summary_sha256':sha_file(w/'vfe1-startup-ownership-summary.json')},
      'closure':{
        'packets':4,'ordinary_register_writes':2131,'dmi_commands':46,'unique_payloads':16,
        'caller_supplied_dynamic_value_fields':len(dynamic),
        'cross_capture_new_dynamic_register':'0x8c period_cfg',
        'cross_capture_difference_after_dmi_normalization':'period_cfg only',
        'normalized_initial_equals_final':True},
      'linux_layout':{
        'main_arena_bytes':4*MAIN_SLOT_ALIGN,'main_slot_alignment':MAIN_SLOT_ALIGN,
        'main_slots':main_slots,
        'dmi_arena_bytes':dmi_linux_bytes,'dmi_payload_alignment':DMI_PAYLOAD_ALIGN,
        'windows_main_slot_stride_frozen':False,'windows_dmi_source_offsets_frozen':False},
      'dynamic_value_fields':dynamic,
      'cross_capture_period_cfg_differences':diff_after_dmi,
      'payload_catalog':cat,
      'dmi_references':refs,
      'safety':{
        'normalized_template_holes':'all 46 DMI address fields plus all 20 dynamic register value fields are zero before materialization',
        'materializer_rule':'caller must provide all 20 dynamic values and 16 exact payload blobs; DMI addresses are rewritten to Linux-owned DMA addresses',
        'runtime_authorized':False,
        'fifo0_submission_authorized':False}}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: four CDM streams normalize across independent Windows captures; 46 DMI IOVAs + 20 caller dynamic fields are the only materializer holes')
    print('normalized:', ', '.join(x['normalized_sha256'] for x in main_slots))
    print(f'linux arenas: main=0x{4*MAIN_SLOT_ALIGN:x}, dmi=0x{dmi_linux_bytes:x}')

if __name__=='__main__': main()
