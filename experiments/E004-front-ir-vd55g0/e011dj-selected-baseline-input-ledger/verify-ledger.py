#!/usr/bin/env python3
"""Read-only ledger check. Never reads private input bytes or executes OEM code."""
from pathlib import Path
import argparse, ast, copy, hashlib, json, re, struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EX = HERE.parent
def one(tag, name):
    paths = list(EX.glob(tag + "-*/" + name))
    assert len(paths) == 1, (tag, name)
    return paths[0]
def source(tag, name):
    return one(tag, name).read_text()
def get_key(obj, dotted):
    for key in dotted.split("."):
        obj = obj[key]
    return obj
def main_function(tag):
    tree = ast.parse(source(tag, "verify-private.py"))
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
def flatten_add(n):
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return flatten_add(n.left) + flatten_add(n.right)
    return [n]
def joined_source(n, fmt=None):
    assert isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "join"
    g = n.args[0]
    assert isinstance(g, ast.GeneratorExp) and len(g.generators) == 1
    assert isinstance(g.generators[0].iter, ast.Name)
    call = g.elt
    if fmt is not None:
        assert isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "pack"
        assert isinstance(call.args[0], ast.Constant) and call.args[0].value == fmt
    else:
        assert isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "bytes"
    return g.generators[0].iter.id

def validate(ledger):
    assert ledger["schema"] == "E011DJ-selected-baseline-input-ledger-v1"
    for key in ("native_rear_runtime_allowed", "complete_deterministic_source_bootstrap_closed",
                "minimal_enabled_module_dependency_closure_proven", "new_kernel_build", "private_bytes_exported"):
        assert ledger[key] is False, key
    assert ledger["new_camera_starts"] == ledger["new_reboots"] == 0
    # Actual semantic union, not a manually assumed module count.
    state = source("e007d", "camss-e007d-register-integration.inc")
    body = re.search(r"struct e007d_rear_register_state\s*\{(.*?)\n\};", state, re.S).group(1)
    members = re.findall(r"struct \w+\s+(\w+);", body)
    rows = ledger["register_members"]
    assert [x["member"] for x in rows] == members
    assert len(members) == 14 and len(set(members)) == 14
    indexed = {r["member"]: r for r in rows}
    for member in ("scalar", "bpcabf", "bfstats", "rs", "aec_be", "awb_bg"):
        assert "observed" in indexed[member]["input_origin"], member
    for member in ("geometry", "mnds", "bhist", "tintless_bg"):
        assert "fixture" in indexed[member]["input_origin"], member
    assert "whole-frame zero-offset scope" in indexed["rs"]["input_origin"]
    assert len(ledger["dmi_families"]) == 5
    # Reconstruct the actual Python wire concatenation, without running it.
    wire = next(n.value for n in ast.walk(main_function("e011bw"))
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "wire" for t in n.targets))
    parts = flatten_add(wire)
    assert len(parts) == 7
    assert [parts[i].id for i in (0, 1, 6)] == ["source_wire", "grid", "old_wire"]
    assert joined_source(parts[2], "<8I") == "rs"
    assert joined_source(parts[3]) == "weight"
    assert joined_source(parts[4], "<10I") == "bg"
    assert joined_source(parts[5], "<4H4I2H") == "scalar"
    bw = source("e011bw", "verify-private.py")
    av = source("e011av", "verify-private.py")
    assert "read_exact(tuning,93)" in av and "read_exact(grid_wire,404)" in bw
    ag = source("e011ag", "integration-check.c")
    for tag, name, count, width in (
        ("e011am", "host-rs-check.h", 3, 32),
        ("e011aj", "host-bg-check.h", 4, 40),
        ("e011ai", "host-scalar-check.h", 3, 28)):
        text = source(tag, name)
        assert re.search(r"(?:p|i)<" + str(count), text)
        assert "u8 wire[" + str(width) + "]" in text and "read_exact(wire,sizeof(wire))" in text
    weights = source("e011bw", "host-source-weight-quad-check.h")
    assert "read_exact((u8 *)&source.phase[p],4)" in weights
    assert re.search(r"p<2", weights)
    assert "source.phase[0].awb_quad==255" in weights
    assert "e011bw_cold_output" in weights
    assert "u8 wire[34]" in ag and "p<3" in ag
    adaptive = source("e011z", "camss-e011z-rear-startup-adaptive-bind.inc")
    materializer = source("e006g", "camss-e006g-rear-materializer.inc")
    lsc = int(re.search(r"#define E006G_LSC_BYTES\s+(\d+)", materializer).group(1))
    gtm = int(re.search(r"#define E006G_GTM_BYTES\s+(\d+)", materializer).group(1))
    lsc_states = int(re.search(r"#define E011Z_LSC_STATES\s+(\d+)", adaptive).group(1))
    sizes = [
        ("cold_awb_root", 93, 1), ("cold_aec_grid", 404, 1),
        ("rs_values", struct.calcsize("<8I"), 3), ("weight_quad", 4, 2),
        ("bg_values", struct.calcsize("<10I"), 4),
        ("scalar_values", struct.calcsize("<4H4I2H"), 3),
        ("bpc_common", struct.calcsize("<2h2H26B"), 3),
        ("lsc_selector1", lsc, lsc_states), ("lsc_selector2", lsc, lsc_states), ("gtm", gtm, 1)]
    offset = 0
    assert len(ledger["wire_groups"]) == len(sizes)
    for group, (name, width, count) in zip(ledger["wire_groups"], sizes):
        assert (group["name"], group["offset"], group["record_bytes"], group["records"], group["bytes"]) == (
            name, offset, width, count, width * count)
        offset += width * count
    assert ledger["wire_bytes"] == offset == 6531
    # Cold inactive gamma replacement is actually in the assembled-harness path.
    gamma = source("e011as", "verify-private.py")
    assert "Explicit host-only completion of an UNUSED cold gamma state." in gamma
    assert "e011as_rear_mark_cold_gamma_inactive(&base[0])" in gamma
    assert "c=c[:a]+" in gamma
    composer = source("e011ag", "camss-e011ag-startup-compose.inc")
    assert re.search(r"e011ag_rear_runtime_authorization\(void\)\s*\{\s*return -EOPNOTSUPP;", composer)
    assert ledger["next_smallest_gap"]["experiment"] == "E011DK"
    # Reused proof claims must agree with their original bounded evidence.
    assert len(ledger["reused_proofs"]) == 15
    for proof in ledger["reused_proofs"]:
        assert get_key(json.loads((ROOT / proof["path"]).read_text()), proof["key"]) == proof["expected"]
    needed = set(ledger["harness_chain"])
    needed.update(x["consumer_or_producer"] for x in ledger["wire_groups"])
    needed.update(x["path"] for x in ledger["reused_proofs"])
    for row in rows + ledger["dmi_families"]:
        assert row["remaining"] and row["reuse"]
        needed.update(row["reuse"])
    locks = {x["path"]: x["sha256"] for x in ledger["source_locks"]}
    assert len(locks) == len(ledger["source_locks"]) and needed <= locks.keys()
    for path, digest in locks.items():
        target = ROOT / path
        assert target.is_file() and target.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest, path
    return {"register_members": len(members), "dmi_families": 5, "wire_groups": len(sizes),
            "wire_bytes": offset, "source_locks": len(locks), "reused_proofs": len(ledger["reused_proofs"])}

def selfcheck(ledger):
    def promote_runtime(x): x["native_rear_runtime_allowed"] = True
    def promote_minimal(x): x["minimal_enabled_module_dependency_closure_proven"] = True
    def omit_consumer(x): x["register_members"].pop()
    def promote_observed(x):
        next(r for r in x["register_members"] if r["member"] == "rs")["input_origin"] = "source-generated policy"
    def corrupt_layout(x): x["wire_groups"][2]["offset"] += 1
    def stale_source(x): x["source_locks"][0]["sha256"] = "0" * 64
    def erase_existing_proof(x):
        next(r for r in x["reused_proofs"] if r["key"] == "initial_rs_origin_closed_for_active_titan680")["expected"] = False
    def overclaim_bootstrap(x): x["complete_deterministic_source_bootstrap_closed"] = True
    negatives = [promote_runtime, promote_minimal, omit_consumer, promote_observed,
                 corrupt_layout, stale_source, erase_existing_proof, overclaim_bootstrap]
    for mutate in negatives:
        bad = copy.deepcopy(ledger)
        mutate(bad)
        try:
            validate(bad)
        except AssertionError:
            continue
        raise AssertionError("invalid ledger accepted: " + mutate.__name__)
    return len(negatives)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args()
    ledger = json.loads((HERE / "INPUT-LEDGER.json").read_text())
    report = validate(ledger)
    if args.selfcheck:
        report["negative_mutations_rejected"] = selfcheck(ledger)
    print(json.dumps({"status": "PASS_INPUT_DEPENDENCY_LEDGER", **report}))
