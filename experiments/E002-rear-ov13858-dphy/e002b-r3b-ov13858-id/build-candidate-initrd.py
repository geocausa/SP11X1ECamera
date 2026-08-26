#!/usr/bin/env python3
import argparse, hashlib, os, pathlib, subprocess

def a4(n): return (n+3)&~3

def parse_newc(data):
    pos=0; out=[]
    while pos+110<=len(data):
        if data[pos:pos+6]!=b'070701':
            if any(data[pos:]): raise ValueError(f'non-zero non-newc data at {pos}')
            break
        h=data[pos:pos+110]; mode=int(h[14:22],16); size=int(h[54:62],16); nsz=int(h[94:102],16)
        ns=pos+110; name=data[ns:ns+nsz-1].decode('utf-8','surrogateescape'); ds=a4(ns+nsz); de=ds+size; nxt=a4(de)
        out.append((name,mode,data[ds:de],pos,nxt))
        if name=='TRAILER!!!': break
        pos=nxt
    return out

def fmap(es): return {n:(m,len(p),hashlib.sha256(p).hexdigest()) for n,m,p,_,_ in es if n!='TRAILER!!!'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--golden',required=True); ap.add_argument('--provider',required=True); ap.add_argument('--probe',required=True); ap.add_argument('--out',required=True); ap.add_argument('--work',required=True); a=ap.parse_args()
    w=pathlib.Path(a.work); w.mkdir(parents=True,exist_ok=True)
    raw=subprocess.check_output(['zstd','-q','-dc',a.golden]); es=parse_newc(raw); tr=[e for e in es if e[0]=='TRAILER!!!']
    if len(tr)!=1: raise SystemExit(f'expected one Golden trailer, got {len(tr)}')
    off=tr[0][3]; prefix=raw[:off]; gm0={e[0]:e for e in es}
    root=w/'layer-root'; extra=pathlib.Path('usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra')
    prel=extra/'sp11_camera_rpmh_regulator.ko'; srel=extra/'sp11_ov13858_probe.ko'; loaderrel=pathlib.Path('scripts/init-top/zz-sp11-camera-r3b-probe'); orderrel=pathlib.Path('scripts/init-top/ORDER')
    (root/extra).mkdir(parents=True,exist_ok=True); (root/loaderrel.parent).mkdir(parents=True,exist_ok=True)
    (root/prel).write_bytes(pathlib.Path(a.provider).read_bytes()); (root/srel).write_bytes(pathlib.Path(a.probe).read_bytes()); os.chmod(root/prel,0o644); os.chmod(root/srel,0o644)
    old=gm0[str(orderrel)][2];
    if b'zz-sp11-camera-r3b-probe' in old: raise SystemExit('Golden ORDER already contains r3b loader')
    add=b'/scripts/init-top/zz-sp11-camera-r3b-probe "$@"\n[ -e /conf/param.conf ] && . /conf/param.conf\n'
    (root/orderrel).write_bytes(old+add); os.chmod(root/orderrel,gm0[str(orderrel)][1]&0o7777)
    loader='''#!/bin/sh\ncase "${1:-}" in\n  prereqs) exit 0 ;;\nesac\nlog() { printf '<6>sp11-camera-r3b-initrd: %s\\n' "$*" > /dev/kmsg 2>/dev/null || true; }\nP=/usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/sp11_camera_rpmh_regulator.ko\nS=/usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/sp11_ov13858_probe.ko\nD=/sys/bus/platform/devices/17500000.rsc:camera-rpmh-regulators/driver\nif /usr/bin/insmod "$P"; then\n  if [ -L "$D" ]; then\n    log "camera RPMh provider bound; arming rear identity probe"\n    if /usr/bin/insmod "$S"; then\n      log "rear identity probe module loaded"\n    else\n      rc=$?; log "rear identity probe module load failed rc=$rc"\n    fi\n  else\n    log "provider module loaded but provider is not bound; sensor probe skipped"\n  fi\nelse\n  rc=$?; log "provider module load failed rc=$rc; sensor probe skipped"\nfi\nexit 0\n'''
    (root/loaderrel).write_text(loader); os.chmod(root/loaderrel,0o755)
    for q in [root/extra,root/prel,root/srel,root/loaderrel,root/orderrel]: os.utime(q,(0,0),follow_symlinks=False)
    names='\n'.join(map(str,[extra,prel,srel,loaderrel,orderrel]))+'\n'
    p=subprocess.run(['cpio','-o','-H','newc','--quiet','--reproducible'],cwd=root,input=names.encode(),stdout=subprocess.PIPE,check=True)
    combined=prefix+p.stdout; (w/'combined.cpio').write_bytes(combined); subprocess.run(['zstd','-q','-T0','-6','-f',str(w/'combined.cpio'),'-o',a.out],check=True)
    gm=fmap(es); cm=fmap(parse_newc(combined)); changes=[(n,gm.get(n),cm.get(n)) for n in sorted(set(gm)|set(cm)) if gm.get(n)!=cm.get(n)]
    expected={str(extra),str(prel),str(srel),str(loaderrel),str(orderrel)}
    if {x[0] for x in changes}!=expected: raise SystemExit(f'unexpected delta {[x[0] for x in changes]}')
    if combined[:off]!=prefix: raise SystemExit('Golden prefix mismatch')
    lines=[f'golden_sha256={hashlib.sha256(pathlib.Path(a.golden).read_bytes()).hexdigest()}',f'golden_uncompressed_prefix_bytes={off}',f'golden_uncompressed_prefix_sha256={hashlib.sha256(prefix).hexdigest()}',f'candidate_sha256={hashlib.sha256(pathlib.Path(a.out).read_bytes()).hexdigest()}','semantic_delta_count=5']
    for n,b,c in changes: lines.append(f'{n}: {b} -> {c}')
    (w/'INITRD-DELTA.txt').write_text('\n'.join(lines)+'\n'); print((w/'INITRD-DELTA.txt').read_text(),end='')
if __name__=='__main__': main()
