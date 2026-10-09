#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""SAME-SP11-only native NV12 decoding and scalar integrity screening."""
import argparse,json,os,stat
from pathlib import Path
import numpy as np
from PIL import Image
W,H=3840,2160
YBYTES=W*H;TOTAL=YBYTES*3//2
ROOT=Path("/var/lib/sp11-camera-native-rear-generation-20261007-53/private-optical")
def sealed(path,directory=False):
 s=path.lstat()
 if stat.S_ISLNK(s.st_mode) or s.st_uid!=0 or stat.S_IMODE(s.st_mode)!=(0o700 if directory else 0o600):
  raise RuntimeError("optical sealed ownership/mode")
 if not (stat.S_ISDIR(s.st_mode) if directory else stat.S_ISREG(s.st_mode)):
  raise RuntimeError("optical sealed file type")
def scalar(a):
 return dict(min=int(a.min()),max=int(a.max()),mean=float(a.mean()),
             std=float(a.std()),p01=float(np.percentile(a,1)),p50=float(np.percentile(a,50)),p99=float(np.percentile(a,99)))
def decode(y,u,v,matrix):
 yy=y.astype(np.float32);uu=np.repeat(np.repeat(u,2,axis=0),2,axis=1).astype(np.float32)-128
 vv=np.repeat(np.repeat(v,2,axis=0),2,axis=1).astype(np.float32)-128
 if matrix.endswith("limited"):
  yy=(yy-16)*(255/219);uu*=255/224;vv*=255/224
 if matrix.startswith("bt601"):
  rr=yy+1.402*vv;gg=yy-0.344136*uu-0.714136*vv;bb=yy+1.772*uu
 else:
  rr=yy+1.5748*vv;gg=yy-0.187324*uu-0.468124*vv;bb=yy+1.8556*uu
 return np.clip(np.stack([rr,gg,bb],axis=-1),0,255).astype(np.uint8)
def save_png(rgb,path):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,"wb") as f:
  Image.fromarray(rgb).save(f,format="PNG",compress_level=1);f.flush();os.fsync(f.fileno())
 sealed(path)
def analyze(directory,make_previews=True):
 sealed(directory,True)
 frames=[];previous=None
 for seq in [15,79,199]:
  path=directory/("frame-"+str(seq)+".nv12");sealed(path)
  if path.stat().st_size!=TOTAL:raise RuntimeError("optical exact NV12 file extent")
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
  with os.fdopen(fd,"rb") as f:raw=np.frombuffer(f.read(),dtype=np.uint8)
  if raw.size!=TOTAL:raise RuntimeError("optical short NV12 read")
  y=raw[:YBYTES].reshape(H,W);uv=raw[YBYTES:].reshape(H//2,W);u=uv[:,::2];v=uv[:,1::2]
  ys=scalar(y);us=scalar(u);vs=scalar(v)
  flags=[]
  if ys["max"]==ys["min"]:flags.append("constant_luma")
  if float((y<=16).mean())>0.995:flags.append("nearly_all_at_or_below_video_black")
  if float((y>=235).mean())>0.995:flags.append("nearly_all_at_or_above_video_white")
  if us["max"]==us["min"] and vs["max"]==vs["min"]:flags.append("constant_chroma")
  identical=previous is not None and bool(np.array_equal(previous,raw));previous=raw.copy()
  if identical:flags.append("identical_to_previous_selected_frame")
  previews={}
  for matrix in ["bt601-limited","bt709-limited","bt709-full"]:
   rgb=decode(y,u,v,matrix)
   previews[matrix]=dict(red_mean=float(rgb[:,:,0].mean()),green_mean=float(rgb[:,:,1].mean()),
                         blue_mean=float(rgb[:,:,2].mean()),all_channels_black_fraction=float((rgb.max(axis=2)==0).mean()),
                         any_channel_white_fraction=float((rgb.max(axis=2)==255).mean()))
   if make_previews:save_png(rgb,directory/("frame-"+str(seq)+"-"+matrix+"-unverified.png"))
  frames.append(dict(sequence=seq,nv12_bytes=TOTAL,Y=ys,U=us,V=vs,
    at_or_below_video_black_fraction=float((y<=16).mean()),at_or_above_video_white_fraction=float((y>=235).mean()),
    horizontal_adjacent_luma_difference_mean=float(np.abs(np.diff(y.astype(np.int16),axis=1)).mean()),
    vertical_adjacent_luma_difference_mean=float(np.abs(np.diff(y.astype(np.int16),axis=0)).mean()),
    diagnostic_flags=flags,preview_interpretations=previews))
 return dict(status="PRIVATE_NATIVE_NV12_CAPTURE_ANALYZED",native_frames=3,
   private_previews_saved=9 if make_previews else 0,frames=frames,
   degenerate_frame_count=sum(bool(x["diagnostic_flags"]) for x in frames),
   negotiated_color_space="unspecified",preview_matrices_are_unverified_hypotheses=True,
   visual_or_matched_Windows_parity_qualified=False,image_bytes_exported=False,
   photos_or_image_hashes_logged=False,pixel_arrays_returned=False)
def main():
 if __import__("sys").argv[1:]==["--identity-check"]:
  print(json.dumps(dict(status="PASS_PRIVATE_OPTICAL_ANALYZER_IDENTITY",candidate_identity=53,hardware_access=False)));return
 p=argparse.ArgumentParser();p.add_argument("--session",type=int,choices=[1,2,3],required=True);a=p.parse_args()
 if os.geteuid()!=0:raise RuntimeError("optical root analysis required")
 sealed(ROOT,True)
 result=analyze(ROOT/("session-"+str(a.session)))
 print(json.dumps(result,allow_nan=False))
if __name__=="__main__":main()
