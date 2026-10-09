
#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Same-SP11 only native NV12 comparison; stdout contains global scalar facts."""
from pathlib import Path
import argparse,json,os,stat,subprocess,datetime
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image,ImageDraw
WROOT=Path("/run/sp11-windows-quality01-ro/Users/Geoca/Documents/SP11-Camera-WindowsQuality-20261009-01")
LROOT=Path("/var/lib/sp11-camera-native-rear-generation-20261007-55")
PREVIEW=Path("/home/geoca/Pictures/SP11-Camera-Private-Windows01-Linux55")
WIDTH=3840;HEIGHT=2160;EXTENT=12441600
def seal(p,directory=False):
 s=p.lstat()
 if p.is_symlink() or s.st_uid!=0 or stat.S_IMODE(s.st_mode)!=(0o700 if directory else 0o600):raise RuntimeError("original private mode mismatch")
 if directory and not p.is_dir():raise RuntimeError("private directory required")
 if not directory and not p.is_file():raise RuntimeError("private original regular file required")
def load_native(p):
 seal(p)
 if p.stat().st_size!=EXTENT:raise RuntimeError("exact original NV12 extent required")
 d=np.fromfile(p,dtype=np.uint8)
 return d[:WIDTH*HEIGHT].reshape(HEIGHT,WIDTH),d[WIDTH*HEIGHT:].reshape(HEIGHT//2,WIDTH//2,2)
def facts(y,uv):
 def scalar(a):
  return dict(min=int(a.min()),max=int(a.max()),mean=float(a.mean()),std=float(a.std()),p01=float(np.percentile(a,1,method="lower")),p50=float(np.percentile(a,50,method="lower")),p99=float(np.percentile(a,99,method="lower")))
 return dict(Y=scalar(y),U=scalar(uv[:,:,0]),V=scalar(uv[:,:,1]),at_or_below_video_black_fraction=float((y<=16).mean()),at_or_above_video_white_fraction=float((y>=235).mean()),horizontal_adjacent_luma_difference_mean=float(np.abs(np.diff(y.astype(np.int16),axis=1)).mean()),vertical_adjacent_luma_difference_mean=float(np.abs(np.diff(y.astype(np.int16),axis=0)).mean()))
def corr(a,b):
 if a.shape!=b.shape or a.ndim!=2:raise ValueError("matching luma grids required")
 x=a.astype(np.float64).ravel();z=b.astype(np.float64).ravel();x-=x.mean();z-=z.mean()
 den=np.linalg.norm(x)*np.linalg.norm(z)
 return None if den<1e-9 else float(x@z/den)
def orient(a,name):
 return {"original":lambda:a,"horizontal_flip":lambda:np.fliplr(a),"vertical_flip":lambda:np.flipud(a),"rotate_180":lambda:a[::-1,::-1]}[name]()
def common(a,b,dy,dx,margin=24):
 h,w=a.shape
 return a[margin:h-margin,margin:w-margin],b[margin+dy:h-margin+dy,margin+dx:w-margin+dx]
def alignment(reference,test):
 if reference.shape!=test.shape or reference.ndim!=2 or min(reference.shape)<60:raise ValueError("large equal native-derived grids required")
 a=gaussian_filter(reference.astype(np.float32),2);rows=[]
 for name in ["original","horizontal_flip","vertical_flip","rotate_180"]:
  b=gaussian_filter(orient(test,name).astype(np.float32),2)
  ac=a[::4,::4];bc=b[::4,::4];h,w=ac.shape;m=8
  for dy in range(-5,6):
   for dx in range(-5,6):
    c=corr(ac[m:h-m,m:w-m],bc[m+dy:h-m+dy,m+dx:w-m+dx])
    if c is not None:rows.append((c,name,dy*4,dx*4))
 if not rows:return dict(coarse_correlation=None,fine_residual_correlation=None,orientation=None,shift_grid_y=None,shift_grid_x=None,consistent_coarse_scene_geometry=False)
 _,name,cy,cx=max(rows)
 b=gaussian_filter(orient(test,name).astype(np.float32),2);refined=[]
 for dy in range(max(-20,cy-3),min(20,cy+3)+1):
  for dx in range(max(-20,cx-3),min(20,cx+3)+1):
   aa,bb=common(a,b,dy,dx);c=corr(aa,bb)
   if c is not None:refined.append((c,dy,dx))
 c,dy,dx=max(refined)
 aa,bb=common(reference.astype(np.float32),orient(test,name).astype(np.float32),dy,dx)
 ah=aa-gaussian_filter(aa,2);bh=bb-gaussian_filter(bb,2)
 return dict(coarse_correlation=c,fine_residual_correlation=corr(ah,bh),orientation=name,shift_grid_y=dy,shift_grid_x=dx,grid_width=reference.shape[1],grid_height=reference.shape[0],sample_stride_native_pixels=8,max_translation_native_pixels=160,consistent_coarse_scene_geometry=c>=0.95,fine_residual_is_not_resolution_or_noise_parity=True)
def selftest():
 a=np.zeros((270,480),dtype=np.float32);a[60:130,90:210]=100;a[140:220,270:390]=220
 r=alignment(a,np.roll(a,(2,-1),(0,1)))
 assert r["coarse_correlation"]>0.99
 assert alignment(a,np.fliplr(a))["coarse_correlation"]>0.99
 assert corr(a,a)>0.999999
 assert corr(np.ones_like(a),np.ones_like(a)) is None
 for v in [np.zeros((2,2)),np.zeros((269,480))]:
  try:alignment(a,v)
  except ValueError:pass
  else:raise AssertionError("bad geometry admitted")
 print(json.dumps(dict(status="PASS_PRIVATE_NATIVE_COMPARISON_SYNTHETIC_GEOMETRY_AND_ALIGNMENT",hardware_access=False,optical_files_read=False,assertions=6)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--selftest",action="store_true");ap.add_argument("--report",type=Path);args=ap.parse_args()
 if args.selftest:selftest();return
 if os.geteuid()!=0 or args.report is None or args.report.exists():raise RuntimeError("root and new scalar report required")
 mount=subprocess.check_output(["findmnt","-rn","-T",str(WROOT),"-o","TARGET,OPTIONS"],text=True).split()
 if len(mount)!=2 or mount[0]!="/run/sp11-windows-quality01-ro" or "ro" not in mount[1].split(","):raise RuntimeError("same SP11 Windows mount must be read only")
 seal(Path("/run/sp11-windows-quality01-ro"),True);seal(WROOT,True);seal(LROOT,True)
 w=json.loads((WROOT/"RESULT.json").read_text(encoding="utf-8-sig"));l=json.loads((LROOT/"RESULT.json").read_text())
 if w["identity"]!="E-WINDOWS-REAR-QUALITY-20261009-01" or w["status"]!="PASS_WINDOWS_REAR_NATIVE_NV12_PRIVATE_CAPTURE" or w["private_native_frames_saved"]!=3 or not w["clean_stop_release"]:raise RuntimeError("Windows actual private capture proof required")
 if l["identity"]!="E-NATIVE-REAR-GENERATION-55" or l["status"]!="PASS_REAR_THREE_SAME_BOOT_LIBCAMERA_SESSIONS_AND_CLEAN_RELEASE" or len(l["sessions"])!=3 or l["completed_application_requests"]!=1200:raise RuntimeError("Linux actual three-session capture proof required")
 if not (LROOT/"RETIREMENT.json").exists():raise RuntimeError("Linux candidate must be retired first")
 ws={}
 for n in [1,4,7]:
  y,uv=load_native(WROOT/("frame-"+str(n)+".nv12"));f=facts(y,uv);original=next(x for x in w["samples"] if x["sequence"]==n)
  for channel in ["Y","U","V"]:
   for key,value in f[channel].items():
    if abs(value-original[channel][key])>1e-6:raise RuntimeError("Windows original metrics do not match saved native bytes")
  ws[n]=(y,uv)
 wy,wuv=ws[4];grid=wy[::8,::8].astype(np.float32);windows_mean=float(wy.mean());comparisons=[];panels=[("Windows automatic, native Y",wy[::4,::4])]
 for session,s in enumerate(l["sessions"],1):
  directory=LROOT/"private-optical"/("session-"+str(session));seal(directory,True)
  frames=[]
  for n in [15,79,199]:
   path=directory/("frame-"+str(n)+".nv12");y,uv=load_native(path);f=facts(y,uv)
   match=alignment(grid,y[::8,::8]);written=datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc)
   delta=(written-datetime.datetime.fromisoformat(w["samples"][4]["captured_utc"])).total_seconds()
   frames.append(dict(sequence=n,global_native_metrics=f,ratio_native_Y_mean_to_Windows_reference=f["Y"]["mean"]/windows_mean,scene_registration=match,seconds_after_Windows_sample_using_Linux_file_write_time=delta,Linux_file_write_time_is_not_frame_timestamp=True))
   if n==79:panels.append(("Linux session "+str(session)+", native Y",y[::4,::4]))
  comparisons.append(dict(session=session,controls=s["sensor_controls_readback"],frames=frames))
 windows_repeat=[dict(pair=[i,j],match=alignment(ws[i][0][::8,::8],ws[j][0][::8,::8])) for i,j in [(1,4),(4,7)]]
 if PREVIEW.exists():raise RuntimeError("new private viewing directory required")
 PREVIEW.mkdir(mode=0o700);os.chown(PREVIEW,1000,1000)
 canvas=Image.new("RGB",(1920,1140),(24,24,24));draw=ImageDraw.Draw(canvas)
 for i,(label,y) in enumerate(panels):
  x=(i%2)*960;top=(i//2)*570
  draw.text((x+8,top+6),label+"; unscaled Y 0-255",(255,255,255))
  canvas.paste(Image.fromarray(y).convert("RGB"),(x,top+30))
 pp=PREVIEW/"PRIVATE-WINDOWS01-LINUX55-NATIVE-Y-COMPARISON.png"
 with pp.open("xb") as f:canvas.save(f,format="PNG")
 os.chmod(pp,0o600);os.chown(pp,1000,1000)
 result=dict(identity="E-WINDOWS01-LINUX55-PRIVATE-COMPARISON",status="PASS_LOCAL_NATIVE_COMPARISON_SCALARS_ONLY",Windows_identity=w["identity"],Linux_identity=l["identity"],Windows_native_original_saved_frames=3,Linux_native_original_saved_frames=9,Windows_saved_native_bytes_reproduce_original_full_frame_metrics=True,Windows_native_scalar_samples=w["samples"],Windows_nominal_controls=w["controls"],Windows_nominal_controls_not_physical_sensor_readbacks=True,Windows_WB_auto_null_not_proven=True,Windows_capture_utc=w["captured_utc"],Windows_scene_temporal_correlations=windows_repeat,Linux_vs_Windows=comparisons,read_only_Windows_originals=True,same_SP11_only=True,pixel_arrays_or_photos_or_hashes_exported=False,private_native_Y_side_by_side_created=True,private_Y_viewing_not_color_parity=True,color_space_and_transfer_functions_unspecified=True,exact_cross_boot_lighting_or_content_stability_proven=False,ambient_lux_or_day_night_classification_proven=False,true_SNR_focus_color_or_visual_parity_proven=False,source_policy_unchanged_from54=True)
 args.report.write_text(json.dumps(result,indent=2)+"\n");os.chmod(args.report,0o600)
 print(json.dumps(dict(status=result["status"],private_images_stayed_on_SP11=True,Windows_Y_mean_range=[min(x["Y"]["mean"] for x in w["samples"]),max(x["Y"]["mean"] for x in w["samples"])],Linux_sessions=[dict(session=s["session"],Y_means=[f["global_native_metrics"]["Y"]["mean"] for f in s["frames"]],coarse_correlations=[f["scene_registration"]["coarse_correlation"] for f in s["frames"]],orientations=[f["scene_registration"]["orientation"] for f in s["frames"]]) for s in comparisons])))
if __name__=="__main__":main()
