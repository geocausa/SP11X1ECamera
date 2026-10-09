#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Private retired57 AEC field validation; only global scalar facts may leave."""
from pathlib import Path
import os,stat,struct,ctypes,json,tempfile,subprocess,re,statistics
HERE=Path(__file__).resolve().parent
ROOT=Path("/var/lib/sp11-camera-native-rear-generation-20261007-57")
SIZES=[0xa0000,0x1800,0x48000,0x151800,0x2d00,0x10000]
SELECTED={begin+offset for begin in [56,120,184,248] for offset in [0,7,10,11,12,23]}
def need(v,m):
 if not v:raise RuntimeError(m)
def main():
 os.umask(0o077);need(os.geteuid()==0,"root needed for sealed private statistics")
 need("sp11_entry=7.1.5-sp11-fullio-v19c" in Path("/proc/cmdline").read_text().split(),"analysis on restored Golden")
 ret=json.loads((ROOT/"RETIREMENT.json").read_text());need(ret["retired"] and ret["do_not_retry"],"retired source required")
 folder=ROOT/"private-statistics/session-1";need(stat.S_IMODE(folder.stat().st_mode)==0o700,"private folder mode")
 paths=list(folder.glob("*.qxr1"));need(len(paths)==24,"24 private statistics records")
 rows=[]
 with tempfile.TemporaryDirectory(prefix="rear57-private-aec-") as td:
  td=Path(td);source=td/"wrapper.cpp";binary=td/"decoder.so"
  source.write_text('#include "rear-aec-statistics.h"\nextern "C" int scalar(const uint8_t *p,size_t n,double *out){RearAec::Meter m;int r=RearAec::decodeNormal(p,n,&m);if(r)return r;out[0]=m.r;out[1]=m.gr;out[2]=m.gb;out[3]=m.b;return 0;}\n')
  subprocess.run(["g++","-std=c++17","-Wall","-Wextra","-Werror","-O2","-fPIC","-shared","-I"+str(HERE),source,"-o",binary],check=True,capture_output=True,text=True)
  lib=ctypes.CDLL(str(binary));lib.scalar.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_double)];lib.scalar.restype=ctypes.c_int
  stream=owner=None
  for p in paths:
   s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600,"private regular sealed file")
   data=p.read_bytes();need(len(data)==96+sum(SIZES),"exact protocol bytes")
   magic,version,h=struct.unpack_from("<IHH",data)
   si,ts,ow,gen=struct.unpack_from("<QQQQ",data,8);seq,cursor=struct.unpack_from("<II",data,40)
   dropped,=struct.unpack_from("<Q",data,48);flags,=struct.unpack_from("<I",data,56)
   sizes=list(struct.unpack_from("<6I",data,60));mask,=struct.unpack_from("<I",data,84);reserved,=struct.unpack_from("<Q",data,88)
   need(magic==0x31525851 and version==1 and h==96 and si and ts and ow==1 and gen==seq+1 and cursor and dropped==0 and flags==1 and sizes==SIZES and mask==sum(1<<i for i in [11,12,13,14,16,18]) and reserved==0,"native packet identity")
   need(p.name=="statistics-"+str(seq)+".qxr1" and seq in SELECTED,"exact private file ordinal")
   if stream is None:stream,owner=si,ow
   need(si==stream and ow==owner,"one stream/owner")
   raw=ctypes.create_string_buffer(data[96:96+SIZES[0]]);values=(ctypes.c_double*4)()
   need(lib.scalar(raw,SIZES[0],values)==0,"actual normal AEC decoder admission")
   r,gr,gb,b=values
   rows.append(dict(sequence=seq,driver_completion_ns=ts,R_mean=r,Gr_mean=gr,Gb_mean=gb,B_mean=b,
    raw_weighted_mean=0.299*r+0.587*(gr+gb)/2+0.114*b,geometry_samples_per_channel=2205))
 rows.sort(key=lambda r:r["sequence"]);need({r["sequence"] for r in rows}==SELECTED,"all selected ordinals")
 need(all(b["driver_completion_ns"]>a["driver_completion_ns"] for a,b in zip(rows,rows[1:])),"monotonic actual timestamps")
 byseq={r["sequence"]:r for r in rows}
 changes=[]
 for begin,kind,expected in [(56,"exposure_increase",1),(120,"exposure_restore",-1),(184,"gain_increase",1),(248,"gain_restore",-1)]:
  before=statistics.median(byseq[begin+i]["raw_weighted_mean"] for i in [0,7])
  after=statistics.median(byseq[begin+i]["raw_weighted_mean"] for i in [10,11,12,23])
  need(after>before*1.2 if expected==1 else after<before*0.8,"scheduled sensor control direction in raw meter")
  changes.append(dict(control=kind,baseline_raw_weighted_mean=before,settled_raw_weighted_mean=after,ratio=after/before,
   first_sample_after_trigger_sequence=begin+10,earliest_response_proven=False,scene_lighting_stability_proven=False))
 proof=dict(status="PASS_REAR57_PRIVATE_NORMAL_AEC_FIELD_GEOMETRY_AND_CONTROL_DIRECTION",identity=ret["identity"],
  packets=24,validated_channel_records=24*1024*4,grid_h=32,grid_v=32,region_width=126,region_height=70,
  samples_per_channel=2205,record_stride_bytes=80,active_prefix_bytes=81920,allocated_capacity_bytes=SIZES[0],
  decoder_source="src/native-rgb/rear-libcamera/rear-aec-statistics.h",four_control_directions_checked=True,
  changes=changes,global_temporal_scalars=rows,spatial_arrays_exported=False,statistics_bytes_or_hashes_exported=False,
  raw_bit_depth_and_full_scale_qualified=False,black_offset_and_weight_calibration_qualified=False,
  clipping_and_saturation_decode_qualified=False,same_optical_exposure_provenance=False,
  clean_full_capture_pass=False,automatic_exposure=False,quality_parity=False)
 out=ROOT/"PRIVATE-AEC-FORMAT-01.json";need(not out.exists(),"fresh immutable private proof required")
 out.write_text(json.dumps(proof,indent=2)+"\n")
 print(json.dumps(proof))
if __name__=="__main__":main()
