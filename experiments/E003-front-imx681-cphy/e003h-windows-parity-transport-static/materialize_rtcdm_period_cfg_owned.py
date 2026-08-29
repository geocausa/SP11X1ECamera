#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
MAIN_DMA=0x20000000; DMI_DMA=0x30000000

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
    if sha(b)!=own['refined_main_slots'][pi]['normalized_sha256']: die(f'p{pi} normalized hash drift')
    return bytes(b)

def logical_period(own, which):
    vals=[int(x[f'{which}_value'],16) for x in own['period_fields']]
    if len(set(vals[1:]))!=1 or vals[0]==vals[1]: die(which+' logical period relation drift')
    return vals[0],vals[1]

def materialize(base,w,old,own,which):
    main=bytearray(old['linux_layout']['main_arena_bytes']); dmi=bytearray(old['linux_layout']['dmi_arena_bytes'])
    source=streams(w,base,which)
    p0,p123=logical_period(own,which)
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
        pi=p['packet']; slot=int(old['linux_layout']['main_slots'][pi]['linux_offset'],16); o=slot+int(p['value_field_offset'],16)
        struct.pack_into('<I',main,o,p0 if pi==0 else p123)
    return main,dmi,{'packet0':f'0x{p0:08x}','packets123':f'0x{p123:08x}'}

def verify(w,old,own,which,main,dmi,logical):
    dec=load(w/'extract_initial_ife_cdm.py','e003h_decode_'+which)
    total_cmd=total_wr=total_dmi=0; hashes=[]
    for pi,s in enumerate(old['linux_layout']['main_slots']):
        slot=int(s['linux_offset'],16); n=s['used_bytes']; stream=bytes(main[slot:slot+n]); cmds,writes,dmis=dec.decode(stream)
        hashes.append(sha(stream)); total_cmd+=len(cmds); total_wr+=len(writes); total_dmi+=len(dmis)
        wr={(x['register_offset'],x['value']) for x in writes}
        want=int(logical['packet0' if pi==0 else 'packets123'],16)
        if (0x8c,want) not in wr: die(f'p{pi} logical period missing')
    if (total_cmd,total_wr,total_dmi)!=(278,2131,46): die('decode totals drift')
    return {'main_arena_sha256':sha(main),'dmi_arena_sha256':sha(dmi),'packet_sha256':hashes,'logical_period_cfg':logical,
            'decoded_commands':total_cmd,'ordinary_register_writes':total_wr,'dmi_commands':total_dmi}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--windows-dir',type=Path,required=True); ap.add_argument('--old-oracle',type=Path,required=True); ap.add_argument('--ownership-oracle',type=Path,required=True); ap.add_argument('--period-contract',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    old=json.loads(a.old_oracle.read_text()); own=json.loads(a.ownership_oracle.read_text()); pc=json.loads(a.period_contract.read_text()); base=a.old_oracle.parent
    if not old.get('accepted') or not own.get('accepted') or not pc.get('accepted'): die('oracle not accepted')
    if pc['linux_consequence']['materializer_dynamic_values']!=2: die('period contract value count drift')
    variants={}
    for which in ('initial','final'):
        ma,da,logical=materialize(base,a.windows_dir,old,own,which); variants[which]=verify(a.windows_dir,old,own,which,ma,da,logical)
    if variants['initial']['dmi_arena_sha256']!=variants['final']['dmi_arena_sha256']: die('DMI arena mismatch')
    out={'schema':'sp11-e003h-rtcdm-period-cfg-two-value-materialization-static-v1','accepted':True,
         'period_contract_sha256':sha(a.period_contract.read_bytes()),'ownership_oracle_sha256':sha(a.ownership_oracle.read_bytes()),
         'variants':variants,'synthetic_dma':{'main':f'0x{MAIN_DMA:08x}','dmi':f'0x{DMI_DMA:08x}'},
         'closure':{'logical_dynamic_caller_values':2,'period_patch_sites':4,'packets123_share_one_value':True,'dmi_addresses_rewritten':46,'commands':278,'ordinary_register_writes':2131,'dmi_commands':46},
         'runtime_authorized':False,'fifo0_submission_authorized':False}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: two logical caller period_cfg values reconstruct both independent Windows startup variants across four packet sites')
if __name__=='__main__': main()
