#!/usr/bin/env python3
from __future__ import annotations
import base64, ctypes, hashlib, importlib.util, json, struct, subprocess
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
E3I=REPO/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization'
CLFILE=E3I/'g-cleanroom-lsc-upstream/cleanroom-front-lsc.py'
CFILE=E3I/'i-cleanroom-tintless/cleanroom-tintless-helpers.py'
KFILE=E3I/'k-cleanroom-lsc-backend/generate-cleanroom-front-lsc-wire.py'
NATIVE=E3I/'x-native-live-lsc-deadline/native-tintless-core.c'
AUTHFILE=HERE/'authority.json'

WRAP=0x270000001000
CORE=0x270000100000
X1A=0x270000003000
IN=0x270000040000
OUT=0x270000050000
D3=0x270000030000
D4=0x270000031000
CLAMP_MIN=np.float32(1.0)
CLAMP_MAX=np.float32(15.99899959564209)

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def f32(v): return struct.unpack('<f',struct.pack('<f',float(v)))[0]
def need(v,m):
    if not v: raise RuntimeError(m)

def descriptor(base):
    b=bytearray(0x28)
    struct.pack_into('<H',b,0,221)
    for i,o in enumerate((8,0x10,0x18,0x20)):
        struct.pack_into('<Q',b,o,base+i*0x374)
    return bytes(b)

def mesh_geometry(active_w,active_h):
    blocks_x,blocks_y,shift=16,12,3
    q=1<<shift
    hx,hy=active_w>>1,active_h>>1
    cells_x=(hx+blocks_x-1)//blocks_x
    cells_y=(hy+blocks_y-1)//blocks_y
    step_x=((cells_x+q-1)//q)*q
    step_y=((cells_y+q-1)//q)*q
    rx=step_x*blocks_x-hx
    ry=step_y*blocks_y-hy
    need(step_x>=18 and step_y>=9 and step_x//q>=9 and step_y//q>=9,'geometry candidate')
    need(step_x>rx and step_y>ry and step_x-((rx+1)//2)>=18,'geometry residual')
    return step_x,step_y,rx,ry

def resample_channel(channel,CL,geom):
    need(len(channel)==221,'channel samples')
    full_w,full_h,out_w,out_h,crop_x,crop_y,scale=geom
    src=np.asarray(channel,dtype=np.float32).reshape(13,17)
    pad=np.zeros((15,19),dtype=np.float32)
    pad[1:14,1:18]=src
    for r in range(1,14):
        pad[r,0]=CL.sub(CL.add(pad[r,1],pad[r,1]),pad[r,2])
        pad[r,18]=CL.sub(CL.add(pad[r,17],pad[r,17]),pad[r,16])
    for c in range(19):
        pad[0,c]=CL.sub(CL.add(pad[1,c],pad[1,c]),pad[2,c])
        pad[14,c]=CL.sub(CL.add(pad[13,c],pad[13,c]),pad[12,c])
    sx=CL.div(CL.f32((full_w>>1)-1),CL.f32(16.0))
    sy=CL.div(CL.f32((full_h>>1)-1),CL.f32(12.0))
    stepx,stepy,rx,ry=mesh_geometry(out_w,out_h)
    x0=crop_x//2-((rx+1)//2)*scale
    y0=crop_y//2-((ry+1)//2)*scale
    out=np.empty((13,17),dtype=np.float32)
    for iy in range(13):
        py=CL.f32(y0+iy*stepy*scale)
        v=CL.div(CL.add(py,sy),sy)
        iv=int(np.floor(v))
        fy=CL.sub(v,CL.f32(iv))
        wy=CL.catmull_weights(fy)
        for ix in range(17):
            px=CL.f32(x0+ix*stepx*scale)
            u=CL.div(CL.add(px,sx),sx)
            iu=int(np.floor(u))
            fx=CL.sub(u,CL.f32(iu))
            wx=CL.catmull_weights(fx)
            if iy in (0,12) or ix in (0,16):
                omx=CL.sub(CL.f32(1.0),fx)
                top=CL.add(CL.mul(pad[iv,iu+1],fx),CL.mul(pad[iv,iu],omx))
                omy=CL.sub(CL.f32(1.0),fy)
                z=CL.mul(top,omy)
                bot=CL.add(CL.mul(pad[iv+1,iu+1],fx),CL.mul(pad[iv+1,iu],omx))
                z=CL.add(z,CL.mul(bot,fy))
            else:
                hc=CL.h4(pad[iv,iu-1:iu+3],wx)
                hp=CL.h4(pad[iv-1,iu-1:iu+3],wx)
                hn=CL.h4(pad[iv+1,iu-1:iu+3],wx)
                h2=CL.h4(pad[iv+2,iu-1:iu+3],wx)
                z=CL.mul(hc,wy[1])
                z=CL.add(z,CL.mul(hp,wy[0]))
                z=CL.add(z,CL.mul(hn,wy[2]))
                z=CL.add(z,CL.mul(h2,wy[3]))
            z=CL.f32(max(CLAMP_MIN,z))
            z=CL.f32(min(CLAMP_MAX,z))
            out[iy,ix]=z
    return out.astype('<f4').tobytes()

def resample_mesh(x23,CL,geom):
    vals=struct.unpack('<884f',x23[:0xdd0])
    return b''.join(resample_channel(vals[c*221:(c+1)*221],CL,geom) for c in range(4))

def compile_native(out):
    subprocess.run([
        'gcc','-O3','-shared','-fPIC','-std=c11','-fno-fast-math',
        '-ffp-contract=off','-Wall','-Wextra','-Werror',str(NATIVE),'-lm','-o',str(out)
    ],check=True)

class RearDynamicLsc:
    def __init__(self,so:Path,authority:Path=AUTHFILE):
        self.auth=json.loads(authority.read_text())
        need(self.auth.get('schema')=='sp11-rear-ov13858-lsc-clean-authority-v1','authority schema')
        self.CL=load(CLFILE,'e007h_cl_runtime')
        self.C=load(CFILE,'e007h_tint_runtime')
        self.K=load(KFILE,'e007h_wire_runtime')
        self.leaves={k:base64.b64decode(v) for k,v in self.auth['leaf_b64'].items()}
        self.gold=tuple(float(v) for v in self.auth['golden_int'])
        self.otp=[tuple(float(v) for v in ch) for ch in self.auth['otp_int_channels']]
        self.x1=base64.b64decode(self.auth['x1_b64'])
        g=self.auth['geometry']
        self.geom=(*g['full'],*g['output'],*g['crop'],g['scale'])
        need(mesh_geometry(g['output'][0],g['output'][1])==tuple(g['half_steps']+g['residual']),'geometry drift')
        lib=ctypes.CDLL(str(so))
        self.core=lib.tintless_core_mode2_native
        self.core.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p]
        self.core.restype=ctypes.c_int
        self.reset()

    def reset(self):
        m=self.K.SparseMemory()
        m.mem_write(WRAP,bytes(0x1090))
        m.mem_write(X1A,self.x1)
        m.mem_write(D3,descriptor(IN))
        m.mem_write(D4,descriptor(OUT))
        need(self.C.update_wrapper_config_front(m,WRAP,X1A),'initial wrapper config')
        self.C.initialize_core_front_mode2(m,CORE,WRAP)
        self.mem=m
        self.state=bytearray(m.mem_read(CORE,self.C.CORE_BYTES))

    def _select_x22(self,lux,cct):
        d=self.auth['domain']
        need(d['lux_min_inclusive']<=lux<=d['lux_max_inclusive'],'rear LSC AEC domain unproven')
        c=f32(cct)
        a=self.leaves['0x29c'];b=self.leaves['0x29e'];w=self.leaves['0x2a0']
        if 1.0<=c<=3100.0:
            return a,{'mode':'leaf','sid':'0x29c','ratio':None}
        if 3100.0<c<3500.0:
            r=f32(f32(c-3100.0)/f32(400.0))
            return self.CL.interpolate_leaf(a,b,r),{'mode':'gap','sid':'0x29c->0x29e','ratio':r}
        if 3500.0<=c<=4200.0:
            return b,{'mode':'leaf','sid':'0x29e','ratio':None}
        if 4200.0<c<4800.0:
            r=f32(f32(c-4200.0)/f32(600.0))
            return self.CL.interpolate_leaf(b,w,r),{'mode':'gap','sid':'0x29e->0x2a0','ratio':r}
        if 4800.0<=c<=10000.0:
            return w,{'mode':'leaf','sid':'0x2a0','ratio':None}
        raise RuntimeError('rear LSC CCT domain unproven')

    def run_parsed(self,stats:bytes,lux:float,cct:float):
        need(0x12bec<=len(stats)<=0x12c20,'parsed Tintless stats size')
        need(struct.unpack_from('<I',stats,4)[0]==0x300 and (struct.unpack_from('<I',stats,0)[0]&2),'parsed Tintless stats ABI')
        x22,sel=self._select_x22(float(lux),float(cct))
        x23=self.CL.calibrate(x22,self.gold,self.otp)
        pre=resample_mesh(x23,self.CL,self.geom)
        raw=stats+bytes(0x12c20-len(stats))
        outb=bytearray(0xdd0)
        SA=(ctypes.c_ubyte*len(self.state)).from_buffer(self.state)
        RA=(ctypes.c_ubyte*len(raw)).from_buffer_copy(raw)
        FA=(ctypes.c_float*884).from_buffer_copy(pre)
        OA=(ctypes.c_float*884).from_buffer(outb)
        need(self.core(SA,len(self.state),RA,len(raw),FA,OA)==0,'native Tintless rc')
        self.mem.mem_write(IN,pre+bytes(0x20))
        self.mem.mem_write(OUT,outb+bytes(0x20))
        self.C._wrapper_temporal_blend(self.mem,WRAP,D3,D4)
        output=self.mem.mem_read(OUT,0xdf0)
        wire=self.K.wire_from_output(output)
        return wire,{
            'selection':sel,
            'x22_sha256':sha(x22),
            'pretintless_sha256':sha(pre),
            'output_sha256':sha(output),
            'lsc0_sha256':sha(wire[0]),
            'lsc1_sha256':sha(wire[1]),
            'lsc2_sha256':sha(wire[2]),
            'gic_sha256':sha(wire[3]),
        }

if __name__=='__main__':
    print('E007H_REAR_LSC_RUNTIME_MODULE')
