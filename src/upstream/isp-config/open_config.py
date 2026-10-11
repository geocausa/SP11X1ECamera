#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Generate open, data-only ISP primitives. No firmware/profile input is read.

This is a partial configuration compiler, NOT a bootable ISP profile or a UAPI.
NV12 storage geometry, an illustrative Bayer-aligned metering grid, neutral
LSC/CCM, gamma, and a standard full-range RGB-to-YCbCr matrix are derived here.
Hardware register bindings, scaler phases, module enables and startup ordering
are intentionally unresolved. Never pass this JSON to a legacy blob loader.
"""
import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path


def integer(value, lo, hi, name):
    if type(value) is not int or not lo <= value <= hi:
        raise ValueError(f"{name} must be an integer in [{lo}, {hi}]")
    return value


def round_fraction(value):
    """Nearest integer, ties away from zero; independent of float rounding."""
    n, d = value.numerator, value.denominator
    return (1 if n >= 0 else -1) * ((2 * abs(n) + d) // (2 * d))


@dataclass(frozen=True)
class Mode:
    width: int
    height: int
    alignment: int = 64

    def nv12(self):
        w = integer(self.width, 2, 65534, "width")
        h = integer(self.height, 2, 65534, "height")
        a = integer(self.alignment, 2, 4096, "alignment")
        if w % 2 or h % 2 or a & (a - 1):
            raise ValueError("NV12 extents must be even; alignment must be a power of two")
        stride = (w + a - 1) // a * a
        ybytes, uvbytes = stride * h, stride * (h // 2)
        if ybytes + uvbytes > 0xffffffff:
            raise ValueError("NV12 extent exceeds a 32-bit buffer size")
        return {"width": w, "height": h, "stride": stride,
                "y": {"offset": 0, "rows": h, "bytes": ybytes},
                "uv": {"offset": ybytes, "rows": h // 2, "bytes": uvbytes},
                "total_bytes": ybytes + uvbytes}


def metering_grid(width, height, columns=32, rows=32):
    """Whole Bayer cells in a centred interior ROI. No hardware field packing."""
    w = integer(width, 2, 65534, "source width")
    h = integer(height, 2, 65534, "source height")
    nx = integer(columns, 1, 64, "columns")
    ny = integer(rows, 1, 64, "rows")
    if w % 2 or h % 2:
        raise ValueError("source dimensions must be even")
    cw, ch = (w // nx) & ~1, (h // ny) & ~1
    if cw < 2 or ch < 2:
        raise ValueError("metering region has no complete Bayer cell")
    used_w, used_h = cw * nx, ch * ny
    x, y = ((w - used_w) // 2) & ~1, ((h - used_h) // 2) & ~1
    return {"columns": nx, "rows": ny, "x": x, "y": y,
            "region_width": cw, "region_height": ch,
            "covered_width": used_w, "covered_height": used_h,
            "samples_per_colour_per_region": cw * ch // 4,
            "hardware_binding_qualified": False}


def bt601_q10_gbr():
    """Full-range YCbCr, Kr=.299, Kb=.114, input order G,B,R.

    Quantisation preserves exact unit Y gain and zero chroma for neutral RGB.
    Chroma offset is 128 at the semantic 8-bit output; register offset/shift
    packing remains a hardware-adapter task.
    """
    kr, kb = Fraction(299, 1000), Fraction(114, 1000)
    kg = 1 - kr - kb
    rgb = ((kr, kg, kb), (-kr / (2 * (1 - kb)), -kg / (2 * (1 - kb)), Fraction(1, 2)),
           (Fraction(1, 2), -kg / (2 * (1 - kr)), -kb / (2 * (1 - kr))))
    result = []
    for i, row in enumerate(rgb):
        r, g, b = (round_fraction(v * 1024) for v in row)
        g += (1024 if i == 0 else 0) - (r + g + b)
        result.append([g, b, r])
    return result


def gamma_points(curve="identity"):
    """257 monotonically increasing 12-bit samples; standard sRGB or linear."""
    if curve not in ("identity", "srgb"):
        raise ValueError("unsupported transfer curve")
    points = []
    for i in range(257):
        if curve == "identity":
            value = round_fraction(Fraction(i * 4095, 256))
        else:
            x = i / 256
            y = 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
            value = int(y * 4095 + 0.5)
        points.append(value)
    return points


def gamma_words(points):
    """Native data words: base12 | signed-delta12<<12. No DMI address."""
    if len(points) != 257:
        raise ValueError("gamma needs 257 endpoints")
    for p in points:
        integer(p, 0, 4095, "gamma point")
    words = []
    for a, b in zip(points, points[1:]):
        delta = b - a
        if not -2048 <= delta <= 2047:
            raise ValueError("gamma delta exceeds the signed 12-bit field")
        words.append(a | ((delta & 0xfff) << 12))
    return words


def pack_s13_pair(a, b):
    integer(a, -4096, 4095, "matrix coefficient")
    integer(b, -4096, 4095, "matrix coefficient")
    return (a & 0x1fff) | ((b & 0x1fff) << 16)


def matrix_words(matrix, transpose=False):
    """Six coefficient words. Front CST row order / CCM transposed order.

    These field layouts match the previously tested front coefficient adapter.
    This does not establish the rear module's packing or a complete register block.
    """
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("matrix must be 3x3")
    for row in matrix:
        for v in row:
            integer(v, -4096, 4095, "matrix coefficient")
    rows = list(zip(*matrix)) if transpose else matrix
    return [v for a, b, c in rows for v in (pack_s13_pair(a, b), pack_s13_pair(c, 0))]


def unity_lsc(columns=17, rows=13):
    """Neutral Q10 shading data in paired 13-bit fields, separated by one bit.

    R/G and B/G arrays are separate semantic channels. No DMI selectors or
    startup addresses are selected here. A unity mesh is a bring-up default,
    not sensor calibration. Limits bound allocation before any table is made.
    """
    nx = integer(columns, 2, 64, "mesh columns")
    ny = integer(rows, 2, 64, "mesh rows")
    word = 1024 | (1024 << 14)
    return {"columns": nx, "rows": ny, "red_green": [word] * (nx * ny),
            "blue_green": [word] * (nx * ny), "calibrated": False}


def generate(camera, curve="identity"):
    if camera not in ("front", "rear"):
        raise ValueError("camera must be front or rear")
    # Active sensor mode dimensions observed through this SP11's Linux media
    # graph. They are not the output image dimensions (especially on the rear).
    source = {"front": (3840, 2160, "RGGB"), "rear": (4064, 2286, "GRBG")}[camera]
    out = {"front": (2560, 1440), "rear": (3840, 2160)}[camera]
    cst = bt601_q10_gbr()
    ccm = [[128, 0, 0], [0, 128, 0], [0, 0, 128]]
    gp = gamma_points(curve)
    return {"schema": "sp11-open-isp-primitives-v1", "camera": camera,
            "complete_startup_profile": False, "hardware_qualified": False,
            "source_mode": {"width": source[0], "height": source[1], "bayer_order": source[2]},
            "nv12": Mode(*out).nv12(), "metering_example": metering_grid(*source[:2]),
            "cst": {"input_order": "GBR", "output_order": "Y,Cb,Cr", "q": 10,
                    "matrix": cst, "coefficient_words": matrix_words(cst),
                    "output_offsets_u8": [0, 128, 128], "hardware_offset_packing_qualified": False},
            "ccm": {"q": 7, "matrix": ccm, "coefficient_words": matrix_words(ccm, transpose=True)},
            "gamma": {"curve": curve, "points": gp, "channel_words": gamma_words(gp),
                      "channel_order": ["R", "G", "B"], "hardware_selectors_qualified": False},
            "lsc": unity_lsc(), "runtime_file_dependencies": [],
            "unresolved": ["scaler-and-crop-registers", "statistics-registers-and-payload-layout",
                           "module-enables-and-safe-defaults", "black-level-and-denoise-calibration",
                           "dmi-bindings-and-bank-lifetime", "cdm-startup-and-frame-sequencing",
                           "native-kernel-provider-integration"]}


def dumps(config):
    return json.dumps(config, indent=2, sort_keys=True, allow_nan=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", choices=("front", "rear"), required=True)
    parser.add_argument("--curve", choices=("identity", "srgb"), default="identity")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = dumps(generate(args.camera, args.curve))
    if args.output:
        # Exclusive create protects prior generated evidence from accidental replacement.
        with args.output.open("x", encoding="utf-8") as f:
            f.write(data)
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
