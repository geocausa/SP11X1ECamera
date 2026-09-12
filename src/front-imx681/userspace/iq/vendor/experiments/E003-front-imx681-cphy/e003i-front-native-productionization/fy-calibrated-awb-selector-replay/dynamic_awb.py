#!/usr/bin/env python3
"""SP11 front IMX681 OTP-calibrated AWB selector + EL replay.

Profile-specific clean reconstruction of the CAWBCtrlV1 -> CSFStatDistV1 slot
selection consumed by CTrigleAdjV1. HH supplies the decoded selector points,
calibration scales and GainAdj topology; EL's proven publication math remains unchanged.
"""
from __future__ import annotations
import importlib.util,json,math,os,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ELP=BASE/'el-calibrated-awb-scalar-join'/'awb_scalar.py'

def _load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
EL=_load(ELP,'fy_el')
GA=EL.GA

def f32(x): return GA.f32(x)
def add(a,b): return GA.add(a,b)
def sub(a,b): return GA.sub(a,b)
def mul(a,b): return GA.mul(a,b)
def div(a,b): return GA.div(a,b)
def bits(x): return EL.bits(x)
def frombits(u): return EL.frombits(u)

def _awb_authority(): return json.loads(Path(os.environ['E003I_IQ_AUTHORITY']).read_text())['awb']
def stored_calibration_table():
    a=_awb_authority();return tuple((frombits(int(x[0],16)),frombits(int(x[1],16))) for x in a['selector_scales_bits'])

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

    def __init__(self,parsed=None):
        a=_awb_authority();self.points=[(frombits(int(x[0],16)),frombits(int(x[1],16))) for x in a['selector_points_bits']]
        self.boundaries=[self._segment(a0,b0) for a0,b0 in self.BOUNDARY_PAIRS]
        self.search=[]
        for pi,bi in zip(self.SEARCH_POINT,self.SEARCH_BOUNDARY):
            p=self.points[pi];b=self.boundaries[bi]
            m=f32(1000.0) if abs(float(b.m))<1e-9 else div(-1.0,b.m)
            self.search.append(Line(m,sub(p[1],mul(p[0],m)),b.sign))
        p3,p5,p7=self.points[3],self.points[5],self.points[7]
        b3,b5=self.boundaries[3],self.boundaries[5]
        m3=div(-1.0,b3.m); c3=sub(p3[1],mul(p3[0],m3))
        m5=div(-1.0,b5.m); c5=sub(p7[1],mul(p7[0],m5))
        den=sub(m5,m3);ix=div(sub(c3,c5),den);iy=div(sub(mul(m5,c3),mul(c5,m3)),den)
        fm=div(sub(iy,p5[1]),sub(ix,p5[0]));fc=sub(p5[1],mul(fm,p5[0]));self.search[4]=Line(fm,fc,self.search[4].sign)
        self.f_intersection=(ix,iy);dist=f32(math.sqrt(float(add(mul(sub(ix,p5[0]),sub(ix,p5[0])),mul(sub(iy,p5[1]),sub(iy,p5[1]))))));self.f_distance=dist
        if bits(dist)!=int(a['f_distance_bits'],16): raise RuntimeError('clean F-bound distance drift')

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
    a=_awb_authority();return tuple((frombits(int(x[0],16)),frombits(int(x[1],16))) for x in a['selector_scales_bits'])

class DynamicCalibratedAWB:
    def __init__(self):
        self.core=EL.CalibratedAWB()
        self.selector=CalibrationSlotSelector()
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
