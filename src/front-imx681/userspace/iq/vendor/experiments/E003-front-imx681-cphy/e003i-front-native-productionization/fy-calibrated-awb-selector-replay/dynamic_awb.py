#!/usr/bin/env python3
"""SP11 front IMX681 OTP-calibrated AWB selector + EL replay.

Profile-specific clean reconstruction of the CAWBCtrlV1 -> CSFStatDistV1 slot
selection consumed by CTrigleAdjV1. The geometry is recovered from the pinned
Windows DeviceMFT and the shipped refPtV1 tuning payload. EL's already-proven
GainAdj mesh/publication implementation remains unchanged.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ELP=BASE/'el-calibrated-awb-scalar-join'/'awb_scalar.py'
EJ=BASE/'ej-clean-awb-cal-factor-replay'/'RESULT.json'
EJCAL=BASE/'ej-clean-awb-cal-factor-replay'/'cal_factors.py'
EK=BASE/'ek-linux-front-awb-otp-read-gate'/'RESULT.json'
EKOTP=BASE/'ek-linux-front-awb-otp-read-gate'/'runtime-output'/'OTP-LINE.txt'
REPO=HERE.parents[3]
TUNING=REPO/'local-authority/project-root/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin'
TUNING_SHA256='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
REFPT_SHA256='0cb86433c9f33101f104aeb1071d6ed0a73c11bba6818cb69149e361dbf9bcc5'
SFDIST_SHA256='1e77f04b2ccf89f944d19ec28214fc26ad73907f8aea76076b25060669462076'

def _load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
EL=_load(ELP,'fy_el')
EJC=_load(EJCAL,'fy_ej_cal')
GA=EL.GA

def f32(x): return GA.f32(x)
def add(a,b): return GA.add(a,b)
def sub(a,b): return GA.sub(a,b)
def mul(a,b): return GA.mul(a,b)
def div(a,b): return GA.div(a,b)
def bits(x): return EL.bits(x)
def frombits(u): return EL.frombits(u)

def stored_calibration_table():
    ek=json.loads(EK.read_text())
    if (ek.get('status')!='PASS_LIVE_LINUX_PHYSICAL_OTP' or
        not ek.get('live_read_proven') or not ek.get('windows_ei_byte_exact')):
        raise RuntimeError('EK Linux physical OTP authority missing')
    line=EKOTP.read_text().strip()
    marker='SP11 EK AWB OTP 0x0941..0x094c:'
    if marker not in line:
        raise RuntimeError('EK OTP line format drift')
    raw=bytes(int(x,16) for x in line.split(marker,1)[1].strip().split())
    if len(raw)!=12 or hashlib.sha256(raw).hexdigest()!=ek.get('expected_ei_sha256'):
        raise RuntimeError('EK OTP bytes drift')
    z=EJC.compute(raw,TUNING)
    table=tuple((f32(a),f32(b)) for a,b in z['table'])
    ej=json.loads(EJ.read_text())
    if ej.get('status')!='PASS_10_OF_10_BIT_EXACT' or not ej.get('linux_runtime_eeprom_read_bound'):
        raise RuntimeError('EJ clean calibration authority missing')
    expected=[]
    for name in ('high','midpoint','low'):
        rec=ej['factor_regions'][name]
        pair=tuple(frombits(int(x,16)) for x in rec['bits'])
        expected.extend([pair]*len(rec['slots']))
    if tuple((bits(a),bits(b)) for a,b in table)!=tuple((bits(a),bits(b)) for a,b in expected):
        raise RuntimeError('EJ clean factor table drift')
    return table

class Line:
    __slots__=('m','c','sign','length')
    def __init__(self,m,c,sign=-1.0,length=0.0):
        self.m=f32(m);self.c=f32(c);self.sign=f32(sign);self.length=f32(length)
    def eval(self,x,y):
        return add(add(mul(self.m,x),mul(-1.0,y)),self.c)

class CalibrationSlotSelector:
    """Clean profile-pinned CSFStatDistV1 selector for the normal front path."""
    BOUNDARY_PAIRS=((0,1),(1,2),(2,3),(3,5),(3,5),(5,7),(7,8),(8,9))
    SEARCH_POINT=(0,1,2,3,5,7,8,9)
    SEARCH_BOUNDARY=(0,1,2,2,3,5,6,7)
    SLOT_PAIRS=((0,1),(1,2),(2,3),(3,5),(4,6),(5,7),(7,8),(8,9))

    def __init__(self,parsed):
        if hashlib.sha256(TUNING.read_bytes()).hexdigest()!=TUNING_SHA256:
            raise RuntimeError('front tuning SHA drift')
        ref=next(e for e in parsed['entries'] if e['name']=='refPtV1')
        raw=bytes.fromhex(ref['raw_hex'])
        if len(raw)!=144 or hashlib.sha256(raw).hexdigest()!=REFPT_SHA256:
            raise RuntimeError('refPtV1 payload drift')
        vals=struct.unpack_from('<20f',raw,0x18)
        raw_points=[(f32(vals[i]),f32(vals[i+1])) for i in range(0,20,2)]
        # Windows CAWBCtrlV1 applies the same-device stored ComputeCalFactors
        # table to refPtV1 before CSFStatDistV1 constructs any boundary/search
        # geometry.  FX captured this configured object directly.
        factors=stored_calibration_table()
        self.points=[(mul(p[0],f[0]),mul(p[1],f[1])) for p,f in zip(raw_points,factors)]
        self.boundaries=[self._segment(a,b) for a,b in self.BOUNDARY_PAIRS]
        self.search=[]
        for pi,bi in zip(self.SEARCH_POINT,self.SEARCH_BOUNDARY):
            p=self.points[pi];b=self.boundaries[bi]
            m=f32(1000.0) if abs(float(b.m))<1e-9 else div(-1.0,b.m)
            self.search.append(Line(m,sub(p[1],mul(p[0],m)),b.sign))
        # Windows Configure always replaces search line 4 with its F-bound:
        # intersection(perp(B3)@P3, perp(B5)@P7) -> line through P5.
        p3,p5,p7=self.points[3],self.points[5],self.points[7]
        b3,b5=self.boundaries[3],self.boundaries[5]
        m3=div(-1.0,b3.m); c3=sub(p3[1],mul(p3[0],m3))
        m5=div(-1.0,b5.m); c5=sub(p7[1],mul(p7[0],m5))
        den=sub(m5,m3)
        ix=div(sub(c3,c5),den)
        iy=div(sub(mul(m5,c3),mul(c5,m3)),den)
        fm=div(sub(iy,p5[1]),sub(ix,p5[0]))
        fc=sub(p5[1],mul(fm,p5[0]))
        self.search[4]=Line(fm,fc,self.search[4].sign)
        self.f_intersection=(ix,iy)
        sf=next(e for e in parsed['entries'] if e['name']=='SFDistWVV1')
        sfraw=bytes.fromhex(sf['raw_hex'])
        if len(sfraw)!=40 or hashlib.sha256(sfraw).hexdigest()!=SFDIST_SHA256:
            raise RuntimeError('SFDistWVV1 payload drift')
        dist=f32(math.sqrt(float(add(mul(sub(ix,p5[0]),sub(ix,p5[0])),
                                      mul(sub(iy,p5[1]),sub(iy,p5[1]))))))
        self.f_distance=dist
        if not (dist > f32(0.30)):
            raise RuntimeError('F-bound distance left pinned no-shift regime')

    def _segment(self,a,b):
        ax,ay=self.points[a];bx,by=self.points[b]
        dx=sub(bx,ax);dy=sub(by,ay)
        den=dx if abs(float(dx))>=1e-9 else f32(0.001)
        m=div(dy,den);c=sub(by,mul(bx,m))
        sign=f32(1.0 if (ax<bx and ay<by) else -1.0)
        length=add(mul(dx,dx),mul(dy,dy))
        return Line(m,c,sign,length)

    def _region(self,x,y):
        i=4;state=0
        while i!=8:
            z=self.search[i].eval(x,y)
            if abs(float(self.search[i].sign)-1.0)<1e-9:
                z=f32(-z)
            if z>=0.0:
                if z<=0.0: return i
                if state==1: return i
                state=2;i+=1
            else:
                if state==2: return i
                state=1;i-=1
                if i==-1:return i
        return i

    def _map(self,group,t):
        t=f32(min(1.0,max(0.0,float(t))))
        return self.SLOT_PAIRS[group][1 if f32(0.5)<t else 0]

    def _segment_t(self,a,b,group,x,y):
        ax,ay=self.points[a];bx,by=self.points[b]
        da=add(mul(sub(x,ax),sub(x,ax)),mul(sub(y,ay),sub(y,ay)))
        db=add(mul(sub(x,bx),sub(x,bx)),mul(sub(y,by),sub(y,by)))
        L=self.boundaries[group].length
        t=div(mul(add(sub(da,db),L),0.5),L)
        return t,self._map(group,t)

    def _wedge(self,li,lj,group,x,y):
        a=self.search[li];b=self.search[lj]
        ea=a.eval(x,y);eb=b.eval(x,y)
        qa=div(mul(ea,ea),add(mul(a.m,a.m),1.0))
        qb=div(mul(eb,eb),add(mul(b.m,b.m),1.0))
        if qa<=0.0:
            t=f32(1.0 if qb<=0.0 else 0.0)
        else:
            t=div(1.0,add(f32(math.sqrt(float(div(qb,qa)))),1.0))
        return t,self._map(group,t)

    def select(self,rg,bg):
        x,y=map(f32,(rg,bg))
        region=self._region(x,y)
        if region<0:return {'slot':0,'region':region,'ratio':f32(0.0)}
        if region==8:return {'slot':9,'region':region,'ratio':f32(1.0)}
        if region==0:t,s=self._segment_t(0,1,0,x,y)
        elif region==1:t,s=self._segment_t(1,2,1,x,y)
        elif region==2:t,s=self._segment_t(2,3,2,x,y)
        elif region==3:t,s=self._wedge(3,4,3,x,y)
        elif region==4:t,s=self._segment_t(3,5,3,x,y)
        elif region==5:t,s=self._wedge(4,5,5,x,y)
        elif region==6:t,s=self._segment_t(7,8,6,x,y)
        elif region==7:t,s=self._segment_t(8,9,7,x,y)
        else: raise RuntimeError(f'unexpected CSFStatDist region {region}')
        return {'slot':s,'region':region,'ratio':t}

def calibration_scales():
    o=json.loads(EJ.read_text())
    if o.get('status')!='PASS_10_OF_10_BIT_EXACT' or not o.get('linux_runtime_eeprom_read_bound'):
        raise RuntimeError('EJ/EK calibration authority not live-bound')
    groups=o['factor_regions']
    def rec(name):
        rb,bb=[int(x,16) for x in groups[name]['bits']]
        return div(1.0,frombits(rb)),div(1.0,frombits(bb))
    hi,mid,lo=rec('high'),rec('midpoint'),rec('low')
    active=o['active_reciprocal_scale_bits']
    if (bits(hi[0]),bits(hi[1]))!=(int(active['rg'],16),int(active['bg'],16)):
        raise RuntimeError('EJ active reciprocal drift')
    return (hi,)*4+(mid,)*3+(lo,)*3

class DynamicCalibratedAWB:
    def __init__(self):
        self.core=EL.CalibratedAWB()
        self.selector=CalibrationSlotSelector(self.core.tuning.parsed)
        self.scales=calibration_scales()
    def reset(self): self.core.reset()
    def run(self,rg,bg,lux,cct,predictive_gain=1.0):
        sel=self.selector.select(rg,bg)
        self.core.cal_rg,self.core.cal_bg=self.scales[sel['slot']]
        out=self.core.run(rg,bg,lux,cct,predictive_gain)
        out['calibration_slot']=sel['slot']
        out['calibration_region']=sel['region']
        out['calibration_ratio']=sel['ratio']
        out['calibration_scale_bits']=[f'0x{bits(self.core.cal_rg):08x}',f'0x{bits(self.core.cal_bg):08x}']
        return out
