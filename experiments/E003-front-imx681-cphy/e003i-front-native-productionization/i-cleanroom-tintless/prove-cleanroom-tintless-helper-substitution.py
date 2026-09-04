#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3,UC_ARM64_REG_X4,UC_ARM64_REG_X5,UC_ARM64_REG_X6,UC_ARM64_REG_X7,UC_ARM64_REG_X9,UC_ARM64_REG_SP,UC_ARM64_REG_D0,UC_ARM64_REG_D1,UC_ARM64_REG_D2,UC_ARM64_REG_D3,UC_ARM64_REG_PC,UC_ARM64_REG_LR

def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m

def main():
 here=Path(__file__).resolve().parent;repo=here.parents[3];hdir=here.parent/'h-integrated-lsc-chain';prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
 H=load(hdir/'generate-integrated-front-lsc-wire.py','e003i_i_h');C=load(here/'cleanroom-tintless-helpers.py','e003i_i_c');proof=load(prod/'prove-lsc-front-atomic-tintless-replay.py','e003i_i_p');surface=load(prod/'prove-gtm-live-exact-replay.py','e003i_i_s')
 dll=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll');cap=repo.parent/'.local-oracles/oracle-live-20260904-front-atomic'
 proof.verify_device_bytes(dll,surface);H.verify_fixture_subset(cap,prod/'FRONT-ATOMIC-TINTLESS-STAGING-20260904.json');pre,_=H.build_pretintless(repo);base=H.run_sequence(cap,dll,proof,surface,pre,0,'zero')
 counts={'preprocess_stats':0,'smooth_stats_map':0,'accumulate_float_fields':0,'ln_float_field':0,'quantize_float_field_q16':0,'pad_mesh_extrapolated':0,'bicubic_row_kernel':0,'interpolate_mesh_to_stats':0,'fft_radix2_inplace':0,'transpose_u32_matrix':0,'fft2d_forward_64x32':0,'fft2d_inverse_64x32':0,'exp_q16_postprocess':0,'map_correction_to_mesh':0,'solver_prepare_layout':0,'periodic_forward_gradients':0,'spectral_threshold_active':0,'project_periodic_zero_mean':0,'periodic_divergence':0,'solver_orchestration':0,'solver_apply_box3x3':0,'final_application_mode2':0,'core_mode2':0,'wrapper_front_mode2':0};Orig=surface.SurfaceEmu
 class Hybrid(Orig):
  def __init__(self,*a,**kw):
   super().__init__(*a,**kw);u=self.uc;B=surface.BASE
   def ret(uc): uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_LR))
   TRAMP=0x62001000;STUB=0x62000000;ADAPT=0x62002000;IFSHIM=0x62003000
   for page in (TRAMP,ADAPT,IFSHIM):
    try:u.mem_map(page,0x1000)
    except Exception:pass
   u.mem_write(TRAMP,b'\x1f\x20\x03\xd5');u.mem_write(IFSHIM,b'\x09\x0c\x40\xf9\x1f\x20\x03\xd5')
   pending={}
   def finish_wrap(uc,args,orig_lr,new_core=0):
    rc=C.wrapper_front_mode2(uc,args[0],args[1],args[2],args[3],args[4],new_core,ADAPT);uc.reg_write(UC_ARM64_REG_X0,rc & 0xffffffffffffffff);uc.reg_write(UC_ARM64_REG_PC,orig_lr)
   def dispatch_wrap(uc,wrap,raw,orig_lr):
    args=(wrap,)+raw
    if C.ru64(uc,wrap+0x128)==0:
     pending['args']=args;pending['lr']=orig_lr;uc.reg_write(UC_ARM64_REG_X2,C.CORE_BYTES);uc.reg_write(UC_ARM64_REG_LR,TRAMP);uc.reg_write(UC_ARM64_REG_PC,STUB)
    else: finish_wrap(uc,args,orig_lr,0)
   def hwrap(uc,a,s,d):
    counts['wrapper_front_mode2']+=1
    pending['raw']=(uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3),uc.reg_read(UC_ARM64_REG_X4));pending['entry_lr']=uc.reg_read(UC_ARM64_REG_LR)
    uc.reg_write(UC_ARM64_REG_PC,IFSHIM)
   def hifshim(uc,a,s,d):
    wrap=uc.reg_read(UC_ARM64_REG_X9);dispatch_wrap(uc,wrap,pending.pop('raw'),pending.pop('entry_lr'))
   def htramp(uc,a,s,d):
    core=uc.reg_read(UC_ARM64_REG_X0);finish_wrap(uc,pending.pop('args'),pending.pop('lr'),core)
   def hp(uc,a,s,d): counts['preprocess_stats']+=1;C.preprocess_stats(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1));ret(uc)
   def hs(uc,a,s,d): counts['smooth_stats_map']+=1;C.smooth_stats_map(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2));ret(uc)
   def ha(uc,a,s,d): counts['accumulate_float_fields']+=1;C.accumulate_float_fields(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3));ret(uc)
   def hl(uc,a,s,d): counts['ln_float_field']+=1;C.ln_float_field(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1));ret(uc)
   def hq(uc,a,s,d): counts['quantize_float_field_q16']+=1;C.quantize_float_field_q16(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1));ret(uc)
   def hpad(uc,a,s,d): counts['pad_mesh_extrapolated']+=1;C.pad_mesh_extrapolated(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2));ret(uc)
   def hinterp(uc,a,s,d): counts['interpolate_mesh_to_stats']+=1;C.interpolate_mesh_to_stats(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2));ret(uc)
   def hfft(uc,a,s,d): counts['fft_radix2_inplace']+=1;C.fft_radix2_inplace(uc,uc.reg_read(UC_ARM64_REG_X0)&0xffffffff,uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3),uc.reg_read(UC_ARM64_REG_X4));ret(uc)
   def htrans(uc,a,s,d): counts['transpose_u32_matrix']+=1;C.transpose_u32_matrix(uc,uc.reg_read(UC_ARM64_REG_X0)&0xffffffff,uc.reg_read(UC_ARM64_REG_X1)&0xffffffff,uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3));ret(uc)
   def hfwd(uc,a,s,d):
    counts['fft2d_forward_64x32']+=1;sp=uc.reg_read(UC_ARM64_REG_SP);perm32=C.ru64(uc,sp)
    C.fft2d_forward_64x32(uc,uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3),uc.reg_read(UC_ARM64_REG_X4),uc.reg_read(UC_ARM64_REG_X5),uc.reg_read(UC_ARM64_REG_X6),uc.reg_read(UC_ARM64_REG_X7),perm32);ret(uc)
   def hinv(uc,a,s,d):
    counts['fft2d_inverse_64x32']+=1;sp=uc.reg_read(UC_ARM64_REG_SP);perm32=C.ru64(uc,sp)
    C.fft2d_inverse_64x32(uc,uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3),uc.reg_read(UC_ARM64_REG_X4),uc.reg_read(UC_ARM64_REG_X5),uc.reg_read(UC_ARM64_REG_X6),uc.reg_read(UC_ARM64_REG_X7),perm32);ret(uc)
   def hexp(uc,a,s,d): counts['exp_q16_postprocess']+=1;C.exp_q16_postprocess(uc,uc.reg_read(UC_ARM64_REG_X0));ret(uc)
   def hmap(uc,a,s,d): counts['map_correction_to_mesh']+=1;C.map_correction_to_mesh(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2));ret(uc)
   def hprep5(uc,a,s,d): counts['solver_prepare_layout']+=1;C.solver_prepare_layout(uc,uc.reg_read(UC_ARM64_REG_X0));ret(uc)
   def hgrad(uc,a,s,d): counts['periodic_forward_gradients']+=1;C.periodic_forward_gradients(uc,uc.reg_read(UC_ARM64_REG_X0)&0xffff,uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3));ret(uc)
   def hthresh(uc,a,s,d): counts['spectral_threshold_active']+=1;C.spectral_threshold_active(uc,uc.reg_read(UC_ARM64_REG_X0));ret(uc)
   def hproj(uc,a,s,d): counts['project_periodic_zero_mean']+=1;C.project_periodic_zero_mean(uc,uc.reg_read(UC_ARM64_REG_X0)&0xffffffff,uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3),uc.reg_read(UC_ARM64_REG_X4));ret(uc)
   def hdiv(uc,a,s,d): counts['periodic_divergence']+=1;C.periodic_divergence(uc,uc.reg_read(UC_ARM64_REG_X1)&0xffff,uc.reg_read(UC_ARM64_REG_X3),uc.reg_read(UC_ARM64_REG_X4),uc.reg_read(UC_ARM64_REG_X5));ret(uc)
   def hsolver(uc,a,s,d): counts['solver_orchestration']+=1;C.solver_orchestration(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2));ret(uc)
   def happly(uc,a,s,d): counts['solver_apply_box3x3']+=1;C.box3x3_preserve_two_cell_border(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2));ret(uc)
   def hfinal(uc,a,s,d): counts['final_application_mode2']+=1;rc=C.final_application_mode2(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X3));uc.reg_write(UC_ARM64_REG_X0,rc & 0xffffffffffffffff);ret(uc)
   def hcore(uc,a,s,d): counts['core_mode2']+=1;rc=C.core_mode2(uc,uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X3),uc.reg_read(UC_ARM64_REG_X4));uc.reg_write(UC_ARM64_REG_X0,rc & 0xffffffffffffffff);ret(uc)
   def hbic(uc,a,s,d):
    counts['bicubic_row_kernel']+=1
    rd=lambda reg: struct.unpack('<d',struct.pack('<Q',uc.reg_read(reg)&0xffffffffffffffff))[0]
    C.bicubic_row_kernel(uc,rd(UC_ARM64_REG_D0),rd(UC_ARM64_REG_D1),rd(UC_ARM64_REG_D2),rd(UC_ARM64_REG_D3),uc.reg_read(UC_ARM64_REG_X0),uc.reg_read(UC_ARM64_REG_X1),uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3),uc.reg_read(UC_ARM64_REG_X4),uc.reg_read(UC_ARM64_REG_X5)&0xffffffff,uc.reg_read(UC_ARM64_REG_X6)&0xffffffff);ret(uc)
   u.hook_add(UC_HOOK_CODE,hwrap,begin=B+0xC95FD0,end=B+0xC95FD0);u.hook_add(UC_HOOK_CODE,hifshim,begin=IFSHIM+4,end=IFSHIM+4);u.hook_add(UC_HOOK_CODE,htramp,begin=TRAMP,end=TRAMP);   u.hook_add(UC_HOOK_CODE,hcore,begin=B+0xCA01B0,end=B+0xCA01B0);u.hook_add(UC_HOOK_CODE,hfinal,begin=B+0xC9F568,end=B+0xC9F568);u.hook_add(UC_HOOK_CODE,hsolver,begin=B+0xC9A630,end=B+0xC9A630);u.hook_add(UC_HOOK_CODE,happly,begin=B+0xC9A9B8,end=B+0xC9A9B8);u.hook_add(UC_HOOK_CODE,hprep5,begin=B+0xC9A288,end=B+0xC9A288);u.hook_add(UC_HOOK_CODE,hgrad,begin=B+0xC98270,end=B+0xC98270);u.hook_add(UC_HOOK_CODE,hthresh,begin=B+0xC989D0,end=B+0xC989D0);u.hook_add(UC_HOOK_CODE,hproj,begin=B+0xC998B8,end=B+0xC998B8);u.hook_add(UC_HOOK_CODE,hdiv,begin=B+0xC99130,end=B+0xC99130);u.hook_add(UC_HOOK_CODE,hinterp,begin=B+0xC9E590,end=B+0xC9E590);u.hook_add(UC_HOOK_CODE,hexp,begin=B+0xC9ED88,end=B+0xC9ED88);u.hook_add(UC_HOOK_CODE,hmap,begin=B+0xC9C868,end=B+0xC9C868);u.hook_add(UC_HOOK_CODE,hfwd,begin=B+0xCA1FB0,end=B+0xCA1FB0);u.hook_add(UC_HOOK_CODE,hinv,begin=B+0xCA2310,end=B+0xCA2310);u.hook_add(UC_HOOK_CODE,hfft,begin=B+0xCA1D98,end=B+0xCA1D98);u.hook_add(UC_HOOK_CODE,htrans,begin=B+0xCA1ED0,end=B+0xCA1ED0);u.hook_add(UC_HOOK_CODE,hp,begin=B+0xC9F438,end=B+0xC9F438);u.hook_add(UC_HOOK_CODE,hs,begin=B+0xC9BB48,end=B+0xC9BB48);u.hook_add(UC_HOOK_CODE,ha,begin=B+0xC9F078,end=B+0xC9F078);u.hook_add(UC_HOOK_CODE,hl,begin=B+0xC9EBC8,end=B+0xC9EBC8);u.hook_add(UC_HOOK_CODE,hq,begin=B+0xC97F40,end=B+0xC97F40);u.hook_add(UC_HOOK_CODE,hpad,begin=B+0xC9C4B0,end=B+0xC9C4B0);u.hook_add(UC_HOOK_CODE,hbic,begin=B+0xC9E398,end=B+0xC9E398)
 surface.SurfaceEmu=Hybrid
 try: hy=H.run_sequence(cap,dll,proof,surface,pre,0,'zero')
 finally: surface.SurfaceEmu=Orig
 for r in (4,5,6):
  for k in ('output_abi','lsc0','lsc1','lsc2','gic'):
   if hy[r][k]!=base[r][k]:raise RuntimeError(f'R{r} substitution drift {k}')
  print(f'R{r} CLEANROOM_HELPERS PASS LSC0={H.sha(hy[r]["lsc0"])} LSC1={H.sha(hy[r]["lsc1"])}')
 if counts!={'preprocess_stats':0,'smooth_stats_map':0,'accumulate_float_fields':0,'ln_float_field':0,'quantize_float_field_q16':0,'pad_mesh_extrapolated':0,'bicubic_row_kernel':0,'interpolate_mesh_to_stats':0,'fft_radix2_inplace':0,'transpose_u32_matrix':0,'fft2d_forward_64x32':0,'fft2d_inverse_64x32':0,'exp_q16_postprocess':0,'map_correction_to_mesh':0,'solver_prepare_layout':0,'periodic_forward_gradients':0,'spectral_threshold_active':0,'project_periodic_zero_mean':0,'periodic_divergence':0,'solver_orchestration':0,'solver_apply_box3x3':0,'final_application_mode2':0,'core_mode2':0,'wrapper_front_mode2':3}:raise RuntimeError(f'hook count drift {counts}')
 print(json.dumps({'schema':'sp11-e003i-cleanroom-tintless-helper-substitution-v1','status':'PASS','substituted_rvas':['0xc9f438','0xc9bb48','0xc9f078','0xc9ebc8','0xc97f40','0xc9c4b0','0xc9e398','0xc9e590','0xca1d98','0xca1ed0','0xca1fb0','0xca2310','0xc9ed88','0xc9c868','0xc9a288','0xc98270','0xc989d0','0xc998b8','0xc99130','0xc9a630','0xc9a9b8','0xc9f568','0xca01b0','0xc95fd0'],'hook_counts':counts,'native_bodies_bypassed':True,'linux_camera_runtime':False},indent=2,sort_keys=True));print('CLEANROOM_TINTLESS_HELPER_SUBSTITUTION=PASS')
if __name__=='__main__':main()
