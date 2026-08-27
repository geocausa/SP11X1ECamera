#!/usr/bin/env python3
import argparse, hashlib, os, pathlib, shutil, subprocess
REL='7.1.5-sp11-render-parity-v4+'
def parse_newc(data):
    out=[]; pos=0
    while pos+110<=len(data):
        if data[pos:pos+6]!=b'070701': raise SystemExit(f'bad cpio magic at {pos}')
        h=data[pos:pos+110]; vals=[int(h[6+i*8:14+i*8],16) for i in range(13)]
        mode=vals[1]; size=vals[6]; namesize=vals[11]
        ns=pos+110; ne=ns+namesize; name=data[ns:ne-1].decode(); ds=(ne+3)&~3; de=ds+size; nxt=(de+3)&~3
        out.append((name,mode,data[ds:de],pos,nxt))
        if name=='TRAILER!!!': break
        pos=nxt
    return out
def fmap(es): return {n:(m,len(p),hashlib.sha256(p).hexdigest()) for n,m,p,_,_ in es if n!='TRAILER!!!'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base',required=True); ap.add_argument('--probe',required=True); ap.add_argument('--out',required=True); ap.add_argument('--work',required=True); a=ap.parse_args()
    w=pathlib.Path(a.work); shutil.rmtree(w,ignore_errors=True); w.mkdir(parents=True)
    base=pathlib.Path(a.base); raw=subprocess.check_output(['zstd','-q','-dc',str(base)]); es=parse_newc(raw); tr=[e for e in es if e[0]=='TRAILER!!!']
    if len(tr)!=1: raise SystemExit('bad base trailer')
    prefix=raw[:tr[0][3]]; bm0={e[0]:e for e in es}
    root=w/'layer-root'; extra_parent=pathlib.Path(f'usr/lib/modules/{REL}/extra'); extra=extra_parent/'e003b-imx681-identity'; root_extra=root/extra; root_extra.mkdir(parents=True)
    orderrel=pathlib.Path('scripts/init-top/ORDER'); loaderrel=pathlib.Path('scripts/init-top/zz-sp11-camera-e003b-imx681-identity'); (root/loaderrel.parent).mkdir(parents=True,exist_ok=True)
    (root_extra/'sp11_imx681_probe.ko').write_bytes(pathlib.Path(a.probe).read_bytes()); os.chmod(root_extra/'sp11_imx681_probe.ko',0o644)
    old=bm0[str(orderrel)][2]
    add=b'/scripts/init-top/zz-sp11-camera-e003b-imx681-identity "$@"\n[ -e /conf/param.conf ] && . /conf/param.conf\n'
    (root/orderrel).write_bytes(old+add); os.chmod(root/orderrel,bm0[str(orderrel)][1]&0o7777)
    loader=f'''#!/bin/sh
case "${{1:-}}" in prereqs) exit 0 ;; esac
log() {{ printf '<6>sp11-camera-e003b-initrd: %s\\n' "$*" > /dev/kmsg 2>/dev/null || true; }}
E=/usr/lib/modules/{REL}/extra/e003b-imx681-identity
log "loading probe-only IMX681 identity shim; no front CSI endpoint exists"
if /usr/bin/insmod "$E/sp11_imx681_probe.ko"; then
    log "sp11_imx681_probe module loaded"
else
    rc=$?; log "sp11_imx681_probe load failed rc=$rc"
fi
exit 0
'''
    (root/loaderrel).write_text(loader); os.chmod(root/loaderrel,0o755)
    tracked=[root/extra,root_extra/'sp11_imx681_probe.ko',root/loaderrel,root/orderrel]
    for q in tracked: os.utime(q,(0,0),follow_symlinks=False)
    names='\n'.join([str(extra),str(extra/'sp11_imx681_probe.ko'),str(loaderrel),str(orderrel)])+'\n'
    cp=subprocess.run(['cpio','-o','-H','newc','--quiet','--reproducible'],cwd=root,input=names.encode(),stdout=subprocess.PIPE,check=True)
    combined=prefix+cp.stdout; (w/'combined.cpio').write_bytes(combined); subprocess.run(['zstd','-q','-T1','-6','-f',str(w/'combined.cpio'),'-o',a.out],check=True)
    bm=fmap(es); cm=fmap(parse_newc(combined)); changes=[(n,bm.get(n),cm.get(n)) for n in sorted(set(bm)|set(cm)) if bm.get(n)!=cm.get(n)]
    expected={str(extra),str(extra/'sp11_imx681_probe.ko'),str(loaderrel),str(orderrel)}; actual={x[0] for x in changes}
    if actual!=expected: raise SystemExit(f'unexpected delta only={sorted(actual-expected)} missing={sorted(expected-actual)}')
    lines=[f'base_sha256={hashlib.sha256(base.read_bytes()).hexdigest()}',f'candidate_sha256={hashlib.sha256(pathlib.Path(a.out).read_bytes()).hexdigest()}',f'semantic_delta_count={len(changes)}']
    for n,b,c in changes: lines.append(f'{n}: {b} -> {c}')
    (w/'INITRD-DELTA.txt').write_text('\n'.join(lines)+'\n'); print((w/'INITRD-DELTA.txt').read_text(),end='')
if __name__=='__main__': main()
