#!/usr/bin/env python3
"""Clean replay of the normal contained-triangle CTrigleAdjV1 AWB gain-adjust path.

Authority is the shipped IMX681 QTI tuning blob plus the SHA-pinned Surface DeviceMFT
static implementation.  No proprietary tuning payload is copied into this directory.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, struct
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
QP = REPO / 'tools' / 'qti_parameter_bin.py'
_spec = importlib.util.spec_from_file_location('qti_parameter_bin', QP)
_qti = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_qti)
DEFAULT_TUNING = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin')
TUNING_SHA256 = '2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'


def f32(x): return struct.unpack('<f', struct.pack('<f', float(x)))[0]
def add(a,b): return f32(f32(a)+f32(b))
def sub(a,b): return f32(f32(a)-f32(b))
def mul(a,b): return f32(f32(a)*f32(b))
def div(a,b): return f32(f32(a)/f32(b))
def bits(x): return struct.unpack('<I', struct.pack('<f', f32(x)))[0]

def gap_s0(x, prev_end, next_start):
    x,prev_end,next_start=map(f32,(x,prev_end,next_start))
    alpha=div(sub(x,prev_end),sub(next_start,prev_end))
    return sub(1.0,alpha)

def mix(prev,nxt,s0):
    s0=f32(s0); a=sub(1.0,s0)
    return add(mul(a,nxt),mul(s0,prev))

def mix3(a,b,s0): return tuple(mix(a[i],b[i],s0) for i in range(3))

@dataclass(frozen=True)
class Rec3:
    start: float; end: float; value: tuple[float,float,float]

@dataclass(frozen=True)
class Vertex:
    rg: float; bg: float; lux: tuple[Rec3,...]

@dataclass(frozen=True)
class Triangle:
    v: tuple[int,int,int]; neighbors: tuple[int,int,int]

class GainAdjustTuning:
    def __init__(self, tuning_path=DEFAULT_TUNING):
        self.path=Path(tuning_path)
        import hashlib
        sha=hashlib.sha256(self.path.read_bytes()).hexdigest()
        if sha != TUNING_SHA256:
            raise ValueError(f'tuning SHA mismatch: {sha}')
        parsed=_qti.parse(self.path); self.parsed=parsed
        self.byid={e['id']:e for e in parsed['entries']}
        top=next(e for e in parsed['entries'] if e['name']=='triglGAV1')
        u=struct.unpack('<19I', bytes.fromhex(top['raw_hex']))
        self.enable=u[2]
        self.triangle_count,self.triangle_ref=u[6],u[7]
        self.vertex_count,self.vertex_ref=u[8],u[9]
        self.outer_count,self.outer_ref=u[17],u[18]
        if (self.triangle_count,self.vertex_count,self.outer_count)!=(44,32,2):
            raise ValueError('unexpected triglGAV1 topology')
        self.triangles=self._triangles()
        self.vertices=self._vertices()
        self.outer=self._outer()

    def _raw(self,sid): return bytes.fromhex(self.byid[sid]['raw_hex'])
    def _table3(self,sid,count=None):
        raw=self._raw(sid)
        if len(raw)%20: raise ValueError(f'bad 3-vector table {sid:#x}')
        n=len(raw)//20 if count is None else count
        if len(raw) != n*20: raise ValueError(f'count mismatch table {sid:#x}')
        return tuple(Rec3(*struct.unpack_from('<ff',raw,i*20), tuple(struct.unpack_from('<fff',raw,i*20+8))) for i in range(n))

    def _vertices(self):
        raw=self._raw(self.vertex_ref)
        if len(raw)!=self.vertex_count*24: raise ValueError('vertex payload size')
        out=[]
        for i in range(self.vertex_count):
            rg,bg,m0,m1,n,ref=struct.unpack_from('<ff4I',raw,i*24)
            if m0 or m1: raise ValueError(f'unexpected vertex metadata V{i}')
            out.append(Vertex(f32(rg),f32(bg),self._table3(ref,n)))
        return tuple(out)

    def _triangles(self):
        raw=self._raw(self.triangle_ref)
        if len(raw)!=self.triangle_count*24: raise ValueError('triangle payload size')
        out=[]
        for i in range(self.triangle_count):
            a,b,c,n0,n1,n2=struct.unpack_from('<6i',raw,i*24)
            if not all(0<=x<self.vertex_count for x in (a,b,c)): raise ValueError(f'bad vertex in T{i}')
            if not all(x==255 or 0<=x<self.triangle_count for x in (n0,n1,n2)): raise ValueError(f'bad neighbor in T{i}')
            out.append(Triangle((a,b,c),(n0,n1,n2)))
        return tuple(out)

    def _outer(self):
        raw=self._raw(self.outer_ref)
        if len(raw)!=self.outer_count*16: raise ValueError('outer payload size')
        out=[]
        for i in range(self.outer_count):
            s,e,n,ref=struct.unpack_from('<ffII',raw,i*16)
            out.append((f32(s),f32(e),self._table3(ref,n)))
        return tuple(out)


def eval1d(table, x):
    x=f32(x)
    if x < table[0].start: return tuple(f32(v) for v in table[0].value)
    if x >= table[-1].end: return tuple(f32(v) for v in table[-1].value)
    prev=table[0]
    for cur in table:
        if x < cur.start:
            return mix3(prev.value,cur.value,gap_s0(x,prev.end,cur.start))
        if x < cur.end:
            return tuple(f32(v) for v in cur.value)
        prev=cur
    return tuple(f32(v) for v in table[-1].value)

def eval_outer(t:GainAdjustTuning, lux, cct):
    lux=f32(lux); vals=[eval1d(child,cct) for _,_,child in t.outer]
    if lux < t.outer[0][0]: return vals[0]
    if lux >= t.outer[-1][1]: return vals[-1]
    for i,(s,e,child) in enumerate(t.outer):
        if lux < s:
            ps,pe,_=t.outer[i-1]
            return mix3(vals[i-1],vals[i],gap_s0(lux,pe,s))
        if lux < e: return vals[i]
    return vals[-1]

def _signed_bary(p,a,b,c):
    # Selection only. Exact Windows magnitude weights are recomputed below in float32.
    den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if den==0: return None
    w0=((b[1]-c[1])*(p[0]-c[0])+(c[0]-b[0])*(p[1]-c[1]))/den
    w1=((c[1]-a[1])*(p[0]-c[0])+(a[0]-c[0])*(p[1]-c[1]))/den
    return w0,w1,1.0-w0-w1

def exact_weights(rg,bg,a,b,c):
    x,y=map(f32,(rg,bg)); x0,y0=map(f32,a); x1,y1=map(f32,b); x2,y2=map(f32,c)
    # Matches CTrigleAdjV1::GetTriangleRatio: absolute sub-triangle areas.
    A2=abs(add(add(mul(sub(y0,y1),x),mul(sub(y1,y),x0)),mul(sub(y,y0),x1)))
    A0=abs(add(add(mul(sub(y1,y2),x),mul(sub(y2,y),x1)),mul(sub(y,y1),x2)))
    A1=abs(add(add(mul(sub(y2,y0),x),mul(sub(y0,y),x2)),mul(sub(y,y2),x0)))
    S=add(add(A0,A1),A2)
    if S==0.0: raise ValueError('degenerate triangle')
    return div(A0,S),div(A1,S),div(A2,S)

def find_triangle(t:GainAdjustTuning, rg,bg):
    p=(float(rg),float(bg)); eps=2e-7
    for i,tr in enumerate(t.triangles):
        pts=[(t.vertices[v].rg,t.vertices[v].bg) for v in tr.v]
        w=_signed_bary(p,*pts)
        if w is not None and min(w)>=-eps and max(w)<=1.0+eps:
            return i,tr,exact_weights(rg,bg,*pts)
    raise ValueError('RG/BG point outside CTrigleAdjV1 mesh; fail closed (Windows two-vertex fallback not yet ported)')

def adjust(t:GainAdjustTuning, rg,bg,lux,cct):
    ti,tr,w=find_triangle(t,rg,bg)
    vv=[eval1d(t.vertices[v].lux,lux) for v in tr.v]
    tri=[]
    for ch in range(3):
        z=add(mul(w[0],vv[0][ch]),0.0)
        z=add(z,mul(w[1],vv[1][ch])); z=add(z,mul(w[2],vv[2][ch])); tri.append(z)
    cctmul=eval_outer(t,lux,cct)
    final=tuple(mul(cctmul[i],tri[i]) for i in range(3))
    return {'triangle':ti,'vertices':list(tr.v),'weights':list(w),'vertex_rgb':[list(x) for x in vv],
            'cct_rgb':list(cctmul),'triangle_rgb':tri,'final_rgb':list(final),
            'final_bits':[f'0x{bits(x):08x}' for x in final]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--tuning',type=Path,default=DEFAULT_TUNING)
    ap.add_argument('--rg',type=float,required=True); ap.add_argument('--bg',type=float,required=True)
    ap.add_argument('--lux',type=float,required=True); ap.add_argument('--cct',type=float,required=True)
    a=ap.parse_args(); t=GainAdjustTuning(a.tuning); print(json.dumps(adjust(t,a.rg,a.bg,a.lux,a.cct),indent=2,sort_keys=True))
if __name__=='__main__': main()
