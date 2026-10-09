
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual existing-V4L2 control calls and exact per-session register admission."""
import argparse,json,os,runpy,struct,subprocess,tempfile,types
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--staged",type=Path,required=True);ap.add_argument("--report",type=Path,required=True);args=ap.parse_args();assert not args.report.exists()
 rt=runpy.run_path(str(HERE/"run-rear-cadence-v18.py"));plan=rt["rear_photometric_plan"];verify=rt["validate_rear_photometric_controls"]
 assertions=0;neg=0
 def check(x):
  nonlocal assertions
  assert x;assertions+=1
 def reject(fn):
  nonlocal neg
  try:fn()
  except (RuntimeError,OSError):neg+=1
  else:raise AssertionError("bad photometric input admitted")
 def log(f):return "NATIVE_REAR_SENSOR_CONTROLS "+" ".join(str(k)+"="+str(v) for k,v in f.items())
 for i in [1,2,3]:
  p=plan(i);f=dict(exposure_reg=p["exposure"]<<4,exposure_lines=p["exposure"],analog=p["analogue_gain"],digital_b=1024,digital_g=1024,digital_r=1024,pattern_reg=0,pattern_control=0)
  check(verify(log(f),i)==f)
  for k in f:
   bad=dict(f);bad[k]+=1;reject(lambda:verify(log(bad),i))
  for other in [j for j in [1,2,3] if plan(j)!=p]:reject(lambda:verify(log(f),other))
 for i in [True,0,4,-1,None,"2"]:reject(lambda:plan(i))
 fn=rt["set_rear_photometric_controls"];g=fn.__globals__
 original={k:g[k] for k in ["run","Path","os","fcntl","set_rear_test_pattern"]}
 calls=[];closed=[];opened=[];state=dict(char=True,cid_drift=False,value_drift=False,ret=0,raises=False,session=1,run_raises=False)
 class FakePath:
  def __init__(self,s):assert s=="/dev/v4l-subdev-model"
  def is_char_device(self):return state["char"]
 def run(argv):
  calls.append(argv)
  if state["run_raises"]:raise RuntimeError("modeled control write failure")
  return "CLI display irrelevant"
 def op(device,flags):
  assert device=="/dev/v4l-subdev-model" and flags==os.O_RDONLY|os.O_NONBLOCK|os.O_CLOEXEC|os.O_NOFOLLOW
  opened.append(123);return 123
 def ioctl(fd,command,buf,mutable):
  assert fd==123 and command==0xc008561b and mutable is True and isinstance(buf,bytearray)
  cid,value=struct.unpack("=Ii",buf);assert value==0 and cid in (0x00980911,0x009e0903)
  if state["raises"]:raise OSError("modeled ioctl failure")
  name="exposure" if cid==0x00980911 else "analogue_gain";value=plan(state["session"])[name]
  buf[:]=struct.pack("=Ii",cid+int(state["cid_drift"]),value+int(state["value_drift"]))
  return state["ret"]
 def pat(device,value):assert device=="/dev/v4l-subdev-model" and value==0;return 0
 g.update(run=run,Path=FakePath,os=types.SimpleNamespace(open=op,close=lambda fd:closed.append(fd),O_RDONLY=os.O_RDONLY,O_NONBLOCK=os.O_NONBLOCK,O_CLOEXEC=os.O_CLOEXEC,O_NOFOLLOW=os.O_NOFOLLOW),fcntl=types.SimpleNamespace(ioctl=ioctl),set_rear_test_pattern=pat)
 for i in [1,2,3]:
  state["session"]=i;before=len(closed);p=plan(i)
  check(fn("/dev/v4l-subdev-model",i)==p);check(len(closed)==before+2)
  check(calls[-1]==["v4l2-ctl","-d","/dev/v4l-subdev-model","--set-ctrl=exposure="+str(p["exposure"])+",analogue_gain="+str(p["analogue_gain"])])
 for key,value in [("char",False),("cid_drift",True),("value_drift",True),("ret",1),("raises",True),("run_raises",True)]:
  state.update(char=True,cid_drift=False,value_drift=False,ret=0,raises=False,session=1,run_raises=False);state[key]=value
  before=len(closed);beforeopen=len(opened)
  reject(lambda:fn("/dev/v4l-subdev-model",1));check(len(closed)-before==len(opened)-beforeopen)
 g.update(original)
 with tempfile.TemporaryDirectory(prefix="photometric-uapi-") as td:
  c=Path(td)/"uapi.c";exe=Path(td)/"uapi"
  c.write_text('#include <stdio.h>\n#include <time.h>\n#include <linux/videodev2.h>\nint main(void){printf("%u %u %lu %zu\\n",V4L2_CID_EXPOSURE,V4L2_CID_ANALOGUE_GAIN,(unsigned long)VIDIOC_G_CTRL,sizeof(struct v4l2_control));return 0;}\n')
  subprocess.run(["gcc","-std=c11","-Wall","-Wextra","-Werror",str(c),"-o",str(exe)],check=True)
  check(subprocess.check_output([str(exe)],text=True).split()==[str(0x00980911),str(0x009e0903),str(0xc008561b),"8"])
 source=(HERE/"run-rear-cadence-v18.py").read_text();main=source.split("def main():",1)[1]
 check(main.index("set_rear_photometric_controls(")<main.index("probe=subprocess.run("))
 check('validate_rear_photometric_controls(log,session)' in main)
 check('pattern=0' in main)
 # Native sensor code unchanged byte-for-byte from completed53.
 baseline=args.staged.parent.parent/"native-rgb-rear-generation-20261007-66/ov13858"
 for name in ["ov13858.c","native-rear-sensor-controls-v2.inc"]:check((runpy.run_path(str(HERE/"apply-rear-live-controls.py"))["undo_sensor"]((args.staged.parent/"ov13858"/name).read_text()) if name=="ov13858.c" else (args.staged.parent/"ov13858"/name).read_text())==(baseline/name).read_text())
 report=dict(status="PASS_EXACT_PHOTOMETRIC_PLAN_EXISTING_V4L2_UAPI_AND_REGISTER_PROOF",assertions=assertions,negative_cases=neg,session_plan=[plan(i) for i in [1,2,3]],actual_UAPI_compiled=True,fd_cleanup_failure_models=True,sensor_source_unchanged_from53=True,hardware_access=False)
 args.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
