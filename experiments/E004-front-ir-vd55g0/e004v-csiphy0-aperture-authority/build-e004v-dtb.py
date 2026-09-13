#!/usr/bin/env python3
from pathlib import Path
import hashlib

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'e004o-ir-only-graph-authority'/'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb'
OUT=HERE/'x1e80100-microsoft-denali-sp11-e004v-ir-csiphy0-8k.dtb'

PARENT_SHA='fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742'
OLD=bytes.fromhex('000000000ace40000000000000001000')
NEW=bytes.fromhex('000000000ace40000000000000002000')
NEXT=bytes.fromhex('000000000ace60000000000000002000')

def sha(b):
    return hashlib.sha256(b).hexdigest()

src=PARENT.read_bytes()
if sha(src)!=PARENT_SHA:
    raise SystemExit('parent DTB drift')
if src.count(OLD)!=1:
    raise SystemExit(f'expected unique CSIPHY0 0x1000 tuple, got {src.count(OLD)}')
off=src.index(OLD)
if src[off+16:off+32]!=NEXT:
    raise SystemExit('CSIPHY1 does not immediately follow at 0x0ace6000 size 0x2000')
out=src[:off]+NEW+src[off+len(OLD):]
if len(out)!=len(src):
    raise SystemExit('DTB size changed')
diff=[i for i,(a,b) in enumerate(zip(src,out)) if a!=b]
if diff!=[off+14]:
    raise SystemExit(f'unexpected binary diff offsets: {diff}')
if src[off+12:off+16]!=bytes.fromhex('00001000'):
    raise SystemExit('old size cell mismatch')
if out[off+12:off+16]!=bytes.fromhex('00002000'):
    raise SystemExit('new size cell mismatch')
OUT.write_bytes(out)
print('E004V_BUILD=PASS')
print(f'PARENT_SHA256={sha(src)}')
print(f'OUTPUT_SHA256={sha(out)}')
print(f'CSIPHY0_TUPLE_OFFSET=0x{off:x}')
print(f'ONLY_CHANGED_BYTE_OFFSET=0x{diff[0]:x}')
print('OLD_RESOURCE=0x0ace4000+0x1000')
print('NEW_RESOURCE=0x0ace4000+0x2000')
print('NEXT_RESOURCE=0x0ace6000+0x2000')
