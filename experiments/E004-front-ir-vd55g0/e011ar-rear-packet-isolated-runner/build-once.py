#!/usr/bin/env python3
"""Fresh one-use isolated ARM64 packet-isolated runner build. Never install/load."""
from pathlib import Path
import hashlib,json,shutil,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011am-rear-rs-full-startup-build")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011ar-rear-packet-isolated-runner-build")
HEADERS=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826")
PARENT="a48adb34c012287e8b8dd767cab3e0670ee512be"
SOURCE_SHA="c332268da02adbf17982b699718b5215c777976f2f538c60328be91fdb2e453d"
def main():
    subprocess.run(["bash","tools/camera-overlap-guard.sh","--require-golden","--require-no-camera-process",
        "--expect-head",PARENT,"--expect-origin",PARENT],cwd=ROOT,check=True)
    assert not BUILD.exists(),"consumed build identity: audit, never rerun"
    assert hashlib.sha256((BASE/"camss-vfe-680.c").read_bytes()).hexdigest()==SOURCE_SHA
    evidence=json.loads((HERE.parent/"e011am-rear-rs-full-startup-integration/INTEGRATION-SAFE.json").read_text())
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
    files=("camss-vfe-e011ar-rear-runner.inc","camss-vfe-e011ar-rear-single-use.inc")
    for name in files: shutil.copy2(HERE/name,BUILD/name)
    p=BUILD/"camss-vfe-680.c";s=p.read_text()
    needle='#include "camss-e011am-startup-rs-bind.inc"'
    assert s.count(needle)==1
    p.write_text(s.replace(needle,needle+"\n"+"\n".join('#include "'+name+'"' for name in files)))
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
        "e011am_rear_bind_startup_rs","e011ag_rear_compose_startup"]
    assert all(x in symbols for x in required)
    assert not (BUILD/"rs-producer.h").exists()
    safe={"experiment":"E011AR","status":"PASS_ISOLATED_ARM64_W1_BUILD",
        "parent_git_revision":PARENT,"base_vfe_source_sha256":SOURCE_SHA,
        "runner_source_sha256":hashlib.sha256((BUILD/files[0]).read_bytes()).hexdigest(),
        "wrapper_source_sha256":hashlib.sha256((BUILD/files[1]).read_bytes()).hexdigest(),
        "vfe_source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "module_sha256":hashlib.sha256(module.read_bytes()).hexdigest(),"module_bytes":module.stat().st_size,
        "warnings":0,"vermagic":vermagic,"retained_symbols":required,
        "packet_isolated_runner":True,"installed":False,"loaded":False,
        "hardware_actions":False,"native_rear_runtime_allowed":False}
    (HERE/"BUILD-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
