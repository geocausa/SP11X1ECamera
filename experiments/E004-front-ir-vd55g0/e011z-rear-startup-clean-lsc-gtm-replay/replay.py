#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LSC_DIR = ROOT / "experiments/E004-front-ir-vd55g0/e007h-rear-lsc-clean-runtime"
GTM_FILE = ROOT / "experiments/E003-front-imx681-cphy/e003i-front-native-productionization/j-cleanroom-gtm/generate-cleanroom-gtm-wire.py"

EXPECTED = {
    "lsc_phase0": [
        "c5a990dc398e6926b2b53c1174219387837029a6051069f4ebc86fc74c8d440b",
        "ed004c388d9b0230c31ffc8b5ef8d54dd60d4f21c174837a10e46e3d62374293",
        "6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e",
    ],
    "lsc_phase1": [
        "d8c34f9fc439253e06f30a2fee776c75034dc9206f75b34046351affc127d73e",
        "efa6f2616a6a56527d0d5605c405c5a5db7b8f65c6be84890f423d2953c0faa8",
        "6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e",
    ],
    "gtm_startup": "b71d4b3eadec95941586227f171e771ae5dc1c70fd48fa5ebf599dcf8fd77d81",
}

def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def clean_lsc():
    R = load(LSC_DIR / "rear-lsc-runtime.py", "e011z_rear_lsc_runtime")
    auth = json.loads((LSC_DIR / "authority.json").read_text())
    CL = R.load(R.CLFILE, "e011z_clean_lsc")
    K = R.load(R.KFILE, "e011z_lsc_wire")
    leaves = {k: base64.b64decode(v) for k, v in auth["leaf_b64"].items()}
    gold = tuple(float(v) for v in auth["golden_int"])
    otp = [tuple(float(v) for v in ch) for ch in auth["otp_int_channels"]]
    g = auth["geometry"]
    geom = (*g["full"], *g["output"], *g["crop"], g["scale"])

    # Exact LSC411Interpolation selector behavior at RVA 0x93c1b0:
    # below the first trigger interval, lower=upper=0 and ratio=0.
    # Therefore the cold CCT=0 startup seed selects the first lower-CCT
    # child (serialized rear/default leaf 0x29c) without extrapolation.
    selections = [
        ("phase0", 0.0, "0x29c", "below-first interval => child0"),
        ("phase1", 5000.0, "0x2a0", "4800..10000 leaf"),
    ]
    result = {}
    wire_bytes = {}
    for phase, cct, sid, law in selections:
        x23 = CL.calibrate(leaves[sid], gold, otp)
        pre = R.resample_mesh(x23, CL, geom)
        l0, l1, l2, gic = K.wire_from_output(pre + bytes(0x20))
        hashes = [sha(l0), sha(l1), sha(l2)]
        want = EXPECTED["lsc_" + phase]
        if hashes != want:
            raise RuntimeError(f"{phase} LSC hash drift: {hashes!r}")
        result[phase] = {
            "cct": cct,
            "selection": sid,
            "selection_law": law,
            "pretintless_sha256": sha(pre),
            "selector1_sha256": hashes[0],
            "selector2_sha256": hashes[1],
            "selector3_sha256": hashes[2],
            "gic_alias_sha256": sha(gic),
        }
        wire_bytes[phase] = (l0, l1)
    return result, wire_bytes

def clean_gtm():
    J = load(GTM_FILE, "e011z_gtm")
    # Source-locked pre-valid-TMC curve is flat: every slope is zero.
    # Its packed output is independent of the interpolation coordinate grid.
    # Supply a canonical increasing grid; no private normal-TMC domain is needed.
    curve = [4096.0] * 257
    wire = J.pack_gtm(curve, list(range(257)))
    if J.pack_gtm(curve, [float(i * i) for i in range(257)]) != wire:
        raise RuntimeError("flat startup GTM unexpectedly depends on coordinate grid")
    got = sha(wire)
    if got != EXPECTED["gtm_startup"]:
        raise RuntimeError(f"startup GTM hash drift: {got}")
    return {
        "region_points": 257,
        "region_unique_value": 4096.0,
        "bytes": len(wire),
        "sha256": got,
    }, wire

def main():
    lsc, _ = clean_lsc()
    gtm, _ = clean_gtm()
    out = {
        "schema": "E011Z-clean-startup-adaptive-replay-safe-v1",
        "status": "PASS",
        "raw_private_inputs_used": False,
        "captured_windows_dmi_used_as_input": False,
        "lsc": lsc,
        "gtm": gtm,
        "packet_schedule": [
            {"phase": 0, "lsc_dmi_present": True,  "lsc_state": 0, "gtm_state": "static_seed"},
            {"phase": 1, "lsc_dmi_present": True,  "lsc_state": 1, "gtm_state": "static_seed"},
            {"phase": 2, "lsc_dmi_present": False, "lsc_state": 1, "gtm_state": "static_seed"},
            {"phase": 3, "lsc_dmi_present": False, "lsc_state": 1, "gtm_state": "static_seed"},
        ],
        "materializer_request_ids": "caller_supplied_per_packet_and_not_derived_from_phase",
        "native_rear_runtime_authorized": False,
    }
    (HERE / "REPLAY-SAFE.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("E011Z_CLEAN_STARTUP_ADAPTIVE_REPLAY_PASS")
    print("LSC phase0/phase1 exact; GTM startup exact; raw_private_inputs=false")

if __name__ == "__main__":
    main()
