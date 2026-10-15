# SPDX-License-Identifier: GPL-2.0-only
"""SP11 rear (ov13858) ISP start-up input: struct native_rear_startup_input.

ctypes mirror of the camss build-48 kernel structure (16,672 bytes): startup
request ids, 3A start state (demux/digital gain, white balance), mode geometry,
statistics windows, IQ (AF window, CST12 colour transform, BPC/ABF parameters)
and per-packet adaptive tables (LSC selectors 1/2, GTM).
"""
import ctypes as C

P = 4
u8, u16, s16, u32, u64, b8 = C.c_uint8, C.c_uint16, C.c_int16, C.c_uint32, C.c_uint64, C.c_bool


class S(C.Structure):
    def dict(self):
        out = {}
        for name, typ in self._fields_:
            v = getattr(self, name)
            if isinstance(v, S):
                v = v.dict()
            elif isinstance(v, C.Array):
                v = [x.dict() if isinstance(x, S) else (list(x) if isinstance(x, C.Array) else x) for x in v]
            out[name] = v
        return out


class Roi(S):
    _fields_ = [("left", u16), ("top", u16), ("width", u16), ("height", u16)]


class Bg(S):
    _fields_ = [("roi", Roi), ("h_num", u16), ("v_num", u16), ("threshold_r", u32), ("threshold_b", u32),
                ("threshold_gr", u32), ("threshold_gb", u32), ("black_level_offset", u32), ("y_weight_q4", u8 * 3),
                ("quad_sync_enable", b8), ("enabled", b8), ("controls_valid", b8)]


class Rs(S):
    _fields_ = [("roi", Roi), ("h_num", u16), ("v_num", u16), ("color_conversion", b8)]


class Stats(S):
    _fields_ = [("request_id", u64), ("phase", u8), ("active_width", u16), ("active_height", u16), ("bhist", Roi),
                ("rs", Rs), ("aec", Bg), ("tintless", Bg), ("awb", Bg)]


class Cst(S):
    _fields_ = [("enabled", b8)] + [(n, u16) for n in ("c00", "c10", "c20", "c01", "c11", "c21")] + \
               [(n, s16) for n in ("m00", "m01", "m02", "m10", "m11", "m12", "m20", "m21", "m22",
                                   "o0", "o1", "o2", "s0", "s1", "s2")]


class BpcAbf(S):
    _fields_ = [("signed10", s16 * 2), ("unsigned9", u16 * 2), ("nibble4", u8 * 2), ("byte_group0", (u8 * 4) * 2),
                ("byte_group1", (u8 * 4) * 2), ("nibble_group", (u8 * 4) * 2)]


class Iq(S):
    _fields_ = [("request_id", u64), ("phase", u8), ("active_width", u16), ("active_height", u16),
                ("af", Roi), ("cst", Cst), ("bpcabf", BpcAbf), ("controls_valid", b8)]


class Adaptive(S):
    _fields_ = [("request_id", u64), ("phase", u8), ("valid", b8), ("lsc1", u8 * 884), ("lsc2", u8 * 884),
                ("gtm", u8 * 2048)]


class Geometry(S):
    _fields_ = [("sensor_width", u16), ("sensor_height", u16), ("isp_width", u16), ("isp_height", u16),
                ("output_width", u16), ("output_height", u16), ("bit_width", u8), ("request_id", u64 * P)]


class Input(S):
    _fields_ = [("request_id", u64 * P), ("scalars", u8 * 208), ("geometry", Geometry), ("stats", Stats * P),
                ("iq", Iq * P), ("adaptive", Adaptive * P)]


assert C.sizeof(Input) == 16672, C.sizeof(Input)

SCALARS_MAGIC = 0x3153524E


def pack_scalars(request_ids, demux_q10, wb_r_q10, wb_b_q10):
    """208-byte scalar envelope. PDPC per-channel gains follow white balance:
    R, B gains and their inverses in Q12 (G = 1)."""
    import struct
    out = bytearray(208)
    struct.pack_into("<IHHII", out, 0, SCALARS_MAGIC, 1, 208, P, 0)
    r, b = wb_r_q10 / 1024.0, wb_b_q10 / 1024.0
    pdpc = [round(r * 4096), round(b * 4096), round(4096 / r), round(4096 / b)]
    for p in range(P):
        o = 16 + 48 * p
        struct.pack_into("<QII", out, o, request_ids[p], p, 0)
        struct.pack_into("<4H", out, o + 16, *demux_q10)
        struct.pack_into("<4I", out, o + 24, *pdpc)
        struct.pack_into("<HHI", out, o + 40, wb_b_q10, wb_r_q10, 0)
    return bytes(out)
