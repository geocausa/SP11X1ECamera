#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Strict real sensor receipt and native AE scalar admission; no spatial data."""
import math,re,runpy,statistics
from pathlib import Path
integer_fields=runpy.run_path(str(Path(__file__).with_name("live-control-proof.py")))["fields"]
def need(ok,message):
 if not ok:raise RuntimeError(message)
def mixed(log,tag,keys):
 rows=[]
 for text in re.findall(re.escape(tag)+r" ([^\n]+)",log):
  pairs=[x.split("=",1) for x in text.split()]
  need(all(len(p)==2 for p in pairs) and len(pairs)==len(keys) and {p[0] for p in pairs}==set(keys),"AE scalar receipt field drift")
  row={}
  for k,v in pairs:
   if k=="meter":
    try:row[k]=float(v)
    except ValueError:raise RuntimeError("AE meter not numeric")
    need(math.isfinite(row[k]) and 0<=row[k]<=1000000,"AE meter outside admitted scalar range")
   else:
    need(re.fullmatch(r"[0-9]+",v),"AE scalar integer malformed")
    row[k]=int(v)
  rows.append(row)
 return rows
def validate(log,stderr,probe,session):
 need(type(session)==int and session==1,"one fresh AE session required")
 kernel=integer_fields(log,"NATIVE_REAR_LIVE_CONTROL",["id","value","reg","readback","before_ns","after_ns"])
 library=integer_fields(stderr,"NATIVE_REAR_LIBCAMERA_CONTROL",["id","value","last_completed_sequence","before_ns","after_ns","cached_readback","per_frame_association"])
 need(len(library)>=3 and len(kernel)==len(library)-2,"real AE controls and initial seed receipts required")
 need({(r["id"],r["value"]) for r in library[:2]}=={(0x00980911,1600),(0x009e0903,128)},"AE initial controls drift")
 frames=mixed(stderr,"NATIVE_REAR_AE_FRAME",["sequence","stream","owner","generation","timestamp","meter","target","lines","gain","update","limited"])
 need(400<=len(frames)<=416 and [r["sequence"] for r in frames]==list(range(len(frames))),"contiguous real AE statistics receipts required")
 prev_time=0;stream=frames[0]["stream"]
 need(0<stream<2**64,"AE stream identity range")
 updates=[];expected_controls=[];lines=1600;gain=128;previous_pair=(lines,gain);last_update=-8
 for f in frames:
  need(f["stream"]==stream and f["owner"]==1 and f["generation"]==f["sequence"]+1 and f["timestamp"]>prev_time,"AE owner/generation/timestamp drift")
  need(f["target"]==12000 and 4<=f["lines"]<=3206 and 128<=f["gain"]<=2048 and f["update"] in (0,1) and f["limited"] in (0,1),"AE proposal outside bounded engineering policy")
  prev_time=f["timestamp"]
  if f["update"]:
   need(f["sequence"]>=8 and f["sequence"]-last_update>=8 and not f["limited"] and (f["lines"],f["gain"])!=(lines,gain),"AE proposal before settling or without changed controls")
   if f["lines"]!=lines:expected_controls.append((f["sequence"],0x00980911,f["lines"]))
   if f["gain"]!=gain:expected_controls.append((f["sequence"],0x009e0903,f["gain"]))
   previous_pair=(lines,gain);lines,gain=f["lines"],f["gain"];last_update=f["sequence"];updates.append(f)
  else:
   need((f["lines"],f["gain"])==(lines,gain) or (f["sequence"]-last_update<8 and (f["lines"],f["gain"])==previous_pair),"foreign AE state outside bounded IPC acknowledgement interval")
 need(updates and len(expected_controls)==len(kernel),"actual AE writes must match proposals exactly")
 receipts=[]
 for k,l,(sequence,cid,value) in zip(kernel,library[2:],expected_controls):
  reg=0x3500 if cid==0x00980911 else 0x3508;readback=value<<4 if reg==0x3500 else value
  need((k["id"],k["value"],k["reg"],k["readback"])==(cid,value,reg,readback) and (l["id"],l["value"])==(cid,value),"AE actual sensor register readback mismatch")
  need(0<l["before_ns"]<=k["before_ns"]<=k["after_ns"]<=l["after_ns"] and sequence-2<=l["last_completed_sequence"]<=sequence and l["cached_readback"]==1 and l["per_frame_association"]==0,"AE sensor receipt clock/order or unproven optical association")
  receipts.append(dict(proposal_sequence=sequence,control_id=cid,value=value,actual_register_readback=k["readback"],actual_read_begin_ns=k["before_ns"],actual_read_end_ns=k["after_ns"]))
 summary=integer_fields(stderr,"NATIVE_REAR_AE_SUMMARY",["decoded","updates","enabled","target","max_gain","settle","engineering_target","quality_calibrated"])
 need(len(summary)==1,"one AE stop summary required")
 need(summary[0]==dict(decoded=len(frames),updates=len(updates),enabled=1,target=12000,max_gain=2048,settle=8,engineering_target=1,quality_calibrated=0),"AE stop summary drift")
 samples=probe.get("AE_control_timing_samples")
 expected=[n for begin in [56,120,184,248] for n in range(begin,begin+24)]
 need(type(samples)==list and len(samples)==96 and [r.get("sequence") for r in samples]==expected,"96 chronological AE global luma samples required")
 need(probe.get("live_control_changes")==0 and probe.get("automatic_exposure_implemented") is True and probe.get("diagnostic_full_Y_bytes_read")==796262400,"AE capture scope drift")
 for row in samples:
  need(set(row)=={"sequence","driver_completion_ns","Y_mean"} and type(row["sequence"])==int and type(row["driver_completion_ns"])==int and 0<=frames[row["sequence"]]["timestamp"]-row["driver_completion_ns"]<1000 and type(row["Y_mean"]) in (int,float) and math.isfinite(row["Y_mean"]) and 0<=row["Y_mean"]<=255,"AE image/statistics completion pairing or luma invalid")
 settled=frames[320:400]
 converged=all(10800<=f["meter"]<=13200 and not f["limited"] for f in settled)
 return dict(status="PASS_REAL_NATIVE_AE_PROPOSALS_AND_SENSOR_READBACKS",enabled=True,decoded_frames=len(frames),updates=len(updates),actual_sensor_register_reads=True,receipts=receipts,whole_frame_meter_series=frames,global_luma_samples=samples,engineering_target=12000,last80_meter_median=statistics.median(f["meter"] for f in settled),last80_within_ten_percent=converged,limited_frames=sum(f["limited"] for f in frames),initial8_meter_median=statistics.median(f["meter"] for f in frames[:8]),final_lines=lines,final_gain=gain,settled_global_Y_median=statistics.median(r["Y_mean"] for r in samples[-24:]),quality_calibrated=False,Windows_quality_parity_proven=False,exact_optical_frame_control_association_proven=False,spatial_statistics_exported=False)
