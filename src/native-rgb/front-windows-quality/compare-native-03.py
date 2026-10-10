
#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Same-SP11 only native NV12 comparison; stdout contains global scalar facts."""
from pathlib import Path
import argparse,json,os,stat,subprocess,datetime,re
import numpy as np
from scipy.ndimage import gaussian_filter
WROOT=Path("/run/sp11-windows-frontquality03-ro/Users/Geoca/Documents/SP11-Camera-WindowsFrontQuality-20261010-03")
LROOT=Path("/var/lib/sp11-camera-native-front-meter-20261010-02")
PREVIEW=Path("/home/geoca/Pictures/SP11-Camera-Private-Windows01-Linux55")
WIDTH=2560;HEIGHT=1440;EXTENT=5529600
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
 if len(mount)!=2 or mount[0]!="/run/sp11-windows-frontquality03-ro" or "ro" not in mount[1].split(","):raise RuntimeError("Windows originals must be read only")
 seal(Path("/run/sp11-windows-frontquality03-ro"),True);seal(WROOT,True);seal(LROOT,True)
 w=json.loads((WROOT/"RESULT.json").read_text(encoding="utf-8-sig"));l=json.loads((LROOT/"RESULT.json").read_text())
 wr=json.loads((WROOT/"RETIREMENT.json").read_text(encoding="utf-8-sig"))
 lr=json.loads((LROOT/"RETIREMENT.json").read_text())
 if w["identity"]!="E-WINDOWS-FRONT-QUALITY-20261010-03" or w["status"]!="PASS_WINDOWS_FRONT_NATIVE_NV12_PRIVATE_CAPTURE" or w["private_native_frames_saved"]!=3 or not w["clean_stop_release"] or not wr["task_unregistered"]:raise RuntimeError("retired Windows capture required")
 if l["identity"]!="E-NATIVE-FRONT-METER-20261010-02" or l["status"]!="FAILED_NATIVE_NV12_PROBE" or not lr["retired"] or not lr["do_not_retry"]:raise RuntimeError("exact retired failed native capture required")
 partial=json.loads((LROOT/"PARTIAL-OPTICAL-SCALARS.json").read_text())
 if partial["status"]!="PARTIAL_FAILED_RUN_NOT_FULL_CONTROL_QUALIFICATION" or partial["missing_requests"]!=[96,128]:raise RuntimeError("exact partial capture disposition required")
 log=(LROOT/"PRIVATE-CAM-STDERR.txt").read_text()
 applied={int(r):(int(seq),[int(fll),int(exp),int(again),int(dgain)]) for r,seq,fll,exp,again,dgain in re.findall(r"CAMSS_X1E_APPLIED_CONTROL request=(\d+) frame=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+)",log)}
 ws={}
 for n in [1,4,7]:
  y,uv=load_native(WROOT/("frame-"+str(n)+".nv12"));f=facts(y,uv);original=next(x for x in w["samples"] if x["sequence"]==n)
  for channel in ["Y","U","V"]:
   for key,value in f[channel].items():
    if abs(value-original[channel][key])>1e-6:raise RuntimeError("original Windows metrics mismatch")
  ws[n]=(y,uv)
 wy,wuv=ws[4];grid=wy[::8,::8].astype(np.float32);comparisons=[]
 for index,request in enumerate([24,56,88,120,152]):
  original=next(x for x in partial["samples"] if x["request"]==request)
  sequence=original["sequence"]
  if request not in applied or applied[request][0]!=sequence:raise RuntimeError("actual applied metadata identity required")
  matches=list(LROOT.glob("frame-*-"+str(sequence).zfill(6)+".bin"))
  if len(matches)!=1:raise RuntimeError("one exact private Linux frame required: "+str(sequence))
  y,uv=load_native(matches[0]);f=facts(y,uv)
  
  if abs(f["Y"]["mean"]-original["Y_mean"])>1e-6:raise RuntimeError("original Linux metrics mismatch")
  comparisons.append(dict(plateau=index,application_request=request,frame_sequence=sequence,
   manual_controls=applied[request][1],global_metrics=f,
   scene_registration=alignment(grid,y[::8,::8]),normalized_or_brightness_scaled_pixels=False))
 report=dict(identity="E-WINDOWS-FRONT03-LINUX-METER02-PARTIAL-COMPARISON",
  status="PASS_PRIVATE_PARTIAL_FRONT_COMPARISON_SCALARS_ONLY",Windows_identity=w["identity"],Linux_identity=l["identity"],
  Windows_capture_utc=w["captured_utc"],Linux_capture_utc=l["capture_started_utc"],
  seconds_between_capture_starts=(datetime.datetime.fromisoformat(w["samples"][0]["captured_utc"])-datetime.datetime.fromisoformat(l["capture_started_utc"])).total_seconds(),
  Windows_scalar_samples=w["samples"],Windows_nominal_controls=w["controls"],
  Windows_nominal_controls_not_sensor_readback=True,Windows_retirement=wr,Linux_retirement=lr,
  native_originals_reproduce_saved_metrics=True,comparison=comparisons,
  Windows_repeat=[alignment(ws[i][0][::8,::8],ws[j][0][::8,::8]) for i,j in [(1,4),(4,7)]],
  same_SP11_only=True,Windows_originals_read_only=True,
  Linux_run_failed=True,Linux_full_manual_bracket_qualified=False,Linux_gain_changes_cancelled=True,
  pixels_spatial_arrays_or_image_hashes_exported=False,cross_boot_scene_illumination_stability_verified=False,
  matching_exposure_gain_verified=False,color_range_matrix_transfer_verified=False,
  ambient_day_night_or_covered_lens_classification_proven=False,Windows_image_quality_parity=False,
  photometrically_calibrated_AE_target=False,coarse_correlation_is_not_SNR_detail_or_optical_parity=True)
 fd=os.open(args.report,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:os.write(fd,(json.dumps(report,indent=2)+"\n").encode());os.fsync(fd)
 finally:os.close(fd)
 print(json.dumps(dict(status=report["status"],Windows_Y_mean_range=[min(x["Y"]["mean"] for x in w["samples"]),max(x["Y"]["mean"] for x in w["samples"])],
  Linux=[dict(plateau=x["plateau"],Y_mean=x["global_metrics"]["Y"]["mean"],coarse_correlation=x["scene_registration"]["coarse_correlation"]) for x in comparisons],
  private_pixels_stayed_SP11=True,quality_parity=False)))
if __name__=="__main__":main()
