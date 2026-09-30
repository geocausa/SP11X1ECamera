#!/usr/bin/env python3
"""Fresh one-use isolated ARM64 weight/quad binder build. Never install/load."""
from pathlib import Path
import hashlib,json,shutil,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011aj-rear-bg-geometry-threshold-build")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011al-rear-bg-weight-quad-build")
HEADERS=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826")
PARENT="c8742eb070b69a5a35f67c0d5fd9484ab2962ab7"
SOURCE_SHA="67efc466cab013ffd0063c17d26d234d8d272096236e808d56d437e12d20eeea"
def main():
    subprocess.run(["bash","tools/camera-overlap-guard.sh","--require-golden","--require-no-camera-process",
        "--expect-head",PARENT,"--expect-origin",PARENT],cwd=ROOT,check=True)
    assert not BUILD.exists(),"consumed build identity: audit, never rerun"
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
    source=HERE/"camss-e011al-startup-weight-quad-bind.inc";shutil.copy2(source,BUILD/source.name)
    p=BUILD/"camss-vfe-680.c";s=p.read_text()
    needle='#include "camss-e011aj-startup-bg-bind.inc"'
    assert s.count(needle)==1
    p.write_text(s.replace(needle,needle+'\n#include "camss-e011al-startup-weight-quad-bind.inc"'))
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
    required=["e011al_rear_bind_startup_weight_quad","e011al_rear_weight_quad_recipe",
        "e011aj_rear_bind_startup_bg","e011ai_rear_bind_startup_scalar",
        "e011ah_rear_bind_request_af_roi","e011ag_rear_compose_startup"]
    assert all(x in symbols for x in required)
    assert not (BUILD/"weight-quad-producer.h").exists()
    safe={"experiment":"E011AL","status":"PASS_ISOLATED_ARM64_W1_BUILD",
        "parent_git_revision":PARENT,"base_vfe_source_sha256":SOURCE_SHA,
        "weight_quad_binder_source_sha256":hashlib.sha256((BUILD/source.name).read_bytes()).hexdigest(),
        "vfe_source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "module_sha256":hashlib.sha256(module.read_bytes()).hexdigest(),"module_bytes":module.stat().st_size,
        "warnings":0,"vermagic":vermagic,"retained_symbols":required,
        "integer_only_binder":True,"installed":False,"loaded":False,
        "hardware_actions":False,"native_rear_runtime_allowed":False}
    (HERE/"BUILD-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
