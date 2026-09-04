#!/usr/bin/env python3
"""Fail-closed native replay of the 2026-09-04 verified-front atomic Tintless capsule.

Raw Windows captures stay local/untracked.  The proof SHA-pins every capture via
FRONT-ATOMIC-TINTLESS-STAGING-20260904.json and the exact Surface DeviceMFT,
executes TintlessAlgorithmWrapper::Process for request4 -> request5 -> request6
in one Unicorn instance, and requires byte-exact Windows wrapper/core/output
state.  Request4 lazy allocation is serviced by an emulator-only allocator shim;
no DeviceMFT instruction is patched.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import struct
from pathlib import Path

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm64_const import (
    UC_ARM64_REG_X0, UC_ARM64_REG_X2, UC_ARM64_REG_X18,
)

DEVICE_MFT_SHA256 = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
CALLBACK_RVA = 0xC95FD0
CORE_BYTES = 0x126E8
CORE_READ_HI = 0x12694
MESH_ARRAY_BYTES = 0x374
MESH_CHANNELS = 4
MESH_PAYLOAD_BYTES = MESH_ARRAY_BYTES * MESH_CHANNELS  # 0xdd0
MESH_CAPTURE_BYTES = 0xDF0  # includes adjacent, unreferenced 0x20 capture tail
EXPECTED_GEOMETRY = (3840, 2160, 120, 90, 32, 24, 0)
ALLOC_IAT_RVA = 0xF7E280
ALLOC_WRAPPER_CODE = {
    0xCB16EC: "681600b0",  # adrp x8, IAT page
    0xCB16F0: "084141f9",  # ldr x8,[x8,#0x280]
    0xCB16F4: "e20313aa",  # mov x2,x19 (allocation bytes)
    0xCB16F8: "01008052",  # mov w1,#0
    0xCB16FC: "00013fd6",  # blr x8
}
INTERFACE_LOAD_CODE = {0xC9600C: "160c40f9"}  # ldr x22,[x0,#0x18]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify_capture(cap: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("camera") != "IMX681 front":
        raise RuntimeError("atomic manifest camera identity is not IMX681 front")
    hashes = manifest.get("hashes", {})
    if len(hashes) != 44:
        raise RuntimeError(f"expected 44 atomic raw captures, manifest has {len(hashes)}")
    for name, meta in hashes.items():
        p = cap / name
        if not p.is_file():
            raise RuntimeError(f"missing atomic capture {name}")
        b = p.read_bytes()
        if len(b) != int(meta["bytes"]) or sha(b) != meta["sha256"]:
            raise RuntimeError(f"atomic capture size/SHA drift: {name}")

    for r in (4, 5, 6):
        x1 = (cap / f"req{r}_x1_config.bin").read_bytes()
        if len(x1) != 0x130 or struct.unpack_from("<7I", x1, 0x1C) != EXPECTED_GEOMETRY:
            raise RuntimeError(f"request{r}: front Tintless geometry drift")
        x2 = (cap / f"req{r}_x2_stats.bin").read_bytes()
        if len(x2) != 0x12BEC or struct.unpack_from("<I", x2, 4)[0] != 0x300:
            raise RuntimeError(f"request{r}: saturated Tintless stats contract drift")
        for k in (3, 4):
            desc = (cap / f"req{r}_x{k}_desc.bin").read_bytes()
            if len(desc) != 0x28 or struct.unpack_from("<H", desc, 0)[0] != 221:
                raise RuntimeError(f"request{r}: x{k} descriptor contract drift")
            ptrs = struct.unpack_from("<4Q", desc, 8)
            if any(ptrs[i + 1] - ptrs[i] != MESH_ARRAY_BYTES for i in range(3)):
                raise RuntimeError(f"request{r}: x{k} mesh pointers are not four contiguous 0x374 arrays")

    pairs = [
        ("req4_wrapper_post.bin", "req5_wrapper_pre.bin"),
        ("req4_core_post.bin", "req5_core_pre.bin"),
        ("req5_wrapper_post.bin", "req6_wrapper_pre.bin"),
        ("req5_core_post.bin", "req6_core_pre.bin"),
    ]
    continuity = {}
    for a, b in pairs:
        equal = (cap / a).read_bytes() == (cap / b).read_bytes()
        continuity[f"{a}=={b}"] = equal
        if not equal:
            raise RuntimeError(f"atomic state continuity failed: {a} != {b}")
    if struct.unpack_from("<Q", (cap / "req4_wrapper_pre.bin").read_bytes(), 0x128)[0] != 0:
        raise RuntimeError("request4 lazy core pointer is unexpectedly non-null before initialization")
    return {"manifest": manifest, "continuity": continuity}


def verify_device_bytes(dll: Path, surface_mod) -> dict:
    if sha_file(dll) != DEVICE_MFT_SHA256:
        raise RuntimeError("DeviceMFT SHA mismatch")
    emu = surface_mod.SurfaceEmu(dll)
    out = {}
    for rva, want in {**ALLOC_WRAPPER_CODE, **INTERFACE_LOAD_CODE}.items():
        got = bytes(emu.uc.mem_read(surface_mod.BASE + rva, 4)).hex()
        if got != want:
            raise RuntimeError(f"DeviceMFT code drift at RVA 0x{rva:x}: {got} != {want}")
        out[f"0x{rva:x}"] = got
    return out


def desc_ptr(cap: Path, req: int, which: int) -> int:
    return struct.unpack_from("<Q", (cap / f"req{req}_x{which}_desc.bin").read_bytes(), 8)[0]


def replay_sequence(cap: Path, dll: Path, surface_mod, allocation_fill: int) -> dict:
    e = surface_mod.SurfaceEmu(dll)
    u = e.uc
    IFACE = 0x260000000000
    WRAP = 0x260000001000
    X1 = 0x260000003000
    X2 = {4: 0x260000010000, 5: 0x260000030000, 6: 0x260000050000}
    D3 = {4: 0x260000070000, 5: 0x260000072000, 6: 0x260000074000}
    D4 = {4: 0x260000071000, 5: 0x260000073000, 6: 0x260000075000}
    STUB = 0x62000000

    def amap(addr: int, size: int) -> None:
        base = addr & ~0xFFF
        end = (addr + size + 0xFFF) & ~0xFFF
        try:
            u.mem_map(base, end - base)
        except Exception as exc:
            if "UC_ERR_MAP" not in str(exc):
                raise

    def put(addr: int, name: str, pad: int = 0) -> bytes:
        b = (cap / name).read_bytes()
        amap(addr, max(len(b), pad))
        u.mem_write(addr, b)
        return b

    teb = 0x70000000
    amap(teb, 0x1000)
    u.mem_write(teb + 0x10, e.stack.to_bytes(8, "little"))
    u.reg_write(UC_ARM64_REG_X18, teb)

    amap(IFACE, 0x1000)
    u.mem_write(IFACE, b"\0" * 0x1000)
    u.mem_write(IFACE + 0x18, WRAP.to_bytes(8, "little"))

    req4_post = (cap / "req4_wrapper_post.bin").read_bytes()
    core_addr = struct.unpack_from("<Q", req4_post, 0x128)[0]
    if not core_addr:
        raise RuntimeError("captured request4 post core pointer is null")

    amap(STUB, 0x1000)
    u.mem_write(STUB, b"\xc0\x03\x5f\xd6")  # ret
    u.mem_write(surface_mod.BASE + ALLOC_IAT_RVA, STUB.to_bytes(8, "little"))
    allocations = []

    def alloc_hook(uc, address, size, user_data):
        n = uc.reg_read(UC_ARM64_REG_X2)
        allocations.append(n)
        if n != CORE_BYTES or len(allocations) != 1:
            raise RuntimeError(f"unexpected Tintless lazy allocation sequence: {allocations}")
        amap(core_addr, CORE_BYTES)
        uc.mem_write(core_addr, bytes([allocation_fill]) * CORE_BYTES)
        uc.reg_write(UC_ARM64_REG_X0, core_addr)

    u.hook_add(UC_HOOK_CODE, alloc_hook, begin=STUB, end=STUB)

    interface_reads = []
    def iface_read_hook(uc, access, address, size, value, user_data):
        if IFACE <= address < IFACE + 0x1000:
            interface_reads.append((address - IFACE, size))
    u.hook_add(UC_HOOK_MEM_READ, iface_read_hook)

    results = {}
    for req in (4, 5, 6):
        if req == 4:
            put(WRAP, "req4_wrapper_pre.bin")
        else:
            # State must be the output of the previous replay, never reseeded.
            wantw = (cap / f"req{req}_wrapper_pre.bin").read_bytes()
            wantc = (cap / f"req{req}_core_pre.bin").read_bytes()
            if bytes(u.mem_read(WRAP, len(wantw))) != wantw:
                raise RuntimeError(f"request{req}: generated wrapper carry does not equal Windows pre-state")
            if bytes(u.mem_read(core_addr, len(wantc))) != wantc:
                raise RuntimeError(f"request{req}: generated core carry does not equal Windows pre-state")

        put(X1, f"req{req}_x1_config.bin", 0x1000)
        put(X2[req], f"req{req}_x2_stats.bin", 0x14000)
        put(D3[req], f"req{req}_x3_desc.bin")
        put(D4[req], f"req{req}_x4_desc.bin")
        in_addr = desc_ptr(cap, req, 3)
        out_addr = desc_ptr(cap, req, 4)
        in_pre = put(in_addr, f"req{req}_input_mesh.bin")
        out_pre = put(out_addr, f"req{req}_output_mesh_pre.bin")

        core_seen = {"r": 0, "w": 0}
        def core_hook(uc, access, address, size, value, user_data):
            if core_addr <= address < core_addr + CORE_BYTES:
                key = "r" if access == 16 else "w"
                core_seen[key] = max(core_seen[key], address + size - core_addr)
        h = u.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, core_hook)
        e.run(CALLBACK_RVA, xargs=(IFACE, X1, X2[req], D3[req], D4[req]), instruction_limit=200_000_000)
        u.hook_del(h)

        ret = u.reg_read(UC_ARM64_REG_X0) & 0xFFFFFFFF
        wantw = (cap / f"req{req}_wrapper_post.bin").read_bytes()
        wantc = (cap / f"req{req}_core_post.bin").read_bytes()
        wanto = (cap / f"req{req}_output_mesh_post.bin").read_bytes()
        gotw = bytes(u.mem_read(WRAP, len(wantw)))
        gotc = bytes(u.mem_read(core_addr, len(wantc)))
        goto = bytes(u.mem_read(out_addr, len(wanto)))
        if ret != 0 or gotw != wantw or gotc != wantc or goto != wanto:
            raise RuntimeError(f"request{req}: native replay mismatch")
        if out_pre[MESH_PAYLOAD_BYTES:] != wanto[MESH_PAYLOAD_BYTES:]:
            raise RuntimeError(f"request{req}: unreferenced output capture tail changed")
        if req in (5, 6) and core_seen != {"r": CORE_READ_HI, "w": CORE_BYTES}:
            raise RuntimeError(f"request{req}: core access footprint drift {core_seen}")
        results[f"request{req}"] = {
            "return": ret,
            "wrapper_sha256": sha(gotw),
            "core_sha256": sha(gotc),
            "output_capture_sha256": sha(goto),
            "output_abi_payload_sha256": sha(goto[:MESH_PAYLOAD_BYTES]),
            "output_capture_tail_unchanged": True,
            "core_access_hi": core_seen,
        }

    if allocations != [CORE_BYTES]:
        raise RuntimeError(f"allocator call sequence drift: {allocations}")
    if set(interface_reads) != {(0x18, 8)} or len(interface_reads) != 3:
        raise RuntimeError(f"synthetic interface contract drift: {interface_reads}")
    return {
        "allocation_fill": f"0x{allocation_fill:02x}",
        "allocator_calls": [f"0x{x:x}" for x in allocations],
        "synthetic_interface_reads": [[o, n] for o, n in interface_reads],
        "requests": results,
    }


def decode_halves(blob: bytes) -> tuple[list[int], list[int]]:
    lo, hi = [], []
    for (word,) in struct.iter_unpack("<I", blob):
        lo.append(word & 0x3FFF)
        hi.append((word >> 14) & 0x3FFF)
    return lo, hi


def q10(v: float) -> int:
    value = int(math.floor(v * 1024.0 + 0.5))
    return max(0x400, min(0x3FFF, value))


def prove_output_to_staging_wire(cap: Path, stage_mod) -> dict:
    orders = [
        (0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3), (0, 2, 3, 1), (0, 3, 1, 2), (0, 3, 2, 1),
        (1, 0, 2, 3), (1, 0, 3, 2), (1, 2, 0, 3), (1, 2, 3, 0), (1, 3, 0, 2), (1, 3, 2, 0),
        (2, 0, 1, 3), (2, 0, 3, 1), (2, 1, 0, 3), (2, 1, 3, 0), (2, 3, 0, 1), (2, 3, 1, 0),
        (3, 0, 1, 2), (3, 0, 2, 1), (3, 1, 0, 2), (3, 1, 2, 0), (3, 2, 0, 1), (3, 2, 1, 0),
    ]
    requests = {}
    zero_lut = b"\0" * 0x374
    for req in (4, 5, 6):
        output = (cap / f"req{req}_output_mesh_post.bin").read_bytes()
        vals = struct.unpack("<884f", output[:MESH_PAYLOAD_BYTES])
        channels = [[q10(v) for v in vals[i * 221:(i + 1) * 221]] for i in range(4)]
        staging = (cap / f"req{req}_lsc_staging.bin").read_bytes()
        geometry, lsc0, lsc1, lsc2 = stage_mod.pack_live_staging(staging)
        targets = list(decode_halves(lsc0) + decode_halves(lsc1))
        matches = [list(order) for order in orders if all(channels[order[i]] == targets[i] for i in range(4))]
        if not matches:
            raise RuntimeError(f"request{req}: Tintless output does not Q10-map to captured staging wire")
        if lsc2 != zero_lut:
            raise RuntimeError(f"request{req}: staging-derived LSC2 is no longer zero")
        cap_l0 = (cap / f"req{req}_lsc0.bin").read_bytes()
        cap_l1 = (cap / f"req{req}_lsc1.bin").read_bytes()
        if cap_l0 != zero_lut or cap_l1 != zero_lut:
            raise RuntimeError(f"request{req}: expected known zero placeholder LSC0/1 capture defect changed")
        requests[f"request{req}"] = {
            "bank": geometry["bank"],
            "accepted_channel_orders": matches,
            "tintless_output_sha256": sha(output),
            "staging_sha256": sha(staging),
            "derived_lsc0_sha256": sha(lsc0),
            "derived_lsc1_sha256": sha(lsc1),
            "derived_lsc2_sha256": sha(lsc2),
            "raw_lsc0_lsc1_zero_placeholders_rejected": True,
        }
    return requests


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--device-mft", type=Path, default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"))
    ap.add_argument("--capture-dir", type=Path, default=here / "oracle-live-20260904-front-atomic")
    ap.add_argument("--manifest", type=Path, default=here / "FRONT-ATOMIC-TINTLESS-STAGING-20260904.json")
    ap.add_argument("--out", type=Path, default=here / "lsc-front-atomic-tintless-replay-oracle.json")
    args = ap.parse_args()

    cap_info = verify_capture(args.capture_dir, args.manifest)
    surface = load_module(here / "prove-gtm-live-exact-replay.py", "surface_emu_front_atomic")
    stage = load_module(here / "prove-lsc-live-staging-pack.py", "stage_pack_front_atomic")
    code = verify_device_bytes(args.device_mft, surface)
    stage.verify_code_bytes(args.device_mft)

    runs = [
        replay_sequence(args.capture_dir, args.device_mft, surface, 0x00),
        replay_sequence(args.capture_dir, args.device_mft, surface, 0xA5),
    ]
    wire = prove_output_to_staging_wire(args.capture_dir, stage)

    oracle = {
        "schema": "sp11-e003h-front-atomic-tintless-native-replay-v1",
        "accepted": True,
        "status": "PASS",
        "classification": "CLOSED VERIFIED-FRONT ATOMIC TINTLESS STATE MACHINE: exact Surface ARM64 request4 initialization then request5/request6 sequential replay reproduces Windows wrapper state, full 0x126e8 persistent core and four-channel output meshes byte-for-byte; captured staging independently converts those outputs to exact nonzero LSC0/LSC1 wire targets.",
        "source_authority": {
            "device_mft_sha256": DEVICE_MFT_SHA256,
            "capture_manifest": args.manifest.name,
            "camera": "IMX681 front",
            "geometry": list(EXPECTED_GEOMETRY),
            "raw_capture_files": len(cap_info["manifest"]["hashes"]),
            "raw_captures_tracked": False,
        },
        "exact_functions": {
            "tintless_wrapper_process_rva": f"0x{CALLBACK_RVA:x}",
            "allocator_iat_rva_emulator_shim": f"0x{ALLOC_IAT_RVA:x}",
            "titan680_lsc_packer_rva": "0xb3d8a0",
        },
        "capture_abi_code_byte_proofs": code,
        "state_continuity": cap_info["continuity"],
        "allocator_initial_contents_independence": {
            "fills_tested": ["0x00", "0xa5"],
            "result": "both produce the same exact captured request4 post-state and exact request5/request6 sequence",
        },
        "native_sequential_replays": runs,
        "output_to_captured_staging_wire": wire,
        "capture_defect": {
            "raw_req4_5_6_lsc0_lsc1_files": "rejected as zero placeholders",
            "authority": "captured 0x18a0 staging -> exact Titan680 packer -> nonzero LSC0/LSC1; LSC2 remains legitimately zero",
        },
        "closed_gate": "The historical OV13858 rear TINTCTX evidence is no longer needed for front Tintless parity. This 2026-09-04 capsule is verified IMX681 3840x2160 and proves request4 lazy initialization plus request5/request6 state evolution natively.",
        "next_gate": "Before Linux request6, reproduce this atomic stream's pre-Tintless input meshes from same-stream upstream LSC tuning/calibration/geometry (req4 input SHA 71fdf640..., req5/req6 input SHA 6499164c...) or capture the exact upstream request/x22/x23 capsule that generated them. Then perform a fresh runtime-authorization review. This proof does not authorize Linux request6.",
        "safety": {
            "linux_camera_runtime_executed": False,
            "linux_request6_executed": False,
            "linux_request6_authorized": False,
            "windows_target_modified": False,
        },
    }
    args.out.write_text(json.dumps(oracle, indent=2, sort_keys=True) + "\n")
    print("PASS verified-front atomic Tintless request4 -> request5 -> request6 native replay")
    for run in runs:
        print("  allocation fill", run["allocation_fill"], "requests exact=4,5,6")
    for req, data in wire.items():
        print(" ", req, "LSC0", data["derived_lsc0_sha256"], "LSC1", data["derived_lsc1_sha256"])
    print("  oracle", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
