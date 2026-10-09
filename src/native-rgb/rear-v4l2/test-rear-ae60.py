#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Offline real AE receipt parser fault admission and exact one400 runner scope."""
import copy,json,runpy
from pathlib import Path
P=Path(__file__).resolve().parent
validate=runpy.run_path(str(P/"ae-control-proof.py"))["validate"]
def render(tag,rows):return "\n".join(tag+" "+" ".join(str(k)+"="+str(v) for k,v in r.items()) for r in rows)
def main():
 frames=[]
 for n in range(400):
  lines=1600 if n<8 else 3200
  frames.append(dict(sequence=n,stream=88,owner=1,generation=n+1,timestamp=(n+1)*66666667,meter=6000 if n<11 else 12000,target=12000,lines=lines,gain=128,update=int(n==8),limited=0))
 kernel=[dict(id=0x00980911,value=3200,reg=0x3500,readback=3200<<4,before_ns=602,after_ns=603)]
 library=[dict(id=cid,value=v,last_completed_sequence=-1,before_ns=1,after_ns=2,cached_readback=1,per_frame_association=0) for cid,v in [(0x00980911,1600),(0x009e0903,128)]]
 library.append(dict(id=0x00980911,value=3200,last_completed_sequence=7,before_ns=601,after_ns=604,cached_readback=1,per_frame_association=0))
 summary=[dict(decoded=400,updates=1,enabled=1,target=12000,max_gain=2048,settle=8,engineering_target=1,quality_calibrated=0)]
 probe=dict(AE_control_timing_samples=[dict(sequence=n,driver_completion_ns=frames[n]["timestamp"]//1000*1000,Y_mean=42.0) for begin in [56,120,184,248] for n in range(begin,begin+24)],live_control_changes=0,automatic_exposure_implemented=True,diagnostic_full_Y_bytes_read=796262400)
 def call(kk=None,ll=None,ff=None,ss=None,pp=None):
  return validate(render("NATIVE_REAR_LIVE_CONTROL",kk if kk is not None else kernel),render("NATIVE_REAR_LIBCAMERA_CONTROL",ll if ll is not None else library)+"\n"+render("NATIVE_REAR_AE_FRAME",ff if ff is not None else frames)+"\n"+render("NATIVE_REAR_AE_SUMMARY",ss if ss is not None else summary),pp if pp is not None else probe,1)
 assert call()["last80_within_ten_percent"] is True
 f=copy.deepcopy(frames);f[9]["lines"]=1600;assert call(ff=f)["updates"]==1
 f=copy.deepcopy(frames)
 for r in f[320:]:r["meter"]=2000;r["limited"]=1
 assert call(ff=f)["last80_within_ten_percent"] is False

 # Both values change in the next proposal; either ControlList ordering is
 # valid only when actual kernel and library receipts agree exactly.
 pair_frames=copy.deepcopy(frames)
 for row in pair_frames[16:]:row["lines"]=3206;row["gain"]=256
 pair_frames[16]["update"]=1
 pair_summary=copy.deepcopy(summary);pair_summary[0]["updates"]=2
 pair_kernel=copy.deepcopy(kernel)+[
  dict(id=0x009e0903,value=256,reg=0x3508,readback=256,before_ns=702,after_ns=703),
  dict(id=0x00980911,value=3206,reg=0x3500,readback=3206<<4,before_ns=704,after_ns=705)]
 pair_library=copy.deepcopy(library)+[
  dict(id=row["id"],value=row["value"],last_completed_sequence=15,before_ns=701,after_ns=706,cached_readback=1,per_frame_association=0)
  for row in pair_kernel[1:]]
 assert call(kk=pair_kernel,ll=pair_library,ff=pair_frames,ss=pair_summary)["updates"]==2
 assert call(kk=pair_kernel[:1]+pair_kernel[1:][::-1],ll=pair_library[:3]+pair_library[3:][::-1],ff=pair_frames,ss=pair_summary)["updates"]==2

 negatives=0
 def reject(**args):
  nonlocal negatives
  try:call(**args)
  except (RuntimeError,KeyError,IndexError,ValueError):negatives+=1;return
  raise AssertionError("invalid AE receipt admitted")
 for key,value in [("readback",1),("reg",1),("id",1),("value",4000),("before_ns",600),("after_ns",605)]:
  x=copy.deepcopy(kernel);x[0][key]=value;reject(kk=x)
 for key,value in [("cached_readback",0),("per_frame_association",1),("last_completed_sequence",12),("id",1)]:
  x=copy.deepcopy(library);x[2][key]=value;reject(ll=x)
 for key,value in [("sequence",9),("stream",89),("owner",2),("generation",1),("timestamp",1),("meter",float("nan")),("meter",-1),("target",1),("lines",3207),("gain",2049),("update",2),("limited",2)]:
  x=copy.deepcopy(frames);x[8][key]=value;reject(ff=x)
 x=copy.deepcopy(frames);x[20]["lines"]=1600;reject(ff=x)
 x=copy.deepcopy(frames);x.pop();reject(ff=x)
 for key,value in [("decoded",401),("updates",2),("enabled",0),("quality_calibrated",1),("max_gain",8191)]:
  x=copy.deepcopy(summary);x[0][key]=value;reject(ss=x)
 for key,value in [("automatic_exposure_implemented",False),("live_control_changes",4),("diagnostic_full_Y_bytes_read",0)]:
  x=copy.deepcopy(probe);x[key]=value;reject(pp=x)
 for key,value in [("driver_completion_ns",1),("Y_mean",float("nan")),("sequence",400)]:
  x=copy.deepcopy(probe);x["AE_control_timing_samples"][0][key]=value;reject(pp=x)
 x=copy.deepcopy(pair_kernel);x[2]=copy.deepcopy(x[1]);reject(kk=x,ll=pair_library,ff=pair_frames,ss=pair_summary)
 reject(kk=pair_kernel,ll=pair_library[:3]+pair_library[3:][::-1],ff=pair_frames,ss=pair_summary)
 baseline=(P/"run-rear-cadence-v20.py").read_text()
 actual=(P/"run-rear-ae60.py").read_text()
 need_fragments=['"csid_stop","bus_stop"','"rtcdm_stop","source_stop","dma_reclaimed","owner_released","arena_released","reboot"','"successful clean stop must release DMA/owner"','"all sensors must suspend after clean release"','validate_idle_clocks','"libcamera release restores neutral links"','"exact_serialized_command_receipts_proven"','"live_public_FULL_retirement_proven"']
 for fragment in need_fragments:assert fragment in baseline and fragment in actual,fragment
 assert 'for session in range(1,2):' in actual and 'f["automatic_exposure"]==1' in actual and 'sp11-audio-fullio-v19c' in actual and 'v20c' not in actual
 assert '"same_boot_restart_proven"]=False' in actual
 result=dict(status="PASS_NATIVE_AE_RECEIPT_PARSER_AND_NEGATIVE_CASES",negative_cases=negatives,synthetic_fixture_only=True,hardware_access=False,actual_runner_lifecycle_checks_preserved=True,convergence_failure_not_falsely_promoted=True,bounded_async_acknowledgement_admitted=True,exact_proposal_pair_both_ControlList_orders_checked=True)
 report=P.parents[4]/"02-kernel/native-rgb-rear-generation-20261007-73/AE-parser-hosted-02.json"
 # Project storage is outside the repository.
 assert not report.exists();report.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
if __name__=="__main__":main()
