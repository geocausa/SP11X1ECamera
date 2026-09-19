#!/usr/bin/env python3
"""Reproducible isolated kernel-module build of the UNINSTALLED E004fv patch."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import subprocess

from generate_patch import PATCH, source_pair

def run(command, timeout=130):
    r = subprocess.run([str(part) for part in command],
                       capture_output=True, text=True, check=False, timeout=timeout)
    if r.returncode:
        raise ValueError("E004FV_OFFLINE_BUILD_FAIL " + r.stderr[-1500:] + r.stdout[-600:])
    return r

def main():
    original, patched = source_pair()
    with TemporaryDirectory(prefix="sp11-e004fv-isolated-kmod-") as temporary:
        root = Path(temporary)
        source = root / "drivers/leds/flash/leds-qcom-flash.c"
        source.parent.mkdir(parents=True)
        source.write_text(original)
        run(["patch", "-s", "-d", root, "-p1", "-i", PATCH.resolve()], timeout=25)
        if source.read_text() != patched:
            raise ValueError("E004FV_SOURCE_AFTER_PATCH_MISMATCH")
        module = root / "module"
        module.mkdir()
        (module / "leds-qcom-flash.c").write_text(patched)
        (module / "Makefile").write_text("obj-m += leds-qcom-flash.o\n")
        kernel_release = run(["uname", "-r"], timeout=10).stdout.strip()
        anchor = Path("/lib/modules") / kernel_release / "build"
        if not anchor.exists():
            raise ValueError("GOLDEN_KERNEL_BUILD_ANCHOR_NOT_FOUND")
        run(["make", "-s", "-C", anchor, "M=" + str(module),
             "W=1", "-j2", "modules"])
        ko = module / "leds-qcom-flash.ko"
        if not ko.is_file() or ko.stat().st_size < 1000:
            raise ValueError("ISOLATED_FLASH_MODULE_NOT_BUILT")
        print("E004FV_ISOLATED_KERNEL_MODULE_BUILD=PASS W=1 MODULE_UNINSTALLED=YES")
        print("SOURCE_SHA256=" + sha256(patched.encode()).hexdigest())

if __name__ == "__main__":
    main()
