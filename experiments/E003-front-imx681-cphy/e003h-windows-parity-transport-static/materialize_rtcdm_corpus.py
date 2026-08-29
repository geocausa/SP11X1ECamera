#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct

MAIN_DMA = 0x20000000
DMI_DMA = 0x30000000

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def make_normalized(w, oracle, pi):
    b=bytearray((w/f'packet{pi}-main-cdm.bin').read_bytes())
    for r in oracle['dmi_references']:
        if r['packet']==pi:
            o=int(r['address_field_offset'],16); b[o:o+4]=b'\0'*4
    for d in oracle['dynamic_value_fields']:
        if d['packet']==pi:
            o=int(d['value_field_offset'],16); b[o:o+4]=b'\0'*4
    exp=oracle['linux_layout']['main_slots'][pi]['normalized_sha256']
    if sha(b)!=exp: die(f'packet {pi} normalized hash drift')
    return bytes(b)

def materialize(w, oracle, which):
    main=bytearray(oracle['linux_layout']['main_arena_bytes'])
    dmi=bytearray(oracle['linux_layout']['dmi_arena_bytes'])
    packets=[]
    for s in oracle['linux_layout']['main_slots']:
        pi=s['packet']; off=int(s['linux_offset'],16); tmpl=make_normalized(w,oracle,pi)
        main[off:off+len(tmpl)]=tmpl; packets.append((pi,off,s['used_bytes']))
    for p in oracle['payload_catalog']:
        src=(w/'dmi-payloads'/f"{p['sha256']}.bin").read_bytes()
        if len(src)!=p['bytes'] or sha(src)!=p['sha256']: die('payload identity drift')
        off=int(p['linux_offset'],16); dmi[off:off+len(src)]=src
    # Patch Linux-owned DMI addresses.
    for r in oracle['dmi_references']:
        pi=r['packet']; slot=int(oracle['linux_layout']['main_slots'][pi]['linux_offset'],16)
        o=slot+int(r['address_field_offset'],16); po=int(r['linux_payload_offset'],16)
        addr=DMI_DMA+po
        if addr > 0xffffffff: die('synthetic DMI DMA exceeds 32 bit')
        struct.pack_into('<I',main,o,addr)
        payload=dmi[po:po+r['payload_bytes']]
        cat=oracle['payload_catalog'][r['payload_id']]
        if sha(payload)!=cat['sha256']: die('materialized DMI payload drift')
    # Patch all caller-required dynamic values; there is deliberately no default.
    for d in oracle['dynamic_value_fields']:
        pi=d['packet']; slot=int(oracle['linux_layout']['main_slots'][pi]['linux_offset'],16)
        o=slot+int(d['value_field_offset'],16); v=int(d[f'{which}_value'],16)
        struct.pack_into('<I',main,o,v)
    return main,dmi,packets

def verify_variant(w, oracle, which, main, dmi, packets):
    dec=load(w/'extract_initial_ife_cdm.py','e003h_decode_'+which)
    total_cmd=total_wr=total_dmi=0; packet_hashes=[]
    refs_by_packet={i:[] for i in range(4)}
    for r in oracle['dmi_references']: refs_by_packet[r['packet']].append(r)
    for pi,slot,n in packets:
        stream=bytes(main[slot:slot+n]); cmds,writes,dmis=dec.decode(stream)
        total_cmd += len(cmds); total_wr += len(writes); total_dmi += len(dmis); packet_hashes.append(sha(stream))
        if len(dmis)!=len(refs_by_packet[pi]): die(f'packet {pi} DMI count drift')
        for got,ref in zip(dmis,refs_by_packet[pi]):
            exp=DMI_DMA+int(ref['linux_payload_offset'],16)
            if got['stream_offset']+4 != int(ref['address_field_offset'],16) or got['data_iova']!=exp:
                die(f'packet {pi} materialized DMI address mismatch')
        dyn={(int(x['register_offset'],16),int(x[f'{which}_value'],16)) for x in oracle['dynamic_value_fields'] if x['packet']==pi}
        wr={(x['register_offset'],x['value']) for x in writes}
        if not dyn <= wr: die(f'packet {pi} dynamic values not present after materialization')
    if total_wr != 2131 or total_dmi != 46 or total_cmd != 278: die('aggregate decode counts drift')
    return {'main_arena_sha256':sha(main),'dmi_arena_sha256':sha(dmi),'packet_sha256':packet_hashes,
            'decoded_commands':total_cmd,'ordinary_register_writes':total_wr,'dmi_commands':total_dmi}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--windows-dir',type=Path,required=True); ap.add_argument('--oracle',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    oracle=json.loads(a.oracle.read_text()); w=a.windows_dir
    if not oracle.get('accepted'): die('materializer oracle not accepted')
    variants={}
    for which in ('initial','final'):
        ma,da,packets=materialize(w,oracle,which)
        variants[which]=verify_variant(w,oracle,which,ma,da,packets)
    if variants['initial']['dmi_arena_sha256'] != variants['final']['dmi_arena_sha256']: die('DMI arena should be identical across variants')
    out={'schema':'sp11-e003h-rtcdm-corpus-materialization-static-v1','accepted':True,
         'oracle_sha256':sha(a.oracle.read_bytes()),'synthetic_dma':{'main':f'0x{MAIN_DMA:08x}','dmi':f'0x{DMI_DMA:08x}'},
         'variants':variants,
         'conclusion':'normalized local templates + 16 exact payloads reconstruct all four 278-command/2131-write/46-DMI streams using Linux-owned addresses; all 20 dynamic register values are explicit caller inputs',
         'runtime_authorized':False,'fifo0_submission_authorized':False}
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: static materializer reconstructs both independent Windows variants with Linux-owned DMI addresses; 278 commands / 2131 writes / 46 DMI')

if __name__=='__main__': main()
