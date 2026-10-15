# SPDX-License-Identifier: GPL-2.0-only
"""Shared model of the SP11 front (imx681, 2560x1440 NV12) ISP startup profile.

The profile file is a data-only carrier: a 64-byte header, then the register
values and DMI table bytes that the camss driver places into its own CDM
instruction topology (native-front-profile-schema.h, which holds no data).
This module labels every profile word with what it programs, so a profile can
be generated from readable sources and any two profiles can be compared.
"""
import re
import struct

MAGIC = b"QXTPRF01"
HEADER = 64

# Steady per-module records (section type 4): module order of
# enum camss_x1e_epoch0_iq_module and its value -> register patch table v0.
MODULES = ["DEMUX_BLS", "PDPC", "LSC", "WB", "GIC", "BPC_ABF", "GTM", "GAMMA", "DSX"]
RECORD_REG = {
    (0, 0): 0x3b70, (0, 1): 0x3b74,
    (1, 0): 0x3d58, (1, 1): 0x3d5c, (1, 2): 0x3d78, (1, 3): 0x3d7c, (1, 4): 0x3d80, (1, 5): 0x3d84,
    (2, 0): 0x4358, (2, 1): 0x435c,
    (3, 0): 0x456c, (3, 1): 0x4570,
    (4, 0): 0x4758, (4, 1): 0x475c,
    (5, 0): 0x4958, (5, 1): 0x495c,
    (6, 0): 0x5a58, (6, 1): 0x5a5c,
    (7, 0): 0x5f58, (7, 1): 0x5f5c,
    (8, 0): 0xa058, (8, 1): 0xa05c, (8, 2): 0xa258, (8, 3): 0xa25c,
}

# DMI payload sections -> (table, selector). Startup payloads (type 2) from the
# corpus DMI references, steady payloads (type 5) from camss_x1e_epoch0_payloads.
TABLES = {
    (2, 0): ("PDPC", 1), (2, 1): ("BAYER_5408", 1), (2, 2): ("DSX_A008", 1), (2, 3): ("GIC", 1),
    (2, 4): ("GAMMA", 0), (2, 5): ("BF_B208", 2), (2, 6): ("LSC", 1), (2, 7): ("LSC", 2),
    (2, 8): ("LSC", 3), (2, 9): ("DSX_A208", 1), (2, 10): ("LSC", 1), (2, 11): ("BF_B208", 1),
    (2, 12): ("GTM", 1), (2, 13): ("GIC", 1), (2, 14): ("BPC_ABF", 1), (2, 15): ("LSC", 2),
    (5, 0): ("PDPC", 1), (5, 1): ("LSC", 1), (5, 2): ("LSC", 2), (5, 3): ("LSC", 3),
    (5, 4): ("GIC", 1), (5, 5): ("BPC_ABF", 1), (5, 6): ("GTM", 1), (5, 7): ("GAMMA", 1),
    (5, 8): ("GAMMA", 2), (5, 9): ("GAMMA", 3), (5, 10): ("DSX_A008", 1), (5, 11): ("DSX_A008", 2),
    (5, 12): ("DSX_A208", 1), (5, 13): ("DSX_A208", 2),
}


def le(b, o):
    return struct.unpack_from("<I", b, o)[0]


class Schema:
    def __init__(self, path):
        t = open(path).read()
        self.defs = {k: int(v.rstrip("U"), 0) for k, v in
                     re.findall(r"#define (NATIVE_FRONT_PROFILE_\w+) ([0-9xa-fA-FU]+)\b", t)}
        fx = t[t.index("native_front_profile_fixed[]"):t.index("native_front_profile_copies[]")]
        cp = t[t.index("native_front_profile_copies[]"):]
        self.fixed = [(int(a, 16), int(b, 16)) for a, b in re.findall(r"\{ (0x[0-9a-f]+), (0x[0-9a-f]+) \}", fx)]
        self.copies = [(int(a, 16), int(b, 16), int(c, 16)) for a, b, c in
                       re.findall(r"\{ (0x[0-9a-f]+), (0x[0-9a-f]+), (0x[0-9a-f]+) \}", cp)]
        d = t[t.index("digest[32]"):]
        self.digest = bytes(int(x, 16) for x in re.findall(r"0x([0-9a-f]{2})", d[:d.index("};")]))
        self.size = self.defs["NATIVE_FRONT_PROFILE_BYTES"]
        self.capsule_size = self.defs["NATIVE_FRONT_PROFILE_CAPSULE_BYTES"]
        self.words = self._label()

    def identity(self):
        d = self.defs
        return [1, HEADER, self.size, 0x80100, 2560, 1440, 3840, 2160, 0x3231564E,
                d["NATIVE_FRONT_PROFILE_SCALAR_WORDS"], d["NATIVE_FRONT_PROFILE_TABLE_BYTES"], 0, 0, 0]

    def materialize(self, data):
        out = bytearray(self.capsule_size)
        out[0:8] = b"E3HPIX01"
        for dst, v in self.fixed:
            out[dst:dst + 4] = struct.pack("<I", v)
        for dst, src, n in self.copies:
            out[dst:dst + n] = data[src:src + n]
        return out

    @staticmethod
    def sections(cap):
        return [dict(type=le(cap, 64 + 16 * i), index=le(cap, 68 + 16 * i),
                     off=le(cap, 72 + 16 * i), size=le(cap, 76 + 16 * i)) for i in range(le(cap, 0x14))]

    @staticmethod
    def walk(cap, off, size):
        p, end = off, off + size
        while p < end:
            h = le(cap, p)
            op, n = h >> 24, h & 0xFFFF
            if op == 3:
                reg = le(cap, p + 4)
                for i in range(n):
                    yield p + 8 + 4 * i, reg + 4 * i
                p += 8 + 4 * n
            elif op == 1:
                p += 12
            else:
                raise ValueError("unexpected CDM opcode 0x%x at 0x%x" % (op, p))

    def _label(self):
        """profile word offset -> label tuple."""
        cap = self.materialize(bytes(self.size))
        lab = {}
        for s in self.sections(cap):
            t, i = s["type"], s["index"]
            if t in (1, 3):
                key = "P%d" % i if t == 1 else "S"
                for o, reg in self.walk(cap, s["off"], s["size"]):
                    lab[o] = ("reg", reg, key)
            elif t == 4:
                for o in range(s["off"], s["off"] + s["size"], 4):
                    k = o - s["off"]
                    m, j = divmod(k, 32)
                    if j == 0:
                        lab[o] = ("const", "mod%d.flags" % m)
                    elif j == 28:
                        lab[o] = ("const", "mod%d.pad" % m)
                    else:
                        v = (j - 4) // 4
                        reg = RECORD_REG.get((m, v))
                        lab[o] = ("reg", reg, "M") if reg else ("const", "mod%d.v%d" % (m, v))
            else:
                for o in range(s["off"], s["off"] + s["size"], 4):
                    lab[o] = ("table", t, i, o - s["off"])
        for o in range(0x18, 0x28, 4):
            lab[o] = ("const", "dyn%d" % ((o - 0x18) // 4))
        words = {}
        for dst, src, n in self.copies:
            for k in range(0, n, 4):
                if dst + k not in lab:
                    raise ValueError("unlabelled profile word 0x%x -> capsule 0x%x" % (src + k, dst + k))
                words[src + k] = lab[dst + k]
        covered = set(words)
        expect = set(range(HEADER, self.size, 4))
        if covered != expect:
            raise ValueError("profile words not covered exactly: %d missing, %d extra" %
                             (len(expect - covered), len(covered - expect)))
        return words


def read_regs(path):
    """Register source: lines 'REG[@SECTION] VALUE  # note' or 'NAME VALUE'."""
    regs = {}
    for ln in open(path):
        ln = ln.split("#", 1)[0].strip()
        if not ln:
            continue
        key, val = ln.split()
        if ".." in key:  # inclusive register range, same value in every section
            a, b = (int(x, 16) for x in key.split(".."))
            for reg in range(a, b + 4, 4):
                regs[(reg, None)] = int(val, 0)
                regs.setdefault("_ranged", set()).add((reg, None))
        elif key.startswith("0x"):
            reg, _, sec = key.partition("@")
            regs[(int(reg, 16), sec or None)] = int(val, 0)
        else:
            regs[key] = int(val, 0)
    return regs


def reg_value(regs, reg, sec):
    if (reg, sec) in regs:
        return regs[(reg, sec)], (reg, sec)
    if (reg, None) in regs:
        return regs[(reg, None)], (reg, None)
    raise KeyError("no value for register 0x%04x (%s)" % (reg, sec))
