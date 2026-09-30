#!/usr/bin/env python3
"""Revalidate ownership audit and unchanged full offline provider parity."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json
HERE=Path(__file__).resolve().parent;EX=HERE.parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    am=EX/"e011am-rear-rs-full-startup-integration"
    locked=[am/"INTEGRATION-SAFE.json",am/"ARITHMETIC-SAFE.json"]
    hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in locked}
    with contextlib.redirect_stdout(io.StringIO()):
        load("e011an_origin",HERE/"native-private.py").main()
        load("e011an_regression",am/"verify-private.py").main()
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==v for p,v in hashes.items())
    prior=json.loads((am/"INTEGRATION-SAFE.json").read_text())
    assert prior["remaining_mismatches_by_phase"]==[0,0,0,0]
    report={"experiment":"E011AN","status":"PASS_ORIGIN_OWNERSHIP_AUDIT_AND_UNCHANGED_FULL_PARITY",
      "parent_git_revision":"a3c81299111f8c1f46c9a0f2a0531293cd7a2ea9",
      "compiler_runs":prior["compiler_runs"],"remaining_mismatches_by_phase":[0,0,0,0],
      "prior_reports_unchanged":True,"original_calls":184,"cold_value_policy_closed":False,
      "new_kernel_build":False,"runtime_actions_performed":False,"native_rear_runtime_allowed":False,
      "source_locks":[{"path":str(p.relative_to(HERE.parents[2])),"sha256":v} for p,v in hashes.items()],
      "next_boundary":"AWB algorithm GetParam selector12; AEC Usecase statistics producer; policy inputs remain open"}
    (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report))
if __name__=="__main__":main()
