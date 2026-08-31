#!/usr/bin/env python3
import argparse, json, mmap, os, struct, time
from pathlib import Path
BASE=0x0AC71000
SIZE=0x4000
HW_VERSION=0x30000002
LOW_OFFSETS=[0x00,0x04,0x08,0x0c,0x10,0x14,0x18,0x1c,0x20,0x24,0x28,0x2c,0x30,0x34,0x38,0x3c,0x40,0x44,0x48,0x4c,0x50,0x54,0x58,0x5c,0x60,0x64,0x68,0x6c,0x70,0x74,0x78,0x7c,0x80,0x84,0x88,0x8c,0x90,0x94,0x98,0x9c]
def read_raw(mm):
    mm.seek(0); return mm.read(SIZE)
def low(raw):
    return {f'0x{o:04x}':f'0x{struct.unpack_from("<I",raw,o)[0]:08x}' for o in LOW_OFFSETS}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('output',type=Path); ap.add_argument('--ready',type=Path,required=True); ap.add_argument('--seconds',type=float,default=4.0); ap.add_argument('--interval-ms',type=float,default=1.0); a=ap.parse_args()
    if a.output.exists() or a.ready.exists(): raise SystemExit('refusing overwrite')
    fd=os.open('/dev/mem',os.O_RDONLY|os.O_SYNC)
    try:
        mm=mmap.mmap(fd,SIZE,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ,offset=BASE)
        try:
            first=read_raw(mm); first_low=low(first)
            a.ready.write_text('READY\n')
            start=time.monotonic_ns(); deadline=start+int(a.seconds*1e9); n=0; active_samples=0; seen=False; prev=None; transitions=[]; snaps=[]; last_active=None
            def snap(label,raw,t): snaps.append({'label':label,'t_ns':t-start,'hex':raw.hex()})
            snap('pre',first,start)
            while time.monotonic_ns()<deadline:
                t=time.monotonic_ns(); raw=read_raw(mm); n+=1; lo=low(raw); hv=int(lo['0x0000'],16); active=(hv==HW_VERSION)
                signature=tuple(lo[k] for k in sorted(lo))
                if signature!=prev:
                    transitions.append({'t_ns':t-start,'active':active,'low':lo}); prev=signature
                if active:
                    active_samples+=1; last_active=(raw,t)
                    if not seen:
                        seen=True; snap('active-first',raw,t)
                    elif active_samples in (25,100,250,500,750): snap(f'active-{active_samples}',raw,t)
                elif seen:
                    snap('post-active',raw,t); break
                time.sleep(a.interval_ms/1000.0)
            if last_active is not None: snap('active-last',last_active[0],last_active[1])
            out={'schema':'sp11-e003h-vfe1-aperture-0058-telemetry-v1','base':f'0x{BASE:08x}','size':SIZE,'read_only':True,'samples':n,'active_samples':active_samples,'seen_active':seen,'pre_low':first_low,'transitions':transitions,'snapshots':snaps}
            a.output.write_text(json.dumps(out,separators=(',',':'))+'\n')
            if not seen: raise SystemExit('no powered VFE1 aperture observed')
        finally: mm.close()
    finally: os.close(fd)
if __name__=='__main__': main()
