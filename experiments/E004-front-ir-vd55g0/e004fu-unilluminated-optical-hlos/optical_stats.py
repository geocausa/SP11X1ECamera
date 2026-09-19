#!/usr/bin/env python3
"""Privacy-minimized grayscale metrics for one bounded unilluminated capture.

Do not store or print source pixels, images, templates, or full histograms.
"""
from __future__ import annotations
from collections import Counter

WIDTH, HEIGHT, STRIDE, FRAMES = 644, 604, 1936, 16
FRAME_BYTES = STRIDE * HEIGHT


def summarize(raw: bytes) -> list[dict[str, float | int | bool]]:
    if len(raw) != FRAMES * FRAME_BYTES:
        raise ValueError("expected precisely sixteen full-stride RGB888 frames")
    report = []
    view = memoryview(raw)
    for n in range(FRAMES):
        hist: Counter[int] = Counter()
        base = n * FRAME_BYTES
        for row in range(HEIGHT):
            line = view[base+row*STRIDE:base+(row+1)*STRIDE]
            if any(line[WIDTH*3:]):
                raise ValueError("nonzero RGB888 padding in frame " + str(n))
            values = bytes(line[:WIDTH*3:3])
            if values != bytes(line[1:WIDTH*3:3]) or values != bytes(line[2:WIDTH*3:3]):
                raise ValueError("non-neutral RGB888 data in frame " + str(n))
            hist.update(values)
        total = WIDTH * HEIGHT
        if sum(hist.values()) != total:
            raise ValueError("incomplete grayscale histogram")
        cumulative, p99 = 0, 255
        for level in range(256):
            cumulative += hist[level]
            if cumulative >= (total*99 + 99)//100:
                p99 = level
                break
        mean = sum(level*count for level,count in hist.items())/total
        report.append({
            "frame": n, "min": min(hist), "max": max(hist),
            "mean": round(mean, 3), "p99": p99,
            "fraction_above_32": round(sum(count for value,count in hist.items()
                                             if value > 32)/total, 6),
            "nonuniform": len(hist) > 1,
        })
    return report
