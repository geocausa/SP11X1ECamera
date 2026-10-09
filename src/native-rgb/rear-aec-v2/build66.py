#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build fresh66 kernel from hash-verified73 sources + published measured tuning + QXA2."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT.parents[1]
BASE=PROJECT/"02-kernel/native-rgb-rear-generation-20261007-73"
OUT=PROJECT/"02-kernel/native-rgb-rear-generation-20261010-67"
HEAD="8186b59b8e4bb23ce28489ac31f8e9e5babdb4d1"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(p,a,b):
 s=p.read_text();assert s.count(a)==1,a;p.write_text(s.replace(a,b,1))
def main():
 subprocess.run(["bash",ROOT/"tools/camera-overlap-guard.sh","--require-golden","--require-no-camera-process","--ignore-parent-builder","--expect-head",HEAD,"--expect-origin",HEAD],check=True)
 assert not OUT.exists()
 base=json.loads((BASE/"build-result.json").read_text())
 assert base["status"]=="PASS_REAR_GENERATION_SOURCE_BUILD_NOT_INSTALLED"
 for n,h in base["staged_sources"].items():assert sha(BASE/n)==h,n
 OUT.mkdir()
 for n in base["staged_sources"]:
  p=OUT/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes((BASE/n).read_bytes())
 # Apply exactly the independently measured63 tone/colour transform.
 tuning=ROOT/"tuning/rear-ov13858-measured-v1.json";fit=json.loads(tuning.read_text())
 curve=fit["tone_curve_12bit"];q=fit["cst12_q10_GBR"]
 assert len(curve)==257 and curve[0]==0 and curve[-1]==4095 and all(0<=a<=b<=4095 for a,b in zip(curve,curve[1:]))
 assert len(q)==3 and all(len(row)==3 and all(type(v)==int and abs(v)<=4095 for v in row) for row in q)
 p=OUT/"camss/camss-e007t-gamma151.inc";s=p.read_text();start=s.index("e007t_gamma_curve[E007T_GAMMA_SAMPLES] = {");a=s.index("{",start)+1;b=s.index("};",a)
 rows=[", ".join(str(v) for v in curve[i:i+12]) for i in range(0,257,12)]
 p.write_text(s[:a]+"\n\t"+",\n\t".join(rows)+",\n"+s[b:])
 m="".join(f"c->m{r}{c}={q[r][c]};" for r in range(3) for c in range(3))
 replace(OUT/"camss/native-rear-startup-iq.inc","\twork->input = *input;\n","\twork->input = *input;\n\t{ /* Independently measured63 colour matrix. */\n\t\tunsigned int q;\n\t\tfor(q=0;q<E007Y_STARTUP_PACKETS;q++){\n\t\t\tstruct e006r_cst12_state *c=&work->input.packet[q].cst;\n\t\t\t"+m+"\n\t\t}\n\t}\n")
 changed=[]
 for n in base["staged_sources"]:
  p=OUT/n;s=p.read_text()
  t=s.replace("identity=60","identity=66").replace("rear-generation-20261007-60.bin","rear-generation-20261010-66.bin")
  if t!=s:p.write_text(t);changed.append(n)
 (OUT/"camss/native-rear-stats.h").write_bytes((HERE/"native-rear-aec-v2.h").read_bytes())
 changed+=["camss/native-rear-stats.h","camss/camss-e007t-gamma151.inc","camss/native-rear-startup-iq.inc"]
 # Every non-declared source must remain byte-identical to the verified baseline.
 for n,h in base["staged_sources"].items():
  if n not in changed:assert sha(OUT/n)==h,n
 result=dict(base);result.update(status="BUILDING",base_verified_source_stage=str(BASE),base_source_head=HEAD,declared_changed_files=changed,tuning_sha256=sha(tuning),statistics_wire_format="QXA2",statistics_version=2,statistics_wire_bytes=82016,statistics_active_AEC_bytes=81920,statistics_extra_planes_absent=True,all_DMA_lifetime_and_stop_sources_byte_identical=True,hardware_access=False,installed=False)
 try:
  for name in ["camss","imx681","ov13858"]:
   with (OUT/(name+"-compile.log")).open("x") as log:
    subprocess.run(["make","-C",PROJECT/"02-kernel/e003i-front-production-src","O="+str(PROJECT/"02-kernel/build-runtime-v4-headers-20260826"),"M="+str(OUT/name),"CONFIG_VIDEO_QCOM_CAMSS=m","W=1","KCFLAGS=-Werror","-j","4","modules"],stdout=log,stderr=subprocess.STDOUT,check=True)
   assert "warning:" not in (OUT/(name+"-compile.log")).read_text().lower()
  result["modules"]={}
  for name in ["camss","imx681","ov13858"]:
   relative=name+"/"+("qcom-camss" if name=="camss" else name)+".ko"
   vermagic=subprocess.check_output(["modinfo","-F","vermagic",OUT/relative],text=True).strip()
   result["modules"][relative]=dict(sha256=sha(OUT/relative),vermagic=vermagic)
  result["staged_sources"]={n:sha(OUT/n) for n in base["staged_sources"]}
  result.update(status="PASS_REAR_GENERATION_SOURCE_BUILD_NOT_INSTALLED",compiler_warnings=0)
 except Exception as e:
  result.update(status="FAIL_COMPACT_AEC66_SOURCE_BUILD",error=str(e));raise
 finally:(OUT/"build-result.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:result[k] for k in ["status","declared_changed_files","statistics_wire_bytes","hardware_access"]}))
if __name__=="__main__":main()
