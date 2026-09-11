#!/usr/bin/env python3
"""Clean SP11 front-IMX681 two-anchor AWB calibration-factor reconstruction.

Inputs are the SHA-pinned shipped tuning blob and the physical 12-byte WB OTP window.
The implementation is intentionally profile-specific and fail-closed: it only accepts the
proven two-anchor Surface IMX681 sensorCalV1 layout and the two-record OTP layout.
"""
from __future__ import annotations
import hashlib,importlib.util,struct
from pathlib import Path
REPO=Path(__file__).resolve().parents[4]
QP=REPO/'tools'/'qti_parameter_bin.py'
spec=importlib.util.spec_from_file_location('qti_parameter_bin',QP); qti=importlib.util.module_from_spec(spec); spec.loader.exec_module(qti)
DEFAULT_TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin')
TUNING_SHA256='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
SENSORCAL_SHA256='39112df25cbdd8a368559514c787b5724b17f3f3c4647deba047f5b132eead8e'

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def add(a,b): return f32(f32(a)+f32(b))
def mul(a,b): return f32(f32(a)*f32(b))
def div(a,b): return f32(f32(a)/f32(b))
def bits(x): return struct.unpack('<I',struct.pack('<f',f32(x)))[0]

def _sensorcal(tuning_path:Path):
    b=tuning_path.read_bytes()
    if hashlib.sha256(b).hexdigest()!=TUNING_SHA256: raise ValueError('front tuning SHA drift')
    p=qti.parse(tuning_path); e=next((x for x in p['entries'] if x['name']=='sensorCalV1'),None)
    if not e: raise ValueError('sensorCalV1 absent')
    raw=bytes.fromhex(e['raw_hex'])
    if len(raw)!=172 or hashlib.sha256(raw).hexdigest()!=SENSORCAL_SHA256: raise ValueError('sensorCalV1 payload drift')
    # Proven Surface two-anchor payload fields.  The values are checked against the Windows
    # ComputeCalFactors bins, so a future layout/profile change fails closed.
    low_cct,high_cct=struct.unpack_from('<ff',raw,0x1c)
    low_rg,low_bg,high_rg,high_bg=struct.unpack_from('<ffff',raw,0x34)
    if (bits(low_cct),bits(high_cct))!=(0x452f0000,0x45cb2000): raise ValueError('sensorCal CCT anchors drift')
    if not (2575.0 <= low_cct < 3425.0 and high_cct >= 6000.0): raise ValueError('anchors left proven Windows bins')
    if tuple(bits(x) for x in (low_rg,low_bg,high_rg,high_bg))!=(0x3f563583,0x3ebc2efd,0x3f182603,0x3f1725c4):
        raise ValueError('sensorCal ratio anchors drift')
    return {'low':(f32(low_cct),f32(low_rg),f32(low_bg)),'high':(f32(high_cct),f32(high_rg),f32(high_bg))}

def compute(raw12:bytes,tuning_path:Path=DEFAULT_TUNING):
    if len(raw12)!=12: raise ValueError('WB OTP window must be 12 bytes')
    u=struct.unpack('<6H',raw12)
    low=(f32(u[0]/1023.0),f32(u[1]/1023.0)); high=(f32(u[3]/1023.0),f32(u[4]/1023.0))
    # The third fields are part of the WB formatter contract but not the RG/BG calibration-factor input.
    third=(f32(u[2]/1023.0),f32(u[5]/1023.0))
    t=_sensorcal(Path(tuning_path)); tl=(t['low'][1],t['low'][2]); th=(t['high'][1],t['high'][2])
    low_factor=(div(low[0],tl[0]),div(low[1],tl[1]))
    high_factor=(div(high[0],th[0]),div(high[1],th[1]))
    mid_otp=(mul(add(low[0],high[0]),0.5),mul(add(low[1],high[1]),0.5))
    mid_tun=(mul(add(tl[0],th[0]),0.5),mul(add(tl[1],th[1]),0.5))
    mid_factor=(div(mid_otp[0],mid_tun[0]),div(mid_otp[1],mid_tun[1]))
    # Static ComputeCalFactors bin/fill behavior for this exact two-anchor profile:
    # high bucket fills slots 0..3, the count==2 midpoint fills 4..6, low bucket fills 7..9.
    table=(high_factor,)*4+(mid_factor,)*3+(low_factor,)*3
    reciprocal=tuple((div(1.0,p[0]),div(1.0,p[1])) for p in table)
    return {'raw_u16':u,'otp_low':low,'otp_high':high,'third':third,'tuning':t,
            'low_factor':low_factor,'mid_factor':mid_factor,'high_factor':high_factor,
            'table':table,'reciprocal':reciprocal}
