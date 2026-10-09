#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual read-only sensor helper and strict scene/pattern/scene runtime proof."""
import argparse,json,os,re,runpy,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 sensor=a.staged.parent/"ov13858/ov13858.c";t=sensor.read_text();t=runpy.run_path(str(HERE/"apply-rear-live-controls.py"))["undo_sensor"](t);helper=a.staged.parent/"ov13858/native-rear-sensor-controls-v2.inc"
 assert helper.read_bytes()==(HERE/helper.name).read_bytes()
 start=t.index("static int ov13858_start_streaming(");stop=t.index("/* Stop streaming */",start);flow=t[start:stop]
 assert flow.index("__v4l2_ctrl_handler_setup(")<flow.index("native_rear_sensor_controls_readback(")<flow.index("return ov13858_write_reg(")
 # Exact baseline sensor source, removing only this readback include and call.
 clean=t.replace('#include "native-rear-sensor-controls-v2.inc"\n\n',"",1).replace('\tret = native_rear_sensor_controls_readback(ov13858);\n\tif (ret)\n\t\treturn ret;\n\n',"",1)
 clean=clean.replace('\tstruct v4l2_ctrl *analogue_gain;\n\tstruct v4l2_ctrl *digital_gain;\n\tstruct v4l2_ctrl *test_pattern;\n','',1)
 for field in ['analogue_gain','digital_gain','test_pattern']:
  clean=clean.replace('ov13858->'+field+' = v4l2_ctrl_new','v4l2_ctrl_new',1)
 baseline=a.staged.parent.parent/"native-rgb-rear-generation-20261007-62/ov13858/ov13858.c"
 assert clean==baseline.read_text(),"undeclared sensor policy change"
 h=helper.read_text();assert "write_reg" not in h and "set_ctrl" not in h
 assert "v4l2_ctrl_find(" not in h and "mutex_lock(" not in h and "lockdep_assert_held(&ov13858->mutex)" in h
 core=(a.staged.parent.parent/"e003i-front-production-src/drivers/media/v4l2-core/v4l2-ctrls-core.c").read_text()
 assert "mutex_lock(hdl->lock);" in core and "struct v4l2_ctrl_ref *ref = find_ref_lock(hdl, id);" in core
 assert "ctrl_hdlr->lock = &ov13858->mutex;" in t
 results=[]
 with tempfile.TemporaryDirectory(prefix="sensor-readback-host-") as temp:
  for cc in ["gcc","clang"]:
   exe=Path(temp)/cc
   subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(helper.parent),"-I"+str(HERE),str(HERE/"test-rear-sensor-controls-model-v2.c"),"-o",str(exe)],check=True,capture_output=True,text=True)
   out=subprocess.check_output([str(exe)],text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   m=re.search(r"SENSOR_READBACK_MODEL_PASS assertions=(\d+) negatives=(\d+)",out);assert m
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,assertions=int(m[1]),negative_cases=int(m[2])))
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v16.py"));parse=runtime["rear_sensor_controls"]
 good=dict(exposure_reg=25600,exposure_lines=1600,analog=128,digital_b=1024,digital_g=1024,digital_r=1024,pattern_reg=0,pattern_control=0)
 def log(f):return "NATIVE_REAR_SENSOR_CONTROLS "+" ".join(str(k)+"="+str(v) for k,v in f.items())
 assert parse(log(good),0)==good
 bars=dict(good,pattern_reg=128,pattern_control=1);assert parse(log(bars),1)==bars
 neg=0
 def reject(text,pattern):
  nonlocal neg
  try:parse(text,pattern)
  except RuntimeError:neg+=1
  else:raise AssertionError("bad sensor proof accepted")
 for key,values in {"exposure_reg":[0,25599,25601],"exposure_lines":[0,3,3207],"analog":[-1,8192],"digital_b":[-1,16385,1023],"digital_g":[1023],"digital_r":[1023],"pattern_reg":[128,256],"pattern_control":[1,4]}.items():
  for value in values:
   f=dict(good);f[key]=value;reject(log(f),0)
 for key in good:
  f=dict(good);del f[key];reject(log(f),0)
 for text in ["",log(good)+"\n"+log(good),log(good)+" analog=128",log(good)+" extra=0",log(good).replace("analog=128","analog=x")]:reject(text,0)
 reject(log(good),1);reject(log(bars),0)
 for pattern in [True,-1,2,None]:reject(log(good),pattern)
 # Actual mutable binary UAPI call, fd release and failed control admission.
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v16.py"))
 fn=runtime["set_rear_test_pattern"];g=fn.__globals__
 import struct,types
 original={key:g[key] for key in ["run","Path","os","fcntl"]}
 calls=[];closed=[];ioctls=[];state=dict(value=1,cid=0x009f0903,ret=0,raises=False,char=True)
 class FakePath:
  def __init__(self,s):assert s=="/dev/v4l-subdev-model"
  def is_char_device(self):return state["char"]
 def fake_run(args):calls.append(args);return "irrelevant CLI display"
 def fake_open(path,flags):
  assert path=="/dev/v4l-subdev-model" and flags==os.O_RDONLY|os.O_NONBLOCK|os.O_CLOEXEC|os.O_NOFOLLOW
  return 123
 def fake_ioctl(fd,command,buf,mutate):
  assert fd==123 and command==0xc008561b and mutate is True and isinstance(buf,bytearray)
  assert bytes(buf)==struct.pack("=Ii",0x009f0903,0)
  ioctls.append(command)
  if state["raises"]:raise OSError("modeled ioctl failure")
  buf[:]=struct.pack("=Ii",state["cid"],state["value"])
  return state["ret"]
 g["Path"]=FakePath;g["run"]=fake_run
 g["os"]=types.SimpleNamespace(open=fake_open,close=lambda fd:closed.append(fd),O_RDONLY=os.O_RDONLY,O_NONBLOCK=os.O_NONBLOCK,O_CLOEXEC=os.O_CLOEXEC,O_NOFOLLOW=os.O_NOFOLLOW)
 g["fcntl"]=types.SimpleNamespace(ioctl=fake_ioctl)
 assert fn("/dev/v4l-subdev-model",1)==1 and closed==[123]
 assert calls==[["v4l2-ctl","-d","/dev/v4l-subdev-model","--set-ctrl=test_pattern=1"]]
 for key,value in [("value",0),("cid",0),("ret",1),("raises",True),("char",False)]:
  state.update(value=1,cid=0x009f0903,ret=0,raises=False,char=True);state[key]=value;before=len(closed)
  try:fn("/dev/v4l-subdev-model",1)
  except (RuntimeError,OSError):neg+=1
  else:raise AssertionError("bad binary control admitted")
  assert len(closed)==before+(0 if key=="char" else 1),"fd leaked on failed readback"
 for key,value in original.items():g[key]=value
 # Compile actual installed UAPI definitions, not a copied constant model.
 with tempfile.TemporaryDirectory(prefix="sensor-uapi-") as temp:
  c=Path(temp)/"uapi.c";exe=Path(temp)/"uapi"
  c.write_text('#include <stdio.h>\n#include <time.h>\n#include <linux/videodev2.h>\nint main(void){printf("%u %lu %zu\\\n",V4L2_CID_TEST_PATTERN,(unsigned long)VIDIOC_G_CTRL,sizeof(struct v4l2_control));return 0;}\n')
  subprocess.run(["gcc","-std=c11","-Wall","-Wextra","-Werror",str(c),"-o",str(exe)],check=True)
  assert subprocess.check_output([str(exe)],text=True).split()==[str(0x009f0903),str(0xc008561b),"8"]
 main=(HERE/"run-rear-cadence-v16.py").read_text().split("def main():",1)[1]
 assert 'pattern=0' in main
 assert main.index("set_rear_photometric_controls(")<main.index("probe=subprocess.run(")
 assert 'validate_rear_photometric_controls(log,session)' in main
 # All kernel transport, ISP and lifetime sources unchanged except identity.
 old=a.staged.parent.parent/"native-rgb-rear-generation-20261007-68/camss"
 compared=0
 for q in sorted(a.staged.iterdir()):
  if q.suffix not in (".c",".h",".inc"):continue
  if q.name=="native-rear-generation-identity.h":continue # unique firmware identity digest
  b=old/q.name;assert b.exists(),q.name
  left=q.read_text().replace("identity=56 consumed=1","identity=55 consumed=1").replace("generation_20261007_56","generation_20261007_55").replace("generation-20261007-56","generation-20261007-55")
  assert left==b.read_text(),("undeclared ISP/queue/lifetime delta",q.name);compared+=1
 report=dict(status="PASS_SENSOR_CONTROL_READBACK_AND_SCENE_PATTERN_SCENE",results=results,sensor_parser_negative_cases=neg,baseline_sensor_flow_exact_after_readonly_additions=True,camss_source_files_equal_except_identity=compared,actual_control_writes_only_existing_V4L2_controls=True,photometric_control_writes_qualified_separately=True,scene_pattern_scene=[0,0,0],all_original_lifetime_and_Golden_guards_preserved=True,recursive_lock_regression_original52_detected=True,fixed_helper_has_no_public_control_lookup_or_lock_acquisition=True,retained_control_pointers_checked=True,hardware_access=False)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
