#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Offline admission tests against a retained real 119-edge media graph."""
import json,re,runpy,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
GRAPH=Path("/var/lib/sp11-camera-native-profile-20261007-01/PRIVATE-GRAPH-BEFORE-CAPTURE.txt")
OUT=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/native-rgb-rear-generation-20261007-34/offline-runner-01.json")
def main():
 classify=runpy.run_path(str(HERE.parent/"rear-generation/route-contract.py"))["classify"]
 runtime=runpy.run_path(str(HERE/"run-live-observe.py"))
 assert runtime["MARKER"]=="sp11_camera_native_rear_generation_20261007_26=1"
 assert str(runtime["D"]).endswith("generation-20261007-26")
 validate=runtime["validate_formats"];run=runtime["run"]
 kernel=OUT.parent/"camss/camss-video.c"
 source=kernel.read_text()
 assert source.count("q->min_queued_buffers = 2;")==1
 assert source.index("q->min_queued_buffers = 2;")<source.index("ret = vb2_queue_init(q);")
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
 formats=re.sub(r"fmt:[^ /]+/[0-9]+x[0-9]+","fmt:SGRBG10_1X10/4064x2286",active)
 validate(formats,pads)
 validate(formats.replace("[stream:0 fmt:","[fmt:"),pads)
 # Mode0 retained graph must reject before a kernel trigger.
 legacy=Path("/var/lib/sp11-camera-native-rear-generation-20261007-02/PRIVATE-REAR-PIX-GRAPH.txt").read_text()
 failures=0
 def reject(action):
  nonlocal failures
  try:action()
  except (ValueError,RuntimeError):failures+=1;return
  raise AssertionError("invalid admission accepted")
 reject(lambda:validate(legacy,pads))
 reject(lambda:classify(links(graph,route|{("msm_csiphy2",1,"msm_csid1",0)})))
 reject(lambda:classify(active.replace('-> "msm_csid1":0 [ENABLED]','-> "msm_csid1":0 []',1)))
 reject(lambda:classify(active.replace('[ENABLED,IMMUTABLE]','[IMMUTABLE]',1)))
 reject(lambda:classify(active.replace('device node name /dev/video','device node name /dev/videobad',1)))
 for name,pad in pads:
  pattern=r"(- entity [0-9]+: "+re.escape(name)+r" \(.*?\n\s*pad"+str(pad)+r":.*?fmt:)SGRBG10_1X10/4064x2286"
  changed,n=re.subn(pattern,r"\g<1>SRGGB10_1X10/4076x2806",formats,count=1,flags=re.S)
  assert n==1
  reject(lambda:validate(changed,pads))
 reject(lambda:validate(formats.replace("[stream:0 fmt:","[stream:1 fmt:"),pads))
 live=runtime["live_observation"]
 record="NATIVE_REAR_LIVE_REPLACEMENT "
 facts=dict(ret=0,owner=1,old_complete=1,next_complete=1,receipts=1,
  enabled=1023,programmed=1023,consumed_addr=1023,published=15,consumed=15,
  cursor=15,epoch_before=2,epoch_after=2,live_release=0)
 def log(f):return record+" ".join(f"{k}={v}" for k,v in f.items())
 assert live(log(facts))==(facts,True)
 blocked=dict(facts,ret=-11,published=16)
 assert live(log(blocked))==(blocked,False)
 for key in facts:
  changed=dict(facts);changed[key]=0 if facts[key]!=0 else 1
  if key=="ret":
   assert live(log(changed))==(changed,False)
  else:reject(lambda:live(log(changed)))
 for bad in ["",log(facts)+"\n"+log(facts),log(facts)+" extra=1",
             log(facts)+" owner=1",log(facts).replace("owner=1","owner=x")]:
  reject(lambda:live(bad))
 with tempfile.TemporaryDirectory(prefix="rear-probe-compile-") as tmp:
  subprocess.run(["gcc","-std=gnu11","-Wall","-Wextra","-Werror","-O2",HERE/"probe.c","-o",Path(tmp)/"probe"],check=True)
 assert failures==31
 result={"status":"PASS_REAL_GRAPH_ADMISSION_FORMAT_READBACK_AND_PROBE_COMPILE",
 "legacy_mode0_graph_rejected":True,"exact_mode1_pad_readbacks_checked":True,"root_service_environment_Git_trust":True,"retained_actual_graph":True,"edges":119,"device_nodes":45,"negative_cases":failures,
 "hardware_access":False,"actual_live_observation_log_parser_checked":True,"negative_observation_cases":18,"synthetic_format_changes_for_offline_testing":True}
 assert not OUT.exists();OUT.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result))
if __name__=="__main__":main()
