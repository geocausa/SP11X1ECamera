#!/usr/bin/env python3
import argparse, hashlib, os, pathlib, shutil, subprocess

REL='7.1.5-sp11-render-parity-v4+'

def a4(n): return (n + 3) & ~3

def parse_newc(data):
    pos=0; out=[]
    while pos + 110 <= len(data):
        if data[pos:pos+6] != b'070701':
            if any(data[pos:]):
                raise ValueError(f'non-zero non-newc data at {pos}')
            break
        h=data[pos:pos+110]
        mode=int(h[14:22],16); size=int(h[54:62],16); nsz=int(h[94:102],16)
        ns=pos+110; name=data[ns:ns+nsz-1].decode('utf-8','surrogateescape')
        ds=a4(ns+nsz); de=ds+size; nxt=a4(de)
        out.append((name,mode,data[ds:de],pos,nxt))
        if name == 'TRAILER!!!': break
        pos=nxt
    return out

def fmap(es):
    return {n:(m,len(p),hashlib.sha256(p).hexdigest()) for n,m,p,_,_ in es if n!='TRAILER!!!'}

def write_raw_zst(src, dst):
    dst.write_bytes(subprocess.check_output(['zstd','-q','-dc',str(src)]))
    os.chmod(dst,0o644)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--golden',required=True)
    ap.add_argument('--provider',required=True)
    ap.add_argument('--sensor',required=True)
    ap.add_argument('--modules-root',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--work',required=True)
    a=ap.parse_args()

    w=pathlib.Path(a.work); shutil.rmtree(w,ignore_errors=True); w.mkdir(parents=True)
    golden=pathlib.Path(a.golden); raw=subprocess.check_output(['zstd','-q','-dc',str(golden)])
    es=parse_newc(raw); tr=[e for e in es if e[0]=='TRAILER!!!']
    if len(tr)!=1: raise SystemExit(f'expected one Golden trailer, got {len(tr)}')
    off=tr[0][3]; prefix=raw[:off]; gm0={e[0]:e for e in es}

    root=w/'layer-root'; extra_parent=pathlib.Path(f'usr/lib/modules/{REL}/extra'); extra=extra_parent/'e002g'
    root_extra=root/extra; root_extra.mkdir(parents=True)
    orderrel=pathlib.Path('scripts/init-top/ORDER')
    loaderrel=pathlib.Path('scripts/init-top/zz-sp11-camera-e002g-native-bind')
    (root/loaderrel.parent).mkdir(parents=True,exist_ok=True)

    files={
        'sp11_camera_rpmh_regulator.ko': pathlib.Path(a.provider),
        'ov13858.ko': pathlib.Path(a.sensor),
    }
    for name,src in files.items():
        (root_extra/name).write_bytes(src.read_bytes()); os.chmod(root_extra/name,0o644)

    mr=pathlib.Path(a.modules_root)
    deps={
        'mc.ko': mr/'kernel/drivers/media/mc/mc.ko.zst',
        'videodev.ko': mr/'kernel/drivers/media/v4l2-core/videodev.ko.zst',
        'v4l2-async.ko': mr/'kernel/drivers/media/v4l2-core/v4l2-async.ko.zst',
        'v4l2-fwnode.ko': mr/'kernel/drivers/media/v4l2-core/v4l2-fwnode.ko.zst',
    }
    for name,src in deps.items(): write_raw_zst(src,root_extra/name)

    old=gm0[str(orderrel)][2]
    if b'zz-sp11-camera-e002g-native-bind' in old: raise SystemExit('Golden ORDER already contains E002g loader')
    add=b'/scripts/init-top/zz-sp11-camera-e002g-native-bind "$@"\n[ -e /conf/param.conf ] && . /conf/param.conf\n'
    (root/orderrel).write_bytes(old+add); os.chmod(root/orderrel,gm0[str(orderrel)][1]&0o7777)

    loader=f'''#!/bin/sh
case "${{1:-}}" in
  prereqs) exit 0 ;;
esac
log() {{ printf '<6>sp11-camera-e002g-initrd: %s\\n' "$*" > /dev/kmsg 2>/dev/null || true; }}
E=/usr/lib/modules/{REL}/extra/e002g
loadmod() {{
  p="$1"; n="$2"
  if [ -d "/sys/module/$n" ]; then log "$n already loaded"; return 0; fi
  /usr/bin/insmod "$p"
  rc=$?
  if [ "$rc" -eq 0 ]; then log "$n loaded"; return 0; fi
  log "$n load failed rc=$rc"; return $rc
}}
if ! loadmod "$E/sp11_camera_rpmh_regulator.ko" sp11_camera_rpmh_regulator; then
  log "provider unavailable; native sensor bind skipped"; exit 0
fi
D=/sys/bus/platform/devices/17500000.rsc:camera-rpmh-regulators/driver
if [ ! -L "$D" ]; then log "provider module loaded but provider is not bound; native sensor bind skipped"; exit 0; fi
log "camera RPMh provider bound"
loadmod "$E/mc.ko" mc || exit 0
loadmod "$E/videodev.ko" videodev || exit 0
loadmod "$E/v4l2-async.ko" v4l2_async || exit 0
loadmod "$E/v4l2-fwnode.ko" v4l2_fwnode || exit 0
if loadmod "$E/ov13858.ko" ov13858; then
  if [ -L /sys/bus/i2c/devices/1-0010/driver ]; then
    log "native OV13858 driver bound to 1-0010"
  else
    log "ov13858 module loaded but 1-0010 is not bound"
  fi
fi
exit 0
'''
    (root/loaderrel).write_text(loader); os.chmod(root/loaderrel,0o755)

    tracked=[root/extra_parent,root_extra,*sorted(root_extra.iterdir()),root/loaderrel,root/orderrel]
    for q in tracked: os.utime(q,(0,0),follow_symlinks=False)
    names='\n'.join([str(extra_parent),str(extra),*(str(extra/x.name) for x in sorted(root_extra.iterdir())),str(loaderrel),str(orderrel)])+'\n'
    cp=subprocess.run(['cpio','-o','-H','newc','--quiet','--reproducible'],cwd=root,input=names.encode(),stdout=subprocess.PIPE,check=True)
    combined=prefix+cp.stdout
    (w/'combined.cpio').write_bytes(combined)
    subprocess.run(['zstd','-q','-T1','-6','-f',str(w/'combined.cpio'),'-o',a.out],check=True)

    gm=fmap(es); cm=fmap(parse_newc(combined)); changes=[(n,gm.get(n),cm.get(n)) for n in sorted(set(gm)|set(cm)) if gm.get(n)!=cm.get(n)]
    expected={str(extra_parent),str(extra),*(str(extra/x) for x in files),*(str(extra/x) for x in deps),str(loaderrel),str(orderrel)}
    actual={x[0] for x in changes}
    if actual != expected:
        raise SystemExit(f'unexpected delta: only={sorted(actual-expected)} missing={sorted(expected-actual)}')
    if combined[:off] != prefix: raise SystemExit('Golden prefix mismatch')

    lines=[
      f'golden_sha256={hashlib.sha256(golden.read_bytes()).hexdigest()}',
      f'golden_uncompressed_prefix_bytes={off}',
      f'golden_uncompressed_prefix_sha256={hashlib.sha256(prefix).hexdigest()}',
      f'candidate_sha256={hashlib.sha256(pathlib.Path(a.out).read_bytes()).hexdigest()}',
      f'semantic_delta_count={len(changes)}',
    ]
    for n,b,c in changes: lines.append(f'{n}: {b} -> {c}')
    (w/'INITRD-DELTA.txt').write_text('\n'.join(lines)+'\n')
    print((w/'INITRD-DELTA.txt').read_text(),end='')

if __name__=='__main__': main()
