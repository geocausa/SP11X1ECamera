#!/usr/bin/env python3
"""Stage the retained native camera algorithms inside an isolated libcamera tree."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def replace(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise ValueError("source anchor missing/repeated: " + str(path))
    path.write_text(text.replace(old, new, 1))

def stage(source, destination):
    manifest = json.loads((HERE / "sources.json").read_text())
    commit = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if commit != manifest["libcamera_commit"]:
        raise ValueError("libcamera base commit changed")
    for name, expected in manifest["libcamera_inputs"].items():
        if sha(source / name) != expected:
            raise ValueError("libcamera source drift: " + name)
    for name, expected in manifest["camera_sources"].items():
        if sha(ROOT / name) != expected:
            raise ValueError("retained algorithm source drift: " + name)
    if destination.exists() or destination.is_relative_to(ROOT):
        raise ValueError("destination must be a fresh directory outside the camera checkout")
    subprocess.run(["git", "clone", "--no-local", "--no-hardlinks",
                    str(source), str(destination)], check=True)
    # Cloning never copies the reference checkout's uncommitted software-ISP edits.
    # Verify the actual files being edited after clone, too.
    for name, expected in manifest["libcamera_inputs"].items():
        if sha(destination / name) != expected:
            raise ValueError("cloned libcamera source differs: " + name)

    names = [Path(name).name for name in manifest["camera_sources"]]
    if len(names) != len(set(names)):
        raise ValueError("retained source basenames collide")
    libipa = destination / "src/ipa/libipa"
    for name in manifest["camera_sources"]:
        shutil.copy2(ROOT / name, libipa / Path(name).name)
    # libcamera enables GNU math declarations, including fadd/fsub/fmul.
    # Namespace the retained file's private helpers without changing arithmetic.
    stats = libipa / "native-stats3a.c"
    text = stats.read_text()
    for name in ("fadd", "fsub", "fmul"):
        if not re.search(r"static float " + name + r"\(", text):
            raise ValueError("statistics helper anchor missing: " + name)
        text = re.sub(r"\b" + name + r"\b", "camss_x1e_" + name, text)
    stats.write_text(text)
    for name in ("camss_x1e_helpers.h", "camss_x1e_helpers.cpp", "../native-front-stats.h"):
        shutil.copy2(HERE / name, libipa / Path(name).name)
    shutil.copy2(HERE / "camss-x1e-helpers-test.cpp",
                 destination / "test/ipa/libipa/camss-x1e-helpers-test.cpp")

    replace(libipa / "camera_sensor_helper.cpp",
            'class CameraSensorHelperImx708 : public CameraSensorHelper',
            (HERE / "imx681-helper.inc").read_text() +
            'class CameraSensorHelperImx708 : public CameraSensorHelper')
    replace(libipa / "meson.build", "libipa_headers = files([",
            "libipa_headers = files([\n    'camss_x1e_helpers.h',")
    replace(libipa / "meson.build", "libipa_sources = files([",
            "libipa_sources = files([\n    'camss_x1e_helpers.cpp',\n"
            "    'native-imx681-control.c',\n    'native-stats3a.c',\n"
            "    'rear-neutral-scalar.c',")
    replace(destination / "test/ipa/libipa/meson.build", "libipa_test = [",
            "libipa_test = [\n    {'name': 'camss-x1e-helpers', "
            "'sources': ['camss-x1e-helpers-test.cpp']},")
    subprocess.run(["git", "-C", str(destination), "diff", "--check"], check=True)
    paths = list(manifest["libcamera_inputs"])
    paths += ["src/ipa/libipa/" + Path(n).name for n in manifest["camera_sources"]]
    paths += ["src/ipa/libipa/camss_x1e_helpers.h",
              "src/ipa/libipa/camss_x1e_helpers.cpp",
              "src/ipa/libipa/native-front-stats.h",
              "test/ipa/libipa/camss-x1e-helpers-test.cpp"]
    result = {
        "status": "STAGED_LIBCAMERA_HELPERS_NOT_INSTALLED",
        "libcamera_commit": commit,
        "inputs": manifest,
        "private_stats_helpers_prefixed": ["fadd", "fsub", "fmul"],
        "staged_sources": {n: sha(destination / n) for n in sorted(paths)},
        "new_camera_daemon": False,
        "pipeline_runtime_implemented": False,
        "kernel_timing_abi_complete": False,
        "native_nv12_proven": False,
    }
    (destination / "native-rgb-source-manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "destination": str(destination),
                      "retained_algorithms": len(manifest["camera_sources"])}, indent=2))
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    stage(args.source.resolve(), args.out.resolve())
