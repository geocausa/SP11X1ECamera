#!/usr/bin/env python3
import argparse, hashlib, os, pathlib, stat, subprocess, tempfile

def a4(n): return (n + 3) & ~3

def parse_newc(data):
    pos = 0
    out = []
    while pos + 110 <= len(data):
        if data[pos:pos+6] != b'070701':
            # allow trailing padding only
            if any(data[pos:]):
                raise ValueError(f'non-zero non-newc data at {pos}')
            break
        h = data[pos:pos+110]
        mode = int(h[14:22],16)
        filesize = int(h[54:62],16)
        namesize = int(h[94:102],16)
        ns = pos + 110
        name = data[ns:ns+namesize-1].decode('utf-8','surrogateescape')
        ds = a4(ns + namesize)
        de = ds + filesize
        nxt = a4(de)
        out.append((name, mode, data[ds:de], pos, nxt))
        if name == 'TRAILER!!!':
            break
        pos = nxt
    return out

def final_map(entries):
    m = {}
    for name, mode, payload, _, _ in entries:
        if name == 'TRAILER!!!': continue
        m[name] = (mode, len(payload), hashlib.sha256(payload).hexdigest())
    return m

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--golden', required=True)
    ap.add_argument('--module', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--work', required=True)
    args=ap.parse_args()
    work=pathlib.Path(args.work); work.mkdir(parents=True,exist_ok=True)
    raw = subprocess.check_output(['zstd','-q','-dc',args.golden])
    ents=parse_newc(raw)
    trailer=[e for e in ents if e[0]=='TRAILER!!!']
    if len(trailer)!=1: raise SystemExit(f'expected one Golden trailer, got {len(trailer)}')
    trailer_off=trailer[0][3]
    golden_prefix=raw[:trailer_off]

    root=work/'layer-root'
    modrel=pathlib.Path('usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/sp11_ov13858_probe.ko')
    loaderrel=pathlib.Path('scripts/init-top/zz-sp11-camera-r2-probe')
    orderrel=pathlib.Path('scripts/init-top/ORDER')
    (root/modrel.parent).mkdir(parents=True,exist_ok=True)
    (root/loaderrel.parent).mkdir(parents=True,exist_ok=True)
    (root/modrel).write_bytes(pathlib.Path(args.module).read_bytes())
    os.chmod(root/modrel,0o644)

    # Recover the exact Golden ORDER content from cpio, then append one explicit call.
    gmap={e[0]:e for e in ents}
    old_order=gmap[str(orderrel)][2]
    add=b'/scripts/init-top/zz-sp11-camera-r2-probe "$@"\n[ -e /conf/param.conf ] && . /conf/param.conf\n'
    if b'zz-sp11-camera-r2-probe' in old_order:
        raise SystemExit('Golden ORDER unexpectedly already contains r2 loader')
    (root/orderrel).write_bytes(old_order+add)
    os.chmod(root/orderrel, gmap[str(orderrel)][1] & 0o7777)

    loader='''#!/bin/sh\ncase "${1:-}" in\n  prereqs) exit 0 ;;\nesac\nlog() { printf '<6>sp11-camera-r2-initrd: %s\\n' "$*" > /dev/kmsg 2>/dev/null || true; }\nM=/usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/sp11_ov13858_probe.ko\nif /usr/bin/insmod "$M"; then\n  log "probe-only module loaded"\nelse\n  rc=$?\n  log "probe-only module load failed rc=$rc; continuing without sensor probe"\nfi\nexit 0\n'''
    (root/loaderrel).write_text(loader)
    os.chmod(root/loaderrel,0o755)

    # Deterministic overlay archive: fixed mtimes and reproducible cpio inode/dev fields.
    for q in [root/modrel.parent, root/modrel, root/loaderrel, root/orderrel]:
        os.utime(q, (0, 0), follow_symlinks=False)

    layer=work/'layer.cpio'
    filelist='\n'.join([
        str(modrel.parent), str(modrel), str(loaderrel), str(orderrel)
    ])+'\n'
    p=subprocess.run(['cpio','-o','-H','newc','--quiet','--reproducible'],cwd=root,input=filelist.encode(),stdout=subprocess.PIPE,check=True)
    layer.write_bytes(p.stdout)
    combined=golden_prefix+p.stdout
    comb=work/'combined.cpio'; comb.write_bytes(combined)
    subprocess.run(['zstd','-q','-T0','-6','-f',str(comb),'-o',args.out],check=True)

    # Mechanical semantic verification over final cpio path map.
    cents=parse_newc(combined)
    gm=final_map(ents); cm=final_map(cents)
    allnames=sorted(set(gm)|set(cm))
    changes=[]
    for n in allnames:
        if gm.get(n)!=cm.get(n): changes.append((n,gm.get(n),cm.get(n)))
    expected={str(orderrel),str(loaderrel),str(modrel),str(modrel.parent)}
    changed_names={x[0] for x in changes}
    if changed_names != expected:
        raise SystemExit(f'unexpected semantic delta: {sorted(changed_names)} expected {sorted(expected)}')
    if combined[:trailer_off] != golden_prefix:
        raise SystemExit('Golden prefix mismatch')
    manifest=work/'INITRD-DELTA.txt'
    lines=[
        f'golden_sha256={hashlib.sha256(pathlib.Path(args.golden).read_bytes()).hexdigest()}',
        f'golden_uncompressed_prefix_bytes={trailer_off}',
        f'golden_uncompressed_prefix_sha256={hashlib.sha256(golden_prefix).hexdigest()}',
        f'candidate_sha256={hashlib.sha256(pathlib.Path(args.out).read_bytes()).hexdigest()}',
        'semantic_delta_count=4',
    ]
    for n,b,a in changes: lines.append(f'{n}: {b} -> {a}')
    manifest.write_text('\n'.join(lines)+'\n')
    print(manifest.read_text(),end='')
if __name__=='__main__': main()
