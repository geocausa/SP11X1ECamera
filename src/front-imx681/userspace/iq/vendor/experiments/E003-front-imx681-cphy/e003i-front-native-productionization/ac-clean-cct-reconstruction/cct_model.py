#!/usr/bin/env python3
"""Cleanroom E003I front AWB/CCT model reconstructed from the Windows oracle.

Inputs:
  AC2-R1.raw .. AC2-R4.raw
  request-local AWB lux index for each raw request

Pipeline:
  raw 0x50 stats -> active subrecord candidate -> P01 StatScr ->
  P03 CCT/distance -> P04 DistWV + P05 IlluWV -> P09 ->
  AGW weighted XY -> startup temporal 60/40 -> P03 final CCT.

The model accepts request-local lux explicitly. Historical AC2 fitted lux values
are kept only in regress-ac2.py and are not model defaults.
"""
from pathlib import Path
import argparse, base64, contextlib, io, json, os, runpy, struct
import numpy as np

ROOT = Path(__file__).resolve().parent
_AUTH=json.loads(Path(os.environ['E003I_IQ_AUTHORITY']).read_text())['cct_tables']
def _ab(name): return base64.b64decode(_AUTH[name]['b64'])
MASK=(1<<34)-1
SHIFT=10
EXPECTED=[5652,5915,6019,5733]
DEFAULT_FITTED=[238.6585693359375,263.858642578125,262.83251953125,374.9688720703125]

# Load bit-exact P03 quietly (its standalone script has self-tests at module scope).
_buf=io.StringIO()
with contextlib.redirect_stdout(_buf):
    _p03ns=runpy.run_path(str(ROOT/'fixtures/E003I-AC31-CCT-replay.py'))
P03=_p03ns['replay']

def f32(x): return np.float32(x)
def bits(x): return struct.unpack('<I',struct.pack('<f',np.float32(x)))[0]
def gap_s0(x,prev_end,next_start):
    x,prev_end,next_start=map(np.float32,(x,prev_end,next_start))
    alpha=np.float32(np.float32(x-prev_end)/np.float32(next_start-prev_end))
    return np.float32(np.float32(1.0)-alpha)
def vendor_mix(prev,nxt,s0):
    prev,nxt,s0=map(np.float32,(prev,nxt,s0))
    alpha2=np.float32(np.float32(1.0)-s0)
    return np.float32(np.float32(alpha2*nxt)+np.float32(s0*prev))
def leaf(curve,x):
    x=np.float32(x)
    if x < curve[0][0]: return curve[0][2]
    if x >= curve[-1][1]: return curve[-1][2]
    prev=curve[0]
    for rec in curve:
        s,e,v=rec
        if x < s: return vendor_mix(prev[2],v,gap_s0(x,prev[1],s))
        if x < e: return v
        prev=rec
    return curve[-1][2]

# P04 CSFDistWVV1 tree.
P04_ROOTS=[(f32(a),f32(b)) for a,b in [(0,91),(160,180),(305,859)]]
P04=[]
for ci in range(3):
    b=_ab(f'E003I-AC36-P04-C{ci}.bin')
    cct=[tuple(f32(z) for z in struct.unpack_from('<ff',b,j*0x18)) for j in range(6)]
    rows=[]
    for ri in range(6):
        d=_ab(f'E003I-AC36-P04-C{ci}-R{ri}.bin')
        rows.append([tuple(f32(z) for z in struct.unpack_from('<fff',d,j*12)) for j in range(5)])
    P04.append((cct,rows))
def p04_boundary(curve,metric):
    return curve[1][1] if f32(metric)<f32(0) else curve[4][0]
def p04_child(ci,cct,metric):
    nodes,rows=P04[ci]; cct=f32(cct); metric=f32(metric)
    if cct<nodes[0][0]: return leaf(rows[0],metric)
    if cct>=nodes[-1][1]: return leaf(rows[-1],metric)
    prev=nodes[0]
    for i,(s,e) in enumerate(nodes):
        if cct<s:
            w=gap_s0(cct,prev[1],s)
            bp=p04_boundary(rows[i-1],metric); bn=p04_boundary(rows[i],metric)
            bi=vendor_mix(bp,bn,w)
            scale=f32(metric/bi)
            vp=leaf(rows[i-1],f32(scale*bp)); vn=leaf(rows[i],f32(scale*bn))
            return vendor_mix(vp,vn,w)
        if cct<e: return leaf(rows[i],metric)
        prev=(s,e)
    return leaf(rows[-1],metric)
def p04(lux,cct,metric):
    L=f32(lux)
    if L<P04_ROOTS[0][0]: return p04_child(0,cct,metric)
    if L>=P04_ROOTS[-1][1]: return p04_child(2,cct,metric)
    prev=P04_ROOTS[0]
    for i,(s,e) in enumerate(P04_ROOTS):
        if L<s:
            return vendor_mix(p04_child(i-1,cct,metric),p04_child(i,cct,metric),gap_s0(L,prev[1],s))
        if L<e: return p04_child(i,cct,metric)
        prev=(s,e)
    return p04_child(2,cct,metric)

# P05 CSFIlluWVV1 tree.
P05_ROOTS=[(f32(a),f32(b)) for a,b in [(0,69),(82,91),(96,110),(120,140),(170,190),(197,207),(225,260),(270,290),(300,350),(360,450)]]
P05=[]
for ci in range(10):
    b=_ab(f'E003I-AC36-P05-C{ci}.bin')
    P05.append([tuple(f32(z) for z in struct.unpack_from('<fff',b,j*12)) for j in range(10)])
def p05(lux,cct):
    L=f32(lux)
    if L<P05_ROOTS[0][0]: return leaf(P05[0],cct)
    if L>=P05_ROOTS[-1][1]: return leaf(P05[-1],cct)
    prev=P05_ROOTS[0]
    for i,(s,e) in enumerate(P05_ROOTS):
        if L<s: return vendor_mix(leaf(P05[i-1],cct),leaf(P05[i],cct),gap_s0(L,prev[1],s))
        if L<e: return leaf(P05[i],cct)
        prev=(s,e)
    return leaf(P05[-1],cct)

def candidate(raw):
    q=lambda o:struct.unpack_from('<Q',raw,o)[0]&MASK
    h=lambda o:struct.unpack_from('<H',raw,o)[0]
    s0,s1,sg=q(0),q(0x18),q(0x08)+q(0x10)
    c0,c1,cg=h(0x06),h(0x1e),h(0x0e)+h(0x16)
    if not c0 or not c1 or not cg: return None
    m0=f32(f32(s0)/f32(c0<<SHIFT)); mg=f32(f32(sg)/f32(cg<<SHIFT)); m1=f32(f32(s1)/f32(c1<<SHIFT))
    x=f32(m0/mg) if mg!=0 else f32(0); y=f32(m1/mg) if mg!=0 else f32(0)
    bad=f32(f32(f32(2640-(c0+c1+cg))*f32(100.0))/f32(2640.0))
    return m0,mg,m1,x,y,bad

def agw(raw_path,lux):
    d=raw_path.read_bytes(); p01=0; valid=0
    sw=sx=sy=f32(0)
    for off in range(0,len(d),0x50):
        z=candidate(d[off:off+0x50])
        if z is None: continue
        m0,mg,m1,x,y,bad=z
        if not (m0>f32(1) and mg>f32(1) and m1>f32(1) and bad<f32(80)): continue
        p01+=1
        r=P03(float(x),float(y)); c=f32(r['cct']); metric=f32(r['metric'])
        w40=f32(p04(lux,c,metric)); w44=f32(p05(lux,c))
        if w40==f32(0) or w44==f32(0): continue
        valid+=1; w=f32(w40*w44)
        sw=f32(sw+w); sx=f32(sx+f32(x*w)); sy=f32(sy+f32(y*w))
    if sw==0: raise RuntimeError(f'No valid AGW candidates for {raw_path.name}')
    x=f32(sx/sw); y=f32(sy/sw); c=f32(P03(float(x),float(y))['cct'])
    return {'p01':p01,'valid':valid,'sumW':sw,'x':x,'y':y,'cct':c}

def temporal(fresh_x,fresh_y,prev_x,prev_y):
    # Startup path proven by AC39: s13=0.4 previous weight; fresh weight = 1-s13 = 0.6.
    pw=f32(0.4); fw=f32(f32(1.0)-pw)
    x=f32(f32(fw*f32(fresh_x))+f32(pw*f32(prev_x)))
    y=f32(f32(fw*f32(fresh_y))+f32(pw*f32(prev_y)))
    c=f32(P03(float(x),float(y))['cct'])
    return x,y,c
