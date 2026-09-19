#!/usr/bin/env python3
"""Build staged E004fv + E004fz source in a disposable kernel build tree."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
from generate_patch import PATCH,base_after_0003,produce,require

def run(argv,timeout=150):
    p=subprocess.run([str(x) for x in argv],text=True,capture_output=True,
                     timeout=timeout,check=False)
    require(p.returncode==0,"isolated build error: "+p.stderr[-1700:]+p.stdout[-600:])
    return p

def main():
    first, second, delta=produce()
    require(PATCH.is_file() and PATCH.read_text()==delta,"E004fz patch bytes drift")
    with TemporaryDirectory(prefix="sp11-e004fz-uninstalled-kmod-") as tmp:
        root=Path(tmp)
        src=root/"drivers/leds/flash/leds-qcom-flash.c"
        src.parent.mkdir(parents=True)
        src.write_text(first)
        run(["patch","--batch","-s","-d",root,"-p1","-i",PATCH.resolve()],timeout=20)
        require(src.read_text()==second,"kernel source patch roundtrip mismatch")
        module=root/"module"
        module.mkdir()
        (module/"leds-qcom-flash.c").write_text(second)
        (module/"Makefile").write_text("obj-m += leds-qcom-flash.o\n")
        release=run(["uname","-r"],timeout=10).stdout.strip()
        headers=Path("/lib/modules")/release/"build"
        require(headers.exists(),"Golden kernel headers unavailable")
        run(["make","-s","-C",headers,"M="+str(module),"W=1","-j2","modules"],timeout=150)
        ko=module/"leds-qcom-flash.ko"
        require(ko.is_file() and ko.stat().st_size>1000,"kernel module build missing")
        print("E004FZ_ISOLATED_GOLDEN_KERNEL_BUILD=PASS W=1")
        print("DRIVER_INSTALLED=NO MODULE_LOADED=NO EMITTER=OFF")
        print("PATCHED_SOURCE_SHA256="+sha256(second.encode()).hexdigest())

if __name__=="__main__":
    main()
