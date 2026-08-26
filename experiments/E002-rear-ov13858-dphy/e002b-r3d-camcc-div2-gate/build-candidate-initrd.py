#!/usr/bin/env python3
import argparse,hashlib,os,pathlib,subprocess
def a4(n): return (n+3)&~3
def parse(data):
 p=0;o=[]
 while p+110<=len(data):
  if data[p:p+6]!=b'070701':
   if any(data[p:]): raise ValueError(p)
   break
  h=data[p:p+110];m=int(h[14:22],16);sz=int(h[54:62],16);nsz=int(h[94:102],16);ns=p+110;n=data[ns:ns+nsz-1].decode();ds=a4(ns+nsz);de=ds+sz;nx=a4(de);o.append((n,m,data[ds:de],p,nx));p=nx
  if n=='TRAILER!!!': break
 return o
def fmap(es): return {n:(m,len(b),hashlib.sha256(b).hexdigest()) for n,m,b,_,_ in es if n!='TRAILER!!!'}
def main():
 a=argparse.ArgumentParser();a.add_argument('--golden',required=True);a.add_argument('--provider',required=True);a.add_argument('--diag',required=True);a.add_argument('--out',required=True);a.add_argument('--work',required=True);x=a.parse_args()
 w=pathlib.Path(x.work);w.mkdir(parents=True,exist_ok=True);raw=subprocess.check_output(['zstd','-q','-dc',x.golden]);es=parse(raw);tr=[e for e in es if e[0]=='TRAILER!!!'];off=tr[0][3];prefix=raw[:off];gm0={e[0]:e for e in es}
 root=w/'root';extra=pathlib.Path('usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra');pr=extra/'sp11_camera_rpmh_regulator.ko';dr=extra/'sp11_mclk_diag.ko';lr=pathlib.Path('scripts/init-top/zz-sp11-camera-r3d-mclk');order=pathlib.Path('scripts/init-top/ORDER');(root/extra).mkdir(parents=True,exist_ok=True);(root/lr.parent).mkdir(parents=True,exist_ok=True)
 (root/pr).write_bytes(pathlib.Path(x.provider).read_bytes());(root/dr).write_bytes(pathlib.Path(x.diag).read_bytes());os.chmod(root/pr,0o644);os.chmod(root/dr,0o644)
 old=gm0[str(order)][2];add=b'/scripts/init-top/zz-sp11-camera-r3d-mclk "$@"\n[ -e /conf/param.conf ] && . /conf/param.conf\n';(root/order).write_bytes(old+add);os.chmod(root/order,gm0[str(order)][1]&0o7777)
 loader='''#!/bin/sh\ncase "${1:-}" in prereqs) exit 0 ;; esac\nlog(){ printf '<6>sp11-camera-r3d-initrd: %s\\n' "$*" >/dev/kmsg 2>/dev/null || true; }\nP=/usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/sp11_camera_rpmh_regulator.ko\nD=/usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/sp11_mclk_diag.ko\nB=/sys/bus/platform/devices/17500000.rsc:camera-rpmh-regulators/driver\nif /usr/bin/insmod "$P" && [ -L "$B" ]; then\n log "provider bound; loading NO-POWER MCLK diagnostic"\n /usr/bin/insmod "$D" && log "MCLK diagnostic loaded" || log "MCLK diagnostic load failed rc=$?"\nelse\n log "provider unavailable; MCLK diagnostic skipped"\nfi\nexit 0\n''';(root/lr).write_text(loader);os.chmod(root/lr,0o755)
 for q in [root/extra,root/pr,root/dr,root/lr,root/order]: os.utime(q,(0,0),follow_symlinks=False)
 names='\n'.join(map(str,[extra,pr,dr,lr,order]))+'\n';cp=subprocess.run(['cpio','-o','-H','newc','--quiet','--reproducible'],cwd=root,input=names.encode(),stdout=subprocess.PIPE,check=True).stdout;comb=prefix+cp;(w/'combined.cpio').write_bytes(comb);subprocess.run(['zstd','-q','-T0','-6','-f',str(w/'combined.cpio'),'-o',x.out],check=True)
 gm=fmap(es);cm=fmap(parse(comb));chg=[(n,gm.get(n),cm.get(n)) for n in sorted(set(gm)|set(cm)) if gm.get(n)!=cm.get(n)];exp={str(extra),str(pr),str(dr),str(lr),str(order)}
 if {z[0] for z in chg}!=exp or comb[:off]!=prefix: raise SystemExit('delta verification failed')
 lines=[f'golden_sha256={hashlib.sha256(pathlib.Path(x.golden).read_bytes()).hexdigest()}',f'golden_uncompressed_prefix_bytes={off}',f'candidate_sha256={hashlib.sha256(pathlib.Path(x.out).read_bytes()).hexdigest()}','semantic_delta_count=5']+[f'{n}: {b} -> {c}' for n,b,c in chg];(w/'INITRD-DELTA.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__':main()
