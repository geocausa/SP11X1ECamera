#!/usr/bin/env python3
from pathlib import Path
import hashlib,pefile,struct
H=Path(__file__).resolve().parent
DLL=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
def need(v,m):
    if not v: raise AssertionError(m)
need(hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA,'DLL drift')
pe=pefile.PE(str(DLL))
# Pin selector call site: fmov s0,s8; mov w2,w22; str s13,[x19,#0x34]; mov x1,x19; mov x0,x20; bl quantizer.
b=pe.get_data(0x6c4220,0x1c)
need(hashlib.sha256(b).hexdigest()=='f93bcbbe87191f65c2dc81d1e531a1ea4964e249e8aecb12c186e7029caab6e1','selector call bytes')
o=(H/'oracle.cmd').read_text(); h=(H/'holder.ps1').read_text()
need('QcDeviceMFT8380+0x6c4234' in o,'selector bp')
need('CSFSTATDIST-OBJECT.bin' in o and '@x20 @x20+0x23f' in o,'object dump')
need(o.count('bp QcDeviceMFT8380+')==1,'one breakpoint')
need('.detach; q' in o,'detach after first hit')
need('Surface Camera Front' in h and h.count('StartAsync')==1 and h.count('StopAsync')==1,'one holder stream')
need('WAIT_START' in h and 'Remove-Item $Go,$Ready,$Done' in h,'holder gates')
print('FX_PINNED_SELECTOR_CALL=PASS')
print('FX_FIRST_HIT_OBJECT_DUMP=PASS')
print('FX_ONE_STREAM_HOLDER=PASS')
print('FX_VERIFY=PASS')
