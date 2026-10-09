#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual control conversion/readback/CPU-read helpers; scalar parser negatives."""
import argparse,copy,json,os,re,runpy,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;LIB=HERE.parent/"rear-libcamera"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--staged",type=Path,required=True);ap.add_argument("--report",type=Path,required=True);a=ap.parse_args();assert not a.report.exists()
 sensor=a.staged.parent/"ov13858";h=sensor/"native-rear-live-control-readback.inc"
 assert h.read_bytes()==(HERE/h.name).read_bytes()
 undo=runpy.run_path(str(HERE/"apply-rear-live-controls.py"))["undo_sensor"]
 assert undo((sensor/"ov13858.c").read_text())==(a.staged.parent.parent/"native-rgb-rear-generation-20261007-68/ov13858/ov13858.c").read_text()
 s=h.read_text()
 assert "write_reg(" not in s and "v4l2_ctrl_find(" not in s and "mutex_lock(" not in s
 assert "lockdep_assert_held" in s
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-live-controls-model-") as td:
  for compiler,source,include,tag in [("g++",LIB/"test-live-controls.cpp",LIB,"LIVE_CONTROLS_MODEL_PASS"),("clang++",LIB/"test-live-controls.cpp",LIB,"LIVE_CONTROLS_MODEL_PASS"),("gcc",HERE/"test-live-sensor-controls.c",sensor,"LIVE_SENSOR_MODEL_PASS"),("clang",HERE/"test-live-sensor-controls.c",sensor,"LIVE_SENSOR_MODEL_PASS")]:
   exe=Path(td)/compiler
   subprocess.run([compiler,"-std="+("c++17" if "++" in compiler else "c11"),"-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(include),str(source),"-o",str(exe)],check=True,capture_output=True,text=True)
   out=subprocess.check_output([str(exe)],text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   m=re.search(tag+r" assertions=(\d+) negatives=(\d+)",out);assert m,out
   results.append(dict(compiler=compiler,ASAN_UBSAN_Werror=True,assertions=int(m[1]),negatives=int(m[2])))
 parse=runpy.run_path(str(HERE/"live-control-proof.py"))["validate"]
 def receipt(tag,row):return tag+" "+" ".join(str(k)+"="+str(v) for k,v in row.items())
 parser_assertions=0;negatives=0
 for session in [1,2,3]:
  initial=3206 if session==2 else 1600;gain=1024 if session==2 else 128
  plan=[(64,0x00980911,1600 if initial==3206 else 3206),(128,0x00980911,initial),(192,0x009e0903,128 if gain==1024 else 1024),(256,0x009e0903,gain)]
  ks=[];ls=[dict(id=cid,value=value,last_completed_sequence=-1,before_ns=10,after_ns=20,cached_readback=1,per_frame_association=0) for cid,value in [(0x00980911,initial),(0x009e0903,gain)]]
  for i,(trigger,cid,value) in enumerate(plan):
   clock=1000+i*100
   ks.append(dict(id=cid,value=value,reg=0x3500 if cid==0x00980911 else 0x3508,readback=value<<4 if cid==0x00980911 else value,before_ns=clock,after_ns=clock+1))
   ls.append(dict(id=cid,value=value,last_completed_sequence=trigger-1,before_ns=clock-1,after_ns=clock+2,cached_readback=1,per_frame_association=0))
  probe=dict(live_control_changes=4,automatic_exposure_implemented=False,diagnostic_full_Y_bytes_read=796262400,manual_control_timing_samples=[dict(sequence=n,driver_completion_ns=(n+1)*33333333,Y_mean=8.0 if n<begin+11 else 16.0) for begin in [56,120,184,248] for n in range(begin,begin+24)])
  def call(kk=ks,ll=ls,pp=probe):
   return parse("\n".join(receipt("NATIVE_REAR_LIVE_CONTROL",r) for r in kk),"\n".join(receipt("NATIVE_REAR_LIBCAMERA_CONTROL",r) for r in ll),pp,session)
  assert call()["status"].startswith("PASS");parser_assertions+=1
  def reject(kk=ks,ll=ls,pp=probe):
   nonlocal negatives
   try:call(kk,ll,pp)
   except (RuntimeError,KeyError):negatives+=1
   else:raise AssertionError("invalid live proof admitted")
  reject(ks[:-1]);reject(ks+[ks[0]]);reject(ll=ls[:-1])
  for field in ["id","value","reg","readback","before_ns","after_ns"]:
   bad=copy.deepcopy(ks);bad[0][field]=-1;reject(kk=bad)
  for field in ["id","value","last_completed_sequence","before_ns","after_ns","cached_readback","per_frame_association"]:
   bad=copy.deepcopy(ls);bad[2][field]=999 if field=="last_completed_sequence" else 1 if field=="per_frame_association" else 0;reject(ll=bad)
  for field,value in [("live_control_changes",3),("automatic_exposure_implemented",True),("diagnostic_full_Y_bytes_read",0)]:
   bad=copy.deepcopy(probe);bad[field]=value;reject(pp=bad)
  bad=copy.deepcopy(probe);bad["manual_control_timing_samples"].pop();reject(pp=bad)
  for field,value in [("sequence",True),("sequence",57),("driver_completion_ns",0),("driver_completion_ns",1.0),("Y_mean",True),("Y_mean",float("nan")),("Y_mean",-1),("Y_mean",256),("extra",0)]:
   bad=copy.deepcopy(probe);bad["manual_control_timing_samples"][0][field]=value;reject(pp=bad)
 pipeline=(LIB/"camss-x1e-rear-statistics-v2.cpp").read_text()
 method=pipeline.split("int RearData::applyControls(",1)[1].split("void RearData::ready(",1)[0]
 assert method.index("return -EOPNOTSUPP")<method.index("sensor_->setControls")
 assert "per_frame_association=0" in method
 queue=pipeline.split(" int queueRequestDevice(",1)[1].split(" bool match(",1)[0]
 assert queue.index("data->applyControls")<queue.index("video_->queueBuffer")
 assert "SensorTimestamp" not in pipeline.split("void RearData::ready",1)[1].split("handler->completeBuffer",1)[0].replace("SensorTimestamp control","")
 report=dict(status="PASS_ACTUAL_MANUAL_CONTROL_CONVERSION_LIVE_REGISTER_READBACK_AND_DIAGNOSTIC_CPU_SYNC",results=results,parser_assertions=parser_assertions,parser_negative_cases=negatives,reversible_sensor_overlay_matches55=True,original_sensor_writes_unchanged=True,unknown_controls_rejected_before_I2C=True,actual_global_Y_read_helper_failure_cleanup_checked=True,automatic_exposure_implemented=False,hardware_access=False)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
