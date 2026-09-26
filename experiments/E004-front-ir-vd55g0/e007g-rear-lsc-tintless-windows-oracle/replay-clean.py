#!/usr/bin/env python3
from __future__ import annotations
import argparse, ctypes, hashlib, importlib.util, json, math, struct, subprocess, tempfile
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PROD=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
E3I=REPO/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization'
CLFILE=E3I/'g-cleanroom-lsc-upstream/cleanroom-front-lsc.py'
CFILE=E3I/'i-cleanroom-tintless/cleanroom-tintless-helpers.py'
KFILE=E3I/'k-cleanroom-lsc-backend/generate-cleanroom-front-lsc-wire.py'
DECFILE=PROD/'decode_imx681_chromatix.py'
GOLDFILE=PROD/'prove-lsc-live-golden-authority.py'
PACKFILE=PROD/'prove-lsc-live-staging-pack.py'
NATIVE=E3I/'x-native-live-lsc-deadline/native-tintless-core.c'
TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin')
OTP=PROD/'oracle-vss-20260902-local/REQ1_LSC_CAL_SLOT_0DF0.bin'
REAR_X1=PROD/'oracle-carved-20260902/TINTCTX_REQ5/REQ5_CB_X1_PRE_0400.bin'
TUNING_SHA='4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635'
OTP_SHA='fb14d234d55317c9665de39fe93ddeb76ee06b9cffc64bee8d250152ae9dfa18'
X1_SHA='b8bb8f82548baa20ea3ce5156d9da1837f65415a6cfc907813c858c7cfcaaffd'
FULL_W,FULL_H,OUT_W,OUT_H,CROP_X,CROP_Y,SCALE=4076,2806,4064,2286,6,260,1
WRAP=0x270000001000; CORE=0x270000100000; X1A=0x270000003000
IN=0x270000040000; OUT=0x270000050000; D3=0x270000030000; D4=0x270000031000

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
def shaf(p):return sha(p.read_bytes())
def need(v,m):
    if not v: raise RuntimeError(m)
def f32(v):return struct.unpack('<f',struct.pack('<f',float(v)))[0]
def descriptor(base):
    b=bytearray(0x28);struct.pack_into('<H',b,0,221)
    for i,o in enumerate((8,0x10,0x18,0x20)):struct.pack_into('<Q',b,o,base+i*0x374)
    return bytes(b)

def rec_bytes(blob,hdr,recs,sid,dec):
    b=dec.data_bytes(blob,hdr['sections'][1],recs[sid])
    need(len(b)==0xdf0,f'sid {sid:#x}: leaf bytes')
    return b

def select_x22(cct, leaves, CL):
    # Rear lower-AEC child sid 0x29a:
    # [1,3100] -> 0x29c; [3500,4200] -> 0x29e; [4800,10000] -> 0x2a0.
    if 1.0 <= cct <= 3100.0:
        return leaves[0x29c],{'mode':'leaf','sid':'0x29c','ratio':None}
    if 3100.0 < cct < 3500.0:
        ratio=f32(f32(cct-3100.0)/f32(400.0))
        return CL.interpolate_leaf(leaves[0x29c],leaves[0x29e],ratio),{'mode':'gap','sid':'0x29c->0x29e','ratio':ratio}
    if 3500.0 <= cct <= 4200.0:
        return leaves[0x29e],{'mode':'leaf','sid':'0x29e','ratio':None}
    if 4200.0 < cct < 4800.0:
        ratio=f32(f32(cct-4200.0)/f32(600.0))
        return CL.interpolate_leaf(leaves[0x29e],leaves[0x2a0],ratio),{'mode':'gap','sid':'0x29e->0x2a0','ratio':ratio}
    if 4800.0 <= cct <= 10000.0:
        return leaves[0x2a0],{'mode':'leaf','sid':'0x2a0','ratio':None}
    raise RuntimeError(f'CCT outside captured lower branch: {cct}')

def mesh_geometry(active_w,active_h):
    # Exact first valid candidate of source-locked 0x9b6048/0x9b5b48 search.
    blocks_x,blocks_y,shift=16,12,3
    q=1<<shift
    hx,hy=active_w>>1,active_h>>1
    cells_x=(hx+blocks_x-1)//blocks_x
    cells_y=(hy+blocks_y-1)//blocks_y
    step_x=((cells_x+q-1)//q)*q
    step_y=((cells_y+q-1)//q)*q
    rx=step_x*blocks_x-hx
    ry=step_y*blocks_y-hy
    need(step_x>=18 and step_y>=9 and step_x//q>=9 and step_y//q>=9,'geometry candidate constraints')
    need(step_x>rx and step_y>ry and step_x-((rx+1)//2)>=18,'geometry residual constraints')
    return step_x,step_y,rx,ry

def resample_channel_generic(channel,CL,geom):
    need(len(channel)==221,'channel samples')
    full_w,full_h,out_w,out_h,crop_x,crop_y,scale=geom
    src=np.asarray(channel,dtype=np.float32).reshape(13,17)
    pad=np.zeros((15,19),dtype=np.float32);pad[1:14,1:18]=src
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
        v=CL.div(CL.add(py,sy),sy);iv=int(np.floor(v));fy=CL.sub(v,CL.f32(iv));wy=CL.catmull_weights(fy)
        for ix in range(17):
            px=CL.f32(x0+ix*stepx*scale)
            u=CL.div(CL.add(px,sx),sx);iu=int(np.floor(u));fx=CL.sub(u,CL.f32(iu));wx=CL.catmull_weights(fx)
            if iy in (0,12) or ix in (0,16):
                omx=CL.sub(CL.f32(1.0),fx)
                top=CL.add(CL.mul(pad[iv,iu+1],fx),CL.mul(pad[iv,iu],omx))
                omy=CL.sub(CL.f32(1.0),fy);z=CL.mul(top,omy)
                bot=CL.add(CL.mul(pad[iv+1,iu+1],fx),CL.mul(pad[iv+1,iu],omx))
                z=CL.add(z,CL.mul(bot,fy))
            else:
                hc=CL.h4(pad[iv,iu-1:iu+3],wx);hp=CL.h4(pad[iv-1,iu-1:iu+3],wx)
                hn=CL.h4(pad[iv+1,iu-1:iu+3],wx);h2=CL.h4(pad[iv+2,iu-1:iu+3],wx)
                z=CL.mul(hc,wy[1]);z=CL.add(z,CL.mul(hp,wy[0]));z=CL.add(z,CL.mul(hn,wy[2]));z=CL.add(z,CL.mul(h2,wy[3]))
            z=CL.f32(max(CLAMP_MIN,z));z=CL.f32(min(CLAMP_MAX,z));out[iy,ix]=z
    return out.astype('<f4').tobytes()

CLAMP_MIN=np.float32(1.0);CLAMP_MAX=np.float32(15.99899959564209)

def resample_x23_generic(x23,CL,geom):
    vals=struct.unpack('<884f',x23[:0xdd0])
    return b''.join(resample_channel_generic(vals[c*221:(c+1)*221],CL,geom) for c in range(4))

def compile_native(out):
    subprocess.run(['gcc','-O3','-shared','-fPIC','-std=c11','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror',str(NATIVE),'-lm','-o',str(out)],check=True)

def core_api(so):
    l=ctypes.CDLL(str(so));f=l.tintless_core_mode2_native
    f.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p];f.restype=ctypes.c_int
    return f

def main():
    ap=argparse.ArgumentParser();ap.add_argument('capture_dir',type=Path);ap.add_argument('--out',type=Path,default=HERE/'CLEAN-REPLAY-SAFE.json');a=ap.parse_args()
    need(shaf(TUNING)==TUNING_SHA,'rear tuning SHA');need(shaf(OTP)==OTP_SHA,'rear OTP SHA');need(shaf(REAR_X1)==X1_SHA,'rear x1 SHA')
    CL=load(CLFILE,'e007g_cl');C=load(CFILE,'e007g_tint');K=load(KFILE,'e007g_wire');D=load(DECFILE,'e007g_dec');GP=load(GOLDFILE,'e007g_gold');P=load(PACKFILE,'e007g_pack')
    blob=TUNING.read_bytes();hdr=D.parse_header(blob);need(hdr['module_name']=='com.surface.tuned.rfc_ov13858','rear module')
    recs,_=D.parse_symbol_table(blob,hdr['sections'][0],hdr['sections'][1])
    # Source-lock lower-AEC CCT topology.
    raw=D.data_bytes(blob,hdr['sections'][1],recs[0x29a]);words=struct.unpack('<18I',raw)
    need(words==(0x3f800000,0x4541c000,0,0x29b,1,0x29c,0x455ac000,0x45834000,0,0x29d,1,0x29e,0x45960000,0x461c4000,0,0x29f,1,0x2a0),'rear lower-CCT topology')
    leaves={sid:rec_bytes(blob,hdr,recs,sid,D) for sid in (0x29c,0x29e,0x2a0)}
    gold=GP.parse_golden(TUNING);need(gold is not None,'rear golden parse');otp=CL.parse_otp(OTP.read_bytes())
    # Prove generic geometry translation reproduces accepted front implementation exactly.
    # Use one arbitrary deterministic 884-float input so this checks arithmetic, not a capture.
    test=struct.pack('<884f',*[1.0+(i%17)/32.0 for i in range(884)])+bytes(0x20)
    front_geom=(4048,3152,3840,2160,104,496,1)
    rear_geom=(FULL_W,FULL_H,OUT_W,OUT_H,CROP_X,CROP_Y,SCALE)
    generic_front=resample_x23_generic(test,CL,front_geom);accepted_front=CL.resample_x23(test)
    need(generic_front==accepted_front,'generic resampler != accepted front')
    stepx,stepy,rx,ry=mesh_geometry(OUT_W,OUT_H)
    need((stepx,stepy,rx,ry)==(128,96,16,9),'rear geometry derivation')

    x1=REAR_X1.read_bytes();need(struct.unpack_from('<7I',x1,0x1c)==(4064,2286,126,94,32,24,0),'rear x1 geometry')
    m=K.SparseMemory();m.mem_write(WRAP,bytes(0x1090));m.mem_write(X1A,x1);m.mem_write(D3,descriptor(IN));m.mem_write(D4,descriptor(OUT))
    dirty=C.update_wrapper_config_front(m,WRAP,X1A);need(dirty,'rear initial config not dirty');C.initialize_core_front_mode2(m,CORE,WRAP)
    state=bytearray(m.mem_read(CORE,C.CORE_BYTES))

    with tempfile.TemporaryDirectory(prefix='e007g-') as td:
        so=Path(td)/'libtintless.so';compile_native(so);core=core_api(so)
        rows=[];all_exact=True
        for req in range(4,19):
            q=f'{req:02d}';stats=(a.capture_dir/f'R{q}_TINTLESS_STATS.bin').read_bytes();trig=(a.capture_dir/f'R{q}_TRIGGER.bin').read_bytes();staging=(a.capture_dir/f'R{q}_LSC_STAGING.bin').read_bytes()
            need(len(stats)==0x12bec and len(trig)==0x100 and len(staging)==0x18a0,f'R{req} sizes')
            lux=struct.unpack_from('<f',trig,0x38)[0];cct=struct.unpack_from('<f',trig,0x48)[0]
            need(1.0<=lux<=340.0,f'R{req} lux left rear lower AEC branch: {lux}')
            x22,sel=select_x22(cct,leaves,CL);x23=CL.calibrate(x22,gold['values'],otp);pre=resample_x23_generic(x23,CL,rear_geom)
            raw=stats+bytes(0x12c20-len(stats));outb=bytearray(b'\0'*0xdd0)
            SA=(ctypes.c_ubyte*len(state)).from_buffer(state);RA=(ctypes.c_ubyte*len(raw)).from_buffer_copy(raw);FA=(ctypes.c_float*884).from_buffer_copy(pre);OA=(ctypes.c_float*884).from_buffer(outb)
            rc=core(SA,len(state),RA,len(raw),FA,OA);need(rc==0,f'R{req} native Tintless rc {rc}')
            m.mem_write(IN,pre+bytes(0x20));m.mem_write(OUT,outb+bytes(0x20));C._wrapper_temporal_blend(m,WRAP,D3,D4)
            output=m.mem_read(OUT,0xdf0);got=K.wire_from_output(output);geo,*want=P.pack_live_staging(staging);want=tuple(want)+((want[0]+want[1])[0x22e:0x42e],)
            exact=[got[i]==want[i] for i in range(4)];all_exact=all_exact and all(exact)
            rows.append({'request':req,'lux':float(lux),'cct':float(cct),'selection':sel,'x22_sha256':sha(x22),'x23_sha256':sha(x23),'pretintless_sha256':sha(pre),'output_sha256':sha(output),'lsc0_sha256':sha(got[0]),'lsc1_sha256':sha(got[1]),'lsc2_sha256':sha(got[2]),'gic_sha256':sha(got[3]),'target_lsc0_sha256':sha(want[0]),'target_lsc1_sha256':sha(want[1]),'target_lsc2_sha256':sha(want[2]),'target_gic_sha256':sha(want[3]),'exact':exact})
        result={'schema':'E007g-clean-rear-lsc-replay-v1','status':'PASS' if all_exact else 'MISMATCH','requests':rows,'all_15_wire_exact':all_exact,'generic_resampler_front_differential_exact':True,'rear_geometry':{'full':[4076,2806],'output':[4064,2286],'crop':[6,260],'half_steps':[stepx,stepy],'residual':[rx,ry]},'rear_x1_sha256':X1_SHA,'rear_tuning_sha256':TUNING_SHA,'rear_calibration_slot_sha256':OTP_SHA,'raw_capture_values_emitted':False}
        a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('E007G_CLEAN_REPLAY_'+result['status'])
        print('exact_requests='+','.join(str(x['request']) for x in rows if all(x['exact'])))
        print('mismatch_requests='+','.join(str(x['request']) for x in rows if not all(x['exact'])))
        for x in rows:
            if not all(x['exact']):print('R',x['request'],'exact',x['exact'],'sel',x['selection'])
        if not all_exact: raise SystemExit(2)
if __name__=='__main__':main()
