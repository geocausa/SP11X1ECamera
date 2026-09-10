#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,pefile,struct

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
EXPECTED_DLL='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'

def sha(b): return hashlib.sha256(b).hexdigest()

b=DLL.read_bytes()
assert sha(b)==EXPECTED_DLL
pe=pefile.PE(data=b,fast_load=True); base=pe.OPTIONAL_HEADER.ImageBase
ranges=[
 ('accumulator',0x1806d0dc0,0x1806d0f70,'df0ecd1018d5d941e57df6bb956f290747c0444ecf8bc033945003bfbea18a5a'),
 ('finalizer',0x1806d1090,0x1806d1920,'375d2b6544312f9d8c371360343b0258e4c16354bc92379d2821aaec3b0c9f33'),
 ('cawb_fallback',0x180692848,0x180693058,'aa03f830c5a7f8b549cf29de5d84c3f5c630d3d376194671610ce432a60aa869'),
]
for name,a,z,h in ranges:
    off=pe.get_offset_from_rva(a-base)
    assert sha(b[off:off+z-a])==h,name

def code(a,n):
    off=pe.get_offset_from_rva(a-base)
    return b[off:off+n]

# Exact critical bytes include:
# ldr s18,[x19,#0x58]; fcmp s18,#0; b.eq; weighted divide path;
# b; stur xzr,[x20,#0x4c]
assert sha(code(0x1806d10ac,44))=='e1b7963f0bed00b3df023a905670c3659fef050572685bf255debcbc0519cb9f'
# Higher CAWB coordinate <=0 branch through previous-gains fallback neighborhood.
assert sha(code(0x180692c9c,368))=='7a31f3b5b44c5b48aa83e35b335fa9c991674ed736d218e1afd814c98fc222aa'
assert b'Computed Decision Point rg : %f, bg :%f, previous AWB gains will be used' in b

ac=json.loads((BASE/'ac-clean-cct-reconstruction/RESULT.json').read_text())
assert ac['temporal']['previous_default_xy_bits']==['0x3f1129ca','0x3f00e486']

# Recompute P03 for the pinned previous pair and prove publication.
import importlib.util
p=BASE/'ac-clean-cct-reconstruction/cct_model.py'
s=importlib.util.spec_from_file_location('dq_cct',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
def fb(u): return struct.unpack('<f',struct.pack('<I',u))[0]
x,y=fb(0x3f1129ca),fb(0x3f00e486)
r=m.P03(float(x),float(y))
assert m.bits(r['cct'])==0x459c3ffb
assert int(m.f32(r['cct']))==4999
fx,fy,fc=m.temporal(x,y,x,y)
assert m.bits(fx)==0x3f1129ca and m.bits(fy)==0x3f00e486
assert m.bits(fc)==0x459c3ffb

print('DQ_DLL_PIN=PASS')
print('DQ_ZERO_WEIGHT_ZERO_TARGET_BRANCH=PASS')
print('DQ_PREVIOUS_AWB_HOLD_BRANCH=PASS')
print('DQ_STARTUP_HELD_CCT=4999')
print('DQ_VERIFY=PASS')
