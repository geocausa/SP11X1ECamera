#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Bounded FULL NV12 setup tests against pinned Qualcomm GPL sources."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def verified(root, manifest):
    sources = {}
    for pin in manifest["files"]:
        relative = Path(pin["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("invalid reference path")
        path = root / relative
        if any(p.is_symlink() for p in [root, path, *path.parents]) or not path.is_file():
            raise ValueError("reference must be a regular non-symlink file")
        data = path.read_bytes()
        blob = hashlib.sha1(("blob " + str(len(data)) + "\0").encode() + data).hexdigest()
        if (len(data) != pin["bytes"] or hashlib.sha256(data).hexdigest() != pin["sha256"]
                or blob != pin["git_blob_sha1"]):
            raise ValueError("public reference pin differs: " + relative.name)
        if relative.name in sources:
            raise ValueError("ambiguous reference name")
        sources[relative.name] = data.decode()
    if len(sources) != 11:
        raise ValueError("incomplete public reference")
    return sources


def balanced(source, start):
    brace = source.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        if source[end] == "{": depth += 1
        if source[end] == "}": depth -= 1
        end += 1
    return source[start:end]


def reference_header(sources):
    bus = sources["cam_vfe_bus_ver3.c"]
    hw = sources["cam_vfe680.h"]
    defines = sources["cam_defs.h"]
    start = re.search(r"static enum cam_vfe_bus_ver3_packer_format\s+"
                      r"cam_vfe_bus_ver3_get_packer_fmt\s*\(", bus).start()
    function = balanced(bus, start)
    enum = balanced(bus, bus.index("enum cam_vfe_bus_ver3_packer_format {")) + ";"
    names = set(re.findall(r"\bCAM_FORMAT_[A-Z0-9_]+\b", function))
    macros = dict(re.findall(r"^#define\s+(CAM_FORMAT_[A-Z0-9_]+)\s+(\d+)\s*$", defines, re.M))
    if not names <= macros.keys():
        raise ValueError("format definitions missing")
    fields = ["cfg", "image_addr", "frame_incr", "image_cfg_0", "image_cfg_1",
              "image_cfg_2", "packer_cfg", "frame_header_addr", "frame_header_incr",
              "frame_header_cfg", "irq_subsample_period", "irq_subsample_pattern",
              "framedrop_period", "framedrop_pattern", "mode_cfg",
              "mmu_prefetch_cfg", "mmu_prefetch_max_offset"]
    registers = []
    for i, name in enumerate(("FULL Y", "FULL C")):
        start = hw.index(f"/* BUS Client {i} {name} */")
        block = balanced(hw, hw.index("{", start))
        values = {key: int(value, 16) for key, value in re.findall(
            r"\.(\w+)\s*=\s*(0x[0-9a-fA-F]+)\s*,", block)}
        ubwc = re.search(r"\bvfe680_ubwc_regs_client_" + str(i) + r"\s*=\s*\{", hw)
        ubwc_block = balanced(hw, ubwc.start())
        values["mode_cfg"] = int(re.search(r"\.mode_cfg\s*=\s*(0x[0-9a-fA-F]+)",
                                          ubwc_block).group(1), 16)
        if not re.search(r"CAM_FORMAT_NV12\)", block):
            raise ValueError("NV12 missing from public supported formats")
        registers.append([values[key] for key in fields])
    # The pinned function writes FULL sample width, while RDI has different units.
    compact = re.sub(r"\s+", "", bus)
    if "cam_io_w((rsrc_data->height<<16)|rsrc_data->width," not in compact:
        raise ValueError("public FULL dimensions expression differs")
    if "casePLANE_C:rsrc_data->height/=2;" not in compact:
        raise ValueError("public chroma height expression differs")
    if "frame_inc=stride*slice_h;" not in compact:
        raise ValueError("public frame increment expression differs")
    prefix = bus[:bus.index("#include")]
    macros_text = "\n".join(f"#define {name} {macros[name]}" for name in sorted(names))
    register_text = "static const u32 public_nv12_registers[2][17] = {\n" + ",\n".join(
        "{" + ",".join(hex(v) for v in row) + "}" for row in registers) + "\n};\n"
    stub = """
#define fallthrough __attribute__((fallthrough))
struct cam_vfe_bus_ver3_wm_resource_data { u32 format, index, num_planes; };
"""
    return prefix + macros_text + "\n" + enum + "\n" + stub + function + "\n" + register_text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", required=True, type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    manifest = json.loads((here / "nv12-bus-reference-20261012.json").read_text())
    sources = verified(args.reference_dir, manifest)
    reference = reference_header(sources)
    headers = ["sp11-vfe680-nv12.h", "sp11-cdm.h"]
    hashes = {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in headers}
    # This helper's production include closure is deliberately only the encoder.
    production = (here / headers[0]).read_text()
    if re.findall(r'^#include\s+"([^\"]+)"', production, re.M) != ["sp11-cdm.h"]:
        raise ValueError("unexpected production include dependency")
    results = []
    with tempfile.TemporaryDirectory(prefix="sp11-vfe680-nv12-") as directory:
        tmp = Path(directory)
        (tmp / "nv12-reference.h").write_text(reference)
        rejected = 0
        first = manifest["files"][0]
        # Exercise the real validator against three altered input sets.
        for mode in ("changed", "missing", "symlink"):
            root = tmp / mode
            root.mkdir()
            for pin in manifest["files"]:
                path = root / pin["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                if pin == first:
                    if mode == "missing": continue
                    if mode == "symlink":
                        path.symlink_to((args.reference_dir / pin["path"]).resolve())
                    else:
                        path.write_text(sources[Path(pin["path"]).name] + "\n")
                else:
                    path.write_text(sources[Path(pin["path"]).name])
            try:
                verified(root, manifest)
            except ValueError:
                rejected += 1
            else:
                raise ValueError("pin rejection failed")
        for cc in ("gcc", "clang"):
            if not shutil.which(cc): raise RuntimeError("required compiler missing: " + cc)
            exe = tmp / cc
            command = [cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                       "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                       "-DSP11_NV12_REFERENCE", "-I", str(tmp),
                       str(here / "test-vfe680-nv12.c"), "-o", str(exe)]
            subprocess.run(command, capture_output=True, text=True, check=True)
            run = subprocess.run([str(exe)], capture_output=True, text=True, check=True)
            results.append({"compiler": cc, "status": "PASS", "asan": True, "ubsan": True,
                            "detail": run.stdout.strip(), "actual_public_packer_function": True,
                            "public_register_addresses": 34})
    print(json.dumps({"schema": "sp11-vfe680-nv12-tests-v1", "tests": results,
                      "public_files_verified": 11, "public_pin_rejection_cases": rejected,
                      "production_headers_sha256": hashes, "source_register_commands": 12,
                      "source_bytes": 232, "clients_enabled": 0, "dmi_transfers": 0,
                      "private_input_read": False, "hardware_access": False,
                      "mapping_ownership_proven": False, "complete_startup_provider": False,
                      "runtime_dependencies_removed": False}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(error.stderr or error.stdout)
        raise
