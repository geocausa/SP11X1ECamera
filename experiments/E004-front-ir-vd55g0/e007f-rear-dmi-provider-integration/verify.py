#!/usr/bin/env python3
from pathlib import Path

D = Path(__file__).resolve().parent
s = (D / "camss-e007f-dmi-integration.inc").read_text()

for token in [
    "struct e007f_rear_dmi_upstream_ops",
    "struct e007f_rear_dmi_state",
    "void *lsc_ctx;",
    "void *gtm_ctx;",
    "void *stable_ctx;",
    "struct e007e_bf_dmi_state bfstats25;",
    ".lsc = e007f_rear_lsc",
    ".gtm = e007f_rear_gtm",
    ".bfstats = e007f_rear_bfstats",
    ".stable = e007f_rear_stable",
    "return e007e_bfstats25_dmi(&s->bfstats25, selector, dst, bytes);",
    "return e006g_rear_prepare_dynamic(&e007f_rear_dmi_ops, s, out);",
    "return e006g_rear_fill_slot(&e007f_rear_dmi_ops, s,",
    "e007f_rear_validate_dmi_integration",
    "e007f_rear_dmi_integration_recipe",
]:
    assert token in s

assert "submit" not in s.lower()
assert "dma_alloc" not in s
assert "writel" not in s
assert "readl" not in s

print("E007F_VERIFY_PASS bfstats25=bound e006g=adapter")
print("lsc_gtm_stable=explicit_upstream contexts=separate runtime_submission=none")
