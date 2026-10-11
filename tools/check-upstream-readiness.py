#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Check the upstream work manifest. This is an engineering gate, not acceptance.

An empty/partial manifest cannot pass. A component needs declared provenance,
an explicit review, local source files and pinned PASS evidence. Hardware work
needs hardware evidence as well. Existing private inputs remain blockers until
their consumers are replaced. No private file contents are read by this tool.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

REQUIRED = {
    "front-startup", "rear-startup", "cphy", "camss-driver", "params-stats-api",
    "imx681", "ov13858", "focus-driver", "regulator-dt", "libcamera-pipeline",
    "ipa", "image-processing", "validation", "submission-export",
}
HARDWARE_REQUIRED = REQUIRED - {"submission-export"}
OPEN_KINDS = {"project-mathematics", "project-measurements", "upstream-open-source",
              "trace-derived-functional"}


def local_file(root, relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError("missing relative file path")
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("file path escapes the checkout")
    full = root / p
    # No symlink in any component, even one pointing back inside the checkout.
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("symlink source/evidence is not admitted")
    if not full.is_file():
        raise ValueError(f"missing file: {relative}")
    return full


def audit(manifest, root):
    problems = []
    if not isinstance(manifest, dict) or type(manifest.get("version")) is not int or manifest.get("version") != 1:
        return ["manifest version must be 1"]
    components = manifest.get("components")
    if not isinstance(components, list):
        return ["components must be a list"]
    seen = set()
    for item in components:
        if not isinstance(item, dict):
            problems.append("component must be an object")
            continue
        name = item.get("id")
        if not isinstance(name, str) or name not in REQUIRED:
            problems.append(f"unknown component: {name!r}")
            continue
        if name in seen:
            problems.append(f"duplicate component: {name}")
        seen.add(name)
        if item.get("status") != "ready":
            problems.append(f"{name}: {item.get('status', 'missing status')}")
            continue
        if item.get("provenance") not in OPEN_KINDS or item.get("provenance_reviewed") is not True:
            problems.append(f"{name}: provenance unreviewed or non-open")
        if item.get("private_runtime_dependencies") != []:
            problems.append(f"{name}: private runtime dependencies remain or are undeclared")
        if item.get("license_reviewed") is not True:
            problems.append(f"{name}: license/attribution review incomplete")
        if name in HARDWARE_REQUIRED and item.get("hardware_required") is False:
            problems.append(f"{name}: required hardware qualification cannot be disabled")
        source_paths = item.get("sources")
        if not isinstance(source_paths, list) or not source_paths:
            problems.append(f"{name}: sources undeclared")
            continue
        try:
            evidence = json.loads(local_file(root, item.get("evidence")).read_text())
            if evidence.get("result") != "PASS" or evidence.get("component") != name:
                raise ValueError("evidence is not a PASS for this component")
            if not evidence.get("validation_scope"):
                raise ValueError("validation scope missing")
            if (name in HARDWARE_REQUIRED or item.get("hardware_required") is not False) and evidence.get("hardware_qualified") is not True:
                raise ValueError("hardware qualification missing")
            pins = evidence.get("source_sha256")
            if not isinstance(pins, dict) or set(pins) != set(source_paths):
                raise ValueError("evidence does not pin every declared source")
            for path in source_paths:
                if hashlib.sha256(local_file(root, path).read_bytes()).hexdigest() != pins[path]:
                    raise ValueError(f"source changed after evidence: {path}")
        except (ValueError, TypeError, OSError, AttributeError) as e:
            problems.append(f"{name}: {e}")
    for name in sorted(REQUIRED - seen):
        problems.append(f"missing component: {name}")
    return problems


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    file = args.manifest or root / "docs/UPSTREAM-COMPONENTS-20261011.json"
    try:
        problems = audit(json.loads(file.read_text()), root)
    except (ValueError, OSError) as e:
        problems = [str(e)]
    print(json.dumps({"upstream_ready": not problems, "blockers": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
