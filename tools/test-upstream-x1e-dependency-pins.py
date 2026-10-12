#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Negative controls for the source replay importer; no kernel build or hardware."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("x1e_replay", ROOT / "tools/prepare-upstream-x1e-dependencies.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-source", type=Path, required=True)
    args = parser.parse_args()
    bundle = replay.BUNDLE
    manifest = json.loads((bundle / "manifest.json").read_text())
    replay.check_pins(args.parent_source, manifest["parent_source_sha256"])
    cases = 0
    targets = [
        ("bundle", "manifest.json"),
        ("bundle", "camss-phy-api-v17/04.patch"),
        ("bundle", manifest["context_rebase"]["adapted_path"]),
        ("parent", "drivers/media/platform/qcom/camss/camss-cdm-power.c"),
        ("parent", "drivers/media/platform/qcom/camss/camss-cdm-2-1.c"),
        ("parent", "drivers/phy/phy-core.c"),
    ]
    with tempfile.TemporaryDirectory(prefix="sp11-x1e-pin-tests-") as tmp:
        tmp = Path(tmp)
        for which, name in targets:
            for mutation in ("modified", "missing", "symlink"):
                case = tmp / str(cases)
                case.mkdir()
                b = case / "bundle"
                shutil.copytree(bundle, b)
                p = case / "parent"
                p.mkdir()
                for rel in manifest["parent_source_sha256"]:
                    dest = p / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(args.parent_source / rel, dest)
                file = (b if which == "bundle" else p) / name
                data = file.read_bytes()
                if mutation == "modified":
                    file.write_bytes(data + b"\n")
                else:
                    file.unlink()
                    if mutation == "symlink":
                        target = case / "symlink-target"
                        target.write_bytes(data)
                        file.symlink_to(target)
                replay.BUNDLE = b
                output = case / "source"
                try:
                    replay.apply(p, output)
                except (ValueError, OSError):
                    pass
                else:
                    raise AssertionError("Accepted " + which + ":" + name + ":" + mutation)
                assert not output.exists(), "Rejection occurred after creating output"
                cases += 1
        replay.BUNDLE = bundle
        existing = tmp / "existing"
        existing.mkdir()
        (existing / "retained.txt").write_text("retain\n")
        try:
            replay.apply(args.parent_source.resolve(), existing)
        except ValueError:
            pass
        else:
            raise AssertionError("Existing output was accepted")
        assert (existing / "retained.txt").read_text() == "retain\n"
        nested_link = tmp / "nested-parent"
        nested_link.symlink_to(args.parent_source.resolve(), target_is_directory=True)
        try:
            replay.apply(args.parent_source.resolve(), nested_link / "sp11-forbidden-nested-output")
        except ValueError:
            pass
        else:
            raise AssertionError("Symlink ancestor bypassed nested-source rejection")
        assert not (nested_link / "sp11-forbidden-nested-output").exists()

    print(json.dumps({"result": "PASS", "pin_rejections_before_output": cases,
                      "existing_output_retained": True, "symlink_ancestor_nested_output_rejected": True, "hardware_qualified": False}))

if __name__ == "__main__":
    main()
