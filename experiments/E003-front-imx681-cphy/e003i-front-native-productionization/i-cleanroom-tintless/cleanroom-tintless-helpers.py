#!/usr/bin/env python3
from __future__ import annotations
import ctypes,struct
GRID_W=32; GRID_H=24; REGIONS=GRID_W*GRID_H
G_STATS_SCALE_A=0x18160AD58; G_STATS_SCALE_B=0x18160A468; G_STATS_MODE=0x1817959A4

def f32(v): return struct.unpack('<f',struct.pack('<f',float(v)))[0]
def ru8(u,a): return u.mem_read(a,1)[0]
def ru16(u,a): return struct.unpack('<H',bytes(u.mem_read(a,2)))[0]
def ru32(u,a): return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
def ru64(u,a): return struct.unpack('<Q',bytes(u.mem_read(a,8)))[0]
def ri32(u,a): return struct.unpack('<i',bytes(u.mem_read(a,4)))[0]
def rf32(u,a): return struct.unpack('<f',bytes(u.mem_read(a,4)))[0]
def wu8(u,a,v): u.mem_write(a,bytes((v&0xff,)))
def wu32(u,a,v): u.mem_write(a,struct.pack('<I',v&0xffffffff))
def wi32(u,a,v): u.mem_write(a,struct.pack('<i',int(v)))
def wf32(u,a,v): u.mem_write(a,struct.pack('<f',f32(v)))

def preprocess_stats(u,state,stats_obj):
    raw=ru64(u,stats_obj)
    wu32(u,G_STATS_SCALE_A,ru32(u,stats_obj+0x10)); wu32(u,G_STATS_SCALE_B,ru32(u,stats_obj+0x14)); wu8(u,G_STATS_MODE,ru8(u,stats_obj+0x0c))
    area=(ru16(u,state+0x0a)>>1)*(ru16(u,state+0x08)>>1); off=ru32(u,state+0x70)
    sr,sgb,sb,sgr=(ru16(u,state+x) for x in (0x18,0x1a,0x1c,0x1e)); stride=0x64 if (ru32(u,raw)&2) else 0x32
    for i in range(REGIONS):
        rec=raw+i*stride
        vals=[]
        for ro,so in ((0x20,sr),(0x28,sgb),(0x30,sb),(0x38,sgr)):
            v=ru64(u,rec+ro)+((area-ru16(u,rec+0x48+(ro-0x20)//4))&0xffffffff)*so+off
            vals.append(1 if v<2 else v)
        r,gb,b,gr=vals; inv=f32(f32(1.0)/f32(gr+b))
        wf32(u,state+0x2e64+i*4,f32(f32(f32(r)+f32(r))*inv)); wf32(u,state+0x3a64+i*4,f32(f32(f32(gb)+f32(gb))*inv))

def smooth_stats_map(u,state,src,dst):
    v=[ri32(u,src+i*4) for i in range(REGIONS)]
    for y in range(GRID_H):
        for x in range(GRID_W):
            s=0
            for yy in (max(0,y-1),y,min(GRID_H-1,y+1)):
                row=yy*GRID_W
                for xx in (max(0,x-1),x,min(GRID_W-1,x+1)): s+=v[row+xx]
            wi32(u,dst+(y*GRID_W+x)*4,int(s/9))

def accumulate_float_fields(u,a,b,da,db):
    for i in range(REGIONS):
        o=i*4; wf32(u,a+o,f32(rf32(u,a+o)+rf32(u,da+o))); wf32(u,b+o,f32(rf32(u,b+o)+rf32(u,db+o)))

_libm=ctypes.CDLL('libm.so.6')
_libm.logf.argtypes=[ctypes.c_float]
_libm.logf.restype=ctypes.c_float

def ln_float_field(u,src,dst):
    for i in range(REGIONS):
        x=rf32(u,src+i*4)
        wf32(u,dst+i*4,_libm.logf(ctypes.c_float(x)))

def quantize_float_field_q16(u,src,dst):
    for i in range(REGIONS):
        x=rf32(u,src+i*4)
        y=f32(f32(f32(x*131072.0)+1.0)*0.5)
        wi32(u,dst+i*4,int(y))

def pad_mesh_extrapolated(u,state,src,dst):
    """Clean-room translation of active Tintless pad helper RVA 0xc9c4b0."""
    h=ru8(u,state+0x20); w=ru8(u,state+0x21); stride=w+3
    if h<2 or w<2: raise ValueError('unsupported degenerate Tintless mesh')
    S=[[rf32(u,src+(y*w+x)*4) for x in range(w)] for y in range(h)]
    P=[[f32(0.0) for _ in range(stride)] for __ in range(h+3)]
    def ext(a,b): return f32(f32(f32(a)+f32(a))-f32(b))
    for y in range(h):
        for x in range(w): P[y+1][x+1]=S[y][x]
    for x in range(w): P[0][x+1]=ext(S[0][x],S[1][x])
    for y in range(h):
        P[y+1][0]=ext(S[y][0],S[y][1])
        P[y+1][w+1]=ext(S[y][w-1],S[y][w-2])
    for x in range(w): P[h+1][x+1]=ext(S[h-1][x],S[h-2][x])
    P[0][0]=ext(P[1][1],P[2][2])
    P[0][w+1]=ext(P[1][w],P[2][w-1])
    P[h+1][0]=ext(P[h][1],P[h-1][2])
    P[h+1][w+1]=ext(P[h][w],P[h-1][w-1])
    for y in range(h+2): P[y][w+2]=ext(P[y][w+1],P[y][w])
    for x in range(w+2): P[h+2][x]=ext(P[h+1][x],P[h][x])
    P[h+2][0]=ext(P[h+1][1],P[h][2])
    P[h+2][w+2]=ext(P[h+1][w+1],P[h][w])
    for y,row in enumerate(P):
        for x,v in enumerate(row): wf32(u,dst+(y*stride+x)*4,v)

def bicubic_row_kernel(u,w0,w1,w2,w3,p0,p1,p2,p3,out,segments,substeps):
    """Clean-room translation of RVA 0xc9e398.

    Each segment evaluates four adjacent samples from four source rows with
    Catmull-Rom horizontal weights, then combines the four row results with
    the caller-supplied vertical weights (w0..w3).
    """
    nseg=int(segments)-1
    if nseg<=0:return
    for j in range(nseg):
        rows=[]
        for p in (p0,p1,p2,p3): rows.append([rf32(u,p+(j+k)*4) for k in range(4)])
        for k in range(int(substeps)):
            t=float(k)/float(substeps);t2=t*t;t3=t2*t
            hx0=((2.0*t2-t3)-t)*0.5
            hx1=((3.0*t3-5.0*t2)+2.0)*0.5
            hx2=((4.0*t2-3.0*t3)+t)*0.5
            hx3=(t3-t2)*0.5
            r=[float(a[0])*hx0+float(a[1])*hx1+float(a[2])*hx2+float(a[3])*hx3 for a in rows]
            y=r[0]*w0+r[1]*w1+r[2]*w2+r[3]*w3
            wf32(u,out+(j*int(substeps)+k)*4,y)

def interpolate_mesh_to_stats(u,state,src,dst):
    """Clean-room translation of active Tintless interpolation RVA 0xc9e590."""
    factor=ru8(u,state+0x2a); src_h=ru8(u,state+0x20); src_w=ru8(u,state+0x21)
    if factor==0 or src_h<2 or src_w<2: raise ValueError('invalid Tintless interpolation geometry')
    padded=state+0x121e8; temp=state+0x5e64
    pad_mesh_extrapolated(u,state,src,padded)
    tw=(src_w-1)*factor+1; th=(src_h-1)*factor+1; pstride=src_w+3
    for yy in range(th-1):
        iy=yy//factor; fy=float(yy)/float(factor)-float(iy); fy2=fy*fy; fy3=fy2*fy
        wy0=((2.0*fy2-fy3)-fy)*0.5; wy1=((3.0*fy3-5.0*fy2)+2.0)*0.5
        wy2=((4.0*fy2-3.0*fy3)+fy)*0.5; wy3=(fy3-fy2)*0.5
        rows=[padded+((iy+k)*pstride)*4 for k in range(4)]
        bicubic_row_kernel(u,wy0,wy1,wy2,wy3,*rows,temp+yy*tw*4,src_w,factor)
        wf32(u,temp+(yy*tw+tw-1)*4,0.0)
    for x in range(tw): wf32(u,temp+((th-1)*tw+x)*4,0.0)
    out_w=ru8(u,state+0x0c); out_h=ru8(u,state+0x0d)
    cell_y=ru16(u,state+0x0a); cell_x=ru16(u,state+0x08)
    off_y=ru16(u,state+0x0e); off_x=ru16(u,state+0x10)
    add_y=ru16(u,state+0x24); add_x=ru16(u,state+0x22)
    den_y=ru16(u,state+0x26); den_x=ru16(u,state+0x28)
    for y in range(out_h):
        py=f32(f32(f32(f32(cell_y*y)+f32(cell_y*0.5))+f32(off_y))+f32(add_y)); yyf=f32(py/f32(den_y)); iy=int(yyf); fy=f32(yyf-f32(iy))
        for x in range(out_w):
            px=f32(f32(f32(f32(cell_x*x)+f32(cell_x*0.5))+f32(off_x))+f32(add_x)); xxf=f32(px/f32(den_x)); ix=int(xxf); fx=f32(xxf-f32(ix))
            lo=iy*tw+ix; hi=(iy+1)*tw+ix; omx=f32(1.0-fx); omy=f32(1.0-fy)
            top=f32(f32(rf32(u,temp+(hi+1)*4)*fx)+f32(rf32(u,temp+hi*4)*omx))
            bot=f32(f32(rf32(u,temp+(lo+1)*4)*fx)+f32(rf32(u,temp+lo*4)*omx))
            wf32(u,dst+(y*out_w+x)*4,f32(f32(top*fy)+f32(bot*omy)))
