#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
E004A=REPO/'experiments/E004-front-ir-vd55g0/e004a-windows-authority'
sys.path.insert(0,str(E004A))
from extract_windows_vd55g0 import extract_patch_bytes

PACKAGE=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor_extension8380.inf_arm64_84ddd55dc933cac9/com.surface.sensormodule.aux_vd55g0_MSHW0492.bin')
PACKAGE_SHA='e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794'
PATCH_SHA='5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321'

if hashlib.sha256(PACKAGE.read_bytes()).hexdigest()!=PACKAGE_SHA:
    raise SystemExit('Surface package identity drift')
patch=extract_patch_bytes(PACKAGE)
if len(patch)!=552 or hashlib.sha256(patch).hexdigest()!=PATCH_SHA:
    raise SystemExit('Surface patch identity drift')

lines=[
    '/* generated from exact Surface Windows package; do not edit */',
    '#ifndef SP11_VD55G0_SURFACE_PATCH_GENERATED_H',
    '#define SP11_VD55G0_SURFACE_PATCH_GENERATED_H',
    f'#define SP11_SURFACE_PATCH_SIZE {len(patch)}',
    f'#define SP11_SURFACE_PATCH_SHA256 "{PATCH_SHA}"',
    'static const u8 sp11_surface_patch[SP11_SURFACE_PATCH_SIZE] = {',
]
for i in range(0,len(patch),16):
    lines.append('\t'+', '.join(f'0x{x:02x}' for x in patch[i:i+16])+',')
lines += ['};', '#endif', '']
out=HERE/'surface-patch.generated.h'
out.write_text('\n'.join(lines))
print('PATCH_HEADER='+str(out))
print('PATCH_BYTES='+str(len(patch)))
print('PATCH_SHA256='+PATCH_SHA)
