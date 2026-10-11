#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile/run the actual kernel-usable field compiler, on synthetic inputs."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    here = Path(__file__).resolve().parent
    repo = here.parents[2]
    result = []
    with tempfile.TemporaryDirectory(prefix="sp11-open-fields-") as tmp:
        for cc in ("gcc", "clang"):
            if not shutil.which(cc):
                raise RuntimeError(f"required compiler missing: {cc}")
            exe = Path(tmp) / cc
            subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                            "-I", str(repo / "src/native-rgb"),
                            str(here / "test-front-fields.c"), "-o", str(exe)],
                           check=True, capture_output=True, text=True)
            p = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            result.append({"compiler": cc, "result": "PASS", "asan": True, "ubsan": True,
                           "detail": p.stdout.strip()})
    print(json.dumps({"hardware_access": False, "private_profile_read": False,
                      "complete_startup_profile": False, "tests": result}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(error.stderr or error.stdout, file=sys.stderr)
        raise
