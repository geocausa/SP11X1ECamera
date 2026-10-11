#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Synthetic tests, optionally against unchanged hash-pinned project packers."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def reference_header(directory, here):
    pins = json.loads((here / "geometry-stats-reference-20261011.json").read_text())["files"]
    parts = []
    for name, digest in pins.items():
        data = (directory / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"reference source hash differs: {name}")
        # Preserve complete functions and license comments; provide only the
        # kernel callback typedef/annotations needed by the existing source.
        parts.append(data.decode())
    prefix = """#include <stdint.h>
typedef uint16_t u16;
typedef int (*e006m_scalar_fn)(void *, u16, u32 *);
#define __used __attribute__((used))
#define BIT(n) (1U << (n))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
"""
    return prefix + "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    reference = reference_header(args.reference_dir, here) if args.reference_dir else None
    results = []
    with tempfile.TemporaryDirectory(prefix="sp11-geometry-stats-") as tmp:
        tmp = Path(tmp)
        if reference:
            (tmp / "reference.h").write_text(reference)
        for cc in ("gcc", "clang"):
            if not shutil.which(cc):
                raise RuntimeError(f"required compiler missing: {cc}")
            exe = tmp / cc
            flags = ["-DSP11_REFERENCE", "-I", str(tmp), "-Wno-unused-function"] if reference else []
            subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                            *flags, str(here / "test-geometry-stats.c"), "-o", str(exe)],
                           check=True, capture_output=True, text=True)
            p = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            results.append({"compiler": cc, "status": "PASS", "asan": True,
                            "ubsan": True, "detail": p.stdout.strip()})
    print(json.dumps({"hardware_access": False, "private_profile_read": False,
                      "complete_startup_profile": False, "pinned_reference_compared": bool(reference),
                      "tests": results}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(e.stderr or e.stdout)
        raise
