#!/usr/bin/env python3
"""Read-only structural decoder for QTI Parameter Parser v3.x .bin files.

This does not contain or redistribute vendor data. It decodes the generic container:
header -> section descriptors -> fixed-size symbol records -> referenced payload bytes.
"""
import argparse, csv, json, struct
from pathlib import Path

REC = struct.Struct('<I32sIIiII')  # id, name, a, b, signed c, payload_offset, payload_size

def u32(buf, off): return struct.unpack_from('<I', buf, off)[0]

def parse(path):
    data = Path(path).read_bytes()
    if not data.startswith(b'QTI Chromatix Header\0'):
        raise ValueError('not a QTI Chromatix Header file')
    declared = u32(data, 0x1c)
    section_table = u32(data, 0xa0)
    section_count = u32(data, 0xa4)
    desc=[]
    p=section_table
    for _ in range(section_count):
        sid, off, size = struct.unpack_from('<III', data, p); p += 12
        desc.append({'id':sid,'offset':off,'size':size})
    if len(desc) < 2:
        raise ValueError('expected symbol and payload sections')
    symsec, payloadsec = desc[0], desc[1]
    if symsec['size'] % REC.size:
        raise ValueError(f'symbol section size {symsec["size"]} not divisible by {REC.size}')
    entries=[]
    for off in range(symsec['offset'], symsec['offset']+symsec['size'], REC.size):
        sid, rawname, a,b,c,poff,psz = REC.unpack_from(data, off)
        name=rawname.split(b'\0',1)[0].decode('ascii','replace')
        start=payloadsec['offset']+poff
        raw=data[start:start+psz] if start <= len(data) and start+psz <= len(data) else b''
        text=''
        if raw and raw[-1:] == b'\0' and all((32 <= x < 127) or x == 0 for x in raw):
            text=raw.rstrip(b'\0').decode('ascii','replace')
        values={}
        if psz == 1: values['u8']=raw[0] if raw else None
        elif psz == 2: values['u16']=struct.unpack('<H',raw)[0] if len(raw)==2 else None
        elif psz == 4:
            if len(raw)==4:
                values['u32']=struct.unpack('<I',raw)[0]; values['s32']=struct.unpack('<i',raw)[0]
        elif psz == 8:
            if len(raw)==8: values['u64']=struct.unpack('<Q',raw)[0]
        entries.append({'id':sid,'name':name,'a':a,'b':b,'c':c,'payload_offset':poff,'payload_size':psz,
                        'text':text,'raw_hex':raw.hex(),'values':values})
    return {'path':str(path),'size':len(data),'declared_size':declared,'section_table':section_table,
            'sections':desc,'symbol_record_size':REC.size,'entries':entries}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--name'); ap.add_argument('--json',action='store_true')
    args=ap.parse_args(); o=parse(args.file)
    entries=o['entries']
    if args.name: entries=[e for e in entries if e['name']==args.name]
    if args.json:
        print(json.dumps({**{k:v for k,v in o.items() if k!='entries'},'entries':entries},indent=2))
    else:
        print(f"size={o['size']} declared={o['declared_size']} record={o['symbol_record_size']} sections={o['sections']}")
        for e in entries:
            val=e['text'] or (str(e['values']) if e['values'] else e['raw_hex'][:64])
            print(f"{e['id']:5d} {e['name']:<32} a={e['a']} b={e['b']} c={e['c']} off=0x{e['payload_offset']:x} size={e['payload_size']:<6} {val}")
if __name__=='__main__': main()
