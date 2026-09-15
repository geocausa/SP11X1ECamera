#!/usr/bin/env python3
"""Check SP11 CAMSS resource extents before a native IR candidate can boot."""
import argparse
import json
from pathlib import Path
import subprocess


CAMSS = "/soc@0/isp@acb7000"


def get(path, prop, kind):
    return subprocess.check_output(
        ["fdtget", "-t", kind, str(path), CAMSS, prop], text=True).split()


def validate(path):
    names = get(path, "reg-names", "s")
    cells = [int(value, 16) for value in get(path, "reg", "x")]
    if len(cells) != 4 * len(names) or len(set(names)) != len(names):
        raise ValueError("invalid or duplicate CAMSS resources")
    resources = {}
    for i, name in enumerate(names):
        a, b, c, d = cells[4 * i:4 * i + 4]
        resources[name] = ((a << 32) | b, (c << 32) | d)
    # Same-machine Windows aperture, already established by E004v/E004w.
    # X1E common CSIPHY registers begin at offset 0x1000, not 0x800.
    if resources.get("csiphy0") != (0x0ace4000, 0x2000):
        raise ValueError("CSIPHY0 must map the verified 0x0ace4000+0x2000 aperture")
    for name in ("csid0", "vfe0", "csid_wrapper"):
        if name not in resources:
            raise ValueError("missing ordinary IR pipeline resource: " + name)
    intervals = sorted((base, base + size, name) for name, (base, size) in resources.items())
    for index, (base, end, name) in enumerate(intervals):
        if end <= base:
            raise ValueError("empty resource: " + name)
        if index and intervals[index - 1][1] > base:
            raise ValueError("overlapping CAMSS resources: " + name)
    return {"status": "PASS", "csiphy0_base": "0x0ace4000",
            "csiphy0_bytes": 8192, "resource_count": len(resources)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dtb", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.dtb), indent=2))
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
