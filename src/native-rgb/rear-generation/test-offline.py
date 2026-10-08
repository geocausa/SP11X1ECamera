#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Offline admission tests against a retained real 119-edge media graph."""
import json,re,runpy,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
GRAPH=Path("/var/lib/sp11-camera-native-profile-20261007-01/PRIVATE-GRAPH-BEFORE-CAPTURE.txt")
OUT=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/native-rgb-rear-generation-20261007-10/offline-runner-01.json")
def main():
 classify=runpy.run_path(str(HERE/"route-contract.py"))["classify"]
 runtime=runpy.run_path(str(HERE/"run-once.py"))
 validate=runtime["validate_formats"];run=runtime["run"]
 root=HERE.parents[2]
 assert run(["git","-C",root,"rev-parse","HEAD"]).strip()==subprocess.check_output(
  ["git","-c","safe.directory="+str(root),"-C",root,"rev-parse","HEAD"],text=True).strip()
 run(["bash",root/"tools/camera-overlap-guard.sh","--require-golden"])
 graph=GRAPH.read_text()
 rear=re.findall(r"^- entity [0-9]+: (ov13858 [0-9]+-0010) ",graph,re.M)
 assert len(rear)==1
 pads=[(rear[0],0),("msm_csiphy1",0),("msm_csiphy1",1),("msm_csid1",0),
       ("msm_csid1",4),("msm_vfe1_pix",0),("msm_vfe1_pix",1)]
 route={("msm_csiphy1",1,"msm_csid1",0),("msm_csid1",4,"msm_vfe1_pix",0)}
 def links(text,enabled):
  source=None;pad=None;output=[]
  for line in text.splitlines():
   m=re.match(r"- entity [0-9]+: (.*?) \(",line)
   if m:source=m[1]
   m=re.match(r"\s*pad([0-9]+):",line)
   if m:pad=int(m[1])
   m=re.fullmatch(r'(\s*)(->|<-) "([^"]+)":([0-9]+) \[([^]]*)\]',line)
   if m and "IMMUTABLE" not in m[5]:
    key=(source,pad,m[3],int(m[4])) if m[2]=="->" else (m[3],int(m[4]),source,pad)
    line=line[:line.rfind("[")+1]+("ENABLED" if key in enabled else "")+"]"
   output.append(line)
  return "\n".join(output)+"\n"
 neutral=links(graph,set());assert classify(neutral)[0]=="neutral"
 active=links(graph,route);assert classify(active)[0]=="rear-pix-only"
 formats=re.sub(r"fmt:[^ /]+/[0-9]+x[0-9]+","fmt:SGRBG10_1X10/4076x2806",active)
 formats,n=re.subn(r"(- entity [0-9]+: msm_vfe1_pix \(.*?\n\s*pad1:.*?fmt:SGRBG10_1X10/)4076x2806",r"\g<1>4064x2806",formats,count=1,flags=re.S)
 assert n==1
 validate(formats,pads)
 validate(formats.replace("[stream:0 fmt:","[fmt:"),pads)
 # Actual preceding rear boot graph is the format-clamping regression fixture.
 live=Path("/var/lib/sp11-camera-native-rear-generation-20261007-02/PRIVATE-REAR-PIX-GRAPH.txt").read_text()
 live_rear=re.findall(r"^- entity [0-9]+: (ov13858 [0-9]+-0010) ",live,re.M)
 assert len(live_rear)==1
 validate(live,[(live_rear[0],0)]+pads[1:])
 failures=0
 def reject(action):
  nonlocal failures
  try:action()
  except (ValueError,RuntimeError):failures+=1;return
  raise AssertionError("invalid admission accepted")
 reject(lambda:classify(links(graph,route|{("msm_csiphy2",1,"msm_csid1",0)})))
 reject(lambda:classify(active.replace('-> "msm_csid1":0 [ENABLED]','-> "msm_csid1":0 []',1)))
 reject(lambda:classify(active.replace('[ENABLED,IMMUTABLE]','[IMMUTABLE]',1)))
 reject(lambda:classify(active.replace('device node name /dev/video','device node name /dev/videobad',1)))
 for name,pad in pads:
  pattern=r"(- entity [0-9]+: "+re.escape(name)+r" \(.*?\n\s*pad"+str(pad)+r":.*?fmt:)SGRBG10_1X10/(?:4076|4064)x2806"
  changed,n=re.subn(pattern,r"\g<1>SRGGB10_1X10/4076x2806",formats,count=1,flags=re.S)
  assert n==1
  reject(lambda:validate(changed,pads))
 reject(lambda:validate(formats.replace("[stream:0 fmt:","[stream:1 fmt:"),pads))
 with tempfile.TemporaryDirectory(prefix="rear-probe-compile-") as tmp:
  subprocess.run(["gcc","-std=gnu11","-Wall","-Wextra","-Werror","-O2",HERE/"probe.c","-o",Path(tmp)/"probe"],check=True)
 assert failures==12
 result={"status":"PASS_REAL_GRAPH_ADMISSION_FORMAT_READBACK_AND_PROBE_COMPILE",
 "actual_rear_boot_VFE_width_clamp_checked":True,"root_service_environment_Git_trust":True,"retained_actual_graph":True,"edges":119,"device_nodes":45,"negative_cases":failures,
 "hardware_access":False,"synthetic_format_changes_for_offline_testing":True}
 assert not OUT.exists();OUT.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result))
if __name__=="__main__":main()
