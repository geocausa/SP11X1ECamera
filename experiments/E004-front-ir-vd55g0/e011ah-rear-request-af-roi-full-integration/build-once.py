#!/usr/bin/env python3
"""Fresh one-use isolated ARM64 compile. Never installs, loads or boots it."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011ag-rear-full-provider-startup-build")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011ah-rear-request-af-roi-build")
HEADERS=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826")
PARENT="2f35a08454e7322ee29db88143d216a4b444351d"
SOURCE_SHA="c5032fcde6d806440576351004e4ab09c7f1043877ba0ea320c348c07f66bf11"
def main():
    subprocess.run(["bash","tools/camera-overlap-guard.sh","--require-golden","--require-no-camera-process",
        "--expect-head",PARENT,"--expect-origin",PARENT],cwd=ROOT,check=True)
    assert not BUILD.exists(),"identity consumed: audit it; never rerun"
    assert hashlib.sha256((BASE/"camss-vfe-680.c").read_bytes()).hexdigest()==SOURCE_SHA
    evidence=json.loads((HERE/"INTEGRATION-SAFE.json").read_text())
    for lock in evidence["source_locks"]:
        p=ROOT/lock["path"]
        assert hashlib.sha256(p.read_bytes()).hexdigest()==lock["sha256"]
    BUILD.mkdir()
    for p in BASE.iterdir():
        if p.is_file() and (p.suffix in (".c",".h",".inc",".S") or p.name in ("Makefile","Kbuild")):
            shutil.copy2(p,BUILD/p.name)
    for lock in evidence["source_locks"]:
        p=ROOT/lock["path"]
        if p.suffix==".inc" and (BUILD/p.name).exists():
            assert (BUILD/p.name).read_bytes()==p.read_bytes(),"base provider drift"
    shutil.copy2(HERE/"camss-e011ah-request-af-roi.inc",BUILD/"camss-e011ah-request-af-roi.inc")
    p=BUILD/"camss-vfe-680.c";s=p.read_text()
    needle='#include "camss-e011ag-startup-compose.inc"'
    assert s.count(needle)==1
    p.write_text(s.replace(needle,needle+'\n#include "camss-e011ah-request-af-roi.inc"'))
    log=BUILD/"BUILD.log"
    with log.open("w") as f:
        result=subprocess.run(["make","-C",str(HEADERS),"M="+str(BUILD),"W=1","-j4"],stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text()
    if result.returncode or "warning:" in text or "error:" in text:
        print("Build diagnostic remains privately at "+str(log))
        raise RuntimeError("isolated W=1 build failed")
    module=BUILD/"qcom-camss.ko"
    vermagic=subprocess.check_output(["modinfo","-F","vermagic",str(module)],text=True).strip()
    assert vermagic=="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"
    symbols=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(module)],text=True)
    required=["e011ah_rear_bind_request_af_roi","e011ah_rear_af_roi_recipe",
        "e011ag_rear_compose_startup","e011ag_rear_startup_recipe"]
    assert all(x in symbols for x in required)
    report={"experiment":"E011AH","status":"PASS_ISOLATED_ARM64_W1_BUILD",
        "parent_git_revision":PARENT,"base_vfe_source_sha256":SOURCE_SHA,
        "af_roi_source_sha256":hashlib.sha256((BUILD/"camss-e011ah-request-af-roi.inc").read_bytes()).hexdigest(),
        "vfe_source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "module_sha256":hashlib.sha256(module.read_bytes()).hexdigest(),"module_bytes":module.stat().st_size,
        "vermagic":vermagic,"warnings":0,"retained_symbols":required,
        "installed":False,"loaded":False,"hardware_actions":False,"native_rear_runtime_allowed":False}
    (HERE/"BUILD-SAFE.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
