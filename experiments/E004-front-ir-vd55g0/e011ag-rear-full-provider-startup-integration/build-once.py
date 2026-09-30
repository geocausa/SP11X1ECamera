#!/usr/bin/env python3
"""One-use isolated ARM64 CAMSS compile; never installs or loads the module."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e008o-rear-packet-semantic-state-contract-build")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e011ag-rear-full-provider-startup-build")
HEADERS=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826")
PARENT="361518ec4aca187cce49f131747ecca89042228b"
SOURCE_SHA="85bf36976b50240d3bcea9df087ddb731dcd8139eede617ebd655b20b7e226ef"
def main():
    subprocess.run(["bash","tools/camera-overlap-guard.sh","--require-golden","--require-no-camera-process",
        "--expect-head",PARENT,"--expect-origin",PARENT],cwd=ROOT,check=True)
    assert not BUILD.exists(),"build identity already consumed; audit, never reuse"
    assert hashlib.sha256((BASE/"camss-vfe-680.c").read_bytes()).hexdigest()==SOURCE_SHA
    BUILD.mkdir()
    for p in BASE.iterdir():
        if p.is_file() and (p.suffix in (".c",".h",".inc",".S") or p.name in ("Makefile","Kbuild")):
            shutil.copy2(p,BUILD/p.name)
    spec=importlib.util.spec_from_file_location("e011ag_includes",HERE/"verify-private.py")
    driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
    for p in driver.includes():
        if (BUILD/p.name).exists():
            assert (BUILD/p.name).read_bytes()==p.read_bytes(),"base provider drift"
        shutil.copy2(p,BUILD/p.name)
    shutil.copy2(HERE/"camss-e011ag-startup-compose.inc",BUILD/"camss-e011ag-startup-compose.inc")
    p=BUILD/"camss-vfe-680.c";s=p.read_text()
    needle='#include "camss-vfe-e008o-rear-semantic-state.inc"'
    assert s.count(needle)==1
    extra='\n#include "camss-e011ae-rear-startup-bpc-bind.inc"\n#include "camss-e011z-rear-startup-adaptive-bind.inc"\n#include "camss-e011ag-startup-compose.inc"'
    p.write_text(s.replace(needle,needle+extra))
    log=BUILD/"BUILD.log"
    with log.open("w") as f:
        result=subprocess.run(["make","-C",str(HEADERS),"M="+str(BUILD),"W=1","-j4"],stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text()
    if result.returncode or "warning:" in text or "error:" in text:
        print(text[-14000:]);raise RuntimeError("isolated W=1 build failed")
    module=BUILD/"qcom-camss.ko"
    vermagic=subprocess.check_output(["modinfo","-F","vermagic",str(module)],text=True).strip()
    assert vermagic=="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"
    symbols=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(module)],text=True)
    required=["e011ag_rear_compose_startup","e011ag_rear_startup_recipe"]
    assert all(x in symbols for x in required)
    report={"experiment":"E011AG","status":"PASS_ISOLATED_ARM64_W1_BUILD",
        "parent_git_revision":PARENT,"base_vfe_source_sha256":SOURCE_SHA,
        "composer_source_sha256":hashlib.sha256((BUILD/"camss-e011ag-startup-compose.inc").read_bytes()).hexdigest(),
        "module_sha256":hashlib.sha256(module.read_bytes()).hexdigest(),"module_bytes":module.stat().st_size,
        "vermagic":vermagic,"warnings":0,"retained_symbols":required,
        "installed":False,"loaded":False,"hardware_actions":False,"native_rear_runtime_allowed":False}
    (HERE/"BUILD-SAFE.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
