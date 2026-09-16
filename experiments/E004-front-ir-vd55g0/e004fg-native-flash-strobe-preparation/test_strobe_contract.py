#!/usr/bin/env python3
"""Compile the real strobe callbacks against an offline hardware-state model.

This checks callback preparation/order and error propagation, not regmap, PMIC
timing, physical current, thermal sensing, or board wiring. It performs no I/O
to hardware. Current/timeout values are synthetic test inputs, not board policy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

BASE_SHA = "770ba6ed706184e3017ebee3c06784569ad7f13a0f20326c6fa7fc56607ef4e0"

PRELUDE = r"""
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <errno.h>
#include <stdio.h>
typedef uint32_t u32;
#define UA_PER_MA 1000U
#define USEC_PER_MSEC 1000U
#define min_t(type, a, b) ((type)(a) < (type)(b) ? (type)(a) : (type)(b))
enum led_mode { FLASH_MODE, TORCH_MODE };
enum led_strobe { SW_STROBE, HW_STROBE };
struct led_classdev_flash { int unused; };
struct qcom_flash_led {
    struct led_classdev_flash flash;
    u32 flash_current_ma, max_flash_current_ma, flash_timeout_ms;
    u32 programmed_current, programmed_timeout, reserved;
    enum led_mode mode;
    enum led_strobe trigger;
    bool module, armed, budget_checked, current_written, timeout_written;
    int step, fail_at, violations;
};
struct v4l2_flash { struct led_classdev_flash *fled_cdev; };
static struct qcom_flash_led *flcdev_to_qcom_fled(struct led_classdev_flash *f)
{
    return (struct qcom_flash_led *)((char *)f -
           offsetof(struct qcom_flash_led, flash));
}
static int step(struct qcom_flash_led *l)
{
    return ++l->step == l->fail_at ? -EIO : 0;
}
static bool ready(struct qcom_flash_led *l)
{
    return l->budget_checked && l->current_written && l->timeout_written &&
           l->mode == FLASH_MODE && l->programmed_current == 350 &&
           l->programmed_timeout == 40 && l->reserved == 350;
}
static int set_flash_strobe(struct qcom_flash_led *l, enum led_strobe s, bool on)
{
    int rc = step(l);
    if (rc)
        return rc;
    if (on && (!l->module || !ready(l))) {
        l->violations++;
        return -EPROTO;
    }
    l->armed = on;
    l->trigger = s;
    return 0;
}
static int update_allowed_flash_current(struct qcom_flash_led *l, u32 *ma, bool on)
{
    int rc = step(l);
    if (rc)
        return rc;
    if (l->armed)
        return -EBUSY;
    *ma = on ? min_t(u32, *ma, 350) : 0;
    l->reserved = *ma;
    l->budget_checked = true;
    return 0;
}
static int set_flash_current(struct qcom_flash_led *l, u32 ma, enum led_mode mode)
{
    int rc = step(l);
    if (rc)
        return rc;
    if (l->armed)
        return -EBUSY;
    l->programmed_current = ma;
    l->mode = mode;
    l->current_written = true;
    return 0;
}
static int set_flash_timeout(struct qcom_flash_led *l, u32 ms)
{
    int rc = step(l);
    if (rc)
        return rc;
    if (l->armed)
        return -EBUSY;
    l->programmed_timeout = ms;
    l->timeout_written = true;
    return 0;
}
static int set_flash_module_en(struct qcom_flash_led *l, bool on)
{
    int rc = step(l);
    if (rc)
        return rc;
    if (on && !ready(l)) {
        l->violations++;
        return -EPROTO;
    }
    l->module = on;
    return 0;
}
"""
TEST = r"""
static struct qcom_flash_led fresh(void)
{
    struct qcom_flash_led l = { .max_flash_current_ma = 1000,
                               .mode = TORCH_MODE };
    assert(qcom_flash_brightness_set(&l.flash, 700000) == 0);
    assert(qcom_flash_timeout_set(&l.flash, 40000) == 0);
    assert(l.flash_current_ma == 700 && l.flash_timeout_ms == 40);
    assert(l.programmed_current == 0 && l.programmed_timeout == 0);
    return l;
}
static int invoke(struct qcom_flash_led *l, bool external, bool on)
{
    struct v4l2_flash v = { .fled_cdev = &l->flash };
    return external ? qcom_flash_external_strobe_set(&v, on) :
                      qcom_flash_strobe_set(&l->flash, on);
}
int main(void)
{
    int cases = 0;
    for (int external = 0; external <= 1; external++) {
        struct qcom_flash_led l = fresh();
        int rc = invoke(&l, external, true);
#if BASELINE
        if (external) {
            assert(rc == -EPROTO && l.violations == 1 && !l.armed);
            puts("baseline external trigger fails preparation contract");
            cases++;
            continue;
        }
#endif
        assert(rc == 0 && l.armed && l.module && ready(&l));
        assert(l.trigger == (external ? HW_STROBE : SW_STROBE));
        assert(invoke(&l, external, false) == 0);
        assert(!l.armed && !l.module && !l.reserved);
        cases++;
        /* Every helper may fail. No subsequent operation may arm the output. */
        for (int fail = 1; fail <= 6; fail++) {
            l = fresh();
            l.fail_at = fail;
            assert(invoke(&l, external, true) == -EIO);
            assert(l.step == fail && !l.armed && !l.violations);
            cases++;
        }
#if !BASELINE
        /* A second request replaces stale state with newly prepared settings. */
        l = fresh();
        assert(invoke(&l, external, true) == 0);
        assert(invoke(&l, external, false) == 0);
        assert(qcom_flash_brightness_set(&l.flash, 700000) == 0);
        l.budget_checked = l.current_written = l.timeout_written = false;
        l.programmed_current = l.programmed_timeout = 0;
        l.mode = TORCH_MODE;
        assert(invoke(&l, external, true) == 0 && ready(&l));
        assert(invoke(&l, external, false) == 0 && !l.armed);
        cases++;
#endif
    }
    printf("PASS %d callback-contract cases\n", cases);
    return 0;
}
"""

def extract(text, name):
    match = re.search(r"^static int " + re.escape(name) + r"\(", text, re.M)
    if not match:
        raise ValueError(f"missing callback: {name}")
    start = text.index("{", match.end())
    depth = 1
    end = start + 1
    while depth:
        if text[end] == "{":
            depth += 1
        elif text[end] == "}":
            depth -= 1
        end += 1
    return text[match.start():end] + "\n"

def run(source, baseline, sanitize):
    text = source.read_text()
    names = ["qcom_flash_brightness_set", "qcom_flash_timeout_set"]
    if not baseline:
        names.append("qcom_flash_strobe")
    names += ["qcom_flash_strobe_set", "qcom_flash_external_strobe_set"]
    program = PRELUDE + "\n".join(extract(text, n) for n in names) + TEST
    with tempfile.TemporaryDirectory(prefix="qcom-flash-contract-") as tmp:
        cfile, binary = Path(tmp) / "contract.c", Path(tmp) / "contract"
        cfile.write_text(program)
        args = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                f"-DBASELINE={int(baseline)}"]
        if sanitize:
            args += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
        subprocess.run(args + [str(cfile), "-o", str(binary)], check=True)
        result = subprocess.run([str(binary)], check=True, text=True,
                                capture_output=True)
    return {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "baseline": baseline, "sanitizers": sanitize,
            "stdout": result.stdout.strip()}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--patched", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    assert hashlib.sha256(args.baseline.read_bytes()).hexdigest() == BASE_SHA
    results = [run(path, baseline, sanitize)
               for sanitize in (False, True)
               for path, baseline in ((args.baseline, True), (args.patched, False))]
    data = {"result": "PASS_OFFLINE_CALLBACK_CONTRACT",
            "hardware_activated": False, "runs": results,
            "limitations": ["Hardware helpers are state-model stubs.",
                            "No register-level, wiring or optical validation.",
                            "Existing helper internals and disable-error recovery are not tested."]}
    args.output.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
