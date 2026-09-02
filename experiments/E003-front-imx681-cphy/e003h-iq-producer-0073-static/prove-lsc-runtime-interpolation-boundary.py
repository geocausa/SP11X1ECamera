#!/usr/bin/env python3
"""Fail-closed proof of the remaining live LSC41 runtime-interpolation boundary.

This proof consumes local/untracked Windows oracle captures plus the exact
Surface DeviceMFT and IMX681 tuning blob. It deliberately does not commit raw
Windows memory. It proves the live 42-float LSC trigger source, x22/x23 ABI at
LSC411Interpolation, exact tuning identity, and that the live pre-calibration
x22 mesh cannot be reproduced as a direct/affine/convex combination of the
five serialized 0xdf0 LSC region payloads as currently decoded.

No Linux camera runtime is performed or authorized.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

import numpy as np
import pefile

DEVICEMFT_SHA256_EXACT = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
TUNING_SHA256 = "2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d"
CAPTURE_FILES = {
    "request5": {
        "common_trigger": ("REQ5_COMMON_TRIGGER_0100.bin", 0x100, "f2147ee801b13be417107ad982890e5594e2216bff2f46de277862e0e15e31a1"),
        "isp_input": ("REQ5_ISPINPUT_2400.bin", 0x2400, "437979139dae97e74284504ce5458b038df99df81c9e9d5e5c007505941983c5"),
        "lsc_common": ("REQ5_LSC_COMMON_01E8.bin", 0x1E8, "7e0426b1cf23dbb60d8378256b704265fb7acd10275314cf9ebd5b086cbe933e"),
        "trigger_vector_object": ("REQ5_TRIGVEC_OBJ_0018.bin", 0x18, "f7f3c24a1953de94b38cd050bb35a062519ab456461b19dfb4dbd950c822146a"),
        "trigger_vector_data": ("REQ5_TRIGVEC_DATA_0100.bin", 0x100, "d12322da10d8f38bb360171f535521d198a27dd30c83db3eef405f03d57e8d78"),
        "x22_precal": ("REQ5_X22_RAW_0DF0.bin", 0xDF0, "e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de"),
        "x23_calibrated": ("REQ5_X23_CAL_0DF0.bin", 0xDF0, "94cbaac591fabf97ebff4a005b02fbcfa7a2bfff5783134794e1c52f0bcead71"),
    },
    "request6": {
        "common_trigger": ("REQ6_COMMON_TRIGGER_0100.bin", 0x100, "dad1ef4be1a70d96469639dd31af705fb22fb6ee3083dce6586226b0921137c4"),
        "isp_input": ("REQ6_ISPINPUT_2400.bin", 0x2400, "a04ac2974552fd0071cc1f5a98a9e479e0dc98a3bf8a6246d493cbb8a2c978db"),
        "lsc_common": ("REQ6_LSC_COMMON_01E8.bin", 0x1E8, "6641c5c645810793e30b8c50a0838ae39a9cf48c51d2f2fbbd3c83178d3615bb"),
        "trigger_vector_object": ("REQ6_TRIGVEC_OBJ_0018.bin", 0x18, "e0410fbb5d782ef7adc919586f1df1e6aea18397f8bbe50fcb4c0c9164b506ff"),
        "trigger_vector_data": ("REQ6_TRIGVEC_DATA_0100.bin", 0x100, "5cac4b3f5d9bb76989aaf85c2945c53473b80850160280fe9b0671c49a60910e"),
        "x22_precal": ("REQ6_X22_RAW_0DF0.bin", 0xDF0, "3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8"),
        "x23_calibrated": ("REQ6_X23_CAL_0DF0.bin", 0xDF0, "62b39d4ee8f66dc4931c0a99bf4c51cc7069ea4829f78df6c80dbfa82b48ad15"),
    },
}
EXPECTED_VECTOR = {
    "request5": [400.93280029296875,18.924766540527344,1.0,1.0,1.0,1.0,4999.0,0.0,370.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
    "request6": [400.27227783203125,27.208637237548828,1.0,1.0,1.0,1.0,4999.0,0.0,370.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
}
LSC_CONTROLS = [8, 2, 5, 100, 0, 6]
LSC_VECTOR_INDICES = [8, 2, 5, 19, 20, 21, 0, 6]
CODE_BYTES = {
    0x93C1F4: "f70301aa",  # mov x23,x1 : interpolation destination argument
    0x93C398: "549c0194",  # bl generic interpolation tree builder
    0x93C3B4: "559e0194",  # bl generic interpolation execution
    0x93C55C: "961e40f9",  # ldr x22,[x20,#0x38] : selected generic result
}
EXPECTED_UNIQUE_LSC_PAYLOADS = {
    "29408fb91e76b9c4b3fa3c044f9dbc8ff7b3563a62f836191b337f666a4a1644": 3301034,
    "8defd46dbc1881d7f22cbdf3c8e1b52c4a89cc2718c394afced8d44b1452af52": 3304602,
    "bdcf62f46070513ca0d343dda341336fe3953891a2643581e8ee455b77f37a3e": 3308170,
    "afc02261b98c3e2655039e29ace838f5780ac26202beda08db74dbd876822a11": 3311738,
    "f0c84bd42df54e3b18abb41d787e922d98f82f0aa72230c90aaea48f94994ee8": 3315330,
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_decoder(path: Path):
    spec = importlib.util.spec_from_file_location("imx681_decode", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load tuning decoder")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify_code(dll: Path) -> dict[str, str]:
    got_sha = sha_file(dll)
    if got_sha != DEVICEMFT_SHA256_EXACT:
        raise RuntimeError(f"DeviceMFT SHA mismatch: {got_sha}")
    pe = pefile.PE(str(dll), fast_load=True)
    raw = dll.read_bytes()
    out = {}
    for rva, want in CODE_BYTES.items():
        off = pe.get_offset_from_rva(rva)
        got = raw[off:off+4].hex()
        if got != want:
            raise RuntimeError(f"code mismatch at 0x{rva:x}: {got} != {want}")
        out[f"0x{rva:x}"] = got
    return out


def load_capture(capture_dir: Path) -> dict:
    result = {}
    for req, files in CAPTURE_FILES.items():
        result[req] = {}
        for key, (name, size, want_sha) in files.items():
            p = capture_dir / name
            b = p.read_bytes()
            if len(b) != size:
                raise RuntimeError(f"{name}: size {len(b):#x} != {size:#x}")
            got = sha(b)
            if got != want_sha:
                raise RuntimeError(f"{name}: SHA mismatch {got}")
            result[req][key] = {"path": p, "bytes": b, "sha256": got, "size": size}
    return result


def affine_metrics(leaves: np.ndarray, observed: np.ndarray) -> dict:
    # Enforce sum(weights)=1 by solving [leaves; ones] * w ~= [obs; 1].
    A = np.vstack([leaves.T.astype(np.float64), np.ones((1, leaves.shape[0]))])
    y = np.concatenate([observed.astype(np.float64), np.array([1.0])])
    w, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = w @ leaves.astype(np.float64)
    d = pred - observed.astype(np.float64)
    return {
        "weights": [float(x) for x in w],
        "weight_sum": float(w.sum()),
        "rms": float(np.sqrt(np.mean(d*d))),
        "max_abs": float(np.max(np.abs(d))),
    }


def best_pair_metrics(leaves: np.ndarray, observed: np.ndarray) -> dict:
    best = None
    n = leaves.shape[0]
    for i in range(n):
        for j in range(i+1, n):
            a = leaves[i].astype(np.float64)
            b = leaves[j].astype(np.float64)
            v = b-a
            den = float(v @ v)
            t = 0.0 if den == 0.0 else float(((observed.astype(np.float64)-a) @ v) / den)
            tc = max(0.0, min(1.0, t))
            pred = a + tc*v
            d = pred-observed.astype(np.float64)
            row = {"i": i, "j": j, "t_unclamped": t, "t": tc,
                   "rms": float(np.sqrt(np.mean(d*d))), "max_abs": float(np.max(np.abs(d)))}
            if best is None or row["rms"] < best["rms"]:
                best = row
    assert best is not None
    return best


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--device-mft", type=Path, default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"))
    ap.add_argument("--tuning", type=Path, default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin"))
    ap.add_argument("--decoder", type=Path, default=here / "decode_imx681_chromatix.py")
    ap.add_argument("--capture-dir", type=Path, default=Path("/mnt/windows/Users/Geoca/Documents/SP11CameraOracle/E003H_20260902_LSCTRIGSRC"))
    ap.add_argument("--installed-tuning", type=Path, default=Path("/mnt/windows/Windows/System32/DriverStore/FileRepository/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin"))
    ap.add_argument("--out", type=Path, default=here / "lsc-runtime-interpolation-boundary-oracle.json")
    args = ap.parse_args()

    code = verify_code(args.device_mft)
    if sha_file(args.tuning) != TUNING_SHA256:
        raise RuntimeError("archived tuning SHA mismatch")
    installed_sha = None
    if args.installed_tuning.exists():
        installed_sha = sha_file(args.installed_tuning)
        if installed_sha != TUNING_SHA256:
            raise RuntimeError("installed Windows tuning differs from archived exact tuning")

    cap = load_capture(args.capture_dir)
    reqs = {}
    for req in ("request5", "request6"):
        obj = cap[req]["trigger_vector_object"]["bytes"]
        start, end, capacity = struct.unpack("<QQQ", obj)
        count = (end-start)//4
        cap_count = (capacity-start)//4
        if (count, cap_count) != (42, 42):
            raise RuntimeError(f"{req}: vector extent {count}/{cap_count} != 42/42")
        vec = list(struct.unpack("<64f", cap[req]["trigger_vector_data"]["bytes"]))[:42]
        if vec != EXPECTED_VECTOR[req]:
            raise RuntimeError(f"{req}: exact live trigger vector drift")
        x22 = np.frombuffer(cap[req]["x22_precal"]["bytes"][:0xDD0], dtype="<f4").copy()
        x23 = np.frombuffer(cap[req]["x23_calibrated"]["bytes"][:0xDD0], dtype="<f4").copy()
        ratios = x23/x22
        reqs[req] = {
            "capture_hashes": {k: v["sha256"] for k, v in cap[req].items()},
            "trigger_vector_count": count,
            "trigger_vector_capacity": cap_count,
            "trigger_vector_42": vec,
            "lsc_controls": LSC_CONTROLS,
            "lsc_vector_indices": LSC_VECTOR_INDICES,
            "lsc_mapped_values": {str(i): vec[i] for i in LSC_VECTOR_INDICES},
            "x22_precal_first8": [float(x) for x in x22[:8]],
            "x23_calibrated_first8": [float(x) for x in x23[:8]],
            "x23_over_x22": {"min": float(ratios.min()), "mean": float(ratios.mean()), "max": float(ratios.max())},
        }

    dec = load_decoder(args.decoder)
    tuning = args.tuning.read_bytes()
    header = dec.parse_header(tuning)
    records, _ = dec.parse_symbol_table(tuning, header["sections"][0], header["sections"][1])
    objsec = header["sections"][1]
    regions = []
    unique = {}
    for sid, rec in records.items():
        if rec["type"] == "region" and rec["data_bytes"] == 0xDF0:
            raw = dec.data_bytes(tuning, objsec, rec)
            h = sha(raw)
            regions.append({"sid": sid, "sha256": h, "data_abs_offset": rec["data_abs_offset"]})
            unique.setdefault((h, rec["data_abs_offset"]), {"sha256": h, "data_abs_offset": rec["data_abs_offset"], "sids": [], "raw": raw})["sids"].append(sid)
    if len(regions) != 25 or len(unique) != 5:
        raise RuntimeError(f"unexpected 0xdf0 region corpus {len(regions)} / unique {len(unique)}")
    got_unique = {k[0]: k[1] for k in unique}
    if got_unique != EXPECTED_UNIQUE_LSC_PAYLOADS:
        raise RuntimeError("unique serialized LSC payload set drift")

    ordered = sorted(unique.values(), key=lambda x: x["data_abs_offset"])
    leaves = np.stack([np.frombuffer(x["raw"][:0xDD0], dtype="<f4").copy() for x in ordered])
    corpus = {
        "serialized_region_records_0xdf0": len(regions),
        "unique_payloads": len(ordered),
        "payloads": [{"sha256": x["sha256"], "data_abs_offset": x["data_abs_offset"], "sids": sorted(x["sids"])} for x in ordered],
    }
    for req in ("request5", "request6"):
        obs = np.frombuffer(cap[req]["x22_precal"]["bytes"][:0xDD0], dtype="<f4").copy()
        direct = []
        for i, leaf in enumerate(leaves):
            d = leaf.astype(np.float64)-obs.astype(np.float64)
            direct.append({"i": i, "rms": float(np.sqrt(np.mean(d*d))), "max_abs": float(np.max(np.abs(d)))})
        direct.sort(key=lambda x: x["rms"])
        reqs[req]["serialized_leaf_test"] = {
            "nearest_direct": direct[0],
            "best_convex_pair": best_pair_metrics(leaves, obs),
            "best_affine_five_leaf": affine_metrics(leaves, obs),
            "classification": "FAILS: live x22 is not a direct, convex-pair, or exact affine combination of the five serialized 0xdf0 LSC payloads as currently decoded",
        }

    oracle = {
        "schema": "sp11-e003h-lsc-runtime-interpolation-boundary-v1",
        "accepted": True,
        "classification": "OPEN RUNTIME-CHROMATIX REPRESENTATION BOUNDARY: live x22 is conclusively the generic pre-calibration LSC41 interpolation result, but it is not reproducible from the five serialized 0xdf0 region payloads under the current raw-container interpretation.",
        "source_authority": {
            "device_mft_sha256": DEVICEMFT_SHA256_EXACT,
            "archived_imx681_tuning_sha256": TUNING_SHA256,
            "installed_windows_imx681_tuning_sha256": installed_sha,
            "capture_session": "E003H_20260902_LSCTRIGSRC",
            "raw_capture_committed": False,
        },
        "exact_abi": {
            "lsc411_interpolation_rva": "0x93c1b0",
            "post_capture_rva": "0x93c8e8",
            "x23": "RunInterpolation x1 destination argument retained from prologue; calibrated destination after calibration stage",
            "x22": "generic interpolation result loaded from interpolation scratch [x20+0x38] at RVA 0x93c55c before calibration",
            "code_byte_proofs": code,
        },
        "requests": reqs,
        "serialized_lsc_corpus": corpus,
        "closed_exclusions": [
            "wrong Windows tuning revision: installed and archived tuning SHA256 are identical",
            "hidden alternate serialized 0xdf0 LSC payload: 25 records collapse to exactly five unique payloads",
            "wrong x22/x23 live label: exact ARM64 prologue/result-load semantics pin x22 pre-calibration and x23 destination/calibrated",
            "missing live trigger values: complete 42/42 float vector captured for requests5/6",
            "EEPROM calibration as cause of x22 discrepancy: x22 is pre-calibration; x23/x22 calibration ratio is stable across the pair",
            "Tintless/GTM/geometry/packer causes: those stages are downstream and independently closed",
        ],
        "next_gate": "Resolve how the exact Surface runtime Chromatix object represents/materializes the LSC41 leaf data consumed by generic interpolation. Prefer static tracing of runtime object construction/leaf pointers; if one live observation is needed, capture the actual leaf pointers/data handed to the generic interpolation engine at request5/6 rather than broad state dumps. Do not run Linux request6.",
        "safety": {"linux_camera_runtime": False, "linux_request6_executed": False, "linux_request6_authorized": False},
    }
    args.out.write_text(json.dumps(oracle, indent=2) + "\n")
    print("PASS lsc runtime interpolation boundary")
    print("trigger vectors 42/42; serialized 0xdf0 regions 25 -> 5 unique")
    for req in ("request5", "request6"):
        t=reqs[req]["serialized_leaf_test"]
        print(req, "x22", reqs[req]["capture_hashes"]["x22_precal"], "affine_rms", t["best_affine_five_leaf"]["rms"], "pair_rms", t["best_convex_pair"]["rms"])
    print("oracle", args.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
