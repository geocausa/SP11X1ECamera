#!/usr/bin/env python3
"""Private final-DMI shape check; emit booleans and counts, never coordinates."""
import importlib.util
import json
from pathlib import Path

here = Path(__file__).resolve().parent
p = here.parent / "e008u-rear-bf-roi-geometry-audit/audit-private.py"
spec = importlib.util.spec_from_file_location("e008u_audit", p)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

checks = {}
for label, payload in audit.observed().items():
    if label == "startup0":
        continue
    rows = audit.decode(payload)
    by_row = [rows[i*5:(i+1)*5] for i in range(5)]
    tops = [row[0]["top"] for row in by_row]
    height_set = {r["height"] for r in rows}
    assert len(height_set) == 1
    height = next(iter(height_set))
    candidates = 0
    for step in range(1, 1025):
        dim = step - 1
        if dim > 0 and not (dim & 1):
            dim -= 1
        if dim != height:
            continue
        for base_parity in (0, 1):
            generated = [(base_parity + i*step) & ~1 for i in range(5)]
            if [x-generated[0] for x in generated] == [x-tops[0] for x in tops]:
                candidates += 1
    checks[label] = {
        "within_row_top_constant": all(len({r["top"] for r in row}) == 1
                                       for row in by_row),
        "within_column_left_constant": all(
            len({rows[row*5+col]["left"] for row in range(5)}) == 1
            for col in range(5)),
        "top_even": all(not (r["top"] & 1) for r in rows),
        "dimension_odd": all((r["width"] & 1) and (r["height"] & 1)
                             for r in rows),
        "map_plus_bf_vertical_shape_candidates": candidates,
    }
    assert all(v for k, v in checks[label].items()
               if k != "map_plus_bf_vertical_shape_candidates")
    assert candidates == 1

result = {
    "schema": "E008X-source-map-shape-v1",
    "classification": "VERTICAL_SHAPE_CONSISTENT_AF_RECTANGLE_UNKNOWN",
    "normal_samples_checked": len(checks),
    "normal_roi_records_checked": len(checks) * 25,
    "shape_checks": checks,
    "request_specific_af_rectangle_source_closed": False,
    "full_normal_selector1_parity": False,
    "captured_values_or_hashes_emitted": False,
    "runtime_actions_performed": False,
}
(here / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
print("E008X_PRIVATE_SHAPE_PASS normal samples=4, AF rectangle input open")
