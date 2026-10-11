#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Three-way merge of the front (robust queue, build 46) and rear (daily 65) camss
module trees into one source tree that drives both cameras.

base   = build.py composition at commit 84425426 (common ancestor of both lines)
ours   = rear daily 65 (rear generation queue, 30 fps statistics, measured tone)
theirs = front build 46 (front native queue, AE metadata, LSC/ABF, robust queue)
Usage: merge-unified.py <base> <rear> <front> <out>   (each holds camss/ imx681/ ov13858/)
Prints a JSON summary; exits 1 if any file has conflicts (markers left in <out>).
"""
import filecmp, json, shutil, subprocess, sys
from pathlib import Path

SKIP_SUFFIX = (".o", ".ko", ".cmd", ".mod", ".mod.c", ".order", ".symvers", ".log")


def sources(d):
    return {p.name for p in d.iterdir() if p.is_file() and not p.name.endswith(SKIP_SUFFIX)
            and p.name not in ("modules.order", "Module.symvers")}


def main():
    base, rear, front, out = (Path(a) for a in sys.argv[1:5])
    summary = {}
    bad = 0
    for sub in ("camss", "imx681", "ov13858"):
        b, r, f, o = base / sub, rear / sub, front / sub, out / sub
        o.mkdir(parents=True, exist_ok=True)
        names = sources(b) | sources(r) | sources(f)
        res = {"rear_only": [], "front_only": [], "merged": [], "conflict": [], "deleted": []}
        for n in sorted(names):
            inb, inr, inf = (b / n).exists(), (r / n).exists(), (f / n).exists()
            if not inb:
                if inr and inf and not filecmp.cmp(r / n, f / n, shallow=False):
                    res["conflict"].append(n + " (added on both sides)")
                    bad += 1
                src = r / n if inr else f / n
                shutil.copy2(src, o / n)
                res["rear_only" if inr else "front_only"].append(n)
                continue
            if not inr or not inf:
                res["deleted"].append(n)
                continue
            rc = filecmp.cmp(b / n, r / n, shallow=False)
            fc = filecmp.cmp(b / n, f / n, shallow=False)
            if rc:
                shutil.copy2(f / n, o / n)
                if not fc:
                    res["front_only"].append(n)
                continue
            if fc:
                shutil.copy2(r / n, o / n)
                res["rear_only"].append(n)
                continue
            shutil.copy2(r / n, o / n)
            p = subprocess.run(["git", "merge-file", "-L", "rear", "-L", "base", "-L", "front",
                                str(o / n), str(b / n), str(f / n)])
            if p.returncode:
                res["conflict"].append(f"{n} ({p.returncode})")
                bad += 1
            else:
                res["merged"].append(n)
        summary[sub] = res
    print(json.dumps(summary, indent=1))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
