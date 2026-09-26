#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE / "rear-gtm-runtime.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("e007o_dir", type=Path)
    ap.add_argument("e007j_dir", type=Path)
    ap.add_argument("--out", type=Path, default=HERE / "PRIVATE-VALIDATION-SAFE.json")
    args = ap.parse_args()

    RT = load(RUNTIME, "e007q_runtime")

    # Captured E007j knots are correspondence/oracle data only. They never
    # enter the producer. Their hashes identify which accepted request state
    # a freshly generated E007p triplet represents.
    req_by_triplet = {}
    want_gtm = {}
    for req in range(4, 19):
        src = (args.e007j_dir / f"R{req:02d}_TMC_SRC.bin").read_bytes()
        dst = (args.e007j_dir / f"R{req:02d}_TMC_DST.bin").read_bytes()
        coef = (args.e007j_dir / f"R{req:02d}_TMC_COEF.bin").read_bytes()
        req_by_triplet.setdefault(sha(src + dst + coef), []).append(req)
        want_gtm[req] = (args.e007j_dir / f"R{req:02d}_GTM_OUT.bin").read_bytes()

    exact_requests = set()
    unmatched_hits = []
    matched_hits = 0
    scale_indices = []

    with tempfile.TemporaryDirectory(prefix="e007q-") as td:
        so = Path(td) / "libe007p.so"
        RT.compile_tmc141(so)
        producer = RT.RearDynamicGtm(so)

        for hit in range(1, 21):
            q = f"H{hit:02d}"
            tune = (args.e007o_dir / f"{q}_TUNE.bin").read_bytes()
            runtime = (args.e007o_dir / f"{q}_RUNTIME.bin").read_bytes()
            common = (args.e007o_dir / f"{q}_COMMON.bin").read_bytes()
            ctrl = (args.e007o_dir / f"{q}_CTRL.bin").read_bytes()
            face = (args.e007o_dir / f"{q}_FACE.bin").read_bytes()

            wire, src, dst, coef, meta = producer.run(
                tune, runtime, common, ctrl, face
            )
            scale_indices.append(meta["scale_index"])
            reqs = req_by_triplet.get(sha(src + dst + coef), [])
            if not reqs:
                unmatched_hits.append(hit)
                continue

            matched_hits += 1
            for req in reqs:
                if wire != want_gtm[req]:
                    raise RuntimeError(f"H{hit:02d}/R{req}: clean GTM mismatch")
                exact_requests.add(req)

    expected = set(range(4, 19))
    if exact_requests != expected:
        raise RuntimeError(
            f"E007j request coverage drift: {sorted(exact_requests)}"
        )

    result = {
        "schema": "E007q-private-validation-safe-v1",
        "status": "PASS",
        "semantic_input_hits_checked": 20,
        "semantic_hits_matching_e007j_state": matched_hits,
        "unmatched_intermediate_hits": unmatched_hits,
        "e007j_requests_covered": sorted(exact_requests),
        "e007j_exact_gtm_requests": len(exact_requests),
        "e007j_total_gtm_requests": 15,
        "end_to_end_gtm_wire_exact": True,
        "gtm_wire_bytes": 2048,
        "scale_index_sequence": scale_indices,
        "captured_tmc_knots_used_as_producer_inputs": False,
        "raw_windows_values_emitted": False,
        "producer_chain": [
            "semantic TUNE/RUNTIME/COMMON/CTRL/FACE",
            "E007p clean TMC141 SRC/DST/COEF",
            "accepted clean GTM backend",
            "2048-byte Titan680 GTM wire payload",
        ],
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("E007Q_PRIVATE_VALIDATION_PASS GTM=15/15 end_to_end=true")
    print(f"matched_semantic_hits={matched_hits}/20 unmatched={unmatched_hits}")
    print("captured_tmc_knots_as_inputs=false raw_values_emitted=false")


if __name__ == "__main__":
    main()
