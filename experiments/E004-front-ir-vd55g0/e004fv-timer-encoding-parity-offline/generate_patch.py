#!/usr/bin/env python3
"""Generate an UNINSTALLED, offline timer-encoding delta against E004fk source."""
from __future__ import annotations
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/E004-front-ir-vd55g0/e004fk-native-flash-disable-ordering/build/source/leds-qcom-flash.c"
WIN = ROOT / "experiments/E004-front-ir-vd55g0/e004fl-ir-trigger-timing-authority/evidence/RESULT.json"
PATCH = ROOT / "src/front-ir-vd55g0/illumination/0003-qcom-flash-align-pmic-timer-encoding.patch"
BASE_SHA = "cd1f98411545cdb4b679bb21c4c29076a88866517488d5b618c31485caa04727"
WIN_SHA = "1d3ab98722a381c64f355b0b71da6cea84c4f569f81da1ebde262f51ea4348ef"

def need(flag: bool, why: str) -> None:
    if not flag:
        raise ValueError("E004FV_OFFLINE_FAIL " + why)

def source_pair() -> tuple[str, str]:
    need(sha256(BASE.read_bytes()).hexdigest() == BASE_SHA, "E004fk source drift")
    need(sha256(WIN.read_bytes()).hexdigest() == WIN_SHA, "Windows timer result drift")
    win = json.loads(WIN.read_text())
    need(win["timer_handler"]["enabled_value"] ==
         "0x80 | floor((requested_ms - 10) / 10)" and
         win["timer_handler"]["accepted_ms"] == [10, 1280] and
         win["timer_handler"]["step_ms"] == 10 and
         win["timer_handler"]["disabled_value"] == 0,
         "Windows timer interpretation changed")
    source = BASE.read_text()
    before = """\t/* set SAFETY_TIMER for all the channels connected to the same LED */
\ttimeout_ms = min_t(u32, timeout_ms, led->max_timeout_ms);

\tfor (i = 0; i < led->chan_count; i++) {
\t\tchan_id = led->chan_id[i];

\t\ttimer = timeout_ms / FLASH_TIMER_STEP_MS;
\t\ttimer = clamp_t(u8, timer, 0, FLASH_TIMER_VAL_MASK);

\t\tif (timeout_ms)
\t\t\ttimer |= FLASH_TIMER_EN_BIT;
"""
    after = """\t/* Fail closed on an enabled but unrepresentable sub-step request. */
\ttimeout_ms = min_t(u32, timeout_ms, led->max_timeout_ms);
\tif (timeout_ms && timeout_ms < FLASH_TIMER_STEP_MS)
\t\treturn -EINVAL;

\t/*
\t * Windows PMIC handler uses bit 7 plus a 10 ms base interval;
\t * bits 6:0 encode additional 10 ms intervals. Zero disables.
\t * Reject an unrepresentable value before any timer-register write.
\t */
\tif (!timeout_ms)
\t\ttimer = 0;
\telse {
\t\tu32 steps = (timeout_ms - FLASH_TIMER_STEP_MS) /
\t\t\t\tFLASH_TIMER_STEP_MS;

\t\tif (steps > FLASH_TIMER_VAL_MASK)
\t\t\treturn -EINVAL;
\t\ttimer = (u8)steps | FLASH_TIMER_EN_BIT;
\t}

\tfor (i = 0; i < led->chan_count; i++) {
\t\tchan_id = led->chan_id[i];
"""
    need(source.count(before) == 1, "unique timer source anchor unavailable")
    patched = source.replace(before, after, 1)
    # A flash cannot be armed with a disabled or unrepresentable timer.
    guard_anchor = """\trc = set_flash_strobe(led, SW_STROBE, false);
\tif (rc)
\t\treturn rc;

\trc = update_allowed_flash_current(led, &led->flash_current_ma, state);
"""
    guarded = """\trc = set_flash_strobe(led, SW_STROBE, false);
\tif (rc)
\t\treturn rc;

\tif (state && (led->flash_timeout_ms < FLASH_TIMER_STEP_MS ||
\t\t      led->max_timeout_ms < FLASH_TIMER_STEP_MS))
\t\treturn -EINVAL;

\trc = update_allowed_flash_current(led, &led->flash_current_ma, state);
"""
    need(patched.count(guard_anchor) == 1, "unique flash arm anchor unavailable")
    return source, patched.replace(guard_anchor, guarded, 1)

def main() -> None:
    old, new = source_pair()
    patch = "".join(unified_diff(old.splitlines(keepends=True),
                                 new.splitlines(keepends=True),
                                 fromfile="a/drivers/leds/flash/leds-qcom-flash.c",
                                 tofile="b/drivers/leds/flash/leds-qcom-flash.c",
                                 n=0))
    need(2 <= patch.count("@@ -") <= 10, "unexpected patch hunk count")
    PATCH.write_text(patch)
    print("E004FV_OFFLINE_PATCH=PREPARED SOURCE_CHANGED_NOT_INSTALLED")
    print("PATCH_SHA256=" + sha256(patch.encode()).hexdigest())

if __name__ == "__main__":
    main()
