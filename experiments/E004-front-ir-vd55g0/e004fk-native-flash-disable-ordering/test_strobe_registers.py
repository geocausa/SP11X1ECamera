#!/usr/bin/env python3
"""Test the real strobe helper against a register-state model; no hardware I/O."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

PRELUDE = r"""
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <errno.h>
typedef uint8_t u8;
#define BIT(n) (1U << (n))
#define FIELD_PREP(mask, val) (((val) << __builtin_ctz(mask)) & (mask))
#define FLASH_STROBE_HW_SW_SEL_BIT BIT(2)
#define SW_STROBE_VAL 0
#define HW_STROBE_VAL 1
#define FLASH_HW_STROBE_TRIGGER_SEL_BIT BIT(1)
#define STROBE_LEVEL_TRIGGER_VAL 0
#define FLASH_STROBE_POLARITY_BIT BIT(0)
#define STROBE_ACTIVE_HIGH_VAL 1
enum led_strobe { SW_STROBE, HW_STROBE };
enum { REG_CHAN_STROBE, REG_CHAN_EN };
struct qcom_flash_data { int r_fields[2]; };
struct qcom_flash_led {
    struct qcom_flash_data *flash_data;
    int chan_count;
    u8 chan_id[2];
    bool enabled;
};
static struct {
    unsigned channels, modes[4], step, fail_at, live_mode_writes;
} hw;
static int regmap_fields_write(int field, u8 channel, unsigned value)
{
    assert(field == REG_CHAN_STROBE && channel < 4);
    if (++hw.step == hw.fail_at)
        return -EIO;
    if (hw.channels & BIT(channel))
        hw.live_mode_writes++;
    hw.modes[channel] = value;
    return 0;
}
static int regmap_field_update_bits(int field, unsigned mask, unsigned value)
{
    assert(field == REG_CHAN_EN);
    if (++hw.step == hw.fail_at)
        return -EIO;
    hw.channels = (hw.channels & ~mask) | (value & mask);
    return 0;
}
"""
TEST = r"""
int main(void)
{
    struct qcom_flash_data data = { .r_fields = { REG_CHAN_STROBE, REG_CHAN_EN } };
    int cases = 0;
    /* Channel 1 belongs to another LED and must survive every operation. */
    for (int initial = 0; initial <= 1; initial++) {
        for (int mode = SW_STROBE; mode <= HW_STROBE; mode++) {
            for (int on = 0; on <= 1; on++) {
                struct qcom_flash_led led = { &data, 2, {0, 3}, initial };
                hw.channels = BIT(1) | (initial ? BIT(0) | BIT(3) : 0);
                for (int i = 0; i < 4; i++) hw.modes[i] = 5;
                hw.step = hw.fail_at = hw.live_mode_writes = 0;
                assert(set_flash_strobe(&led, mode, on) == 0);
#if BASELINE
                assert(hw.live_mode_writes == (initial ? 2U : 0U));
#else
                assert(hw.live_mode_writes == 0);
#endif
                assert(hw.channels == (BIT(1) | (on ? BIT(0) | BIT(3) : 0)));
                assert(led.enabled == (bool)on);
                assert(hw.modes[1] == 5 && hw.modes[2] == 5);
                assert(hw.modes[0] == (unsigned)(mode == HW_STROBE ? 5 : 1));
                assert(hw.modes[3] == hw.modes[0]);
                cases++;
            }
        }
    }
#if !BASELINE
    for (int on = 0; on <= 1; on++) {
        int operations = on ? 4 : 3;
        for (int fail = 1; fail <= operations; fail++) {
            struct qcom_flash_led led = { &data, 2, {0, 3}, true };
            hw.channels = BIT(0) | BIT(1) | BIT(3);
            hw.modes[0] = hw.modes[1] = hw.modes[2] = hw.modes[3] = 5;
            hw.step = hw.live_mode_writes = 0;
            hw.fail_at = fail;
            assert(set_flash_strobe(&led, SW_STROBE, on) == -EIO);
            assert(hw.step == (unsigned)fail && !hw.live_mode_writes);
            assert(hw.channels & BIT(1));
            assert(hw.modes[1] == 5 && hw.modes[2] == 5);
            if (fail > 1) {
                assert(!(hw.channels & (BIT(0) | BIT(3))));
                assert(!led.enabled);
            } else {
                assert(led.enabled && hw.channels == 11);
                assert(hw.modes[0] == 5 && hw.modes[3] == 5);
            }
            cases++;
        }
    }
#endif
    printf("PASS %d strobe-register contract cases%s\n", cases,
           BASELINE ? " (baseline armed-mode writes reproduced)" : "");
    return 0;
}
"""

def extract(source):
    text = source.read_text()
    match = re.search(r"^static int set_flash_strobe\(", text, re.M)
    assert match
    opening = text.index("{", match.end())
    end, depth = opening + 1, 1
    while depth:
        if text[end] == "{":
            depth += 1
        elif text[end] == "}":
            depth -= 1
        end += 1
    return text[match.start():end]

def run(path, baseline, sanitize):
    with tempfile.TemporaryDirectory(prefix="qcom-flash-register-") as tmp:
        source, exe = Path(tmp) / "test.c", Path(tmp) / "test"
        source.write_text(PRELUDE + extract(path) + TEST)
        args = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                f"-DBASELINE={int(baseline)}"]
        if sanitize:
            args += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
        subprocess.run(args + [str(source), "-o", str(exe)], check=True)
        output = subprocess.check_output([str(exe)], text=True).strip()
    return {"baseline": baseline, "sanitizers": sanitize, "stdout": output,
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--patched", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {"status": "PASS_OFFLINE_STROBE_REGISTER_ORDERING",
              "hardware_access": False,
              "runs": [run(path, baseline, sanitize)
                       for sanitize in (False, True)
                       for path, baseline in ((args.baseline, True),
                                              (args.patched, False))],
              "limitations": ["Regmap state model, no physical PMIC validation.",
                              "No concurrency or power-failure proof.",
                              "If initial disable fails, output is not proven off; no trigger writes follow."]}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
