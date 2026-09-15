#!/usr/bin/env python3
"""Decode V4L2 Y10P active pixels, excluding row padding, and report metrics."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def decode(data, width, height, stride):
    if width <= 0 or width % 4 or height <= 0 or stride < width * 5 // 4:
        raise ValueError("invalid Y10P geometry")
    extent = height * stride
    if not len(data) or len(data) % extent:
        raise ValueError("input does not contain whole frames")
    rows = np.frombuffer(data, dtype=np.uint8).reshape(-1, height, stride)
    groups = rows[:, :, :width * 5 // 4].reshape(-1, height, width // 4, 5)
    groups = groups.astype(np.uint16)
    # Kernel Y10P definition: four high bytes followed by packed low pairs.
    pixels = (groups[:, :, :, :4] << 2) | (
        (groups[:, :, :, 4, None] >> (2 * np.arange(4))) & 3)
    return pixels.reshape(-1, height, width)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path, nargs="?")
    parser.add_argument("--width", type=int, default=644)
    parser.add_argument("--height", type=int, default=604)
    parser.add_argument("--stride", type=int, default=816)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        # Independent bit-pattern vectors plus deliberately nonzero row padding.
        actual = decode(bytes([0, 0, 0, 0, 0xe4, 0xa5,
                               255, 255, 255, 255, 0xe4, 0x5a]), 4, 2, 6)
        assert actual.tolist() == [[[0, 1, 2, 3], [1020, 1021, 1022, 1023]]]
        for payload, w, h, s in [(b"", 4, 1, 5), (b"1234", 4, 1, 5),
                                  (b"12345", 3, 1, 5), (b"1234", 4, 1, 4)]:
            try:
                decode(payload, w, h, s)
            except ValueError:
                continue
            raise AssertionError("invalid input accepted")
        print("Y10P decoder vectors and malformed-input checks: PASS")
        return
    if args.raw is None:
        parser.error("raw input is required")
    data = args.raw.read_bytes()
    try:
        pixels = decode(data, args.width, args.height, args.stride)
    except ValueError as exc:
        parser.error(str(exc))
    frames = []
    for frame in pixels:
        frames.append({
            "active_sha256_le16": hashlib.sha256(frame.astype("<u2").tobytes()).hexdigest(),
            "min": int(frame.min()), "max": int(frame.max()),
            "mean": float(frame.mean()), "stddev": float(frame.std()),
            "percentiles_1_50_99": np.percentile(frame, [1, 50, 99]).tolist(),
        })
    print(json.dumps({
        "format": "Y10P", "width": args.width, "height": args.height,
        "stride": args.stride, "input_sha256": hashlib.sha256(data).hexdigest(),
        "input_bytes": len(data), "frames": frames,
        "changed_active_pixels_between_frames":
            np.count_nonzero(pixels[1:] != pixels[:-1], axis=(1, 2)).tolist(),
        "note": "Statistics do not establish scene visibility or image quality.",
    }, indent=2))


if __name__ == "__main__":
    main()
