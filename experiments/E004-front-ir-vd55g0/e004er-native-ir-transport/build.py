#!/usr/bin/env python3
"""Build an isolated native IR candidate. Never installs or activates it."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PACKAGE_SHA = "e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794"
FIRMWARE_SHA = "5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel-source", required=True, type=Path)
    parser.add_argument("--kernel-build", required=True, type=Path)
    parser.add_argument("--sensor-package", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        parser.error("output already exists; use a fresh directory")
    if sha(args.sensor_package) != PACKAGE_SHA:
        parser.error("sensor package identity differs from the verified board")
    out.mkdir(parents=True)
    (out / "logs").mkdir()
    (out / "modules").mkdir()
    native = REPO / "src/front-ir-vd55g0/native"
    sources = {}
    for name, source in (("sensor", native),
                         ("camss", REPO / "src/front-imx681/kernel/camss")):
        work = out / "source" / name
        shutil.copytree(source, work, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for path in source.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                sources[str(path.relative_to(REPO))] = sha(path)
        mapping = f"-ffile-prefix-map={work}=/usr/src/sp11-native-ir/{name} -fdebug-prefix-map={work}=/usr/src/sp11-native-ir/{name}"
        proc = subprocess.run(
            ["make", "-C", str(args.kernel_source), "O=" + str(args.kernel_build),
             "M=" + str(work), "W=1", "KCFLAGS=" + mapping,
             "KCPPFLAGS=" + mapping, "modules", "-j4"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out / "logs" / (name + ".txt")).write_text(proc.stdout)
        if proc.returncode:
            sys.exit(proc.stdout)
        module = "sp11-vd55g0-native.ko" if name == "sensor" else "qcom-camss.ko"
        shutil.copy2(work / module, out / "modules" / module)

    # Firmware remains a local, separately supplied runtime dependency.
    sys.path.insert(0, str(REPO / "experiments/E004-front-ir-vd55g0/e004a-windows-authority"))
    from extract_windows_vd55g0 import extract_patch_bytes
    firmware = extract_patch_bytes(args.sensor_package)
    if len(firmware) != 552 or hashlib.sha256(firmware).hexdigest() != FIRMWARE_SHA:
        sys.exit("sensor firmware identity drift")
    fw = out / "firmware/st/vd55g0-sp11-cut1.bin"
    fw.parent.mkdir(parents=True)
    fw.write_bytes(firmware)
    dtb = REPO / "experiments/E004-front-ir-vd55g0/e004o-ir-only-graph-authority/x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb"
    shutil.copy2(dtb, out / "ir-only.dtb")
    sources[str(dtb.relative_to(REPO))] = sha(dtb)
    artifacts = {str(p.relative_to(out)): sha(p) for p in
                 [*sorted((out / "modules").glob("*.ko")), fw, out / "ir-only.dtb"]}
    manifest = {
        "schema": "sp11-native-ir-candidate-v1",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "sources": sources, "artifacts": artifacts,
        "route": "CSIPHY0 -> CSID0 RDI0 -> VFE0 RDI0",
        "format": "Y10P/644x604", "gpio_outputs": "disabled",
        "protected_runtime": False, "hardware_tested": False,
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "BUILD_PASS_NOT_HARDWARE_VALIDATED", "output": str(out),
                      "artifacts": artifacts}, indent=2))


if __name__ == "__main__":
    main()
