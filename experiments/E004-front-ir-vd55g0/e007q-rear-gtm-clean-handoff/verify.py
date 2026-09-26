#!/usr/bin/env python3
from pathlib import Path
import json, py_compile

D=Path(__file__).resolve().parent
p=json.load(open(D/"PRIVATE-VALIDATION-SAFE.json"))
s=(D/"camss-e007q-rear-gtm-handoff.inc").read_text()

assert p["status"]=="PASS"
assert p["e007j_exact_gtm_requests"]==15
assert p["e007j_total_gtm_requests"]==15
assert p["end_to_end_gtm_wire_exact"] is True
assert p["gtm_wire_bytes"]==2048
assert p["captured_tmc_knots_used_as_producer_inputs"] is False
assert p["raw_windows_values_emitted"] is False

for token in (
    "#define E007Q_GTM_VALID BIT(0)",
    "u8 payload[E006G_GTM_BYTES];",
    "if (s->gtm.request_id != expected_request_id)",
    "return -EPROTO;",
    "return -EAGAIN;",
    ".gtm = e007q_rear_gtm",
    ".stable = e007q_rear_stable",
    "e007i_rear_prepare_dynamic",
    "e007i_rear_fill_slot",
    "e007q_rear_gtm_handoff_recipe",
):
    assert token in s

for bad in ("writel(", "readl(", "dma_alloc", "submit", "RTCDM_FIFO"):
    assert bad not in s

py_compile.compile(str(D/"rear-gtm-runtime.py"),doraise=True)
py_compile.compile(str(D/"prove-runtime.py"),doraise=True)
print("E007Q_VERIFY_PASS gtm=15/15 request_tagged=true")
print("captured_knots_as_inputs=false runtime_submission=none")
