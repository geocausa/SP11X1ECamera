#!/usr/bin/env python3
import argparse, hashlib, json, struct
from pathlib import Path

MAGIC=b'E3HPIX01'; VERSION=1; HEADER_BYTES=1024; ALIGN=64
EXPECTED_COUNTS={1:4,2:16,3:1,4:1,5:14}

def die(s): raise SystemExit('FAIL: '+s)
def sha(b): return hashlib.sha256(b).hexdigest()
def aligned(v): return (v & (ALIGN-1)) == 0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--capsule', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, required=True)
    a=ap.parse_args()
    cap=a.capsule.read_bytes(); m=json.loads(a.manifest.read_text())
    if not m.get('accepted') or m.get('schema')!='sp11-e003h-pix-oracle-capsule-v1': die('manifest identity')
    if m.get('capsule_committed') is not False: die('capsule privacy policy drift')
    if len(cap)!=m['capsule']['bytes'] or sha(cap)!=m['capsule']['sha256']: die('capsule identity')
    if len(cap)<HEADER_BYTES: die('short capsule')
    vals=struct.unpack_from('<8sIIIIIIIIIIQII',cap,0)
    magic,ver,hdr,total,count,s0,s1,p0,p1,variant,req,sub,res0,res1=vals
    if magic!=MAGIC or ver!=VERSION or hdr!=HEADER_BYTES: die('header identity')
    if total!=len(cap) or count!=len(m['sections']): die('header size/count')
    if (s0,s1)!=tuple(int(x,16) for x in m['period_cfg']['startup']): die('startup period')
    if (p0,p1)!=tuple(int(x,16) for x in m['period_cfg']['priming']): die('priming period')
    if variant!=int(m['steady']['variant'],16) or req!=m['steady']['request_id'] or sub!=m['steady']['subrequest']: die('steady header')
    if res0 or res1: die('reserved header nonzero')
    desc=[]; counts={}
    for i in range(count):
        typ,idx,off,n=struct.unpack_from('<IIII',cap,64+i*16)
        if typ not in EXPECTED_COUNTS: die(f'unknown section type {typ}')
        if not aligned(off) or off<HEADER_BYTES or n==0 or off+n>len(cap): die(f'bad descriptor {i}')
        desc.append((typ,idx,off,n)); counts[typ]=counts.get(typ,0)+1
    if counts!=EXPECTED_COUNTS: die(f'section census {counts}')
    if len(set((t,i) for t,i,_,_ in desc))!=len(desc): die('duplicate type/index')
    # Require descriptor order and bytes to equal the hash-only manifest exactly.
    for i,(d,ms) in enumerate(zip(desc,m['sections'])):
        typ,idx,off,n=d
        if (typ,idx,off,n)!=(ms['type'],ms['index'],int(ms['offset'],16),ms['bytes']): die(f'manifest descriptor {i}')
        if sha(cap[off:off+n])!=ms['sha256']: die(f'section hash {i}')
    # No section overlap and all capsule padding must be zero.
    intervals=sorted((off,off+n) for _,_,off,n in desc)
    prev=HEADER_BYTES
    for start,end in intervals:
        if start<prev: die('section overlap')
        if any(cap[prev:start]): die('nonzero padding')
        prev=end
    if any(cap[prev:]): die('nonzero trailing padding')
    # Descriptor table tail and unused header bytes remain zero.
    dt_end=64+count*16
    if any(cap[dt_end:HEADER_BYTES]): die('nonzero unused header')
    # Named-module section ABI: nine 32-byte records, masks agree with manifest.
    mod=[d for d in desc if d[0]==4]
    if len(mod)!=1 or mod[0][3]!=9*32: die('module section size')
    _,_,off,n=mod[0]; blob=cap[off:off+n]
    vm=[]; pm=[]
    for i in range(9):
        v,p,r=struct.unpack_from('<BBH',blob,i*32)
        if r: die(f'module reserved {i}')
        vm.append(f'0x{v:02x}'); pm.append(f'0x{p:02x}')
    if vm!=m['steady']['module_value_valid'] or pm!=m['steady']['module_payload_valid']: die('module masks')
    print('PASS',a.capsule,len(cap),sha(cap),'sections',count,'variant',hex(variant),'request',req)

if __name__=='__main__': main()
