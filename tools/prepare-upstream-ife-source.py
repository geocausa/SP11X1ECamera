#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prepare the pinned public Linux/IFE source in a new isolated directory.

No build, installation, boot change, camera access or private input is performed.
The stage must not already exist. Original archives and failed attempts persist.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tarfile
import time
import urllib.request

BASE = "8d3ae59288f1e7d58d76558a6ee96d533bc5019f"
MIN_FREE = 2 * 1024 ** 3
MAX_ARCHIVE = 512 * 1024 ** 2


def save(stage, result):
    target = stage / "source-result.json"
    temporary = stage / "source-result.json.tmp"
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(target)


def prepare(args):
    manifest = json.loads(args.manifest.read_text())
    if manifest["base_commit"] != BASE:
        raise ValueError("unexpected upstream base")
    spec = importlib.util.spec_from_file_location(
        "reference", Path(__file__).with_name("verify-upstream-ife-reference.py"))
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)
    pinned = reference.verify(args.archive, manifest)
    if shutil.disk_usage(args.stage.parent).free < 5 * 1024 ** 3:
        raise ValueError("source staging needs at least 5 GiB free")
    args.stage.mkdir(exist_ok=False)
    url = "https://codeload.github.com/0xB0D/linux/tar.gz/" + BASE
    result = {"status": "DOWNLOADING", "base_commit": BASE, "url": url,
              "pinned_rfc_files": pinned, "compiled": False, "loaded": False,
              "hardware_qualified": False, "private_input_read": False,
              "runtime_changed": False}
    save(args.stage, result)
    try:
        archive = args.stage / "linux-base.tar.gz"
        partial = args.stage / "linux-base.tar.gz.partial"
        digest = hashlib.sha256()
        count = 0
        last_update = time.monotonic()
        request = urllib.request.Request(url, headers={"User-Agent": "SP11-public-IFE-source"})
        with urllib.request.urlopen(request, timeout=30) as response, partial.open("xb") as out:
            while chunk := response.read(1024 * 1024):
                count += len(chunk)
                if count > MAX_ARCHIVE or shutil.disk_usage(args.stage).free < MIN_FREE:
                    raise ValueError("archive size/free-space bound exceeded")
                out.write(chunk)
                digest.update(chunk)
                if time.monotonic() - last_update > 10:
                    result["download_bytes"] = count
                    save(args.stage, result)
                    print("download_bytes", count, flush=True)
                    last_update = time.monotonic()
        partial.rename(archive)
        result.update(status="EXTRACTING", archive_bytes=count,
                      archive_sha256=digest.hexdigest())
        save(args.stage, result)
        with tarfile.open(archive, "r:gz") as tar:
            members = tar.getmembers()
            roots = {Path(member.name).parts[0] for member in members}
            if roots != {"linux-" + BASE}:
                raise ValueError("unexpected archive root")
            expanded = sum(member.size for member in members if member.isfile())
            result["expanded_file_bytes"] = expanded
            if shutil.disk_usage(args.stage).free - expanded < MIN_FREE:
                raise ValueError("extraction would violate 2 GiB free-space reserve")
            instructions = [member.name for member in members
                            if Path(member.name).name == "AGENTS.md"]
            if instructions:
                result["instruction_files"] = instructions
                raise ValueError("new source instructions require review before preparation")
            tar.extractall(args.stage, filter="data")
        source = args.stage / ("linux-" + BASE)
        result.update(status="APPLYING_RFC", source=str(source))
        save(args.stage, result)
        import subprocess
        checks = 0
        for number in range(1, 75):
            # Recheck each normalized patch immediately before applying it.
            name = "normalized/patch-%02d.patch" % number
            pin = next(item for item in manifest["files"] if item["path"] == name)
            patch = reference.safe_path(args.archive, name).resolve()
            if reference.digest(patch) != pin["sha256"]:
                raise ValueError("patch changed since verification")
            changes = list(reference.blobs(patch))
            for old, new, before, after in changes:
                checks += reference.check_blob(source, old, before)
            for options in (["--check", "--whitespace=error"], ["--whitespace=error"]):
                subprocess.run(["git", "apply", *options, str(patch)], cwd=source,
                               capture_output=True, text=True, check=True)
            for old, new, before, after in changes:
                checks += reference.check_blob(source, new, after)
            result["patches_applied"] = number
        for pin in manifest["files"]:
            if pin["path"].startswith("applied-normalized/"):
                path = reference.safe_path(source, pin["path"][19:])
                if reference.digest(path) != pin["sha256"]:
                    raise ValueError("final RFC source differs")
        if checks != manifest["git_blob_checks"]:
            raise ValueError("blob check count differs")
        result.update(status="PASS_FULL_SOURCE_RFC_PREPARED", git_blob_checks=checks,
                      remaining_free_bytes=shutil.disk_usage(args.stage).free)
        save(args.stage, result)
        print(json.dumps(result), flush=True)
    except Exception as error:
        result.update(status="FAILED_PRESERVED", error=str(error))
        save(args.stage, result)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    prepare(parser.parse_args())


if __name__ == "__main__":
    main()
