#!/usr/bin/env python3
from pathlib import Path
import hashlib, struct, sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
E004A=REPO/'experiments/E004-front-ir-vd55g0/e004a-windows-authority'
sys.path.insert(0,str(E004A))
from extract_windows_vd55g0 import _largest_regsetting, extract_patch_bytes

PACKAGE=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor_extension8380.inf_arm64_84ddd55dc933cac9/com.surface.sensormodule.aux_vd55g0_MSHW0492.bin')
PACKAGE_SHA='e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794'
PATCH_SHA='5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321'
FULL43_SHA='9664529aab0c65d6f3ae9778c8c31f54fa1675bde748fdaafc8e2d2ab4ea387c'
SAFE42_SHA='159647774f45331210044d0680e50bf16e8aaeeb8c3e98449d2cef7adeffacb2'

if hashlib.sha256(PACKAGE.read_bytes()).hexdigest()!=PACKAGE_SHA:
    raise SystemExit('Surface package identity drift')
patch=extract_patch_bytes(PACKAGE)
if len(patch)!=552 or hashlib.sha256(patch).hexdigest()!=PATCH_SHA:
    raise SystemExit('Surface patch identity drift')

_,rows=_largest_regsetting(PACKAGE)
final=rows[558:601]
if len(final)!=43 or any(x['operation']!=0 for x in final):
    raise SystemExit('final config row drift')
def seqhash(rr):
    return hashlib.sha256(b''.join(struct.pack('<HB',x['address'],x['data']) for x in rr)).hexdigest()
if seqhash(final)!=FULL43_SHA:
    raise SystemExit('full43 identity drift')
strobe=[x for x in final if x['address']==0x0468]
if len(strobe)!=1 or strobe[0]['data']!=0x02:
    raise SystemExit('strobe selector drift')
safe=[x for x in final if x['address']!=0x0468]
if len(safe)!=42 or seqhash(safe)!=SAFE42_SHA:
    raise SystemExit('safe42 identity drift')

lines=[
 '/* generated from exact Surface Windows package; do not edit */',
 '#ifndef SP11_VD55G0_WINDOWS_GENERATED_H',
 '#define SP11_VD55G0_WINDOWS_GENERATED_H',
 f'#define SP11_SURFACE_PATCH_SIZE {len(patch)}',
 f'#define SP11_SURFACE_PATCH_SHA256 "{PATCH_SHA}"',
 f'#define SP11_WINDOWS_FULL43_SHA256 "{FULL43_SHA}"',
 f'#define SP11_WINDOWS_SAFE42_SHA256 "{SAFE42_SHA}"',
 '#define SP11_WINDOWS_SAFE42_COUNT 42',
 '#define SP11_WINDOWS_ISOLATED_STROBE_REG 0x0468',
 '#define SP11_WINDOWS_ISOLATED_STROBE_VALUE 0x02',
 'struct sp11_reg8 { u16 reg; u8 data; };',
 'static const u8 sp11_surface_patch[SP11_SURFACE_PATCH_SIZE] = {',
]
for i in range(0,len(patch),16):
    lines.append('\t'+', '.join(f'0x{x:02x}' for x in patch[i:i+16])+',')
lines += ['};','static const struct sp11_reg8 sp11_windows_safe42[SP11_WINDOWS_SAFE42_COUNT] = {']
for x in safe:
    lines.append(f'\t{{ 0x{x["address"]:04x}, 0x{x["data"]:02x} }},')
lines += ['};','#endif','']
out=HERE/'surface-windows.generated.h'
out.write_text('\n'.join(lines))
print('WINDOWS_HEADER='+str(out))
print('PATCH_SHA256='+PATCH_SHA)
print('FULL43_SHA256='+FULL43_SHA)
print('SAFE42_SHA256='+SAFE42_SHA)
print('ISOLATED_STROBE=0x0468=0x02')
