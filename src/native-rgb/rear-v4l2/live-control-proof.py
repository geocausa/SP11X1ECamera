#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Strict live control receipt and global per-frame scalar timing admission."""
import math,re,statistics
def fields(log,tag,keys):
 rows=[]
 for text in re.findall(re.escape(tag)+r" ([^\n]+)",log):
  parts=text.split();pairs=[p.split("=",1) for p in parts]
  if len(pairs)!=len(keys) or {p[0] for p in pairs}!=set(keys) or any(len(p)!=2 or not re.fullmatch(r"-?\d+",p[1]) for p in pairs):
   raise RuntimeError("malformed live control scalar receipt")
  rows.append({k:int(v) for k,v in pairs})
 return rows
def validate(log,stderr,probe,session):
 if type(session)!=int or session not in (1,2,3):raise RuntimeError("exact session required")
 initial=3206 if session==2 else 1600
 gain=1024 if session==2 else 128
 plan=[(64,0x00980911,1600 if initial==3206 else 3206),(128,0x00980911,initial),(192,0x009e0903,128 if gain==1024 else 1024),(256,0x009e0903,gain)]
 kernel=fields(log,"NATIVE_REAR_LIVE_CONTROL",["id","value","reg","readback","before_ns","after_ns"])
 library=fields(stderr,"NATIVE_REAR_LIBCAMERA_CONTROL",["id","value","last_completed_sequence","before_ns","after_ns","cached_readback","per_frame_association"])
 if len(kernel)!=4 or len(library)!=6:raise RuntimeError("four sensor and six libcamera receipts required")
 if {(r["id"],r["value"]) for r in library[:2]}!={(0x00980911,initial),(0x009e0903,gain)}:raise RuntimeError("start controls differ from session plan")
 samples=probe.get("manual_control_timing_samples")
 expected=[n for begin in [56,120,184,248] for n in range(begin,begin+24)]
 if type(samples)!=list or len(samples)!=96 or [r.get("sequence") for r in samples]!=expected:raise RuntimeError("96 exact chronological global luma samples required")
 if probe.get("live_control_changes")!=4 or probe.get("automatic_exposure_implemented") is not False or probe.get("diagnostic_full_Y_bytes_read")!=796262400:raise RuntimeError("diagnostic scope differs")
 prev=0
 for row in samples:
  if set(row)!={"sequence","driver_completion_ns","Y_mean"} or type(row["sequence"])!=int or type(row["driver_completion_ns"])!=int or row["driver_completion_ns"]<=prev or isinstance(row["Y_mean"],bool) or not isinstance(row["Y_mean"],(int,float)) or not math.isfinite(row["Y_mean"]) or not 0<=row["Y_mean"]<=255:
   raise RuntimeError("invalid global timing sample")
  prev=row["driver_completion_ns"]
 responses=[]
 for index,(trigger,cid,value) in enumerate(plan):
  k=kernel[index];l=library[index+2]
  reg=0x3500 if cid==0x00980911 else 0x3508
  expected_reg=value<<4 if cid==0x00980911 else value
  if (k["id"],k["value"],k["reg"],k["readback"])!=(cid,value,reg,expected_reg) or (l["id"],l["value"])!=(cid,value):raise RuntimeError("actual live sensor register/control mismatch")
  if not (0<l["before_ns"]<=k["before_ns"]<=k["after_ns"]<=l["after_ns"]) or not trigger-1<=l["last_completed_sequence"]<=trigger+2 or l["cached_readback"]!=1 or l["per_frame_association"]!=0:raise RuntimeError("receipt clocks/order or association claim invalid")
  segment=samples[index*24:(index+1)*24]
  before=statistics.median(r["Y_mean"] for r in segment[:8])
  after=statistics.median(r["Y_mean"] for r in segment[-8:])
  delta=after-before;threshold=max(2.0,abs(before)*0.1);first=None
  for j in range(8,22):
   if all(abs(segment[x]["Y_mean"]-before)>threshold and (segment[x]["Y_mean"]-before)*delta>0 for x in range(j,j+3)):
    first=segment[j]["sequence"];break
  responses.append(dict(trigger_completed_count=trigger,control_id=cid,value=value,actual_register_readback=k["readback"],last_completed_sequence_at_apply=l["last_completed_sequence"],sensor_read_begin_ns=k["before_ns"],sensor_read_end_ns=k["after_ns"],libcamera_set_begin_ns=l["before_ns"],libcamera_set_end_ns=l["after_ns"],baseline_Y_median=before,settled_Y_median=after,code_space_Y_ratio=after/before if before else None,first_three_frame_consistent_response_sequence=first,response_sequence_minus_trigger=first-trigger if first is not None else None,threshold_code_space_Y=threshold,scene_lighting_stability_proven=False,exact_frame_control_metadata_association_proven=False))
 return dict(status="PASS_REAL_LIBCAMERA_LIVE_SENSOR_CONTROL_RECEIPTS_AND_GLOBAL_RESPONSE_TIMING",changes=responses,samples=samples,automatic_exposure_implemented=False,group_hold_or_atomic_pair_claimed=False,actual_sensor_register_reads=True,hardware_SOF_timestamp_available=False)
