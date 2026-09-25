#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def req(x,msg):
    if not x:
        raise AssertionError("E005O_FAIL_CLOSED "+msg)

def main():
    d=json.loads((HERE/"RESULT.json").read_text())
    req(d["capture"]["elapsed_ms"] == 8026, "capture duration")
    req(d["capture"]["valid_frame_handles"] == 13, "valid frames")
    req(d["capture"]["start_success"] and d["capture"]["stop_success"], "clean capture lifecycle")
    c=d["exact_live_marker_counts"]
    req(c["bf_event"] == 22, "BF exact hits")
    req(c["fifo8_nonnull"] == 22, "FIFO exact hits")
    req(c["matcher_nonnull"] == 22, "matcher exact hits")
    req(c["wm16_consumed_status_nonnull"] == 42, "WM16 status hits")
    req(c["vfe_bus_compgrp7_probe_mode_a"] == 0, "BUS7 A must remain negative")
    req(c["vfe_bus_compgrp7_probe_mode_b"] == 0, "BUS7 B must remain negative")
    req(c["bf_event"] == c["fifo8_nonnull"] == c["matcher_nonnull"], "each observed BF event had FIFO+matcher in this bounded run")
    p=d["proven"]
    req(p["successful_rear4k_capture_during_external_kd"], "physical capture")
    req(p["live_bf_event_observed"], "live BF")
    req(p["live_bf_event_with_nonnull_fifo8_entry_observed"], "live FIFO8")
    req(p["live_bf_event_with_nonnull_matcher_return_observed"], "live matcher")
    req(p["wm16_consumed_status_nonzero_observed_in_same_session"], "WM16 activity")
    for k,v in d["not_proven"].items():
        req(v is True, "unproven predicate must stay explicit: "+k)
    req(d["native_rear_hardware_isp_runtime_authorized"] is False, "rear runtime remains denied")
    print("PASS_E005O_LIVE_BF_FIFO8_MATCHER_POSITIVE_BUS7_PROBES_NEGATIVE_REAR_DENIED")

if __name__=="__main__":
    main()
