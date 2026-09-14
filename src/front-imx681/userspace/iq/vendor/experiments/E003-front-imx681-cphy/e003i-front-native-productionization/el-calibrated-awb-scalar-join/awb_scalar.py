#!/usr/bin/env python3
"""Clean calibrated AWB decision -> published RGB gains -> Titan680 PDPC/WB scalars.

Scope is the SP11 front normal-preview Windows CTrigleAdjV1 path, including stateful triangle walk, anti-cycle centroid fallback, and reachable two-vertex boundary fallback.
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
    def _selection_adjust_triangle(self,ti,lux,cct,point=None):
        tr=self.tuning.triangles[ti]
        pts=[(self.tuning.vertices[v].rg,self.tuning.vertices[v].bg) for v in tr.v]
        if point is None:
            raise ValueError('explicit interpolation point required')
        w=GA.exact_weights(point[0],point[1],*pts)
        vv=[GA.eval1d(self.tuning.vertices[v].lux,lux) for v in tr.v]
        tri=[]
        for ch in range(3):
            z=GA.add(GA.mul(w[0],vv[0][ch]),0.0)
            z=GA.add(z,GA.mul(w[1],vv[1][ch]));z=GA.add(z,GA.mul(w[2],vv[2][ch]));tri.append(z)
        cctmul=GA.eval_outer(self.tuning,lux,cct)
        final=tuple(GA.mul(cctmul[i],tri[i]) for i in range(3))
        return {'triangle':ti,'vertices':list(tr.v),'weights':list(w),'vertex_rgb':[list(x) for x in vv],
                'mesh_point':[point[0],point[1]],'mesh_point_bits':[f'0x{GA.bits(point[0]):08x}',f'0x{GA.bits(point[1]):08x}'],
                'cct_rgb':list(cctmul),'triangle_rgb':tri,'final_rgb':list(final),
                'final_bits':[f'0x{GA.bits(x):08x}' for x in final]}
    def _pair_weight(self,a,b,p):
        ax,ay=map(GA.f32,a);bx,by=map(GA.f32,b);px,py=map(GA.f32,p)
        dx=GA.sub(ax,bx);dy=GA.sub(ay,by);L2=GA.add(GA.mul(dx,dx),GA.mul(dy,dy))
        w=GA.f32(1.0)
        if L2!=0.0:
            bdx=GA.sub(bx,px);bdy=GA.sub(by,py);bd=GA.add(GA.mul(bdx,bdx),GA.mul(bdy,bdy))
            adx=GA.sub(ax,px);ady=GA.sub(ay,py);ad=GA.add(GA.mul(adx,adx),GA.mul(ady,ady))
            w=GA.div(GA.mul(GA.add(GA.sub(bd,ad),L2),0.5),L2)
        # Exact GetCurrentTriangle behavior: negative projection resets to endpoint A.
        # There is no corresponding >1 clamp in the pinned implementation.
        if w < 0.0:w=GA.f32(1.0)
        return w
    def _selection_adjust_pair(self,sel,lux,cct):
        va,vb=sel['vertices'];w=sel['weight'];wb=GA.sub(1.0,w)
        aa=GA.eval1d(self.tuning.vertices[va].lux,lux);bb=GA.eval1d(self.tuning.vertices[vb].lux,lux)
        tri=[]
        for ch in range(3):tri.append(GA.add(GA.mul(aa[ch],w),GA.mul(wb,bb[ch])))
        cctmul=GA.eval_outer(self.tuning,lux,cct);final=tuple(GA.mul(cctmul[i],tri[i]) for i in range(3))
        return {'triangle':sel['triangle'],'selector_return':255,'vertices':[va,vb,-1],
                'weights':[w,wb,GA.f32(0.0)],'vertex_rgb':[list(aa),list(bb)],
                'mesh_point':list(sel['mesh_point']),'mesh_point_bits':[f'0x{GA.bits(x):08x}' for x in sel['mesh_point']],
                'cct_rgb':list(cctmul),'triangle_rgb':tri,'final_rgb':list(final),
                'final_bits':[f'0x{GA.bits(x):08x}' for x in final]}
    def _boundary_selection(self,ti,edge,x,y,move=None):
        tr=self.tuning.triangles[ti]
        if edge in (-1,0): pair=(tr.v[0],tr.v[1])
        elif edge==1: pair=(tr.v[1],tr.v[2])
        elif edge==2: pair=(tr.v[0],tr.v[2])
        elif edge==3:
            # Literal port of GetCurrentTriangle's rare two-boundary/all-three-side
            # resolver. local_b8 contains only crossed-edge neighbor IDs; 255 marks a
            # boundary edge. The final boundary edge visited supplies the pair, with
            # Windows' endpoint-distance guards allowed to collapse it to one vertex.
            if move is None:raise ValueError('missing Windows boundary-move state')
            pair=None
            edges=((tr.v[0],tr.v[1]),(tr.v[1],tr.v[2]),(tr.v[2],tr.v[0]))
            px,py=map(GA.f32,(x,y))
            for i,n in enumerate(move):
                if n!=255:continue
                va,vb=edges[i];a=(self.tuning.vertices[va].rg,self.tuning.vertices[va].bg);b=(self.tuning.vertices[vb].rg,self.tuning.vertices[vb].bg)
                ax,ay=map(GA.f32,a);bx,by=map(GA.f32,b)
                dx=GA.sub(ax,bx);dy=GA.sub(ay,by);L2=GA.add(GA.mul(dx,dx),GA.mul(dy,dy))
                dax=GA.sub(ax,px);day=GA.sub(ay,py);dA2=GA.add(GA.mul(dax,dax),GA.mul(day,day))
                dbx=GA.sub(bx,px);dby=GA.sub(by,py);dB2=GA.add(GA.mul(dbx,dbx),GA.mul(dby,dby))
                first=vb;second=vb
                if dA2<=L2:
                    first=va
                    second=vb if dB2<=L2 else va
                pair=(first,second)
            if pair is None:pair=(tr.v[0],tr.v[1])
        else:raise ValueError('invalid Windows boundary edge')
        a=(self.tuning.vertices[pair[0]].rg,self.tuning.vertices[pair[0]].bg)
        b=(self.tuning.vertices[pair[1]].rg,self.tuning.vertices[pair[1]].bg)
        w=self._pair_weight(a,b,(x,y));self.current_triangle=ti
        return {'mode':'two_vertex','triangle':ti,'vertices':pair,'weight':w,'edge':edge,'mesh_point':(x,y)}
    def _select_triangle(self,rg,bg):
        x=GA.mul(rg,self.cal_rg);y=GA.mul(bg,self.cal_bg)
        if 0<=self.current_triangle<len(self.tuning.triangles) and _inside_cross(self.tuning,self.current_triangle,x,y):
            return {'mode':'triangle','triangle':self.current_triangle,'mesh_point':(x,y),'visits':{}}
        ti=self._seed(x,y);visits=[0]*len(self.tuning.triangles);last_edge=-1
        while 0<=ti<len(self.tuning.triangles):
            tr=self.tuning.triangles[ti]
            if _inside_cross(self.tuning,ti,x,y):
                visits[ti]+=1;self.current_triangle=ti
                return {'mode':'triangle','triangle':ti,'mesh_point':(x,y),'visits':{i:n for i,n in enumerate(visits) if n}}
            crossed=_crossed_edges(self.tuning,ti,x,y)
            mask=sum(1<<e for e in crossed)
            if crossed:last_edge=crossed[-1]
            if mask>4 or mask==3:
                n0,n1,n2=tr.neighbors
                def sent(n): return n in (255,-1)
                target=ti if sent(n0) else n0
                boundary_count=1 if n0==255 else 0
                target=target if sent(n1) else n1
                if n1==255:boundary_count+=1
                target=target if sent(n2) else n2
                if n2==255:boundary_count+=1
                if boundary_count==2:
                    move=[-1,-1,-1]
                    for e in crossed:move[e]=tr.neighbors[e]
                    return self._boundary_selection(ti,3,x,y,move)
            elif mask==0:
                return self._boundary_selection(ti,last_edge,x,y)
            else:
                edge={1:0,2:1,4:2}[mask];last_edge=edge;target=tr.neighbors[edge]
                if target==255:return self._boundary_selection(ti,edge,x,y)
            if target in (255,-1):return self._boundary_selection(ti,last_edge,x,y)
            visits[target]+=1
            if visits[target]>2:
                # Pinned Windows GetCurrentTriangle marks +0x23c and returns this
                # triangle. GetTriangleRatio then substitutes its centroid for P.
                self.current_triangle=target;cx,cy=_centroid(self.tuning,target)
                return {'mode':'centroid','triangle':target,'mesh_point':(x,y),'interpolation_point':(cx,cy),
                        'visits':{i:n for i,n in enumerate(visits) if n}}
            ti=target
        raise ValueError('invalid CTrigleAdjV1 triangle walk')
    def publish(self,rg,bg,lux,cct):
        rg,bg,lux,cct=map(f32,(rg,bg,lux,cct))
        if not all(math.isfinite(x) and x>0.0 for x in (rg,bg,cct)) or not math.isfinite(lux):
            raise ValueError('invalid AWB decision/trigger')
        sel=self._select_triangle(rg,bg)
        if sel['mode']=='triangle':
            z=GA.adjust(self.tuning,rg,bg,lux,cct,self.cal_rg,self.cal_bg,triangle_hint=sel['triangle'])
        elif sel['mode']=='centroid':
            z=self._selection_adjust_triangle(sel['triangle'],lux,cct,sel['interpolation_point'])
            z['actual_mesh_point']=list(sel['mesh_point']);z['actual_mesh_point_bits']=[f'0x{GA.bits(x):08x}' for x in sel['mesh_point']]
        else:
            z=self._selection_adjust_pair(sel,lux,cct)
        z['selection_mode']=sel['mode'];z['selector_visits']=sel.get('visits',{})
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
