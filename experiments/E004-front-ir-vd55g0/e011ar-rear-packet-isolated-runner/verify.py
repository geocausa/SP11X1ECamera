#!/usr/bin/env python3
"""Host lifecycle fault tests and immutable isolated-module verification."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    reports=[]
    with tempfile.TemporaryDirectory(prefix="e011ar-host-") as tmp:
        for cc in ("gcc","clang"):
            out=Path(tmp)/cc
            subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-fno-omit-frame-pointer","-g",
                "-I"+str(HERE.parent/"e008k-rear-complete-unreachable-runner"),
                str(HERE/"test-runner.c"),"-o",str(out)],check=True)
            report=json.loads(subprocess.check_output([str(out)],text=True))
            reports.append({"compiler":cc,**report})
    assert {k:v for k,v in reports[0].items() if k!="compiler"}=={k:v for k,v in reports[1].items() if k!="compiler"}
    build=json.loads((HERE/"BUILD-SAFE.json").read_text())
    # The project repository is /06-camera/REPO; the build is /02-kernel.
    actual=ROOT.parent.parent/"02-kernel/e011ar-rear-packet-isolated-runner-build"
    module=actual/"qcom-camss.ko"
    assert sha(module)==build["module_sha256"]
    assert sha(actual/"camss-vfe-680.c")==build["vfe_source_sha256"]
    for name,key in (("camss-vfe-e011ar-rear-runner.inc","runner_source_sha256"),
                     ("camss-vfe-e011ar-rear-single-use.inc","wrapper_source_sha256")):
        assert sha(HERE/name)==sha(actual/name)==build[key]
    assert subprocess.check_output(["modinfo","-F","vermagic",str(module)],text=True).strip()==build["vermagic"]
    symbols=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(module)],text=True)
    assert all(name in symbols for name in build["retained_symbols"])
    original=ROOT.parent.parent/"02-kernel/e011am-rear-rs-full-startup-build"
    injected='\n#include "camss-vfe-e011ar-rear-runner.inc"\n#include "camss-vfe-e011ar-rear-single-use.inc"'
    vfe=(actual/"camss-vfe-680.c").read_text()
    assert vfe.count(injected)==1
    assert vfe.replace(injected,"")== (original/"camss-vfe-680.c").read_text()
    for p in original.iterdir():
        if p.is_file() and (p.suffix in (".c",".h",".inc",".S") or p.name in ("Makefile","Kbuild")):
            if p.name not in ("camss-vfe-680.c","qcom-camss.mod.c"):assert sha(p)==sha(actual/p.name)
    log=(actual/"BUILD.log").read_text()
    assert "warning:" not in log and "error:" not in log
    runner=(HERE/"camss-vfe-e011ar-rear-runner.inc").read_text()
    wrapper=(HERE/"camss-vfe-e011ar-rear-single-use.inc").read_text()
    assert "packet_request_id" not in runner and "->regs" not in runner and "->dmi_state" not in runner
    assert "atomic_cmpxchg" in wrapper
    assert "module_param" not in runner+wrapper
    assert runner.count("return -EOPNOTSUPP;")==1 and wrapper.count("return -EOPNOTSUPP;")==1
    safe={"experiment":"E011AR","status":"PASS_HOST_LIFECYCLE_AND_ISOLATED_MODULE",
        "compiler_runs":reports,"base_sources_preserved":True,
        "module_sha256":build["module_sha256"],"module_warnings":0,
        "original_hardware_contracts_mocked_in_host_tests":True,
        "independent_live_DMA_retirement_proven":False,"runtime_authorized":False,
        "source_locks":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in
            (HERE/"test-runner.c",HERE/"verify.py",HERE/"camss-vfe-e011ar-rear-runner.inc",
             HERE/"camss-vfe-e011ar-rear-single-use.inc")]}
    (HERE/"LIFECYCLE-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in safe.items() if k!="source_locks"},indent=2))
if __name__=="__main__":main()
