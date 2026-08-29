#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
MAIN_DMA=0x20000000
DMI_DMA=0x30000000

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def streams(w, base, which):
    if which=='initial': return [(w/f'packet{i}-main-cdm.bin').read_bytes() for i in range(4)]
    mod=load(base/'extract_rtcdm_corpus_materializer.py','e003h_final_streams'); return mod.final_main_streams(w)[0]

def normalized(stream, pi, old, own):
    b=bytearray(stream)
    for r in old['dmi_references']:
        if r['packet']==pi:
            o=int(r['address_field_offset'],16); b[o:o+4]=b'\0'*4
    p=own['period_fields'][pi]; o=int(p['value_field_offset'],16); b[o:o+4]=b'\0'*4
    exp=own['refined_main_slots'][pi]['normalized_sha256']
    if sha(b)!=exp: die(f'packet {pi} refined normalized hash drift')
    return bytes(b)

def materialize(base,w,old,own,which):
    main=bytearray(old['linux_layout']['main_arena_bytes']); dmi=bytearray(old['linux_layout']['dmi_arena_bytes'])
    source=streams(w,base,which)
    for pi,s in enumerate(old['linux_layout']['main_slots']):
        off=int(s['linux_offset'],16); t=normalized(source[pi],pi,old,own); main[off:off+len(t)]=t
    for p in old['payload_catalog']:
        blob=(w/'dmi-payloads'/f"{p['sha256']}.bin").read_bytes()
        if len(blob)!=p['bytes'] or sha(blob)!=p['sha256']: die('payload drift')
        po=int(p['linux_offset'],16); dmi[po:po+len(blob)]=blob
    for r in old['dmi_references']:
        slot=int(old['linux_layout']['main_slots'][r['packet']]['linux_offset'],16)
        o=slot+int(r['address_field_offset'],16); addr=DMI_DMA+int(r['linux_payload_offset'],16)
        struct.pack_into('<I',main,o,addr)
    for p in own['period_fields']:
        slot=int(old['linux_layout']['main_slots'][p['packet']]['linux_offset'],16)
        o=slot+int(p['value_field_offset'],16); struct.pack_into('<I',main,o,int(p[f'{which}_value'],16))
    return main,dmi

def verify(base,w,old,own,which,main,dmi):
    dec=load(w/'extract_initial_ife_cdm.py','e003h_decode_'+which)
    total_cmd=total_wr=total_dmi=0; hashes=[]
    for pi,s in enumerate(old['linux_layout']['main_slots']):
        slot=int(s['linux_offset'],16); n=s['used_bytes']; stream=bytes(main[slot:slot+n]); cmds,writes,dmis=dec.decode(stream)
        hashes.append(sha(stream)); total_cmd+=len(cmds); total_wr+=len(writes); total_dmi+=len(dmis)
        wr={(x['register_offset'],x['value']) for x in writes}
        # Four caller period values are present.
        p=own['period_fields'][pi]
        if (0x8c,int(p[f'{which}_value'],16)) not in wr: die(f'p{pi} period value missing')
        # Sixteen formerly over-broad dynamic fields stay in the exact template.
        for x in own['startup_template_fields']:
            if x['packet']==pi and (int(x['register_offset'],16),int(x['initial_value'],16)) not in wr:
                die(f'p{pi} invariant startup-template field missing {x["register_offset"]}')
    if (total_cmd,total_wr,total_dmi)!=(278,2131,46): die('decode totals drift')
    return {'main_arena_sha256':sha(main),'dmi_arena_sha256':sha(dmi),'packet_sha256':hashes,
            'decoded_commands':total_cmd,'ordinary_register_writes':total_wr,'dmi_commands':total_dmi}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--windows-dir',type=Path,required=True); ap.add_argument('--old-oracle',type=Path,required=True); ap.add_argument('--ownership-oracle',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    old=json.loads(a.old_oracle.read_text()); own=json.loads(a.ownership_oracle.read_text()); base=a.old_oracle.parent
    if not old.get('accepted') or not own.get('accepted'): die('oracle not accepted')
    variants={}
    for which in ('initial','final'):
        ma,da=materialize(base,a.windows_dir,old,own,which); variants[which]=verify(base,a.windows_dir,old,own,which,ma,da)
    if variants['initial']['dmi_arena_sha256']!=variants['final']['dmi_arena_sha256']: die('DMI arena mismatch')
    out={'schema':'sp11-e003h-rtcdm-startup-owned-materialization-static-v1','accepted':True,
         'ownership_oracle_sha256':sha(a.ownership_oracle.read_bytes()),'old_0019_oracle_sha256':sha(a.old_oracle.read_bytes()),
         'synthetic_dma':{'main':f'0x{MAIN_DMA:08x}','dmi':f'0x{DMI_DMA:08x}'},'variants':variants,
         'closure':{'dynamic_caller_values':4,'startup_template_invariant_live_mutable_values':16,'dmi_addresses_rewritten':46,
                    'commands':278,'ordinary_register_writes':2131,'dmi_commands':46},
         'conclusion':'refined templates retain the 16 invariant startup words and require only four caller-supplied period_cfg values; Linux rewrites only 46 DMI addresses plus those four period words',
         'runtime_authorized':False,'fifo0_submission_authorized':False}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: refined static materializer reconstructs both Windows variants with 4 caller period values; 16 startup words remain template-owned')

if __name__=='__main__': main()
