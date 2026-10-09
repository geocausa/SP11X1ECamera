#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Check explicit QXA2 admission and exact retained lifecycle parser implementation."""
import ast,copy,json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT.parents[1]
def main():
 base=(HERE.parent/"rear-v4l2/run-rear-ae60.py").read_text()
 actual=(HERE/"run66.py").read_text()
 def functions(source):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
 before=functions(base);after=functions(actual.replace("identity=66","identity=60"))
 unchanged=[n for n in before if n not in ["validate_statistics_join","main"]]
 assert all(before[n]==after[n] for n in unchanged),[n for n in unchanged if before[n]!=after[n]]
 run=runpy.run_path(str(HERE/"run66.py"))
 assert run["IDENTITY"]=="E-NATIVE-REAR-GENERATION-66" and run["MARKER"]=="sp11_camera_native_rear_generation_20261010_66=1"
 f=dict(received=400,joined=400,stream=8,owner=1,failed=0,private_saved=24,decoded_photometry=0,automatic_exposure=1)
 def log(x):return "NATIVE_REAR_STATISTICS_JOIN "+" ".join(f"{k}={v}" for k,v in x.items())
 r=run["validate_statistics_join"](log(f),1)
 assert r["wire_format"]=="QXA2" and r["wire_bytes"]==82016 and r["raw_statistics_exported"] is False
 negative=0
 for key,values in {"received":[399,417],"joined":[399,401],"stream":[0,2**64],"owner":[0,2],"failed":[1],"private_saved":[23,25],"decoded_photometry":[1],"automatic_exposure":[0]}.items():
  for v in values:
   bad=dict(f);bad[key]=v
   try:run["validate_statistics_join"](log(bad),1)
   except RuntimeError:negative+=1;continue
   raise AssertionError((key,v))
 try:run["validate_statistics_join"](log(f)+" unknown=1",1)
 except RuntimeError:negative+=1
 else:raise AssertionError("unknown field accepted")
 assert 'total=82016' in actual and '.qxa2' in actual and '.qxr1' not in actual
 assert 'for session in range(1,2):' in actual
 assert 'camera-native-rear-generation-20261010-66/private-statistics/session-' in (HERE/"camss-x1e-rear-compact66.cpp").read_text()
 result=dict(status="PASS_COMPACT_AEC66_RUNTIME_RECEIPTS_AND_PRESERVED_LIFECYCLE",unchanged_runtime_functions=unchanged,negative_receipt_cases=negative,synthetic_fixture_only=True,hardware_access=False,baseline_runtime_policy_unchanged=True,private_wire_extent=82016)
 report=PROJECT/"02-kernel/native-rgb-rear-generation-20261010-67/runtime-v2-hosted-01.json"
 assert not report.exists();report.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
if __name__=="__main__":main()
