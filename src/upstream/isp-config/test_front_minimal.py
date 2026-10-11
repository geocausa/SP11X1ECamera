#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Test the independent processing builder; no camera or private input access."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from open_config import bt601_q10_gbr

PINS = {
    "vfe680": "bce9607bac5b46ce907a1434b3a772c5c40b753b1c933db7d37822b9c26e020e",
    "vfe880": "c4845b4e33212267db16200574686b0b8898d5c3af1a73580761fb72c94fefd0",
}
HEADERS = {"sp11-front-minimal.h", "sp11-geometry-stats.h", "sp11-cst-stats.h",
           "sp11-front-fields.h", "sp11-cdm.h"}


def pinned(path, key):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"reference must be a regular non-symlink file: {key}")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f"reference hash differs: {key}")
    return data.decode()


def public_oracle(header, source):
    modules = {int(value, 16) for value in re.findall(
        r"^#define\s+VFE_PP_CLC_\w+_MODULE_CFG\s+(0x[0-9a-fA-F]+)\s*$", header, re.M)}
    if len(modules) != 64:
        raise ValueError("pinned module map extraction failed")
    macros = {name: int(value, 16) for name, value in re.findall(
        r"^#define\s+(IFE_DEMOSAIC_\w+)\s+(0x[0-9a-fA-F]+)\s*$", source, re.M)}
    body = source.split("static void vfe_setup_demosaic(", 1)[1].split("\n}", 1)[0]
    words = {macros[name]: int(value, 16) for value, name in re.findall(
        r"writel_relaxed\((0x[0-9a-fA-F]+), vfe->base \+ (IFE_DEMOSAIC_\w+)\)", body)}
    if len(words) != 5:
        raise ValueError("pinned demosaic extraction failed")
    return modules, words


def closure(here):
    seen, pending, hashes = set(), ["sp11-front-minimal.h"], {}
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        if name not in HEADERS:
            raise ValueError(f"unexpected builder dependency: {name}")
        path = here / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"invalid builder source: {name}")
        data = path.read_bytes()
        text = re.sub(r"/\*.*?\*/|//[^\n]*", "", data.decode(), flags=re.S)
        if re.search(r"\b(?:request_firmware\w*|fopen|open|read|filp_open|kernel_read|"
                     r"native_\w*|writel\w*|ioremap\w*)\s*\(", text):
            raise ValueError(f"forbidden runtime dependency in builder: {name}")
        pending.extend(re.findall(r'^#include\s+"([^\"]+)"', text, re.M))
        seen.add(name)
        hashes[name] = hashlib.sha256(data).hexdigest()
    if seen != HEADERS:
        raise ValueError("unexpected builder include closure")
    return hashes


def semantic_checks(program, modules, demosaic):
    if program["bytes"] != 1204 or program["dmi_transfers"] != 0:
        raise ValueError("unexpected program extent")
    for key in ("complete_startup_provider", "hardware_qualified", "runtime_dependencies_removed",
                "private_input_read"):
        if program[key] is not False:
            raise ValueError(f"invalid qualification claim: {key}")
    commands = program["register_commands"]
    if len(commands) != 81:
        raise ValueError("unexpected register-command count")
    disabled = commands[:64]
    if {c["register"] for c in disabled} != modules or any(c["values"] != [0] for c in disabled):
        raise ValueError("public module disable map differs")
    before_enable = {}
    final = {}
    for i, c in enumerate(commands):
        for j, value in enumerate(c["values"]):
            addr = c["register"] + 4 * j
            final[addr] = value
            if i < 75:
                before_enable[addr] = value
    if any(before_enable[a] & 1 for a in modules):
        raise ValueError("module enabled before final phase")
    for addr, value in demosaic.items():
        if final[addr] != value:
            raise ValueError("public demosaic parameters differ")
    matrix = bt601_q10_gbr()
    for i, row in enumerate(matrix):
        expected = [(row[0] & 8191) | ((row[1] & 8191) << 16), row[2] & 8191,
                    (512 if i else 0) << 19, 0, 0, 1023 << 20]
        actual = [final[0x6168 + i * 24 + j * 4] for j in range(6)]
        if actual != expected:
            raise ValueError("mathematical CST differs")
    # Independent semantic oracle, not a claim about ISP precision or rounding.
    for grey in range(1024):
        values = [sum(v * grey for v in row) // 1024 + (512 if i else 0)
                  for i, row in enumerate(matrix)]
        if values != [grey, 512, 512]:
            raise ValueError("neutral semantic colour conversion differs")
    for addr, value in ((0x9c68, 1439), (0x9c6c, 2559), (0x9e68, 719), (0x9e6c, 1279)):
        if final[addr] != value:
            raise ValueError("full-frame 4:2:0 crop geometry differs")
    enabled = {0x5660, 0x6160, 0x9860, 0x9a60, 0x9c60, 0x9e60}
    if {a for a in modules if final[a] & 1} != enabled:
        raise ValueError("optional block unexpectedly enabled")
    return {"public_module_addresses": 64, "public_demosaic_configuration_words": 4,
            "neutral_colour_vectors": 1024, "optional_modules_disabled": 58,
            "mathematical_cst_words": 18, "crop_geometry_words": 4}


def rejection_checks(tmp, references):
    count = 0
    for key, original in references.items():
        changed = tmp / (key + "-changed")
        changed.write_bytes(original.read_bytes() + b"\n")
        link = tmp / (key + "-link")
        link.symlink_to(original)
        for path in (changed, link, tmp / (key + "-missing")):
            try:
                pinned(path, key)
            except ValueError:
                count += 1
            else:
                raise ValueError("reference rejection failed")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vfe680-header", required=True, type=Path)
    parser.add_argument("--vfe880-source", required=True, type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    hashes = closure(here)
    refs = {"vfe680": args.vfe680_header, "vfe880": args.vfe880_source}
    modules, demosaic = public_oracle(pinned(refs["vfe680"], "vfe680"),
                                      pinned(refs["vfe880"], "vfe880"))
    results, baseline = [], None
    with tempfile.TemporaryDirectory(prefix="sp11-front-minimal-") as directory:
        tmp = Path(directory)
        rejected = rejection_checks(tmp, refs)
        for cc in ("gcc", "clang"):
            if not shutil.which(cc):
                raise RuntimeError(f"required compiler missing: {cc}")
            exe = tmp / cc
            subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                            str(here / "test-front-minimal.c"), "-o", str(exe)],
                           check=True, capture_output=True, text=True)
            run = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            dump = subprocess.run([str(exe), "--dump"], check=True, capture_output=True, text=True)
            program = json.loads(dump.stdout)
            semantic = semantic_checks(program, modules, demosaic)
            canonical = json.dumps(program, sort_keys=True, separators=(",", ":")).encode()
            if baseline is not None and canonical != baseline:
                raise ValueError("compiler command outputs differ")
            baseline = canonical
            results.append({"compiler": cc, "status": "PASS", "asan": True, "ubsan": True,
                            "detail": run.stdout.strip(), "semantic": semantic})
    print(json.dumps({"schema": "sp11-front-minimal-tests-v1", "tests": results,
                      "reference_rejection_cases": rejected, "public_reference_sha256": PINS,
                      "builder_include_closure_sha256": hashes,
                      "generated_public_program_sha256": hashlib.sha256(baseline).hexdigest(),
                      "program_bytes": 1204, "register_commands": 81, "dmi_transfers": 0,
                      "hardware_access": False, "private_profile_read": False,
                      "complete_startup_provider": False, "runtime_dependencies_removed": False}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(error.stderr or error.stdout)
        raise
