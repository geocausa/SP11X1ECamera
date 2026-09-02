#!/usr/bin/env python3
"""Fail-closed exact replay proof for the 2026-09-02 Surface GTM live capture.

The proprietary DeviceMFT and raw Windows captures remain local/untracked.  This
script maps the exact SHA-pinned ARM64 PE into Unicorn and executes the Surface
GTM helper implementations themselves for the dynamic generation-5/mode-2 path.
Only derived hashes/scalars are suitable for the tracked oracle JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

try:
    import pefile
    from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_INVALID
    from unicorn.arm64_const import *
except Exception as exc:  # fail closed
    raise SystemExit(f"missing proof dependency (pefile/unicorn): {exc}")

BASE = 0x180000000
DEVICE_MFT_SHA256 = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
CAPTURE_ZIP_SHA256 = "429102b00ca808bd9680ae9f1d309610c701ff541763f1236fd2a0dea342cb71"

RVA = {
    "gtm131_hw_setting": 0x9AA6E0,
    "mode2_cubic_map": 0x9A4F38,
    "tmc_domain_map": 0x9A55C8,
    "final_adaptive_map": 0x9AA3A8,
    "titan680_packer": 0xB5B3D0,
    "mode2_domain": 0x1689340,
    "titan_x_grid": 0x1689750,
}

EXPECTED_OUT_SHA256 = {
    4: "656d35c87e95b376f3d6b4eac7624c3387e1857100cf5529f5ae7e2a87ec7f43",
    5: "9e54b3b16a6a146f9f1f448150a88a929c2ffe3cd4c8aa93e98e5498afb0216e",
    6: "89bc45b890f6508912bad1b543c7f7ad56e20b6794fdc908455e9f47c967cf95",
}

TRIGGER_FIELDS = {
    "ET": (0x00, "f"),
    "RATIO": (0x04, "f"),
    "SENS": (0x2C, "f"),
    "GAIN": (0x30, "f"),
    "LUX": (0x38, "f"),
    "AWBG": (0x3C, "f"),
    "AWBB": (0x40, "f"),
    "AWBR": (0x44, "f"),
    "CCT": (0x48, "f"),
    "DRC": (0x74, "f"),
    "LENS": (0x7C, "f"),
    "BLACK": (0xF0, "I"),
}
TRIGGER_BASE = 0x2080

GEOMETRY_FIELDS = {
    "output_width": (0x24, "I"),
    "output_height": (0x28, "I"),
    "full_width": (0x1C, "I"),
    "full_height": (0x20, "I"),
    "offset_x": (0x2C, "I"),
    "offset_y": (0x30, "I"),
    "scale": (0x3C, "I"),
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def f32(v: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(v)))[0]


def s32(v: int) -> int:
    return v if v < (1 << 31) else v - (1 << 32)


def unpack_scalar(buf: bytes, off: int, typ: str):
    return struct.unpack_from("<" + typ, buf, off)[0]


class SurfaceEmu:
    def __init__(self, dll: Path):
        if sha256_file(dll) != DEVICE_MFT_SHA256:
            raise RuntimeError("DeviceMFT SHA-256 mismatch")
        self.dll = dll
        self.pe = pefile.PE(str(dll), fast_load=False)
        raw = dll.read_bytes()
        image_size = (self.pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF
        self.uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        self.uc.mem_map(BASE, image_size)
        self.uc.mem_write(BASE, raw[: self.pe.OPTIONAL_HEADER.SizeOfHeaders])
        for section in self.pe.sections:
            data = section.get_data()
            if data:
                self.uc.mem_write(BASE + section.VirtualAddress, data)

        self.stack = 0x40000000
        self.heap = 0x50000000
        self.stop = 0x60000000
        self.uc.mem_map(self.stack, 0x400000)
        self.uc.mem_map(self.heap, 0x400000)
        self.uc.mem_map(self.stop, 0x1000)
        self.uc.mem_write(self.stop, b"\xc0\x03\x5f\xd6")  # ret

        def invalid(uc, access, address, size, value, user_data):
            pc = uc.reg_read(UC_ARM64_REG_PC)
            raise RuntimeError(f"unmapped access={access} address=0x{address:x} size={size} pc=0x{pc:x}")
        self.uc.hook_add(UC_HOOK_MEM_INVALID, invalid)

    def run(self, rva: int, xargs=(), sargs=(), instruction_limit=20_000_000):
        uc = self.uc
        uc.reg_write(UC_ARM64_REG_SP, self.stack + 0x3FF000)
        for i, value in enumerate(xargs):
            uc.reg_write(UC_ARM64_REG_X0 + i, int(value) & ((1 << 64) - 1))
        for i, value in enumerate(sargs):
            bits = struct.unpack("<I", struct.pack("<f", float(value)))[0]
            uc.reg_write(UC_ARM64_REG_S0 + i, bits)
        uc.reg_write(UC_ARM64_REG_X30, self.stop)

        def stop_hook(uc, address, size, user_data):
            if address == self.stop:
                uc.emu_stop()

        hook = uc.hook_add(UC_HOOK_CODE, stop_hook)
        try:
            uc.emu_start(BASE + rva, 0, count=instruction_limit)
        finally:
            uc.hook_del(hook)
        if uc.reg_read(UC_ARM64_REG_PC) != self.stop:
            raise RuntimeError(f"RVA 0x{rva:x} failed to return cleanly")


def decode_live_request(capture_dir: Path, request: int) -> dict:
    isp = (capture_dir / f"REQ{request}_ISPINPUT.bin").read_bytes()
    mod = (capture_dir / f"REQ{request}_GTM_MODULE.bin").read_bytes()
    tmc = (capture_dir / f"REQ{request}_GTM_TMC.bin").read_bytes()
    out = (capture_dir / f"REQ{request}_GTM_OUT.bin").read_bytes()
    lsc_common = (capture_dir / f"REQ{request}_LSC_COMMON.bin").read_bytes()
    if len(isp) < 0x2180 or len(mod) < 0x220 or len(tmc) < 0x6328 or len(out) != 0x800 or len(lsc_common) < 0x40:
        raise RuntimeError(f"request{request}: unexpected capture sizes")

    common = mod[0xA8:0xA8 + 0x80]
    generation = struct.unpack_from("<I", tmc, 0x08)[0]
    hw_version = struct.unpack_from("<I", tmc, 0x0C)[0]
    valid = struct.unpack_from("<I", tmc, 0x10)[0]
    mode = struct.unpack_from("<I", tmc, 0x74)[0]
    common_hw = struct.unpack_from("<I", common, 0x34)[0]
    common_sensor_bit = struct.unpack_from("<H", common, 0x2A)[0]
    common_enable = common[0x70]
    common_strength = struct.unpack_from("<f", common, 0x74)[0]
    common_power = struct.unpack_from("<f", common, 0x78)[0]
    expected = (5, 0x60800, 1, 2, 0x60800, 1, 1)
    actual = (generation, hw_version, valid, mode, common_hw, common_sensor_bit, common_enable)
    if actual != expected:
        raise RuntimeError(f"request{request}: GTM branch mismatch {actual!r} != {expected!r}")
    if struct.pack("<f", common_strength) != struct.pack("<f", 0.8500000238418579):
        raise RuntimeError(f"request{request}: GTM common +0x74 mismatch")
    if struct.pack("<f", common_power) != struct.pack("<f", 1.0):
        raise RuntimeError(f"request{request}: GTM common +0x78 mismatch")
    tone_prefix = tmc[0x6228:0x6328]
    if len(tone_prefix) != 0x100 or any(tone_prefix):
        raise RuntimeError(f"request{request}: expected zero captured tone-domain prefix")
    if sha256_bytes(out) != EXPECTED_OUT_SHA256[request]:
        raise RuntimeError(f"request{request}: GTM output SHA mismatch")

    triggers = {}
    for name, (off, typ) in TRIGGER_FIELDS.items():
        value = unpack_scalar(isp, TRIGGER_BASE + off, typ)
        raw = isp[TRIGGER_BASE + off:TRIGGER_BASE + off + struct.calcsize("<" + typ)]
        triggers[name] = {"value": value, "raw_hex": raw.hex()}
    geometry = {name: unpack_scalar(lsc_common, off, typ) for name, (off, typ) in GEOMETRY_FIELDS.items()}

    return {
        "isp": isp,
        "module": mod,
        "tmc": tmc,
        "out": out,
        "lsc_common": lsc_common,
        "common": common,
        "triggers": triggers,
        "geometry": geometry,
        "branch": {
            "generation": generation,
            "hardware_version": f"0x{hw_version:x}",
            "valid": valid,
            "mode": mode,
            "common_sensor_selector_halfword": common_sensor_bit,
            "common_enable": common_enable,
            "common_strength": common_strength,
            "common_power": common_power,
        },
    }


def replay_request(emu: SurfaceEmu, request: int, live: dict) -> dict:
    uc = emu.uc
    TMC = emu.heap
    OUT = emu.heap + 0x10000
    LOC = emu.heap + 0x20000
    PU = BASE + RVA["mode2_domain"]
    PF = BASE + RVA["titan_x_grid"]

    # Only +0x6228..+0x6327 was captured from the large tone domain.  Both
    # captured blend scalars at +0x109c/+0x10a0 are exactly zero, so the
    # domain value is algebraically multiplied away.  Fill the uncaptured tail
    # with a finite non-zero sentinel to prove the replay does not depend on
    # assuming zero bytes there.
    uc.mem_write(TMC, b"\0" * 0x8000)
    uc.mem_write(TMC, live["tmc"])
    sentinel = struct.pack("<f", 0.25) * ((0x7228 - 0x6328) // 4)
    uc.mem_write(TMC + 0x6328, sentinel)
    uc.mem_write(OUT, b"\0" * 0x1200)

    # AAPCS64 mixed FP/integer register classes are independent.  Execute the
    # exact Surface mode-2 cubic mapper using the captured internal TMC state.
    emu.run(
        RVA["mode2_cubic_map"],
        [TMC + 0x5104, TMC + 0x5120, TMC + 0x51B0, PU, OUT, 0x100],
    )
    cubic = bytes(uc.mem_read(OUT, 0x404))

    # Exact Surface TMC-domain mapper.  For 0x60800 the +0x6228 source-domain
    # length is the non-0x60400 branch; the captured 0x1000-byte domain is zero.
    emu.run(
        RVA["tmc_domain_map"],
        [PU, OUT, TMC, TMC + 0x6228, 12, 0, 0x100],
        [1.0],
    )
    mapped = bytes(uc.mem_read(OUT, 0x404))
    mapped_f = struct.unpack("<257f", mapped)

    # The main GTM function widens the clamped 257 float values to doubles.
    local = b"".join(struct.pack("<d", float(max(0.0, value))) for value in mapped_f)
    uc.mem_write(LOC, local)

    # Exact Surface final adaptive map.  Common +0x78/+0x74 are s0/s1; integer
    # args are local-double pointer, +0x70 byte, iVar8=10, iVar16=12, domain.
    emu.run(
        RVA["final_adaptive_map"],
        [LOC, 1, 10, 12, PU],
        [1.0, 0.8500000238418579],
    )
    local_d = struct.unpack("<257d", bytes(uc.mem_read(LOC, 257 * 8)))
    x_grid = struct.unpack("<257f", bytes(uc.mem_read(PF, 257 * 4)))

    # Reproduce the exact setting loop.  On this branch every computed slope is
    # safely |slope| < 0.5, so the Surface log2-derived exponent necessarily
    # clamps to its maximum 30; no libm boundary decision remains here.
    packed = bytearray()
    max_abs_slope = 0.0
    slope_saturated = 0
    for i in range(256):
        base_value = int(local_d[i] + 0.5)
        if i < 255:
            dx = int(f32(x_grid[i + 1] - x_grid[i]))
        else:
            dx = (0x3FFF - int(x_grid[i])) + 1
        if dx < 1 or local_d[i + 1] == local_d[i]:
            slope = 0.0
        else:
            slope = f32(f32(local_d[i + 1] - local_d[i]) / float(dx))
        max_abs_slope = max(max_abs_slope, abs(slope))
        if abs(slope) >= 0.5:
            raise RuntimeError(f"request{request}: exponent-30 proof no longer safe at index {i}")
        shift = 30
        scaled = f32(f32((2.0 ** shift) * slope) + 0.5)
        slope_i = int(scaled)
        clamped = max(-0x2000000, min(0x1FFFFFF, slope_i))
        slope_saturated += int(clamped != slope_i)
        word = (
            (base_value & 0x3FFFFF)
            | ((clamped & 0x3FFFFFF) << 22)
            | ((shift & 0x1F) << 48)
        )
        packed += struct.pack("<Q", word)

    packed = bytes(packed)
    if packed != live["out"]:
        diffs = [i for i, (a, b) in enumerate(zip(packed, live["out"])) if a != b]
        raise RuntimeError(
            f"request{request}: replay mismatch: {len(diffs)} bytes, first=0x{diffs[0]:x}, last=0x{diffs[-1]:x}"
        )

    return {
        "exact_qwords": 256,
        "exact_bytes": 0x800,
        "byte_equal": True,
        "replay_sha256": sha256_bytes(packed),
        "oracle_sha256": sha256_bytes(live["out"]),
        "cubic_stage_sha256": sha256_bytes(cubic),
        "mapped_stage_sha256": sha256_bytes(mapped),
        "post_adaptive_local_double_sha256": sha256_bytes(struct.pack("<257d", *local_d)),
        "max_abs_slope": max_abs_slope,
        "slope_saturation_count": slope_saturated,
        "first_word": f"0x{struct.unpack_from('<Q', packed, 0)[0]:016x}",
        "last_word": f"0x{struct.unpack_from('<Q', packed, 0x7F8)[0]:016x}",
    }


def main() -> int:
    here = Path(__file__).resolve().parent
    repo = here.parents[3]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--device-mft",
        type=Path,
        default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"),
    )
    parser.add_argument("--capture-dir", type=Path, default=here / "windows-adaptive-live-20260902")
    parser.add_argument("--matched-triggers", type=Path, default=here / "windows-request4-6-matched-triggers.json")
    parser.add_argument("--out", type=Path, default=here / "gtm-live-exact-replay-oracle.json")
    args = parser.parse_args()

    emu = SurfaceEmu(args.device_mft)
    live_requests = {request: decode_live_request(args.capture_dir, request) for request in (4, 5, 6)}
    replays = {request: replay_request(emu, request, live_requests[request]) for request in (4, 5, 6)}

    geometry = [live_requests[r]["geometry"] for r in (4, 5, 6)]
    if not all(g == geometry[0] for g in geometry[1:]):
        raise RuntimeError("live request4/5/6 geometry is not invariant")
    expected_geometry = {
        "output_width": 3840,
        "output_height": 2160,
        "full_width": 4048,
        "full_height": 3152,
        "offset_x": 104,
        "offset_y": 496,
        "scale": 1,
    }
    if geometry[0] != expected_geometry:
        raise RuntimeError(f"unexpected geometry: {geometry[0]!r}")

    # This live producer session is intentionally classified separately from the
    # earlier matched request4/5/6 DMI oracle; trigger vectors prove they differ.
    matched_equal = None
    if args.matched_triggers.exists():
        old = json.loads(args.matched_triggers.read_text())
        matched_equal = True
        for request in (4, 5, 6):
            old_req = old["requests"][f"request{request}"]
            for key in ("GAIN", "LUX", "AWBB", "AWBR", "CCT", "DRC"):
                if live_requests[request]["triggers"][key]["raw_hex"] != old_req[key]["raw_hex"].removeprefix("0x"):
                    matched_equal = False
                    break
    if matched_equal is True:
        raise RuntimeError("live session unexpectedly aliases the earlier matched trigger session")

    file_hashes = {}
    for request in (4, 5, 6):
        for kind in ("ISPINPUT", "GTM_MODULE", "GTM_TMC", "GTM_OUT", "LSC_COMMON"):
            path = args.capture_dir / f"REQ{request}_{kind}.bin"
            file_hashes[path.name] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}

    dynamic_ranges = {
        "header_0x0008_0x0013": False,
        "mode_0x0074_0x0077": False,
        "blend_0x109c_0x10a3": False,
        "source_knots_0x5104_0x511f": True,
        "target_knots_0x5120_0x513b": True,
        "cubic_0x51b0_0x51eb": True,
        "tone_domain_prefix_0x6228_0x6327": False,
    }
    # Verify the declared dynamic/invariant classification directly.
    tmc = [live_requests[r]["tmc"] for r in (4, 5, 6)]
    ranges = {
        "header_0x0008_0x0013": (0x8, 0xC),
        "mode_0x0074_0x0077": (0x74, 4),
        "blend_0x109c_0x10a3": (0x109C, 8),
        "source_knots_0x5104_0x511f": (0x5104, 0x1C),
        "target_knots_0x5120_0x513b": (0x5120, 0x1C),
        "cubic_0x51b0_0x51eb": (0x51B0, 0x3C),
        "tone_domain_prefix_0x6228_0x6327": (0x6228, 0x100),
    }
    for name, (off, length) in ranges.items():
        changes = not (tmc[0][off:off+length] == tmc[1][off:off+length] == tmc[2][off:off+length])
        if changes != dynamic_ranges[name]:
            raise RuntimeError(f"dynamic-range classification changed for {name}: {changes}")

    mode2_domain = bytes(emu.uc.mem_read(BASE + RVA["mode2_domain"], 0x404))
    titan_x_grid = bytes(emu.uc.mem_read(BASE + RVA["titan_x_grid"], 0x404))

    oracle = {
        "schema": "sp11-e003h-0073-gtm-live-exact-replay-v1",
        "accepted": True,
        "classification": "CLOSED LIVE/OFFLINE GTM PRODUCER REPLAY: exact Surface ARM64 adaptive helpers plus Titan680 setting math reproduce request4/5/6 GTM0 byte-for-byte in an independent Windows producer session.",
        "safety": {
            "linux_camera_runtime_executed": False,
            "linux_request6_executed": False,
            "linux_request6_authorized": False,
            "raw_windows_captures_tracked": False,
        },
        "source_authority": {
            "device_mft_sha256": DEVICE_MFT_SHA256,
            "capture_zip_sha256": CAPTURE_ZIP_SHA256,
            "capture_session": "E003H_ADAPTIVE_0073_LIVE_20260902",
            "capture_session_equals_prior_matched_trigger_session": matched_equal,
        },
        "exact_rvas": {name: f"0x{rva:x}" for name, rva in RVA.items()},
        "static_surface_tables": {
            "mode2_domain_bytes": len(mode2_domain),
            "mode2_domain_sha256": sha256_bytes(mode2_domain),
            "titan_x_grid_bytes": len(titan_x_grid),
            "titan_x_grid_sha256": sha256_bytes(titan_x_grid),
        },
        "live_geometry": expected_geometry,
        "tmc_branch": {
            "generation": 5,
            "hardware_version": "0x60800",
            "valid": 1,
            "mode": 2,
            "common_strength_float": 0.8500000238418579,
            "common_power_float": 1.0,
            "captured_tone_domain_prefix_bytes": 256,
            "captured_tone_domain_prefix_all_zero": True,
            "uncaptured_tone_domain_tail_required_for_replay": False,
            "reason_tone_domain_tail_irrelevant": "both generation-5 blend scalars at +0x109c/+0x10a0 are exactly 0.0; exact replay still matches when the uncaptured tail is filled with finite non-zero sentinel values",
        },
        "bounded_tmc_range_changes_4_to_6": dynamic_ranges,
        "requests": {},
        "capture_file_hashes": file_hashes,
        "gate": "GTM producer replay is closed for this live session. Do not conflate it with the earlier matched request6 stream. Remaining independent wire closure is LSC0/LSC1 sequential calibration/Tintless/ALSC replay; wire GIC follows the proven LSC alias. Linux request6 remains forbidden.",
    }
    for request in (4, 5, 6):
        oracle["requests"][f"request{request}"] = {
            "triggers": live_requests[request]["triggers"],
            "replay": replays[request],
        }

    args.out.write_text(json.dumps(oracle, indent=2, sort_keys=True) + "\n")
    print("PASS exact GTM live replay")
    for request in (4, 5, 6):
        r = replays[request]
        print(f"  request{request}: {r['exact_qwords']}/256 qwords, sha256={r['replay_sha256']}")
    print(f"  geometry: {expected_geometry}")
    print(f"  prior matched trigger session equal: {matched_equal}")
    print(f"  oracle: {args.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
