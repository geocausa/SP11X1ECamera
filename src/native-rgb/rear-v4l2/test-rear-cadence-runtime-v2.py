#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Offline admission tests against a retained real 119-edge media graph."""
import json,re,runpy,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
GRAPH=Path("/var/lib/sp11-camera-native-profile-20261007-01/PRIVATE-GRAPH-BEFORE-CAPTURE.txt")
OUT=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/native-rgb-rear-generation-20261007-53/offline-runner-01.json")
def main():
 classify=runpy.run_path(str(HERE.parent/"rear-generation/route-contract.py"))["classify"]
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v2.py"))
 assert runtime["MARKER"]=="sp11_camera_native_rear_generation_20261007_42=1"
 assert str(runtime["D"]).endswith("generation-20261007-42")
 validate=runtime["validate_formats"];run=runtime["run"]
 kernel=OUT.parent/"camss/camss-video.c"
 source=kernel.read_text()
 assert source.count("q->min_queued_buffers = 2;")==1
 assert source.index("q->min_queued_buffers = 2;")<source.index("ret = vb2_queue_init(q);")
 root=HERE.parents[2]
 assert run(["git","-C",root,"rev-parse","HEAD"]).strip()==subprocess.check_output(
  ["git","-c","safe.directory="+str(root),"-C",root,"rev-parse","HEAD"],text=True).strip()
 run(["bash",root/"tools/camera-overlap-guard.sh","--require-golden"])
 graph=subprocess.check_output(["sudo","-n","cat",str(GRAPH)],text=True)
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
 legacy=subprocess.check_output(["sudo","-n","cat","/var/lib/sp11-camera-native-rear-generation-20261007-02/PRIVATE-REAR-PIX-GRAPH.txt"],text=True)
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
 retire=runtime["live_retirement"]
 full=dict(ret=0,released=1,old_valid=1,next_pinned=1,aux_pinned=8,stop_flags=0,vb2_complete=0,requeue=0)
 def full_log(f):return "NATIVE_REAR_LIVE_FULL_RETIRE "+" ".join(f"{k}={v}" for k,v in f.items())
 assert retire(full_log(full))==(full,True)
 blocked=dict(full,ret=-11,released=0,old_valid=0)
 assert retire(full_log(blocked))==(blocked,False)
 for key in full:
  changed=dict(full);changed[key]=0 if full[key] else 1
  reject(lambda:retire(full_log(changed)))
 for bad in ["",full_log(full)+"\\n"+full_log(full),full_log(full)+" extra=1",
             full_log(full)+" released=1",full_log(full).replace("released=1","released=x")]:
  reject(lambda:retire(bad))
 aux=runtime["live_aux_retirement"]
 aux_facts=dict(ret=0,released=8,old_valid=1,next_aux_pinned=8,next_FULL_pinned=1,stop_flags=0,vb2_complete=0,requeue=0)
 def aux_log(f):return "NATIVE_REAR_LIVE_AUX_RETIRE "+" ".join(f"{k}={v}" for k,v in f.items())
 assert aux(aux_log(aux_facts))==(aux_facts,True)
 blocked=dict(aux_facts,ret=-11,released=0,old_valid=0)
 assert aux(aux_log(blocked))==(blocked,False)
 for key in aux_facts:
  changed=dict(aux_facts);changed[key]=0 if aux_facts[key] else 1
  reject(lambda:aux(aux_log(changed)))
 for bad in ["",aux_log(aux_facts)+"\n"+aux_log(aux_facts),aux_log(aux_facts)+" extra=1",
             aux_log(aux_facts)+" released=8",aux_log(aux_facts).replace("released=8","released=x")]:
  reject(lambda:aux(bad))
 command=runtime["command_receipts"]
 command_facts=dict(ret=0,packets=4,BL_complete=22,first_seq=1,last_seq=22,command_arenas_pinned=4,live_release=0,rewrite=0,requeue=0)
 def command_log(f):return "NATIVE_REAR_COMMAND_RECEIPTS "+" ".join(f"{k}={v}" for k,v in f.items())
 assert command(command_log(command_facts))==(command_facts,True)
 blocked=dict(command_facts,ret=-11,packets=0,BL_complete=0,last_seq=0)
 assert command(command_log(blocked))==(blocked,False)
 for key in command_facts:
  if key=="ret":continue
  changed=dict(command_facts);changed[key]=0 if command_facts[key] else 1
  reject(lambda:command(command_log(changed)))
 for bad in ["",command_log(command_facts)+"\n"+command_log(command_facts),command_log(command_facts)+" extra=1",command_log(command_facts)+" packets=4",command_log(command_facts).replace("packets=4","packets=x")]:
  reject(lambda:command(bad))
 retirement=runtime["command_retirement"]
 retired_facts=dict(ret=0,released=4,retired_valid=1,command_arenas_pinned=0,owner=1,BL_complete=22,stop_flags=0,vb2_complete=0,requeue=0)
 def retired_log(f):return "NATIVE_REAR_COMMAND_RETIRE "+" ".join(f"{k}={v}" for k,v in f.items())
 assert retirement(retired_log(retired_facts))==(retired_facts,True)
 blocked=dict(retired_facts,ret=-11,released=0,retired_valid=0,command_arenas_pinned=4,BL_complete=0)
 assert retirement(retired_log(blocked))==(blocked,False)
 for key in retired_facts:
  changed=dict(retired_facts);changed[key]=0 if retired_facts[key] else 1
  reject(lambda:retirement(retired_log(changed)))
 for bad in ["",retired_log(retired_facts)+"\n"+retired_log(retired_facts),retired_log(retired_facts)+" extra=1",retired_log(retired_facts)+" owner=1",retired_log(retired_facts).replace("owner=1","owner=x")]:
  reject(lambda:retirement(bad))
 reject(lambda:retirement(retired_log(dict(blocked,released=1))))
 reject(lambda:retirement(retired_log(dict(blocked,command_arenas_pinned=3))))
 queue=runtime["rear_queue"]
 q=dict(ret=0,live_completed=80,handoffs=79,output_updates=79,cursor=237,starved=0,command_resubmissions=0,cpu_pixel_copy=0)
 def queue_log(f):return "NATIVE_REAR_QUEUE "+" ".join(f"{k}={v}" for k,v in f.items())
 assert queue(queue_log(q))==(q,True)
 blocked=dict(q,ret=-11,live_completed=2,handoffs=1,cursor=13)
 assert queue(queue_log(blocked))==(blocked,False)
 for key in q:
  if key=="ret":continue
  changed=dict(q);changed[key]=0 if q[key] else 1
  reject(lambda:queue(queue_log(changed)))
 for bad in ["",queue_log(q)+"\n"+queue_log(q),queue_log(q)+" extra=1",queue_log(q)+" ret=0",queue_log(q).replace("cursor=237","cursor=x")]:
  reject(lambda:queue(bad))
 for key,value in [("live_completed",79),("handoffs",78),("cursor",16),("cursor",2**32-1),("live_completed",-1)]:
  reject(lambda:queue(queue_log(dict(q,**{key:value}))))
 with tempfile.TemporaryDirectory(prefix="rear-probe-compile-") as tmp:
  subprocess.run(["gcc","-std=gnu11","-Wall","-Wextra","-Werror","-O2",HERE/"probe.c","-o",Path(tmp)/"probe"],check=True)
 assert failures==103
 result={"status":"PASS_REAL_GRAPH_ADMISSION_FORMAT_READBACK_AND_PROBE_COMPILE",
 "legacy_mode0_graph_rejected":True,"exact_mode1_pad_readbacks_checked":True,"root_service_environment_Git_trust":True,"retained_actual_graph":True,"edges":119,"device_nodes":45,"negative_cases":failures,
 "hardware_access":False,"actual_live_observation_log_parser_checked":True,"negative_observation_cases":18,"negative_live_retirement_cases":13,"negative_live_auxiliary_retirement_cases":13,"negative_command_receipt_cases":13,"negative_live_command_retirement_cases":16,"negative_rolling_queue_cases":17,"synthetic_format_changes_for_offline_testing":True}
 assert not OUT.exists();OUT.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result))
if __name__=="__main__":main()
