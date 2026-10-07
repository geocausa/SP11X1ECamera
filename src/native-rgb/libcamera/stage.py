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

def stage(source, destination, front_pipeline=False):
    manifest = json.loads((HERE / "sources.json").read_text())
    commit = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if commit != manifest["libcamera_commit"]:
        raise ValueError("libcamera base commit changed")
    for name, expected in manifest["libcamera_inputs"].items():
        if sha(source / name) != expected:
            raise ValueError("libcamera source drift: " + name)
    if front_pipeline:
        for name, expected in manifest["pipeline_inputs"].items():
            if sha(source / name) != expected:
                raise ValueError("pinned pipeline source drift: " + name)
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
    # The retained C zero initializer triggers C++ missing-field warnings.
    # Spell out both members in the staged copy; arithmetic stays unchanged.
    replace(libipa / "weight-quad-producer.h",
            "struct e011al_weight_quad_output v={0};",
            "struct e011al_weight_quad_output v={{0,0,0},0};")
    # libcamera enables GNU math declarations, including fadd/fsub/fmul.
    # Namespace the retained file's private helpers without changing arithmetic.
    stats = libipa / "native-stats3a.c"
    text = stats.read_text()
    for name in ("fadd", "fsub", "fmul"):
        if not re.search(r"static float " + name + r"\(", text):
            raise ValueError("statistics helper anchor missing: " + name)
        text = re.sub(r"\b" + name + r"\b", "camss_x1e_" + name, text)
    stats.write_text(text)
    for name in ("camss_x1e_helpers.h", "camss_x1e_helpers.cpp", "../native-front-stats.h", "../native-front-params.h"):
        shutil.copy2(HERE / name, libipa / Path(name).name)
    shutil.copy2(HERE / "camss-x1e-controls.h", libipa / "camss-x1e-controls.h")
    shutil.copy2(HERE / "camss-x1e-controls-test.cpp", destination / "test/ipa/libipa/camss-x1e-controls-test.cpp")
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
            "libipa_test = [\n    {'name': 'camss-x1e-controls', 'sources': ['camss-x1e-controls-test.cpp']},\n    {'name': 'camss-x1e-helpers', "
            "'sources': ['camss-x1e-helpers-test.cpp']},")
    if front_pipeline:
        for name, expected in manifest["pipeline_inputs"].items():
            if sha(destination / name) != expected:
                raise ValueError("cloned pipeline source differs: " + name)
        pipeline = destination / "src/libcamera/pipeline/camss-x1e"
        pipeline.mkdir()
        shutil.copy2(HERE / "camss-x1e.cpp", pipeline / "camss-x1e.cpp")
        shutil.copy2(HERE / "camss-x1e-controls.h", pipeline / "camss-x1e-controls.h")
        for name in ("native-front-params.h", "native-front-stats.h"):
            shutil.copy2(HERE.parent / name, pipeline / name)
        (pipeline / "meson.build").write_text(
            "# SPDX-License-Identifier: CC0-1.0\nlibcamera_internal_sources += files('camss-x1e.cpp')\n")
        replace(destination / "meson_options.txt", "            'all',",
                "            'camss-x1e',\n            'all',")
        replace(destination / "meson.build", "pipelines_support = {",
                "pipelines_support = {\n    'camss-x1e': ['aarch64'],")
        shutil.copy2(HERE / "camss_x1e.mojom", destination / "include/libcamera/ipa/camss_x1e.mojom")
        replace(destination / "include/libcamera/ipa/meson.build",
                "pipeline_ipa_mojom_mapping = {",
                "pipeline_ipa_mojom_mapping = {\n    'camss-x1e': 'camss_x1e.mojom',")
        replace(destination / "meson_options.txt",
                "choices : ['ipu3', 'mali-c55', 'rkisp1', 'rpi/pisp', 'rpi/vc4', 'simple',",
                "choices : ['camss-x1e', 'ipu3', 'mali-c55', 'rkisp1', 'rpi/pisp', 'rpi/vc4', 'simple',")
        ipa = destination / "src/ipa/camss-x1e"
        ipa.mkdir()
        shutil.copy2(HERE / "camss-x1e-ipa-test.cpp",
                     destination / "test/ipa/libipa/camss-x1e-ipa-test.cpp")
        replace(destination / "test/ipa/libipa/meson.build", "libipa_test = [",
                "libipa_test = [\n    {'name': 'camss-x1e-ipa', 'sources': ['camss-x1e-ipa-test.cpp']},")

        shutil.copy2(HERE / "camss-x1e-ipa.cpp", ipa / "camss-x1e.cpp")
        shutil.copy2(HERE / "camss-x1e-ipa-meson.build", ipa / "meson.build")

    subprocess.run(["git", "-C", str(destination), "diff", "--check"], check=True)
    paths = list(manifest["libcamera_inputs"])
    paths += ["src/ipa/libipa/" + Path(n).name for n in manifest["camera_sources"]]
    paths += ["src/ipa/libipa/camss-x1e-controls.h",
              "test/ipa/libipa/camss-x1e-controls-test.cpp",
              "src/ipa/libipa/camss_x1e_helpers.h",
              "src/ipa/libipa/camss_x1e_helpers.cpp",
              "src/ipa/libipa/native-front-stats.h",
              "src/ipa/libipa/native-front-params.h",
              "test/ipa/libipa/camss-x1e-helpers-test.cpp"]
    if front_pipeline:
        paths += list(manifest["pipeline_inputs"])
        paths += ["test/ipa/libipa/camss-x1e-ipa-test.cpp",
                  "include/libcamera/ipa/camss_x1e.mojom",
                  "src/ipa/camss-x1e/camss-x1e.cpp",
                  "src/ipa/camss-x1e/meson.build"]

        paths += ["src/libcamera/pipeline/camss-x1e/" + name for name in
                  ("camss-x1e.cpp", "camss-x1e-controls.h", "native-front-params.h", "native-front-stats.h", "meson.build")]
    result = {
        "status": ("STAGED_LIBCAMERA_NATIVE_FRONT_PIPELINE_NOT_INSTALLED"
                   if front_pipeline else "STAGED_LIBCAMERA_HELPERS_NOT_INSTALLED"),
        "libcamera_commit": commit,
        "inputs": manifest,
        "private_stats_helpers_prefixed": ["fadd", "fsub", "fmul"],
        "staged_sources": {n: sha(destination / n) for n in sorted(paths)},
        "new_camera_daemon": False,
        "pipeline_runtime_implemented": front_pipeline,
        "pipeline_hardware_proven": False,
        "front_pipeline_trial_staged": front_pipeline,
        "pipeline_control_scope": "standard delayed manual requests; actual IPA meters shared statistics and supplies typed defaults",
        "DelayedControls_runtime_integrated": front_pipeline,
        "DelayedControls_hardware_qualified": False,
        "ipa_runtime_implemented": front_pipeline,
        "automatic_feedback_enabled": False,
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
