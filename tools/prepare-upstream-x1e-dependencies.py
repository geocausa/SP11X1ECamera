#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Replay pinned public X1E dependencies into a fresh source tree; no build/install."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "src/upstream/platform/x1e-dependencies-20261012"
MANIFEST_SHA256 = "c5c833e77db8e504fca4f4275374912b73231c0ab9fadcc1572a82c9cd79818c"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def regular(root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("Invalid relative path")
    p = root
    for part in path.parts:
        p = p / part
        if p.is_symlink():
            raise ValueError("Symlink rejected: " + str(p))
    if not p.is_file():
        raise ValueError("Missing regular file: " + str(p))
    return p

def check_pins(root, pins):
    for name, pin in pins.items():
        if sha(regular(root, name)) != pin:
            raise ValueError("Source pin mismatch: " + name)

def patch_changes(path):
    lines = path.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("diff --git "))
    return [line for line in lines[start:]
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
            and line != "-- "]

def apply(parent, output):
    parent = parent.resolve()
    output = output.resolve()
    if sha(regular(BUNDLE, "manifest.json")) != MANIFEST_SHA256:
        raise ValueError("Bundle manifest pin mismatch")
    manifest = json.loads((BUNDLE / "manifest.json").read_text())
    check_pins(parent, manifest["parent_source_sha256"])
    check_pins(BUNDLE, manifest["bundle_sha256"])
    rebase = manifest["context_rebase"]
    if patch_changes(BUNDLE / rebase["original_path"]) != patch_changes(BUNDLE / rebase["adapted_path"]):
        raise ValueError("Context rebase changes additions/deletions")
    if output.exists() or output.is_symlink():
        raise ValueError("Output must be a fresh path; failed attempts are retained")
    if output == parent or parent in output.parents or output in parent.parents:
        raise ValueError("Source trees must be separate")
    if not output.parent.is_dir():
        raise ValueError("Output parent directory must exist")
    touched = set(manifest["output_source_sha256"])
    patches = []
    for entry in manifest["patches"]:
        p = regular(BUNDLE, entry["applied_path"])
        paths = re.findall(r"^diff --git a/(\S+) b/(\S+)$", p.read_text(), re.M)
        if not paths or any(a != b or a not in touched for a, b in paths):
            raise ValueError("Unexpected patch target")
        patches.append(p)
    # The parent is an immutable source snapshot. Break all links a patch can
    # modify before applying it. Fresh build output must use a separate O=.
    shutil.copytree(parent, output, copy_function=os.link, symlinks=True,
                    ignore=shutil.ignore_patterns(".git"))
    for name in sorted(touched):
        p = output / name
        if p.exists():
            data = regular(output, name).read_bytes()
            p.unlink()
            p.write_bytes(data)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
    runs = []
    try:
        for p in patches:
            args = ["patch", "--batch", "--forward", "--fuzz=0", "-p1", "-i", str(p)]
            for dry in (True, False):
                run = subprocess.run(args + (["--dry-run"] if dry else []),
                                     cwd=output, text=True, capture_output=True)
                runs.append({"patch": str(p.relative_to(BUNDLE)), "dry_run": dry,
                             "exit_code": run.returncode, "output": run.stdout + run.stderr})
                if run.returncode:
                    raise ValueError("Patch failed: " + str(p))
        check_pins(output, manifest["output_source_sha256"])
        check_pins(output, manifest["unchanged_parent_source_sha256"])
        check_pins(parent, manifest["parent_source_sha256"])
        result = {"result": "PASS_SOURCE_REPLAY_ONLY", "patches": len(patches),
                  "changed_files": len(touched),
                  "unchanged_camss_files": len(manifest["unchanged_parent_source_sha256"]),
                  "installed": False, "hardware_qualified": False, "runs": runs}
    except Exception as error:
        result = {"result": "FAIL_RETAINED_SOURCE_REPLAY", "error": str(error), "runs": runs}
        raise
    finally:
        with (output / "sp11-dependency-replay-result.json").open("x") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    return {k: v for k, v in result.items() if k != "runs"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-source", type=Path, required=True)
    parser.add_argument("--output-source", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(apply(args.parent_source.resolve(), args.output_source.absolute())))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
