#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import importlib.util
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
E007P = REPO / "experiments/E004-front-ir-vd55g0/e007p-rear-tmc141-clean-producer"
GTM_DIR = REPO / "experiments/E003-front-imx681-cphy/e003i-front-native-productionization/j-cleanroom-gtm"
GTM_PY = GTM_DIR / "generate-cleanroom-gtm-wire.py"


class TmcInput(ctypes.Structure):
    _fields_ = [
        ("runtime_0c", ctypes.c_float),
        ("runtime_18", ctypes.c_float),
        ("runtime_480", ctypes.c_float),
        ("runtime_488", ctypes.c_float),
        ("runtime_48c", ctypes.c_float),
        ("common_64", ctypes.c_float),
        ("mode", ctypes.c_uint32),
        ("curve_order", ctypes.c_uint32),
        ("ctrl_8234", ctypes.c_uint32),
        ("ctrl_8238", ctypes.c_uint32),
        ("ctrl_8244", ctypes.c_uint32),
        ("ctrl_8254", ctypes.c_uint32),
        ("face_count", ctypes.c_uint32),
    ]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def _f32(buf: bytes, off: int) -> float:
    return struct.unpack_from("<f", buf, off)[0]


def _u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def compile_tmc141(output: Path) -> None:
    subprocess.run(
        [
            "gcc", "-O2", "-shared", "-fPIC", "-Wall", "-Wextra", "-Werror",
            "-fno-fast-math", "-ffp-contract=off",
            str(E007P / "tmc141-clean.c"), "-lm", "-o", str(output),
        ],
        check=True,
    )


class RearDynamicGtm:
    """Clean rear GTM producer for the source-proven OV13858 4K path."""

    def __init__(self, tmc_so: Path):
        self.gtm = _load(GTM_PY, "e007q_clean_gtm")
        self.domain = self.gtm.load_domain(GTM_DIR)
        self.lib = ctypes.CDLL(str(tmc_so))
        self.solve = self.lib.e007p_tmc141_solve
        self.solve.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t,
            ctypes.POINTER(TmcInput),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_uint),
        ]
        self.solve.restype = ctypes.c_int

    def run(
        self,
        tune: bytes,
        runtime: bytes,
        common: bytes,
        ctrl: bytes,
        face: bytes,
        mode: int = 0x60800,
    ):
        if len(tune) != 0x170:
            raise ValueError("rear TMC tune size")
        if len(runtime) != 0x498:
            raise ValueError("rear TMC runtime size")
        if len(common) < 0x68:
            raise ValueError("rear TMC common size")
        if len(ctrl) < 0x30:
            raise ValueError("rear TMC ctrl size")
        if len(face) < 4:
            raise ValueError("rear TMC face size")

        tune_arr = (ctypes.c_float * (len(tune) // 4)).from_buffer_copy(tune)
        src = (ctypes.c_float * 7)()
        dst = (ctypes.c_float * 7)()
        coeff = (ctypes.c_float * 15)()
        scale_index = ctypes.c_uint()

        inp = TmcInput(
            _f32(runtime, 0x0C),
            _f32(runtime, 0x18),
            _f32(runtime, 0x480),
            _f32(runtime, 0x488),
            _f32(runtime, 0x48C),
            _f32(common, 0x64),
            mode,
            _u32(common, 0x60),
            _u32(ctrl, 0x0C),
            _u32(ctrl, 0x10),
            ctrl[0x1C],
            _u32(ctrl, 0x2C),
            _u32(face, 0),
        )

        rc = self.solve(
            tune_arr,
            len(tune) // 4,
            ctypes.byref(inp),
            src,
            dst,
            coeff,
            ctypes.byref(scale_index),
        )
        if rc:
            raise RuntimeError(f"TMC141 solver rc={rc}")

        # The accepted clean GTM backend consumes only these three family-2
        # arrays. The mode-2 domain is clean immutable authority loaded above.
        tmc = bytearray(0x7228)
        tmc[0x5104:0x5120] = bytes(src)
        tmc[0x5120:0x513C] = bytes(dst)
        tmc[0x51B0:0x51EC] = bytes(coeff)
        wire = self.gtm.generate(bytes(tmc), self.domain)
        if len(wire) != 0x800:
            raise RuntimeError("GTM wire size drift")

        meta = {
            "scale_index": int(scale_index.value),
            "src_bytes": len(bytes(src)),
            "dst_bytes": len(bytes(dst)),
            "coeff_bytes": len(bytes(coeff)),
            "gtm_bytes": len(wire),
        }
        return wire, bytes(src), bytes(dst), bytes(coeff), meta


if __name__ == "__main__":
    print("E007Q_REAR_GTM_RUNTIME_MODULE")
