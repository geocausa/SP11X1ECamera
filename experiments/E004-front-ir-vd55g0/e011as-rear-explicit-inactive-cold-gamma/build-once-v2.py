#!/usr/bin/env python3
"""Fresh one-use isolated ARM64 explicit inactive cold gamma build. Never install/load."""
from pathlib import Path
import hashlib,json,shutil,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011ar-rear-packet-isolated-runner-build")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011as-rear-explicit-inactive-cold-gamma-build-v2")
HEADERS=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826")
PARENT="e73c4ff38221a28b4bf7995581e756a1f607a9a1"
SOURCE_SHA="56f2e69bde9d13742b88136b6384dec6eab3479ec36c9d33bafd341976e28897"
def main():
    subprocess.run(["bash","tools/camera-overlap-guard.sh","--require-golden","--require-no-camera-process",
        "--expect-head",PARENT,"--expect-origin",PARENT],cwd=ROOT,check=True)
    assert not BUILD.exists(),"consumed build identity: audit, never rerun"
    assert hashlib.sha256((BASE/"camss-vfe-680.c").read_bytes()).hexdigest()==SOURCE_SHA
    evidence=json.loads((HERE.parent/"e011ar-rear-packet-isolated-runner/INTEGRATION-SAFE.json").read_text())
    for lock in evidence["source_locks"]:
        assert hashlib.sha256((ROOT/lock["path"]).read_bytes()).hexdigest()==lock["sha256"]
    BUILD.mkdir()
    for p in BASE.iterdir():
        if p.is_file() and (p.suffix in (".c",".h",".inc",".S") or p.name in ("Makefile","Kbuild")):
            shutil.copy2(p,BUILD/p.name)
    for lock in evidence["source_locks"]:
        p=ROOT/lock["path"]
        if p.suffix==".inc" and (BUILD/p.name).exists():
            assert (BUILD/p.name).read_bytes()==p.read_bytes(),"base provider drift"
    manifest=json.loads((HERE/"PROVIDERS.json").read_text())
    p=BUILD/"camss-vfe-680.c";s=p.read_text()
    for item in manifest:
        original=ROOT/item["parent_path"];new=ROOT/item["path"]
        assert hashlib.sha256(original.read_bytes()).hexdigest()==item["parent_sha256"]
        assert hashlib.sha256(new.read_bytes()).hexdigest()==item["sha256"]
        # E008t is a historical host-only seed, absent from the kernel base.
        if item["old_name"]=="camss-vfe-e008t-rear-bf-semantic.inc":
            continue
        assert (BASE/item["old_name"]).read_bytes()==original.read_bytes()
        shutil.copy2(new,BUILD/item["new_name"])
        needle='#include "'+item["old_name"]+'"'
        assert s.count(needle)==1
        s=s.replace(needle,'#include "'+item["new_name"]+'"')
    helper="camss-e011as-cold-gamma-policy.inc"
    shutil.copy2(HERE/helper,BUILD/helper)
    needle='#include "camss-e011am-startup-rs-bind.inc"'
    assert s.count(needle)==1
    s=s.replace(needle,needle+'\n#include "'+helper+'"')
    p.write_text(s)
    log=BUILD/"BUILD.log"
    with log.open("w") as f:
        result=subprocess.run(["make","-C",str(HEADERS),"M="+str(BUILD),"W=1","-j4"],stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text()
    if result.returncode or "warning:" in text or "error:" in text:
        print("Private build diagnostic: "+str(log));raise RuntimeError("isolated W=1 build failed")
    module=BUILD/"qcom-camss.ko"
    vermagic=subprocess.check_output(["modinfo","-F","vermagic",str(module)],text=True).strip()
    assert vermagic=="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"
    symbols=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(module)],text=True)
    required=["e011ar_rear_run_once_unreachable","e011ar_rear_run_unreachable",
        "e011ar_rear_single_use_recipe","e011ar_rear_runner_recipe",
        "e011ar_rear_runtime_authorization","e011ar_rear_once_runtime_authorization",
        "e011am_rear_bind_startup_rs","e011ag_rear_compose_startup",
        "e011as_rear_mark_cold_gamma_inactive","e011as_rear_gamma_runtime_authorization"]
    assert all(x in symbols for x in required)
    assert not (BUILD/"rs-producer.h").exists()
    safe={"experiment":"E011AS","status":"PASS_ISOLATED_ARM64_W1_BUILD",
        "parent_git_revision":PARENT,"base_vfe_source_sha256":SOURCE_SHA,
        "provider_derivatives":manifest,
        "host_only_seed_not_in_kernel":"camss-vfe-e008t-rear-bf-semantic.inc",
        "cold_gamma_policy_source_sha256":hashlib.sha256((HERE/helper).read_bytes()).hexdigest(),
        "vfe_source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "module_sha256":hashlib.sha256(module.read_bytes()).hexdigest(),"module_bytes":module.stat().st_size,
        "warnings":0,"vermagic":vermagic,"retained_symbols":required,
        "explicit_inactive_gamma":True,"installed":False,"loaded":False,
        "hardware_actions":False,"native_rear_runtime_allowed":False}
    (HERE/"BUILD-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
