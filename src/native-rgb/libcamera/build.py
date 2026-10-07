#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build and test native libipa helpers in a fresh checkout; never install."""
import argparse
import json
import subprocess
from pathlib import Path

from stage import ROOT, sha, stage

TESTS = [
    "camss-x1e-helpers", "vd55g0-helper", "control_info", "control_info_map",
    "control_list", "control_value", "fixedpoint", "histogram", "interpolator", "pwl",
]
OPTIONS = [
    "-Dpipelines=uvcvideo,vimc", "-Dipas=vimc", "-Dcam=enabled", "-Dtest=true",
    "-Ddocumentation=disabled", "-Dgstreamer=disabled", "-Dqcam=disabled",
    "-Dv4l2=disabled", "-Dpycamera=disabled", "-Dlibunwind=disabled",
    "-Dtracing=disabled", "-Dlc-compliance=disabled", "-Dwerror=true",
]

def run(arguments, log):
    with log.open("w") as stream:
        subprocess.run([str(a) for a in arguments], stdout=stream,
                       stderr=subprocess.STDOUT, check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    source, out, build = (p.resolve() for p in (args.source, args.out, args.build_dir))
    if args.jobs < 1:
        parser.error("jobs must be positive")
    for path in (out, build):
        if path.exists() or path.is_relative_to(ROOT):
            parser.error("output and build must be fresh directories outside the camera checkout")
    if out.is_relative_to(build) or build.is_relative_to(out):
        parser.error("source and build outputs must be separate directories")
    result = stage(source, out)
    build.mkdir(parents=True)
    result.update(status="BUILD_IN_PROGRESS", build_dir=str(build),
                  meson_options=OPTIONS, installed=False, hardware_access=False)
    report = build / "native-rgb-build-result.json"
    try:
        run(["meson", "setup", build, out, *OPTIONS], build / "native-setup.log")
        run(["meson", "compile", "-C", build, "-j", args.jobs], build / "native-compile.log")
        run(["meson", "test", "-C", build, "--no-rebuild", "--print-errorlogs", *TESTS],
            build / "native-tests.log")
        tests = [json.loads(line) for line in
                 (build / "meson-logs/testlog.json").read_text().splitlines()]
        result["tests"] = [
            {"name": test["name"], "result": test["result"],
             "duration_seconds": test["duration"]}
            for test in tests
        ]
        if len(tests) != len(TESTS):
            raise ValueError("selected test inventory changed")
        native = [test for test in tests if test["name"].endswith(":camss-x1e-helpers")]
        if len(native) != 1 or native[0]["result"] != "OK":
            raise ValueError("native helper test must pass, never skip")
        if any(test["result"] not in ("OK", "SKIP") for test in tests):
            raise ValueError("selected test failed")
        for name, expected in result["staged_sources"].items():
            if sha(out / name) != expected:
                raise ValueError("staged source changed during build: " + name)
        compile_log = (build / "native-compile.log").read_text()
        result["compiler_warning_lines"] = [
            line for line in compile_log.splitlines() if "warning:" in line.lower()
        ]
        if result["compiler_warning_lines"]:
            raise ValueError("compiler emitted warnings")
        binary_names = [
            "src/libcamera/libcamera.so.0.7.0",
            "src/ipa/libipa/libipa.a",
            "test/ipa/libipa/camss-x1e-helpers",
        ]
        result["built_outputs"] = {name: sha(build / name) for name in binary_names}
        result["status"] = "PASS_LIBCAMERA_NATIVE_HELPERS_NOT_INSTALLED"
    except Exception as exc:
        result.update(status="FAILED_LIBCAMERA_NATIVE_HELPERS", error=str(exc))
        raise
    finally:
        report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "report": str(report),
                      "tests": result["tests"], "installed": False,
                      "hardware_access": False}, indent=2))

if __name__ == "__main__":
    main()
