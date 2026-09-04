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

def fft_radix2_inplace(u,n,real_ptr,imag_ptr,twiddle_ptr,perm_ptr):
    """Clean-room translation of active solver FFT leaf RVA 0xca1d98."""
    n=int(n)
    if n>1:
        for i in range(1,n):
            j=ru8(u,perm_ptr+i)
            rb=bytes(u.mem_read(real_ptr+i*4,4)); rj=bytes(u.mem_read(real_ptr+j*4,4))
            ib=bytes(u.mem_read(imag_ptr+i*4,4)); ij=bytes(u.mem_read(imag_ptr+j*4,4))
            u.mem_write(real_ptr+i*4,rj);u.mem_write(real_ptr+j*4,rb)
            u.mem_write(imag_ptr+i*4,ij);u.mem_write(imag_ptr+j*4,ib)
    levels=1
    if n>2:
        while (1<<levels)<n: levels+=1
    stride=1; half=n//2; butterflies=n
    for _ in range(levels):
        twstep=half//stride if stride else 0
        butterflies >>= 1
        for group in range(stride):
            ti=group*twstep*2
            wr=rf32(u,twiddle_ptr+ti*4); wi=rf32(u,twiddle_ptr+(ti+1)*4)
            idx=group
            for __ in range(butterflies):
                j=idx+stride
                br=rf32(u,real_ptr+j*4); bi=rf32(u,imag_ptr+j*4)
                tr=f32(f32(br*wr)-f32(bi*wi))
                tii=f32(f32(bi*wr)+f32(br*wi))
                ar=rf32(u,real_ptr+idx*4); ai=rf32(u,imag_ptr+idx*4)
                wf32(u,real_ptr+j*4,f32(ar-tr)); wf32(u,imag_ptr+j*4,f32(ai-tii))
                wf32(u,real_ptr+idx*4,f32(ar+tr)); wf32(u,imag_ptr+idx*4,f32(ai+tii))
                idx += stride*2
        stride <<= 1

def transpose_u32_matrix(u,rows,cols,src,dst):
    rows=int(rows);cols=int(cols)
    for r in range(rows):
        for c in range(cols):
            u.mem_write(dst+(c*rows+r)*4,bytes(u.mem_read(src+(r*cols+c)*4,4)))

def _negate_float_bits(u,ptr,count):
    for i in range(int(count)):
        b=ru32(u,ptr+i*4)^0x80000000
        wu32(u,ptr+i*4,b)

def fft2d_forward_64x32(u,real_ptr,imag_ptr,temp_ptr,tw32,tw64,perm64,perm32):
    """Clean-room translation of RVA 0xca1fb0."""
    total=0x800
    for off in range(0,total,0x20):
        fft_radix2_inplace(u,0x20,real_ptr+off*4,imag_ptr+off*4,tw32,perm32)
    transpose_u32_matrix(u,0x40,0x20,real_ptr,temp_ptr)
    transpose_u32_matrix(u,0x40,0x20,imag_ptr,real_ptr)
    for off in range(0,total,0x40):
        fft_radix2_inplace(u,0x40,temp_ptr+off*4,real_ptr+off*4,tw64,perm64)
    transpose_u32_matrix(u,0x20,0x40,real_ptr,imag_ptr)
    transpose_u32_matrix(u,0x20,0x40,temp_ptr,real_ptr)

def fft2d_inverse_64x32(u,real_ptr,imag_ptr,temp_ptr,tw32,tw64,perm64,perm32):
    """Clean-room translation of RVA 0xca2310 (conjugate/FFT/conjugate/2048)."""
    total=0x800
    _negate_float_bits(u,imag_ptr,total)
    for off in range(0,total,0x20):
        fft_radix2_inplace(u,0x20,real_ptr+off*4,imag_ptr+off*4,tw32,perm32)
    transpose_u32_matrix(u,0x40,0x20,real_ptr,temp_ptr)
    transpose_u32_matrix(u,0x40,0x20,imag_ptr,real_ptr)
    for off in range(0,total,0x40):
        fft_radix2_inplace(u,0x40,temp_ptr+off*4,real_ptr+off*4,tw64,perm64)
    transpose_u32_matrix(u,0x20,0x40,real_ptr,imag_ptr)
    transpose_u32_matrix(u,0x20,0x40,temp_ptr,real_ptr)
    _negate_float_bits(u,imag_ptr,total)
    scale=f32(1.0/2048.0)
    for i in range(total):
        wf32(u,real_ptr+i*4,f32(rf32(u,real_ptr+i*4)*scale))
        wf32(u,imag_ptr+i*4,f32(rf32(u,imag_ptr+i*4)*scale))
_libm.expf.argtypes=[ctypes.c_float]
_libm.expf.restype=ctypes.c_float

def exp_q16_postprocess(u,ptr):
    """Clean-room translation of RVA 0xc9ed88."""
    inv=f32(1.0/65536.0); scale=f32(131072.0)
    for i in range(REGIONS):
        x=ri32(u,ptr+i*4)
        arg=f32(-f32(float(x))*inv)
        ev=f32(_libm.expf(ctypes.c_float(arg)))
        y=f32(f32(ev*scale)+f32(1.0)); y=f32(y*f32(0.5))
        wi32(u,ptr+i*4,int(y))

def map_correction_to_mesh(u,state,src,dst):
    """Clean-room structural translation of RVA 0xc9c868.

    Source is 24x32 int32. Surface embeds it at [2:26,2:34] of a 29x37
    field and repeatedly linearly extrapolates two cells top/left and three
    cells bottom/right, then bilinearly samples the padded field to the
    configured Tintless mesh.
    """
    sh,sw=24,32; ph,pw=29,37
    g=[[0]*pw for _ in range(ph)]
    for y in range(sh):
        for x in range(sw): g[y+2][x+2]=ri32(u,src+(y*sw+x)*4)
    # horizontal extrapolation on source-bearing rows
    for y in range(2,26):
        g[y][1]=2*g[y][2]-g[y][3]; g[y][0]=2*g[y][1]-g[y][2]
        g[y][34]=2*g[y][33]-g[y][32]; g[y][35]=2*g[y][34]-g[y][33]; g[y][36]=2*g[y][35]-g[y][34]
    # First build ordinary separable extrapolation. Surface then overrides
    # 25 extended-corner cells with diagonal rules; those assignments are
    # represented structurally below.
    for x in range(pw):
        g[1][x]=2*g[2][x]-g[3][x]; g[0][x]=2*g[1][x]-g[2][x]
        g[26][x]=2*g[25][x]-g[24][x]; g[27][x]=2*g[26][x]-g[25][x]; g[28][x]=2*g[27][x]-g[26][x]
    # top-left / top-right first diagonal corners
    g[1][1]=2*g[2][2]-g[3][3]
    g[1][34]=2*g[2][33]-g[3][32]
    g[0][1]=2*g[1][1]-g[2][1]
    g[0][34]=2*g[1][34]-g[2][34]
    g[1][0]=2*g[1][1]-g[1][2]
    g[1][35]=2*g[1][34]-g[1][33]
    g[0][0]=2*g[1][1]-g[2][2]
    g[0][35]=2*g[1][34]-g[2][33]
    g[0][36]=2*g[0][35]-g[0][34]
    g[1][36]=2*g[1][35]-g[1][34]
    # bottom-left / bottom-right first diagonal corners
    g[26][1]=2*g[25][2]-g[24][3]
    g[26][34]=2*g[25][33]-g[24][32]
    g[26][0]=2*g[26][1]-g[26][2]
    g[26][35]=2*g[26][34]-g[26][33]
    g[26][36]=2*g[26][35]-g[26][34]
    g[27][0]=2*g[26][1]-g[25][2]
    g[27][1]=2*g[26][1]-g[25][1]
    g[27][34]=2*g[26][34]-g[25][34]
    g[27][35]=2*g[26][34]-g[25][33]
    g[27][36]=2*g[27][35]-g[27][34]
    g[28][0]=2*g[27][0]-g[26][0]
    g[28][1]=2*g[27][1]-g[26][1]
    g[28][34]=2*g[27][34]-g[26][34]
    g[28][35]=2*g[27][35]-g[26][35]
    g[28][36]=2*g[27][35]-g[26][34]
    # Surface persists the entire 29x37 padded int32 map in Tintless core
    # state at +0x5e64; later requests consume this state.
    for yy in range(ph):
        for xx in range(pw):
            wi32(u,state+0x5e64+(yy*pw+xx)*4,g[yy][xx])
    cell_x=ru16(u,state+0x08); cell_y=ru16(u,state+0x0a)
    mesh_h=ru8(u,state+0x20); mesh_w=ru8(u,state+0x21); factor=ru8(u,state+0x2a)
    off_y=ru16(u,state+0x0e); off_x=ru16(u,state+0x10); add_x=ru16(u,state+0x22); add_y=ru16(u,state+0x24)
    den_y=ru16(u,state+0x26); den_x=ru16(u,state+0x28)
    start_x=f32(1.5-f32(f32(add_x+off_x)/f32(cell_x))); start_x=f32(max(0.0,start_x))
    start_y=f32(1.5-f32(f32(add_y+off_y)/f32(cell_y))); start_y=f32(max(0.0,start_y))
    step_x=f32(f32(den_x*factor)/f32(cell_x)); step_y=f32(f32(den_y*factor)/f32(cell_y))
    for y in range(mesh_h):
        yf=f32(f32(f32(float(y))*step_y)+start_y); iy=int(yf); fy=f32(yf-f32(iy)); omy=f32(1.0-fy)
        for x in range(mesh_w):
            xf=f32(f32(f32(float(x))*step_x)+start_x); ix=int(xf); fx=f32(xf-f32(ix)); omx=f32(1.0-fx)
            top=f32(f32(f32(float(g[iy][ix]))*omx)+f32(f32(float(g[iy][ix+1]))*fx))
            bot=f32(f32(f32(float(g[iy+1][ix]))*omx)+f32(f32(float(g[iy+1][ix+1]))*fx))
            wf32(u,dst+(y*mesh_w+x)*4,f32(f32(top*omy)+f32(bot*fy)))


def solver_prepare_layout(u,state):
    """Clean-room translation of RVA 0xc9a288.

    Re-layout two 0x600-byte state planes around a zeroed 0x800-byte
    workspace. This helper performs no arithmetic.
    """
    a=bytes(u.mem_read(state,0x600))
    b=bytes(u.mem_read(state+0x600,0x600))
    u.mem_write(state+0xc00,a)
    u.mem_write(state+0x1200,b'\0'*0x800)
    u.mem_write(state+0x1a00,b)


def periodic_forward_gradients(u,mode,src,dx,dy):
    """Active mode-2 clean-room translation of RVA 0xc98270.

    Compute periodic forward differences on the 24x32 float field.
    """
    if (mode & 0xffff) not in (1,2):
        raise ValueError('unsupported inactive Tintless gradient mode')
    a=[rf32(u,src+i*4) for i in range(REGIONS)]
    for yy in range(GRID_H):
        for xx in range(GRID_W):
            i=yy*GRID_W+xx
            rx=yy*GRID_W+((xx+1)%GRID_W)
            ry=((yy+1)%GRID_H)*GRID_W+xx
            wf32(u,dx+i*4,f32(a[rx]-a[i]))
            wf32(u,dy+i*4,f32(a[ry]-a[i]))


def spectral_threshold_active(u,state):
    """Active (mode0=2, mode1=2) clean-room branch of RVA 0xc989d0."""
    mode0=ru16(u,state); mode1=ru16(u,state+2)
    if mode0!=2 or mode1 not in (1,2):
        raise ValueError('unsupported inactive Tintless threshold mode')
    levels=[rf32(u,state+0x30+i*4) for i in range(16)]
    thresholds=[]
    hundred=f32(100.0)
    for v in levels:
        q=f32(v/hundred)
        thresholds.append(f32(q*q))
    classes=[int(rf32(u,state+0x78+i*4)) for i in range(REGIONS)]
    for c in classes:
        if not 0<=c<16: raise ValueError('Tintless threshold class out of range')
    def apply(re_base,im_base,ys,xs):
        for yy in ys:
            for xx in xs:
                i=yy*GRID_W+xx
                re=rf32(u,re_base+i*4); im=rf32(u,im_base+i*4)
                mag=f32(f32(re*re)+f32(im*im))
                if thresholds[classes[i]] < mag:
                    wf32(u,re_base+i*4,0.0); wf32(u,im_base+i*4,0.0)
    apply(state+0x5e64,state+0x6a64,range(GRID_H),range(GRID_W-1))
    apply(state+0x7664,state+0x8264,range(GRID_H-1),range(GRID_W))


def project_periodic_zero_mean(u,mode,a,b,c,d):
    """Active mode-2 clean-room branch of RVA 0xc998b8."""
    if (mode & 0xffffffff)!=2:
        raise ValueError('unsupported inactive Tintless projection mode')
    def rows(base):
        vals=[rf32(u,base+i*4) for i in range(REGIONS)]
        for yy in range(GRID_H):
            off=yy*GRID_W
            total=f32(0.0)
            for xx in range(GRID_W-1): total=f32(total+vals[off+xx])
            mean_vec=struct.unpack('<f',struct.pack('<I',0x3d042108))[0]
            mean16=f32(total*mean_vec)
            mean_scalar=f32(total/f32(31.0))
            for xx in range(16): vals[off+xx]=f32(vals[off+xx]-mean16)
            for xx in range(16,GRID_W-1): vals[off+xx]=f32(vals[off+xx]-mean_scalar)
            vals[off+GRID_W-1]=f32(0.0)
        u.mem_write(base,struct.pack('<768f',*vals))
    def cols(base):
        vals=[rf32(u,base+i*4) for i in range(REGIONS)]
        for xx in range(GRID_W):
            total=f32(0.0)
            for yy in range(GRID_H-1): total=f32(total+vals[yy*GRID_W+xx])
            mean=f32(total/f32(23.0))
            for yy in range(GRID_H-1): vals[yy*GRID_W+xx]=f32(vals[yy*GRID_W+xx]-mean)
            vals[(GRID_H-1)*GRID_W+xx]=f32(0.0)
        u.mem_write(base,struct.pack('<768f',*vals))
    rows(a); rows(b); cols(c); cols(d)


def periodic_divergence(u,mode,a,b,out):
    """Active mode-2 clean-room branch of RVA 0xc99130."""
    if (mode & 0xffff) not in (1,2):
        raise ValueError('unsupported inactive Tintless divergence mode')
    av=[rf32(u,a+i*4) for i in range(REGIONS)]
    bv=[rf32(u,b+i*4) for i in range(REGIONS)]
    ov=[]
    for yy in range(GRID_H):
        for xx in range(GRID_W):
            i=yy*GRID_W+xx
            left=yy*GRID_W+((xx-1)%GRID_W)
            up=((yy-1)%GRID_H)*GRID_W+xx
            da=f32(av[left]-av[i])
            db=f32(bv[up]-bv[i])
            ov.append(f32(da+db))
    u.mem_write(out,struct.pack('<768f',*ov))


def solver_orchestration(u,state,field_a,field_b):
    """Clean-room active front translation of RVA 0xc9a630."""
    mode=ru16(u,state+2)
    periodic_forward_gradients(u,mode,field_a,state+0x5e64,state+0x7664)
    periodic_forward_gradients(u,mode,field_b,state+0x6a64,state+0x8264)
    spectral_threshold_active(u,state)
    project_periodic_zero_mean(u,mode,state+0x5e64,state+0x6a64,state+0x7664,state+0x8264)
    periodic_divergence(u,mode,state+0x5e64,state+0x7664,state+0x8e64)
    periodic_divergence(u,mode,state+0x6a64,state+0x8264,state+0xae64)
    solver_prepare_layout(u,state+0x8e64)
    solver_prepare_layout(u,state+0xae64)
    fft2d_forward_64x32(u,state+0x8e64,state+0xae64,state+0x5e64,
                        state+0xc84,state+0xd04,state+0xe24,state+0xe04)
    for i in range(0x800):
        off=i*4
        w=rf32(u,state+0xe64+off)
        wf32(u,state+0x8e64+off,f32(rf32(u,state+0x8e64+off)*w))
        wf32(u,state+0xae64+off,f32(rf32(u,state+0xae64+off)*w))
    wf32(u,state+0x8e64,0.0)
    wf32(u,state+0xae64,0.0)
    fft2d_inverse_64x32(u,state+0x8e64,state+0xae64,state+0x5e64,
                        state+0xc84,state+0xd04,state+0xe24,state+0xe04)
