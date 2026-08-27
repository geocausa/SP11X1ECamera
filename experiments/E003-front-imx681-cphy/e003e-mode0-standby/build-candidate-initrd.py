#!/usr/bin/env python3
import argparse, hashlib, os, pathlib, shutil, subprocess
REL='7.1.5-sp11-render-parity-v4+'
def parse_newc(data):
    out=[]; pos=0
    while pos+110<=len(data):
        if data[pos:pos+6] != b'070701': raise SystemExit(f'bad cpio magic at {pos}')
        h=data[pos:pos+110]; vals=[int(h[6+i*8:14+i*8],16) for i in range(13)]
        mode=vals[1]; size=vals[6]; namesize=vals[11]
        ns=pos+110; ne=ns+namesize; name=data[ns:ne-1].decode(); ds=(ne+3)&~3; de=ds+size; nxt=(de+3)&~3
        out.append((name,mode,data[ds:de],pos,nxt))
        if name=='TRAILER!!!': break
        pos=nxt
    return out
def fmap(es): return {n:(m,len(p),hashlib.sha256(p).hexdigest()) for n,m,p,_,_ in es if n!='TRAILER!!!'}
def raw_zst(src,dst): dst.write_bytes(subprocess.check_output(['zstd','-q','-dc',str(src)])); os.chmod(dst,0o644)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--base',required=True); ap.add_argument('--sensor',required=True); ap.add_argument('--camss',required=True)
    ap.add_argument('--modules-root',required=True); ap.add_argument('--out',required=True); ap.add_argument('--work',required=True)
    a=ap.parse_args(); w=pathlib.Path(a.work); shutil.rmtree(w,ignore_errors=True); w.mkdir(parents=True)
    base=pathlib.Path(a.base); raw=subprocess.check_output(['zstd','-q','-dc',str(base)]); es=parse_newc(raw)
    trailers=[e for e in es if e[0]=='TRAILER!!!']
    if len(trailers)!=1: raise SystemExit('bad base trailer')
    prefix=raw[:trailers[0][3]]; bm0={e[0]:e for e in es}
    root=w/'layer-root'; extra=pathlib.Path(f'usr/lib/modules/{REL}/extra/e003e-mode0-standby'); re=root/extra; re.mkdir(parents=True)
    (re/'qcom-camss.ko').write_bytes(pathlib.Path(a.camss).read_bytes()); os.chmod(re/'qcom-camss.ko',0o644)
    (re/'imx681.ko').write_bytes(pathlib.Path(a.sensor).read_bytes()); os.chmod(re/'imx681.ko',0o644)
    mr=pathlib.Path(a.modules_root)
    deps={
      'videobuf2-common.ko': mr/'kernel/drivers/media/common/videobuf2/videobuf2-common.ko.zst',
      'videobuf2-memops.ko': mr/'kernel/drivers/media/common/videobuf2/videobuf2-memops.ko.zst',
      'videobuf2-v4l2.ko': mr/'kernel/drivers/media/common/videobuf2/videobuf2-v4l2.ko.zst',
      'videobuf2-dma-sg.ko': mr/'kernel/drivers/media/common/videobuf2/videobuf2-dma-sg.ko.zst',
      'v4l2-cci.ko': mr/'kernel/drivers/media/v4l2-core/v4l2-cci.ko.zst',
    }
    for name,src in deps.items(): raw_zst(src,re/name)
    order=pathlib.Path('scripts/init-top/ORDER'); hook=pathlib.Path('scripts/init-top/zz-sp11-camera-e003e-mode0-standby'); (root/hook.parent).mkdir(parents=True,exist_ok=True)
    old=bm0[str(order)][2]; add=b'/scripts/init-top/zz-sp11-camera-e003e-mode0-standby "$@"\n[ -e /conf/param.conf ] && . /conf/param.conf\n'; (root/order).write_bytes(old+add); os.chmod(root/order,bm0[str(order)][1]&0o7777)
    loader=f'''#!/bin/sh
case "${{1:-}}" in prereqs) exit 0 ;; esac
log() {{ printf '<6>sp11-camera-e003e-initrd: %s\\n' "$*" > /dev/kmsg 2>/dev/null || true; }}
E=/usr/lib/modules/{REL}/extra/e003e-mode0-standby
loadmod() {{ p="$1"; n="$2"; [ -d "/sys/module/$n" ] && {{ log "$n already loaded"; return 0; }}; /usr/bin/insmod "$p"; rc=$?; [ "$rc" -eq 0 ] && {{ log "$n loaded"; return 0; }}; log "$n load failed rc=$rc"; return $rc; }}
log "loading E003d idle C-PHY graph; IMX681 streaming remains hard-blocked"
loadmod "$E/videobuf2-common.ko" videobuf2_common || exit 0
loadmod "$E/videobuf2-memops.ko" videobuf2_memops || exit 0
loadmod "$E/videobuf2-v4l2.ko" videobuf2_v4l2 || exit 0
loadmod "$E/videobuf2-dma-sg.ko" videobuf2_dma_sg || exit 0
loadmod "$E/qcom-camss.ko" qcom_camss || exit 0
loadmod "$E/v4l2-cci.ko" v4l2_cci || exit 0
loadmod "$E/imx681.ko" imx681 || exit 0
i=0
while [ "$i" -lt 100 ]; do
  if [ -L /sys/bus/i2c/devices/3-0010/driver ]; then log "IMX681 driver bound to 3-0010"; exit 0; fi
  i=$((i+1)); sleep 0.05
done
log "imx681 loaded but 3-0010 did not bind within 5s"
exit 0
'''
    (root/hook).write_text(loader); os.chmod(root/hook,0o755)
    tracked=[re,*sorted(re.iterdir()),root/hook,root/order]
    for q in tracked: os.utime(q,(0,0),follow_symlinks=False)
    names='\n'.join([str(extra),*(str(extra/x.name) for x in sorted(re.iterdir())),str(hook),str(order)])+'\n'
    cp=subprocess.run(['cpio','-o','-H','newc','--quiet','--reproducible'],cwd=root,input=names.encode(),stdout=subprocess.PIPE,check=True)
    combined=prefix+cp.stdout; (w/'combined.cpio').write_bytes(combined); subprocess.run(['zstd','-q','-T1','-6','-f',str(w/'combined.cpio'),'-o',a.out],check=True)
    bm=fmap(es); cm=fmap(parse_newc(combined)); changes=[(n,bm.get(n),cm.get(n)) for n in sorted(set(bm)|set(cm)) if bm.get(n)!=cm.get(n)]
    expected={str(extra),str(extra/'qcom-camss.ko'),str(extra/'imx681.ko'),*(str(extra/x) for x in deps),str(hook),str(order)}; actual={x[0] for x in changes}
    if actual!=expected: raise SystemExit(f'unexpected delta only={sorted(actual-expected)} missing={sorted(expected-actual)}')
    lines=[f'base_sha256={hashlib.sha256(base.read_bytes()).hexdigest()}',f'candidate_sha256={hashlib.sha256(pathlib.Path(a.out).read_bytes()).hexdigest()}',f'semantic_delta_count={len(changes)}']
    for n,b,c in changes: lines.append(f'{n}: {b} -> {c}')
    (w/'INITRD-DELTA.txt').write_text('\n'.join(lines)+'\n'); print((w/'INITRD-DELTA.txt').read_text(),end='')
if __name__=='__main__': main()
