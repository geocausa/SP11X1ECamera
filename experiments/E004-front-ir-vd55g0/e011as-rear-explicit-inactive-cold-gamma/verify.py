#!/usr/bin/env python3
"""Read-only audit of inactive-gamma source, build and private replay evidence."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BUILD=ROOT.parent.parent/"02-kernel/e011as-rear-explicit-inactive-cold-gamma-build-v2"
BASE=ROOT.parent.parent/"02-kernel/e011ar-rear-packet-isolated-runner-build"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=json.loads((HERE/"PROVIDERS.json").read_text())
    assert len(m)==4
    build=json.loads((HERE/"BUILD-SAFE.json").read_text())
    assert sha(BUILD/"qcom-camss.ko")==build["module_sha256"]
    assert sha(BUILD/"camss-vfe-680.c")==build["vfe_source_sha256"]
    vfe=(BUILD/"camss-vfe-680.c").read_text()
    for x in m:
        original=ROOT/x["parent_path"];new=ROOT/x["path"]
        assert sha(original)==x["parent_sha256"] and sha(new)==x["sha256"]
        assert sha(BUILD/x["new_name"])==x["sha256"]
        assert sha(BASE/x["old_name"])==x["parent_sha256"]
        vfe=vfe.replace('#include "'+x["new_name"]+'"','#include "'+x["old_name"]+'"')
    helper="camss-e011as-cold-gamma-policy.inc"
    assert sha(HERE/helper)==sha(BUILD/helper)==build["cold_gamma_policy_source_sha256"]
    needle='\n#include "'+helper+'"'
    assert vfe.count(needle)==1
    assert vfe.replace(needle,"")==(BASE/"camss-vfe-680.c").read_text()
    for p in BASE.iterdir():
        if p.is_file() and (p.suffix in (".c",".h",".inc",".S") or p.name in ("Makefile","Kbuild")):
            if p.name not in ("camss-vfe-680.c","qcom-camss.mod.c"):
                assert sha(p)==sha(BUILD/p.name)
    assert not (BUILD/"camss-e011as-vfe-e008t-rear-bf-semantic.inc").exists()
    assert subprocess.check_output(["modinfo","-F","vermagic",str(BUILD/"qcom-camss.ko")],text=True).strip()==build["vermagic"]
    symbols=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(BUILD/"qcom-camss.ko")],text=True)
    assert all(x in symbols for x in build["retained_symbols"])
    log=(BUILD/"BUILD.log").read_text()
    assert "warning:" not in log and "error:" not in log
    integration=json.loads((HERE/"INTEGRATION-SAFE.json").read_text())
    for x in integration["source_locks"]:
        assert sha(ROOT/x["path"])==x["sha256"]
    assert integration["remaining_mismatches_by_phase"]==[0,0,0,0]
    assert integration["inactive_cold_gamma_policy_closed"]
    assert integration["cold_gamma_policy_producer_atomic_negative_cases"]==38
    assert all(not x["cold_bf_gamma_emitted"] for x in integration["compiler_runs"])
    safe={"experiment":"E011AS","status":"PASS_IMMUTABLE_DERIVATIVE_BUILD_AND_REPLAY_AUDIT",
        "original_sources_preserved":True,"base_runner_preserved":True,
        "kernel_provider_derivatives":4,"inactive_cold_gamma_policy_closed":True,
        "remaining_mismatches_by_phase":[0,0,0,0],
        "assertions_each":[x["assertions"] for x in integration["compiler_runs"]],
        "module_sha256":build["module_sha256"],"warnings":0,
        "hardware_runtime_proven":False,"native_rear_runtime_allowed":False}
    (HERE/"AUDIT-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
