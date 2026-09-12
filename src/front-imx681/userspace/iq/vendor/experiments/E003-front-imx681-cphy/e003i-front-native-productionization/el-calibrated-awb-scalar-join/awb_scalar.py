#!/usr/bin/env python3
"""Clean calibrated AWB decision -> published RGB gains -> Titan680 PDPC/WB scalars.

Scope is the proven SP11 front normal-preview contained-triangle GainAdj path.
Per-device calibration is read from HH clean runtime authority, derived from the proven physical OTP.
"""
from __future__ import annotations
import importlib.util,json,math,os,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
EF=BASE/'ef-clean-awb-gain-adjust-replay'/'gain_adjust.py'

def _load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
GA=_load(EF,'el_gain_adjust')

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def bits(x): return struct.unpack('<I',struct.pack('<f',f32(x)))[0]
def frombits(u): return struct.unpack('<f',struct.pack('<I',int(u)))[0]
def q_round_positive(v): return int(math.floor(float(v)+0.5))
def clamp(v,lo,hi): return max(lo,min(hi,v))

def calibration():
    a=json.loads(Path(os.environ['E003I_IQ_AUTHORITY']).read_text())['awb']
    p=a['active_reciprocal_bits'];return frombits(int(p[0],16)),frombits(int(p[1],16))

SEED_TRIANGLES=(5,19,38,41)

def _centroid(t,ti):
    tr=t.triangles[ti]; pts=[t.vertices[v] for v in tr.v]
    x=GA.div(GA.add(GA.add(pts[0].rg,pts[1].rg),pts[2].rg),3.0)
    y=GA.div(GA.add(GA.add(pts[0].bg,pts[1].bg),pts[2].bg),3.0)
    return x,y

def _cross(a,b,p):
    ax,ay=a; bx,by=b; px,py=p
    # FUN_1806abd80 exact float32 shape.
    return GA.sub(GA.mul(GA.sub(px,bx),GA.sub(ay,by)),
                  GA.mul(GA.sub(ax,bx),GA.sub(py,by)))

def _cross_sign(z):
    lo=frombits(0xb3d6bf95); hi=frombits(0x33d6bf95)  # -/+ 1.00000001169e-7
    if z < lo: return -1
    if z > hi: return 1
    return 0

def _inside_cross(t,ti,x,y):
    tr=t.triangles[ti]; pts=[(t.vertices[v].rg,t.vertices[v].bg) for v in tr.v]
    s=[_cross(pts[0],pts[1],(x,y)),_cross(pts[1],pts[2],(x,y)),_cross(pts[2],pts[0],(x,y))]
    q=[_cross_sign(z) for z in s]
    return not (q[0]*q[1]==-1 or q[2]*q[1]==-1 or q[2]*q[0]==-1)

def _crossed_edges(t,ti,x,y):
    tr=t.triangles[ti]; xy=[(t.vertices[v].rg,t.vertices[v].bg) for v in tr.v]
    cx,cy=_centroid(t,ti); out=[]
    for ei,(a,b) in enumerate(((0,1),(1,2),(2,0))):
        cp=_cross(xy[a],xy[b],(x,y)); cc=_cross(xy[a],xy[b],(cx,cy))
        if GA.mul(cp,cc) < 0.0: out.append(ei)
    return out

class CalibratedAWB:
    def __init__(self):
        self.tuning=GA.GainAdjustTuning();self.cal_rg,self.cal_bg=calibration();self.current_triangle=-1
        a=json.loads(Path(os.environ['E003I_IQ_AUTHORITY']).read_text())['awb']
        if tuple(a['seed_triangles'])!=SEED_TRIANGLES: raise RuntimeError('GainAdj seed topology drift')
    def reset(self): self.current_triangle=-1
    def _seed(self,x,y):
        candidates=[]
        if 0<=self.current_triangle<len(self.tuning.triangles): candidates.append(self.current_triangle)
        candidates.extend(SEED_TRIANGLES)
        best=candidates[0]; bx,by=_centroid(self.tuning,best); dx=GA.sub(x,bx);dy=GA.sub(y,by);bd=GA.add(GA.mul(dx,dx),GA.mul(dy,dy))
        for ti in candidates[1:]:
            cx,cy=_centroid(self.tuning,ti);dx=GA.sub(x,cx);dy=GA.sub(y,cy);d=GA.add(GA.mul(dx,dx),GA.mul(dy,dy))
            if d < bd: best,bd=ti,d
        return best
    def _select_triangle(self,rg,bg):
        x=float(GA.mul(rg,self.cal_rg)); y=float(GA.mul(bg,self.cal_bg))
        if 0<=self.current_triangle<len(self.tuning.triangles) and _inside_cross(self.tuning,self.current_triangle,x,y):
            return self.current_triangle
        ti=self._seed(x,y); seen=set()
        while ti not in seen and 0<=ti<len(self.tuning.triangles):
            seen.add(ti)
            if _inside_cross(self.tuning,ti,x,y):
                self.current_triangle=ti; return ti
            crossed=_crossed_edges(self.tuning,ti,x,y)
            if not crossed: break
            tr=self.tuning.triangles[ti]
            if len(crossed)==1:
                ti=tr.neighbors[crossed[0]]
                if ti==255: break
            else:
                # GetCurrentTriangle's multi-side branch (RVA 0x6bfcc0): when more
                # than one side is crossed it resolves neighbor sentinels in n0->n1->n2
                # order and continues with n2 when present, else the last surviving
                # prior neighbor.  It does not immediately collapse to the 2-vertex
                # out-of-zone fallback.  EO G6 exercises this exact path: 10 -> 8 -> 16.
                n0,n1,n2=tr.neighbors
                cur=ti
                a=cur if n0 in (255,-1) else n0
                b=a if n1 in (255,-1) else n1
                c=b if n2 in (255,-1) else n2
                boundary_count=sum(1 for n in (n0,n1,n2) if n==255)
                if boundary_count==2:
                    break  # Windows proceeds to its true two-vertex boundary fallback.
                ti=c
                if ti in (255,-1): break
        raise ValueError('RG/BG point outside stateful CTrigleAdjV1 mesh; fail closed')
    def publish(self,rg,bg,lux,cct):
        rg,bg,lux,cct=map(f32,(rg,bg,lux,cct))
        if not all(math.isfinite(x) and x>0.0 for x in (rg,bg,cct)) or not math.isfinite(lux):
            raise ValueError('invalid AWB decision/trigger')
        tri=self._select_triangle(rg,bg)
        z=GA.adjust(self.tuning,rg,bg,lux,cct,self.cal_rg,self.cal_bg,triangle_hint=tri)
        ar,ag,ab=z['final_rgb']
        # Single-camera Windows publication uses only GA_R/GA_B to transform the
        # decision ratios: adjustedRG=rawRG/GA_R, adjustedBG=rawBG/GA_B.  GA_G is
        # retained in shared state (and used by dual-camera mixing) but is not part
        # of this ratio-to-gain normalization.  The final triplet uses M=max(1,RG,BG).
        arg=GA.div(rg,ar);abg=GA.div(bg,ab);M=GA.f32(max(GA.f32(1.0),arg,abg))
        R=GA.div(M,arg);G=M;B=GA.div(M,abg)
        if not all(math.isfinite(x) and x>0.0 for x in (R,G,B)): raise RuntimeError('invalid published gains')
        return {'R':R,'G':G,'B':B,'gain_adjust':z}
    @staticmethod
    def scalar_regs(gains,predictive_gain):
        R,G,B=map(f32,(gains['R'],gains['G'],gains['B']));pg=f32(predictive_gain)
        if not math.isfinite(pg) or pg<=0.0: raise ValueError('invalid predictive gain')
        # Exact normal-positive Surface rounding domain: FRINTA/ties-away == floor(x+0.5).
        qpd=[clamp(q_round_positive(x*4096.0),0,0x3ffff) for x in (R/G,B/G,G/R,G/B)]
        qwb=[clamp(q_round_positive(x*pg*1024.0),0,0x7fff) for x in (G,B,R)]
        return {0x3d78:qpd[0],0x3d7c:qpd[1],0x3d80:qpd[2],0x3d84:qpd[3],
                0x4568:qwb[0]<<17,0x456c:qwb[1]<<17,0x4570:qwb[2]<<17}
    def run(self,rg,bg,lux,cct,predictive_gain=1.0):
        p=self.publish(rg,bg,lux,cct);p['registers']=self.scalar_regs(p,predictive_gain);return p
