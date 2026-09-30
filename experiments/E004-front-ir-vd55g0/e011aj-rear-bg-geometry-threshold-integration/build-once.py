#!/usr/bin/env python3
"""Fresh one-use isolated ARM64 kernel BG geometry/threshold binder build; never load/install."""
from pathlib import Path
import hashlib,json,shutil,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011ai-rear-neutral-scalar-build")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011aj-rear-bg-geometry-threshold-build")
HEADERS=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826")
PARENT="c5fab3f3066d69833aa02a23bc801bee47c10cf2"
SOURCE_SHA="e8887ab9989cd0280cd76fcf2e214d591f7c3a29362cf14eae59f8ca4ae8d1c4"
def main():
    subprocess.run(["bash","tools/camera-overlap-guard.sh","--require-golden","--require-no-camera-process",
        "--expect-head",PARENT,"--expect-origin",PARENT],cwd=ROOT,check=True)
    assert not BUILD.exists(),"consumed identity: audit; never rerun"
    assert hashlib.sha256((BASE/"camss-vfe-680.c").read_bytes()).hexdigest()==SOURCE_SHA
    evidence=json.loads((HERE/"INTEGRATION-SAFE.json").read_text())
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
    source=HERE/"camss-e011aj-startup-bg-bind.inc"
    shutil.copy2(source,BUILD/source.name)
    p=BUILD/"camss-vfe-680.c";s=p.read_text()
    needle='#include "camss-e011ai-startup-scalar-bind.inc"'
    assert s.count(needle)==1
    p.write_text(s.replace(needle,needle+'\n#include "camss-e011aj-startup-bg-bind.inc"'))
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
    required=["e011aj_rear_bind_startup_bg","e011aj_rear_bg_recipe",
        "e011ai_rear_bind_startup_scalar",
        "e011ah_rear_bind_request_af_roi","e011ag_rear_compose_startup"]
    assert all(x in symbols for x in required)
    assert not (BUILD/"bg-producer.h").exists(),"user-space producer must not enter kernel"
    safe={"experiment":"E011AJ","status":"PASS_ISOLATED_ARM64_W1_BUILD",
        "parent_git_revision":PARENT,"base_vfe_source_sha256":SOURCE_SHA,
        "bg_binder_source_sha256":hashlib.sha256((BUILD/source.name).read_bytes()).hexdigest(),
        "vfe_source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "module_sha256":hashlib.sha256(module.read_bytes()).hexdigest(),"module_bytes":module.stat().st_size,
        "warnings":0,"vermagic":vermagic,"retained_symbols":required,
        "user_space_float_producer_in_kernel":False,"installed":False,"loaded":False,
        "hardware_actions":False,"native_rear_runtime_allowed":False}
    (HERE/"BUILD-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
