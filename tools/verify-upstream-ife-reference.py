#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify the pinned public IFE archive, optionally replaying its 74 patches.

This verifies source identity and patch application, never kernel compilation,
maintainer acceptance, runtime safety, provenance clearance or camera support.
No fetched code or build scripts are executed. Replay uses a temporary tree.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile


def safe_path(root, name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or str(path) != name:
        raise ValueError("non-canonical archive path")
    result = root
    if root.is_symlink():
        raise ValueError("symlink archive root")
    for part in path.parts:
        result = result / part
        if result.is_symlink():
            raise ValueError("symlink in archive path: " + name)
    return result


def digest(path):
    if not path.is_file():
        raise ValueError("missing regular file: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(archive, manifest):
    if manifest["version"] != 1 or manifest["patch_count"] != 74:
        raise ValueError("unsupported archive manifest")
    names = [item["path"] for item in manifest["files"]]
    if len(set(names)) != len(names):
        raise ValueError("duplicate file pin")
    required = {"patch-%02d.patch" % n for n in range(1, 75)}
    required |= {"normalized/patch-%02d.patch" % n for n in range(1, 75)}
    required |= {"patch-%02d-page.html" % n for n in range(75)}
    required |= {"patch-%02d-mail.txt" % n for n in range(75)}
    if not required <= set(names):
        raise ValueError("incomplete public series")
    patches = manifest["patches"]
    if [p["number"] for p in patches] != list(range(75)):
        raise ValueError("missing, reordered or duplicate message identity")
    for item in patches:
        expected = ("20261005-linux-mainline-7-2-sm8650-hdk-rfc-0-v1-%d-"
                    "ed985aefd611@kernel.org" % item["number"])
        if item["message_id"] != expected:
            raise ValueError("unexpected message identity")
    for item in manifest["files"]:
        path = safe_path(archive, item["path"])
        if digest(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            raise ValueError("changed source: " + item["path"])
    return len(names)


def blobs(patch):
    blocks = patch.read_text().split("diff --git ")[1:]
    if not blocks:
        raise ValueError("missing patch diff")
    for block in blocks:
        match = re.match(r"a/(\S+) b/(\S+)\n", block)
        if not match:
            raise ValueError("unsupported diff path")
        old, new = match.groups()
        for name in (old, new):
            safe_path(Path("."), name)
        if re.search(r"^(?:new file|new|old|deleted file) mode 120000$", block, re.M):
            raise ValueError("symlink patch is not admitted")
        index = re.search(r"^index ([0-9a-f]{12,40})\.\.([0-9a-f]{12,40})", block, re.M)
        if index:
            yield old, new, index[1], index[2]


def check_blob(tree, name, expected):
    if set(expected) == {"0"}:
        return 0
    actual = subprocess.check_output(
        ["git", "hash-object", str(safe_path(tree, name))], text=True).strip()
    if not actual.startswith(expected):
        raise ValueError("Git blob mismatch: " + name)
    return 1


def replay(archive, manifest):
    count = 0
    with tempfile.TemporaryDirectory(prefix="sp11-public-ife-") as temporary:
        tree = Path(temporary)
        for item in manifest["files"]:
            if item["path"].startswith("base/"):
                target = safe_path(tree, item["path"][5:])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(safe_path(archive, item["path"]), target)
        for number in range(1, 75):
            patch = safe_path(archive, "normalized/patch-%02d.patch" % number).resolve()
            changes = list(blobs(patch))
            for old, new, before, after in changes:
                count += check_blob(tree, old, before)
            for options in (["--check", "--whitespace=error"], ["--whitespace=error"]):
                subprocess.run(["git", "apply", *options, str(patch)], cwd=tree,
                               capture_output=True, text=True, check=True)
            for old, new, before, after in changes:
                count += check_blob(tree, new, after)
        finals = {item["path"][19:]: item for item in manifest["files"]
                  if item["path"].startswith("applied-normalized/")}
        actual_files = {str(p.relative_to(tree)) for p in tree.rglob("*") if p.is_file()}
        if actual_files != set(finals):
            raise ValueError("replayed tree file set differs")
        for name, item in finals.items():
            if digest(safe_path(tree, name)) != item["sha256"]:
                raise ValueError("replayed final source differs: " + name)
    if count != manifest["git_blob_checks"]:
        raise ValueError("Git blob check count differs")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text())
        pinned = verify(args.archive, manifest)
        checked = replay(args.archive, manifest) if args.replay else None
        print(json.dumps({"status": "PASS_PUBLIC_SOURCE_IDENTITY", "pinned_files": pinned,
                          "patches_replayed": 74 if args.replay else 0,
                          "git_blob_checks": checked, "compiled": False,
                          "hardware_qualified": False}))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, "FAIL: %s\n" % error)


if __name__ == "__main__":
    main()
