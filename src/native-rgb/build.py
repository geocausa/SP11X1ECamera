#!/usr/bin/env python3
"""Assemble and build retained native camera sources; never install or access hardware."""
import argparse
import hashlib
import json
import re
import runpy
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def checked_source(name, expected):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError("source outside checkout or missing: " + name)
    if digest(path) != expected:
        raise ValueError("source digest changed: " + name)
    return path

def command(args, **kwargs):
    subprocess.run([str(a) for a in args], check=True, **kwargs)

def assemble(out, nv12_trial=False, front_owner_trial=False, front_queue_trial=False, front_meta_trial=False, front_params_trial=False, front_profile_trial=False, front_sof_trial=False, front_control_trace_trial=False):
    manifest = json.loads((HERE / "sources.json").read_text())
    if front_owner_trial and not nv12_trial:
        raise ValueError("front owner trial requires isolated NV12 trial")
    for name, expected in manifest["baseline_inputs"].items():
        checked_source(name, expected)
    for name, expected in manifest["integration_inputs"].items():
        checked_source(name, expected)
    if nv12_trial:
        for name, expected in manifest["nv12_trial_inputs"].items():
            checked_source(name, expected)
    if front_owner_trial:
        for name, expected in manifest["front_owner_trial_inputs"].items():
            checked_source(name, expected)
    if front_queue_trial:
        if not front_owner_trial:
            raise ValueError("front queue trial requires consumed owner trial")
        for name, expected in manifest["front_queue_trial_inputs"].items():
            checked_source(name, expected)
    if front_meta_trial:
        if not front_queue_trial:
            raise ValueError("front metadata trial requires serialized front queue")
        for name, expected in manifest["front_meta_trial_inputs"].items():
            checked_source(name, expected)
    if front_params_trial:
        if not front_meta_trial:
            raise ValueError("front typed parameters require frame metadata trial")
        for name, expected in manifest["front_params_trial_inputs"].items():
            checked_source(name, expected)
    if front_profile_trial:
        if not front_params_trial:
            raise ValueError("front tuning profile requires typed parameter trial")
        for name, expected in manifest["front_profile_trial_inputs"].items():
            checked_source(name, expected)
    if front_sof_trial:
        if not front_profile_trial:
            raise ValueError("native SOF events require data-only profile trial")
        for name, expected in manifest["front_sof_trial_inputs"].items():
            checked_source(name, expected)
    if front_control_trace_trial:
        if not front_sof_trial:
            raise ValueError("native sensor control trace requires receiver SOF trial")
        for name, expected in manifest["front_control_trace_trial_inputs"].items():
            checked_source(name, expected)
    destinations = set()
    for fragment in manifest["rear_fragments"]:
        checked_source(fragment["source"], fragment["sha256"])
        name = fragment["destination"]
        if Path(name).name != name or name in destinations:
            raise ValueError("invalid or duplicate fragment destination")
        destinations.add(name)
    # Refuse existing outputs: no recycled build identity, no destructive cleanup.
    out.mkdir(parents=True, exist_ok=False)
    camss = out / "camss"
    camss.mkdir()
    for name in manifest["baseline_inputs"]:
        path = ROOT / name
        if path.parent == ROOT / "src/front-imx681/kernel/camss":
            shutil.copy2(path, camss / path.name)
    overlay = runpy.run_path(str(ROOT /
        "experiments/E004-front-ir-vd55g0/e004ip-qc10c-mapped-dma-coverage/make_qc10c_span.py"))
    overlay_result = overlay["make"](ROOT / "src/front-imx681/kernel/camss", camss)
    for fragment in manifest["rear_fragments"]:
        destination = camss / fragment["destination"]
        shutil.copy2(ROOT / fragment["source"], destination)
        if fragment.get("transform") == "mark_e011z_binder_maybe_unused":
            text = destination.read_text()
            anchor = "static int\ne011z_rear_bind_startup_adaptive("
            if text.count(anchor) != 1:
                raise ValueError("adaptive binder declaration drift")
            destination.write_text(text.replace(anchor,
                "static int __maybe_unused\ne011z_rear_bind_startup_adaptive(", 1))
        elif fragment.get("transform"):
            raise ValueError("unrecognized source transform")
    command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
             HERE / "rear-bf-composition.patch"], cwd=camss)
    # E004IO adds this include at a context line in the pinned rear patch.
    # Temporarily remove exactly that include, apply with zero fuzz, restore it.
    vfe = camss / "camss-vfe-680.c"
    include = "#include <media/videobuf2-dma-sg.h>\n"
    text = vfe.read_text()
    if text.count(include) != 1:
        raise ValueError("NV12 DMA include missing or repeated")
    vfe.write_text(text.replace(include, "", 1))
    command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
             HERE / "rear-composition.patch"], cwd=camss)
    text = vfe.read_text()
    anchor = '#include "camss.h"'
    if text.count(anchor) != 1:
        raise ValueError("CAMSS include anchor changed")
    vfe.write_text(text.replace(anchor, include + anchor, 1))
    if nv12_trial:
        shutil.copy2(HERE / "native-front-nv12-commands.h",
                     camss / "native-front-nv12-commands.h")
        command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
                 HERE / "front-linear-nv12-trial.patch"], cwd=camss)
    if front_owner_trial:
        shutil.copy2(HERE / "native-front-owner.h", camss / "native-front-owner.h")
        command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
                 HERE / "front-owner-trial.patch"], cwd=camss)
    if front_queue_trial:
        shutil.copy2(HERE / "native-front-queue.inc", camss / "native-front-queue.inc")
        command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
                 HERE / "front-queue-trial.patch"], cwd=camss)
    if front_meta_trial:
        for name in ("native-front-meta.inc", "native-front-stats.h"):
            shutil.copy2(HERE / name, camss / name)
        command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
                 HERE / "front-meta-trial.patch"], cwd=camss)
    if front_params_trial:
        for name in ("native-front-params-kernel.inc", "native-front-params.h"):
            shutil.copy2(HERE / name, camss / name)
        command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
                 HERE / "front-params-trial.patch"], cwd=camss)
    if front_profile_trial:
        for name in ("native-front-profile-kernel.inc", "native-front-profile.h", "native-front-profile-schema.h"):
            shutil.copy2(HERE / name, camss / name)
        command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
                 HERE / "front-profile-trial.patch"], cwd=camss)
    if front_sof_trial:
        command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
                 HERE / "front-sof-trial.patch"], cwd=camss)
    (out / "imx681").mkdir()
    for name in manifest["baseline_inputs"]:
        path = ROOT / name
        if path.parent == ROOT / "src/front-imx681/kernel/imx681":
            shutil.copy2(path, out / "imx681" / path.name)
    command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
             HERE / "front-sensor-timing.patch"], cwd=out / "imx681")
    if front_control_trace_trial:
        command(["patch", "--batch", "--fuzz=0", "-p1", "-i",
                 HERE / "front-control-trace-trial.patch"], cwd=out / "imx681")
    rear = out / "ov13858"
    rear.mkdir()
    shutil.copy2(ROOT / "src/native-rgb/ov13858/ov13858.c", rear / "ov13858.c")
    (rear / "Makefile").write_text("obj-m += ov13858.o\n")
    # Validate include closure; compilation checks actual call/type consistency.
    for source in camss.iterdir():
        if source.suffix in (".c", ".h", ".inc"):
            for name in re.findall(r'^#include "([^"]+)"', source.read_text(), re.M):
                if not (camss / name).is_file():
                    raise ValueError("missing local include: " + name)
    staged = {}
    for directory in (camss, out / "imx681", rear):
        for path in directory.iterdir():
            if path.is_file():
                staged[str(path.relative_to(out))] = digest(path)
    result = {
        "schema": 1, "status": "ASSEMBLED_NOT_INSTALLED",
        "source_manifest_sha256": digest(HERE / "sources.json"),
        "rear_fragments": len(destinations),
        "overlay_audit": overlay_result,
        "staged_sources": dict(sorted(staged.items())),
        "runtime_access": False,
        "nv12_trial_staged": nv12_trial,
        "front_owner_trial_staged": front_owner_trial,
        "front_queue_trial_staged": front_queue_trial,
        "front_meta_trial_staged": front_meta_trial,
        "front_params_trial_staged": front_params_trial,
        "front_profile_trial_staged": front_profile_trial,
        "front_sof_trial_staged": front_sof_trial,
        "front_control_trace_trial_staged": front_control_trace_trial,
        "nv12_trial_default_denied": True,
        "compiler_policy": "W=1 and -Werror",
        "nv12_runtime_proven": False,
        "rear_runtime_proven": False,
    }
    (out / "source-manifest.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--kernel-source", type=Path)
    parser.add_argument("--kernel-output", type=Path)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--nv12-trial", action="store_true",
                        help="Stage isolated cold-state four-frame diagnostic; no installation")
    parser.add_argument("--front-owner-trial", action="store_true",
                        help="Stage native front IRQ consumed-address validation; requires --nv12-trial")
    parser.add_argument("--front-queue-trial", action="store_true",
                        help="Stage serialized queue qualification; requires NV12 and owner trials")
    parser.add_argument("--front-meta-trial", action="store_true",
                        help="Stage frame-associated statistics metadata; requires queue trial")
    parser.add_argument("--front-params-trial", action="store_true",
                        help="Stage typed front scalar qualification; requires metadata trial")
    parser.add_argument("--front-profile-trial", action="store_true",
                        help="Stage data-only kernel firmware tuning; requires typed parameter trial")
    parser.add_argument("--front-sof-trial", action="store_true",
                        help="Stage native receiver frame-sync events; requires profile trial")
    parser.add_argument("--front-control-trace-trial", action="store_true",
                        help="Stage read-only grouped sensor transaction timing; requires receiver SOF trial")
    options = parser.parse_args()
    if bool(options.kernel_source) != bool(options.kernel_output):
        parser.error("kernel-source and kernel-output must be supplied together")
    out = options.out.resolve()
    if out.is_relative_to(ROOT):
        parser.error("build output must be outside the source checkout")
    result = assemble(out, options.nv12_trial, options.front_owner_trial, options.front_queue_trial, options.front_meta_trial, options.front_params_trial, options.front_profile_trial, options.front_sof_trial, options.front_control_trace_trial)
    if options.kernel_source:
        result["status"] = "BUILD_IN_PROGRESS"
        (out / "build-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        try:
            for name in ("camss", "imx681", "ov13858"):
                command(["make", "-C", options.kernel_source.resolve(),
                         "O=" + str(options.kernel_output.resolve()),
                         "M=" + str(out / name), "CONFIG_VIDEO_QCOM_CAMSS=m",
                         "W=1", "KCFLAGS=-Werror", "-j" + str(options.jobs), "modules"])
            modules = {}
            for relative in ("camss/qcom-camss.ko", "imx681/imx681.ko", "ov13858/ov13858.ko"):
                path = out / relative
                modules[relative] = {
                    "sha256": digest(path),
                    "vermagic": subprocess.check_output(
                        ["modinfo", "-F", "vermagic", str(path)], text=True).strip(),
                }
            result.update(status="PASS_NATIVE_SOURCE_BUILD_NOT_INSTALLED", modules=modules)
        except Exception as exc:
            result.update(status="FAILED_NATIVE_SOURCE_BUILD", error=str(exc))
            raise
        finally:
            (out / "build-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "out": str(out),
                      "rear_fragments": result["rear_fragments"],
                      "modules": result.get("modules", {})}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
